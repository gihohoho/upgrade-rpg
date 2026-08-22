#!/usr/bin/env python3
"""DB/network-free smoke for the v377 auth abuse and raw-body primitives."""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import sys
from typing import Any

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.sql.selectable import Select
from fastapi.testclient import TestClient
from starlette.requests import Request


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.api.routes import auth as auth_routes  # noqa: E402
from app.core.auth_errors import AuthFlowHTTPException, auth_error  # noqa: E402
from app.main import auth_flow_error_handler  # noqa: E402
from app.main import create_app  # noqa: E402
from app.middleware.auth_ip_rate_limit import (  # noqa: E402
    AUTH_IP_RATE_LIMIT_ACTION_SUFFIXES,
)
from app.middleware.request_body_limit import RequestBodyLimitMiddleware  # noqa: E402
from app.models.auth_rate_limit import AuthRateLimitBucket  # noqa: E402
from app.services.auth_rate_limiter import (  # noqa: E402
    AuthRateLimitKey,
    AuthRateLimitPolicy,
    AuthRateLimiter,
)
from app.services.auth_request_protection import (  # noqa: E402
    AUTH_IP_PROTECTION_STATE_KEY,
    AUTH_RATE_POLICIES,
    AuthIPProtectionState,
    AuthProtectionContext,
    AuthProtectionUnavailable,
    AuthRateLimited,
    AuthRequestProtection,
)


NOW = datetime(2026, 8, 15, 5, 0, tzinfo=UTC)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


async def exercise_body_limit(
    *,
    path: str,
    chunks: list[bytes],
    headers: list[tuple[bytes, bytes]] | None = None,
    global_limit: int = 32,
    auth_limit: int = 12,
) -> dict[str, Any]:
    downstream_calls = 0
    downstream_body = bytearray()
    sent: list[dict[str, Any]] = []
    receive_calls = 0

    messages = [
        {
            "type": "http.request",
            "body": chunk,
            "more_body": index < len(chunks) - 1,
        }
        for index, chunk in enumerate(chunks)
    ] or [{"type": "http.request", "body": b"", "more_body": False}]

    async def receive():  # type: ignore[no-untyped-def]
        nonlocal receive_calls
        receive_calls += 1
        if messages:
            return messages.pop(0)
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):  # type: ignore[no-untyped-def]
        sent.append(dict(message))

    async def downstream(_scope, replay_receive, replay_send):  # type: ignore[no-untyped-def]
        nonlocal downstream_calls
        downstream_calls += 1
        while True:
            message = await replay_receive()
            if message["type"] != "http.request":
                break
            downstream_body.extend(message.get("body", b""))
            if not message.get("more_body", False):
                break
        await replay_send({"type": "http.response.start", "status": 204, "headers": []})
        await replay_send({"type": "http.response.body", "body": b""})

    middleware = RequestBodyLimitMiddleware(
        downstream,
        global_max_bytes=global_limit,
        auth_max_bytes=auth_limit,
        auth_path_prefix="/api/v1/auth",
    )
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers or [],
        "client": ("203.0.113.8", 12345),
        "server": ("game.example.com", 443),
    }
    await middleware(scope, receive, send)
    status = next(item["status"] for item in sent if item["type"] == "http.response.start")
    response_headers = dict(
        next(item["headers"] for item in sent if item["type"] == "http.response.start")
    )
    response_body = b"".join(
        item.get("body", b"") for item in sent if item["type"] == "http.response.body"
    )
    return {
        "status": status,
        "responseBody": response_body,
        "downstreamCalls": downstream_calls,
        "downstreamBody": bytes(downstream_body),
        "receiveCalls": receive_calls,
        "responseHeaders": response_headers,
    }


class FakeResult:
    def __init__(self, row: AuthRateLimitBucket | None):
        self.row = row

    def scalar_one(self) -> AuthRateLimitBucket:
        require(self.row is not None, "fake rate bucket missing")
        return self.row

    def scalar_one_or_none(self) -> AuthRateLimitBucket | None:
        return self.row


