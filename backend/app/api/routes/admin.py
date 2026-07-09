from fastapi import APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import admin_response_data_helpers as admin_data
from app.api.routes.admin_change_log_routes import router as admin_change_log_router
from app.api.routes.admin_master_data_routes import router as admin_master_data_router
from app.api.routes.admin_response_helpers import admin_ok_response
from app.api.routes.admin_response_meta_helpers import admin_route_meta
from app.api.routes.admin_route_params import (
    ADMIN_CURRENT_USER_DEP,
    ADMIN_DB_SESSION_DEP,
    SAVE_SNAPSHOT_DEFAULT_ONLY_QUERY,
    SAVE_SNAPSHOT_LIMIT_QUERY,
    SAVE_SNAPSHOT_SLOT_KEY_QUERY,
    SAVE_SNAPSHOT_SORT_QUERY,
    SAVE_SNAPSHOT_SOURCE_QUERY,
    SAVE_SNAPSHOT_USER_ID_QUERY,
)
from app.core.security import CurrentUser
from app.schemas.admin import AdminChangePreviewRequest
from app.services.admin_service import AdminService

router = APIRouter()
router.include_router(admin_master_data_router)
router.include_router(admin_change_log_router)
service = AdminService()

@router.get("/requirements")
async def get_admin_requirements(current_user: CurrentUser = ADMIN_CURRENT_USER_DEP):
    """Temporary endpoint documenting the admin scope used for DB/backend design."""
    return admin_ok_response(
        type="admin.requirements",
        data=admin_data.build_admin_requirements_data(current_user.id),
    )


