"""Smoke test for the backend admin schema/model metadata contract."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import sqlalchemy.ext.asyncio as sa_async


def _create_async_engine_stub(*args, **kwargs):  # type: ignore[no-untyped-def]
    return object()


class _DummySessionMaker:
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        pass

    def __call__(self):  # type: ignore[no-untyped-def]
        class _Context:
            async def __aenter__(self):
                return None

            async def __aexit__(self, *args):
                return None
        return _Context()


sa_async.create_async_engine = _create_async_engine_stub
sa_async.async_sessionmaker = _DummySessionMaker

from app.api.routes.admin_schema_model_contract import (  # noqa: E402
    ADMIN_SCHEMA_MODEL_CONTRACT,
    get_admin_schema_model_contract_readiness,
)
from app.main import app  # noqa: E402


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


readiness = get_admin_schema_model_contract_readiness(app)
contract_text = (ROOT / "backend/app/services/admin_service_split_contract.py").read_text(encoding="utf-8")
entry_text = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
schema_model_source = (ROOT / "backend/app/api/routes/admin_schema_model_contract.py").read_text(encoding="utf-8")
run_smoke_text = (ROOT / "tools/run_smoke_core.sh").read_text(encoding="utf-8")

assert_true(ADMIN_SCHEMA_MODEL_CONTRACT["version"] == "v235.backend-admin-schema-model-contract", "schema contract version mismatch")
assert_true(ADMIN_SCHEMA_MODEL_CONTRACT["status"] == "admin-schema-model-metadata-v235", "schema contract status mismatch")
assert_true("collect_admin_runtime_route_entries" in schema_model_source, "schema/model contract should use shared runtime route collector")
assert_true("for route in app.routes" not in schema_model_source, "schema/model contract should not scan app.routes directly")
assert_true(readiness["ok"], f"schema/model readiness failed: {readiness}")
assert_true(readiness["expectedSchemaCount"] == 11, "expected 11 Admin request schemas")
assert_true(readiness["classSchemaCount"] == 12, "admin.py should keep 11 exposed request schemas plus one legacy unexposed schema class")
assert_true(readiness["openApiSchemaCount"] == 11, "OpenAPI should expose exactly 11 Admin request schemas")
assert_true(readiness["routeBodyCount"] == 11, "11 admin routes should have request body models")
assert_true(readiness["guardedApplySchemaCount"] == 5, "five guarded apply schemas should be checked")
assert_true(not readiness["failedRouteBodyChecks"], "route body models should match schema class names")
assert_true(not readiness["failedSchemaChecks"], "OpenAPI schema fields/aliases should match Pydantic models")
assert_true(not readiness["failedGuardedFieldChecks"], "guarded apply schemas should retain confirmText and reason")
assert_true("backend/app/api/routes/admin_schema_model_contract.py" in contract_text, "split contract should list schema/model contract")
assert_true("Admin request schema classes and OpenAPI components.schemas are checked for drift" in contract_text, "split contract should mention schema drift guard")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry_text, "frontend splitStatus should be v236")
assert_true('const VERSION = "v250.backend-admin-rollback-snapshot"' in entry_text, "frontend readiness version should be v238.1.1")
assert_true('Admin request schema classes and OpenAPI components.schemas are checked for drift' in entry_text, "frontend split contract should include the matching readiness marker")
assert_true("backendSchemaModelContractReady" in entry_text, "frontend should expose schema/model contract readiness")
assert_true("smoke_backend_admin_schema_model_contract.py" in run_smoke_text, "core smoke should run schema/model contract smoke")

print("backend admin schema/model contract smoke test passed")
