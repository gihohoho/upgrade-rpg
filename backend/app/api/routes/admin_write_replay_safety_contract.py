from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.schemas import admin as admin_schemas


ADMIN_WRITE_REPLAY_SAFETY_CONTRACT: dict[str, Any] = {
    "version": "v246.backend-admin-write-replay-safety-contract",
    "status": "admin-write-replay-safety-v246",
    "policy": (
        "Preview request parsing must be deterministic, all five apply routes must retain ADMIN_WRITE_GUARD_DEP, "
        "and no idempotency-key support may be claimed until an explicit implementation exists"
    ),
    "previewCases": [
        {"key": "master-create-preview", "model": "AdminMasterDataCreatePreviewRequest", "payload": {"domain": "items", "draft": {}, "reason": "preview", "dryRun": True}},
        {"key": "master-edit-preview", "model": "AdminMasterDataEditPreviewRequest", "payload": {"domain": "items", "id": 1, "draft": {}, "baseValues": {}, "reason": "preview", "dryRun": True}},
        {"key": "rollback-preview", "model": "AdminChangeLogRollbackPreviewRequest", "payload": {"reason": "preview", "dryRun": True}},
        {"key": "create-delete-preview", "model": "AdminCreateDeletePreviewRequest", "payload": {"reason": "preview", "dryRun": True}},
        {"key": "create-delete-restore-preview", "model": "AdminCreateDeleteRestorePreviewRequest", "payload": {"reason": "preview", "dryRun": True}},
    ],
    "applyFunctions": [
        ["backend/app/api/routes/admin_master_data_routes.py", "apply_admin_master_data_create"],
        ["backend/app/api/routes/admin_master_data_routes.py", "apply_admin_master_data_edit"],
        ["backend/app/api/routes/admin_change_log_routes.py", "apply_admin_create_delete_rollback"],
        ["backend/app/api/routes/admin_change_log_routes.py", "apply_admin_create_delete_restore"],
        ["backend/app/api/routes/admin_change_log_routes.py", "apply_admin_change_log_rollback"],
    ],
    "idempotency": {
        "supported": False,
        "header": "Idempotency-Key",
        "policy": "unsupported-observation-only",
    },
}


def _build_replay_app() -> FastAPI:
    app = FastAPI()
    for index, case in enumerate(ADMIN_WRITE_REPLAY_SAFETY_CONTRACT["previewCases"]):
        model: type[BaseModel] = getattr(admin_schemas, case["model"])

        def endpoint(payload: BaseModel = Body(...)) -> dict[str, Any]:
            return {"payload": payload.model_dump(by_alias=True)}

        endpoint.__name__ = f"preview_replay_{index}"
        endpoint.__annotations__["payload"] = model
        app.post(f"/preview-replay/{index}")(endpoint)
    return app


def _function_has_write_guard(path: Path, function_name: str) -> bool:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            args = node.args.args
            defaults = node.args.defaults
            default_map = {arg.arg: default for arg, default in zip(args[-len(defaults):], defaults)} if defaults else {}
            guard = default_map.get("_write_guard")
            return isinstance(guard, ast.Name) and guard.id == "ADMIN_WRITE_GUARD_DEP"
    return False


def get_admin_write_replay_safety_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    contract = ADMIN_WRITE_REPLAY_SAFETY_CONTRACT
    client = TestClient(_build_replay_app())
    checks: list[dict[str, Any]] = []

    for index, case in enumerate(contract["previewCases"]):
        first = client.post(f"/preview-replay/{index}", json=case["payload"])
        second = client.post(f"/preview-replay/{index}", json=case["payload"])
        first_payload = first.json().get("payload") if first.status_code == 200 else None
        second_payload = second.json().get("payload") if second.status_code == 200 else None
        checks.append({
            "key": f"{case['key']}:repeat-parse",
            "ok": first.status_code == 200 and second.status_code == 200 and first_payload == second_payload,
            "firstStatus": first.status_code,
            "secondStatus": second.status_code,
            "firstPayload": first_payload,
            "secondPayload": second_payload,
        })

    root_path = Path(root) if root is not None else Path(__file__).resolve().parents[5]
    for relative, function_name in contract["applyFunctions"]:
        ok = _function_has_write_guard(root_path / relative, function_name)
        checks.append({"key": f"{function_name}:write-guard", "ok": ok, "expected": "ADMIN_WRITE_GUARD_DEP"})

    searched_files = [root_path / item[0] for item in contract["applyFunctions"]]
    idempotency_mentions = [str(path.relative_to(root_path)) for path in sorted(set(searched_files)) if "idempotency-key" in path.read_text(encoding="utf-8").lower()]
    checks.append({
        "key": "idempotency-key-support-observation",
        "ok": not idempotency_mentions and contract["idempotency"]["supported"] is False,
        "supported": contract["idempotency"]["supported"],
        "mentions": idempotency_mentions,
    })

    failed = [item for item in checks if not item["ok"]]
    return {
        "ok": not failed,
        "version": contract["version"],
        "status": contract["status"],
        "checkCount": len(checks),
        "checks": checks,
        "failedChecks": failed,
        "idempotency": contract["idempotency"],
        "dbWriteAttemptCount": 0,
        "serviceCallCount": 0,
    }
