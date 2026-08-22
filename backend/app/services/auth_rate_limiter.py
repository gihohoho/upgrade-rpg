from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import ipaddress
import math
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_rate_limit import AuthRateLimitBucket
from app.schemas.auth import (
    EmailValidationUnavailable,
    NormalizedEmail,
    normalize_email_identity,
    normalize_username,
)


RATE_LIMIT_HMAC_DOMAIN = b"upgrade-rpg-auth-rate-limit-v1"
RATE_LIMIT_SCOPE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,79}$")
SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class AuthRateLimitKey:
    scope: str
    subject_digest: str

    def __post_init__(self) -> None:
        if not RATE_LIMIT_SCOPE_PATTERN.fullmatch(self.scope):
            raise ValueError("invalid_auth_rate_limit_scope")
        if not SHA256_HEX_PATTERN.fullmatch(self.subject_digest):
            raise ValueError("invalid_auth_rate_limit_subject_digest")


@dataclass(frozen=True)
class AuthRateLimitPolicy:
    window_seconds: int
    max_requests: int
    failure_threshold: int = 3
    failure_cooldown_base_seconds: int = 5
    failure_cooldown_max_seconds: int = 300
    failure_delay_base_seconds: float = 0.2
    failure_delay_max_seconds: float = 2.0

    def __post_init__(self) -> None:
        if int(self.window_seconds) < 1:
            raise ValueError("rate_limit_window_must_be_positive")
        if int(self.max_requests) < 1:
            raise ValueError("rate_limit_max_requests_must_be_positive")
        if int(self.failure_threshold) < 1:
            raise ValueError("rate_limit_failure_threshold_must_be_positive")
        if int(self.failure_cooldown_base_seconds) < 0:
            raise ValueError("rate_limit_failure_cooldown_base_must_not_be_negative")
        if int(self.failure_cooldown_max_seconds) < int(self.failure_cooldown_base_seconds):
            raise ValueError("rate_limit_failure_cooldown_max_too_small")
        if int(self.failure_cooldown_max_seconds) > int(self.window_seconds):
            raise ValueError("rate_limit_failure_cooldown_must_fit_window")
        if float(self.failure_delay_base_seconds) < 0:
            raise ValueError("rate_limit_failure_delay_base_must_not_be_negative")
        if float(self.failure_delay_max_seconds) < float(self.failure_delay_base_seconds):
            raise ValueError("rate_limit_failure_delay_max_too_small")


@dataclass(frozen=True)
class AuthRateLimitDecision:
    allowed: bool
    retry_after_seconds: int
    remaining_requests: int
    request_count: int
    failure_count: int
    response_delay_seconds: float = 0.0


SessionFactory = Callable[[], AsyncSession]
EmailNormalizer = Callable[[str], NormalizedEmail]
AsyncSleeper = Callable[[float], Awaitable[Any]]


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _bounded_exponential(base: float, maximum: float, exponent: int) -> float:
    if base <= 0 or maximum <= 0:
        return 0.0
    value = min(float(base), float(maximum))
    for _ in range(max(0, min(int(exponent), 63))):
        value = min(float(maximum), value * 2)
        if value >= maximum:
            break
    return value


