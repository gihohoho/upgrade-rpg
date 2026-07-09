from fastapi import APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import admin_response_data_helpers as admin_data
from app.api.routes.admin_response_helpers import admin_ok_response
from app.api.routes.admin_response_meta_helpers import admin_route_meta
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
    MASTER_CATALOG_ENABLED_QUERY,
    MASTER_CATALOG_LIMIT_QUERY,
    MASTER_CATALOG_PAGE_QUERY,
    MASTER_CATALOG_SEARCH_QUERY,
    MASTER_CATALOG_SORT_QUERY,
    MASTER_DOMAIN_QUERY,
    MASTER_RELATIONS_LIMIT_QUERY,
    MASTER_ROW_ID_QUERY,
    SAVE_SNAPSHOT_DEFAULT_ONLY_QUERY,
    SAVE_SNAPSHOT_LIMIT_QUERY,
    SAVE_SNAPSHOT_SLOT_KEY_QUERY,
    SAVE_SNAPSHOT_SORT_QUERY,
    SAVE_SNAPSHOT_SOURCE_QUERY,
    SAVE_SNAPSHOT_USER_ID_QUERY,
)
from app.core.security import CurrentUser
from app.schemas.admin import AdminChangeLogRollbackApplyRequest, AdminChangeLogRollbackPreviewRequest, AdminChangePreviewRequest, AdminCreateDeleteApplyRequest, AdminCreateDeletePreviewRequest, AdminCreateDeleteRestoreApplyRequest, AdminCreateDeleteRestorePreviewRequest, AdminMasterDataCreateApplyRequest, AdminMasterDataCreatePreviewRequest, AdminMasterDataEditApplyRequest, AdminMasterDataEditPreviewRequest
from app.services.admin_service import AdminService

router = APIRouter()
service = AdminService()

# Guarded write-route metadata still documents X-Admin-Dev-Key through
# backend/app/api/routes/admin_response_meta_helpers.py. Keep this marker here
# for legacy static smoke tests while route response meta stays centralized.
# Legacy smoke marker: X-Admin-Dev-Key, 확인 문구, allow-list


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


