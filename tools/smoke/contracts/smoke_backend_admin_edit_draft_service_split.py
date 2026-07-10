"""Static/runtime smoke test for the backend admin edit draft service split.

Run from the project root:

    python tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_edit_draft_service import AdminEditDraftService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    split_file = ROOT / "backend/app/services/admin/admin_edit_draft_service.py"
    package_file = ROOT / "backend/app/services/admin/__init__.py"

    assert_true(split_file.exists(), "missing admin_edit_draft_service.py")
    assert_true(package_file.exists(), "missing backend/app/services/admin/__init__.py")
    assert_true(issubclass(AdminService, AdminEditDraftService), "AdminService must keep the edit draft split service mixin in its MRO")

    split_methods = {
        "preview_master_data_edit",
        "apply_master_data_edit",
        "_empty_edit_preview",
        "_master_edit_column_map",
        "_master_edit_field_is_readonly",
        "_master_edit_field_is_allowed",
        "_master_relation_edit_field_is_open",
        "_validate_master_relation_edit_value",
        "_describe_master_relation_edit_value",
        "_build_proposed_combo_values",
        "_normalize_master_edit_value",
        "_master_edit_column_type",
    }
    shared_methods = {"_exists_by_code", "_fetch_code_name", "_exists_duplicate_combo"}
    for name in split_methods:
        assert_true(hasattr(AdminEditDraftService, name), f"split service missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited {name}")
    for name in shared_methods:
        assert_true(hasattr(AdminSharedUtilsService, name), f"shared utils missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited shared helper {name}")

    admin_direct = set(AdminService.__dict__.keys())
    split_direct = set(AdminEditDraftService.__dict__.keys())
    shared_direct = set(AdminSharedUtilsService.__dict__.keys())
    for name in split_methods:
        assert_true(name in split_direct, f"{name} should live directly on the edit draft split service")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")
    for name in shared_methods:
        assert_true(name in shared_direct, f"{name} should live directly on shared utils")
        assert_true(name not in split_direct, f"{name} should not be duplicated directly on edit draft service after v204")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    source = service_file.read_text(encoding="utf-8")
    split_source = split_file.read_text(encoding="utf-8")
    assert_true("from app.services.admin.admin_edit_draft_service import AdminEditDraftService" in source, "AdminService must import the edit draft split service")
    assert_true("AdminEditDraftService" in source and "class AdminService(" in source, "AdminService must inherit the edit draft split service")
    assert_true("class AdminEditDraftService" in split_source, "split file must define AdminEditDraftService")
    assert_true("AdminChangeLog(" in split_source, "guarded edit apply must still write an admin change log")
    assert_true('action="update"' in split_source, "edit apply must keep update action logging")
    assert_true("base_values_required_for_apply" in split_source, "stale guard base value requirement must be preserved")
    assert_true("duplicate_skill_code_level" in split_source, "combo duplicate guard must be preserved")
    assert_true("relation_target_not_found_enhancement_group" in split_source, "relation validation guard must be preserved")
    assert_true("_normalize_master_edit_value" in split_source, "normalizer must move with edit draft service")
    assert_true(len(source.splitlines()) < 800, "admin_service.py should be smaller after the edit draft split")
    assert_true(len(split_source.splitlines()) >= 560, "split service should contain the edit draft implementation")
    assert_true(inspect.iscoroutinefunction(AdminService.preview_master_data_edit), "preview_master_data_edit should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.apply_master_data_edit), "apply_master_data_edit should remain async")

    service = AdminService()
    empty = service._empty_edit_preview(status="invalid_domain", domain="bad", domain_label="bad", row_id=0, warnings=["domain_invalid"])
    assert_true(empty["writeBlocked"] is True and empty["applyReady"] is False, "empty edit preview should stay guarded")
    assert_true(service._master_edit_field_is_allowed("itemTemplates", "name") is True, "allowed scalar field should stay allowed")
    assert_true(service._master_edit_field_is_readonly("itemTemplates", "code") is True, "code should remain read-only")
    assert_true(service._master_relation_edit_field_is_open("itemTemplates", "enhance_group_code") is True, "relation edit field should stay open")

    print("backend admin edit draft service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
