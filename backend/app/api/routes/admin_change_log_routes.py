from fastapi import APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import admin_response_data_helpers as admin_data
from app.api.routes.admin_response_helpers import admin_ok_response
from app.api.routes.admin_response_meta_helpers import admin_route_meta
from app.api.routes.admin_route_services import create_admin_service
from app.services.admin.admin_preview_enrichment import enrich_admin_preview
from app.api.routes.admin_route_error_helpers import build_admin_change_logs_unavailable_payload
from app.api.routes.admin_route_params import (
    ADMIN_CURRENT_USER_DEP,
    ADMIN_DB_SESSION_DEP,
    ADMIN_WRITE_GUARD_DEP,
    CHANGE_LOG_ACTION_QUERY,
    CHANGE_LOG_APPLIED_QUERY,
    CHANGE_LOG_CHANGED_KEY_QUERY,
    CHANGE_LOG_LIMIT_QUERY,
    CHANGE_LOG_SORT_QUERY,
    CHANGE_LOG_TARGET_ID_QUERY,
    CHANGE_LOG_TARGET_TYPE_QUERY,
)
from app.core.security import CurrentUser
from app.schemas.admin import (
    AdminChangeLogRollbackApplyRequest,
    AdminChangeLogRollbackPreviewRequest,
    AdminCreateDeleteApplyRequest,
    AdminCreateDeletePreviewRequest,
    AdminCreateDeleteRestoreApplyRequest,
    AdminCreateDeleteRestorePreviewRequest,
)

router = APIRouter()
service = create_admin_service()

