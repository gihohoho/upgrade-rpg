"""Static smoke test for the backend admin master catalog/detail service split.

Run from the project root:

    python tools/smoke_backend_admin_master_catalog_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    split_file = ROOT / "backend/app/services/admin/admin_master_catalog_service.py"
    package_file = ROOT / "backend/app/services/admin/__init__.py"

    assert_true(split_file.exists(), "missing admin_master_catalog_service.py")
    assert_true(package_file.exists(), "missing backend/app/services/admin/__init__.py")
    assert_true(issubclass(AdminService, AdminMasterCatalogService), "AdminService must keep the master catalog split service mixin in its MRO")

    split_methods = {
        "list_master_catalog_domains",
        "list_master_catalog_rows",
        "get_master_catalog_detail",
        "get_master_catalog_relations",
        "_empty_relation_response",
        "_build_master_relation_groups",
        "_fetch_master_relation_group",
        "_serialize_master_relation_row",
        "_build_master_catalog_where_clauses",
        "_master_catalog_order_by",
        "_count_master_catalog_rows",
        "_master_catalog_columns",
        "_serialize_master_catalog_row",
        "_serialize_master_detail_scalar_fields",
        "_serialize_master_detail_json_fields",
        "_build_master_detail_relation_hints",
        "_build_master_relation_edit_options",
    }
    shared_methods = {
        "_clean_filter_text",
        "_is_safe_slot_key",
        "_join_json_keys",
        "_fetch_relation_code_options",
        "_serialize_relation_option",
        "_count_where",
        "_is_asset_field",
        "_serialize_asset_field",
        "_safe_detail_scalar_value",
        "_sanitize_json_preview",
        "_sanitize_json_value",
        "_humanize_field_name",
    }
    for name in split_methods:
        assert_true(hasattr(AdminMasterCatalogService, name), f"split service missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited {name}")
    for name in shared_methods:
        assert_true(hasattr(AdminSharedUtilsService, name), f"shared utils missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited shared helper {name}")

    admin_direct = set(AdminService.__dict__.keys())
    split_direct = set(AdminMasterCatalogService.__dict__.keys())
    shared_direct = set(AdminSharedUtilsService.__dict__.keys())
    for name in split_methods:
        assert_true(name in split_direct, f"{name} should live directly on the split service")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")
    for name in shared_methods:
        assert_true(name in shared_direct, f"{name} should live directly on shared utils")
        assert_true(name not in split_direct, f"{name} should not be duplicated directly on master catalog service after v204")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    source = service_file.read_text(encoding="utf-8")
    split_source = split_file.read_text(encoding="utf-8")
    assert_true("from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService" in source, "AdminService must import the master catalog split service")
    assert_true("AdminMasterCatalogService" in source and "class AdminService(" in source, "AdminService must inherit the master catalog split service")
    assert_true("class AdminMasterCatalogService" in split_source, "split file must define AdminMasterCatalogService")

    assert_true(len(source.splitlines()) < 3200, "admin_service.py should be smaller after the master catalog split")
    assert_true(len(split_source.splitlines()) >= 700, "split service should contain the master catalog/detail implementation")
    assert_true(inspect.iscoroutinefunction(AdminService.list_master_catalog_rows), "list_master_catalog_rows should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.get_master_catalog_detail), "get_master_catalog_detail should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.get_master_catalog_relations), "get_master_catalog_relations should remain async")

    service = AdminService()
    assert_true(service._clean_filter_text("  abc  ") == "abc", "clean filter helper should still work through facade")
    assert_true(AdminService._join_json_keys({"baseStats": {"a": 1}, "options": {}}) == "baseStats:a", "json key helper should remain staticmethod-compatible")
    assert_true(AdminService._is_asset_field("icon_url"), "asset field helper should remain staticmethod-compatible")
    assert_true(AdminService._humanize_field_name("owner_code") == "owner code", "field humanize helper should remain available")

    row = SimpleNamespace(id=1, code="skill_smoke", name="Smoke Skill", slot_key="Q", proc_rate=0.25, cooldown_seconds=5, options_json={"a": 1}, updated_at=None)
    serialized = service._serialize_master_catalog_row("skills", row)
    assert_true(serialized["domain"] == "skills", "catalog row serializer should preserve domain")
    assert_true(serialized["cells"]["code"] == "skill_smoke", "catalog row serializer should preserve code")
    assert_true(serialized["rawJsonReturned"] is False, "catalog row serializer must stay read-only")
    assert_true(serialized["assetsReturned"] is False, "catalog row serializer must hide assets")

    print("backend admin master catalog/detail service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
