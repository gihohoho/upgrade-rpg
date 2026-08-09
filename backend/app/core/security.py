from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import json
import secrets
from typing import Any

import bcrypt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.models import User


ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "JWT"
ACCESS_TOKEN_KIND = "access"
ACCESS_TOKEN_CLOCK_SKEW_SECONDS = 60
ACCESS_TOKEN_MAX_LENGTH = 4096
BCRYPT_ROUNDS = 12


@dataclass(frozen=True)
class CurrentUser:
    id: int
    username: str
    is_admin: bool = False


class InvalidAccessToken(ValueError):
    """Raised when an access token is malformed, expired, or has a bad signature."""


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    if not value or any(character.isspace() for character in value):
        raise InvalidAccessToken("invalid_base64url")
    padding = "=" * (-len(value) % 4)
    try:
        return base64.b64decode(
            (value + padding).encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
    except (UnicodeEncodeError, ValueError) as exc:
        raise InvalidAccessToken("invalid_base64url") from exc


def _json_object(value: bytes) -> dict[str, Any]:
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidAccessToken("invalid_json") from exc
    if not isinstance(parsed, dict):
        raise InvalidAccessToken("token_json_must_be_an_object")
    return parsed


def hash_password(password: str) -> str:
    """Hash one validated password.

    The caller must run this CPU-heavy function in a worker thread when invoked
    from an async request path.
    """
    raw = password.encode("utf-8")
    if len(raw) > 72:
        raise ValueError("password_too_long_for_bcrypt")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify one password without leaking bcrypt parser errors.

    The caller must run this CPU-heavy function in a worker thread when invoked
    from an async request path.
    """
    try:
        raw = password.encode("utf-8")
        if len(raw) > 72:
            return False
        return bcrypt.checkpw(raw, password_hash.encode("ascii"))
    except (TypeError, ValueError, UnicodeEncodeError):
        return False


def create_access_token(
    user_id: int,
    *,
    now: datetime | None = None,
    nonce: str | None = None,
) -> tuple[str, int]:
    """Create a fixed-algorithm signed access token and return token/TTL seconds."""
    issued_at = now or datetime.now(UTC)
    if issued_at.tzinfo is None:
        issued_at = issued_at.replace(tzinfo=UTC)
    issued_at = issued_at.astimezone(UTC)
    ttl_seconds = max(60, int(settings.access_token_expire_minutes) * 60)
    expires_at = issued_at + timedelta(seconds=ttl_seconds)

    header = {"alg": ACCESS_TOKEN_ALGORITHM, "typ": ACCESS_TOKEN_TYPE}
    payload = {
        "sub": str(int(user_id)),
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "nonce": nonce or secrets.token_hex(16),
        "tokenType": ACCESS_TOKEN_KIND,
    }
    encoded_header = _base64url_encode(
        json.dumps(header, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}", ttl_seconds


def decode_access_token(token: str, *, now: datetime | None = None) -> dict[str, Any]:
    """Verify a signed access token with an exact header and bounded claims."""
    if not token or len(token) > ACCESS_TOKEN_MAX_LENGTH:
        raise InvalidAccessToken("invalid_token_length")
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidAccessToken("invalid_token_segments")

    encoded_header, encoded_payload, encoded_signature = parts
    header = _json_object(_base64url_decode(encoded_header))
    if header != {"alg": ACCESS_TOKEN_ALGORITHM, "typ": ACCESS_TOKEN_TYPE}:
        raise InvalidAccessToken("unsupported_token_header")

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    actual_signature = _base64url_decode(encoded_signature)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise InvalidAccessToken("invalid_signature")

    payload = _json_object(_base64url_decode(encoded_payload))
    if payload.get("tokenType") != ACCESS_TOKEN_KIND:
        raise InvalidAccessToken("invalid_token_type")
    try:
        user_id = int(payload["sub"])
        issued_at = int(payload["iat"])
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidAccessToken("invalid_token_claims") from exc
    nonce = payload.get("nonce")
    if user_id < 1 or not isinstance(nonce, str) or not nonce or len(nonce) > 128:
        raise InvalidAccessToken("invalid_token_claims")

    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    current_timestamp = int(current.astimezone(UTC).timestamp())
    if issued_at > current_timestamp + ACCESS_TOKEN_CLOCK_SKEW_SECONDS:
        raise InvalidAccessToken("token_issued_in_future")
    if expires_at <= current_timestamp:
        raise InvalidAccessToken("token_expired")
    if expires_at <= issued_at:
        raise InvalidAccessToken("invalid_token_lifetime")
    configured_ttl_seconds = max(60, int(settings.access_token_expire_minutes) * 60)
    if expires_at - issued_at > configured_ttl_seconds:
        raise InvalidAccessToken("token_lifetime_exceeds_limit")

    return {**payload, "userId": user_id}


def _bearer_token(authorization: str | None) -> str:
    value = str(authorization or "").strip()
    scheme, separator, token = value.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token or any(character.isspace() for character in token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_current_user(
    authorization: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUser:
    """Authenticate one bearer token and reload current account state from DB."""
    token = _bearer_token(authorization)
    try:
        claims = decode_access_token(token)
    except InvalidAccessToken as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인 정보가 만료되었거나 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await session.get(User, int(claims["userId"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인 정보를 확인할 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="현재 이용이 중지된 계정입니다.",
        )
    return CurrentUser(id=user.id, username=user.username, is_admin=bool(user.is_admin))


async def require_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


async def require_admin_write_dev_key(
    x_admin_dev_key: str | None = Header(default=None, alias="X-Admin-Dev-Key"),
) -> bool:
    """Additional fail-closed guard retained for dangerous admin writes."""
    expected = str(settings.admin_write_dev_key or "").strip()
    provided = str(x_admin_dev_key or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_WRITE_DEV_KEY is not configured.",
        )
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 쓰기 dev key가 없거나 올바르지 않습니다.",
        )
    return True
