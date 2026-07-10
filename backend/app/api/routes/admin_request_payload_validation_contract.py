from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.schemas import admin as admin_schemas


ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT: dict[str, Any] = {
    "version": "v240.backend-admin-request-payload-validation-contract",
    "status": "admin-request-payload-validation-v240",
    "policy": "Admin body aliases and representative FastAPI 422 validation detail must not drift; validation must stop before service or DB execution",
    "cases": [
        {
            "key": "master-create-preview",
            "path": "/master-data/create-preview",
            "model": "AdminMasterDataCreatePreviewRequest",
            "valid": {"domain": " items ", "draft": {"name": "Potion"}, "reason": " preview ", "dryRun": True},
            "expectedAliasDump": {"domain": "items", "draft": {"name": "Potion"}, "reason": "preview", "dryRun": True},
            "invalid": {},
            "expected422": {"type": "missing", "loc": ["body", "domain"], "msg": "Field required"},
        },
        {
            "key": "master-create-apply",
            "path": "/master-data/create-apply",
            "model": "AdminMasterDataCreateApplyRequest",
            "valid": {"domain": "items", "draft": {}, "confirmText": " APPLY ", "dryRun": False},
            "expectedAliasDump": {"domain": "items", "draft": {}, "reason": None, "dryRun": False, "confirmText": "APPLY"},
            "invalid": {"domain": "items", "confirmText": "x" * 81},
            "expected422": {"type": "string_too_long", "loc": ["body", "confirmText"], "msg": "String should have at most 80 characters"},
        },
        {
            "key": "master-edit-preview",
            "path": "/master-data/edit-preview",
            "model": "AdminMasterDataEditPreviewRequest",
            "valid": {"domain": "items", "id": 1, "draft": {}, "baseValues": {"name": "Old"}, "dryRun": True},
            "expectedAliasDump": {"domain": "items", "id": 1, "draft": {}, "baseValues": {"name": "Old"}, "reason": None, "dryRun": True},
            "invalid": {"domain": "items", "id": 0},
            "expected422": {"type": "greater_than_equal", "loc": ["body", "id"], "msg": "Input should be greater than or equal to 1"},
        },
        {
            "key": "master-edit-apply",
            "path": "/master-data/edit-apply",
            "model": "AdminMasterDataEditApplyRequest",
            "valid": {"domain": "items", "id": 1, "draft": {}, "baseValues": None, "confirmText": " APPLY ", "dryRun": False},
            "expectedAliasDump": {"domain": "items", "id": 1, "draft": {}, "baseValues": None, "reason": None, "dryRun": False, "confirmText": "APPLY"},
            "invalid": {"domain": "   ", "id": 1},
            "expected422": {"type": "string_too_short", "loc": ["body", "domain"], "msg": "String should have at least 1 character"},
        },
        {
            "key": "change-log-rollback-preview",
            "path": "/change-logs/rollback-preview",
            "model": "AdminChangeLogRollbackPreviewRequest",
            "valid": {"reason": " rollback ", "dryRun": True},
            "expectedAliasDump": {"reason": "rollback", "dryRun": True},
            "invalid": {"reason": "x" * 501},
            "expected422": {"type": "string_too_long", "loc": ["body", "reason"], "msg": "String should have at most 500 characters"},
        },
        {
            "key": "change-log-rollback-apply",
            "path": "/change-logs/rollback-apply",
            "model": "AdminChangeLogRollbackApplyRequest",
            "valid": {"reason": None, "confirmText": " ROLLBACK ", "dryRun": False},
            "expectedAliasDump": {"reason": None, "dryRun": False, "confirmText": "ROLLBACK"},
            "invalid": {"dryRun": "not-a-bool"},
            "expected422": {"type": "bool_parsing", "loc": ["body", "dryRun"], "msg": "Input should be a valid boolean, unable to interpret input"},
        },
        {
            "key": "create-delete-preview",
            "path": "/change-logs/create-delete-preview",
            "model": "AdminCreateDeletePreviewRequest",
            "valid": {"reason": None, "dryRun": True},
            "expectedAliasDump": {"reason": None, "dryRun": True},
            "invalid": {"reason": 123},
            "expected422": {"type": "string_type", "loc": ["body", "reason"], "msg": "Input should be a valid string"},
        },
        {
            "key": "create-delete-apply",
            "path": "/change-logs/create-delete-apply",
            "model": "AdminCreateDeleteApplyRequest",
            "valid": {"confirmText": " DELETE ", "dryRun": False},
            "expectedAliasDump": {"reason": None, "dryRun": False, "confirmText": "DELETE"},
            "invalid": {"confirmText": ["DELETE"]},
            "expected422": {"type": "string_type", "loc": ["body", "confirmText"], "msg": "Input should be a valid string"},
        },
        {
            "key": "create-delete-restore-preview",
            "path": "/change-logs/create-delete-restore-preview",
            "model": "AdminCreateDeleteRestorePreviewRequest",
            "valid": {"reason": " restore ", "dryRun": True},
            "expectedAliasDump": {"reason": "restore", "dryRun": True},
            "invalid": {"dryRun": {}},
            "expected422": {"type": "bool_type", "loc": ["body", "dryRun"], "msg": "Input should be a valid boolean"},
        },
        {
            "key": "create-delete-restore-apply",
            "path": "/change-logs/create-delete-restore-apply",
            "model": "AdminCreateDeleteRestoreApplyRequest",
            "valid": {"confirmText": " RESTORE ", "dryRun": False},
            "expectedAliasDump": {"reason": None, "dryRun": False, "confirmText": "RESTORE"},
            "invalid": {"confirmText": "x" * 81},
            "expected422": {"type": "string_too_long", "loc": ["body", "confirmText"], "msg": "String should have at most 80 characters"},
        },
    ],
}


