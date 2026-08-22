#!/usr/bin/env python3
"""DB/network-free focused smoke for v371 verified-email account lifecycle."""
from __future__ import annotations

import asyncio
import builtins
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any
from urllib.error import HTTPError

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.core.security import CurrentUser, decode_access_token, get_current_user, hash_password  # noqa: E402
from app.api.routes import auth as auth_route_module  # noqa: E402
from app.api.routes.auth import router as auth_router  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import AuthEmailOutbox, User, UserEmailActionToken, UserProfile  # noqa: E402
from app.schemas.auth import (  # noqa: E402
    AccountDeletionConfirmRequest,
    EmailRequest,
    EmailValidationUnavailable,
    LoginRequest,
    NormalizedEmail,
    PasswordResetRequest,
    RegisterRequest,
    normalize_email_identity,
)
from app.services.auth_email_delivery import (  # noqa: E402
    BrevoEmailDelivery,
    EmailDeliveryError,
    EmailDeliveryResult,
    _RejectRedirectHandler,
    render_email_verification,
)
from app.services.auth_service import (  # noqa: E402
    EMAIL_PURPOSE_ACCOUNT_DELETION,
    EMAIL_PURPOSE_VERIFY,
    AuthFlowHTTPException,
    AuthService,
)
from app.services import auth_service as auth_service_module  # noqa: E402


NOW = datetime(2026, 8, 11, 3, 0, tzinfo=UTC)
TOKEN = "T" * 43
TOKEN_SECRET = "e" * 40


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@contextmanager
def replaced_route_protection(value):  # type: ignore[no-untyped-def]
    original = auth_route_module.protection
    auth_route_module.protection = value
    try:
        yield
    finally:
        auth_route_module.protection = original


class FakeResult:
    def __init__(self, rows: list[Any]):
        self.rows = list(rows)

    def scalar_one_or_none(self):  # type: ignore[no-untyped-def]
        if not self.rows:
            return None
        require(len(self.rows) == 1, "fake result expected at most one row")
        return self.rows[0]

    def scalar_one(self):  # type: ignore[no-untyped-def]
        require(len(self.rows) == 1, "fake result expected exactly one row")
        return self.rows[0]

    def one_or_none(self):  # type: ignore[no-untyped-def]
        if not self.rows:
            return None
        require(len(self.rows) == 1, "fake result expected at most one row")
        return self.rows[0]

    def scalars(self):  # type: ignore[no-untyped-def]
        return iter(self.rows)


class FakeSession:
    def __init__(
        self,
        execute_rows=(),  # type: ignore[no-untyped-def]
        *,
        get_user: User | None = None,
        flush_integrity_once: bool = False,
        commit_fail_on_calls: set[int] | None = None,
    ) -> None:
        self.execute_rows = [list(rows) for rows in execute_rows]
        self.get_user = get_user
        self.added: list[Any] = []
        self.statements: list[Any] = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.flush_calls = 0
        self.refresh_calls = 0
        self.flush_integrity_once = bool(flush_integrity_once)
        self.commit_fail_on_calls = set(commit_fail_on_calls or set())
        self._in_transaction = False

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        self._in_transaction = True
        self.statements.append(statement)
        rows = self.execute_rows.pop(0) if self.execute_rows else []
        return FakeResult(rows)

    async def get(self, _model, _identity):  # type: ignore[no-untyped-def]
        return self.get_user

    def add(self, value):  # type: ignore[no-untyped-def]
        self._in_transaction = True
        self.added.append(value)

    async def flush(self):
        self._in_transaction = True
        self.flush_calls += 1
        if self.flush_integrity_once:
            self.flush_integrity_once = False
            raise IntegrityError("INSERT users", {}, RuntimeError("unique violation"))
        for row in self.added:
            if isinstance(row, User) and row.id is None:
                row.id = 101

    async def commit(self):
        self.commit_calls += 1
        if self.commit_calls in self.commit_fail_on_calls:
            self._in_transaction = True
            raise RuntimeError("fake delivery audit commit failure")
        self._in_transaction = False

    async def rollback(self):
        self.rollback_calls += 1
        self._in_transaction = False

    async def refresh(self, _row):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        self._in_transaction = True

    def in_transaction(self) -> bool:
        return self._in_transaction


class FakeDelivery:
    def __init__(
        self,
        transaction_probe=None,  # type: ignore[no-untyped-def]
        *,
        error_code: str | None = None,
    ) -> None:
        self.calls: list[dict[str, Any]] = []
        self.transaction_probe = transaction_probe
        self.transaction_states: list[bool] = []
        self.error_code = error_code

    async def send(self, **kwargs):  # type: ignore[no-untyped-def]
        if self.transaction_probe is not None:
            self.transaction_states.append(bool(self.transaction_probe()))
        self.calls.append(dict(kwargs))
        if self.error_code:
            raise EmailDeliveryError(self.error_code)
        return EmailDeliveryResult(provider="brevo", message_id="fake-message-id")


