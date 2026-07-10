from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"backend"))
from app.api.routes.admin_service_mutation_boundary_contract import get_admin_service_mutation_boundary_contract_readiness
r=get_admin_service_mutation_boundary_contract_readiness(root=ROOT)
assert r["ok"], r["failedChecks"]
assert r["dbWriteAttemptCount"] == 0
print("[OK] backend admin service mutation boundary contract")