def _build_validation_app() -> FastAPI:
    app = FastAPI()

    for index, case in enumerate(ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT["cases"]):
        model: type[BaseModel] = getattr(admin_schemas, case["model"])

        def endpoint(payload: BaseModel = Body(...)) -> dict[str, Any]:
            return {"payload": payload.model_dump(by_alias=True)}

        endpoint.__name__ = f"validate_admin_payload_{index}"
        endpoint.__annotations__["payload"] = model
        app.post(case["path"])(endpoint)

    return app


def _compact_error(error: dict[str, Any]) -> dict[str, Any]:
    return {"type": error.get("type"), "loc": error.get("loc"), "msg": error.get("msg")}


def get_admin_request_payload_validation_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT
    client = TestClient(_build_validation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        valid_response = client.post(case["path"], json=case["valid"])
        valid_json = valid_response.json() if valid_response.headers.get("content-type", "").startswith("application/json") else {}
        alias_dump = valid_json.get("payload")
        valid_ok = valid_response.status_code == 200 and alias_dump == case["expectedAliasDump"]
        checks.append({
            "key": f"{case['key']}:alias-serialization",
            "ok": valid_ok,
            "expectedStatus": 200,
            "actualStatus": valid_response.status_code,
            "expected": case["expectedAliasDump"],
            "actual": alias_dump,
        })

        invalid_response = client.post(case["path"], json=case["invalid"])
        invalid_json = invalid_response.json() if invalid_response.headers.get("content-type", "").startswith("application/json") else {}
        detail = invalid_json.get("detail", [])
        first_error = _compact_error(detail[0]) if detail else None
        validation_ok = invalid_response.status_code == 422 and first_error == case["expected422"]
        checks.append({
            "key": f"{case['key']}:422-detail",
            "ok": validation_ok,
            "expectedStatus": 422,
            "actualStatus": invalid_response.status_code,
            "expected": case["expected422"],
            "actual": first_error,
        })

    failed = [check for check in checks if not check["ok"]]
    return {
        "ok": not failed,
        "version": contract["version"],
        "status": contract["status"],
        "caseCount": len(contract["cases"]),
        "checkCount": len(checks),
        "checks": checks,
        "failedChecks": failed,
        "dbWriteAttemptCount": 0,
        "serviceCallCount": 0,
    }
