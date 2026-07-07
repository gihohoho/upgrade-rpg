from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GameSavePayload(BaseModel):
    save_version: int = Field(alias="saveVersion")
    server_state: dict = Field(alias="serverState")


SAVE_SLOT_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class GameSaveSnapshotRequest(BaseModel):
    """Temporary raw-save payload used while migrating from localStorage to DB.

    The browser can send the current localStorage payload as-is in `snapshot`.
    Later stages can normalize this into user_profiles, item_instances, inventory,
    equipment, skills, mailbox, and records tables.
    """

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    save_version: int | None = Field(default=None, alias="saveVersion", ge=0, le=999)
    client_save_key: str = Field(default="idleRpgSaveV22", alias="clientSaveKey", min_length=1, max_length=120)
    slot_key: str = Field(default="default", alias="slotKey", min_length=1, max_length=80)
    snapshot: dict[str, Any] = Field(default_factory=dict)
    summary: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="localStorage", min_length=1, max_length=80)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("slot_key")
    @classmethod
    def validate_slot_key(cls, value: str) -> str:
        if not SAVE_SLOT_KEY_PATTERN.match(value):
            raise ValueError("slotKey는 영문/숫자/점(.)/언더바(_)/하이픈(-)만 사용할 수 있습니다.")
        return value


class MasterDataResponseData(BaseModel):
    characters: list[dict] = []
    skills: list[dict] = []
    items: list[dict] = []
    bosses: list[dict] = []
    field_zones: list[dict] = []
    enhancement_rules: list[dict] = []
