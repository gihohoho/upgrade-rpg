from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.response import error_response
from app.db.session import engine
from app.services.auth_service import AuthFlowHTTPException


SENSITIVE_VALIDATION_FIELDS = frozenset(
    {
        "password",
        "passwordconfirm",
        "password_confirm",
        "newpassword",
        "new_password",
        "token",
        "email",
        "identifier",
    }
)
AUTH_VALIDATION_PATHS = frozenset(
    {
        f"{settings.api_prefix.rstrip('/')}/auth/login",
        f"{settings.api_prefix.rstrip('/')}/auth/register",
        f"{settings.api_prefix.rstrip('/')}/auth/verify-email",
        f"{settings.api_prefix.rstrip('/')}/auth/resend-verification",
        f"{settings.api_prefix.rstrip('/')}/auth/recover-username",
        f"{settings.api_prefix.rstrip('/')}/auth/request-password-reset",
        f"{settings.api_prefix.rstrip('/')}/auth/reset-password",
        f"{settings.api_prefix.rstrip('/')}/auth/account-deletion/request",
        f"{settings.api_prefix.rstrip('/')}/auth/account-deletion/confirm",
    }
)


def sanitize_request_validation_errors(
    request: Request,
    errors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return loc/type/msg only for auth, otherwise remove sensitive input values."""
    request_path = request.url.path.rstrip("/")
    is_auth_request = request_path in AUTH_VALIDATION_PATHS
    if is_auth_request:
        return [
            {
                "loc": error.get("loc", ()),
                "type": str(error.get("type") or "value_error"),
                "msg": str(error.get("msg") or "요청 값이 올바르지 않습니다."),
            }
            for error in errors
        ]

    sanitized_errors: list[dict[str, Any]] = []

    for error in errors:
        sanitized = dict(error)
        location = {
            str(part).replace("-", "_").lower()
            for part in sanitized.get("loc", ())
            if isinstance(part, str)
        }
        contains_sensitive_field = bool(location & SENSITIVE_VALIDATION_FIELDS)
        if contains_sensitive_field:
            sanitized.pop("input", None)
        sanitized_errors.append(sanitized)

    return sanitized_errors


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Match FastAPI's 422 shape without reflecting authentication secrets."""
    errors = sanitize_request_validation_errors(request, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
    )


async def auth_flow_error_handler(
    _request: Request,
    exc: AuthFlowHTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = str(detail.get("code") or "auth_request_failed")[:80]
    message = str(detail.get("message") or "계정 요청을 처리하지 못했습니다.")[:300]
    return JSONResponse(
        status_code=int(exc.status_code),
        headers=exc.headers,
        content=error_response(
            type="auth.error",
            code=code,
            message=message,
            payload={"status": "error", "code": code},
            data={"status": "error"},
            meta={"sensitiveInputReturned": False},
        ),
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Release pooled DB connections on shutdown without running migrations."""
    try:
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(AuthFlowHTTPException, auth_flow_error_handler)

    # Large read-only master-data snapshots benefit from transport compression.
    # Register GZip first so the subsequently registered CORS middleware remains
    # the outer wrapper and also covers middleware-generated responses.
    app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
