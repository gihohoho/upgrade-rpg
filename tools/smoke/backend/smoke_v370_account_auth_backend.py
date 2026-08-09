#!/usr/bin/env python3
"""Focused, DB-free smoke for the v370 account/auth backend foundation."""
from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.core.security import (  # noqa: E402
    CurrentUser,
    InvalidAccessToken,
    create_access_token,
    decode_access_token,
    get_current_user,
    hash_password,
    require_admin_user,
    verify_password,
)
from app.core.config import settings  # noqa: E402
from app.schemas.account import (  # noqa: E402
    AccountCharacterCreateRequest,
    AccountCharacterGameSaveRequest,
)
from app.models import User, UserProfile  # noqa: E402
from app.schemas.auth import LoginRequest, RegisterRequest  # noqa: E402
from app.services.account_character_service import (  # noqa: E402
    ACCOUNT_CHARACTER_SUMMARY_KEY,
    AccountCharacterService,
    account_character_metadata,
    account_character_slot_index,
    account_character_slot_key,
)
from app.services.game_service import GameService, SAVE_SNAPSHOT_MAX_SIZE_BYTES  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from app.main import create_app  # noqa: E402
from app.db.session import engine  # noqa: E402


class FakeScalars:
    def __init__(self, rows):  # type: ignore[no-untyped-def]
        self.rows = list(rows)

    def all(self):  # type: ignore[no-untyped-def]
        return list(self.rows)


class FakeResult:
    def __init__(self, rows):  # type: ignore[no-untyped-def]
        self.rows = list(rows)

    def scalars(self):  # type: ignore[no-untyped-def]
        return FakeScalars(self.rows)

    def scalar_one_or_none(self):  # type: ignore[no-untyped-def]
        if not self.rows:
            return None
        if len(self.rows) != 1:
            raise AssertionError("fake scalar result contains multiple rows")
        return self.rows[0]


class FakeSession:
    def __init__(self, rows=()):  # type: ignore[no-untyped-def]
        self.rows = list(rows)
        self.execute_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0

    async def execute(self, _statement):  # type: ignore[no-untyped-def]
        self.execute_calls += 1
        return FakeResult(self.rows)

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1

    async def refresh(self, _row):  # type: ignore[no-untyped-def]
        return None


class AuthFakeSession:
    def __init__(self, execute_rows=(), *, get_user=None):  # type: ignore[no-untyped-def]
        self.execute_rows = [list(rows) for rows in execute_rows]
        self.get_user = get_user
        self.added = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.flush_calls = 0

    async def execute(self, _statement):  # type: ignore[no-untyped-def]
        rows = self.execute_rows.pop(0) if self.execute_rows else []
        return FakeResult(rows)

    def add(self, value):  # type: ignore[no-untyped-def]
        self.added.append(value)

    async def flush(self):
        self.flush_calls += 1
        for value in self.added:
            if isinstance(value, User) and value.id is None:
                value.id = 101

    async def commit(self):
        self.commit_calls += 1

    async def rollback(self):
        self.rollback_calls += 1

    async def refresh(self, _row):  # type: ignore[no-untyped-def]
        return None

    async def get(self, _model, _identity):  # type: ignore[no-untyped-def]
        return self.get_user


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_validation_error(factory, message: str) -> None:  # type: ignore[no-untyped-def]
    try:
        factory()
    except ValidationError:
        return
    raise AssertionError(message)


