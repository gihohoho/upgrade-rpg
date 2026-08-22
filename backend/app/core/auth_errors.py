from collections.abc import Mapping

from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.core.response import error_response


class AuthFlowHTTPException(HTTPException):
    """HTTP error carrying a stable, non-sensitive account-flow code."""


def auth_error(
    status_code: int,
    code: str,
    message: str,
    *,
    headers: Mapping[str, str] | None = None,
) -> AuthFlowHTTPException:
    return AuthFlowHTTPException(
        status_code=int(status_code),
        detail={"code": str(code)[:80], "message": str(message)[:300]},
        headers=dict(headers or {}),
    )


def auth_error_response(exc: AuthFlowHTTPException) -> JSONResponse:
    """Render one stable, non-reflective envelope for route and middleware errors."""
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = str(detail.get("code") or "auth_request_failed")[:80]
    message = str(detail.get("message") or "계정 요청을 처리하지 못했습니다.")[:300]
    response_meta: dict[str, object] = {"sensitiveInputReturned": False}
    retry_after = str((exc.headers or {}).get("Retry-After") or "").strip()
    if retry_after.isdigit():
        response_meta["retryAfterSeconds"] = max(1, int(retry_after))
    return JSONResponse(
        status_code=int(exc.status_code),
        headers=exc.headers,
        content=error_response(
            type="auth.error",
            code=code,
            message=message,
            payload={"status": "error", "code": code},
            data={"status": "error"},
            meta=response_meta,
        ),
    )


def auth_internal_error_response() -> JSONResponse:
    """Return the fixed envelope for an unexpected auth route failure."""
    code = "auth_internal_error"
    return JSONResponse(
        status_code=500,
        headers={"Cache-Control": "no-store"},
        content=error_response(
            type="auth.error",
            code=code,
            message="계정 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.",
            payload={"status": "error", "code": code},
            data={"status": "error"},
            meta={"sensitiveInputReturned": False},
        ),
    )
