from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUser:
    id: int
    username: str
    is_admin: bool = False


async def get_current_user_placeholder() -> CurrentUser:
    """Temporary dependency until real auth is implemented."""
    return CurrentUser(id=1, username="local-dev", is_admin=True)


from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_admin_write_dev_key(
    x_admin_dev_key: str | None = Header(default=None, alias="X-Admin-Dev-Key"),
) -> bool:
    """Temporary local-dev guard for admin write endpoints.

    This is not a replacement for real authentication. It only prevents accidental
    writes while the static admin page is being developed. Read-only admin APIs
    intentionally stay open for local diagnostics.
    """
    expected = str(settings.admin_write_dev_key or "").strip()
    provided = str(x_admin_dev_key or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_WRITE_DEV_KEY is not configured.",
        )
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 쓰기 dev key가 없거나 올바르지 않습니다.",
        )
    return True