class FakeTransaction:
    def __init__(self, owner: "FakeRateStore") -> None:
        self.owner = owner

    async def __aenter__(self):  # type: ignore[no-untyped-def]
        self.owner.active_transactions += 1
        return self

    async def __aexit__(self, *_args):  # type: ignore[no-untyped-def]
        self.owner.active_transactions -= 1
        return False


class FakeSession:
    def __init__(self, owner: "FakeRateStore") -> None:
        self.owner = owner
        self.last_key: tuple[str, str] | None = None

    async def __aenter__(self):  # type: ignore[no-untyped-def]
        return self

    async def __aexit__(self, *_args):  # type: ignore[no-untyped-def]
        return False

    def begin(self) -> FakeTransaction:
        return FakeTransaction(self.owner)

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        compiled = statement.compile(dialect=postgresql.dialect())
        params = compiled.params
        if isinstance(statement, Insert):
            key = (str(params["scope"]), str(params["subject_digest"]))
            self.last_key = key
            if key not in self.owner.rows:
                self.owner.rows[key] = AuthRateLimitBucket(**params)
            return FakeResult(None)
        require(isinstance(statement, Select), "unexpected fake rate statement")
        scope = next(value for name, value in params.items() if name.startswith("scope_"))
        digest = next(
            value for name, value in params.items() if name.startswith("subject_digest_")
        )
        key = (str(scope), str(digest))
        self.last_key = key
        return FakeResult(self.owner.rows.get(key))


class FakeRateStore:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], AuthRateLimitBucket] = {}
        self.active_transactions = 0

    def __call__(self) -> FakeSession:
        return FakeSession(self)


async def test_body_limits() -> None:
    declared = await exercise_body_limit(
        path="/api/v1/auth/login",
        chunks=[b"never-read"],
        headers=[(b"content-length", b"13")],
    )
    require(declared["status"] == 413, "declared auth oversize was not rejected")
    require(declared["downstreamCalls"] == 0, "declared oversize reached downstream")
    require(declared["receiveCalls"] == 0, "declared oversize body was unnecessarily read")

    private_marker = b"private-identifier-token"
    understated = await exercise_body_limit(
        path="/api/v1/auth/login",
        chunks=[b"123456", b"7890123" + private_marker],
        headers=[(b"content-length", b"1")],
    )
    require(understated["status"] == 413, "understated auth body bypassed actual-byte cap")
    require(understated["downstreamCalls"] == 0, "understated oversize reached downstream")
    require(private_marker not in understated["responseBody"], "413 reflected private body")
    require(json.loads(understated["responseBody"])["error"]["code"] == "request_body_too_large", "413 code mismatch")

    headerless = await exercise_body_limit(
        path="/api/v1/game/save",
        chunks=[b"x" * 20, b"y" * 13],
    )
    require(headerless["status"] == 413, "headerless global oversize bypassed cap")
    require(headerless["downstreamCalls"] == 0, "headerless oversize reached downstream")

    auth_small = await exercise_body_limit(
        path="/api/v1/auth/register",
        chunks=[b"a" * 13],
    )
    global_same = await exercise_body_limit(
        path="/api/v1/game/save",
        chunks=[b"a" * 13],
    )
    require(auth_small["status"] == 413, "auth-specific smaller cap was not selected")
    require(global_same["status"] == 204, "global cap rejected a body allowed outside auth")
    require(global_same["downstreamBody"] == b"a" * 13, "accepted body was not replayed exactly")

    exact = await exercise_body_limit(
        path="/api/v1/auth/reset-password",
        chunks=[b"123456", b"789012"],
        headers=[(b"content-length", b"12"), (b"content-length", b"12")],
    )
    require(exact["status"] == 204 and exact["downstreamBody"] == b"123456789012", "exact cap or duplicate equal length failed")
    require(
        exact["responseHeaders"].get(b"cache-control") == b"no-store",
        "accepted auth response omitted Cache-Control no-store",
    )
    require(
        b"cache-control" not in global_same["responseHeaders"],
        "non-auth middleware response received the auth cache policy",
    )

    conflicting = await exercise_body_limit(
        path="/api/v1/auth/login",
        chunks=[b"ok"],
        headers=[(b"content-length", b"2"), (b"content-length", b"3")],
    )
    malformed = await exercise_body_limit(
        path="/api/v1/auth/login",
        chunks=[b"ok"],
        headers=[(b"content-length", b"private-invalid-length")],
    )
    require(conflicting["status"] == 413, "conflicting Content-Length was accepted")
    require(malformed["status"] == 413, "malformed Content-Length was accepted")
    require(conflicting["downstreamCalls"] == 0, "conflicting length reached downstream")
    require(malformed["downstreamCalls"] == 0, "malformed length reached downstream")


