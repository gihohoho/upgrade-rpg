from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUser:
    id: int
    username: str
    is_admin: bool = False


async def get_current_user_placeholder() -> CurrentUser:
    """Temporary dependency until real auth is implemented."""
    return CurrentUser(id=1, username="local-dev", is_admin=True)
