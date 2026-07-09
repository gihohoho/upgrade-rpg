from fastapi import APIRouter, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import admin_response_data_helpers as admin_data
from app.api.routes.admin_response_helpers import admin_ok_response
from app.api.routes.admin_response_meta_helpers import admin_route_meta
from app.api.routes.admin_route_services import create_admin_service
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

router = APIRouter()
service = create_admin_service()


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
    """Validate an admin edit preview without mutating DB data."""
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
