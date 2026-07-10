"""Static smoke for v221/v222 backend AdminService facade MRO contract.

Run from the project root:

    python tools/smoke_backend_admin_service_facade_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin_service import AdminService  # noqa: E402
from app.services.admin_service_facade_contract import (  # noqa: E402
    ADMIN_SERVICE_FACADE_CONTRACT,
    get_admin_service_facade_contract_readiness,
)
from app.services.admin_service_split_contract import get_admin_service_split_contract_readiness  # noqa: E402

ADMIN_SERVICE_FILE = ROOT / "backend/app/services/admin_service.py"
SPLIT_CONTRACT_FILE = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


admin_service_source = read(ADMIN_SERVICE_FILE)
split_contract_source = read(SPLIT_CONTRACT_FILE)
entry_source = read(ENTRY)
run_smoke_source = read(RUN_SMOKE)
facade_readiness = get_admin_service_facade_contract_readiness(AdminService, root=ROOT)
split_readiness = get_admin_service_split_contract_readiness(AdminService, root=ROOT)

assert_true(ADMIN_SERVICE_FACADE_CONTRACT["version"] == "v222.backend-admin-service-facade-contract", "facade contract version mismatch")
assert_true(facade_readiness["ok"], f"AdminService facade readiness failed: {facade_readiness}")
assert_true(facade_readiness["mixinOrderOk"], "AdminService mixin order should match the contract")
assert_true(facade_readiness["actualMixinOrder"] == ADMIN_SERVICE_FACADE_CONTRACT["expectedMixinOrder"], "actual MRO order mismatch")
assert_true(facade_readiness["lineLimitOk"], "admin_service.py should stay tiny")
assert_true(facade_readiness["legacyMarkerFree"], "admin_service.py should not keep legacy marker constants")
assert_true(facade_readiness["oneLineMroRemoved"], "AdminService MRO should be multi-line for readability")
assert_true('__all__ = ["AdminService"]' in admin_service_source, "admin_service.py should explicitly export AdminService")
assert_true("class AdminService(\n" in admin_service_source, "AdminService class should use multi-line base declaration")
assert_true("backend/app/services/admin_service_facade_contract.py" in split_readiness["extractedFiles"], "split contract should include facade contract file")
assert_true(split_readiness["splitStatus"] == "admin-schema-field-constraint-contract-v238", "splitStatus should be v222")
assert_true('"key": "service-facade-contract"' in split_contract_source, "split contract should include service-facade-contract group")
assert_true('const VERSION = "v239.backend-admin-shared-route-collector-hotfix"' in entry_source, "frontend readiness version should be v222")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry_source, "frontend splitStatus should be v222")
assert_true("backendServiceFacadeContractReady" in entry_source, "frontend should expose service facade contract readiness")
assert_true("smoke_backend_admin_service_facade_contract.py" in run_smoke_source, "core smoke should include v222 smoke")

print("backend admin service facade MRO contract smoke test passed")
