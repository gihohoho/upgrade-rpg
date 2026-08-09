from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.game import GameSaveSnapshotRequest


ACCOUNT_CHARACTER_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
ACCOUNT_CHARACTER_SLOT_KEY_PATTERN = re.compile(r"^character-([1-8])$")
CHARACTER_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
ACCOUNT_CHARACTER_NAME_PATTERN = re.compile(r"^[가-힣A-Za-z0-9_. -]+$")


def validate_account_character_id(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if not ACCOUNT_CHARACTER_ID_PATTERN.fullmatch(normalized):
        raise ValueError("accountCharacterId 형식이 올바르지 않습니다.")
    return normalized


class AccountCharacterCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    slot_index: int = Field(alias="slotIndex", ge=1, le=8)
    name: str = Field(min_length=1, max_length=24)
    character_code: str = Field(alias="characterCode", min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not ACCOUNT_CHARACTER_NAME_PATTERN.fullmatch(value):
            raise ValueError("캐릭터 이름에는 한글, 영문, 숫자, 공백, _, -, .만 사용할 수 있습니다.")
        return value

    @field_validator("character_code")
    @classmethod
    def validate_character_code(cls, value: str) -> str:
        if not CHARACTER_CODE_PATTERN.fullmatch(value):
            raise ValueError("characterCode 형식이 올바르지 않습니다.")
        return value


class AccountCharacterGameSaveRequest(GameSaveSnapshotRequest):
    account_character_id: str = Field(alias="accountCharacterId")
    slot_key: str = Field(alias="slotKey", min_length=11, max_length=11)

    @field_validator("account_character_id")
    @classmethod
    def validate_character_id(cls, value: str) -> str:
        return validate_account_character_id(value)

    @field_validator("slot_key")
    @classmethod
    def validate_character_slot_key(cls, value: str) -> str:
        if not ACCOUNT_CHARACTER_SLOT_KEY_PATTERN.fullmatch(value):
            raise ValueError("slotKey는 character-1부터 character-8까지만 사용할 수 있습니다.")
        return value