async def test_auth_response_and_proxy_contract() -> None:
    limited = auth_error(
        429,
        "auth_rate_limited",
        "rate limited",
        headers={"Retry-After": "17"},
    )
    response = await auth_flow_error_handler(None, limited)  # type: ignore[arg-type]
    body = json.loads(response.body)
    require(response.headers.get("retry-after") == "17", "429 Retry-After header missing")
    require(body["error"]["code"] == "auth_rate_limited", "429 stable code missing")
    require(body["meta"]["retryAfterSeconds"] == 17, "429 retry metadata missing")

    private_marker = "private-db-failure-detail"
    exception_app = create_app()

    @exception_app.post("/api/v1/auth/_smoke-unhandled")
    async def raise_unhandled_auth_failure():  # type: ignore[no-untyped-def]
        raise RuntimeError(private_marker)

    with TestClient(exception_app) as client:
        internal = client.post("/api/v1/auth/_smoke-unhandled", json={})
    internal_body = internal.json()
    require(internal.status_code == 500, "unhandled auth failure status changed")
    require(
        internal.headers.get("Cache-Control") == "no-store",
        "unhandled auth failure omitted Cache-Control no-store",
    )
    require(
        internal_body["type"] == "auth.error"
        and internal_body["error"]["code"] == "auth_internal_error",
        "unhandled auth failure omitted the stable generic envelope",
    )
    require(
        internal_body["meta"] == {"sensitiveInputReturned": False},
        "unhandled auth failure metadata changed",
    )
    require(
        private_marker not in internal.text and "RuntimeError" not in internal.text,
        "unhandled auth failure reflected exception details",
    )

    class DummyLimiter:
        pass

    render_settings = type(
        "RenderSettings",
        (),
        {"auth_trusted_proxy_mode": "render", "environment": "production"},
    )()
    render_protection = AuthRequestProtection(
        current_settings=render_settings,  # type: ignore[arg-type]
        limiter=DummyLimiter(),  # type: ignore[arg-type]
    )
    render_request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "headers": [
                (b"cf-connecting-ip", b"203.0.113.9"),
                (b"x-forwarded-for", b"198.51.100.7, 10.0.0.1"),
            ],
            "client": ("10.0.0.2", 1234),
            "scheme": "https",
            "server": ("game.example", 443),
            "query_string": b"",
        }
    )
    require(
        render_protection._client_ip(render_request) == "203.0.113.9",
        "Render trusted client address did not use CF-Connecting-IP",
    )
    missing_forwarded = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "headers": [],
            "client": ("10.0.0.2", 1234),
            "scheme": "https",
            "server": ("game.example", 443),
            "query_string": b"",
        }
    )
    try:
        render_protection._client_ip(missing_forwarded)
    except AuthProtectionUnavailable:
        pass
    else:
        raise AssertionError("Render mode trusted a request without CF-Connecting-IP")

    route_source = Path(auth_routes.__file__).read_text(encoding="utf-8")
    for action in AUTH_RATE_POLICIES:
        require(f'action="{action}"' in route_source, f"route rate policy is unused: {action}")
    require(
        set(AUTH_IP_RATE_LIMIT_ACTION_SUFFIXES.values()) == set(AUTH_RATE_POLICIES),
        "pre-parse IP middleware and route action policies differ",
    )