def test_password_and_token() -> None:
    request = RegisterRequest(
        username="PLAYER_01",
        password="account123",
        passwordConfirm="account123",
    )
    require(request.username == "player_01", "username must normalize to lowercase")
    expect_validation_error(
        lambda: RegisterRequest(username="abc", password="account123", passwordConfirm="account123"),
        "short username was accepted",
    )
    expect_validation_error(
        lambda: RegisterRequest(username="player02", password="onlyletters", passwordConfirm="onlyletters"),
        "password without a number was accepted",
    )
    expect_validation_error(
        lambda: RegisterRequest(username="player02", password="숫자1234" * 10, passwordConfirm="숫자1234" * 10),
        "password exceeding 72 UTF-8 bytes was accepted",
    )

    password_hash = hash_password("account123")
    require("account123" not in password_hash, "password hash leaked plaintext")
    require(verify_password("account123", password_hash), "bcrypt password verification failed")
    require(not verify_password("account124", password_hash), "wrong password was accepted")

    now = datetime(2026, 8, 10, tzinfo=UTC)
    token, ttl_seconds = create_access_token(17, now=now, nonce="focused-smoke")
    claims = decode_access_token(token, now=now + timedelta(seconds=1))
    require(claims["userId"] == 17, "token subject did not round-trip")
    require(claims["nonce"] == "focused-smoke", "token nonce did not round-trip")

    header, payload, signature = token.split(".")
    replacement = "A" if payload[0] != "A" else "B"
    tampered = f"{header}.{replacement}{payload[1:]}.{signature}"
    try:
        decode_access_token(tampered, now=now + timedelta(seconds=1))
    except InvalidAccessToken:
        pass
    else:
        raise AssertionError("tampered token was accepted")

    try:
        decode_access_token(token, now=now + timedelta(seconds=ttl_seconds + 1))
    except InvalidAccessToken:
        pass
    else:
        raise AssertionError("expired token was accepted")

    encoded_header, encoded_payload, _encoded_signature = token.split(".")
    payload_padding = "=" * (-len(encoded_payload) % 4)
    long_lived_claims = json.loads(base64.urlsafe_b64decode(encoded_payload + payload_padding))
    long_lived_claims["exp"] = long_lived_claims["iat"] + ttl_seconds + 1
    long_lived_payload = base64.urlsafe_b64encode(
        json.dumps(long_lived_claims, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).rstrip(b"=").decode("ascii")
    signing_input = f"{encoded_header}.{long_lived_payload}".encode("ascii")
    long_lived_signature = base64.urlsafe_b64encode(
        hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode("ascii")
    long_lived_token = f"{encoded_header}.{long_lived_payload}.{long_lived_signature}"
    try:
        decode_access_token(long_lived_token, now=now + timedelta(seconds=1))
    except InvalidAccessToken:
        pass
    else:
        raise AssertionError("token exceeding the configured lifetime was accepted")


def test_auth_validation_secrets_are_not_reflected() -> None:
    app = create_app()
    with TestClient(app) as client:
        weak_secret = "onlyletters"
        weak_response = client.post(
            f"{settings.api_prefix}/auth/register",
            json={
                "username": "player_01",
                "password": weak_secret,
                "passwordConfirm": weak_secret,
            },
        )
        require(weak_response.status_code == 422, "weak password must return HTTP 422")
        require(weak_secret not in weak_response.text, "weak password was reflected in HTTP 422")

        password = "v370Secret123"
        password_confirm = "v370Other456"
        mismatch_response = client.post(
            f"{settings.api_prefix}/auth/register",
            json={
                "username": "player_01",
                "password": password,
                "passwordConfirm": password_confirm,
            },
        )
        require(mismatch_response.status_code == 422, "password mismatch must return HTTP 422")
        require(password not in mismatch_response.text, "password was reflected by model-level HTTP 422")
        require(password_confirm not in mismatch_response.text, "password confirmation was reflected by model-level HTTP 422")

        malformed_secret = "malformedSecret123"
        malformed_response = client.post(
            f"{settings.api_prefix}/auth/register",
            content=f'{{"username":"player_01","password":"{malformed_secret}"',
            headers={"Content-Type": "application/json"},
        )
        require(malformed_response.status_code == 422, "malformed auth JSON must return HTTP 422")
        require(malformed_secret not in malformed_response.text, "malformed auth body was reflected in HTTP 422")

        long_password = "v370LongSecret1" * 8
        login_response = client.post(
            f"{settings.api_prefix}/auth/login",
            json={"username": "player_01", "password": long_password},
        )
        require(login_response.status_code == 422, "overlong login password must return HTTP 422")
        require(long_password not in login_response.text, "login password was reflected in HTTP 422")

        invalid_username = "bad!"
        username_response = client.post(
            f"{settings.api_prefix}/auth/register",
            json={
                "username": invalid_username,
                "password": "v370Valid123",
                "passwordConfirm": "v370Valid123",
            },
        )
        require(username_response.status_code == 422, "invalid username must return HTTP 422")
        require(invalid_username in username_response.text, "safe non-password validation input was removed")

    require(engine.echo is False, "SQLAlchemy echo must stay disabled")
    require(engine.sync_engine.hide_parameters is True, "SQLAlchemy bind parameters must stay hidden")


async def test_auth_service_and_current_user() -> None:
    service = AuthService()
    register_payload = RegisterRequest(
        username="PLAYER_10",
        password="account123",
        passwordConfirm="account123",
    )
    register_session = AuthFakeSession([[]])
    registered = await service.register(register_session, register_payload)
    added_user = next(value for value in register_session.added if isinstance(value, User))
    added_profile = next(value for value in register_session.added if isinstance(value, UserProfile))
    require(registered["status"] == "registered", "registration status changed")
    require(registered["user"]["username"] == "player_10", "registered username was not normalized")
    require(registered["user"]["isAdmin"] is False, "self registration unexpectedly granted admin")
    require(added_user.password_hash != "account123", "registration stored a plaintext password")
    require(verify_password("account123", added_user.password_hash or ""), "registered password hash is invalid")
    require(added_profile.user_id == added_user.id == 101, "registration did not create the matching profile")
    require(register_session.commit_calls == 1, "registration did not commit exactly once")
    require(isinstance(registered["accessToken"], str) and registered["accessToken"], "registration token missing")

    duplicate_session = AuthFakeSession([[101]])
    try:
        await service.register(duplicate_session, register_payload)
    except HTTPException as exc:
        require(exc.status_code == 409, "duplicate username must return 409")
    else:
        raise AssertionError("duplicate username was accepted")
    require(not duplicate_session.added and duplicate_session.commit_calls == 0, "duplicate registration mutated state")

    active_user = User(
        id=22,
        username="player_22",
        password_hash=added_user.password_hash,
        is_active=True,
        is_admin=False,
    )
    login_payload = LoginRequest(username="PLAYER_22", password="account123")
    logged_in = await service.login(AuthFakeSession([[active_user]]), login_payload)
    require(logged_in["status"] == "authenticated", "valid login failed")
    require(logged_in["user"]["id"] == 22, "login returned the wrong user")

    wrong_errors: list[HTTPException] = []
    for session, payload in (
        (AuthFakeSession([[active_user]]), LoginRequest(username="player_22", password="account124")),
        (AuthFakeSession([[]]), LoginRequest(username="missing_22", password="account124")),
    ):
        try:
            await service.login(session, payload)
        except HTTPException as exc:
            wrong_errors.append(exc)
        else:
            raise AssertionError("invalid credentials were accepted")
    require(all(exc.status_code == 401 for exc in wrong_errors), "invalid credentials must return 401")
    require(wrong_errors[0].detail == wrong_errors[1].detail, "unknown username leaked through a distinct error")

    inactive_user = User(
        id=23,
        username="player_23",
        password_hash=added_user.password_hash,
        is_active=False,
        is_admin=False,
    )
    try:
        await service.login(
            AuthFakeSession([[inactive_user]]),
            LoginRequest(username="player_23", password="account123"),
        )
    except HTTPException as exc:
        require(exc.status_code == 403, "inactive login must return 403")
    else:
        raise AssertionError("inactive user logged in")

    token, _ttl = create_access_token(active_user.id)
    current = await get_current_user(
        authorization=f"Bearer {token}",
        session=AuthFakeSession(get_user=active_user),
    )
    require(current == CurrentUser(id=22, username="player_22", is_admin=False), "current user DB reload changed")

    try:
        await get_current_user(
            authorization=f"Bearer {token}",
            session=AuthFakeSession(get_user=inactive_user),
        )
    except HTTPException as exc:
        require(exc.status_code == 403, "inactive current user must return 403")
    else:
        raise AssertionError("inactive current user was accepted")

    try:
        await require_admin_user(CurrentUser(id=22, username="player_22", is_admin=False))
    except HTTPException as exc:
        require(exc.status_code == 403, "non-admin dependency must return 403")
    else:
        raise AssertionError("non-admin user passed the admin dependency")


def snapshot_row(*, character_id: str = "a" * 32, slot_index: int = 1):  # type: ignore[no-untyped-def]
    created_at = "2026-08-10T00:00:00+00:00"
    return SimpleNamespace(
        id=1,
        user_id=7,
        slot_key=account_character_slot_key(slot_index),
        client_save_key="idleRpgSaveV22",
        save_version=5,
        snapshot_json={"saveVersion": 5, "player": {"currentCharacterId": "weapon_master"}},
        summary_json={
            ACCOUNT_CHARACTER_SUMMARY_KEY: {
                "id": character_id,
                "slotIndex": slot_index,
                "name": "검신",
                "characterCode": "weapon_master",
                "createdAt": created_at,
            },
            "level": 1,
        },
        source="smoke",
        note=None,
        created_at=datetime(2026, 8, 10, tzinfo=UTC),
        updated_at=datetime(2026, 8, 10, tzinfo=UTC),
    )


async def test_character_slot_and_save_guards() -> None:
    require([account_character_slot_key(index) for index in range(1, 9)] == [f"character-{index}" for index in range(1, 9)], "slot keys changed")
    require(account_character_slot_index("character-8") == 8, "slot index parsing failed")
    require(account_character_slot_index("character-9") is None, "out-of-range slot was accepted")

    create = AccountCharacterCreateRequest(slotIndex=1, name="검신", characterCode="weapon_master")
    require(create.slot_index == 1 and create.character_code == "weapon_master", "character create schema changed")
    trimmed = AccountCharacterCreateRequest(slotIndex=1, name="  검신 01  ", characterCode="weapon_master")
    require(trimmed.name == "검신 01", "character name must trim surrounding whitespace")
    for unsafe_name in ("<script>", "검신&관리자", "검신\n관리자", "검신😀"):
        expect_validation_error(
            lambda unsafe_name=unsafe_name: AccountCharacterCreateRequest(
                slotIndex=1,
                name=unsafe_name,
                characterCode="weapon_master",
            ),
            f"unsafe character name was accepted: {unsafe_name!r}",
        )
    expect_validation_error(
        lambda: AccountCharacterCreateRequest(slotIndex=9, name="검신", characterCode="weapon_master"),
        "ninth character slot was accepted",
    )
    save = AccountCharacterGameSaveRequest(
        accountCharacterId="a" * 32,
        slotKey="character-1",
        snapshot={"saveVersion": 5, "player": {"currentCharacterId": "weapon_master"}},
        summary={},
    )
    require(save.account_character_id == "a" * 32, "account character id was not retained")
    expect_validation_error(
        lambda: AccountCharacterGameSaveRequest(
            accountCharacterId="a" * 32,
            snapshot={},
            summary={},
        ),
        "account character save accepted a missing slotKey",
    )
    expect_validation_error(
        lambda: AccountCharacterGameSaveRequest(
            accountCharacterId="a" * 32,
            slotKey="default",
            snapshot={},
            summary={},
        ),
        "legacy default slot was accepted for account character save",
    )

    row = snapshot_row()
    metadata = account_character_metadata(row)
    require(metadata is not None and metadata["id"] == "a" * 32, "character metadata parsing failed")

    listing = await AccountCharacterService().list_characters(FakeSession([row]), user_id=7)
    require(listing["slotCount"] == 8, "character list must always contain eight slots")
    require(len(listing["slots"]) == 8, "character slot list length changed")
    require(listing["occupiedCount"] == 1, "occupied slot count mismatch")
    require(
        isinstance(listing["slots"][0]["accountCharacterId"], str)
        and listing["slots"][0]["accountCharacterId"] == "a" * 32,
        "accountCharacterId response must remain a string",
    )
    require(
        listing["slots"][0]["slotKey"] == "character-1"
        and listing["slots"][0]["accountCharacter"]["slotIndex"] == 1,
        "account character slotKey/slotIndex contract changed",
    )

    stale_payload = SimpleNamespace(
        account_character_id="b" * 32,
        slot_key="character-1",
        snapshot={"saveVersion": 5, "player": {"currentCharacterId": "weapon_master"}},
        summary={},
        save_version=5,
        client_save_key="idleRpgSaveV22",
        source="smoke",
        note=None,
    )
    stale_session = FakeSession([row])
    try:
        await GameService().save_game_snapshot(stale_session, user_id=7, payload=stale_payload)
    except HTTPException as exc:
        require(exc.status_code == 409, "stale character UUID must return 409")
    else:
        raise AssertionError("stale character UUID was accepted")
    require(stale_session.commit_calls == 0, "stale save unexpectedly committed")

    oversized_payload = SimpleNamespace(
        account_character_id="a" * 32,
        slot_key="character-1",
        snapshot={"oversized": "x" * (SAVE_SNAPSHOT_MAX_SIZE_BYTES + 1)},
        summary={},
        save_version=5,
        client_save_key="idleRpgSaveV22",
        source="smoke",
        note=None,
    )
    oversized_session = FakeSession([row])
    try:
        await GameService().save_game_snapshot(oversized_session, user_id=7, payload=oversized_payload)
    except HTTPException as exc:
        require(exc.status_code == 413, "oversized save must return 413")
    else:
        raise AssertionError("oversized save was accepted")
    require(oversized_session.execute_calls == 0, "oversized save queried DB before failing closed")


def test_static_contract() -> None:
    sources = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "backend/app/core/security.py",
            "backend/app/services/auth_service.py",
            "backend/app/services/account_character_service.py",
            "backend/app/services/game_service.py",
            "backend/app/api/routes/auth.py",
            "backend/app/api/routes/account.py",
            "backend/app/api/routes/game.py",
            "backend/app/main.py",
            "backend/app/db/session.py",
            "backend/pyproject.toml",
            "backend/requirements/runtime.in",
        )
    }
    security = sources["backend/app/core/security.py"]
    require("hmac.compare_digest" in security, "constant-time token/key comparison missing")
    require("await session.get(User" in security, "current user DB reload missing")
    require("get_current_user_placeholder" not in security, "placeholder authentication alias remains")

    auth_service = sources["backend/app/services/auth_service.py"]
    require(auth_service.count("await run_in_threadpool(") >= 3, "bcrypt calls are not threadpool guarded")
    require("password_hash" not in auth_service.split("def serialize_user", 1)[1].split("async def register", 1)[0], "auth response serializer exposes password hash")

    account_routes = sources["backend/app/api/routes/account.py"]
    for marker in (
        '@router.get("/characters")',
        '@router.post("/characters")',
        '@router.delete("/characters/{account_character_id}")',
    ):
        require(marker in account_routes, f"missing account route: {marker}")
    require("/progress" not in account_routes, "unrequested progress-only destructive route remains")

    game_service = sources["backend/app/services/game_service.py"]
    require("_ensure_local_user" not in game_service, "local placeholder user creation remains")
    require("SAVE_SNAPSHOT_MAX_SIZE_BYTES = 2_000_000" in game_service, "2MB save limit missing")
    require("require_owned_character" in game_service, "save ownership guard missing")

    game_routes = sources["backend/app/api/routes/game.py"]
    master_block = game_routes.split('@router.get("/master-data")', 1)[1].split('@router.get("/load")', 1)[0]
    require("get_current_user" not in master_block, "public master-data unexpectedly requires auth")
    require("accountCharacterId" in game_routes, "load accountCharacterId query missing")
    require("AccountCharacterGameSaveRequest" in game_routes, "save accountCharacterId schema missing")

    main_source = sources["backend/app/main.py"]
    require("RequestValidationError" in main_source, "central request validation handler missing")
    require("sanitized.pop(\"input\", None)" in main_source, "sensitive validation input is not removed")
    db_session = sources["backend/app/db/session.py"]
    require("echo=False" in db_session, "SQLAlchemy echo was re-enabled")
    require("hide_parameters=True" in db_session, "SQLAlchemy parameter hiding missing")

    require('"bcrypt>=5.0.0"' in sources["backend/pyproject.toml"], "pyproject bcrypt dependency missing")
    require("bcrypt==5.0.0" in sources["backend/requirements/runtime.in"], "runtime bcrypt input missing")
    require("passlib" not in sources["backend/requirements/runtime.in"], "runtime input still declares passlib")


def main() -> None:
    test_password_and_token()
    test_auth_validation_secrets_are_not_reflected()
    asyncio.run(test_auth_service_and_current_user())
    asyncio.run(test_character_slot_and_save_guards())
    test_static_contract()
    print("OK: v370 account/auth backend focused smoke passed")


if __name__ == "__main__":
    main()
