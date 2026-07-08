from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user_placeholder, require_admin_write_dev_key
from app.db.session import get_db_session
from app.schemas.admin import AdminChangeLogRollbackApplyRequest, AdminChangeLogRollbackPreviewRequest, AdminChangePreviewRequest, AdminMasterDataCreatePreviewRequest, AdminMasterDataEditApplyRequest, AdminMasterDataEditPreviewRequest
from app.services.admin_service import AdminService

router = APIRouter()
service = AdminService()


@router.get("/requirements")
async def get_admin_requirements(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Temporary endpoint documenting the admin scope used for DB/backend design."""
    return ok_response(
        type="admin.requirements",
        data={
            "editableDomains": [
                "characters",
                "skills",
                "items",
                "bosses",
                "drop_tables",
                "field_zones",
                "enhancement_rules",
                "mailbox_rewards",
                "events",
                "users",
            ],
            "requiresChangeLog": True,
            "requiresRollback": True,
            "readOnlyOverviewReady": True,
            "adminUserId": current_user.id,
        },
    )


@router.get("/overview")
async def get_admin_readonly_overview(
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
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
    return ok_response(
        type="admin.overview",
        payload=overview,
        data={
            "status": overview["status"],
            "readOnly": overview["readOnly"],
            "adminUserId": current_user.id,
            "readiness": overview.get("readiness"),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 페이지 준비용 읽기 전용 overview API입니다. DB를 수정하지 않습니다.",
        },
    )


@router.get("/master-data/domains")
async def list_admin_master_catalog_domains(
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """List admin master-data catalog domains without returning row payloads."""
    domains = await service.list_master_catalog_domains(session)
    return ok_response(
        type="admin.master_data.domains",
        payload=domains,
        data={
            "status": domains["status"],
            "readOnly": domains["readOnly"],
            "adminUserId": current_user.id,
            "count": domains["count"],
            "defaultDomain": domains["defaultDomain"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 카탈로그 도메인 목록입니다. DB를 수정하지 않습니다.",
        },
    )


@router.get("/master-data/catalog")
async def list_admin_master_catalog_rows(
    domain: str = Query(default="itemTemplates", max_length=80),
    limit: int = Query(default=20, ge=1, le=200),
    page: int = Query(default=1, ge=1, le=100000),
    query: str | None = Query(default=None, max_length=120),
    enabled: str = Query(default="all", max_length=20),
    sort: str = Query(default="id_asc", max_length=30),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
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
    return ok_response(
        type="admin.master_data.catalog",
        payload=catalog,
        data={
            "status": catalog["status"],
            "readOnly": catalog["readOnly"],
            "adminUserId": current_user.id,
            "domain": catalog["domain"],
            "count": catalog["count"],
            "total": catalog["total"],
            "page": catalog["page"],
            "totalPages": catalog["totalPages"],
            "filters": catalog["filters"],
            "rawJsonReturned": catalog["rawJsonReturned"],
            "assetsReturned": catalog["assetsReturned"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 카탈로그 조회 전용 목록입니다. 원본 JSON과 이미지 data URL은 내려주지 않습니다.",
        },
    )





@router.get("/master-data/create-blueprint")
async def get_admin_master_create_blueprint(
    domain: str = Query(default="itemTemplates", max_length=80),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Return a read-only new-row blueprint for one master-data domain."""
    blueprint = await service.get_master_create_blueprint(session, domain=domain)
    return ok_response(
        type="admin.master_data.create_blueprint",
        payload=blueprint,
        data={
            "status": blueprint["status"],
            "readOnly": blueprint["readOnly"],
            "createApplyReady": blueprint["createApplyReady"],
            "adminUserId": current_user.id,
            "domain": blueprint["domain"],
            "fieldCount": blueprint.get("fieldCount", 0),
            "requiredFields": blueprint.get("requiredFields", []),
            "relationOptionsReturned": blueprint.get("relationOptionsReturned", False),
            "rawJsonReturned": blueprint.get("rawJsonReturned", False),
            "assetsReturned": blueprint.get("assetsReturned", False),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 신규 row 생성 준비용 read-only blueprint입니다. DB를 수정하지 않습니다.",
        },
    )


@router.post("/master-data/create-preview")
async def preview_admin_master_data_create(
    payload: AdminMasterDataCreatePreviewRequest = Body(...),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Validate a new-row draft without inserting anything."""
    preview = await service.preview_master_data_create(
        session,
        domain=payload.domain,
        draft=payload.draft,
        reason=payload.reason,
        dry_run=payload.dry_run,
    )
    return ok_response(
        type="admin.master_data.create_preview",
        payload=preview,
        data={
            "status": preview["status"],
            "readOnly": preview["readOnly"],
            "dryRun": preview["dryRun"],
            "writeBlocked": preview["writeBlocked"],
            "adminUserId": current_user.id,
            "domain": preview["domain"],
            "fieldCount": preview.get("fieldCount", 0),
            "errorCount": preview.get("errorCount", 0),
            "wouldBeValid": preview.get("wouldBeValid", False),
            "createApplyReady": preview.get("createApplyReady", False),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 신규 row 생성 초안 검증 전용입니다. DB insert는 아직 잠겨 있고, 이 API는 DB를 수정하지 않습니다.",
        },
    )


@router.get("/master-data/detail")
async def get_admin_master_catalog_detail(
    domain: str = Query(default="itemTemplates", max_length=80),
    id: int = Query(..., ge=1),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Return one sanitized read-only master-data row for the admin detail panel."""
    detail = await service.get_master_catalog_detail(
        session,
        domain=domain,
        row_id=id,
    )
    return ok_response(
        type="admin.master_data.detail",
        payload=detail,
        data={
            "status": detail["status"],
            "readOnly": detail["readOnly"],
            "adminUserId": current_user.id,
            "domain": detail["domain"],
            "id": detail["id"],
            "rawJsonReturned": detail["rawJsonReturned"],
            "sanitizedJsonReturned": detail["sanitizedJsonReturned"],
            "assetsReturned": detail["assetsReturned"],
            "safeForAdminWriteUi": detail["safeForAdminWriteUi"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 상세 조회 전용입니다. DB를 수정하지 않고, 이미지 data URL은 숨깁니다.",
        },
    )



@router.get("/master-data/relations")
async def get_admin_master_catalog_relations(
    domain: str = Query(default="itemTemplates", max_length=80),
    id: int = Query(..., ge=1),
    limit: int = Query(default=20, ge=1, le=80),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Return compact read-only related master-data rows for the admin detail panel."""
    relations = await service.get_master_catalog_relations(
        session,
        domain=domain,
        row_id=id,
        limit=limit,
    )
    return ok_response(
        type="admin.master_data.relations",
        payload=relations,
        data={
            "status": relations["status"],
            "readOnly": relations["readOnly"],
            "adminUserId": current_user.id,
            "domain": relations["domain"],
            "id": relations["id"],
            "groupCount": relations["groupCount"],
            "totalRelatedRows": relations["totalRelatedRows"],
            "rawJsonReturned": relations["rawJsonReturned"],
            "assetsReturned": relations["assetsReturned"],
            "safeForAdminWriteUi": relations["safeForAdminWriteUi"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 연결 항목 조회 전용입니다. 관련 행도 축약된 목록만 내려줍니다.",
        },
    )


@router.post("/master-data/edit-preview")
async def preview_admin_master_data_edit(
    payload: AdminMasterDataEditPreviewRequest = Body(...),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
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
    return ok_response(
        type="admin.master_data.edit_preview",
        payload=preview,
        data={
            "status": preview["status"],
            "readOnly": preview["readOnly"],
            "dryRun": preview["dryRun"],
            "adminUserId": current_user.id,
            "domain": preview["domain"],
            "id": preview["id"],
            "diffCount": preview["diffCount"],
            "errorCount": preview["errorCount"],
            "wouldBeValid": preview["wouldBeValid"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 편집 초안 검증 전용입니다. DB를 수정하지 않습니다.",
        },
    )



@router.post("/master-data/edit-apply")
async def apply_admin_master_data_edit(
    payload: AdminMasterDataEditApplyRequest = Body(...),
    _write_guard: bool = Depends(require_admin_write_dev_key),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
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
    return ok_response(
        type="admin.master_data.edit_apply",
        payload=applied,
        data={
            "status": applied["status"],
            "readOnly": applied.get("readOnly"),
            "dryRun": applied.get("dryRun"),
            "writeBlocked": applied.get("writeBlocked"),
            "applied": applied.get("applied", False),
            "adminUserId": current_user.id,
            "domain": applied.get("domain"),
            "id": applied.get("id"),
            "diffCount": applied.get("diffCount", 0),
            "errorCount": applied.get("errorCount", 0),
            "changeLogId": applied.get("changeLogId"),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 마스터 데이터 변경 적용 API입니다. X-Admin-Dev-Key, 확인 문구, allow-list를 통과한 스칼라 필드만 DB에 반영합니다.",
        },
    )


@router.get("/change-logs")
async def list_admin_change_logs(
    limit: int = Query(default=20, ge=1, le=100),
    target_type: str | None = Query(default=None, alias="targetType", max_length=120),
    target_id: str | None = Query(default=None, alias="targetId", max_length=160),
    action: str | None = Query(default=None, max_length=80),
    changed_key: str | None = Query(default=None, alias="changedKey", max_length=120),
    applied: bool | None = Query(default=None),
    sort: str | None = Query(default="created_desc", max_length=40),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """List compact admin change logs without returning full before/after JSON."""
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
    return ok_response(
        type="admin.change_logs",
        payload=logs,
        data={
            "status": logs["status"],
            "readOnly": logs["readOnly"],
            "adminUserId": current_user.id,
            "count": logs["count"],
            "total": logs["total"],
            "limit": logs["limit"],
            "filters": logs["filters"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 변경 이력 읽기 전용 목록입니다. before/after JSON 원본은 내려주지 않습니다.",
        },
    )


@router.get("/change-logs/{change_log_id}")
async def get_admin_change_log_detail(
    change_log_id: int,
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Return a safe scalar detail for one admin change log."""
    detail = await service.get_admin_change_log_detail(
        session,
        change_log_id=change_log_id,
    )
    return ok_response(
        type="admin.change_log.detail",
        payload=detail,
        data={
            "status": detail["status"],
            "readOnly": detail["readOnly"],
            "adminUserId": current_user.id,
            "id": detail.get("id"),
            "changedKeyCount": detail.get("changedKeyCount", 0),
            "rollbackAvailable": (detail.get("rollback") or {}).get("available", False),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 변경 이력 상세 조회입니다. before/after 전체 JSON 원본 대신 스칼라 변경 행만 내려줍니다.",
        },
    )


@router.post("/change-logs/{change_log_id}/rollback-preview")
async def preview_admin_change_log_rollback(
    change_log_id: int,
    payload: AdminChangeLogRollbackPreviewRequest | None = Body(default=None),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Preview a guarded rollback without mutating DB."""
    preview = await service.preview_admin_change_log_rollback(
        session,
        change_log_id=change_log_id,
        reason=payload.reason if payload else None,
    )
    return ok_response(
        type="admin.change_log.rollback_preview",
        payload=preview,
        data={
            "status": preview["status"],
            "readOnly": preview.get("readOnly"),
            "dryRun": preview.get("dryRun"),
            "writeBlocked": preview.get("writeBlocked"),
            "adminUserId": current_user.id,
            "changeLogId": preview.get("changeLogId"),
            "rollbackReady": preview.get("rollbackReady", False),
            "currentMatchesAfter": preview.get("currentMatchesAfter", False),
            "diffCount": preview.get("diffCount", 0),
            "errorCount": preview.get("errorCount", 0),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 변경 이력 되돌리기 미리보기입니다. 현재 DB 값이 이력의 after 값과 일치할 때만 rollbackReady가 true가 됩니다.",
        },
    )


@router.post("/change-logs/{change_log_id}/rollback-apply")
async def apply_admin_change_log_rollback(
    change_log_id: int,
    payload: AdminChangeLogRollbackApplyRequest = Body(...),
    _write_guard: bool = Depends(require_admin_write_dev_key),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """Apply a guarded rollback for a safe master-data change log."""
    result = await service.apply_admin_change_log_rollback(
        session,
        change_log_id=change_log_id,
        confirm_text=payload.confirm_text,
        reason=payload.reason,
        admin_user_id=current_user.id,
    )
    return ok_response(
        type="admin.change_log.rollback_apply",
        payload=result,
        data={
            "status": result["status"],
            "readOnly": result.get("readOnly"),
            "dryRun": result.get("dryRun"),
            "writeBlocked": result.get("writeBlocked"),
            "rolledBack": result.get("rolledBack", False),
            "adminUserId": current_user.id,
            "changeLogId": result.get("changeLogId"),
            "rollbackChangeLogId": result.get("rollbackChangeLogId"),
            "diffCount": result.get("diffCount", 0),
        },
        meta={
            "source": "postgresql",
            "note": "관리자 변경 이력 되돌리기 적용 API입니다. X-Admin-Dev-Key, 확인 문구, 현재값 검사를 통과한 경우에만 DB에 반영합니다.",
        },
    )


@router.get("/save-snapshots")
async def list_admin_save_snapshots(
    limit: int = Query(default=20, ge=1, le=100),
    user_id: int | None = Query(default=None, alias="userId", ge=1),
    slot_key: str | None = Query(default=None, alias="slotKey", max_length=80),
    source: str | None = Query(default=None, max_length=80),
    default_only: bool = Query(default=False, alias="defaultOnly"),
    sort: str = Query(default="updated_desc", max_length=30),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
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
    return ok_response(
        type="admin.save_snapshots",
        payload=snapshots,
        data={
            "status": snapshots["status"],
            "readOnly": snapshots["readOnly"],
            "adminUserId": current_user.id,
            "count": snapshots["count"],
            "total": snapshots["total"],
            "totalAll": snapshots["totalAll"],
            "limit": snapshots["limit"],
            "filters": snapshots["filters"],
        },
        meta={
            "source": "postgresql",
            "note": "관리자 페이지 준비용 세이브 스냅샷 읽기 전용 목록입니다. snapshot_json 원본은 내려주지 않습니다.",
        },
    )


@router.post("/change-preview")
async def preview_admin_change(
    payload: AdminChangePreviewRequest | None = Body(default=None),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
):
    """Future endpoint: validate an admin edit before applying it.

    Still read-only in this version. It echoes the requested before/after values and
    marks the result as preview-only so the browser cannot mistake it for an apply.
    """
    target_type = payload.target_type if payload else "unknown"
    before = payload.before if payload else {}
    after = payload.after if payload else {}
    preview = await service.preview_change(target_type, before, after)
    return ok_response(
        type="admin.change.preview",
        payload=preview,
        data={"status": "preview_only", "readOnly": True, "adminUserId": current_user.id},
        meta={"note": "관리자 변경 미리보기 API 초안입니다. 아직 DB를 수정하지 않습니다."},
    )