def test_preparse_ip_rate_limit() -> None:
    class RecordingProtection:
        def __init__(self) -> None:
            self.ip_actions: list[str] = []
            self.subject_actions: list[str] = []
            self.block_action: str | None = None

        async def check_ip(self, *, request, action):  # type: ignore[no-untyped-def]
            require(request.url.path.endswith(action.replace("verify-email", "verify-email")) or action in {"account-deletion-request", "account-deletion-confirm"}, "middleware request path/action mismatch")
            self.ip_actions.append(action)
            if action == self.block_action:
                raise AuthRateLimited(23)
            return AuthProtectionContext(keyed_policies=())

        async def check_subject(self, *, action, **_kwargs):  # type: ignore[no-untyped-def]
            self.subject_actions.append(action)
            return AuthProtectionContext(keyed_policies=())

        async def record_failure(self, _context):  # type: ignore[no-untyped-def]
            return None

        async def record_success(self, _context):  # type: ignore[no-untyped-def]
            return None

    recording = RecordingProtection()
    original_protection = auth_routes.protection
    auth_routes.protection = recording
    try:
        with TestClient(create_app()) as client:
            private_marker = "private-malformed-identifier"
            malformed = client.post(
                "/api/v1/auth/login",
                content=f'{{"identifier":"{private_marker}"'.encode(),
                headers={"Content-Type": "application/json"},
            )
            require(malformed.status_code == 422, "allowed malformed JSON did not reach validation")
            require(recording.ip_actions == ["login"], "malformed JSON skipped the IP bucket")
            require(not recording.subject_actions, "malformed JSON reached the subject bucket")

            schema_invalid = client.post(
                "/api/v1/auth/login",
                json={"identifier": "schema-private"},
            )
            require(schema_invalid.status_code == 422, "schema-invalid auth body status changed")
            require(recording.ip_actions == ["login", "login"], "schema-invalid body skipped the IP bucket")
            require(not recording.subject_actions, "schema-invalid body reached the subject bucket")

            recording.block_action = "login"
            blocked = client.post(
                "/api/v1/auth/login",
                content=f'{{"identifier":"{private_marker}"'.encode(),
                headers={"Content-Type": "application/json"},
            )
            require(blocked.status_code == 429, "pre-parse IP block lost to JSON validation")
            require(blocked.headers.get("Retry-After") == "23", "middleware 429 Retry-After missing")
            blocked_body = blocked.json()
            require(blocked_body["error"]["code"] == "auth_rate_limited", "middleware 429 code mismatch")
            require(blocked_body["meta"]["retryAfterSeconds"] == 23, "middleware 429 retry metadata missing")
            require(blocked.headers.get("Cache-Control") == "no-store", "middleware 429 cache policy missing")
            require(private_marker not in blocked.text, "middleware 429 reflected malformed input")

            async def unavailable_check_ip(**_kwargs):  # type: ignore[no-untyped-def]
                raise AuthProtectionUnavailable("forced_store_failure")

            original_check_ip = recording.check_ip
            recording.check_ip = unavailable_check_ip  # type: ignore[method-assign]
            unavailable = client.post(
                "/api/v1/auth/login",
                content=f'{{"identifier":"{private_marker}"'.encode(),
                headers={"Content-Type": "application/json"},
            )
            recording.check_ip = original_check_ip  # type: ignore[method-assign]
            require(unavailable.status_code == 503, "pre-parse IP store failure did not fail closed")
            require(
                unavailable.json()["error"]["code"] == "auth_protection_unavailable",
                "middleware 503 stable code missing",
            )
            require(unavailable.headers.get("Cache-Control") == "no-store", "middleware 503 cache policy missing")
            require(private_marker not in unavailable.text, "middleware 503 reflected malformed input")

            recording.block_action = None
            deletion = client.post(
                "/api/v1/auth/account-deletion/request",
                json={"password": "private-password"},
            )
            require(deletion.status_code == 401, "deletion auth dependency status changed")
            require(
                recording.ip_actions[-1] == "account-deletion-request",
                "deletion dependency ran before the IP limiter",
            )

            protected_call_count = len(recording.ip_actions)
            require(client.post("/api/v1/auth/logout").status_code == 401, "logout dependency status changed")
            require(client.post("/api/v1/auth/login-extra", json={}).status_code == 404, "near auth path status changed")
            require(client.get("/api/v1/auth/login").status_code == 405, "non-POST auth method status changed")
            require(
                len(recording.ip_actions) == protected_call_count,
                "IP middleware matched a method or path outside its exact POST set",
            )

            oversized = client.post(
                "/api/v1/auth/login",
                content=b"x" * (16 * 1024 + 1),
                headers={"Content-Type": "application/json"},
            )
            require(oversized.status_code == 413, "raw body cap did not precede IP limiting")
            require(
                len(recording.ip_actions) == protected_call_count,
                "oversized body consumed an IP bucket before the raw body cap",
            )
    finally:
        auth_routes.protection = original_protection


