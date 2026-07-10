from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_request_transport_header_observation_contract import (
    get_admin_request_transport_header_observation_contract_readiness,
)

r = get_admin_request_transport_header_observation_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["version"] == "v245.backend-admin-transport-header-observation-contract"
assert r["caseCount"] == 4 and r["checkCount"] == 4
assert r["dbWriteAttemptCount"] == 0 and r["serviceCallCount"] == 0
checks = {item["key"]: item for item in r["checks"]}
assert checks["duplicate-content-type"]["actualRawValues"] == ["application/json", "text/plain"]
assert checks["duplicate-content-type"]["actualSelectedValue"] == "application/json"
assert checks["duplicate-accept"]["actualRawValues"] == ["application/json", "text/plain"]
assert checks["duplicate-accept"]["actualSelectedValue"] == "application/json"
assert checks["declared-content-length-mismatch"]["actualSelectedValue"] == "999"
assert checks["declared-content-length-mismatch"]["actualBodyLength"] == 2
assert checks["transfer-encoding-header-observation"]["actualSelectedValue"] == "chunked"
assert r["networkBoundary"]["testClientCanProveWireChunkFraming"] is False
assert r["networkBoundary"]["testClientCanProveServerContentLengthRejection"] is False
entry = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert "requestTransportHeaderObservationContractReady" in entry
assert "backendRequestTransportHeaderObservationContractReady" in entry
assert "backend/app/api/routes/admin_request_transport_header_observation_contract.py" in entry
print("[OK] backend admin transport header observation contract")
