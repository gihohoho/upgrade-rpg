from fastapi import APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import admin_response_data_helpers as admin_data
from app.api.routes.admin_response_helpers import admin_ok_response
from app.api.routes.admin_response_meta_helpers import admin_route_meta
from app.api.routes.admin_route_services import create_admin_service
from app.api.routes.admin_route_params import (
    ADMIN_CURRENT_USER_DEP,
    ADMIN_DB_SESSION_DEP,
    ADMIN_WRITE_GUARD_DEP,
    MASTER_CATALOG_ENABLED_QUERY,
    MASTER_CATALOG_LIMIT_QUERY,
    MASTER_CATALOG_PAGE_QUERY,
    MASTER_CATALOG_SEARCH_QUERY,
    MASTER_CATALOG_SORT_QUERY,
    MASTER_DOMAIN_QUERY,
    MASTER_RELATIONS_LIMIT_QUERY,
    MASTER_ROW_ID_QUERY,
)
from app.core.security import CurrentUser
from app.schemas.admin import (
    AdminMasterDataCreateApplyRequest,
    AdminMasterDataCreatePreviewRequest,
    AdminMasterDataEditApplyRequest,
    AdminMasterDataEditPreviewRequest,
)

router = APIRouter()
service = create_admin_service()

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
