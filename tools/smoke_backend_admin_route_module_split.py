"""Static smoke test for v213/v214 backend admin route module split.

Run from the project root:

    python tools/smoke_backend_admin_route_module_split.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "backend/app/api/routes/admin.py"
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
master = read(MASTER)
change = read(CHANGE)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(MASTER.exists(), "master-data route module missing")
assert_true(CHANGE.exists(), "change-log route module missing")
assert_true("from app.api.routes.admin_master_data_routes import router as admin_master_data_router" in admin, "admin.py should import master-data router")
assert_true("from app.api.routes.admin_change_log_routes import router as admin_change_log_router" in admin, "admin.py should import change-log router")
assert_true("router.include_router(admin_master_data_router)" in admin, "admin.py should include master-data router")
assert_true("router.include_router(admin_change_log_router)" in admin, "admin.py should include change-log router")
assert_true(len(admin.splitlines()) <= 180, "admin.py should be thin after route module split")

for pattern in (
    '@router.get("/master-data/domains")',
    '@router.get("/master-data/catalog")',
    '@router.get("/master-data/create-blueprint")',
    '@router.post("/master-data/create-preview")',
    '@router.post("/master-data/create-apply")',
    '@router.get("/master-data/detail")',
    '@router.get("/master-data/relations")',
    '@router.post("/master-data/edit-preview")',
    '@router.post("/master-data/edit-apply")',
):
    assert_true(pattern in master, f"master route missing in module: {pattern}")

for pattern in (
    '@router.get("/change-logs")',
    '@router.get("/change-logs/{change_log_id}")',
    '@router.post("/change-logs/{change_log_id}/create-delete-preview")',
    '@router.post("/change-logs/{change_log_id}/create-delete-apply")',
    '@router.post("/change-logs/{change_log_id}/create-delete-restore-preview")',
    '@router.post("/change-logs/{change_log_id}/create-delete-restore-apply")',
    '@router.post("/change-logs/{change_log_id}/rollback-preview")',
    '@router.post("/change-logs/{change_log_id}/rollback-apply")',
):
    assert_true(pattern in change, f"change-log route missing in module: {pattern}")

assert_true("AdminMasterDataCreateApplyRequest" in master, "master route module should own master create/apply schemas")
assert_true("AdminMasterDataEditApplyRequest" in master, "master route module should own master edit/apply schemas")
assert_true("AdminChangeLogRollbackApplyRequest" in change, "change-log route module should own rollback schemas")
assert_true("AdminCreateDeleteRestoreApplyRequest" in change, "change-log route module should own restore schemas")
assert_true("build_admin_change_logs_unavailable_payload" in change, "change-log route module should keep local fallback guard")
assert_true("admin_ok_response(" in master and "admin_ok_response(" in change, "route modules should preserve admin response helper")
assert_true("admin_route_meta(" in master and "admin_route_meta(" in change, "route modules should preserve meta helper")
assert_true('"backend/app/api/routes/admin_master_data_routes.py"' in contract, "contract should list master route module")
assert_true('"backend/app/api/routes/admin_change_log_routes.py"' in contract, "contract should list change-log route module")
assert_true('"splitStatus": "admin-service-facade-contract-v222"' in contract, "contract splitStatus should be v216")
assert_true('const VERSION = "v222.backend-admin-service-facade-contract"' in entry, "frontend readiness version should be v216")
assert_true('splitStatus: "admin-service-facade-contract-v222"' in entry, "frontend splitStatus should be v216")
assert_true("backendRouteModuleSplitReady" in entry, "top-level route module readiness flag missing")
assert_true("routeMasterDataModuleReady" in entry, "contract master-data route module flag missing")
assert_true("routeChangeLogModuleReady" in entry, "contract change-log route module flag missing")
assert_true("smoke_backend_admin_route_module_split.py" in run_smoke, "core smoke should include v214 smoke")

print("backend admin route module split smoke test passed")
