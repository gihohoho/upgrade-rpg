from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.account import (
    ACCOUNT_CHARACTER_ID_PATTERN,
    AccountCharacterCreateRequest,
)
from app.services.account_character_service import AccountCharacterService


router = APIRouter()
service = AccountCharacterService()


@router.get("/characters")
async def list_account_characters(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.list_characters(session, user_id=current_user.id)
    return ok_response(
        type="account.characters",
        payload=result,
        data={
            "status": result["status"],
            "slotCount": result["slotCount"],
            "occupiedCount": result["occupiedCount"],
        },
        meta={"storage": "user_save_snapshots", "rawSnapshotReturned": False},
    )


@router.post("/characters")
async def create_account_character(
    payload: AccountCharacterCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    character = await service.create_character(session, user_id=current_user.id, payload=payload)
    return ok_response(
        type="account.character.create",
        payload={"status": "created", "character": character},
        data={
            "status": "created",
            "slotIndex": character["slotIndex"],
            "accountCharacterId": character["accountCharacter"]["id"],
        },
        meta={"storage": "user_save_snapshots", "emptyProgressCreated": True},
    )


@router.delete("/characters/{account_character_id}")
async def delete_account_character(
    account_character_id: str = Path(
        ...,
        pattern=ACCOUNT_CHARACTER_ID_PATTERN.pattern,
        min_length=32,
        max_length=32,
    ),
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.delete_character(
        session,
        user_id=current_user.id,
        account_character_id=account_character_id,
    )
    character = result["character"]
    return ok_response(
        type="account.character.delete",
        payload=result,
        data={
            "status": result["status"],
            "slotIndex": character["slotIndex"],
            "accountCharacterId": character["accountCharacter"]["id"],
        },
        meta={"slotBecameEmpty": True, "progressDeleted": True},
    )
