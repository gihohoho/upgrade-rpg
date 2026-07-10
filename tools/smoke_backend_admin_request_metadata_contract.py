"""Smoke test for v233/v234 backend admin request metadata contract.

Run from the project root:

    python tools/smoke_backend_admin_request_metadata_contract.py
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

from app.api.routes.admin_request_metadata_contract import (  # noqa: E402
    ADMIN_REQUEST_METADATA_CONTRACT,
    _body_metadata,
    _param_metadata,
    get_admin_request_metadata_contract_readiness,
)
from app.api.routes.admin_response_metadata_contract import get_admin_response_metadata_contract_readiness  # noqa: E402
from app.main import app  # noqa: E402

CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


response_metadata = get_admin_response_metadata_contract_readiness(app)
request_metadata = get_admin_request_metadata_contract_readiness(app, root=ROOT)


class _CompatFieldInfo:
    alias = "compatAlias"
    default = None
    metadata = []
    annotation = "AdminMasterDataCreateApplyRequest"


class _CompatModelFieldWithoutRequired:
    name = "compat_param"
    default = None
    field_info = _CompatFieldInfo()

    def is_required(self) -> bool:
        return True


compat_param = _CompatModelFieldWithoutRequired()
compat_param_metadata = _param_metadata(compat_param)
compat_body_metadata = _body_metadata(compat_param)
contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(ADMIN_REQUEST_METADATA_CONTRACT["version"] == "v233.backend-admin-route-request-metadata-contract", "request metadata contract version mismatch")
assert_true(ADMIN_REQUEST_METADATA_CONTRACT["status"] == "route-request-dependency-metadata-v233", "request metadata contract status mismatch")
assert_true(response_metadata["ok"], f"response metadata contract should pass before request metadata check: {response_metadata}")
assert_true(request_metadata["ok"], f"request metadata readiness failed: {request_metadata}")
assert_true(compat_param_metadata["required"] is True, "request metadata should support ModelField.is_required() without .required")
assert_true(compat_param_metadata["alias"] == "compatAlias", "request metadata should read aliases from compatibility field_info")
assert_true(compat_body_metadata["model"] == "AdminMasterDataCreateApplyRequest", "request body metadata should read compatibility annotations")
assert_true(request_metadata["expectedRouteCount"] == 21, "request metadata contract should cover all 21 admin routes")
assert_true(request_metadata["runtimeRouteCount"] == 21, "runtime request metadata should expose all 21 admin routes")
assert_true(request_metadata["openApiRouteCount"] == 21, "OpenAPI request metadata should expose all 21 admin routes")
assert_true(request_metadata["writeGuardRouteCount"] == 5, "exactly five admin apply routes should require the write guard")
assert_true(request_metadata["requestBodyRouteCount"] == 11, "exactly eleven admin routes should expose a JSON request body")
assert_true(request_metadata["countCheck"]["ok"], "runtime/OpenAPI/admin request metadata counts should match")
assert_true(not request_metadata["missingRuntimeRoutes"], "request metadata runtime check should not miss routes")
assert_true(not request_metadata["unexpectedRuntimeRoutes"], "request metadata runtime check should not include unexpected routes")
assert_true(not request_metadata["missingOpenApiRoutes"], "request metadata OpenAPI check should not miss routes")
assert_true(not request_metadata["unexpectedOpenApiRoutes"], "request metadata OpenAPI check should not include unexpected routes")
assert_true(not request_metadata["failedOperationChecks"], "request metadata operations should align with operation contract")
assert_true(not request_metadata["failedRuntimeChecks"], "runtime query/path/body/dependency checks should pass")
assert_true(not request_metadata["failedOpenApiChecks"], "OpenAPI query/path/header/body checks should pass")
assert_true(not request_metadata["failedSourceWriteGuardChecks"], "source write guard checks should pass")
assert_true(all(item["dependenciesOk"] for item in request_metadata["runtimeChecks"]), "runtime dependency call order should remain stable")
assert_true(all(item["queryParamsOk"] for item in request_metadata["runtimeChecks"]), "runtime query params should remain stable")
assert_true(all(item["pathParamsOk"] for item in request_metadata["runtimeChecks"]), "runtime path params should remain stable")
assert_true(all(item["bodyOk"] for item in request_metadata["runtimeChecks"]), "runtime request bodies should remain stable")
assert_true(all(item["headerParameterNamesOk"] for item in request_metadata["openApiChecks"]), "OpenAPI write guard header exposure should remain stable")

for key in (
    "backend/app/api/routes/admin_request_metadata_contract.py",
    "route-request-metadata",
    "Admin route request metadata contract lives in admin_request_metadata_contract.py",
    "Runtime query/path/body params are checked against request metadata contract",
    "OpenAPI query/path/header/body request metadata is checked against runtime routes",
    "Write apply routes keep require_admin_write_dev_key through ADMIN_WRITE_GUARD_DEP",
):
    assert_true(key in contract, f"split contract should mention {key}")

assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "admin page splitStatus should be v234")
assert_true('const VERSION = "v244.backend-admin-request-header-encoding-compatibility-contract"' in entry, "admin page version should be v234")
assert_true('backendRequestMetadataContractReady' in entry, "admin page should expose request metadata contract readiness flag")
assert_true('backendRuntimeRequestMetadataReady' in entry, "admin page should expose runtime request metadata readiness flag")
assert_true('backendOpenApiRequestMetadataReady' in entry, "admin page should expose OpenAPI request metadata readiness flag")
assert_true('backendWriteGuardDependencyMetadataReady' in entry, "admin page should expose write guard dependency metadata readiness flag")
assert_true("tools/smoke_backend_admin_request_metadata_contract.py" in run_smoke, "core smoke should run request metadata contract smoke")

print("backend admin request metadata contract smoke test passed")
