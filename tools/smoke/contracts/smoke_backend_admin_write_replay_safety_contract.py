from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_write_replay_safety_contract import get_admin_write_replay_safety_contract_readiness

r = get_admin_write_replay_safety_contract_readiness(root=ROOT)
assert r["ok"], r["failedChecks"]
assert r["version"] == "v246.backend-admin-write-replay-safety-contract"
assert r["dbWriteAttemptCount"] == 0
assert r["serviceCallCount"] == 0
assert r["idempotency"]["supported"] is False
print("[OK] backend admin write replay safety contract")
