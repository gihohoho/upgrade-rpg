from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user_placeholder
from app.db.session import get_db_session
from app.services.game_service import GameService

router = APIRouter()
service = GameService()


@router.get("/master-data")
async def get_master_data(
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Return master data imported from PostgreSQL seed tables."""
    master_data = await service.get_master_data(session)
    return ok_response(
        type="game.master_data",
        payload=master_data,
        data={"status": "loaded", "userId": current_user.id},
        meta={
            "source": "postgresql",
            "counts": master_data["counts"],
            "note": "PostgreSQL seed 데이터를 실제로 읽어온 응답입니다.",
        },
    )


@router.get("/load")
async def load_game(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: load user profile/progress/inventory/equipment/skills."""
    return ok_response(
        type="game.load",
        data=await service.load_game(current_user.id),
        meta={"note": "DB 저장 구조 연결 전 임시 응답입니다."},
    )


@router.post("/save")
async def save_game(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: temporary save bridge while migrating from localStorage."""
    return ok_response(
        type="game.save",
        data={"status": "stub", "userId": current_user.id},
    )
