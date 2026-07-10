from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"backend"))
from app.api.routes.admin_rollback_snapshot_contract import get_admin_rollback_snapshot_contract_readiness
r=get_admin_rollback_snapshot_contract_readiness()
assert r["ok"], r["failedChecks"]
assert r["dbWriteAttemptCount"] == 0
print("[OK] backend admin rollback snapshot contract")
