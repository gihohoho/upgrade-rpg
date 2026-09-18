"""No timed logout, while signatures and account revocation remain mandatory."""

import asyncio
from datetime import UTC, datetime, timedelta
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

os.environ["DEBUG"] = "false"
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "backend"))
from fastapi import HTTPException
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_current_user,
    InvalidAccessToken,
)
from app.core.config import settings


async def main():
    now = datetime.now(UTC)
    with patch.object(settings, "access_token_expire_minutes", 0):
        token, ttl = create_access_token(17, auth_version=3, now=now)
        assert ttl == 0
        for days in (1, 2, 30, 3650):
            claims = decode_access_token(token, now=now + timedelta(days=days))
            assert claims["authVersion"] == 3 and "exp" not in claims
        parts = token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        try:
            decode_access_token(".".join(parts))
        except InvalidAccessToken:
            pass
        else:
            raise AssertionError("tampered login accepted")
        account = SimpleNamespace(
            id=17,
            username="synthetic",
            auth_version=3,
            is_active=True,
            is_admin=False,
            email_original=None,
            email_canonical=None,
        )
        db = SimpleNamespace(get=AsyncMock(return_value=account))
        assert (await get_current_user("Bearer " + token, db)).id == 17
        for changes, expected in [
            ({"auth_version": 4}, 401),
            ({"auth_version": 3, "is_active": False}, 403),
        ]:
            for key, value in changes.items():
                setattr(account, key, value)
            try:
                await get_current_user("Bearer " + token, db)
            except HTTPException as error:
                assert error.status_code == expected
            else:
                raise AssertionError("revoked login accepted")
        with patch.object(settings, "access_token_expire_minutes", 1440):
            old, _ = create_access_token(17, now=now - timedelta(days=2))
        try:
            decode_access_token(old, now=now)
        except InvalidAccessToken:
            pass
        else:
            raise AssertionError("old expired login revived")
    print("v402 no automatic logout, signature/account revocation and old expiry: PASS")


if __name__ == "__main__":
    asyncio.run(main())
