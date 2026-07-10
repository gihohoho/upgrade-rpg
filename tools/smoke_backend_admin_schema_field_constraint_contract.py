"""Smoke test for Admin request field constraints and Pydantic behavior."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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

from app.api.routes.admin_schema_field_constraint_contract import (  # noqa: E402
    ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT,
    get_admin_schema_field_constraint_contract_readiness,
)
from app.main import app  # noqa: E402


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


readiness = get_admin_schema_field_constraint_contract_readiness(app)
contract_text = (ROOT / "backend/app/services/admin_service_split_contract.py").read_text(encoding="utf-8")
entry_text = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
run_smoke_text = (ROOT / "tools/run_smoke_core.sh").read_text(encoding="utf-8")

assert_true(ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT["version"] == "v237.backend-admin-schema-field-constraint-contract", "field constraint contract version mismatch")
assert_true(ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT["status"] == "admin-schema-field-constraints-v237", "field constraint contract status mismatch")
assert_true(readiness["ok"], f"schema field constraint readiness failed: {readiness}")
assert_true(readiness["requiredCheckCount"] == 11, "all 11 exposed request schemas should have required-field checks")
assert_true(readiness["fieldConstraintCheckCount"] == 31, "expected 31 field constraint/default checks")
assert_true(readiness["modelConfigCheckCount"] == 10, "10 normalized request models should keep model_config")
assert_true(readiness["runtimeBehaviorCheckCount"] == 10, "expected 10 runtime validation behavior checks")
assert_true(not readiness["failedRequiredChecks"], "required fields should not drift")
assert_true(not readiness["failedFieldConstraintChecks"], "OpenAPI field constraints/defaults should not drift")
assert_true(not readiness["failedModelConfigChecks"], "Pydantic model config should not drift")
assert_true(not readiness["failedRuntimeBehaviorChecks"], "runtime validation behavior should not drift")
assert_true("backend/app/api/routes/admin_schema_field_constraint_contract.py" in contract_text, "split contract should list field constraint contract")
assert_true("Admin request field constraints, defaults, required fields, and Pydantic normalization behavior are checked for drift" in contract_text, "split contract should mention field constraint drift guard")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry_text, "frontend splitStatus should be v238")
assert_true('const VERSION = "v239.backend-admin-shared-route-collector-hotfix"' in entry_text, "frontend readiness version should be v238.1")
assert_true('Admin request field constraints, defaults, required fields, and Pydantic normalization behavior are checked for drift' in entry_text, "frontend split contract should include the matching readiness marker")
assert_true("backendSchemaFieldConstraintContractReady" in entry_text, "frontend should expose field constraint readiness")
assert_true("smoke_backend_admin_schema_field_constraint_contract.py" in run_smoke_text, "core smoke should run field constraint smoke")

print("backend admin schema field constraint contract smoke test passed")
