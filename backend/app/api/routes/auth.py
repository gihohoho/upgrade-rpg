from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


router = APIRouter()
service = AuthService()


@router.post("/register")
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    registered = await service.register(session, payload)
    return ok_response(
        type="auth.register",
        payload=registered,
        data={"status": "registered", "user": registered["user"]},
        meta={"authMode": "bearer-signed-access-token"},
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    authenticated = await service.login(session, payload)
    return ok_response(
        type="auth.login",
        payload=authenticated,
        data={"status": "authenticated", "user": authenticated["user"]},
        meta={"authMode": "bearer-signed-access-token"},
    )


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    user = service.serialize_current_user(current_user)
    return ok_response(
        type="auth.me",
        payload={"status": "authenticated", "user": user},
        data={"status": "authenticated", "user": user},
        meta={"authMode": "bearer-signed-access-token"},
    )


@router.post("/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    return ok_response(
        type="auth.logout",
        payload={
            "status": "client_token_discard_required",
            "userId": current_user.id,
            "serverRevoked": False,
        },
        data={"status": "logged_out_on_client"},
        meta={
            "logoutMode": "client-token-discard",
            "note": "서버 세션 테이블이 없는 access token 방식이므로 클라이언트가 토큰을 즉시 폐기해야 합니다.",
        },
    )