@router.get("/change-logs")
async def list_admin_change_logs(
    limit: int = CHANGE_LOG_LIMIT_QUERY,
    target_type: str | None = CHANGE_LOG_TARGET_TYPE_QUERY,
    target_id: str | None = CHANGE_LOG_TARGET_ID_QUERY,
    action: str | None = CHANGE_LOG_ACTION_QUERY,
    changed_key: str | None = CHANGE_LOG_CHANGED_KEY_QUERY,
    applied: bool | None = CHANGE_LOG_APPLIED_QUERY,
    sort: str | None = CHANGE_LOG_SORT_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """List compact admin change logs without returning full before/after JSON."""
    try:
        logs = await service.list_admin_change_logs(
            session,
            limit=limit,
            target_type=target_type,
            target_id=target_id,
            action=action,
            changed_key=changed_key,
            applied=applied,
            sort=sort,
        )
    except Exception as exc:  # pragma: no cover - local admin guard against unexpected dev DB/code drift
        try:
            await session.rollback()
        except Exception:
            pass
        logs = build_admin_change_logs_unavailable_payload(
            limit=limit,
            target_type=target_type,
            target_id=target_id,
            action=action,
            changed_key=changed_key,
            applied=applied,
            sort=sort,
            exc=exc,
        )
    return admin_ok_response(
        type="admin.change_logs",
        payload=logs,
        data=admin_data.build_change_logs_data(logs, current_user.id),
        meta=admin_route_meta("change_logs"),
    )


@router.get("/change-logs/{change_log_id}")
async def get_admin_change_log_detail(
    change_log_id: int,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Return a safe scalar detail for one admin change log."""
    detail = await service.get_admin_change_log_detail(
        session,
        change_log_id=change_log_id,
    )
    return admin_ok_response(
        type="admin.change_log.detail",
        payload=detail,
        data=admin_data.build_change_log_detail_data(detail, current_user.id),
        meta=admin_route_meta("change_log_detail"),
    )


@router.post("/change-logs/{change_log_id}/create-delete-preview")
async def preview_admin_create_delete_rollback(
    change_log_id: int,
    payload: AdminCreateDeletePreviewRequest | None = Body(default=None),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Preview safe deletion rollback for a row made by create-apply."""
    preview = await service.preview_admin_create_delete_rollback(
        session,
        change_log_id=change_log_id,
        reason=payload.reason if payload else None,
    )
    preview = enrich_admin_preview(preview, mode="delete", target_id=change_log_id)
    return admin_ok_response(
        type="admin.change_log.create_delete_preview",
        payload=preview,
        data=admin_data.build_create_delete_preview_data(preview, current_user.id),
        meta=admin_route_meta("create_delete_preview"),
    )


@router.post("/change-logs/{change_log_id}/create-delete-apply")
async def apply_admin_create_delete_rollback(
    change_log_id: int,
    payload: AdminCreateDeleteApplyRequest = Body(...),
    _write_guard: bool = ADMIN_WRITE_GUARD_DEP,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Apply a guarded deletion rollback for a row made by create-apply."""
    result = await service.apply_admin_create_delete_rollback(
        session,
        change_log_id=change_log_id,
        confirm_text=payload.confirm_text,
        reason=payload.reason,
        admin_user_id=current_user.id,
    )
    return admin_ok_response(
        type="admin.change_log.create_delete_apply",
        payload=result,
        data=admin_data.build_create_delete_apply_data(result, current_user.id),
        meta=admin_route_meta("create_delete_apply"),
    )


@router.post("/change-logs/{change_log_id}/create-delete-restore-preview")
async def preview_admin_create_delete_restore(
    change_log_id: int,
    payload: AdminCreateDeleteRestorePreviewRequest | None = Body(default=None),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Preview restoring a row deleted by create-delete apply without mutating DB."""
    preview = await service.preview_admin_create_delete_restore(
        session,
        change_log_id=change_log_id,
        reason=payload.reason if payload else None,
    )
    preview = enrich_admin_preview(preview, mode="restore", target_id=change_log_id)
    return admin_ok_response(
        type="admin.change_log.create_delete_restore_preview",
        payload=preview,
        data=admin_data.build_create_delete_restore_preview_data(preview, current_user.id),
        meta=admin_route_meta("create_delete_restore_preview"),
    )


@router.post("/change-logs/{change_log_id}/create-delete-restore-apply")
async def apply_admin_create_delete_restore(
    change_log_id: int,
    payload: AdminCreateDeleteRestoreApplyRequest = Body(...),
    _write_guard: bool = ADMIN_WRITE_GUARD_DEP,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Apply a guarded restore for a row deleted by create-delete apply."""
    result = await service.apply_admin_create_delete_restore(
        session,
        change_log_id=change_log_id,
        confirm_text=payload.confirm_text,
        reason=payload.reason,
        admin_user_id=current_user.id,
    )
    return admin_ok_response(
        type="admin.change_log.create_delete_restore_apply",
        payload=result,
        data=admin_data.build_create_delete_restore_apply_data(result, current_user.id),
        meta=admin_route_meta("create_delete_restore_apply"),
    )


@router.post("/change-logs/{change_log_id}/rollback-preview")
async def preview_admin_change_log_rollback(
    change_log_id: int,
    payload: AdminChangeLogRollbackPreviewRequest | None = Body(default=None),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Preview a guarded rollback without mutating DB."""
    preview = await service.preview_admin_change_log_rollback(
        session,
        change_log_id=change_log_id,
        reason=payload.reason if payload else None,
    )
    preview = enrich_admin_preview(preview, mode="rollback", target_id=change_log_id)
    return admin_ok_response(
        type="admin.change_log.rollback_preview",
        payload=preview,
        data=admin_data.build_rollback_preview_data(preview, current_user.id),
        meta=admin_route_meta("rollback_preview"),
    )


@router.post("/change-logs/{change_log_id}/rollback-apply")
async def apply_admin_change_log_rollback(
    change_log_id: int,
    payload: AdminChangeLogRollbackApplyRequest = Body(...),
    _write_guard: bool = ADMIN_WRITE_GUARD_DEP,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Apply a guarded rollback for a safe master-data change log."""
    result = await service.apply_admin_change_log_rollback(
        session,
        change_log_id=change_log_id,
        confirm_text=payload.confirm_text,
        reason=payload.reason,
        admin_user_id=current_user.id,
    )
    return admin_ok_response(
        type="admin.change_log.rollback_apply",
        payload=result,
        data=admin_data.build_rollback_apply_data(result, current_user.id),
        meta=admin_route_meta("rollback_apply"),
    )
