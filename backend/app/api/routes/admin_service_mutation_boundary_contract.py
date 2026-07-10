from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

ADMIN_SERVICE_MUTATION_BOUNDARY_CONTRACT: dict[str, Any] = {
    "version": "v248.backend-admin-service-mutation-boundary-contract",
    "status": "admin-service-mutation-boundary-v248",
    "mutationCalls": ["add", "add_all", "delete", "flush", "commit"],
    "applyMethods": [
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "apply_master_data_create"],
        ["backend/app/services/admin/admin_edit_draft_service.py", "apply_master_data_edit"],
        ["backend/app/services/admin/admin_change_log_service.py", "apply_admin_change_log_rollback"],
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "apply_admin_create_delete_rollback"],
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "apply_admin_create_delete_restore"],
    ],
}


def _calls(path: Path, name: str) -> list[str]:
    module=ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(module):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return [child.func.attr for child in ast.walk(node) if isinstance(child,ast.Call) and isinstance(child.func,ast.Attribute)]
    return []


def get_admin_service_mutation_boundary_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    root_path=Path(root) if root else Path(__file__).resolve().parents[5]
    mutation=set(ADMIN_SERVICE_MUTATION_BOUNDARY_CONTRACT["mutationCalls"])
    checks=[]
    for relative,name in ADMIN_SERVICE_MUTATION_BOUNDARY_CONTRACT["applyMethods"]:
        found=sorted(mutation.intersection(_calls(root_path/relative,name)))
        checks.append({"key":name,"ok":bool(found),"mutationCallsFound":found})
    failed=[item for item in checks if not item["ok"]]
    return {"ok":not failed,"version":ADMIN_SERVICE_MUTATION_BOUNDARY_CONTRACT["version"],"status":ADMIN_SERVICE_MUTATION_BOUNDARY_CONTRACT["status"],"checks":checks,"failedChecks":failed,"dbWriteAttemptCount":0}
