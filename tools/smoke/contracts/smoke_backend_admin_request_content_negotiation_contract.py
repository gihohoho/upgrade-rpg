from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_request_content_negotiation_contract import (
    get_admin_request_content_negotiation_contract_readiness,
)

r = get_admin_request_content_negotiation_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["version"] == "v242.backend-admin-request-content-negotiation-contract"
assert r["caseCount"] == 8 and r["checkCount"] == 8
assert r["ignoredErrorFields"] == ["input", "ctx"]
assert r["dbWriteAttemptCount"] == 0 and r["serviceCallCount"] == 0
checks = {item["key"]: item for item in r["checks"]}
assert checks["json-without-content-type"]["actualStatus"] in (200, 422)
assert len(checks["json-without-content-type"]["allowedOutcomes"]) == 2
assert checks["empty-json-object"]["actualError"]["loc"] == ["body", "domain"]
assert checks["empty-body"]["actualError"]["loc"] == ["body"]
assert checks["accept-text-plain-keeps-json-response"]["actualContentType"].startswith("application/json")
entry = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert "requestContentNegotiationContractReady" in entry
assert "backendRequestContentNegotiationContractReady" in entry
assert "backend/app/api/routes/admin_request_content_negotiation_contract.py" in entry
print("[OK] backend admin request content negotiation contract")
