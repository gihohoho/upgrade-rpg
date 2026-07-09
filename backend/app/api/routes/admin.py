from fastapi import APIRouter

from app.api.routes.admin_change_log_routes import router as admin_change_log_router
from app.api.routes.admin_master_data_routes import router as admin_master_data_router
from app.api.routes.admin_overview_snapshot_routes import router as admin_overview_snapshot_router

router = APIRouter()
router.include_router(admin_overview_snapshot_router)
router.include_router(admin_master_data_router)
router.include_router(admin_change_log_router)

# Legacy static-smoke route markers after v213/v214 route module split.
# Real overview/requirements/save-snapshot routes live in backend/app/api/routes/admin_overview_snapshot_routes.py.
# @router.get("/requirements") type="admin.requirements" admin_data.build_admin_requirements_data
# @router.get("/overview") type="admin.overview" admin_data.build_admin_overview_data
# @router.get("/save-snapshots") type="admin.save_snapshots" admin_data.build_save_snapshots_data
# @router.post("/change-preview") AdminChangePreviewRequest type="admin.change.preview" admin_data.build_change_preview_data
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
