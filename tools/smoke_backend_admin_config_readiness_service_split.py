"""Static/runtime smoke test for backend admin config/readiness service split.

Run from the project root:

    python tools/smoke_backend_admin_config_readiness_service_split.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin.admin_config import AdminConfigService
from app.services.admin.admin_readiness_service import AdminReadinessService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService
from app.services.admin_service import AdminService
from app.services.admin_service_split_contract import get_admin_service_split_contract_readiness


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    service_file = ROOT / "backend/app/services/admin_service.py"
    config_file = ROOT / "backend/app/services/admin/admin_config.py"
    readiness_file = ROOT / "backend/app/services/admin/admin_readiness_service.py"

    assert_true(config_file.exists(), "missing admin_config.py")
    assert_true(readiness_file.exists(), "missing admin_readiness_service.py")
    assert_true(issubclass(AdminService, AdminConfigService), "AdminService must inherit AdminConfigService")
    assert_true(issubclass(AdminService, AdminReadinessService), "AdminService must inherit AdminReadinessService")
    assert_true(AdminConfigService in AdminService.__mro__, "AdminConfigService must be in AdminService MRO")
    assert_true(AdminReadinessService in AdminService.__mro__, "AdminReadinessService must be in AdminService MRO")
    assert_true(AdminSharedUtilsService in AdminService.__mro__, "AdminSharedUtilsService must remain in AdminService MRO")

    config_constants = {
        "MASTER_DATA_MODELS",
        "MASTER_EDIT_APPLY_CONFIRM_TEXT",
        "MASTER_EDIT_ROLLBACK_CONFIRM_TEXT",
        "MASTER_CREATE_APPLY_CONFIRM_TEXT",
        "MASTER_CREATE_DELETE_CONFIRM_TEXT",
        "MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT",
        "MASTER_CREATE_APPLY_ALLOWED_DOMAINS",
        "MASTER_CREATE_DELETE_ALLOWED_DOMAINS",
        "ADMIN_CHANGE_LOG_ACTION_FILTERS",
        "MASTER_EDIT_ALLOWED_FIELDS",
        "MASTER_RELATION_EDIT_FIELDS",
        "MASTER_COMBO_GUARDED_FIELDS",
        "MASTER_CATALOG_DOMAINS",
        "MASTER_CREATE_BLUEPRINT_FIELDS",
    }
    admin_direct = set(AdminService.__dict__.keys())
    config_direct = set(AdminConfigService.__dict__.keys())
    for name in config_constants:
        assert_true(name in config_direct, f"{name} should live directly on AdminConfigService")
        assert_true(hasattr(AdminService, name), f"AdminService facade should expose inherited {name}")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    readiness_methods = {"preview_change", "_build_readiness"}
    readiness_direct = set(AdminReadinessService.__dict__.keys())
    for name in readiness_methods:
        assert_true(name in readiness_direct, f"{name} should live directly on AdminReadinessService")
        assert_true(hasattr(AdminService, name), f"AdminService facade should expose inherited {name}")
        assert_true(name not in admin_direct, f"{name} should not be duplicated directly on AdminService")

    service_source = service_file.read_text(encoding="utf-8")
    config_source = config_file.read_text(encoding="utf-8")
    readiness_source = readiness_file.read_text(encoding="utf-8")

    assert_true("from app.services.admin.admin_config import AdminConfigService" in service_source, "facade must import AdminConfigService")
    assert_true("from app.services.admin.admin_readiness_service import AdminReadinessService" in service_source, "facade must import AdminReadinessService")
    assert_true("class AdminService(AdminConfigService, AdminSharedUtilsService, AdminReadinessService," in service_source, "facade MRO should keep config/shared/readiness order")
    assert_true("class AdminConfigService" in config_source, "config file must define AdminConfigService")
    assert_true("class AdminReadinessService" in readiness_source, "readiness file must define AdminReadinessService")
    assert_true("Boss," in config_source and "ItemTemplate," in config_source and "SkillLevel," in config_source, "config file must own model imports")
    assert_true("MASTER_CREATE_BLUEPRINT_FIELDS" in config_source, "config file must own create blueprint fields")
    assert_true("safeForAdminReadOnlyUi" in readiness_source, "readiness file must preserve read-only readiness flags")
    assert_true("guardedMasterEditApplyReady" in readiness_source, "readiness file must preserve guarded edit readiness")
    assert_true("async def preview_change" not in service_source, "facade should not keep preview_change implementation")
    assert_true("def _build_readiness" not in service_source, "facade should not keep readiness implementation")
    assert_true("from app.models import" not in service_source, "facade should not import DB models after config split")
    assert_true(len(service_source.splitlines()) < 340, "admin_service.py should be thin after config/readiness split")

    service = AdminService()
    assert_true(service.MASTER_EDIT_APPLY_CONFIRM_TEXT == "APPLY MASTER DATA EDIT", "confirm text must remain exposed through facade")
    assert_true("itemTemplates" in service.MASTER_CATALOG_DOMAINS, "catalog domains must remain exposed through facade")
    assert_true("skills" in dict(service.MASTER_DATA_MODELS), "master data models must remain exposed through facade")
    assert_true("update" in service.ADMIN_CHANGE_LOG_ACTION_FILTERS, "change log action filters must remain exposed through facade")
    assert_true("name" in service.MASTER_EDIT_ALLOWED_FIELDS["itemTemplates"], "edit allow-list must remain exposed through facade")
    assert_true(service._build_readiness({"itemTemplates": {"total": 1}, "skills": {"total": 1}}, {"totalSlots": 1})["ok"] is True, "readiness helper should work through facade")

    preview = asyncio.run(service.preview_change("test", {"a": 1}, {"a": 2}))
    assert_true(preview["allowed"] is True and preview["readOnly"] is True, "preview_change should remain route-safe")

    contract = get_admin_service_split_contract_readiness(AdminService, root=ROOT)
    assert_true(contract["ok"], f"split contract readiness failed: {contract}")
    assert_true(contract["splitStatus"] == "admin-route-map-contract-v218", "split status should be v216 route module split")
    assert_true("backend/app/services/admin/admin_config.py" in contract["extractedFiles"], "contract must include config file")
    assert_true("backend/app/services/admin/admin_readiness_service.py" in contract["extractedFiles"], "contract must include readiness file")

    print("backend admin config/readiness service split smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
