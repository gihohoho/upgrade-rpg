"""Runtime smoke test for v225 backend admin FastAPI route registration contract.

Run from the project root:

    python tools/smoke_backend_admin_runtime_route_contract.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = (ROOT / "backend").resolve()

# Always make this project's backend the first import location. Merely checking
# whether it exists somewhere in sys.path is not enough on Windows: another
# package/directory named ``app`` can be resolved first and produce a valid but
# unrelated FastAPI application.
backend_path = str(BACKEND)
sys.path[:] = [item for item in sys.path if str(Path(item or ".").resolve()) != backend_path]
sys.path.insert(0, backend_path)

# This smoke verifies the canonical /api/v1 admin route assembly.
# A developer machine may have API_PREFIX set in the shell or a root .env;
# force the contract value before app.core.config is imported so the result is
# deterministic on Windows, macOS, Linux, CI, and local Git Bash.
os.environ["API_PREFIX"] = "/api/v1"


def _install_db_import_stubs() -> None:
    """Let the route-registration smoke import the FastAPI app without DB drivers.

    This smoke does not open a DB connection. It only inspects registered route
    metadata. The local tool container may not have asyncpg installed, so we stub
    the engine/session factory before app.db.session is imported.
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

import app as app_package  # noqa: E402
from app.api import router as api_router_module  # noqa: E402
from app.api.routes.admin_runtime_route_contract import (  # noqa: E402
    ADMIN_RUNTIME_ROUTE_CONTRACT,
    get_admin_runtime_route_contract_readiness,
)
from app.api.routes.admin_route_map_contract import get_admin_route_module_contract_readiness  # noqa: E402
from app.core.config import settings  # noqa: E402
from app import main as app_main_module  # noqa: E402

app = app_main_module.app

CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


runtime = get_admin_runtime_route_contract_readiness(app)
static = get_admin_route_module_contract_readiness(root=ROOT)
runtime_contract_source = read(ROOT / "backend/app/api/routes/admin_runtime_route_contract.py")

expected_app_init = (BACKEND / "app" / "__init__.py").resolve()
expected_api_router = (BACKEND / "app" / "api" / "router.py").resolve()
expected_main = (BACKEND / "app" / "main.py").resolve()
actual_app_init = Path(app_package.__file__ or "").resolve()
actual_api_router = Path(api_router_module.__file__ or "").resolve()
actual_main = Path(app_main_module.__file__ or "").resolve()
assert_true(
    actual_app_init == expected_app_init,
    f"wrong app package imported: expected {expected_app_init}, got {actual_app_init}",
)
assert_true(
    actual_api_router == expected_api_router,
    f"wrong app.api.router imported: expected {expected_api_router}, got {actual_api_router}",
)
assert_true(
    actual_main == expected_main,
    f"wrong app.main imported: expected {expected_main}, got {actual_main}",
)
assert_true(
    "_iter_runtime_route_nodes" in runtime_contract_source,
    "runtime route contract must support nested FastAPI/APIRouter containers",
)
assert_true(
    'nested_app = getattr(node, "app", None)' in runtime_contract_source,
    "runtime route contract must inspect Starlette mounted app containers",
)

assert_true(
    settings.api_prefix == "/api/v1",
    f"runtime smoke must use canonical API_PREFIX=/api/v1, got {settings.api_prefix!r}",
)
# Do not inspect only ``app.routes`` here. Some FastAPI/Starlette versions
# preserve included routers as nodes whose direct path is an empty string.
# The canonical runtime contract below recursively flattens those containers,
# so a direct-path precheck would reject a valid nested registration before the
# real contract gets a chance to inspect it.

contract = read(CONTRACT)
entry = read(ENTRY)
run_smoke = read(RUN_SMOKE)

assert_true(ADMIN_RUNTIME_ROUTE_CONTRACT["version"] == "v225.backend-admin-runtime-route-contract", "runtime route contract version mismatch")
assert_true(ADMIN_RUNTIME_ROUTE_CONTRACT["status"] == "runtime-route-registration-v225", "runtime route contract status mismatch")
assert_true(static["ok"], f"static route ownership contract should pass before runtime check: {static}")
assert_true(runtime["ok"], f"runtime route registration readiness failed: {runtime}")
assert_true(runtime["expectedRouteCount"] == 21, "runtime contract should expect all 21 admin routes")
assert_true(runtime["actualRouteCount"] == 21, "FastAPI app/router assembly should expose all 21 admin routes")
assert_true(runtime["routeSource"] in {"fastapi-app", "canonical-api-router-fallback", "canonical-owner-routers-fallback"}, "runtime route source should be explicit")
assert_true(runtime["countCheck"]["ok"], "runtime route count should match static contract")
assert_true(not runtime["missingRoutes"], "FastAPI app should not miss admin routes")
assert_true(not runtime["unexpectedRoutes"], "FastAPI app should not register unexpected admin routes")
assert_true(not runtime["duplicateRouteKeys"], "FastAPI app should not register duplicate admin method/path routes")
assert_true(all(item["ok"] for item in runtime["prefixChecks"]), "runtime prefixes should stay /api/v1/admin")
assert_true(all(item["path"].startswith("/api/v1/admin/") or item["path"] == "/api/v1/admin/overview" for item in runtime["actualRoutes"]), "actual admin route paths should use /api/v1/admin prefix")
assert_true("GET /api/v1/admin/overview" in {item["key"] for item in runtime["actualRoutes"]}, "runtime route list should include overview")
assert_true("POST /api/v1/admin/master-data/edit-apply" in {item["key"] for item in runtime["actualRoutes"]}, "runtime route list should include edit apply")
assert_true("POST /api/v1/admin/change-logs/{change_log_id}/rollback-apply" in {item["key"] for item in runtime["actualRoutes"]}, "runtime route list should include rollback apply")

assert_true('"backend/app/api/routes/admin_runtime_route_contract.py"' in contract, "backend split contract should list runtime route contract")
assert_true('"splitStatus": "admin-schema-field-constraint-contract-v238"' in contract, "backend split contract should be v226")
assert_true('"FastAPI runtime route registration is checked against static ownership map"' in contract, "backend route contract should mention runtime registration")
assert_true('const VERSION = "v240.backend-admin-request-payload-validation-contract"' in entry, "frontend readiness version should be v226")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry, "frontend splitStatus should be v226")
assert_true("backendRuntimeRouteContractReady" in entry, "frontend top-level runtime route contract readiness flag missing")
assert_true("backendRuntimeRouteRegistrationReady" in entry, "frontend top-level runtime route registration readiness flag missing")
assert_true("runtimeRouteContractReady" in entry, "frontend split contract should expose runtime route contract flag")
assert_true("runtimeRouteRegistrationReady" in entry, "frontend split contract should expose runtime registration route flag")
assert_true("smoke_backend_admin_runtime_route_contract.py" in run_smoke, "core smoke should include v225 runtime route smoke")

print("backend admin runtime route contract smoke test passed")
