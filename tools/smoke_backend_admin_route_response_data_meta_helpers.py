"""Static smoke test for v211/v214 backend admin route response data/meta helpers.

Run from the project root:

    python tools/smoke_backend_admin_route_response_data_meta_helpers.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "backend/app/api/routes/admin.py"
OVERVIEW = ROOT / "backend/app/api/routes/admin_overview_snapshot_routes.py"
MASTER = ROOT / "backend/app/api/routes/admin_master_data_routes.py"
CHANGE = ROOT / "backend/app/api/routes/admin_change_log_routes.py"
DATA_HELPERS = ROOT / "backend/app/api/routes/admin_response_data_helpers.py"
META_HELPERS = ROOT / "backend/app/api/routes/admin_response_meta_helpers.py"
CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


route = read(ROUTE)
route_modules = route + read(OVERVIEW) + read(MASTER) + read(CHANGE)
data_helpers = read(DATA_HELPERS)
meta_helpers = read(META_HELPERS)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(DATA_HELPERS.exists(), "admin response data helper file missing")
assert_true(META_HELPERS.exists(), "admin response meta helper file missing")
assert_true("from app.api.routes import admin_response_data_helpers as admin_data" in route_modules, "route should import response data helper module")
assert_true("from app.api.routes.admin_response_meta_helpers import admin_route_meta" in route_modules, "route should import response meta helper")
assert_true("data={" not in route, "admin.py should not build large inline response data dicts")
assert_true("meta={" not in route, "admin.py should not build inline route metadata dicts")
assert_true("admin_data.build_master_catalog_data" in route_modules, "master catalog route should use response data helper")
assert_true("admin_data.build_change_logs_data" in route_modules, "change logs route should use response data helper")
assert_true("admin_data.build_save_snapshots_data" in route_modules, "save snapshots route should use response data helper")
assert_true("meta=admin_route_meta(\"master_catalog\")" in route_modules, "master catalog route should use meta helper")
assert_true("meta=admin_route_meta(\"change_logs\")" in route_modules, "change logs route should use meta helper")
assert_true("def build_admin_requirements_data" in data_helpers, "requirements data builder missing")
assert_true("def build_admin_overview_data" in data_helpers, "overview data builder missing")
assert_true("def build_master_create_apply_data" in data_helpers, "create apply data builder missing")
assert_true("def build_create_delete_restore_apply_data" in data_helpers, "restore apply data builder missing")
assert_true("def build_change_preview_data" in data_helpers, "change preview data builder missing")
assert_true("def admin_route_meta" in meta_helpers, "admin_route_meta missing")
assert_true("_ADMIN_ROUTE_META" in meta_helpers, "route meta mapping missing")
assert_true("관리자 마스터 데이터 카탈로그 조회 전용 목록" in meta_helpers, "master catalog meta note missing")
assert_true("관리자 변경 이력 읽기 전용 목록" in meta_helpers, "change logs meta note missing")
assert_true('"backend/app/api/routes/admin_response_data_helpers.py"' in contract, "data helper should be listed in backend contract")
assert_true('"backend/app/api/routes/admin_response_meta_helpers.py"' in contract, "meta helper should be listed in backend contract")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "contract splitStatus should be v216")
assert_true('"No route path changes through v234"' in contract, "route path contract should mention v214")
assert_true('const VERSION = "v244.backend-admin-request-header-encoding-compatibility-contract"' in entry, "frontend readiness version should be v216")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v216")
assert_true("backendRouteResponseDataHelperReady" in entry, "top-level response data readiness flag missing")
assert_true("backendRouteResponseMetaHelperReady" in entry, "top-level response meta readiness flag missing")
assert_true("routeResponseDataHelperReady" in entry, "contract response data readiness flag missing")
assert_true("routeResponseMetaHelperReady" in entry, "contract response meta readiness flag missing")
assert_true("smoke_backend_admin_route_response_data_meta_helpers.py" in run_smoke, "core smoke should include v214 smoke")
assert_true(len(route.splitlines()) <= 620, "admin.py should be slimmer after data/meta extraction")

# Route paths must remain visible in admin.py for existing static route/path tests.
for route_path in (
    '@router.get("/requirements")',
    '@router.get("/overview")',
    '@router.get("/master-data/catalog")',
    '@router.post("/master-data/edit-apply")',
    '@router.get("/change-logs")',
    '@router.post("/change-logs/{change_log_id}/rollback-apply")',
    '@router.get("/save-snapshots")',
):
    assert_true(route_path in route_modules, f"route path missing after helper extraction: {route_path}")

print("backend admin route response data/meta helpers smoke test passed")
