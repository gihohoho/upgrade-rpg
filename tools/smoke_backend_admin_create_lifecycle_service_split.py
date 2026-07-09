"""Static/runtime smoke test for the backend admin create lifecycle service split.

Run from the project root:

    python tools/smoke_backend_admin_create_lifecycle_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_create_lifecycle_service import AdminCreateLifecycleService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    split_file = ROOT / "backend/app/services/admin/admin_create_lifecycle_service.py"
    package_file = ROOT / "backend/app/services/admin/__init__.py"

    assert_true(split_file.exists(), "missing admin_create_lifecycle_service.py")
    assert_true(package_file.exists(), "missing backend/app/services/admin/__init__.py")
    assert_true(issubclass(AdminService, AdminCreateLifecycleService), "AdminService must keep the create lifecycle split service mixin in its MRO")

    split_methods = {
        "_master_create_lifecycle_dependency_guards",
        "_master_create_lifecycle_payload",
        "preview_master_data_create",
        "apply_master_data_create",
        "get_master_create_blueprint",
        "preview_admin_create_delete_rollback",
        "apply_admin_create_delete_rollback",
        "preview_admin_create_delete_restore",
        "apply_admin_create_delete_restore",
        "_empty_create_preview",
        "_empty_create_delete_preview",
        "_empty_create_delete_restore_preview",
        "_build_create_delete_dependency_checks",
        "_master_create_column_map",
        "_exists_duplicate_unique_value",
        "_create_combo_guard_labels",
        "_validate_master_create_relations",
        "_describe_master_create_relation_value",
        "_build_master_create_relation_options",
    }
    for name in split_methods:
        assert_true(hasattr(AdminCreateLifecycleService, name), f"split service missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited {name}")

    admin_direct = set(AdminService.__dict__.keys())
    split_direct = set(AdminCreateLifecycleService.__dict__.keys())
    for name in split_methods:
        assert_true(name in split_direct, f"{name} should live directly on the create lifecycle split service")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    source = service_file.read_text(encoding="utf-8")
    split_source = split_file.read_text(encoding="utf-8")
    assert_true("from app.services.admin.admin_create_lifecycle_service import AdminCreateLifecycleService" in source, "AdminService must import the create lifecycle split service")
    assert_true("AdminCreateLifecycleService" in source and "class AdminService(" in source, "AdminService must inherit the create lifecycle split service")
    assert_true("class AdminCreateLifecycleService" in split_source, "split file must define AdminCreateLifecycleService")

    assert_true(len(source.splitlines()) < 2200, "admin_service.py should be smaller after the create lifecycle split")
    assert_true(len(split_source.splitlines()) >= 1000, "split service should contain the create lifecycle implementation")
    assert_true(inspect.iscoroutinefunction(AdminService.preview_master_data_create), "preview_master_data_create should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.apply_master_data_create), "apply_master_data_create should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.get_master_create_blueprint), "get_master_create_blueprint should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.preview_admin_create_delete_restore), "preview_admin_create_delete_restore should remain async")

    service = AdminService()
    lifecycle = service._master_create_lifecycle_payload("skillLevels")
    assert_true(lifecycle["createApplyUnlocked"] is True, "skillLevels create apply should remain unlocked")
    assert_true(lifecycle["identityMode"] == "id", "skillLevels should remain id based")
    assert_true(lifecycle["confirmTexts"]["create"] == service.MASTER_CREATE_APPLY_CONFIRM_TEXT, "create confirm text should be preserved")
    assert_true(service._create_combo_guard_labels("characterSkills") == ["character_code + skill_code"], "combo guard labels should still work through facade")

    empty_preview = service._empty_create_preview(status="invalid_domain", domain="x", domain_label="x", warnings=["domain_invalid"])
    assert_true(empty_preview["status"] == "invalid_domain", "empty create preview helper should remain callable")
    assert_true(empty_preview["createApplyUnlocked"] is False, "invalid domain create apply should stay locked")
    column_map = service._master_create_column_map(service.MASTER_CATALOG_DOMAINS["skills"]["model"])
    assert_true("code" in column_map and "name" in column_map, "create column map should still inspect model columns")

    print("backend admin create lifecycle service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
