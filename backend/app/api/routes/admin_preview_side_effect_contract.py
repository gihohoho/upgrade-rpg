from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

ADMIN_PREVIEW_SIDE_EFFECT_CONTRACT: dict[str, Any] = {
    "version": "v247.backend-admin-preview-side-effect-static-contract",
    "status": "admin-preview-side-effect-static-v247",
    "forbiddenCalls": ["add", "add_all", "delete", "flush", "commit", "rollback"],
    "previewMethods": [
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "preview_master_data_create"],
        ["backend/app/services/admin/admin_edit_draft_service.py", "preview_master_data_edit"],
        ["backend/app/services/admin/admin_change_log_service.py", "preview_admin_change_log_rollback"],
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "preview_admin_create_delete_rollback"],
        ["backend/app/services/admin/admin_create_lifecycle_service.py", "preview_admin_create_delete_restore"],
    ],
}


def _method_calls(path: Path, name: str) -> list[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            calls=[]
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
            return calls
    return ["<missing-method>"]


def get_admin_preview_side_effect_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    root_path=Path(root) if root else Path(__file__).resolve().parents[5]
    forbidden=set(ADMIN_PREVIEW_SIDE_EFFECT_CONTRACT["forbiddenCalls"])
    checks=[]
    for relative,name in ADMIN_PREVIEW_SIDE_EFFECT_CONTRACT["previewMethods"]:
        calls=_method_calls(root_path/relative,name)
        blocked=sorted(forbidden.intersection(calls))
        checks.append({"key":name,"ok":not blocked and "<missing-method>" not in calls,"forbiddenCallsFound":blocked})
    failed=[item for item in checks if not item["ok"]]
    return {"ok":not failed,"version":ADMIN_PREVIEW_SIDE_EFFECT_CONTRACT["version"],"status":ADMIN_PREVIEW_SIDE_EFFECT_CONTRACT["status"],"checks":checks,"failedChecks":failed,"dbWriteAttemptCount":0}
