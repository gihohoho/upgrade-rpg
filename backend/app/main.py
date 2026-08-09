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
from app.db.session import engine


SENSITIVE_VALIDATION_FIELDS = frozenset({"password", "passwordconfirm", "password_confirm"})
AUTH_VALIDATION_PATHS = frozenset(
    {
        f"{settings.api_prefix.rstrip('/')}/auth/login",
        f"{settings.api_prefix.rstrip('/')}/auth/register",
    }
)


def sanitize_request_validation_errors(
    request: Request,
    errors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Remove password-bearing validation input while preserving safe error detail."""
    request_path = request.url.path.rstrip("/")
    is_auth_request = request_path in AUTH_VALIDATION_PATHS
    sanitized_errors: list[dict[str, Any]] = []

    for error in errors:
        sanitized = dict(error)
        location = {
            str(part).replace("-", "_").lower()
            for part in sanitized.get("loc", ())
            if isinstance(part, str)
        }
        contains_sensitive_field = bool(location & SENSITIVE_VALIDATION_FIELDS)
        input_value = sanitized.get("input")
        contains_auth_body = is_auth_request and (
            isinstance(input_value, dict | list)
            or location == {"body"}
        )
        if contains_sensitive_field or contains_auth_body:
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
