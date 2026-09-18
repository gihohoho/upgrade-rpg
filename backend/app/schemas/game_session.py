from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GameSessionIdentity(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid", strict=True)
    slot_key: str = Field(alias="slotKey", pattern=r"^character-[1-8]$")
    account_character_id: str = Field(alias="accountCharacterId", pattern=r"^[0-9a-f]{32}$")


class GameSessionResume(GameSessionIdentity):
    session_key: str = Field(alias="sessionKey", pattern=r"^[0-9a-f]{64}$")


class GameCommand(GameSessionResume):
    request_id: str = Field(alias="requestId", pattern=r"^[A-Za-z0-9_-]{16,64}$")
    kind: Literal[
        "stop",
        "save",
        "town",
        "boss_zone",
        "field",
        "summon",
        "remove_boss",
        "auto_boss",
        "equip_drop",
        "auto_special",
        "equip",
        "unequip",
        "enhance",
        "move",
        "trash",
        "compact",
        "trash_all",
        "empty_trash",
        "reset_special",
        "beginner",
        "mail",
        "mail_all",
    ]
    args: dict = Field(default_factory=dict)
