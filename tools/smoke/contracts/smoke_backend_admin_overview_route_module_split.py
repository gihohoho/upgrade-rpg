"""Static smoke test for v215/v216 backend admin overview route module split.

Run from the project root:

    python tools/smoke/contracts/smoke_backend_admin_overview_route_module_split.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
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

assert_true(OVERVIEW.exists(), "overview/snapshot route module missing")
assert_true(MASTER.exists(), "master-data route module missing")
assert_true(CHANGE.exists(), "change-log route module missing")
assert_true("from app.api.routes.admin_overview_snapshot_routes import router as admin_overview_snapshot_router" in admin, "admin.py should import overview/snapshot router")
assert_true("router.include_router(admin_overview_snapshot_router)" in admin, "admin.py should include overview/snapshot router")
assert_true("router.include_router(admin_master_data_router)" in admin, "admin.py should still include master-data router")
assert_true("router.include_router(admin_change_log_router)" in admin, "admin.py should still include change-log router")
assert_true(len(admin.splitlines()) <= 90, "admin.py should be a very thin include-router facade after v216")

for forbidden in (
    "async def get_admin_requirements(",
    "async def get_admin_readonly_overview(",
    "async def list_admin_save_snapshots(",
    "async def preview_admin_change(",
):
    assert_true(forbidden not in admin, f"admin.py should not own route body after v216: {forbidden}")

for pattern in (
    '@router.get("/requirements")',
    '@router.get("/overview")',
    '@router.get("/save-snapshots")',
    '@router.post("/change-preview")',
    'type="admin.requirements"',
    'type="admin.overview"',
    'type="admin.save_snapshots"',
    'type="admin.change.preview"',
    "build_admin_requirements_data",
    "build_admin_overview_data",
    "build_save_snapshots_data",
    "build_change_preview_data",
    "SAVE_SNAPSHOT_LIMIT_QUERY",
    "AdminChangePreviewRequest",
):
    assert_true(pattern in overview, f"overview route module missing pattern: {pattern}")

assert_true("admin_ok_response(" in overview, "overview route module should use admin response helper")
assert_true("admin_route_meta(" in overview, "overview route module should use meta helper")
assert_true('"backend/app/api/routes/admin_overview_snapshot_routes.py"' in contract, "contract should list overview route module")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "contract splitStatus should be v216")
assert_true('"Overview/save-snapshot routes live in admin_overview_snapshot_routes.py"' in contract, "route contract should mention overview module")
assert_true('const VERSION = "v250.backend-admin-rollback-snapshot"' in entry, "frontend readiness version should be v216")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v216")
assert_true("backendRouteOverviewSnapshotModuleReady" in entry, "top-level overview route module readiness flag missing")
assert_true("backendRouteFacadeReady" in entry, "top-level route facade readiness flag missing")
assert_true("routeOverviewSnapshotModuleReady" in entry, "contract overview route module flag missing")
assert_true("routeFacadeReady" in entry, "contract route facade flag missing")
assert_true("smoke_backend_admin_overview_route_module_split.py" in run_smoke, "core smoke should include v216 smoke")

print("backend admin overview route module split smoke test passed")
