from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Character, UserSaveSnapshot
from app.schemas.account import AccountCharacterCreateRequest, validate_account_character_id


ACCOUNT_CHARACTER_SLOT_COUNT = 8
ACCOUNT_CHARACTER_SUMMARY_KEY = "accountCharacter"
ACCOUNT_CHARACTER_SLOT_PREFIX = "character-"
ACCOUNT_CHARACTER_SOURCE_CREATE = "account-character-create"


def _serialize_summary_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def account_character_slot_key(slot_index: int) -> str:
    if slot_index < 1 or slot_index > ACCOUNT_CHARACTER_SLOT_COUNT:
        raise ValueError("slot_index_out_of_range")
    return f"{ACCOUNT_CHARACTER_SLOT_PREFIX}{slot_index}"


def account_character_slot_index(slot_key: str) -> int | None:
    if not str(slot_key).startswith(ACCOUNT_CHARACTER_SLOT_PREFIX):
        return None
    try:
        value = int(str(slot_key)[len(ACCOUNT_CHARACTER_SLOT_PREFIX) :])
    except ValueError:
        return None
    return value if 1 <= value <= ACCOUNT_CHARACTER_SLOT_COUNT else None


def account_character_metadata(snapshot: UserSaveSnapshot) -> dict[str, Any] | None:
    summary = snapshot.summary_json if isinstance(snapshot.summary_json, dict) else {}
    metadata = summary.get(ACCOUNT_CHARACTER_SUMMARY_KEY)
    if not isinstance(metadata, dict):
        return None
    character_id = str(metadata.get("id") or "").strip().lower()
    try:
        validate_account_character_id(character_id)
        slot_index = int(metadata.get("slotIndex"))
    except (TypeError, ValueError):
        return None
    if slot_index != account_character_slot_index(snapshot.slot_key):
        return None
    name = str(metadata.get("name") or "").strip()
    character_code = str(metadata.get("characterCode") or "").strip()
    created_at = str(metadata.get("createdAt") or "").strip()
    if not name or not character_code or not created_at:
        return None
    return {
        "id": character_id,
        "slotIndex": slot_index,
        "name": name,
        "characterCode": character_code,
        "createdAt": created_at,
    }


class AccountCharacterService:
    async def list_characters(self, session: AsyncSession, *, user_id: int) -> dict[str, Any]:
        rows = await self._owned_rows(session, user_id=user_id)
        by_slot = {row.slot_key: row for row in rows}
        slots: list[dict[str, Any]] = []
        for slot_index in range(1, ACCOUNT_CHARACTER_SLOT_COUNT + 1):
            slot_key = account_character_slot_key(slot_index)
            row = by_slot.get(slot_key)
            metadata = account_character_metadata(row) if row is not None else None
            slots.append(self._serialize_slot(slot_index, row, metadata))
        return {
            "status": "loaded",
            "slotCount": ACCOUNT_CHARACTER_SLOT_COUNT,
            "occupiedCount": len([slot for slot in slots if slot["occupied"]]),
            "slots": slots,
        }

    async def create_character(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        payload: AccountCharacterCreateRequest,
    ) -> dict[str, Any]:
        character_result = await session.execute(
            select(Character).where(
                Character.code == payload.character_code,
                Character.is_enabled.is_(True),
            )
        )
        if character_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="선택한 캐릭터를 현재 생성할 수 없습니다.",
            )

        slot_key = account_character_slot_key(payload.slot_index)
        existing_result = await session.execute(
            select(UserSaveSnapshot.id).where(
                UserSaveSnapshot.user_id == user_id,
                UserSaveSnapshot.slot_key == slot_key,
            )
        )
        if existing_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 캐릭터 슬롯입니다.",
            )

        metadata = {
            "id": uuid4().hex,
            "slotIndex": payload.slot_index,
            "name": payload.name,
            "characterCode": payload.character_code,
            "createdAt": datetime.now(UTC).isoformat(),
        }
        row = UserSaveSnapshot(
            user_id=user_id,
            slot_key=slot_key,
            client_save_key="idleRpgSaveV22",
            save_version=0,
            snapshot_json={},
            summary_json={ACCOUNT_CHARACTER_SUMMARY_KEY: metadata},
            source=ACCOUNT_CHARACTER_SOURCE_CREATE,
            note=None,
        )
        session.add(row)
        try:
            await session.commit()
            await session.refresh(row)
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 캐릭터 슬롯입니다.",
            ) from exc
        except Exception:
            await session.rollback()
            raise
        return self._serialize_slot(payload.slot_index, row, metadata)

    async def delete_character(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        account_character_id: str,
    ) -> dict[str, Any]:
        row, metadata = await self.require_owned_character(
            session,
            user_id=user_id,
            account_character_id=account_character_id,
        )
        deleted = self._serialize_slot(int(metadata["slotIndex"]), row, metadata)
        try:
            await session.delete(row)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return {"status": "deleted", "character": deleted}

    async def require_owned_character(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        account_character_id: str,
        slot_key: str | None = None,
    ) -> tuple[UserSaveSnapshot, dict[str, Any]]:
        normalized_id = validate_account_character_id(account_character_id)
        rows = await self._owned_rows(session, user_id=user_id)
        if slot_key is not None:
            row = next((candidate for candidate in rows if candidate.slot_key == slot_key), None)
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="캐릭터를 찾을 수 없습니다.",
                )
            metadata = account_character_metadata(row)
            if metadata is None or metadata["id"] != normalized_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="캐릭터 선택 정보가 오래되었거나 현재 슬롯과 일치하지 않습니다.",
                )
            return row, metadata

        for row in rows:
            metadata = account_character_metadata(row)
            if metadata and metadata["id"] == normalized_id:
                return row, metadata
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캐릭터를 찾을 수 없습니다.",
        )

    async def _owned_rows(self, session: AsyncSession, *, user_id: int) -> list[UserSaveSnapshot]:
        result = await session.execute(
            select(UserSaveSnapshot)
            .where(
                UserSaveSnapshot.user_id == user_id,
                UserSaveSnapshot.slot_key.in_(
                    [account_character_slot_key(index) for index in range(1, ACCOUNT_CHARACTER_SLOT_COUNT + 1)]
                ),
            )
            .order_by(UserSaveSnapshot.slot_key)
        )
        return list(result.scalars().all())

    @staticmethod
    def _serialize_slot(
        slot_index: int,
        row: UserSaveSnapshot | None,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if row is None:
            return {
                "slotIndex": slot_index,
                "slotKey": account_character_slot_key(slot_index),
                "occupied": False,
                "accountCharacterId": None,
                "accountCharacter": None,
                "progress": None,
            }
        if metadata is None:
            return {
                "slotIndex": slot_index,
                "slotKey": row.slot_key,
                "occupied": True,
                "unavailable": True,
                "accountCharacterId": None,
                "accountCharacter": None,
                "progress": None,
            }
        summary = row.summary_json if isinstance(row.summary_json, dict) else {}
        return {
            "slotIndex": slot_index,
            "slotKey": row.slot_key,
            "occupied": True,
            "accountCharacterId": str(metadata["id"]),
            "accountCharacter": dict(metadata),
            "progress": {
                "saveVersion": row.save_version,
                "gold": _serialize_summary_value(summary.get("gold")),
                "level": _serialize_summary_value(summary.get("level")),
                "currentZoneIndex": _serialize_summary_value(summary.get("currentZoneIndex")),
                "currentZoneType": _serialize_summary_value(summary.get("currentZoneType")),
                "updatedAt": _serialize_summary_value(row.updated_at),
            },
        }
