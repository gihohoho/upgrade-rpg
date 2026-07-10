"""Smoke test for v231/v232 backend admin response metadata contract.

Run from the project root:

    python tools/smoke_backend_admin_response_metadata_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def _install_db_import_stubs() -> None:
    """Let this smoke import the FastAPI app without DB drivers."""

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

from app.api.routes.admin_openapi_route_contract import get_admin_openapi_route_contract_readiness  # noqa: E402
from app.api.routes.admin_response_metadata_contract import (  # noqa: E402
    ADMIN_RESPONSE_METADATA_CONTRACT,
    get_admin_response_metadata_contract_readiness,
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
response_metadata = get_admin_response_metadata_contract_readiness(app)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(ADMIN_RESPONSE_METADATA_CONTRACT["version"] == "v231.backend-admin-route-response-metadata-contract", "response metadata contract version mismatch")
assert_true(ADMIN_RESPONSE_METADATA_CONTRACT["status"] == "route-response-metadata-v231", "response metadata contract status mismatch")
assert_true(runtime["ok"], f"runtime route contract should pass before response metadata check: {runtime}")
assert_true(operation["ok"], f"route operation contract should pass before response metadata check: {operation}")
assert_true(openapi["ok"], f"OpenAPI route contract should pass before response metadata check: {openapi}")
assert_true(response_metadata["ok"], f"response metadata readiness failed: {response_metadata}")
assert_true(response_metadata["expectedRouteCount"] == 21, "response metadata contract should cover all 21 admin routes")
assert_true(response_metadata["runtimeRouteCount"] == 21, "runtime response metadata should expose all 21 admin routes")
assert_true(response_metadata["openApiRouteCount"] == 21, "OpenAPI response metadata should expose all 21 admin routes")
assert_true(response_metadata["countCheck"]["ok"], "runtime/OpenAPI/admin response metadata counts should match")
assert_true(not response_metadata["missingRuntimeRoutes"], "response metadata runtime check should not miss routes")
assert_true(not response_metadata["unexpectedRuntimeRoutes"], "response metadata runtime check should not include unexpected routes")
assert_true(not response_metadata["missingOpenApiRoutes"], "response metadata OpenAPI check should not miss routes")
assert_true(not response_metadata["unexpectedOpenApiRoutes"], "response metadata OpenAPI check should not include unexpected routes")
assert_true(not response_metadata["failedRuntimeChecks"], "runtime status_code/response_model/include_in_schema checks should pass")
assert_true(not response_metadata["failedOpenApiChecks"], "OpenAPI summary/response-code checks should pass")
assert_true(all(item["statusCodeDefaultOk"] for item in response_metadata["runtimeChecks"]), "admin routes should keep default 200 status_code metadata")
assert_true(all(item["responseModelDefaultOk"] for item in response_metadata["runtimeChecks"]), "admin routes should not add route-level response_model metadata")
assert_true(all(item["includeInSchemaOk"] for item in response_metadata["runtimeChecks"]), "admin routes should remain included in OpenAPI schema")
assert_true(all(item["summaryOk"] for item in response_metadata["openApiChecks"]), "admin OpenAPI summaries should remain default endpoint summaries")
assert_true(all(item["responseCodesOk"] for item in response_metadata["openApiChecks"]), "admin OpenAPI response code sets should remain stable")
assert_true(all(item["successDescriptionOk"] for item in response_metadata["openApiChecks"]), "admin OpenAPI 200 response description should remain stable")
assert_true(all(item["validationDescriptionOk"] for item in response_metadata["openApiChecks"]), "admin OpenAPI 422 response description should remain stable where expected")

for key in (
    "backend/app/api/routes/admin_response_metadata_contract.py",
    "route-response-metadata",
    "Admin route response metadata contract lives in admin_response_metadata_contract.py",
    "OpenAPI response codes and summaries are checked against runtime route defaults",
):
    assert_true(key in contract, f"split contract should mention {key}")

assert_true('splitStatus: "admin-response-metadata-contract-v232"' in entry, "admin page splitStatus should be v232")
assert_true('backendResponseMetadataContractReady' in entry, "admin page should expose response metadata contract readiness flag")
assert_true('backendOpenApiResponseCodeMetadataReady' in entry, "admin page should expose OpenAPI response-code readiness flag")
assert_true('backendRuntimeResponseDefaultsReady' in entry, "admin page should expose runtime response defaults readiness flag")
assert_true("tools/smoke_backend_admin_response_metadata_contract.py" in run_smoke, "core smoke should run response metadata contract smoke")

print("backend admin response metadata contract smoke test passed")