async def test_route_subject_context_contract() -> None:
    ip_context = AuthProtectionContext(
        keyed_policies=(
            (
                AuthRateLimitKey(scope="login:ip", subject_digest="a" * 64),
                AUTH_RATE_POLICIES["login"]["ip"],
            ),
        )
    )
    subject_context = AuthProtectionContext(
        keyed_policies=(
            (
                AuthRateLimitKey(scope="login:identifier", subject_digest="b" * 64),
                AUTH_RATE_POLICIES["login"]["subject"],
            ),
        )
    )

    class SubjectOnlyProtection:
        def __init__(self) -> None:
            self.subject_actions: list[str] = []

        async def check_subject(self, *, action, **_kwargs):  # type: ignore[no-untyped-def]
            self.subject_actions.append(action)
            return subject_context

    split = SubjectOnlyProtection()
    original_protection = auth_routes.protection
    auth_routes.protection = split  # type: ignore[assignment]
    try:
        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/auth/login",
                "headers": [],
                "query_string": b"",
                "state": {
                    AUTH_IP_PROTECTION_STATE_KEY: AuthIPProtectionState(
                        action="login",
                        context=ip_context,
                        protection=split,
                    )
                },
            }
        )
        combined = await auth_routes._check_protection(
            request=request,
            action="login",
            subject_kind="identifier",
            subject_value="player22",
        )
        require(split.subject_actions == ["login"], "route did not check exactly one subject bucket")
        require(
            combined.keyed_policies == ip_context.keyed_policies + subject_context.keyed_policies,
            "route did not combine middleware IP and route subject contexts",
        )

        request.scope["state"][AUTH_IP_PROTECTION_STATE_KEY] = AuthIPProtectionState(
            action="register",
            context=ip_context,
            protection=split,
        )
        try:
            await auth_routes._check_protection(
                request=request,
                action="login",
                subject_kind="identifier",
                subject_value="player22",
            )
        except AuthFlowHTTPException as exc:
            require(exc.status_code == 503, "mismatched IP action context status changed")
            require(exc.detail["code"] == "auth_protection_unavailable", "mismatched IP context code changed")
        else:
            raise AssertionError("route accepted a mismatched IP action context")
        require(split.subject_actions == ["login"], "mismatched IP context reached subject limiting")
    finally:
        auth_routes.protection = original_protection


