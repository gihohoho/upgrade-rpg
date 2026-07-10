from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
from app.api.routes.admin_preview_side_effect_contract import get_admin_preview_side_effect_contract_readiness
r=get_admin_preview_side_effect_contract_readiness(root=ROOT)
assert r["ok"], r["failedChecks"]
assert r["dbWriteAttemptCount"] == 0
print("[OK] backend admin preview side-effect static contract")
