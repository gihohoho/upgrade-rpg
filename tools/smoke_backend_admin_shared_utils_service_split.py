"""Static/runtime smoke test for the backend admin shared utils service split.

Run from the project root:

    python tools/smoke_backend_admin_shared_utils_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_change_log_service import AdminChangeLogService
from app.services.admin.admin_edit_draft_service import AdminEditDraftService
from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService
from app.services.admin.admin_overview_snapshots_service import AdminOverviewSnapshotsService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    shared_file = ROOT / "backend/app/services/admin/admin_shared_utils.py"
    master_file = ROOT / "backend/app/services/admin/admin_master_catalog_service.py"
    overview_file = ROOT / "backend/app/services/admin/admin_overview_snapshots_service.py"
    edit_file = ROOT / "backend/app/services/admin/admin_edit_draft_service.py"
    change_file = ROOT / "backend/app/services/admin/admin_change_log_service.py"

    assert_true(shared_file.exists(), "missing admin_shared_utils.py")
    assert_true(issubclass(AdminService, AdminSharedUtilsService), "AdminService must keep shared utils first-class in its MRO")
    assert_true(AdminSharedUtilsService in AdminService.__mro__, "AdminService MRO must include AdminSharedUtilsService")

    shared_methods = {
        "_get_master_row",
        "_count",
        "_count_where",
        "_exists_by_code",
        "_fetch_code_name",
        "_exists_duplicate_combo",
        "_fetch_relation_code_options",
        "_serialize_relation_option",
        "_clean_filter_text",
        "_is_safe_slot_key",
        "_is_safe_admin_change_key",
        "_is_asset_field",
        "_serialize_asset_field",
        "_safe_detail_scalar_value",
        "_sanitize_json_preview",
        "_sanitize_json_value",
        "_humanize_field_name",
        "_join_json_keys",
        "_count_filled_items",
    }
    for name in shared_methods:
        assert_true(hasattr(AdminSharedUtilsService, name), f"shared utils missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing shared helper {name}")

    admin_direct = set(AdminService.__dict__.keys())
    shared_direct = set(AdminSharedUtilsService.__dict__.keys())
    master_direct = set(AdminMasterCatalogService.__dict__.keys())
    overview_direct = set(AdminOverviewSnapshotsService.__dict__.keys())
    edit_direct = set(AdminEditDraftService.__dict__.keys())
    change_direct = set(AdminChangeLogService.__dict__.keys())

    moved_from_master = {
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
    moved_from_overview = {"_count_filled_items"}
    moved_from_edit = {"_exists_by_code", "_fetch_code_name", "_exists_duplicate_combo"}
    moved_from_change = {"_is_safe_admin_change_key"}
    moved_from_facade = {"_get_master_row", "_count"}

    for name in shared_methods:
        assert_true(name in shared_direct, f"{name} should live directly on shared utils")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")
    for name in moved_from_master:
        assert_true(name not in master_direct, f"{name} should not be duplicated directly on master catalog service")
    for name in moved_from_overview:
        assert_true(name not in overview_direct, f"{name} should not be duplicated directly on overview service")
    for name in moved_from_edit:
        assert_true(name not in edit_direct, f"{name} should not be duplicated directly on edit draft service")
    for name in moved_from_change:
        assert_true(name not in change_direct, f"{name} should not be duplicated directly on change log service")
    for name in moved_from_facade:
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService facade")

    service_source = service_file.read_text(encoding="utf-8")
    shared_source = shared_file.read_text(encoding="utf-8")
    master_source = master_file.read_text(encoding="utf-8")
    overview_source = overview_file.read_text(encoding="utf-8")
    edit_source = edit_file.read_text(encoding="utf-8")
    change_source = change_file.read_text(encoding="utf-8")

    assert_true("from app.services.admin.admin_shared_utils import AdminSharedUtilsService" in service_source, "AdminService must import shared utils")
    assert_true("class AdminService(AdminSharedUtilsService," in service_source, "AdminSharedUtilsService should be first in AdminService inheritance list")
    assert_true("class AdminSharedUtilsService" in shared_source, "shared file must define AdminSharedUtilsService")
    assert_true("select(func.count())" in shared_source, "shared utils must contain count helper implementation")
    assert_true("[asset hidden:data-url]" in shared_source, "shared utils must preserve asset hiding guard")
    assert_true("_sanitize_json_preview" in shared_source, "shared utils must preserve JSON preview sanitizer")
    assert_true("def _get_master_row" not in service_source and "def _count(" not in service_source, "AdminService facade should not keep moved shared helpers")
    assert_true("def _count_where" not in master_source, "master catalog should not keep moved count_where helper")
    assert_true("def _count_filled_items" not in overview_source, "overview should not keep moved count_filled_items helper")
    assert_true("def _exists_by_code" not in edit_source, "edit draft should not keep moved relation existence helper")
    assert_true("def _is_safe_admin_change_key" not in change_source, "change log should not keep moved safe-key helper")

    assert_true(len(service_source.splitlines()) < 540, "admin_service.py should remain thin after v204 shared utils split")
    assert_true(len(shared_source.splitlines()) >= 150, "shared utils service should contain moved helper implementations")

    service = AdminService()
    assert_true(service._clean_filter_text("  abc  ") == "abc", "shared clean filter helper should work through facade")
    assert_true(service._is_safe_slot_key("Q-1.ok") is True, "slot key safety helper should work through facade")
    assert_true(service._is_safe_admin_change_key("owner_code") is True, "change key safety helper should work through facade")
    assert_true(service._is_safe_admin_change_key("owner code!") is False, "unsafe change key should be blocked")
    assert_true(service._join_json_keys({"baseStats": {"a": 1}, "options": {}}) == "baseStats:a", "json key join helper should work through facade")
    assert_true(service._count_filled_items([{"id": 1}, None, {}]) == 1, "filled item counter should work through facade")
    assert_true(service._humanize_field_name("owner_code") == "owner code", "field humanizer should work through facade")

    option = service._serialize_relation_option(SimpleNamespace(code="skill_q", name="Q Skill"), "skill_q")
    assert_true(option["current"] is True and option["label"] == "skill_q · Q Skill", "relation option serializer should preserve current label")

    asset = service._safe_detail_scalar_value("data:image/png;base64,abc")
    assert_true(asset == "[asset hidden:data-url]", "asset-like scalar values must stay hidden")
    preview, stats = service._sanitize_json_preview({"img": "data:image/png;base64,abc", "long": "x" * 700})
    assert_true(preview["img"] == "[asset hidden:data-url]", "JSON asset values must stay hidden")
    assert_true(stats["hiddenAssetCount"] == 1 and stats["truncatedCount"] == 1, "JSON sanitizer stats should remain accurate")

    assert_true(inspect.iscoroutinefunction(AdminService._get_master_row), "_get_master_row should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService._count), "_count should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService._count_where), "_count_where should remain async")

    print("backend admin shared utils service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
