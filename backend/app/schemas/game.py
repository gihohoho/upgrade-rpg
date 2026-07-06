from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GameSavePayload(BaseModel):
    save_version: int = Field(alias="saveVersion")
    server_state: dict = Field(alias="serverState")


class GameSaveSnapshotRequest(BaseModel):
    """Temporary raw-save payload used while migrating from localStorage to DB.

    The browser can send the current localStorage payload as-is in `snapshot`.
    Later stages can normalize this into user_profiles, item_instances, inventory,
    equipment, skills, mailbox, and records tables.
    """

    model_config = ConfigDict(populate_by_name=True)

    save_version: int | None = Field(default=None, alias="saveVersion")
    client_save_key: str = Field(default="idleRpgSaveV22", alias="clientSaveKey")
    slot_key: str = Field(default="default", alias="slotKey")
    snapshot: dict[str, Any] = Field(default_factory=dict)
    summary: dict[str, Any] = Field(default_factory=dict)
    source: str = "localStorage"
    note: str | None = None


class MasterDataResponseData(BaseModel):
    characters: list[dict] = []
    skills: list[dict] = []
    items: list[dict] = []
    bosses: list[dict] = []
    field_zones: list[dict] = []
    enhancement_rules: list[dict] = []
