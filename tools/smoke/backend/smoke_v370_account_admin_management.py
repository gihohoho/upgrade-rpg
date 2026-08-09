#!/usr/bin/env python3
"""DB-free safety smoke for authenticated account administration."""
from __future__ import annotations

from datetime import UTC, datetime
import os
from pathlib import Path
from types import SimpleNamespace
import sys
from typing import Any

from fastapi.routing import APIRoute
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.api.routes.account_admin import router  # noqa: E402
from app.schemas.account_admin import (  # noqa: E402
    AccountAdminStatusApplyRequest,
    AccountAdminStatusPreviewRequest,
)
from app.services.admin.account_user_management_service import (  # noqa: E402
    AccountUserManagementService,
)


FORBIDDEN_RESPONSE_KEYS = {
    "passwordhash",
    "password_hash",
    "accesstoken",
    "access_token",
    "snapshot",
    "snapshot_json",
    "token",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalized_key(value: Any) -> str:
    return "".join(character.lower() for character in str(value) if character.isalnum() or character == "_")


def assert_no_sensitive_response_keys(value: Any, path: str = "response") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            require(
                normalized_key(key) not in FORBIDDEN_RESPONSE_KEYS,
                f"sensitive key leaked at {path}.{key}",
            )
            assert_no_sensitive_response_keys(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            assert_no_sensitive_response_keys(nested, f"{path}[{index}]")


def user_row(
    *,
    user_id: int = 7,
    username: str = "manager",
    is_active: bool = True,
    is_admin: bool = False,
    password_hash: str | None = "$2b$12$not-a-real-hash",
) -> SimpleNamespace:
    stamp = datetime(2026, 8, 10, tzinfo=UTC)
    return SimpleNamespace(
        id=user_id,
        username=username,
        is_active=is_active,
        is_admin=is_admin,
        password_hash=password_hash,
        created_at=stamp,
        updated_at=stamp,
    )


def snapshot_row(
    *,
    slot_key: str = "character-3",
    slot_index: int = 3,
    character_id: str = "a" * 32,
    name: str = "검신",
) -> SimpleNamespace:
    stamp = datetime(2026, 8, 10, tzinfo=UTC)
    return SimpleNamespace(
        id=11,
        user_id=7,
        slot_key=slot_key,
        save_version=5,
        summary_json={
            "accountCharacter": {
                "id": character_id,
                "slotIndex": slot_index,
                "name": name,
                "characterCode": "weapon_master",
                "createdAt": stamp.isoformat(),
            },
            "level": 21,
            "gold": 12345,
            "currentZoneIndex": 4,
            "currentZoneType": "field",
        },
        updated_at=stamp,
    )


def test_route_dependencies() -> None:
    routes = {
        route.path: route
        for route in router.routes
        if isinstance(route, APIRoute)
    }
    expected = {
        "/bootstrap-status": {"get_current_user", "get_db_session"},
        "/bootstrap": {"require_admin_write_dev_key", "get_current_user", "get_db_session"},
        "/users": {"require_admin_user", "get_db_session"},
        "/users/{user_id}": {"require_admin_user", "get_db_session"},
        "/users/{user_id}/status-preview": {"require_admin_user", "get_db_session"},
        "/users/{user_id}/status-apply": {
            "require_admin_write_dev_key",
            "require_admin_user",
            "get_db_session",
        },
    }
    require(set(routes) == set(expected), "account-admin route set changed")
    for path, required_names in expected.items():
        dependency_order = [
            dependency.call.__name__
            for dependency in routes[path].dependant.dependencies
            if dependency.call is not None
        ]
        require(required_names <= set(dependency_order), f"{path} dependency guard changed: {dependency_order}")
        if path == "/bootstrap":
            require(
                dependency_order.index("get_current_user") < dependency_order.index("require_admin_write_dev_key"),
                "bootstrap must authenticate before checking the dev key",
            )
        if path == "/users/{user_id}/status-apply":
            require(
                dependency_order.index("require_admin_user") < dependency_order.index("require_admin_write_dev_key"),
                "status apply must authorize the administrator before checking the dev key",
            )


def test_safe_serialization_and_character_slots() -> None:
    service = AccountUserManagementService()
    malicious_name = '\"><img src=x onerror="window.pwned=1">'
    valid = snapshot_row(name=malicious_name)
    slots = service._build_character_slots([valid])
    require(len(slots) == 8, "admin detail must always return eight character slots")
    require(slots[2]["isEmpty"] is False, "valid character slot was not summarized")
    require(slots[2]["characterId"] == "a" * 32, "safe character UUID was not returned")
    require(slots[2]["name"] == malicious_name, "character name changed before frontend escaping")

    mismatched = snapshot_row(slot_key="character-4", slot_index=3)
    invalid_uuid = snapshot_row(character_id="not-a-uuid")
    rejected_slots = service._build_character_slots([mismatched, invalid_uuid])
    require(all(slot["isEmpty"] for slot in rejected_slots), "invalid accountCharacter metadata was accepted")

    serialized = service._serialize_user(
        user_row(username='\"><img src=x onerror="window.pwned=1">'),
        character_slots=slots,
    )
    require(serialized["characterSlotsUsed"] == 1, "character slot count mismatch")
    assert_no_sensitive_response_keys({"user": serialized, "characterSlots": slots})


def test_status_safety_contract() -> None:
    service = AccountUserManagementService()
    administrator = user_row(is_admin=True)

    self_preview = service._build_status_preview(
        administrator,
        admin_user_id=administrator.id,
        base_is_active=True,
        next_is_active=False,
        reason="본인 정지 시도",
        active_admin_count=2,
    )
    require("cannot_suspend_self" in self_preview["blockers"], "self-suspension was not blocked")

    last_preview = service._build_status_preview(
        administrator,
        admin_user_id=99,
        base_is_active=True,
        next_is_active=False,
        reason="마지막 관리자 정지 시도",
        active_admin_count=1,
    )
    require(
        "cannot_suspend_last_active_admin" in last_preview["blockers"],
        "last login-capable administrator suspension was not blocked",
    )

    legacy_admin = user_row(user_id=8, username="local-dev", is_admin=True, password_hash=None)
    legacy_preview = service._build_status_preview(
        legacy_admin,
        admin_user_id=99,
        base_is_active=True,
        next_is_active=False,
        reason="로그인 불가 과거 계정 정리",
        active_admin_count=1,
    )
    require(
        "cannot_suspend_last_active_admin" not in legacy_preview["blockers"],
        "password-less local-dev row was treated as the last real administrator",
    )

    stale_preview = service._build_status_preview(
        user_row(user_id=9),
        admin_user_id=99,
        base_is_active=False,
        next_is_active=False,
        reason="오래된 목록 상태 검사",
        active_admin_count=1,
    )
    require(stale_preview["status"] == "stale", "stale baseIsActive was not rejected")
    require(last_preview["confirmationText"] == "계정 정지: manager", "exact confirmation text changed")
    assert_no_sensitive_response_keys(last_preview)


def test_schema_and_source_guards() -> None:
    preview = AccountAdminStatusPreviewRequest(
        baseIsActive=True,
        nextIsActive=False,
        reason="  운영 정책 위반  ",
    )
    require(preview.reason == "운영 정책 위반", "status reason must be whitespace-trimmed")
    try:
        AccountAdminStatusPreviewRequest(baseIsActive=True, nextIsActive=False, reason="x")
    except ValidationError:
        pass
    else:
        raise AssertionError("one-character audit reason was accepted")
    apply = AccountAdminStatusApplyRequest(
        baseIsActive=True,
        nextIsActive=False,
        reason="운영 정책 위반",
        confirmText="계정 정지: manager",
    )
    require(apply.confirm_text == "계정 정지: manager", "confirmation alias changed")

    source = (BACKEND / "app/services/admin/account_user_management_service.py").read_text(encoding="utf-8")
    require("account_character_metadata(snapshot)" in source, "shared character metadata validator is not used")
    require("load_only(" in source, "member summary query loads the raw save payload")
    load_only_block = source.split("load_only(", 1)[1].split(")\n            )", 1)[0]
    require("snapshot_json" not in load_only_block, "member summary query explicitly loads raw snapshot_json")
    count_block = source.split("async def _count_active_admins", 1)[1].split("async def _snapshots_by_user", 1)[0]
    require("User.password_hash.is_not(None)" in count_block, "active admin count includes login-ineligible rows")
    lock_block = source.split("lock_stmt =", 1)[1].split("locked_users =", 1)[0]
    require("User.password_hash.is_not(None)" in lock_block, "status apply lock omits login-capable admin filter")
    require("AdminChangeLog(" in source, "account status/bootstrap writes lack an audit log")


def main() -> None:
    test_route_dependencies()
    test_safe_serialization_and_character_slots()
    test_status_safety_contract()
    test_schema_and_source_guards()
    print("OK: v370 authenticated account-admin management smoke passed")


if __name__ == "__main__":
    main()
