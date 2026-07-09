"""Static/runtime smoke test for v217/v218 backend admin route facade cleanup.

Run from the project root:

    python tools/smoke_backend_admin_route_map_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_route_map_contract import (  # noqa: E402
    ADMIN_ROUTE_MODULE_CONTRACT,
    get_admin_route_module_contract_readiness,
)

ADMIN = ROOT / "backend/app/api/routes/admin.py"
OVERVIEW = ROOT / "backend/app/api/routes/admin_overview_snapshot_routes.py"
MASTER = ROOT / "backend/app/api/routes/admin_master_data_routes.py"
CHANGE = ROOT / "backend/app/api/routes/admin_change_log_routes.py"
CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


admin = read(ADMIN)
overview = read(OVERVIEW)
master = read(MASTER)
change = read(CHANGE)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)
readiness = get_admin_route_module_contract_readiness(root=ROOT)

assert_true(ADMIN_ROUTE_MODULE_CONTRACT["version"] == "v218.backend-admin-route-map-contract", "route map contract version mismatch")
assert_true(readiness["ok"], f"route map readiness failed: {readiness}")
assert_true(readiness["moduleCount"] == 3, "route map should own three feature modules")
assert_true(readiness["routeCount"] == 21, "route map should list all admin routes")
assert_true(not readiness["duplicatePaths"], "route map should not contain duplicate paths")
assert_true(not readiness["missingRoutes"], "route map should not miss route decorators/types")
assert_true(not readiness["failedFacadeChecks"], "admin.py facade checks should pass")

assert_true(len(admin.splitlines()) <= 12, "admin.py should be a minimal include-router facade after v217 cleanup")
assert_true("Legacy static-smoke" not in admin, "admin.py should not keep legacy static-smoke marker comments")
assert_true("# @router." not in admin, "admin.py should not keep commented route decorators")
assert_true("@router.get(" not in admin and "@router.post(" not in admin, "admin.py should not own route bodies")
assert_true("router.include_router(admin_overview_snapshot_router)" in admin, "admin.py should include overview module")
assert_true("router.include_router(admin_master_data_router)" in admin, "admin.py should include master-data module")
assert_true("router.include_router(admin_change_log_router)" in admin, "admin.py should include change-log module")

for marker in (
    '@router.get("/requirements")',
    '@router.get("/overview")',
    '@router.get("/save-snapshots")',
    '@router.post("/change-preview")',
):
    assert_true(marker in overview, f"overview route module missing {marker}")
for marker in (
    '@router.get("/master-data/domains")',
    '@router.post("/master-data/create-apply")',
    '@router.post("/master-data/edit-apply")',
):
    assert_true(marker in master, f"master-data route module missing {marker}")
for marker in (
    '@router.get("/change-logs")',
    '@router.post("/change-logs/{change_log_id}/rollback-apply")',
    '@router.post("/change-logs/{change_log_id}/create-delete-restore-apply")',
):
    assert_true(marker in change, f"change-log route module missing {marker}")

# Legacy smoke checks should now point at real modules/helpers rather than admin.py comments.
legacy_smoke_files = {
    "tools/smoke_admin_master_data_catalog.js": "backend/app/api/routes/admin_master_data_routes.py",
    "tools/smoke_admin_master_data_detail.js": "backend/app/api/routes/admin_master_data_routes.py",
    "tools/smoke_admin_master_data_relations.js": "backend/app/api/routes/admin_master_data_routes.py",
    "tools/smoke_admin_edit_draft_validation.js": "backend/app/api/routes/admin_master_data_routes.py",
    "tools/smoke_admin_create_apply_limited.js": "backend/app/api/routes/admin_master_data_routes.py",
    "tools/smoke_admin_create_delete_rollback.js": "backend/app/api/routes/admin_change_log_routes.py",
    "tools/smoke_admin_create_delete_restore.js": "backend/app/api/routes/admin_change_log_routes.py",
    "tools/smoke_admin_change_log_rollback.js": "backend/app/api/routes/admin_change_log_routes.py",
    "tools/smoke_admin_save_snapshot_filters.js": "backend/app/api/routes/admin_response_data_helpers.py",
}
for smoke_path, target in legacy_smoke_files.items():
    source = read(ROOT / smoke_path)
    assert_true(target in source, f"{smoke_path} should read {target}")

assert_true('"backend/app/api/routes/admin_route_map_contract.py"' in contract, "backend split contract should list route map contract")
assert_true('"splitStatus": "admin-route-map-contract-v218"' in contract, "backend split contract should be v218")
assert_true('"Legacy static smoke checks read actual route modules instead of admin.py comments"' in contract, "backend route contract should mention legacy smoke cleanup")
assert_true('"Admin route ownership map lives in admin_route_map_contract.py"' in contract, "backend route contract should mention route map")
assert_true('const VERSION = "v218.backend-admin-route-map-contract"' in entry, "frontend readiness version should be v218")
assert_true('splitStatus: "admin-route-map-contract-v218"' in entry, "frontend splitStatus should be v218")
assert_true("backendRouteMapContractReady" in entry, "frontend top-level route map readiness flag missing")
assert_true("backendRouteLegacySmokeCleanupReady" in entry, "frontend top-level legacy cleanup readiness flag missing")
assert_true("routeMapContractReady" in entry, "contract route map readiness flag missing")
assert_true("routeLegacySmokeCleanupReady" in entry, "contract legacy cleanup readiness flag missing")
assert_true("smoke_backend_admin_route_map_contract.py" in run_smoke, "core smoke should include v218 smoke")

print("backend admin route map contract smoke test passed")
