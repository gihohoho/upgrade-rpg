from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import ipaddress
from typing import Any, Literal

from fastapi import Request
from sqlalchemy import delete

from app.core.config import PRODUCTION_ENVIRONMENTS, Settings, settings
from app.db.session import AsyncSessionLocal
from app.models import AuthRateLimitBucket
from app.schemas.auth import EmailValidationUnavailable
from app.services.auth_rate_limiter import (
    AuthRateLimitDecision,
    AuthRateLimitKey,
    AuthRateLimitPolicy,
    AuthRateLimiter,
)


SubjectKind = Literal["email", "identifier", "token", "user"]


class AuthProtectionUnavailable(RuntimeError):
    """Raised when a request cannot be protected without trusting raw input."""


class AuthRateLimited(RuntimeError):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = max(1, int(retry_after_seconds))
        super().__init__("auth_rate_limited")


@dataclass(frozen=True)
class AuthProtectionContext:
    keyed_policies: tuple[tuple[AuthRateLimitKey, AuthRateLimitPolicy], ...]


@dataclass(frozen=True)
class AuthIPProtectionState:
    action: str
    context: AuthProtectionContext
    protection: Any


AUTH_IP_PROTECTION_STATE_KEY = "auth_ip_protection"


def combine_auth_protection_contexts(
    *contexts: AuthProtectionContext,
) -> AuthProtectionContext:
    return AuthProtectionContext(
        keyed_policies=tuple(
            keyed_policy
            for context in contexts
            for keyed_policy in context.keyed_policies
        )
    )


def _policy(
    *,
    window: int,
    requests: int,
    failures: int = 3,
) -> AuthRateLimitPolicy:
    return AuthRateLimitPolicy(
        window_seconds=window,
        max_requests=requests,
        failure_threshold=failures,
        failure_cooldown_base_seconds=5,
        failure_cooldown_max_seconds=min(300, window),
        failure_delay_base_seconds=0.2,
        failure_delay_max_seconds=2.0,
    )


AUTH_RATE_POLICIES: dict[str, dict[str, AuthRateLimitPolicy]] = {
    "register": {"ip": _policy(window=3600, requests=12), "subject": _policy(window=3600, requests=4)},
    "login": {"ip": _policy(window=900, requests=60, failures=8), "subject": _policy(window=900, requests=12)},
    "verify-email": {"ip": _policy(window=900, requests=30, failures=8), "subject": _policy(window=900, requests=10)},
    "resend-verification": {"ip": _policy(window=3600, requests=20), "subject": _policy(window=3600, requests=4)},
    "recover-username": {"ip": _policy(window=3600, requests=20), "subject": _policy(window=3600, requests=4)},
    "request-password-reset": {"ip": _policy(window=3600, requests=20), "subject": _policy(window=3600, requests=4)},
    "reset-password": {"ip": _policy(window=900, requests=30, failures=8), "subject": _policy(window=900, requests=8)},
    "account-deletion-request": {"ip": _policy(window=3600, requests=20), "subject": _policy(window=3600, requests=5)},
    "account-deletion-confirm": {"ip": _policy(window=900, requests=20, failures=8), "subject": _policy(window=900, requests=8)},
}