@router.get("/master-data/domains")
async def list_admin_master_catalog_domains(
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """List admin master-data catalog domains without returning row payloads."""
    domains = await service.list_master_catalog_domains(session)
    return admin_ok_response(
        type="admin.master_data.domains",
        payload=domains,
        data=admin_data.build_master_domains_data(domains, current_user.id),
        meta=admin_route_meta("master_domains"),
    )


@router.get("/master-data/catalog")
async def list_admin_master_catalog_rows(
    domain: str = MASTER_DOMAIN_QUERY,
    limit: int = MASTER_CATALOG_LIMIT_QUERY,
    page: int = MASTER_CATALOG_PAGE_QUERY,
    query: str | None = MASTER_CATALOG_SEARCH_QUERY,
    enabled: str = MASTER_CATALOG_ENABLED_QUERY,
    sort: str = MASTER_CATALOG_SORT_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """List safe master-data rows for the read-only admin catalog.

    This is still read-only. It does not return inline assets or raw JSON blobs.
    """
    catalog = await service.list_master_catalog_rows(
        session,
        domain=domain,
        limit=limit,
        page=page,
        query=query,
        enabled=enabled,
        sort=sort,
    )
    return admin_ok_response(
        type="admin.master_data.catalog",
        payload=catalog,
        data=admin_data.build_master_catalog_data(catalog, current_user.id),
        meta=admin_route_meta("master_catalog"),
    )





@router.get("/master-data/create-blueprint")
async def get_admin_master_create_blueprint(
    domain: str = MASTER_DOMAIN_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Return a read-only new-row blueprint for one master-data domain."""
    blueprint = await service.get_master_create_blueprint(session, domain=domain)
    return admin_ok_response(
        type="admin.master_data.create_blueprint",
        payload=blueprint,
        data=admin_data.build_master_create_blueprint_data(blueprint, current_user.id),
        meta=admin_route_meta("master_create_blueprint"),
    )


@router.post("/master-data/create-preview")
async def preview_admin_master_data_create(
    payload: AdminMasterDataCreatePreviewRequest = Body(...),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Validate a new-row draft without inserting anything."""
    preview = await service.preview_master_data_create(
        session,
        domain=payload.domain,
        draft=payload.draft,
        reason=payload.reason,
        dry_run=payload.dry_run,
    )
    return admin_ok_response(
        type="admin.master_data.create_preview",
        payload=preview,
        data=admin_data.build_master_create_preview_data(preview, current_user.id),
        meta=admin_route_meta("master_create_preview"),
    )


@router.post("/master-data/create-apply")
async def apply_admin_master_data_create(
    payload: AdminMasterDataCreateApplyRequest = Body(...),
    _write_guard: bool = ADMIN_WRITE_GUARD_DEP,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Apply a guarded new master-data row insert for limited safe domains."""
    created = await service.apply_master_data_create(
        session,
        domain=payload.domain,
        draft=payload.draft,
        reason=payload.reason,
        confirm_text=payload.confirm_text,
        admin_user_id=current_user.id,
    )
    return admin_ok_response(
        type="admin.master_data.create_apply",
        payload=created,
        data=admin_data.build_master_create_apply_data(created, current_user.id),
        meta=admin_route_meta("master_create_apply"),
    )


@router.get("/master-data/detail")
async def get_admin_master_catalog_detail(
    domain: str = MASTER_DOMAIN_QUERY,
    id: int = MASTER_ROW_ID_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Return one sanitized read-only master-data row for the admin detail panel."""
    detail = await service.get_master_catalog_detail(
        session,
        domain=domain,
        row_id=id,
    )
    return admin_ok_response(
        type="admin.master_data.detail",
        payload=detail,
        data=admin_data.build_master_detail_data(detail, current_user.id),
        meta=admin_route_meta("master_detail"),
    )



@router.get("/master-data/relations")
async def get_admin_master_catalog_relations(
    domain: str = MASTER_DOMAIN_QUERY,
    id: int = MASTER_ROW_ID_QUERY,
    limit: int = MASTER_RELATIONS_LIMIT_QUERY,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Return compact read-only related master-data rows for the admin detail panel."""
    relations = await service.get_master_catalog_relations(
        session,
        domain=domain,
        row_id=id,
        limit=limit,
    )
    return admin_ok_response(
        type="admin.master_data.relations",
        payload=relations,
        data=admin_data.build_master_relations_data(relations, current_user.id),
        meta=admin_route_meta("master_relations"),
    )


@router.post("/master-data/edit-preview")
async def preview_admin_master_data_edit(
    payload: AdminMasterDataEditPreviewRequest = Body(...),
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Validate an admin master-data edit draft without applying it.

    This is the first safe bridge from read-only admin pages toward future writes:
    the browser can edit fields and ask FastAPI what would change, but the service
    never commits or flushes database mutations.
    """
    preview = await service.preview_master_data_edit(
        session,
        domain=payload.domain,
        row_id=payload.id,
        draft=payload.draft,
        base_values=payload.base_values,
        reason=payload.reason,
        dry_run=payload.dry_run,
    )
    return admin_ok_response(
        type="admin.master_data.edit_preview",
        payload=preview,
        data=admin_data.build_master_edit_preview_data(preview, current_user.id),
        meta=admin_route_meta("master_edit_preview"),
    )



@router.post("/master-data/edit-apply")
async def apply_admin_master_data_edit(
    payload: AdminMasterDataEditApplyRequest = Body(...),
    _write_guard: bool = ADMIN_WRITE_GUARD_DEP,
    current_user: CurrentUser = ADMIN_CURRENT_USER_DEP,
    session: AsyncSession = ADMIN_DB_SESSION_DEP,
):
    """Apply a guarded scalar master-data edit and create an admin change log.

    This endpoint is intentionally narrow: it only accepts allow-listed scalar fields
    and requires an exact confirmation phrase. It does not edit JSON/asset/relationship
    fields yet. The game runtime sees the changed master data after refresh/reload.
    """
    applied = await service.apply_master_data_edit(
        session,
        domain=payload.domain,
        row_id=payload.id,
        draft=payload.draft,
        base_values=payload.base_values,
        reason=payload.reason,
        confirm_text=payload.confirm_text,
        admin_user_id=current_user.id,
    )
    return admin_ok_response(
        type="admin.master_data.edit_apply",
        payload=applied,
        data=admin_data.build_master_edit_apply_data(applied, current_user.id),
        meta=admin_route_meta("master_edit_apply"),
    )


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
