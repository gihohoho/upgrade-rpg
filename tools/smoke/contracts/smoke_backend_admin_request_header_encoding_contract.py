from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_request_header_encoding_contract import (
    get_admin_request_header_encoding_contract_readiness,
)

r = get_admin_request_header_encoding_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["version"] == "v244.backend-admin-request-header-encoding-compatibility-contract"
assert r["caseCount"] == 6 and r["checkCount"] == 6
assert r["dbWriteAttemptCount"] == 0 and r["serviceCallCount"] == 0
checks = {item["key"]: item for item in r["checks"]}
assert checks["utf8-korean-and-symbols"]["actualPayload"]["domain"] == "아이템"
assert checks["utf8-korean-and-symbols"]["actualPayload"]["draft"]["이름"] == "검⚔"
assert checks["charset-name-and-value-case-insensitive"]["actualStatus"] == 200
assert checks["content-type-header-name-case-insensitive"]["actualStatus"] == 200
assert checks["extra-content-type-parameter"]["actualStatus"] == 200
assert checks["duplicate-charset-parameter"]["actualStatus"] in (200, 400)
assert checks["invalid-utf8-byte-sequence"]["actualStatus"] in (400, 422)
entry = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert "requestHeaderEncodingContractReady" in entry
assert "backendRequestHeaderEncodingContractReady" in entry
assert "backend/app/api/routes/admin_request_header_encoding_contract.py" in entry
print("[OK] backend admin request header/encoding compatibility contract")
