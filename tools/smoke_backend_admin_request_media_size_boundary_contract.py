from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_request_media_size_boundary_contract import (
    get_admin_request_media_size_boundary_contract_readiness,
)

r = get_admin_request_media_size_boundary_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["version"] == "v243.backend-admin-request-media-size-boundary-contract"
assert r["caseCount"] == 6 and r["checkCount"] == 6
assert r["dbWriteAttemptCount"] == 0 and r["serviceCallCount"] == 0
assert r["sizePolicy"]["applicationLimitConfigured"] is False
assert r["sizePolicy"]["applicationLimitBytes"] is None
assert r["sizePolicy"]["enforcementOwner"] == "deployment-proxy-or-server-configuration"
checks = {item["key"]: item for item in r["checks"]}
for key in ("octet-stream-json-bytes", "octet-stream-binary", "urlencoded-form", "multipart-form"):
    assert checks[key]["actualError"]["type"] == "model_attributes_type"
assert checks["octet-stream-empty"]["actualError"] == {
    "type": "missing",
    "loc": ["body"],
    "msg": "Field required",
}
assert checks["moderate-json-body-no-app-limit"]["actualProbeLength"] == 65536
entry = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert "requestMediaSizeBoundaryContractReady" in entry
assert "backendRequestMediaSizeBoundaryContractReady" in entry
assert "backend/app/api/routes/admin_request_media_size_boundary_contract.py" in entry
print("[OK] backend admin request media/size boundary contract")