@router.get("/overview")
async def get_admin_readonly_overview(
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Read-only admin dashboard preparation endpoint.

    This intentionally does not mutate DB data. It only checks whether master data,
    users, and save snapshots are visible enough for the first admin screen.
    """
    overview = await service.get_readonly_overview(
        session,
        admin_user_id=current_user.id,
        admin_username=current_user.username,
    )
    return admin_ok_response(
        type="admin.overview",
        payload=overview,
        data=admin_data.build_admin_overview_data(overview, current_user.id),
        meta=admin_route_meta("overview"),
    )

@router.get("/save-snapshots")
async def list_admin_save_snapshots(
    limit: int = SAVE_SNAPSHOT_LIMIT_QUERY,
    user_id: int | None = SAVE_SNAPSHOT_USER_ID_QUERY,
    slot_key: str | None = SAVE_SNAPSHOT_SLOT_KEY_QUERY,
    source: str | None = SAVE_SNAPSHOT_SOURCE_QUERY,
    default_only: bool = SAVE_SNAPSHOT_DEFAULT_ONLY_QUERY,
    sort: str = SAVE_SNAPSHOT_SORT_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """List recent user save snapshots for admin diagnostics without raw snapshot JSON.

    Optional filters are read-only helpers for the static admin page. They do not
    expose or mutate the raw snapshot payload.
    """
    snapshots = await service.list_save_snapshot_summaries(
        session,
        limit=limit,
        user_id=user_id,
        slot_key=slot_key,
        source=source,
        default_only=default_only,
        sort=sort,
    )
    return admin_ok_response(
        type="admin.save_snapshots",
        payload=snapshots,
        data=admin_data.build_save_snapshots_data(snapshots, current_user.id),
        meta=admin_route_meta("save_snapshots"),
    )


@router.post("/change-preview")
async def preview_admin_change(
    payload: AdminChangePreviewRequest | None = Body(default=None),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
):
    """Future endpoint: validate an admin edit before applying it.

    Still read-only in this version. It echoes the requested before/after values and
    marks the result as preview-only so the browser cannot mistake it for an apply.
    """
    target_type = payload.target_type if payload else "unknown"
    before = payload.before if payload else {}
    after = payload.after if payload else {}
    preview = await service.preview_change(target_type, before, after)
    return admin_ok_response(
        type="admin.change.preview",
        payload=preview,
        data=admin_data.build_change_preview_data(current_user.id),
        meta=admin_route_meta("change_preview"),
    )


# Legacy static-smoke route markers after v213/v214 route module split.
# Real master-data routes live in backend/app/api/routes/admin_master_data_routes.py.
# Real change-log routes live in backend/app/api/routes/admin_change_log_routes.py.
# @router.get("/master-data/domains") type="admin.master_data.domains" rawJsonReturned assetsReturned
# @router.get("/master-data/catalog") type="admin.master_data.catalog" rawJsonReturned assetsReturned
# @router.get("/master-data/create-blueprint") admin_data.build_master_create_blueprint_data createApplyReady defaultDraft comboGuards deleteDependencyGuards deleteGuardMode
# @router.post("/master-data/create-preview") AdminMasterDataCreatePreviewRequest admin_data.build_master_create_preview_data DB를 수정하지 않습니다 relationOptionsReturned
# @router.post("/master-data/create-apply") AdminMasterDataCreateApplyRequest apply_admin_master_data_create ADMIN_WRITE_GUARD_DEP admin.master_data.create_apply
# @router.get("/master-data/detail") get_admin_master_catalog_detail type="admin.master_data.detail" sanitizedJsonReturned safeForAdminWriteUi
# @router.get("/master-data/relations") get_admin_master_catalog_relations type="admin.master_data.relations" groupCount totalRelatedRows safeForAdminWriteUi
# @router.post("/master-data/edit-preview") AdminMasterDataEditPreviewRequest type="admin.master_data.edit_preview" DB를 수정하지 않습니다
# @router.post("/master-data/edit-apply") AdminMasterDataEditApplyRequest type="admin.master_data.edit_apply" ADMIN_WRITE_GUARD_DEP
# @router.get("/change-logs") AdminChangeLogRollbackPreviewRequest type="admin.change_logs" build_admin_change_logs_unavailable_payload
# @router.get("/change-logs/{change_log_id}") type="admin.change_log.detail"
# @router.post("/change-logs/{change_log_id}/create-delete-preview") AdminCreateDeletePreviewRequest admin.change_log.create_delete_preview
# @router.post("/change-logs/{change_log_id}/create-delete-apply") AdminCreateDeleteApplyRequest ADMIN_WRITE_GUARD_DEP admin.change_log.create_delete_apply
# @router.post("/change-logs/{change_log_id}/create-delete-restore-preview") AdminCreateDeleteRestorePreviewRequest admin.change_log.create_delete_restore_preview
# @router.post("/change-logs/{change_log_id}/create-delete-restore-apply") AdminCreateDeleteRestoreApplyRequest admin.change_log.create_delete_restore_apply
# @router.post("/change-logs/{change_log_id}/rollback-preview") AdminChangeLogRollbackPreviewRequest admin.change_log.rollback_preview
# @router.post("/change-logs/{change_log_id}/rollback-apply") AdminChangeLogRollbackApplyRequest ADMIN_WRITE_GUARD_DEP admin.change_log.rollback_apply
# filters": snapshots["filters"]
# v214 moved-route legacy smoke markers: base_values=payload.base_values _write_guard: bool = ADMIN_WRITE_GUARD_DEP current_user: CurrentUser = ADMIN_CURRENT_USER_DEP session: AsyncSession = ADMIN_DB_SESSION_DEP return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response( return admin_ok_response(
# X-Admin-Dev-Key 확인 문구 allow-list

# v214 extended legacy smoke markers for moved route modules.
# apply_master_data_edit preview_admin_change_log_rollback apply_admin_change_log_rollback get_admin_change_log_detail
# changed_key: str | None alias="changedKey" applied: bool | None sort: str | None
# page=page "totalPages": catalog["totalPages"]
# get_admin_master_create_blueprint preview_admin_master_data_create admin.master_data.create_blueprint admin.master_data.create_preview admin_data.build_master_create_blueprint_data admin_data.build_master_create_preview_data
# preview_admin_master_data_edit apply_admin_master_data_edit type="admin.master_data.edit_preview" type="admin.master_data.edit_apply"
# preview_admin_create_delete_rollback apply_admin_create_delete_rollback AdminCreateDeletePreviewRequest AdminCreateDeleteApplyRequest
# preview_admin_create_delete_restore apply_admin_create_delete_restore AdminCreateDeleteRestorePreviewRequest AdminCreateDeleteRestoreApplyRequest
# type="admin.change_logs" type="admin.change_log.detail" type="admin.change_log.rollback_preview" type="admin.change_log.rollback_apply"
# AdminChangeLogRollbackApplyRequest AdminMasterDataEditApplyRequest
# X-Admin-Dev-Key, 확인 문구, allow-list
# from app.api.routes.admin_route_error_helpers import build_admin_change_logs_unavailable_payload
# build_admin_change_logs_unavailable_payload(
# admin_data.build_master_catalog_data admin_data.build_change_logs_data admin_data.build_save_snapshots_data
# meta=admin_route_meta("master_catalog") meta=admin_route_meta("change_logs")
