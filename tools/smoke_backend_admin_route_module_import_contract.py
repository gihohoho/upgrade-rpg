"""Static/runtime smoke test for v224 backend admin route module import contract.

Run from the project root:

    python tools/smoke_backend_admin_route_module_import_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api.routes.admin_route_module_import_contract import (  # noqa: E402
    ADMIN_ROUTE_MODULE_IMPORT_CONTRACT,
    get_admin_route_module_import_contract_readiness,
)
from app.api.routes.admin_route_map_contract import get_admin_route_module_contract_readiness  # noqa: E402
from app.services.admin_service import AdminService  # noqa: E402
from app.services.admin_service_split_contract import get_admin_service_split_contract_readiness  # noqa: E402

SPLIT_CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


import_readiness = get_admin_route_module_import_contract_readiness(root=ROOT)
route_readiness = get_admin_route_module_contract_readiness(root=ROOT)
split_readiness = get_admin_service_split_contract_readiness(AdminService, root=ROOT)
split_contract_source = read(SPLIT_CONTRACT)
entry_source = read(ENTRY)
run_smoke_source = read(RUN_SMOKE)

assert_true(ADMIN_ROUTE_MODULE_IMPORT_CONTRACT["version"] == "v224.backend-admin-route-module-import-contract", "route module import contract version mismatch")
assert_true(ADMIN_ROUTE_MODULE_IMPORT_CONTRACT["status"] == "route-module-imports-frozen-v224", "route module import contract status mismatch")
assert_true(import_readiness["ok"], f"route module import readiness failed: {import_readiness}")
assert_true(import_readiness["moduleCount"] == 3, "route module import contract should cover three modules")
assert_true(not import_readiness["failedModules"], "route module import contract should not have failed modules")
assert_true(route_readiness["ok"], f"strict route ownership should still pass: {route_readiness}")
assert_true(route_readiness["status"] == "route-ownership-strict-v223", "route ownership contract should stay strict")
assert_true(split_readiness["splitStatus"] == "admin-schema-field-constraint-contract-v238", "splitStatus should be v224")
assert_true("backend/app/api/routes/admin_route_module_import_contract.py" in split_readiness["extractedFiles"], "split contract should include route module import contract file")
assert_true('"key": "route-module-import-contract"' in split_contract_source, "split contract should include route-module-import-contract group")
assert_true('"Admin route module import/dependency style is tracked by admin_route_module_import_contract.py"' in split_contract_source, "split contract should mention route module import contract")
assert_true('const VERSION = "v242.backend-admin-request-content-negotiation-contract"' in entry_source, "frontend readiness version should be v224")
assert_true('splitStatus: "admin-schema-field-constraint-contract-v238"' in entry_source, "frontend splitStatus should be v224")
assert_true("backendRouteModuleImportContractReady" in entry_source, "frontend top-level route module import readiness flag missing")
assert_true("routeModuleImportContractReady" in entry_source, "contract route module import readiness flag missing")
assert_true("smoke_backend_admin_route_module_import_contract.py" in run_smoke_source, "core smoke should include v224 smoke")

print("backend admin route module import contract smoke test passed")
