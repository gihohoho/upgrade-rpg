"""Static smoke for v219/v220 backend admin route service dependency and legacy marker cleanup.

Run from the project root:

    python tools/smoke_backend_admin_route_service_legacy_cleanup.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_route_services import (  # noqa: E402
    ADMIN_ROUTE_SERVICE_DEPENDENCY_CONTRACT,
    create_admin_service,
    get_admin_route_service_dependency_readiness,
)
from app.services.admin_service import AdminService  # noqa: E402
from app.services.admin_service_split_contract import get_admin_service_split_contract_readiness  # noqa: E402

ADMIN_SERVICE = ROOT / "backend/app/services/admin_service.py"
LEGACY_MARKERS = ROOT / "backend/app/services/admin_service_legacy_markers.py"
OVERVIEW = ROOT / "backend/app/api/routes/admin_overview_snapshot_routes.py"
MASTER = ROOT / "backend/app/api/routes/admin_master_data_routes.py"
CHANGE = ROOT / "backend/app/api/routes/admin_change_log_routes.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


admin_service_source = read(ADMIN_SERVICE)
legacy_source = read(LEGACY_MARKERS)
entry_source = read(ENTRY)
run_smoke_source = read(RUN_SMOKE)
readiness = get_admin_route_service_dependency_readiness(root=ROOT)
split_readiness = get_admin_service_split_contract_readiness(AdminService, root=ROOT)

assert_true(ADMIN_ROUTE_SERVICE_DEPENDENCY_CONTRACT["version"] == "v219.backend-admin-route-service-dependency", "route service contract version mismatch")
assert_true(readiness["ok"], f"route service dependency readiness failed: {readiness}")
assert_true(isinstance(create_admin_service(), AdminService), "create_admin_service should return AdminService facade")
assert_true(readiness["routeModuleCount"] == 3, "three admin route modules should use the service factory")
assert_true(readiness["factoryOk"], "service factory readiness should pass")
assert_true(not readiness["failedModules"], "all admin route modules should use create_admin_service")

for route_file in [OVERVIEW, MASTER, CHANGE]:
    source = read(route_file)
    assert_true("from app.api.routes.admin_route_services import create_admin_service" in source, f"{route_file} should import create_admin_service")
    assert_true("service = create_admin_service()" in source, f"{route_file} should create service through helper")
    assert_true("from app.services.admin_service import AdminService" not in source, f"{route_file} should not directly import AdminService")
    assert_true("service = AdminService()" not in source, f"{route_file} should not instantiate AdminService directly")

assert_true(len(admin_service_source.splitlines()) <= 40, "admin_service.py should remain a tiny readable facade after MRO tidy")
assert_true("LEGACY_SMOKE_MARKERS" not in admin_service_source, "admin_service.py should not keep legacy marker constants")
assert_true("preview_master_data_create" not in admin_service_source, "admin_service.py should not keep create lifecycle markers")
assert_true("list_admin_change_logs" not in admin_service_source, "admin_service.py should not keep change-log markers")
assert_true("class AdminService(" in admin_service_source, "admin_service.py should still expose AdminService facade")
assert_true("AdminConfigService" in admin_service_source and "AdminSharedUtilsService" in admin_service_source, "AdminService MRO should stay intact")

assert_true(LEGACY_MARKERS.exists(), "legacy marker file should exist")
assert_true("ADMIN_SERVICE_FACADE_LEGACY_SMOKE_MARKERS" in legacy_source, "legacy marker file should include facade markers")
assert_true("BACKEND_ADMIN_CREATE_LIFECYCLE_SPLIT_LEGACY_SMOKE_MARKERS" in legacy_source, "legacy marker file should include create lifecycle markers")
assert_true("BACKEND_ADMIN_CHANGE_LOG_SERVICE_SPLIT_LEGACY_SMOKE_MARKERS" in legacy_source, "legacy marker file should include change-log markers")
assert_true("MASTER_CREATE_APPLY_ALLOWED_DOMAINS: set[str]" in legacy_source, "legacy marker file should preserve legacy set markers")

assert_true(split_readiness["ok"], f"backend service split contract readiness failed: {split_readiness}")
assert_true(split_readiness["splitStatus"] == "admin-schema-field-constraint-contract-v238", "splitStatus should be v222")
assert_true("backend/app/api/routes/admin_route_services.py" in split_readiness["extractedFiles"], "split contract should include route service helper")
assert_true("backend/app/services/admin_service_legacy_markers.py" in split_readiness["extractedFiles"], "split contract should include legacy marker file")
assert_true('const VERSION = "v245.backend-admin-transport-header-observation-contract"' in entry_source, "frontend readiness version should be v222")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry_source, "frontend splitStatus should be v222")
assert_true("backendRouteServiceDependencyReady" in entry_source, "frontend should expose route service dependency readiness")
assert_true("backendServiceLegacyMarkersReady" in entry_source, "frontend should expose service legacy marker readiness")
assert_true("smoke_backend_admin_route_service_legacy_cleanup.py" in run_smoke_source, "core smoke should include v220 smoke")

print("backend admin route service dependency and legacy cleanup smoke test passed")