def fake_normalize(value: str) -> NormalizedEmail:
    original = str(value).strip()
    return NormalizedEmail(original=original, canonical=original.casefold())


def service(delivery: FakeDelivery | None = None) -> AuthService:
    return AuthService(
        email_delivery=delivery or FakeDelivery(),
        email_normalizer=fake_normalize,
        token_secret=TOKEN_SECRET,
        abuse_secret="a" * 40,
        token_factory=lambda: TOKEN,
        now_factory=lambda: NOW,
        provider_ready=True,
        public_frontend_origin="https://game.example.com",
        discovery_floor_ms=0,
        discovery_jitter_ms=0,
    )


def user_row(*, verified: bool, is_admin: bool = False, auth_version: int = 2) -> User:
    return User(
        id=22,
        username="player22",
        email_original="Player22@example.com",
        email_canonical="player22@example.com",
        email_verified_at=NOW if verified else None,
        password_hash=hash_password("account123"),
        auth_version=auth_version,
        is_active=True,
        is_admin=is_admin,
        created_at=NOW,
        updated_at=NOW,
    )


async def test_register_login_and_generation() -> None:
    register_session = FakeSession([[], []])
    delivery = FakeDelivery(register_session.in_transaction)
    auth = service(delivery)
    registered = await auth.register(
        register_session,
        RegisterRequest(
            username="player01",
            email="Player01@example.com",
            password="account123",
            passwordConfirm="account123",
        ),
    )
    require(registered["status"] == "verification_required", "registration status mismatch")
    require("accessToken" not in registered, "registration issued an access token")
    require(registered["accessTokenIssued"] is False, "registration token marker mismatch")
    added_user = next(row for row in register_session.added if isinstance(row, User))
    added_profile = next(row for row in register_session.added if isinstance(row, UserProfile))
    added_outbox = next(row for row in register_session.added if isinstance(row, AuthEmailOutbox))
    require(added_user.is_admin is False and added_user.email_verified_at is None, "unsafe registration flags")
    require(added_profile.user_id == added_user.id == 101, "profile ownership mismatch")
    require(added_outbox.target_digest != TOKEN and len(added_outbox.target_digest) == 64, "raw email target stored")
    require(added_outbox.status == "pending", "registration outbox state was not persisted")
    require(len(delivery.calls) == 0 and register_session.commit_calls == 1, "registration sent mail synchronously")
    require(delivery.transaction_states == [], "registration invoked the provider")
    require(register_session.refresh_calls == 0, "registration refreshed rows before email send")

    unverified = user_row(verified=False)
    try:
        await auth.login(
            FakeSession([[unverified]]),
            LoginRequest(identifier="player22", password="account123"),
        )
    except AuthFlowHTTPException as exc:
        require(exc.status_code == 403, "unverified login status mismatch")
        require(exc.detail["code"] == "email_verification_required", "unverified error code mismatch")
    else:
        raise AssertionError("unverified account received a token")

    verified = user_row(verified=True, auth_version=7)
    logged_in = await auth.login(
        FakeSession([[verified]]),
        LoginRequest(identifier="PLAYER22", password="account123"),
    )
    claims = decode_access_token(logged_in["accessToken"])
    require(claims["authVersion"] == 7, "login token omitted authVersion")

    try:
        await get_current_user(
            authorization=f"Bearer {logged_in['accessToken']}",
            session=FakeSession(get_user=user_row(verified=True, auth_version=8)),
        )
    except HTTPException as exc:
        require(exc.status_code == 401, "stale authVersion did not return 401")
    else:
        raise AssertionError("stale access token remained valid")

    pending_user = user_row(verified=False)
    retry_delivery = FakeDelivery()
    retry_auth = service(retry_delivery)
    retry_session = FakeSession([[pending_user], [pending_user]])
    retried = await retry_auth.register(
        retry_session,
        RegisterRequest(
            username="player22",
            email="player22@example.com",
            password="account123",
            passwordConfirm="account123",
        ),
    )
    require(retried["status"] == "verification_required", "exact pending retry was rejected")
    require("accessToken" not in retried, "pending retry issued an access token")
    require(
        not any(isinstance(row, (User, UserProfile)) for row in retry_session.added),
        "pending retry created a duplicate account/profile",
    )
    require(
        len([row for row in retry_session.added if isinstance(row, AuthEmailOutbox)]) == 1,
        "pending retry did not create exactly one verification outbox request",
    )
    require(len(retry_delivery.calls) == 0, "pending retry sent email synchronously")

    wrong_session = FakeSession([[pending_user]])
    try:
        await retry_auth.register(
            wrong_session,
            RegisterRequest(
                username="player22",
                email="player22@example.com",
                password="wrong1234",
                passwordConfirm="wrong1234",
            ),
        )
    except AuthFlowHTTPException as exc:
        require(exc.status_code == 409, "wrong-password retry did not return generic 409")
        require(exc.detail["code"] == "account_identity_already_used", "retry 409 code changed")
    else:
        raise AssertionError("wrong-password retry resent verification")

    verified_conflict = user_row(verified=True)
    try:
        await retry_auth.register(
            FakeSession([[verified_conflict]]),
            RegisterRequest(
                username="player22",
                email="player22@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        )
    except AuthFlowHTTPException as exc:
        require(exc.status_code == 409, "verified exact identity did not return generic 409")
    else:
        raise AssertionError("verified identity resent registration verification")

    try:
        await retry_auth.register(
            FakeSession([[], [99]]),
            RegisterRequest(
                username="player22",
                email="different@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        )
    except AuthFlowHTTPException as exc:
        require(exc.status_code == 409, "partial identity collision did not return generic 409")
    else:
        raise AssertionError("partial identity collision created an account")

    race_winner = user_row(verified=False)
    race_winner.id = 33
    race_winner.username = "player33"
    race_winner.email_original = "Player33@example.com"
    race_winner.email_canonical = "player33@example.com"
    race_session = FakeSession(
        [[], [], [race_winner], [race_winner]],
        flush_integrity_once=True,
    )
    raced = await retry_auth.register(
        race_session,
        RegisterRequest(
            username="player33",
            email="player33@example.com",
            password="account123",
            passwordConfirm="account123",
        ),
    )
    require(raced["status"] == "verification_required", "unique race did not recover")
    require(race_session.rollback_calls == 3, "unique race did not release each read before bcrypt")


async def test_registration_conflict_bcrypt_shape() -> None:
    auth = service()
    original_run_in_threadpool = auth_service_module.run_in_threadpool
    bcrypt_calls: list[tuple[str, bool]] = []
    active_session: FakeSession | None = None

    async def recording_run_in_threadpool(function, *args):  # type: ignore[no-untyped-def]
        if function in (auth_service_module.hash_password, auth_service_module.verify_password):
            require(active_session is not None, "bcrypt probe has no active fake session")
            bcrypt_calls.append((function.__name__, active_session.in_transaction()))
        return await original_run_in_threadpool(function, *args)

    scenarios = [
        (
            "exact-wrong",
            FakeSession([[user_row(verified=False)]]),
            RegisterRequest(
                username="player22",
                email="player22@example.com",
                password="wrong1234",
                passwordConfirm="wrong1234",
            ),
        ),
        (
            "exact-verified",
            FakeSession([[user_row(verified=True)]]),
            RegisterRequest(
                username="player22",
                email="player22@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        ),
        (
            "username-only",
            FakeSession([[], [22]]),
            RegisterRequest(
                username="player22",
                email="different@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        ),
        (
            "email-only",
            FakeSession([[], [22]]),
            RegisterRequest(
                username="different22",
                email="player22@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        ),
    ]
    auth_service_module.run_in_threadpool = recording_run_in_threadpool
    try:
        for scenario_name, scenario_session, payload in scenarios:
            active_session = scenario_session
            before = len(bcrypt_calls)
            try:
                await auth.register(scenario_session, payload)
            except AuthFlowHTTPException as exc:
                require(exc.status_code == 409, f"{scenario_name} did not return generic 409")
                require(
                    exc.detail["code"] == "account_identity_already_used",
                    f"{scenario_name} disclosed a different conflict code",
                )
            else:
                raise AssertionError(f"{scenario_name} conflict created or recovered an account")
            require(
                len(bcrypt_calls) == before + 1,
                f"{scenario_name} did not perform exactly one bcrypt operation",
            )
            require(
                bcrypt_calls[-1][1] is False,
                f"{scenario_name} held a DB transaction during bcrypt",
            )
            require(
                scenario_session.rollback_calls == 3,
                f"{scenario_name} did not release lookup and reclaim transactions",
            )
    finally:
        auth_service_module.run_in_threadpool = original_run_in_threadpool


async def test_unverified_account_recovery_guard() -> None:
    auth = service()
    expired = user_row(verified=False)
    expired.created_at = NOW - timedelta(days=8)

    reclaim_session = FakeSession([[expired], [False], [0]])
    reclaimed = await auth._reclaim_expired_registration_conflicts(
        reclaim_session,
        username=expired.username,
        email_canonical=str(expired.email_canonical),
    )
    require(reclaimed is True, "abandoned unverified identity was not reclaimed")
    require(
        any("DELETE FROM users" in str(statement) for statement in reclaim_session.statements),
        "abandoned account reclaim did not delete the locked user",
    )
    require(reclaim_session.commit_calls == 1, "abandoned account reclaim did not commit once")

    owned_data_session = FakeSession([[expired], [True]])
    require(
        await auth._reclaim_expired_registration_conflicts(
            owned_data_session,
            username=expired.username,
            email_canonical=str(expired.email_canonical),
        )
        is False,
        "expired account with user-owned data was reclaimed",
    )
    require(
        not any("DELETE FROM users" in str(statement) for statement in owned_data_session.statements),
        "owned-data recovery reached user deletion",
    )

    audit_session = FakeSession([[expired], [False], [1]])
    require(
        await auth._reclaim_expired_registration_conflicts(
            audit_session,
            username=expired.username,
            email_canonical=str(expired.email_canonical),
        )
        is False,
        "expired account with admin audit history was reclaimed",
    )

    recent = user_row(verified=False)
    recent_session = FakeSession([[recent]])
    require(
        await auth._reclaim_expired_registration_conflicts(
            recent_session,
            username=recent.username,
            email_canonical=str(recent.email_canonical),
        )
        is False,
        "recent unverified account was reclaimed before TTL",
    )


async def test_generic_discovery_and_token_lock() -> None:
    auth = service()
    unknown_session = FakeSession([[]])
    unknown = await auth.resend_verification(
        unknown_session,
        EmailRequest(email="missing@example.com"),
    )
    require(unknown == {
        "status": "accepted",
        "request": "verification_email_if_eligible",
        "accountDisclosed": False,
        "emailRequestAccepted": True,
    }, "generic discovery response changed")
    unknown_outbox = next(
        row for row in unknown_session.added if isinstance(row, AuthEmailOutbox)
    )
    require(unknown_outbox.user_id is None, "unknown account was not queued as a decoy")

    recovery_user = user_row(verified=True)
    recovery_session = FakeSession([[recovery_user]])
    recovery_delivery = FakeDelivery(recovery_session.in_transaction)
    recovery_auth = service(recovery_delivery)
    recovered = await recovery_auth.recover_username(
        recovery_session,
        EmailRequest(email="player22@example.com"),
    )
    require(recovered["status"] == "accepted", "username recovery response changed")
    recovery_outbox = next(
        row for row in recovery_session.added if isinstance(row, AuthEmailOutbox)
    )
    require(recovery_outbox.user_id == recovery_user.id, "eligible recovery was not queued")
    require(recovery_session.commit_calls == 1, "username recovery queue did not commit once")
    require(recovery_delivery.transaction_states == [], "username recovery invoked the provider")
    require(recovery_session.refresh_calls == 0, "username recovery refreshed queue rows")

    token_row = UserEmailActionToken(
        id=9,
        user_id=22,
        purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        token_digest=auth.digest_email_token(TOKEN),
        expires_at=NOW + timedelta(minutes=10),
        consumed_at=None,
        delivery_status="sent",
        delivered_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )
    token_user = user_row(verified=True)
    lock_session = FakeSession([[(token_row.id, token_row.user_id)], [token_user], [token_row]])
    locked_user, locked_token = await auth._lock_action_token(
        lock_session,
        raw_token=TOKEN,
        purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
    )
    require(locked_user is token_user and locked_token is token_row, "valid token lock mismatch")
    lock_sql = [str(statement) for statement in lock_session.statements]
    require("FOR UPDATE" not in lock_sql[0].upper(), "candidate token lookup acquired a lock")
    candidate_select = lock_sql[0].split("FROM", 1)[0]
    require(
        "user_email_action_tokens.id" in candidate_select
        and "user_email_action_tokens.user_id" in candidate_select
        and "token_digest" not in candidate_select
        and "consumed_at" not in candidate_select,
        "candidate token lookup loaded a full ORM entity",
    )
    require(
        "FROM users" in lock_sql[1] and "FOR UPDATE" in lock_sql[1].upper(),
        "user row was not locked first",
    )
    require(
        "FROM user_email_action_tokens" in lock_sql[2]
        and "FOR UPDATE" in lock_sql[2].upper(),
        "token row was not re-locked after user",
    )
    require(
        lock_session.statements[1].get_execution_options().get("populate_existing") is True
        and lock_session.statements[2].get_execution_options().get("populate_existing") is True,
        "locked user/token state is not refreshed",
    )

    concurrently_consumed = UserEmailActionToken(
        id=token_row.id,
        user_id=token_row.user_id,
        purpose=token_row.purpose,
        token_digest=token_row.token_digest,
        expires_at=token_row.expires_at,
        consumed_at=NOW,
        delivery_status="sent",
        created_at=NOW,
        updated_at=NOW,
    )
    stale_candidate_session = FakeSession(
        [[(token_row.id, token_row.user_id)], [token_user], [concurrently_consumed]]
    )
    try:
        await auth._lock_action_token(
            stale_candidate_session,
            raw_token=TOKEN,
            purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        )
    except AuthFlowHTTPException as exc:
        require(exc.detail["code"] == "email_action_token_invalid", "stale consumed token code changed")
    else:
        raise AssertionError("concurrently consumed token was reused")
    require(stale_candidate_session.rollback_calls == 1, "stale consumed token was not rolled back")

    for index, delivery_status in enumerate(("pending", "failed"), start=20):
        ambiguous_token = UserEmailActionToken(
            id=index,
            user_id=token_user.id,
            purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
            token_digest=auth.digest_email_token(TOKEN),
            expires_at=NOW + timedelta(minutes=10),
            consumed_at=None,
            delivery_status=delivery_status,
            created_at=NOW,
            updated_at=NOW,
        )
        ambiguous_user, accepted = await auth._lock_action_token(
            FakeSession(
                [[(ambiguous_token.id, ambiguous_token.user_id)], [token_user], [ambiguous_token]]
            ),
            raw_token=TOKEN,
            purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        )
        require(ambiguous_user is token_user and accepted is ambiguous_token, f"{delivery_status} token rejected")

    expired = UserEmailActionToken(
        id=10,
        user_id=22,
        purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        token_digest=auth.digest_email_token(TOKEN),
        expires_at=NOW - timedelta(seconds=1),
        consumed_at=None,
        delivery_status="sent",
        created_at=NOW,
        updated_at=NOW,
    )
    expired_session = FakeSession([[(expired.id, expired.user_id)], [token_user], [expired]])
    try:
        await auth._lock_action_token(
            expired_session,
            raw_token=TOKEN,
            purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        )
    except AuthFlowHTTPException as exc:
        require(exc.detail["code"] == "email_action_token_invalid", "expired token error mismatch")
    else:
        raise AssertionError("expired token was accepted")
    require(expired_session.rollback_calls == 1, "invalid token lock was not rolled back")

    reset_user = user_row(verified=True, auth_version=5)
    reset_token = UserEmailActionToken(
        id=11,
        user_id=reset_user.id,
        purpose="password_reset",
        token_digest=auth.digest_email_token(TOKEN),
        expires_at=NOW + timedelta(minutes=10),
        consumed_at=None,
        delivery_status="sent",
        created_at=NOW,
        updated_at=NOW,
    )
    reset_session = FakeSession(
        [[(reset_token.id, reset_token.user_id)], [reset_user], [reset_token], []]
    )
    reset = await auth.reset_password(
        reset_session,
        PasswordResetRequest(
            token=TOKEN,
            password="newAccount456",
            passwordConfirm="newAccount456",
        ),
    )
    require(reset_user.auth_version == 6, "password reset did not advance authVersion")
    require(reset["accessTokensRevoked"] is True, "password reset revocation marker missing")
    require(reset_session.commit_calls == 1, "password reset transaction did not commit once")

    old_token = UserEmailActionToken(
        id=30,
        user_id=22,
        purpose=EMAIL_PURPOSE_VERIFY,
        token_digest="a" * 64,
        expires_at=NOW + timedelta(minutes=10),
        consumed_at=None,
        delivery_status="sent",
        created_at=NOW,
        updated_at=NOW,
    )
    issue_user = user_row(verified=False)
    issue_session = FakeSession([[issue_user]])
    issue_delivery = FakeDelivery(issue_session.in_transaction)
    issue_auth = service(issue_delivery)
    await issue_auth.resend_verification(
        issue_session,
        EmailRequest(email="player22@example.com"),
    )
    require(old_token.consumed_at is None, "resend pre-consumed an older valid token")
    require(
        not any("UPDATE user_email_action_tokens" in str(statement) for statement in issue_session.statements),
        "resend updated existing action tokens before successful action",
    )
    require(issue_delivery.transaction_states == [], "resend invoked the provider synchronously")
    require(issue_session.refresh_calls == 0, "resend refreshed token before queueing")

    audit_register_session = FakeSession([[], []], commit_fail_on_calls={1})
    audit_register_delivery = FakeDelivery(audit_register_session.in_transaction)
    try:
        await service(audit_register_delivery).register(
            audit_register_session,
            RegisterRequest(
                username="audituser",
                email="audituser@example.com",
                password="account123",
                passwordConfirm="account123",
            ),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("registration accepted an outbox commit failure")
    require(audit_register_session.commit_calls == 1, "registration queue failure was not exercised")
    require(audit_register_session.rollback_calls == 2, "registration queue failure was not rolled back")
    require(audit_register_delivery.calls == [], "failed registration queue invoked provider")

    audit_failure_user = user_row(verified=False)
    audit_failure_session = FakeSession(
        [[audit_failure_user]],
        commit_fail_on_calls={1},
    )
    audit_failure_delivery = FakeDelivery(
        audit_failure_session.in_transaction,
        error_code="brevo_network_error",
    )
    try:
        await service(audit_failure_delivery).resend_verification(
            audit_failure_session,
            EmailRequest(email="player22@example.com"),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("generic discovery accepted an outbox commit failure")
    require(audit_failure_session.commit_calls == 1, "generic queue failure was not exercised")
    require(audit_failure_session.rollback_calls == 1, "failure audit commit was not rolled back")
    require(audit_failure_delivery.calls == [], "failed generic queue invoked provider")


async def test_deletion_preview_and_hard_delete() -> None:
    auth = service()
    user = user_row(verified=True)
    current = CurrentUser(
        id=user.id,
        username=user.username,
        email=user.email_original,
        email_verified=True,
        auth_version=user.auth_version,
        is_admin=False,
    )
    preview = await auth.preview_account_deletion(
        FakeSession([[0], [3], [2]], get_user=user),
        current_user=current,
    )
    require(preview["characterCount"] == 2 and preview["saveSnapshotCount"] == 3, "delete counts changed")
    require(preview["maskedEmail"] == "p*******@example.com", "email mask changed")
    require(preview["rawSnapshotReturned"] is False, "raw snapshot preview leak")
    require("snapshot" not in preview and "snapshot_json" not in preview, "raw snapshot-shaped key leaked")

    invalid_confirmation_session = FakeSession()
    try:
        await auth.confirm_account_deletion(
            invalid_confirmation_session,
            SimpleNamespace(confirm_text="삭제", token=None),  # type: ignore[arg-type]
        )
    except AuthFlowHTTPException as exc:
        require(exc.status_code == 422, "service deletion confirmation did not fail closed")
        require(
            exc.detail["code"] == "account_deletion_confirmation_required",
            "service deletion confirmation code changed",
        )
    else:
        raise AssertionError("service accepted an invalid deletion confirmation")
    require(
        not invalid_confirmation_session.statements,
        "invalid deletion confirmation queried token state",
    )

    token_row = UserEmailActionToken(
        id=12,
        user_id=user.id,
        purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        token_digest=auth.digest_email_token(TOKEN),
        expires_at=NOW + timedelta(minutes=10),
        consumed_at=None,
        delivery_status="sent",
        created_at=NOW,
        updated_at=NOW,
    )
    deletion_session = FakeSession(
        [[(token_row.id, token_row.user_id)], [user], [token_row], [0], []]
    )
    deleted = await auth.confirm_account_deletion(
        deletion_session,
        AccountDeletionConfirmRequest(token=TOKEN, confirmText="계정 삭제"),
    )
    require(deleted == {"status": "deleted", "deletedUserId": 22}, "delete response leaked fields")
    require(deletion_session.commit_calls == 1, "hard delete did not commit exactly once")
    require("DELETE FROM users" in str(deletion_session.statements[-1]), "hard delete statement missing")

    admin = user_row(verified=True, is_admin=True)
    try:
        await auth.preview_account_deletion(
            FakeSession([[0]], get_user=admin),
            current_user=CurrentUser(
                id=admin.id,
                username=admin.username,
                email=admin.email_original,
                email_verified=True,
                auth_version=admin.auth_version,
                is_admin=True,
            ),
        )
    except AuthFlowHTTPException as exc:
        require(exc.detail["code"] == "admin_account_deletion_blocked", "admin delete blocker missing")
    else:
        raise AssertionError("administrator deletion preview was allowed")

    target_audit_session = FakeSession([[1]], get_user=user)
    try:
        await auth.preview_account_deletion(
            target_audit_session,
            current_user=current,
        )
    except AuthFlowHTTPException as exc:
        require(
            exc.detail["code"] == "admin_account_deletion_blocked",
            "target-only audit relationship did not block deletion",
        )
    else:
        raise AssertionError("account referenced as an audit target was deletable")
    audit_sql = str(target_audit_session.statements[0])
    require("admin_user_id" in audit_sql, "audit actor relationship is no longer counted")
    require(
        "target_type" in audit_sql and "target_id" in audit_sql,
        "audit target relationship is not counted",
    )


def test_validation_sanitizer_and_route_contract() -> None:
    class NoopProtection:
        async def check_ip(self, **_kwargs):  # type: ignore[no-untyped-def]
            return auth_route_module.AuthProtectionContext(keyed_policies=())

        async def check_subject(
            self,
            *,
            subject_kind,
            subject_value,
            **_kwargs,
        ):  # type: ignore[no-untyped-def]
            if subject_kind == "email":
                try:
                    normalize_email_identity(str(subject_value))
                except EmailValidationUnavailable as exc:
                    raise auth_route_module.AuthProtectionUnavailable(
                        "email_validation_unavailable"
                    ) from exc
            return auth_route_module.AuthProtectionContext(keyed_policies=())

        async def record_failure(self, _context):  # type: ignore[no-untyped-def]
            return None

        async def record_success(self, _context):  # type: ignore[no-untyped-def]
            return None

    app = create_app()
    with replaced_route_protection(NoopProtection()), TestClient(app) as client:
        password = "account123"
        different = "different456"
        mismatch = client.post(
            "/api/v1/auth/reset-password",
            json={"token": TOKEN, "password": password, "passwordConfirm": different},
        )
        require(mismatch.status_code == 422, "password mismatch must return 422")
        require(password not in mismatch.text and different not in mismatch.text, "password reflected in 422")
        require(TOKEN not in mismatch.text, "email action token reflected in 422")
        require(
            mismatch.json()["detail"]
            and all(set(error) == {"loc", "type", "msg"} for error in mismatch.json()["detail"]),
            "auth 422 detail must contain exactly loc/type/msg",
        )

        malformed_token = "token with spaces and private-value"
        invalid = client.post(
            "/api/v1/auth/account-deletion/confirm",
            json={"token": malformed_token, "confirmText": "계정 삭제"},
        )
        require(invalid.status_code == 422, "invalid token must return 422")
        require(malformed_token not in invalid.text, "invalid token reflected in 422")

        private_identifier = f"private-owner@{'x' * 245}.example.com"
        invalid_identifier = client.post(
            "/api/v1/auth/login",
            json={"identifier": private_identifier, "password": "account123"},
        )
        require(invalid_identifier.status_code == 422, "overlong identifier must return 422")
        require(private_identifier not in invalid_identifier.text, "identifier reflected in 422")

        class UnverifiedLoginService:
            async def login(self, _session, _payload):  # type: ignore[no-untyped-def]
                raise AuthFlowHTTPException(
                    status_code=403,
                    detail={
                        "code": "email_verification_required",
                        "message": "verification required",
                    },
                )

        original_service = auth_route_module.service
        auth_route_module.service = UnverifiedLoginService()
        try:
            unverified = client.post(
                "/api/v1/auth/login",
                json={"identifier": "player22", "password": "account123"},
            )
        finally:
            auth_route_module.service = original_service
        require(unverified.status_code == 403, "unverified HTTP response status mismatch")
        require(
            unverified.json()["error"]["code"] == "email_verification_required",
            "unverified HTTP error envelope code missing",
        )

        original_import = builtins.__import__

        def import_without_email_validator(name, *args, **kwargs):  # type: ignore[no-untyped-def]
            if name == "email_validator" or name.startswith("email_validator."):
                raise ImportError("forced missing email-validator for fail-closed smoke")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = import_without_email_validator
        try:
            unavailable = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "player01",
                    "email": "owner@example.com",
                    "password": "account123",
                    "passwordConfirm": "account123",
                },
            )
            require(unavailable.status_code == 503, "missing email-validator did not fail closed")
            body = unavailable.json()
            require(body["error"]["code"] == "email_validation_unavailable", "503 code mismatch")
        finally:
            builtins.__import__ = original_import

    routes = {
        (method, route.path)
        for route in auth_router.routes
        for method in getattr(route, "methods", set())
    }
    require(len(routes) == 12, f"auth route count changed: {sorted(routes)}")
    require(("GET", "/account-deletion/preview") in routes, "deletion preview missing")
    require(("POST", "/account-deletion/confirm") in routes, "deletion confirm missing")


def test_admin_email_contract_source() -> None:
    source = (BACKEND / "app/services/admin/account_user_management_service.py").read_text(encoding="utf-8")
    require("User.email_canonical" in source, "admin email search missing")
    require('"maskedEmail"' in source and '"emailVerified"' in source, "admin list email fields missing")
    require("include_full_email=True" in source, "admin detail full email opt-in missing")
    require("User.email_verified_at.is_not(None)" in source, "admin login-capable count omits verification")

    auth_source = (BACKEND / "app/services/auth_service.py").read_text(encoding="utf-8")
    require("session.refresh" not in auth_source, "auth email path refreshes rows before provider wait")
    require("async def _lock_token_user" not in auth_source, "token-first lock helper returned")
    lock_block = auth_source.split("async def _lock_action_token", 1)[1].split(
        "async def _consume_outstanding_tokens",
        1,
    )[0]
    candidate_block = lock_block.split("candidate =", 1)[1].split("if candidate is None", 1)[0]
    require("select(UserEmailActionToken)" not in candidate_block, "candidate loads Token ORM entity")
    require(
        "UserEmailActionToken.id" in candidate_block
        and "UserEmailActionToken.user_id" in candidate_block,
        "candidate scalar identity columns missing",
    )
    require("token_row.delivery_status" not in lock_block, "delivery audit state gates token validity")
    outbox_source = (BACKEND / "app/services/auth_email_outbox.py").read_text(encoding="utf-8")
    prepare_block = outbox_source.split("async def _prepare_claimed", 1)[1].split(
        "async def _eligible",
        1,
    )[0]
    require(
        "update(UserEmailActionToken)" not in prepare_block,
        "outbox prepare pre-consumes older links",
    )
    finalize_block = outbox_source.split("async def _finalize_attempt", 1)[1].split(
        "def new_token_row",
        1,
    )[0]
    require(
        "UserEmailActionToken.id != int(token_row.id)" in finalize_block,
        "successful outbox finalize does not preserve its newly delivered link",
    )
    require("async def _retry_pending_registration" in auth_source, "ambiguous registration recovery missing")
    require("async def _dummy_registration_password_check" in auth_source, "dummy bcrypt equalizer missing")
    partial_conflict_block = auth_source.split("if conflicting_id is not None:", 1)[1].split(
        "password_hash =", 1
    )[0]
    require(
        partial_conflict_block.index("await session.rollback()")
        < partial_conflict_block.index("_dummy_registration_password_check"),
        "partial registration conflict does bcrypt before releasing the DB transaction",
    )
    audit_block = auth_source.split("async def _admin_audit_count", 1)[1].split(
        "def _assert_deletable", 1
    )[0]
    require(
        "AdminChangeLog.admin_user_id" in audit_block
        and "AdminChangeLog.target_type" in audit_block
        and "AdminChangeLog.target_id" in audit_block,
        "account deletion audit relationship predicate is incomplete",
    )


def test_email_rendering_and_redirect_fail_closed() -> None:
    action_url = f"https://game.example.com/index.html#auth=verify-email&token={TOKEN}"
    rendered = render_email_verification(
        username='<img src="https://tracker.example/pixel">',
        action_url=action_url,
    )
    require("&lt;img" in rendered.html_content, "email username was not HTML-escaped")
    require("<img" not in rendered.html_content.lower(), "email contains an external image element")
    require("<link" not in rendered.html_content.lower(), "email contains an external stylesheet")
    require(action_url in rendered.text_content, "plaintext email action URL missing")

    provider_settings = SimpleNamespace(
        brevo_ready=True,
        brevo_from_name="Upgrade RPG",
        brevo_from_email="noreply@example.com",
        brevo_api_key=SimpleNamespace(get_secret_value=lambda: "private-brevo-api-key"),
        email_delivery_timeout_seconds=10,
    )
    opener_calls = 0

    def redirecting_opener(request, *, timeout):  # type: ignore[no-untyped-def]
        nonlocal opener_calls
        opener_calls += 1
        require(timeout == 10, "Brevo timeout contract changed")
        raise HTTPError(
            request.full_url,
            302,
            "Found",
            {"Location": "https://attacker.example/steal"},
            None,
        )

    transport = BrevoEmailDelivery(
        current_settings=provider_settings,  # type: ignore[arg-type]
        opener=redirecting_opener,
    )
    try:
        transport._send_once(recipient="owner@example.com", rendered=rendered)
    except EmailDeliveryError as exc:
        require(exc.code == "brevo_http_302", "redirect did not fail with a safe provider code")
        require("private-brevo-api-key" not in str(exc), "Brevo API key leaked in provider error")
        require(TOKEN not in str(exc), "email action token leaked in provider error")
    else:
        raise AssertionError("Brevo redirect was accepted")
    require(opener_calls == 1, "Brevo transport retried a redirected request")
    require(
        _RejectRedirectHandler().redirect_request(None, None, 302, "Found", {}, "https://attacker.example")
        is None,
        "default Brevo opener no longer rejects redirects",
    )


async def main_async() -> None:
    await test_register_login_and_generation()
    await test_registration_conflict_bcrypt_shape()
    await test_unverified_account_recovery_guard()
    await test_generic_discovery_and_token_lock()
    await test_deletion_preview_and_hard_delete()


def main() -> None:
    asyncio.run(main_async())
    test_validation_sanitizer_and_route_contract()
    test_admin_email_contract_source()
    test_email_rendering_and_redirect_fail_closed()
    print("OK: v371 verified-email account backend smoke passed")


if __name__ == "__main__":
    main()
