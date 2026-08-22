from __future__ import annotations

import asyncio
from typing import Final

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.auth_errors import auth_internal_error_response
from app.core.response import error_response


DEFAULT_GLOBAL_REQUEST_BODY_MAX_BYTES: Final = 2_500_000
DEFAULT_AUTH_REQUEST_BODY_MAX_BYTES: Final = 16 * 1024
DEFAULT_AUTH_PATH_PREFIX: Final = "/api/v1/auth"


class RequestBodyLimitMiddleware:
    """Reject oversized HTTP bodies before FastAPI parses JSON.

    This is deliberately a small, pure-ASGI middleware instead of
    ``BaseHTTPMiddleware``. It validates ``Content-Length`` when present and also
    counts the actual ASGI body messages, so a missing or understated header
    cannot bypass the limit. The bounded body is replayed to the downstream app
    only after the complete request has passed validation.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        global_max_bytes: int = DEFAULT_GLOBAL_REQUEST_BODY_MAX_BYTES,
        auth_max_bytes: int = DEFAULT_AUTH_REQUEST_BODY_MAX_BYTES,
        auth_path_prefix: str = DEFAULT_AUTH_PATH_PREFIX,
    ) -> None:
        normalized_global_limit = int(global_max_bytes)
        normalized_auth_limit = int(auth_max_bytes)
        if normalized_global_limit < 1:
            raise ValueError("global_request_body_limit_must_be_positive")
        if normalized_auth_limit < 1:
            raise ValueError("auth_request_body_limit_must_be_positive")
        if normalized_auth_limit > normalized_global_limit:
            raise ValueError("auth_request_body_limit_must_not_exceed_global_limit")

        normalized_prefix = "/" + str(auth_path_prefix or "").strip().strip("/")
        if normalized_prefix == "/":
            raise ValueError("auth_request_body_path_prefix_required")

        self.app = app
        self.global_max_bytes = normalized_global_limit
        self.auth_max_bytes = normalized_auth_limit
        self.auth_path_prefix = normalized_prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        limit_bytes = self._limit_for_path(str(scope.get("path") or ""))
        declared_length = self._declared_content_length(scope)
        if declared_length is ... or (
            isinstance(declared_length, int) and declared_length > limit_bytes
        ):
            await self._send_too_large(scope, receive, send, limit_bytes=limit_bytes)
            return

        buffered_body = bytearray()
        received_bytes = 0
        disconnected = False

        while True:
            message = await receive()
            message_type = message.get("type")

            if message_type == "http.disconnect":
                disconnected = True
                break
            if message_type != "http.request":
                await self._send_too_large(scope, receive, send, limit_bytes=limit_bytes)
                return

            body = message.get("body", b"")
            if not isinstance(body, bytes):
                await self._send_too_large(scope, receive, send, limit_bytes=limit_bytes)
                return
            received_bytes += len(body)
            if received_bytes > limit_bytes:
                await self._send_too_large(scope, receive, send, limit_bytes=limit_bytes)
                return
            buffered_body.extend(body)
            if not bool(message.get("more_body", False)):
                break

        # A conflicting framing claim is rejected with the same non-reflective
        # 413 response. Uvicorn/ingress remain responsible for wire-level request
        # smuggling defenses, while this check prevents an understated ASGI
        # Content-Length from weakening the application cap.
        if isinstance(declared_length, int) and declared_length != received_bytes:
            await self._send_too_large(scope, receive, send, limit_bytes=limit_bytes)
            return

        replay_queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=1)
        if disconnected:
            replay_queue.put_nowait({"type": "http.disconnect"})
        else:
            replay_queue.put_nowait(
                {
                    "type": "http.request",
                    "body": bytes(buffered_body),
                    "more_body": False,
                }
            )

        async def replay_receive() -> Message:
            if not replay_queue.empty():
                return await replay_queue.get()
            if disconnected:
                return {"type": "http.disconnect"}
            return {"type": "http.request", "body": b"", "more_body": False}

        downstream_send = send
        is_auth_path = self._is_auth_path(str(scope.get("path") or ""))
        response_started = False
        if is_auth_path:

            async def send_auth_no_store(message: Message) -> None:
                nonlocal response_started
                if message.get("type") != "http.response.start":
                    await send(message)
                    return
                response_started = True
                protected_message = dict(message)
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != b"cache-control"
                ]
                headers.append((b"cache-control", b"no-store"))
                protected_message["headers"] = headers
                await send(protected_message)

            downstream_send = send_auth_no_store

        try:
            await self.app(scope, replay_receive, downstream_send)
        except Exception:
            if not is_auth_path or response_started:
                raise
            # Starlette's ServerErrorMiddleware wraps all user middleware, so
            # its 500 response would bypass the auth no-store send wrapper.  The
            # inner boundary must therefore render the stable auth envelope.
            response = auth_internal_error_response()
            await response(scope, receive, send)

    def _limit_for_path(self, path: str) -> int:
        if self._is_auth_path(path):
            return self.auth_max_bytes
        return self.global_max_bytes

    def _is_auth_path(self, path: str) -> bool:
        normalized_path = str(path or "").rstrip("/") or "/"
        return normalized_path == self.auth_path_prefix or normalized_path.startswith(
            f"{self.auth_path_prefix}/"
        )

    @staticmethod
    def _declared_content_length(scope: Scope) -> int | None | object:
        values: list[int] = []
        for raw_name, raw_value in scope.get("headers", []):
            if raw_name.lower() != b"content-length":
                continue
            try:
                decoded = raw_value.decode("ascii")
            except UnicodeDecodeError:
                return ...
            for part in decoded.split(","):
                normalized = part.strip()
                if not normalized or not normalized.isascii() or not normalized.isdigit():
                    return ...
                try:
                    values.append(int(normalized))
                except ValueError:
                    return ...

        if not values:
            return None
        if len(set(values)) != 1:
            return ...
        return values[0]

    @staticmethod
    async def _send_too_large(
        scope: Scope,
        receive: Receive,
        send: Send,
        *,
        limit_bytes: int,
    ) -> None:
        code = "request_body_too_large"
        response = JSONResponse(
            status_code=413,
            headers={"Cache-Control": "no-store"},
            content=error_response(
                type="request.body_too_large",
                code=code,
                message="요청 본문이 허용 크기를 초과했습니다.",
                payload={"status": "error", "code": code},
                data={"status": "error"},
                meta={"limitBytes": int(limit_bytes), "bodyParsed": False},
            ),
        )
        await response(scope, receive, send)
