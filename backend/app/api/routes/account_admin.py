from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.admin_response_helpers import admin_ok_response
from app.core.security import (
    CurrentUser,
    get_current_user,
    require_admin_user,
    require_admin_write_dev_key,
)
from app.db.session import get_db_session
from app.schemas.account_admin import (
    AccountAdminBootstrapRequest,
    AccountAdminStatusApplyRequest,
    AccountAdminStatusPreviewRequest,
)
from app.services.admin.account_user_management_service import AccountUserManagementService


router = APIRouter()
service = AccountUserManagementService()


def _meta(note: str) -> dict[str, str]:
    return {"source": "postgresql", "note": note}


@router.get("/bootstrap-status")
async def get_account_admin_bootstrap_status(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.get_bootstrap_status(session, current_user_id=current_user.id)
    return admin_ok_response(
        type="account_admin.bootstrap_status",
        payload=result,
        data={
            "status": result["status"],
            "bootstrapRequired": result["bootstrapRequired"],
            "canBootstrap": result["canBootstrap"],
        },
        meta=_meta("로그인 계정이 최초 관리자가 될 수 있는지 조회만 합니다."),
    )


@router.post("/bootstrap")
async def bootstrap_first_account_admin(
    payload: AccountAdminBootstrapRequest = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
    _write_guard: bool = Depends(require_admin_write_dev_key),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.bootstrap_first_admin(
        session,
        current_user_id=current_user.id,
        reason=payload.reason,
    )
    return admin_ok_response(
        type="account_admin.bootstrap",
        payload=result,
        data={"status": result["status"], "applied": result["applied"]},
        meta=_meta("로그인 가능한 관리자가 한 명도 없을 때만 현재 계정을 최초 관리자로 지정합니다."),
    )


@router.get("/users")
async def list_account_admin_users(
    page: int = Query(default=1, ge=1, le=100000),
    limit: int = Query(default=20, ge=1, le=100),
    query: str | None = Query(default=None, max_length=120),
    status_filter: str = Query(default="all", alias="status", max_length=20),
    sort: str = Query(default="created_desc", max_length=30),
    _admin_user: CurrentUser = Depends(require_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.list_users(
        session,
        page=page,
        limit=limit,
        query=query,
        account_status=status_filter,
        sort=sort,
    )
    return admin_ok_response(
        type="account_admin.users",
        payload=result,
        data={
            "status": result["status"],
            "count": result["count"],
            "total": result["total"],
            "page": result["page"],
        },
        meta=_meta("회원 계정 메타데이터와 캐릭터 슬롯 사용 수만 안전하게 조회합니다."),
    )


@router.get("/users/{user_id}")
async def get_account_admin_user_detail(
    user_id: int = Path(..., ge=1),
    _admin_user: CurrentUser = Depends(require_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.get_user_detail(session, user_id=user_id)
    return admin_ok_response(
        type="account_admin.user_detail",
        payload=result,
        data={"status": result["status"], "userId": user_id},
        meta=_meta("원본 저장 데이터 없이 회원 정보와 8개 캐릭터 슬롯 요약만 조회합니다."),
    )


@router.post("/users/{user_id}/status-preview")
async def preview_account_admin_user_status(
    payload: AccountAdminStatusPreviewRequest,
    user_id: int = Path(..., ge=1),
    admin_user: CurrentUser = Depends(require_admin_user),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.preview_status_change(
        session,
        admin_user_id=admin_user.id,
        user_id=user_id,
        base_is_active=payload.base_is_active,
        next_is_active=payload.next_is_active,
        reason=payload.reason,
    )
    return admin_ok_response(
        type="account_admin.user_status_preview",
        payload=result,
        data={
            "status": result["status"],
            "userId": user_id,
            "applyReady": result["applyReady"],
        },
        meta=_meta("회원 활성·정지 변경의 stale 상태와 안전 차단 조건을 쓰기 없이 확인합니다."),
    )


@router.post("/users/{user_id}/status-apply")
async def apply_account_admin_user_status(
    payload: AccountAdminStatusApplyRequest,
    user_id: int = Path(..., ge=1),
    admin_user: CurrentUser = Depends(require_admin_user),
    _write_guard: bool = Depends(require_admin_write_dev_key),
    session: AsyncSession = Depends(get_db_session),
):
    result = await service.apply_status_change(
        session,
        admin_user_id=admin_user.id,
        user_id=user_id,
        base_is_active=payload.base_is_active,
        next_is_active=payload.next_is_active,
        reason=payload.reason,
        confirm_text=payload.confirm_text,
    )
    return admin_ok_response(
        type="account_admin.user_status_apply",
        payload=result,
        data={
            "status": result["status"],
            "userId": user_id,
            "applied": result["applied"],
        },
        meta=_meta("관리자 권한, dev key, stale guard와 정확한 확인 문구를 모두 통과할 때만 상태를 변경합니다."),
    )