async def test_rate_limiter() -> None:
    store = FakeRateStore()
    clock = [NOW]
    sleep_calls: list[float] = []

    async def sleeper(seconds: float) -> None:
        require(store.active_transactions == 0, "failure delay held a rate bucket row lock")
        sleep_calls.append(seconds)

    limiter = AuthRateLimiter(
        session_factory=store,  # type: ignore[arg-type]
        hmac_secret="r" * 40,
        now_factory=lambda: clock[0],
        sleeper=sleeper,
    )
    ip_key = limiter.key_for_ip("login:ip", "2001:0db8:0:0:0:0:0:1")
    equivalent_ip = limiter.key_for_ip("login:ip", "2001:db8::1")
    require(ip_key == equivalent_ip, "equivalent IPv6 addresses produced different buckets")

    email_key = limiter.key_for_email("login:identifier", " Player@Example.COM ")
    equivalent_email = limiter.key_for_email("login:identifier", "player@example.com")
    require(email_key == equivalent_email, "canonical emails produced different buckets")
    raw_values = ("2001:db8::1", "Player@Example.COM", "private-token-value")
    token_key = limiter.key_for_token("verify-email:token", raw_values[2])
    for raw in raw_values:
        require(raw not in repr((ip_key, email_key, token_key)), "raw rate subject leaked in key repr")

    policy = AuthRateLimitPolicy(
        window_seconds=60,
        max_requests=2,
        failure_threshold=2,
        failure_cooldown_base_seconds=5,
        failure_cooldown_max_seconds=20,
        failure_delay_base_seconds=0.1,
        failure_delay_max_seconds=0.4,
    )
    first = await limiter.check_request(email_key, policy)
    second = await limiter.check_request(email_key, policy)
    third = await limiter.check_request(email_key, policy)
    require(first.allowed and second.allowed, "rate window blocked an allowed request")
    require(not third.allowed and third.retry_after_seconds == 60, "rate window Retry-After mismatch")

    clock[0] += timedelta(seconds=61)
    reset = await limiter.check_request(email_key, policy)
    require(reset.allowed and reset.request_count == 1, "expired request window did not reset")

    failure_policy = AuthRateLimitPolicy(
        window_seconds=60,
        max_requests=10,
        failure_threshold=2,
        failure_cooldown_base_seconds=5,
        failure_cooldown_max_seconds=20,
        failure_delay_base_seconds=0.1,
        failure_delay_max_seconds=0.4,
    )
    await limiter.check_request(ip_key, failure_policy)
    failure_one = await limiter.record_failure(ip_key, failure_policy)
    require(failure_one.failure_count == 1 and failure_one.retry_after_seconds == 0, "first failure unexpectedly cooled down")
    failure_two = await limiter.record_failure(ip_key, failure_policy)
    require(not failure_two.allowed and failure_two.retry_after_seconds == 5, "repeated failure cooldown mismatch")
    require(abs(failure_two.response_delay_seconds - 0.2) < 0.0001, "failure response delay mismatch")
    await limiter.wait_after_failure(failure_two)
    require(sleep_calls == [0.2], "async repeated-failure delay was not applied")

    blocked = await limiter.check_request(ip_key, failure_policy)
    require(not blocked.allowed and blocked.retry_after_seconds == 5, "cooldown was not enforced on next request")
    cleared = await limiter.record_success(ip_key)
    require(cleared, "successful auth did not clear failure state")
    clock[0] += timedelta(seconds=6)
    after_success = await limiter.check_request(ip_key, failure_policy)
    require(after_success.allowed and after_success.failure_count == 0, "success did not clear cooldown")

    insert_statement = limiter.build_insert_statement(token_key, now=clock[0])
    insert_sql = str(insert_statement.compile(dialect=postgresql.dialect())).upper()
    lock_statement = limiter.build_lock_statement(token_key)
    lock_sql = str(lock_statement.compile(dialect=postgresql.dialect())).upper()
    require("ON CONFLICT (SCOPE, SUBJECT_DIGEST) DO NOTHING" in insert_sql, "PostgreSQL safe upsert missing")
    require("FOR UPDATE" in lock_sql, "concurrent bucket row lock missing")
    compiled_values = repr(
        {
            **insert_statement.compile(dialect=postgresql.dialect()).params,
            **lock_statement.compile(dialect=postgresql.dialect()).params,
        }
    )
    for raw in raw_values:
        require(raw not in compiled_values, "raw rate subject reached SQL bind parameters")


async def main_async() -> None:
    await test_body_limits()
    await test_auth_response_and_proxy_contract()
    test_preparse_ip_rate_limit()
    await test_route_subject_context_contract()
    await test_rate_limiter()


def main() -> None:
    asyncio.run(main_async())
    print("OK: v377 auth public-security primitives smoke passed")


if __name__ == "__main__":
    main()
