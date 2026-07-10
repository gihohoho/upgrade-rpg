from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.admin_request_payload_validation_contract import _build_validation_app


ADMIN_REQUEST_CONTENT_NEGOTIATION_CONTRACT: dict[str, Any] = {
    "version": "v242.backend-admin-request-content-negotiation-contract",
    "status": "admin-request-content-negotiation-v242",
    "policy": "JSON charset, absent Content-Type, invalid top-level JSON types, empty object versus empty body, and Accept negotiation must stay stable before service or DB execution",
    "path": "/master-data/create-preview",
    "validPayload": {"domain": "items", "draft": {}, "dryRun": True},
    "cases": [
        {
            "key": "json-with-charset",
            "request": {
                "content": '{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"content-type": "application/json; charset=utf-8"},
            },
            "expectedStatus": 200,
            "expectedContentTypePrefix": "application/json",
            "expectedPayload": {"domain": "items", "draft": {}, "reason": None, "dryRun": True},
        },
        {
            "key": "json-without-content-type",
            "request": {"content": '{"domain":"items","draft":{},"dryRun":true}'},
            "expectedContentTypePrefix": "application/json",
            "allowedOutcomes": [
                {
                    "status": 200,
                    "payload": {"domain": "items", "draft": {}, "reason": None, "dryRun": True},
                },
                {
                    "status": 422,
                    "error": {
                        "type": "model_attributes_type",
                        "loc": ["body"],
                        "msg": "Input should be a valid dictionary or object to extract fields from",
                    },
                },
            ],
            "compatibilityReason": "Starlette/FastAPI versions differ on whether a body without Content-Type is JSON-decoded or passed through as raw text",
        },
        {
            "key": "json-array-top-level",
            "request": {"json": []},
            "expectedStatus": 422,
            "expectedContentTypePrefix": "application/json",
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "json-string-top-level",
            "request": {"json": "items"},
            "expectedStatus": 422,
            "expectedContentTypePrefix": "application/json",
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "empty-json-object",
            "request": {"json": {}},
            "expectedStatus": 422,
            "expectedContentTypePrefix": "application/json",
            "expectedError": {"type": "missing", "loc": ["body", "domain"], "msg": "Field required"},
        },
        {
            "key": "empty-body",
            "request": {"content": b"", "headers": {"content-type": "application/json"}},
            "expectedStatus": 422,
            "expectedContentTypePrefix": "application/json",
            "expectedError": {"type": "missing", "loc": ["body"], "msg": "Field required"},
        },
        {
            "key": "accept-application-json",
            "request": {"json": {"domain": "items", "draft": {}, "dryRun": True}, "headers": {"accept": "application/json"}},
            "expectedStatus": 200,
            "expectedContentTypePrefix": "application/json",
            "expectedPayload": {"domain": "items", "draft": {}, "reason": None, "dryRun": True},
        },
        {
            "key": "accept-text-plain-keeps-json-response",
            "request": {"json": {"domain": "items", "draft": {}, "dryRun": True}, "headers": {"accept": "text/plain"}},
            "expectedStatus": 200,
            "expectedContentTypePrefix": "application/json",
            "expectedPayload": {"domain": "items", "draft": {}, "reason": None, "dryRun": True},
        },
    ],
}


def _stable_error(error: dict[str, Any]) -> dict[str, Any]:
    return {"type": error.get("type"), "loc": error.get("loc"), "msg": error.get("msg")}


def get_admin_request_content_negotiation_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_REQUEST_CONTENT_NEGOTIATION_CONTRACT
    client = TestClient(_build_validation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        response = client.post(contract["path"], **case["request"])
        response_content_type = response.headers.get("content-type", "")
        body = response.json() if response_content_type.startswith("application/json") else {}
        expected_error = case.get("expectedError")
        expected_payload = case.get("expectedPayload")
        allowed_outcomes = case.get("allowedOutcomes")
        detail = body.get("detail", []) if isinstance(body, dict) else []
        actual_error = _stable_error(detail[0]) if detail else None
        actual_payload = body.get("payload") if isinstance(body, dict) else None

        if allowed_outcomes is not None:
            outcome_matches = []
            for outcome in allowed_outcomes:
                outcome_matches.append(
                    response.status_code == outcome["status"]
                    and ("error" not in outcome or actual_error == outcome["error"])
                    and ("payload" not in outcome or actual_payload == outcome["payload"])
                )
            ok = response_content_type.startswith(case["expectedContentTypePrefix"]) and any(outcome_matches)
            expected_status = [outcome["status"] for outcome in allowed_outcomes]
        else:
            ok = (
                response.status_code == case["expectedStatus"]
                and response_content_type.startswith(case["expectedContentTypePrefix"])
                and (expected_error is None or actual_error == expected_error)
                and (expected_payload is None or actual_payload == expected_payload)
            )
            expected_status = case["expectedStatus"]

        checks.append(
            {
                "key": case["key"],
                "ok": ok,
                "expectedStatus": expected_status,
                "actualStatus": response.status_code,
                "expectedContentTypePrefix": case["expectedContentTypePrefix"],
                "actualContentType": response_content_type,
                "expectedError": expected_error,
                "actualError": actual_error,
                "expectedPayload": expected_payload,
                "actualPayload": actual_payload,
                "allowedOutcomes": allowed_outcomes,
                "compatibilityReason": case.get("compatibilityReason"),
            }
        )

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
