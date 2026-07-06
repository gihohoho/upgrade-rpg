from typing import Any

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    code: str
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel):
    ok: bool
    responseVersion: str = "game-api-response.v1"
    type: str
    requestId: str | None = None
    serverTime: str | None = None
    createdAt: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)
    logs: list[Any] = Field(default_factory=list)
    effects: list[dict[str, Any]] = Field(default_factory=list)
    ui: dict[str, Any] = Field(default_factory=dict)
    statePatch: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    error: ApiError | None = None
