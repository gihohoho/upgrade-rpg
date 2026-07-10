"""Static/runtime smoke test for the backend admin change log service split.

Run from the project root:

    python tools/smoke/contracts/smoke_backend_admin_change_log_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_change_log_service import AdminChangeLogService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    split_file = ROOT / "backend/app/services/admin/admin_change_log_service.py"
    package_file = ROOT / "backend/app/services/admin/__init__.py"

    assert_true(split_file.exists(), "missing admin_change_log_service.py")
    assert_true(package_file.exists(), "missing backend/app/services/admin/__init__.py")
    assert_true(issubclass(AdminService, AdminChangeLogService), "AdminService must keep the change log split service mixin in its MRO")

    split_methods = {
        "list_admin_change_logs",
        "get_admin_change_log_detail",
        "preview_admin_change_log_rollback",
        "apply_admin_change_log_rollback",
        "_clean_admin_change_log_filters",
        "_build_admin_change_log_where_clauses",
        "_admin_change_log_order_by",
        "_get_admin_change_log",
        "_empty_change_log_detail",
        "_empty_rollback_preview",
        "_serialize_admin_change_log_detail",
        "_build_change_log_changes",
        "_build_change_log_changes_with_relations",
        "_enrich_rollback_mismatches_with_relations",
        "_describe_change_log_relation_value",
        "_extract_master_change_target",
        "_current_master_values",
        "_count_admin_change_logs",
        "_serialize_admin_change_log",
    }
    shared_methods = {"_is_safe_admin_change_key"}
    for name in split_methods:
        assert_true(hasattr(AdminChangeLogService, name), f"split service missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited {name}")
    for name in shared_methods:
        assert_true(hasattr(AdminSharedUtilsService, name), f"shared utils missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited shared helper {name}")

    admin_direct = set(AdminService.__dict__.keys())
    split_direct = set(AdminChangeLogService.__dict__.keys())
    shared_direct = set(AdminSharedUtilsService.__dict__.keys())
    for name in split_methods:
        assert_true(name in split_direct, f"{name} should live directly on the change log split service")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")
    for name in shared_methods:
        assert_true(name in shared_direct, f"{name} should live directly on shared utils")
        assert_true(name not in split_direct, f"{name} should not be duplicated directly on change log service after v204")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    source = service_file.read_text(encoding="utf-8")
    split_source = split_file.read_text(encoding="utf-8")
    assert_true("from app.services.admin.admin_change_log_service import AdminChangeLogService" in source, "AdminService must import the change log split service")
    assert_true("AdminChangeLogService" in source and "class AdminService(" in source, "AdminService must inherit the change log split service")
    assert_true("class AdminChangeLogService" in split_source, "split file must define AdminChangeLogService")
    assert_true("except SQLAlchemyError" in split_source, "change-log list schema guard must move with the split")
    assert_true('"admin_change_logs_schema_unavailable_run_create_schema"' in split_source, "schema guard warning must be preserved")
    assert_true("return preview" in split_source[split_source.index("async def apply_admin_change_log_rollback"):], "rollback apply must return the updated preview payload")

    assert_true(len(source.splitlines()) < 1500, "admin_service.py should be smaller after the change log split")
    assert_true(len(split_source.splitlines()) >= 500, "split service should contain the change log implementation")
    assert_true(inspect.iscoroutinefunction(AdminService.list_admin_change_logs), "list_admin_change_logs should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.get_admin_change_log_detail), "get_admin_change_log_detail should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.preview_admin_change_log_rollback), "preview_admin_change_log_rollback should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.apply_admin_change_log_rollback), "apply_admin_change_log_rollback should remain async")

    service = AdminService()
    filters = service._clean_admin_change_log_filters(action="bad-action", changed_key="bad key!", sort="unknown")
    assert_true(filters["action"] is None, "invalid action should be dropped")
    assert_true(filters["changedKey"] is None, "unsafe changedKey should be dropped")
    assert_true(filters["sort"] == "created_desc", "invalid sort should fall back to created_desc")
    empty = service._empty_rollback_preview(status="not_found", change_log_id=0, warnings=["change_log_not_found"])
    assert_true(empty["rollbackReady"] is False and empty["writeBlocked"] is True, "empty rollback preview should stay guarded")

    print("backend admin change log service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
