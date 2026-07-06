from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.db.session import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check():
    """FastAPI 앱 자체가 정상 실행 중인지 확인합니다."""
    return ok_response(type="system.health", data={"status": "ok"})


@router.get("/health/db")
async def database_health_check(session: AsyncSession = Depends(get_db_session)):
    """PostgreSQL 연결이 정상인지 확인합니다."""
    await session.execute(text("SELECT 1"))
    return ok_response(type="system.health.db", data={"status": "ok"})