class AuthRateLimiter:
    """PostgreSQL-backed fixed-window and repeated-failure limiter.

    Each operation owns a short, independent transaction. ``INSERT .. ON
    CONFLICT DO NOTHING`` creates a bucket, and ``SELECT .. FOR UPDATE`` then
    serializes concurrent decisions for that bucket. Expensive bcrypt work and
    any response delay happen only after the row lock has been released.
    """

    def __init__(
        self,
        *,
        session_factory: SessionFactory,
        hmac_secret: str,
        email_normalizer: EmailNormalizer | None = None,
        now_factory: Callable[[], datetime] | None = None,
        sleeper: AsyncSleeper | None = None,
    ) -> None:
        normalized_secret = str(hmac_secret or "").strip()
        if len(normalized_secret) < 32:
            raise ValueError("auth_rate_limit_hmac_secret_unavailable")
        self.session_factory = session_factory
        self._hmac_secret = normalized_secret.encode("utf-8")
        self.email_normalizer = email_normalizer or normalize_email_identity
        self.now_factory = now_factory or (lambda: datetime.now(UTC))
        self.sleeper = sleeper or asyncio.sleep

    def key_for_ip(self, scope: str, value: str) -> AuthRateLimitKey:
        try:
            address = ipaddress.ip_address(str(value or "").strip())
        except ValueError:
            raise ValueError("invalid_ip_rate_limit_subject") from None
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
            address = address.ipv4_mapped
        return self._key(scope, "ip", address.compressed)

    def key_for_email(self, scope: str, value: str) -> AuthRateLimitKey:
        try:
            canonical = self.email_normalizer(str(value or "")).canonical.strip().casefold()
        except EmailValidationUnavailable:
            raise
        except Exception:
            raise ValueError("invalid_email_rate_limit_subject") from None
        if not canonical or "@" not in canonical:
            raise ValueError("invalid_email_rate_limit_subject")
        return self._key(scope, "email", canonical)

    def key_for_username(self, scope: str, value: str) -> AuthRateLimitKey:
        try:
            normalized = normalize_username(str(value or ""))
        except ValueError:
            raise ValueError("invalid_username_rate_limit_subject") from None
        return self._key(scope, "username", normalized)

    def key_for_identifier(self, scope: str, value: str) -> AuthRateLimitKey:
        normalized = str(value or "").strip()
        if "@" in normalized:
            return self.key_for_email(scope, normalized)
        return self.key_for_username(scope, normalized)

    def key_for_token(self, scope: str, value: str) -> AuthRateLimitKey:
        normalized = str(value or "").strip()
        if not normalized or len(normalized) > 4096 or any(character.isspace() for character in normalized):
            raise ValueError("invalid_token_rate_limit_subject")
        return self._key(scope, "token", normalized)

    def key_for_user_id(self, scope: str, value: int) -> AuthRateLimitKey:
        normalized = int(value)
        if normalized < 1:
            raise ValueError("invalid_user_rate_limit_subject")
        return self._key(scope, "user", str(normalized))

    def _key(self, scope: str, subject_kind: str, normalized_value: str) -> AuthRateLimitKey:
        normalized_scope = str(scope or "").strip().lower()
        if not RATE_LIMIT_SCOPE_PATTERN.fullmatch(normalized_scope):
            raise ValueError("invalid_auth_rate_limit_scope")
        message = b"\x00".join(
            (
                RATE_LIMIT_HMAC_DOMAIN,
                normalized_scope.encode("ascii"),
                str(subject_kind).encode("ascii"),
                str(normalized_value).encode("utf-8"),
            )
        )
        digest = hmac.new(self._hmac_secret, message, hashlib.sha256).hexdigest()
        return AuthRateLimitKey(scope=normalized_scope, subject_digest=digest)

    async def check_request(
        self,
        key: AuthRateLimitKey,
        policy: AuthRateLimitPolicy,
    ) -> AuthRateLimitDecision:
        now = self._now()
        async with self.session_factory() as session:
            async with session.begin():
                bucket = await self._lock_or_create_bucket(session, key=key, now=now)
                self._reset_expired_window(bucket, policy=policy, now=now)
                bucket.request_count = int(bucket.request_count or 0) + 1
                bucket.last_attempt_at = now
                bucket.updated_at = now
                decision = self._decision(bucket, policy=policy, now=now)
        return decision

    async def record_failure(
        self,
        key: AuthRateLimitKey,
        policy: AuthRateLimitPolicy,
    ) -> AuthRateLimitDecision:
        now = self._now()
        async with self.session_factory() as session:
            async with session.begin():
                bucket = await self._lock_or_create_bucket(session, key=key, now=now)
                self._reset_expired_window(bucket, policy=policy, now=now)
                bucket.failure_count = int(bucket.failure_count or 0) + 1
                bucket.last_failure_at = now
                bucket.updated_at = now

                cooldown_seconds = self._failure_cooldown_seconds(
                    int(bucket.failure_count),
                    policy,
                )
                if cooldown_seconds > 0:
                    candidate = now + timedelta(seconds=cooldown_seconds)
                    current = (
                        _as_utc(bucket.blocked_until)
                        if bucket.blocked_until is not None
                        else None
                    )
                    bucket.blocked_until = candidate if current is None else max(current, candidate)

                decision = self._decision(
                    bucket,
                    policy=policy,
                    now=now,
                    response_delay_seconds=self._failure_delay_seconds(
                        int(bucket.failure_count),
                        policy,
                    ),
                )
        return decision

    async def record_success(self, key: AuthRateLimitKey) -> bool:
        now = self._now()
        async with self.session_factory() as session:
            async with session.begin():
                bucket = (
                    await session.execute(self.build_lock_statement(key))
                ).scalar_one_or_none()
                if bucket is None:
                    return False
                bucket.failure_count = 0
                bucket.blocked_until = None
                bucket.last_failure_at = None
                bucket.updated_at = now
        return True

    async def wait_after_failure(self, decision: AuthRateLimitDecision) -> None:
        delay = max(0.0, float(decision.response_delay_seconds))
        if delay > 0:
            await self.sleeper(delay)

    async def _lock_or_create_bucket(
        self,
        session: AsyncSession,
        *,
        key: AuthRateLimitKey,
        now: datetime,
    ) -> AuthRateLimitBucket:
        await session.execute(self.build_insert_statement(key, now=now))
        bucket = (await session.execute(self.build_lock_statement(key))).scalar_one()
        return bucket

    @staticmethod
    def build_insert_statement(key: AuthRateLimitKey, *, now: datetime):
        return (
            postgresql_insert(AuthRateLimitBucket)
            .values(
                scope=key.scope,
                subject_digest=key.subject_digest,
                window_started_at=now,
                request_count=0,
                failure_count=0,
                blocked_until=None,
                last_attempt_at=None,
                last_failure_at=None,
                created_at=now,
                updated_at=now,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    AuthRateLimitBucket.scope,
                    AuthRateLimitBucket.subject_digest,
                ]
            )
        )

    @staticmethod
    def build_lock_statement(key: AuthRateLimitKey):
        return (
            select(AuthRateLimitBucket)
            .where(
                AuthRateLimitBucket.scope == key.scope,
                AuthRateLimitBucket.subject_digest == key.subject_digest,
            )
            .execution_options(populate_existing=True)
            .with_for_update()
        )

    @staticmethod
    def _reset_expired_window(
        bucket: AuthRateLimitBucket,
        *,
        policy: AuthRateLimitPolicy,
        now: datetime,
    ) -> None:
        started_at = _as_utc(bucket.window_started_at)
        if started_at + timedelta(seconds=int(policy.window_seconds)) > now:
            return
        bucket.window_started_at = now
        bucket.request_count = 0
        bucket.failure_count = 0
        bucket.blocked_until = None
        bucket.last_failure_at = None

    @staticmethod
    def _failure_cooldown_seconds(
        failure_count: int,
        policy: AuthRateLimitPolicy,
    ) -> int:
        if int(failure_count) < int(policy.failure_threshold):
            return 0
        return int(
            _bounded_exponential(
                float(policy.failure_cooldown_base_seconds),
                float(policy.failure_cooldown_max_seconds),
                int(failure_count) - int(policy.failure_threshold),
            )
        )

    @staticmethod
    def _failure_delay_seconds(
        failure_count: int,
        policy: AuthRateLimitPolicy,
    ) -> float:
        if int(failure_count) < 1:
            return 0.0
        return float(
            _bounded_exponential(
                float(policy.failure_delay_base_seconds),
                float(policy.failure_delay_max_seconds),
                int(failure_count) - 1,
            )
        )

    @staticmethod
    def _decision(
        bucket: AuthRateLimitBucket,
        *,
        policy: AuthRateLimitPolicy,
        now: datetime,
        response_delay_seconds: float = 0.0,
    ) -> AuthRateLimitDecision:
        request_count = max(0, int(bucket.request_count or 0))
        failure_count = max(0, int(bucket.failure_count or 0))
        window_retry = 0
        if request_count > int(policy.max_requests):
            window_end = _as_utc(bucket.window_started_at) + timedelta(
                seconds=int(policy.window_seconds)
            )
            window_retry = max(1, math.ceil((window_end - now).total_seconds()))

        cooldown_retry = 0
        if bucket.blocked_until is not None and _as_utc(bucket.blocked_until) > now:
            cooldown_retry = max(
                1,
                math.ceil((_as_utc(bucket.blocked_until) - now).total_seconds()),
            )
        retry_after = max(window_retry, cooldown_retry)
        return AuthRateLimitDecision(
            allowed=retry_after == 0,
            retry_after_seconds=int(retry_after),
            remaining_requests=max(0, int(policy.max_requests) - request_count),
            request_count=request_count,
            failure_count=failure_count,
            response_delay_seconds=max(0.0, float(response_delay_seconds)),
        )

    def _now(self) -> datetime:
        return _as_utc(self.now_factory())
