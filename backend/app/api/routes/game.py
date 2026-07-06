from fastapi import APIRouter, Depends

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user_placeholder

router = APIRouter()


@router.get("/master-data")
async def get_master_data(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: items, bosses, drops, fields, skills, enhancement rules."""
    return ok_response(
        type="game.master_data",
        data={"status": "stub", "userId": current_user.id},
        meta={"note": "마스터 데이터 seed 연결 전 임시 응답입니다."},
    )


@router.get("/load")
async def load_game(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: load user profile/progress/inventory/equipment/skills."""
    return ok_response(
        type="game.load",
        data={"status": "stub", "userId": current_user.id},
        meta={"note": "DB 저장 구조 연결 전 임시 응답입니다."},
    )


@router.post("/save")
async def save_game(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: temporary save bridge while migrating from localStorage."""
    return ok_response(
        type="game.save",
        data={"status": "stub", "userId": current_user.id},
    )
