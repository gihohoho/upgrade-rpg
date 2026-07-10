from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_validation_error_compatibility_contract import get_admin_validation_error_compatibility_contract_readiness

r = get_admin_validation_error_compatibility_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["version"] == "v241.backend-admin-validation-error-compatibility-contract"
assert r["caseCount"] == 3 and r["checkCount"] == 3
assert r["ignoredErrorFields"] == ["input", "ctx"]
assert r["dbWriteAttemptCount"] == 0 and r["serviceCallCount"] == 0
entry=(ROOT/"src/api/admin-page-readonly.js").read_text(encoding="utf-8")
assert "validationErrorCompatibilityContractReady" in entry
assert "backendValidationErrorCompatibilityContractReady" in entry
print("[OK] backend admin validation error compatibility contract")
