from fastapi import APIRouter, Depends

from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user_placeholder

router = APIRouter()


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
            "adminUserId": current_user.id,
        },
    )


@router.post("/change-preview")
async def preview_admin_change(current_user: CurrentUser = Depends(get_current_user_placeholder)):
    """Future endpoint: validate an admin edit before applying it."""
    return ok_response(
        type="admin.change.preview",
        data={"status": "stub", "adminUserId": current_user.id},
        meta={"note": "관리자 변경 미리보기 API 초안입니다."},
    )
