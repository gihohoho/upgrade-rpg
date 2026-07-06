from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

API_RESPONSE_VERSION = "game-api-response.v1"


def api_response(
    *,
    ok: bool,
    type: str,
    payload: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    logs: list[dict[str, Any]] | list[str] | None = None,
    effects: list[dict[str, Any]] | None = None,
    ui: dict[str, Any] | None = None,
    state_patch: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Return the response shape fixed in docs/API_RESPONSE_CONTRACT.md."""
    now = datetime.now(UTC)
    return {
        "ok": ok,
        "responseVersion": API_RESPONSE_VERSION,
        "type": type,
        "requestId": request_id or str(uuid4()),
        "serverTime": now.isoformat(),
        "createdAt": int(now.timestamp() * 1000),
        "payload": payload or {},
        "data": data or {},
        "logs": logs or [],
        "effects": effects or [],
        "ui": ui or {},
        "statePatch": state_patch or {},
        "meta": meta or {},
        "error": error,
    }


def ok_response(type: str, **kwargs: Any) -> dict[str, Any]:
    return api_response(ok=True, type=type, **kwargs)


def error_response(type: str, code: str, message: str, **kwargs: Any) -> dict[str, Any]:
    return api_response(ok=False, type=type, error={"code": code, "message": message}, **kwargs)
