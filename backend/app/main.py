import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.core.auth_errors import AuthFlowHTTPException, auth_error_response
from app.core.config import settings
from app.db.session import AsyncSessionLocal, engine
from app.middleware.auth_ip_rate_limit import AuthIPRateLimitMiddleware
from app.middleware.request_body_limit import RequestBodyLimitMiddleware
from app.services.auth_email_outbox import run_auth_email_outbox_worker


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
    return auth_error_response(exc)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Run the durable mail worker and release pooled connections on shutdown."""
    stop_event: asyncio.Event | None = None
    worker_task: asyncio.Task[None] | None = None
    if (
        settings.email_outbox_worker_enabled
        and settings.brevo_ready
        and settings.auth_abuse_ready
    ):
        stop_event = asyncio.Event()
        worker_task = asyncio.create_task(
            run_auth_email_outbox_worker(
                stop_event=stop_event,
                session_factory=AsyncSessionLocal,
            ),
            name="auth-email-outbox-worker",
        )
    try:
        yield
    finally:
        if stop_event is not None and worker_task is not None:
            stop_event.set()
            try:
                await asyncio.wait_for(
                    worker_task,
                    timeout=float(settings.email_delivery_timeout_seconds) + 2.0,
                )
            except TimeoutError:
                worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await worker_task
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

    # Starlette wraps middleware in reverse registration order. Register the IP
    # gate before the body boundary so the effective request order is CORS ->
    # GZip -> body cap -> IP rate limit -> FastAPI parsing/dependencies.
    app.add_middleware(
        AuthIPRateLimitMiddleware,
        auth_path_prefix=f"{settings.api_prefix.rstrip('/')}/auth",
    )
    app.add_middleware(
        RequestBodyLimitMiddleware,
        global_max_bytes=settings.request_body_limit_bytes,
        auth_max_bytes=settings.auth_request_body_limit_bytes,
        auth_path_prefix=f"{settings.api_prefix.rstrip('/')}/auth",
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Retry-After"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
