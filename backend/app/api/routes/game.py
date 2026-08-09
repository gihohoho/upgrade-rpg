from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.account import ACCOUNT_CHARACTER_ID_PATTERN, AccountCharacterGameSaveRequest
from app.services.game_service import GameService

router = APIRouter()
service = GameService()


@router.get("/master-data")
async def get_master_data(
    include_assets: bool = Query(
        default=False,
        alias="includeAssets",
        description="긴 SVG/data URL 이미지 문자열까지 포함하려면 true로 설정합니다.",
    ),
    session: AsyncSession = Depends(get_db_session),
):
    """Return master data imported from PostgreSQL seed tables.

    기본 응답에서는 백신 오탐과 과도한 응답 크기를 줄이기 위해 긴
    imageUrl/iconUrl data URL을 제외합니다. 로컬 디버깅 등으로 이미지 문자열이
    필요할 때만 `?includeAssets=true`를 붙여 요청합니다.
    """
    master_data = await service.get_master_data(session, include_assets=include_assets)
    return ok_response(
        type="game.master_data",
        payload=master_data,
        data={"status": "loaded"},
        meta={
            "source": "postgresql",
            "counts": master_data["counts"],
            "includeAssets": include_assets,
            "assetPolicy": master_data.get("assetPolicy"),
            "note": "PostgreSQL seed 데이터를 실제로 읽어온 응답입니다.",
        },
    )


@router.get("/load")
async def load_game(
    slot_key: str = Query(..., alias="slotKey", pattern=r"^character-[1-8]$"),
    account_character_id: str = Query(
        ...,
        alias="accountCharacterId",
        pattern=ACCOUNT_CHARACTER_ID_PATTERN.pattern,
        min_length=32,
        max_length=32,
    ),
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Load one account character save owned by the authenticated user."""
    save_data = await service.load_game(
        session,
        current_user.id,
        slot_key=slot_key,
        account_character_id=account_character_id,
    )
    return ok_response(
        type="game.load",
        payload=save_data,
        data={
            "status": save_data["status"],
            "userId": current_user.id,
            "slotKey": slot_key,
            "accountCharacterId": save_data["accountCharacterId"],
            "exists": save_data["exists"],
            "integrity": save_data.get("integrity"),
        },
        meta={"source": "postgresql", "note": "localStorage 원본 세이브 스냅샷 조회 API입니다."},
    )


@router.get("/save-slots")
async def list_save_slots(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List the authenticated account's character slots without raw save JSON."""
    slots_data = await service.list_save_slots(session, current_user.id)
    return ok_response(
        type="game.save_slots",
        payload=slots_data,
        data={
            "status": slots_data["status"],
            "userId": current_user.id,
            "count": slots_data["count"],
            "defaultSlot": slots_data.get("defaultSlot"),
            "latestSlot": slots_data.get("latestSlot"),
        },
        meta={
            "source": "postgresql",
            "note": "저장 슬롯 목록 조회 API입니다. 전체 snapshot_json은 내려주지 않습니다.",
        },
    )


@router.post("/save")
async def save_game(
    payload: AccountCharacterGameSaveRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Store a raw localStorage save snapshot in PostgreSQL.

    The normalized save tables already exist as drafts, but this snapshot bridge is
    the safest first migration step because it preserves the current browser save
    payload exactly.
    """
    saved = await service.save_game_snapshot(
        session,
        user_id=current_user.id,
        payload=payload,
    )
    return ok_response(
        type="game.save",
        payload=saved,
        data={
            "status": "saved",
            "userId": current_user.id,
            "slotKey": saved["slotKey"],
            "accountCharacterId": saved["accountCharacterId"],
            "saveVersion": saved["saveVersion"],
            "integrity": saved.get("integrity"),
        },
        meta={"source": "postgresql", "note": "localStorage 원본 세이브 스냅샷 저장 API입니다."},
    )
