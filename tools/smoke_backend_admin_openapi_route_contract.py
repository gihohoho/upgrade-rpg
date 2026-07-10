"""OpenAPI smoke test for v229/v230 backend admin route metadata contract.

Run from the project root:

    python tools/smoke_backend_admin_openapi_route_contract.py
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

    The OpenAPI contract only inspects route metadata generated from the assembled
    FastAPI app. It never opens a database connection, so the same tiny SQLAlchemy
    async engine/session stub used by adjacent route-contract smokes is enough.
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

from app.api.routes.admin_openapi_route_contract import (  # noqa: E402
    ADMIN_OPENAPI_ROUTE_CONTRACT,
    get_admin_openapi_route_contract_readiness,
)
from app.api.routes.admin_route_operation_contract import get_admin_route_operation_contract_readiness  # noqa: E402
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


runtime = get_admin_runtime_route_contract_readiness(app)
operation = get_admin_route_operation_contract_readiness(root=ROOT, app=app)
openapi = get_admin_openapi_route_contract_readiness(app)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(ADMIN_OPENAPI_ROUTE_CONTRACT["version"] == "v229.backend-admin-openapi-route-contract", "OpenAPI route contract version mismatch")
assert_true(ADMIN_OPENAPI_ROUTE_CONTRACT["status"] == "openapi-route-metadata-v229", "OpenAPI route contract status mismatch")
assert_true(runtime["ok"], f"runtime route registration should pass before OpenAPI check: {runtime}")
assert_true(operation["ok"], f"route operation contract should pass before OpenAPI check: {operation}")
assert_true(openapi["ok"], f"OpenAPI route readiness failed: {openapi}")
assert_true(openapi["expectedOperationCount"] == 21, "OpenAPI contract should expect all 21 admin routes")
assert_true(openapi["actualOperationCount"] == 21, "OpenAPI schema should expose all 21 admin routes")
assert_true(openapi["countCheck"]["ok"], "OpenAPI admin route count should match the operation contract")
assert_true(not openapi["missingOperations"], "OpenAPI schema should not miss admin route operations")
assert_true(not openapi["unexpectedOperations"], "OpenAPI schema should not include unexpected admin route operations")
assert_true(not openapi["duplicateOperationKeys"], "OpenAPI admin method/path keys should be unique")
assert_true(not openapi["duplicateOperationIds"], "OpenAPI operationId values should be unique")
assert_true(not openapi["failedOperationChecks"], "OpenAPI operationId/tag/response checks should pass")
assert_true(all(item["operationIdOk"] for item in openapi["operationChecks"]), "OpenAPI operationIds should match FastAPI default names")
assert_true(all(item["operationIdEndpointPrefixOk"] for item in openapi["operationChecks"]), "OpenAPI operationIds should keep endpoint-name prefixes")
assert_true(all(item["tagOk"] for item in openapi["operationChecks"]), "OpenAPI admin routes should keep admin tag")
assert_true(all(item["responseShapeOk"] for item in openapi["operationChecks"]), "OpenAPI admin routes should expose 200 responses")

expected_operation_ids = {item["actualOperationId"] for item in openapi["operationChecks"]}
for operation_id in (
    "get_admin_readonly_overview_api_v1_admin_overview_get",
    "list_admin_master_catalog_rows_api_v1_admin_master_data_catalog_get",
    "apply_admin_master_data_edit_api_v1_admin_master_data_edit_apply_post",
    "list_admin_change_logs_api_v1_admin_change_logs_get",
    "apply_admin_change_log_rollback_api_v1_admin_change_logs__change_log_id__rollback_apply_post",
):
    assert_true(operation_id in expected_operation_ids, f"OpenAPI schema should include operationId {operation_id}")

assert_true('"backend/app/api/routes/admin_openapi_route_contract.py"' in contract, "backend split contract should list OpenAPI route contract")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "backend split contract should be v230")
assert_true('"FastAPI OpenAPI admin route metadata is checked against operation contract"' in contract, "backend route contract should mention OpenAPI metadata")
assert_true('"OpenAPI operationId metadata is checked against runtime endpoint names"' in contract, "backend route contract should mention OpenAPI operationId metadata")
assert_true('const VERSION = "v243.backend-admin-request-media-size-boundary-contract"' in entry, "frontend readiness version should be v230")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v230")
assert_true("backendOpenApiRouteContractReady" in entry, "frontend top-level OpenAPI route contract flag missing")
assert_true("backendOpenApiRouteMetadataReady" in entry, "frontend top-level OpenAPI route metadata flag missing")
assert_true("backendOpenApiOperationIdMetadataReady" in entry, "frontend top-level OpenAPI operationId flag missing")
assert_true("openApiRouteContractReady" in entry, "frontend split contract should expose OpenAPI route contract flag")
assert_true("openApiRouteMetadataReady" in entry, "frontend split contract should expose OpenAPI route metadata flag")
assert_true("openApiOperationIdMetadataReady" in entry, "frontend split contract should expose OpenAPI operationId metadata flag")
assert_true("smoke_backend_admin_openapi_route_contract.py" in run_smoke, "core smoke should include v229/v230 OpenAPI route smoke")

print("backend admin OpenAPI route contract smoke test passed")
