"""Static smoke test for the backend admin overview/snapshots service split.

Run from the project root:

    python tools/smoke/contracts/smoke_backend_admin_overview_snapshots_service_split.py
"""

from __future__ import annotations

import inspect
import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_overview_snapshots_service import AdminOverviewSnapshotsService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    split_file = ROOT / "backend/app/services/admin/admin_overview_snapshots_service.py"
    package_file = ROOT / "backend/app/services/admin/__init__.py"

    assert_true(split_file.exists(), "missing admin_overview_snapshots_service.py")
    assert_true(package_file.exists(), "missing backend/app/services/admin/__init__.py")
    assert_true(issubclass(AdminService, AdminOverviewSnapshotsService), "AdminService must keep the split service mixin in its MRO")

    split_methods = {
        "get_readonly_overview",
        "list_save_snapshot_summaries",
        "_get_master_data_counts",
        "_get_save_snapshot_summary",
        "_get_user_summary",
        "_build_snapshot_filters",
        "_build_snapshot_where_clauses",
        "_snapshot_order_by",
        "_count_save_snapshots",
        "_serialize_save_snapshot_summary",
    }
    shared_methods = {"_count_filled_items"}
    for name in split_methods:
        assert_true(hasattr(AdminOverviewSnapshotsService, name), f"split service missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited {name}")
    for name in shared_methods:
        assert_true(hasattr(AdminSharedUtilsService, name), f"shared utils missing {name}")
        assert_true(hasattr(AdminService, name), f"AdminService facade missing inherited shared helper {name}")

    admin_direct = set(AdminService.__dict__.keys())
    split_direct = set(AdminOverviewSnapshotsService.__dict__.keys())
    shared_direct = set(AdminSharedUtilsService.__dict__.keys())
    for name in split_methods:
        assert_true(name in split_direct, f"{name} should live directly on the split service")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")
    for name in shared_methods:
        assert_true(name in shared_direct, f"{name} should live directly on shared utils")
        assert_true(name not in split_direct, f"{name} should not be duplicated directly on overview service after v204")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    source = service_file.read_text(encoding="utf-8")
    split_source = split_file.read_text(encoding="utf-8")
    assert_true("from app.services.admin.admin_overview_snapshots_service import AdminOverviewSnapshotsService" in source, "AdminService must import the split service")
    assert_true("AdminOverviewSnapshotsService" in source and "class AdminService(" in source, "AdminService must inherit the split service")
    assert_true("class AdminOverviewSnapshotsService" in split_source, "split file must define AdminOverviewSnapshotsService")

    assert_true(len(source.splitlines()) < 3900, "admin_service.py should be smaller after the split")
    assert_true(len(split_source.splitlines()) >= 200, "split service should contain the overview/snapshot implementation")
    assert_true(inspect.iscoroutinefunction(AdminService.get_readonly_overview), "get_readonly_overview should remain async")
    assert_true(inspect.iscoroutinefunction(AdminService.list_save_snapshot_summaries), "list_save_snapshot_summaries should remain async")
    assert_true(
        isinstance(AdminSharedUtilsService.__dict__.get("_count_filled_items"), staticmethod),
        "_count_filled_items must remain staticmethod after the shared utils split",
    )

    fake_snapshot = SimpleNamespace(
        id=1,
        user_id=1,
        slot_key="default",
        client_save_key="rpg_save",
        save_version="smoke",
        summary_json={},
        snapshot_json={
            "player": {
                "inventory": [{"id": 1}, None, {}],
                "storage": [None, {"id": 2}],
                "trash": [],
                "mailbox": [{"id": 3}],
            }
        },
        source="smoke",
        note=None,
        created_at=None,
        updated_at=None,
    )
    serialized = AdminService()._serialize_save_snapshot_summary(fake_snapshot)
    assert_true(serialized["counts"]["inventoryItems"] == 1, "snapshot inventory count should be serialized without bound-method errors")
    assert_true(serialized["counts"]["storageItems"] == 1, "snapshot storage count should be serialized without bound-method errors")
    assert_true(serialized["rawSnapshotReturned"] is False, "snapshot serialization must stay read-only")

    print("backend admin overview/snapshots service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
