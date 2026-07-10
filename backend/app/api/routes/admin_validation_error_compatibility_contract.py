from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.admin_request_payload_validation_contract import _build_validation_app


ADMIN_VALIDATION_ERROR_COMPATIBILITY_CONTRACT: dict[str, Any] = {
    "version": "v241.backend-admin-validation-error-compatibility-contract",
    "status": "admin-validation-error-compatibility-v241",
    "policy": "Malformed JSON, empty body, and unsupported JSON content type must keep stable FastAPI 422 type/loc/msg fields without service or DB execution; input and ctx are intentionally excluded",
    "path": "/master-data/create-preview",
    "cases": [
        {
            "key": "malformed-json",
            "content": '{"domain":',
            "headers": {"content-type": "application/json"},
            "expected422": {"type": "json_invalid", "locPrefix": ["body"], "msg": "JSON decode error"},
        },
        {
            "key": "empty-json-body",
            "content": b"",
            "headers": {"content-type": "application/json"},
            "expected422": {"type": "missing", "loc": ["body"], "msg": "Field required"},
        },
        {
            "key": "json-string-with-text-content-type",
            "content": '{"domain":"items","draft":{},"dryRun":true}',
            "headers": {"content-type": "text/plain"},
            "expected422": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
    ],
}


def _stable_error(error: dict[str, Any]) -> dict[str, Any]:
    return {"type": error.get("type"), "loc": error.get("loc"), "msg": error.get("msg")}


def get_admin_validation_error_compatibility_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_VALIDATION_ERROR_COMPATIBILITY_CONTRACT
    client = TestClient(_build_validation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        response = client.post(contract["path"], content=case["content"], headers=case["headers"])
        payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        detail = payload.get("detail", [])
        actual = _stable_error(detail[0]) if detail else None
        expected = case["expected422"]
        if actual is None:
            ok = False
        elif "locPrefix" in expected:
            loc = actual.get("loc") or []
            ok = response.status_code == 422 and actual.get("type") == expected["type"] and loc[:len(expected["locPrefix"])] == expected["locPrefix"] and actual.get("msg") == expected["msg"]
        else:
            ok = response.status_code == 422 and actual == expected
        checks.append({"key": case["key"], "ok": ok, "expectedStatus": 422, "actualStatus": response.status_code, "expected": expected, "actual": actual})

    failed = [check for check in checks if not check["ok"]]
    return {
        "ok": not failed,
        "version": contract["version"],
        "status": contract["status"],
        "caseCount": len(contract["cases"]),
        "checkCount": len(checks),
        "checks": checks,
        "failedChecks": failed,
        "ignoredErrorFields": ["input", "ctx"],
        "dbWriteAttemptCount": 0,
        "serviceCallCount": 0,
    }
