"""Static smoke test for v210 backend admin route params/error helper cleanup.

Run from the project root:

    python tools/smoke_backend_admin_route_params_error_helpers.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "backend/app/api/routes/admin.py"
OVERVIEW = ROOT / "backend/app/api/routes/admin_overview_snapshot_routes.py"
MASTER = ROOT / "backend/app/api/routes/admin_master_data_routes.py"
CHANGE = ROOT / "backend/app/api/routes/admin_change_log_routes.py"
PARAMS = ROOT / "backend/app/api/routes/admin_route_params.py"
ERROR_HELPERS = ROOT / "backend/app/api/routes/admin_route_error_helpers.py"
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
params = read(PARAMS)
error_helpers = read(ERROR_HELPERS)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true("from app.api.routes.admin_route_params import" in route_modules, "admin route params import missing")
assert_true("from app.api.routes.admin_route_error_helpers import build_admin_change_logs_unavailable_payload" in route_modules, "admin route error helper import missing")
assert_true("Query(default=\"itemTemplates\", max_length=80)" in params, "master domain query default missing")
assert_true("Query(default=20, ge=1, le=200)" in params, "master catalog limit query missing")
assert_true("Query(default=None, alias=\"targetType\", max_length=120)" in params, "change-log targetType query missing")
assert_true("Query(default=None, alias=\"userId\", ge=1)" in params, "save snapshot userId query missing")
assert_true("ADMIN_CURRENT_USER_DEP = Depends(get_current_user_placeholder)" in params, "current user dependency helper missing")
assert_true("ADMIN_DB_SESSION_DEP = Depends(get_db_session)" in params, "DB session dependency helper missing")
assert_true("ADMIN_WRITE_GUARD_DEP = Depends(require_admin_write_dev_key)" in params, "write guard dependency helper missing")
assert_true("current_user: CurrentUser = ADMIN_CURRENT_USER_DEP" in route_modules, "routes should use current user helper")
assert_true("session: AsyncSession = ADMIN_DB_SESSION_DEP" in route_modules, "routes should use DB session helper")
assert_true("_write_guard: bool = ADMIN_WRITE_GUARD_DEP" in route_modules, "write routes should use write guard helper")
assert_true("build_admin_change_logs_unavailable_payload(" in error_helpers, "change-log unavailable builder missing")
assert_true("build_admin_change_logs_unavailable_payload(" in route_modules, "route should call change-log unavailable builder")
assert_true("admin_change_logs_route_exception_guarded" in error_helpers, "guard warning marker missing")
assert_true('"backend/app/api/routes/admin_route_params.py"' in contract, "params helper should be listed in contract")
assert_true('"backend/app/api/routes/admin_route_error_helpers.py"' in contract, "error helper should be listed in contract")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "contract splitStatus should be v216")
assert_true('const VERSION = "v241.backend-admin-validation-error-compatibility-contract"' in entry, "frontend readiness version should be v216")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v216")
assert_true("backendRouteParamsReady" in entry, "top-level route params readiness flag missing")
assert_true("backendRouteErrorHelperReady" in entry, "top-level route error helper readiness flag missing")
assert_true("smoke_backend_admin_route_params_error_helpers.py" in run_smoke, "core smoke should include v210 smoke")

print("backend admin route params/error helpers smoke test passed")
