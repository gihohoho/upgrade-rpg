from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user_placeholder
from app.db.session import get_db_session
from app.schemas.admin import AdminChangePreviewRequest
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


@router.get("/save-snapshots")
async def list_admin_save_snapshots(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user_placeholder),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent user save snapshots for admin diagnostics without raw snapshot JSON."""
    snapshots = await service.list_save_snapshot_summaries(session, limit=limit)
    return ok_response(
        type="admin.save_snapshots",
        payload=snapshots,
        data={
            "status": snapshots["status"],
            "readOnly": snapshots["readOnly"],
            "adminUserId": current_user.id,
            "count": snapshots["count"],
            "total": snapshots["total"],
            "limit": snapshots["limit"],
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
