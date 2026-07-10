"""Static/runtime smoke test for v227 backend admin route operation metadata contract.

Run from the project root:

    python tools/smoke_backend_admin_route_operation_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def _install_db_import_stubs() -> None:
    """Let this smoke import the FastAPI app without DB drivers.

    The operation contract only inspects registered route metadata. It never opens
    a database connection, so a tiny SQLAlchemy async engine/session stub is enough
    for local tool containers that do not have asyncpg installed.
    """

    import sqlalchemy.ext.asyncio as sa_async

    def create_async_engine_stub(*args, **kwargs):  # type: ignore[no-untyped-def]
        class DummyEngine:
            pass

        return DummyEngine()

    class DummySessionMaker:
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

        def __call__(self):  # type: ignore[no-untyped-def]
            class DummySessionContext:
                async def __aenter__(self):  # type: ignore[no-untyped-def]
                    return None

                async def __aexit__(self, *args):  # type: ignore[no-untyped-def]
                    return None

            return DummySessionContext()

    sa_async.create_async_engine = create_async_engine_stub
    sa_async.async_sessionmaker = DummySessionMaker


_install_db_import_stubs()

from app.api.routes.admin_route_map_contract import get_admin_route_module_contract_readiness  # noqa: E402
from app.api.routes.admin_route_operation_contract import (  # noqa: E402
    ADMIN_ROUTE_OPERATION_CONTRACT,
    get_admin_route_operation_contract_readiness,
)
from app.api.routes.admin_runtime_route_contract import get_admin_runtime_route_contract_readiness  # noqa: E402
from app.main import app  # noqa: E402

CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


operation = get_admin_route_operation_contract_readiness(root=ROOT, app=app)
static = get_admin_route_module_contract_readiness(root=ROOT)
runtime = get_admin_runtime_route_contract_readiness(app)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(ADMIN_ROUTE_OPERATION_CONTRACT["version"] == "v227.backend-admin-route-operation-contract", "route operation contract version mismatch")
assert_true(ADMIN_ROUTE_OPERATION_CONTRACT["status"] == "route-operation-metadata-v227", "route operation contract status mismatch")
assert_true(static["ok"], f"strict route ownership should pass before operation check: {static}")
assert_true(runtime["ok"], f"runtime route registration should pass before operation check: {runtime}")
assert_true(operation["ok"], f"route operation readiness failed: {operation}")
assert_true(operation["operationCount"] == 21, "operation contract should list all 21 admin routes")
assert_true(operation["routeMapCount"] == 21, "operation contract should align with all static route-map routes")
assert_true(operation["runtimeRouteCount"] == 21, "operation contract should align with all runtime routes")
assert_true(not operation["duplicateOperationKeys"], "operation contract should not contain duplicate method/path operations")
assert_true(not operation["routeMapMissing"], "operation contract should not miss any static route-map operations")
assert_true(not operation["routeMapUnexpected"], "operation contract should not leave route-map operations without metadata")
assert_true(not operation["failedRouteMapAlignmentChecks"], "operation metadata should match static route ownership/type map")
assert_true(not operation["failedStaticOperationChecks"], "route source endpoint/type/admin_ok_response checks should pass")
assert_true(not operation["failedRuntimeOperationChecks"], "runtime endpoint/name checks should pass")
assert_true(all(item["endpointOk"] for item in operation["staticOperationChecks"]), "all static endpoint names should match contract")
assert_true(all(item["typeMarkerOk"] for item in operation["staticOperationChecks"]), "all static response type markers should match contract")
assert_true(all(item["responseWrapperOk"] for item in operation["staticOperationChecks"]), "all route handlers should use admin_ok_response")
assert_true(all(item["ok"] for item in operation["runtimeOperationChecks"]), "all runtime endpoints should match static operation metadata")

expected_endpoints = {item["endpoint"] for item in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]}
for endpoint in (
    "get_admin_readonly_overview",
    "list_admin_master_catalog_rows",
    "apply_admin_master_data_edit",
    "list_admin_change_logs",
    "apply_admin_change_log_rollback",
):
    assert_true(endpoint in expected_endpoints, f"operation contract should include {endpoint}")

assert_true('"backend/app/api/routes/admin_route_operation_contract.py"' in contract, "backend split contract should list route operation contract")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "backend split contract should be v228")
assert_true('"Admin route operation metadata lives in admin_route_operation_contract.py"' in contract, "backend route contract should mention operation metadata")
assert_true('"Runtime route endpoint metadata is checked against static response type markers"' in contract, "backend route contract should mention runtime endpoint metadata")
assert_true('const VERSION = "v246.backend-admin-write-replay-safety-contract"' in entry, "frontend readiness version should be v228")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v228")
assert_true("backendRouteOperationContractReady" in entry, "frontend top-level route operation readiness flag missing")
assert_true("backendRuntimeRouteEndpointMetadataReady" in entry, "frontend top-level runtime endpoint metadata flag missing")
assert_true("routeOperationContractReady" in entry, "frontend split contract should expose route operation contract flag")
assert_true("runtimeRouteEndpointMetadataReady" in entry, "frontend split contract should expose runtime endpoint metadata flag")
assert_true("smoke_backend_admin_route_operation_contract.py" in run_smoke, "core smoke should include v227/v228 route operation smoke")

print("backend admin route operation contract smoke test passed")
