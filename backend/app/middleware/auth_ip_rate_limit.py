from __future__ import annotations

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.auth_errors import auth_error, auth_error_response
from app.services.auth_request_protection import (
    AUTH_IP_PROTECTION_STATE_KEY,
    AuthIPProtectionState,
    AuthProtectionUnavailable,
    AuthRateLimited,
)


AUTH_IP_RATE_LIMIT_ACTION_SUFFIXES = {
    "/register": "register",
    "/login": "login",
    "/verify-email": "verify-email",
    "/resend-verification": "resend-verification",
    "/recover-username": "recover-username",
    "/request-password-reset": "request-password-reset",
    "/reset-password": "reset-password",
    "/account-deletion/request": "account-deletion-request",
    "/account-deletion/confirm": "account-deletion-confirm",
}


class AuthIPRateLimitMiddleware:
    """Consume the IP bucket before FastAPI parses an auth request body."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        auth_path_prefix: str,
    ) -> None:
        normalized_prefix = "/" + str(auth_path_prefix or "").strip().strip("/")
        if normalized_prefix == "/":
            raise ValueError("auth_rate_limit_path_prefix_required")
        self.app = app
        self.action_by_path = {
            f"{normalized_prefix}{suffix}": action
            for suffix, action in AUTH_IP_RATE_LIMIT_ACTION_SUFFIXES.items()
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http" or str(scope.get("method") or "").upper() != "POST":
            await self.app(scope, receive, send)
            return

        action = self.action_by_path.get(str(scope.get("path") or ""))
        if action is None:
            await self.app(scope, receive, send)
            return

        # Resolve the module variable per request so focused tests and future
        # dependency replacement cannot make middleware and route protection
        # disagree silently.
        from app.api.routes import auth as auth_routes

        active_protection = auth_routes.protection
        try:
            ip_context = await active_protection.check_ip(
                request=Request(scope),
                action=action,
            )
        except AuthRateLimited as exc:
            await auth_error_response(
                auth_error(
                    429,
                    "auth_rate_limited",
                    "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
                    headers={
                        "Retry-After": str(exc.retry_after_seconds),
                        "Cache-Control": "no-store",
                    },
                )
            )(scope, receive, send)
            return
        except AuthProtectionUnavailable:
            await auth_error_response(
                auth_error(
                    503,
                    "auth_protection_unavailable",
                    "계정 요청 보호 기능을 확인할 수 없습니다. 잠시 후 다시 시도해 주세요.",
                    headers={"Cache-Control": "no-store"},
                )
            )(scope, receive, send)
            return

        state = scope.setdefault("state", {})
        if not isinstance(state, dict):
            await auth_error_response(
                auth_error(
                    503,
                    "auth_protection_unavailable",
                    "계정 요청 보호 기능을 확인할 수 없습니다. 잠시 후 다시 시도해 주세요.",
                    headers={"Cache-Control": "no-store"},
                )
            )(scope, receive, send)
            return
        state[AUTH_IP_PROTECTION_STATE_KEY] = AuthIPProtectionState(
            action=action,
            context=ip_context,
            protection=active_protection,
        )
        await self.app(scope, receive, send)
