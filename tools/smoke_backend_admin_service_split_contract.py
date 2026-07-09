"""Static smoke test for the backend AdminService split contract.

Run from the project root:

    python tools/smoke_backend_admin_service_split_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.admin_service import AdminService
from app.services.admin_service_split_contract import (
    ADMIN_SERVICE_SPLIT_CONTRACT,
    get_admin_service_split_contract_readiness,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    readiness = get_admin_service_split_contract_readiness(AdminService, root=ROOT)
    assert_true(readiness["ok"], f"backend admin service split readiness failed: {readiness}")
    assert_true(readiness["version"] == "v198.backend-admin-service-split-contract", "unexpected contract version")
    assert_true(readiness["status"] == "contract-frozen-v198", "unexpected contract status")
    assert_true(readiness["splitStatus"] == "admin-route-overview-facade-split-v216", "unexpected split status")
    assert_true("backend/app/services/admin/admin_master_catalog_service.py" in readiness["extractedFiles"], "missing extracted master catalog file")
    assert_true("backend/app/services/admin/admin_create_lifecycle_service.py" in readiness["extractedFiles"], "missing extracted create lifecycle file")
    assert_true("backend/app/services/admin/admin_change_log_service.py" in readiness["extractedFiles"], "missing extracted change log file")
    assert_true("backend/app/services/admin/admin_edit_draft_service.py" in readiness["extractedFiles"], "missing extracted edit draft file")
    assert_true("backend/app/services/admin/admin_shared_utils.py" in readiness["extractedFiles"], "missing extracted shared utils file")
    assert_true("backend/app/services/admin/admin_config.py" in readiness["extractedFiles"], "missing extracted config file")
    assert_true("backend/app/services/admin/admin_readiness_service.py" in readiness["extractedFiles"], "missing extracted readiness file")
    assert_true(readiness["groupCount"] >= 8, "expected at least six split groups")
    assert_true(readiness["publicMethodCount"] >= 19, "public method contract is too small")
    assert_true(readiness["helperMethodCount"] >= 60, "helper method contract is too small")
    assert_true(readiness["lineCount"] and readiness["lineCount"] < 800, "admin_service.py should be smaller after v206 config/readiness split")
    assert_true(not readiness["duplicateGroupKeys"], "duplicate split group keys found")
    assert_true(not readiness["duplicateCandidateFiles"], "duplicate candidate files found")
    assert_true("backend/app/services/admin/admin_create_lifecycle_service.py" in readiness["extractedFiles"], "create lifecycle service should be extracted")
    assert_true("backend/app/services/admin/admin_change_log_service.py" in [group["candidateFile"] for group in ADMIN_SERVICE_SPLIT_CONTRACT["splitGroups"]], "missing change log candidate")
    print("backend admin service split contract smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