class AuthRequestProtection:
    def __init__(
        self,
        *,
        current_settings: Settings | None = None,
        limiter: AuthRateLimiter | None = None,
    ) -> None:
        self.settings = current_settings or settings
        self.limiter = limiter or AuthRateLimiter(
            session_factory=AsyncSessionLocal,
            hmac_secret=self.settings.auth_abuse_secret.get_secret_value(),
        )

    async def check(
        self,
        *,
        request: Request,
        action: str,
        subject_kind: SubjectKind,
        subject_value: str | int,
    ) -> AuthProtectionContext:
        ip_context = await self.check_ip(request=request, action=action)
        subject_context = await self.check_subject(
            action=action,
            subject_kind=subject_kind,
            subject_value=subject_value,
        )
        return combine_auth_protection_contexts(ip_context, subject_context)

    async def check_ip(
        self,
        *,
        request: Request,
        action: str,
    ) -> AuthProtectionContext:
        policies = self._policies_for_action(action)
        try:
            ip_key = self.limiter.key_for_ip(
                f"{action}:ip",
                self._client_ip(request),
            )
        except (TypeError, ValueError) as exc:
            raise AuthProtectionUnavailable("invalid_auth_rate_subject") from exc
        return await self._check_keyed_policies(((ip_key, policies["ip"]),))

    async def check_subject(
        self,
        *,
        action: str,
        subject_kind: SubjectKind,
        subject_value: str | int,
    ) -> AuthProtectionContext:
        policies = self._policies_for_action(action)
        try:
            subject_key = self._subject_key(
                action=action,
                subject_kind=subject_kind,
                subject_value=subject_value,
            )
        except EmailValidationUnavailable as exc:
            raise AuthProtectionUnavailable("email_validation_unavailable") from exc
        except (TypeError, ValueError) as exc:
            raise AuthProtectionUnavailable("invalid_auth_rate_subject") from exc
        return await self._check_keyed_policies(((subject_key, policies["subject"]),))

    async def _check_keyed_policies(
        self,
        keyed_policies: tuple[tuple[AuthRateLimitKey, AuthRateLimitPolicy], ...],
    ) -> AuthProtectionContext:
        retry_after = 0
        try:
            for key, policy in keyed_policies:
                decision = await self.limiter.check_request(key, policy)
                retry_after = max(retry_after, decision.retry_after_seconds)
        except Exception as exc:
            raise AuthProtectionUnavailable("auth_rate_store_unavailable") from exc
        if retry_after > 0:
            raise AuthRateLimited(retry_after)
        return AuthProtectionContext(keyed_policies=keyed_policies)

    @staticmethod
    def _policies_for_action(action: str) -> dict[str, AuthRateLimitPolicy]:
        policies = AUTH_RATE_POLICIES.get(action)
        if policies is None:
            raise AuthProtectionUnavailable("unknown_auth_rate_policy")
        return policies

    async def record_failure(self, context: AuthProtectionContext) -> None:
        decisions: list[AuthRateLimitDecision] = []
        try:
            for key, policy in context.keyed_policies:
                decisions.append(await self.limiter.record_failure(key, policy))
        except Exception as exc:
            raise AuthProtectionUnavailable("auth_rate_store_unavailable") from exc
        delay = max((item.response_delay_seconds for item in decisions), default=0.0)
        if delay > 0:
            await self.limiter.sleeper(delay)

    async def record_success(self, context: AuthProtectionContext) -> None:
        # A successful credential/token check clears only the account-specific
        # cooldown. The IP bucket keeps its aggregate failures to prevent one
        # valid login from resetting distributed identifier guesses.
        try:
            for key, _policy_value in context.keyed_policies:
                if key.scope.endswith(":ip"):
                    continue
                await self.limiter.record_success(key)
        except Exception as exc:
            raise AuthProtectionUnavailable("auth_rate_store_unavailable") from exc

    async def cleanup_expired(self) -> None:
        cutoff = datetime.now(UTC) - timedelta(
            days=int(self.settings.auth_rate_limit_retention_days)
        )
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(AuthRateLimitBucket).where(AuthRateLimitBucket.updated_at < cutoff)
            )
            await session.commit()

    def _subject_key(
        self,
        *,
        action: str,
        subject_kind: SubjectKind,
        subject_value: str | int,
    ) -> AuthRateLimitKey:
        scope = f"{action}:{subject_kind}"
        if subject_kind == "email":
            return self.limiter.key_for_email(scope, str(subject_value))
        if subject_kind == "identifier":
            return self.limiter.key_for_identifier(scope, str(subject_value))
        if subject_kind == "token":
            return self.limiter.key_for_token(scope, str(subject_value))
        return self.limiter.key_for_user_id(scope, int(subject_value))

    def _client_ip(self, request: Request) -> str:
        mode = self.settings.auth_trusted_proxy_mode.strip().lower()
        environment = self.settings.environment.strip().lower()
        raw_value = ""
        if mode == "render":
            # Render's Cloudflare edge overwrites this single-address header.
            # X-Forwarded-For is not used because a caller-controlled leftmost
            # entry can survive an append-only proxy chain.
            raw_value = str(request.headers.get("cf-connecting-ip") or "").strip()
            if not raw_value:
                raise AuthProtectionUnavailable("trusted_proxy_client_ip_missing")
        elif mode == "direct":
            raw_value = str(request.client.host if request.client else "").strip()
        else:
            raise AuthProtectionUnavailable("unsupported_auth_trusted_proxy_mode")

        try:
            return ipaddress.ip_address(raw_value).compressed
        except ValueError:
            if environment not in PRODUCTION_ENVIRONMENTS and mode == "direct":
                return "127.0.0.1"
            raise AuthProtectionUnavailable("trusted_client_ip_invalid") from None


auth_request_protection = AuthRequestProtection()
