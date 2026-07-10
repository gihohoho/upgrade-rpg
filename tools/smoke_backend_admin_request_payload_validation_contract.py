from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_request_payload_validation_contract import (  # noqa: E402
    ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT,
    get_admin_request_payload_validation_contract_readiness,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


readiness = get_admin_request_payload_validation_contract_readiness()
assert_true(readiness["ok"], f"payload/422 contract failed: {readiness['failedChecks']}")
assert_true(readiness["version"] == "v240.backend-admin-request-payload-validation-contract", "unexpected v240 contract version")
assert_true(readiness["caseCount"] == 10, "all ten admin request body schemas must be covered")
assert_true(readiness["checkCount"] == 20, "each request must have alias serialization and 422 checks")
assert_true(readiness["dbWriteAttemptCount"] == 0, "contract must not write DB")
assert_true(readiness["serviceCallCount"] == 0, "contract must stop at request parsing boundary")

cases = ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT["cases"]
assert_true(any("confirmText" in case["expectedAliasDump"] for case in cases), "confirmText alias must be frozen")
assert_true(any("baseValues" in case["expectedAliasDump"] for case in cases), "baseValues alias must be frozen")
assert_true(all("dryRun" in case["expectedAliasDump"] for case in cases), "dryRun alias must be frozen for every request")

split_text = (ROOT / "backend/app/services/admin_service_split_contract.py").read_text(encoding="utf-8")
assert_true("backend/app/api/routes/admin_request_payload_validation_contract.py" in split_text, "split contract must track v240 payload contract")
assert_true("FastAPI 422 validation detail" in split_text, "route contract must describe v240 422 boundary")

entry_text = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert_true('const VERSION = "v240.backend-admin-request-payload-validation-contract"' in entry_text, "frontend readiness version must be v240")
assert_true("requestPayloadValidationContractReady" in entry_text, "frontend readiness must expose payload validation contract")

run_smoke_text = (ROOT / "tools/run_smoke_core.sh").read_text(encoding="utf-8")
assert_true("smoke_backend_admin_request_payload_validation_contract.py" in run_smoke_text, "core smoke must run v240 contract")

print("[OK] backend admin request payload / FastAPI 422 validation contract")
