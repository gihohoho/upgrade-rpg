from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.security import CurrentUser, create_access_token, hash_password, verify_password
from app.models import User, UserProfile
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    @staticmethod
    def serialize_current_user(current_user: CurrentUser) -> dict[str, Any]:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "isAdmin": current_user.is_admin,
        }

    @staticmethod
    def serialize_user(user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username,
            "isAdmin": bool(user.is_admin),
        }

    async def register(self, session: AsyncSession, payload: RegisterRequest) -> dict[str, Any]:
        existing = await session.execute(select(User.id).where(User.username == payload.username))
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 아이디입니다.",
            )

        password = payload.password.get_secret_value()
        password_hash = await run_in_threadpool(hash_password, password)
        user = User(
            username=payload.username,
            password_hash=password_hash,
            is_active=True,
            is_admin=False,
        )
        session.add(user)
        try:
            await session.flush()
            session.add(UserProfile(user_id=user.id))
            await session.commit()
            await session.refresh(user)
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 아이디입니다.",
            ) from exc
        except Exception:
            await session.rollback()
            raise

        token, expires_in = create_access_token(user.id)
        return {
            "status": "registered",
            "user": self.serialize_user(user),
            "accessToken": token,
            "tokenType": "bearer",
            "expiresIn": expires_in,
        }

    async def login(self, session: AsyncSession, payload: LoginRequest) -> dict[str, Any]:
        result = await session.execute(select(User).where(User.username == payload.username))
        user = result.scalar_one_or_none()
        password = payload.password.get_secret_value()

        if user is None or not user.password_hash:
            # Unknown accounts still perform one bcrypt operation so the most obvious
            # username timing distinction is not exposed by the async API.
            await run_in_threadpool(hash_password, password)
            raise self._invalid_credentials()

        password_ok = await run_in_threadpool(verify_password, password, user.password_hash)
        if not password_ok:
            raise self._invalid_credentials()
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="현재 이용이 중지된 계정입니다.",
            )

        token, expires_in = create_access_token(user.id)
        return {
            "status": "authenticated",
            "user": self.serialize_user(user),
            "accessToken": token,
            "tokenType": "bearer",
            "expiresIn": expires_in,
        }

    @staticmethod
    def _invalid_credentials() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
