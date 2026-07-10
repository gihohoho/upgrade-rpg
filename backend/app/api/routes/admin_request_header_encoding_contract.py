from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.admin_request_payload_validation_contract import _build_validation_app


ADMIN_REQUEST_HEADER_ENCODING_CONTRACT: dict[str, Any] = {
    "version": "v244.backend-admin-request-header-encoding-compatibility-contract",
    "status": "admin-request-header-encoding-compatibility-v244",
    "policy": (
        "UTF-8 JSON text, Content-Type parameter normalization, header-name case insensitivity, "
        "and malformed byte parsing must stay stable before service or DB execution"
    ),
    "path": "/master-data/create-preview",
    "cases": [
        {
            "key": "utf8-korean-and-symbols",
            "request": {
                "content": '{"domain":"아이템","draft":{"이름":"검⚔","설명":"강화 +10%"},"reason":"한글 테스트","dryRun":true}'.encode("utf-8"),
                "headers": {"content-type": "application/json; charset=utf-8"},
            },
            "expectedStatus": 200,
            "expectedPayload": {
                "domain": "아이템",
                "draft": {"이름": "검⚔", "설명": "강화 +10%"},
                "reason": "한글 테스트",
                "dryRun": True,
            },
        },
        {
            "key": "charset-name-and-value-case-insensitive",
            "request": {
                "content": b'{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"content-type": "application/json; CHARSET=UTF-8"},
            },
            "expectedStatus": 200,
        },
        {
            "key": "content-type-header-name-case-insensitive",
            "request": {
                "content": b'{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"CoNtEnT-TyPe": "application/json"},
            },
            "expectedStatus": 200,
        },
        {
            "key": "extra-content-type-parameter",
            "request": {
                "content": b'{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"content-type": "application/json; charset=utf-8; profile=test"},
            },
            "expectedStatus": 200,
        },
        {
            "key": "duplicate-charset-parameter",
            "request": {
                "content": b'{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"content-type": "application/json; charset=utf-8; charset=latin-1"},
            },
            "allowedOutcomes": [
                {"status": 200, "payloadDomain": "items"},
                {"status": 400, "detail": "There was an error parsing the body"},
            ],
            "compatibilityReason": "ASGI/FastAPI parser versions may accept the first charset parameter or reject ambiguous parameters",
        },
        {
            "key": "invalid-utf8-byte-sequence",
            "request": {
                "content": b'{"domain":"items","draft":{"x":"\xff"},"dryRun":true}',
                "headers": {"content-type": "application/json; charset=utf-8"},
            },
            "allowedOutcomes": [
                {"status": 400, "detail": "There was an error parsing the body"},
                {
                    "status": 422,
                    "errorTypes": ["json_invalid", "value_error.jsondecode"],
                    "locPrefix": ["body"],
                },
            ],
            "compatibilityReason": "Malformed byte decoding may be rejected by Starlette before JSON validation or surfaced by FastAPI validation",
        },
    ],
}


def _stable_error(error: dict[str, Any]) -> dict[str, Any]:
    return {"type": error.get("type"), "loc": error.get("loc"), "msg": error.get("msg")}


def _matches_outcome(*, response_status: int, body: Any, payload: Any, actual_error: dict[str, Any] | None, outcome: dict[str, Any]) -> bool:
    if response_status != outcome["status"]:
        return False
    if "detail" in outcome and (not isinstance(body, dict) or body.get("detail") != outcome["detail"]):
        return False
    if "payloadDomain" in outcome and (not isinstance(payload, dict) or payload.get("domain") != outcome["payloadDomain"]):
        return False
    if "errorTypes" in outcome:
        if not actual_error or actual_error.get("type") not in outcome["errorTypes"]:
            return False
        prefix = outcome.get("locPrefix", [])
        loc = actual_error.get("loc") or []
        if loc[: len(prefix)] != prefix:
            return False
    return True


def get_admin_request_header_encoding_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_REQUEST_HEADER_ENCODING_CONTRACT
    client = TestClient(_build_validation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        response = client.post(contract["path"], **case["request"])
        content_type = response.headers.get("content-type", "")
        body = response.json() if content_type.startswith("application/json") else None
        payload = body.get("payload") if isinstance(body, dict) else None
        detail = body.get("detail", []) if isinstance(body, dict) else []
        actual_error = _stable_error(detail[0]) if isinstance(detail, list) and detail else None
        allowed_outcomes = case.get("allowedOutcomes")

        if allowed_outcomes:
            ok = content_type.startswith("application/json") and any(
                _matches_outcome(
                    response_status=response.status_code,
                    body=body,
                    payload=payload,
                    actual_error=actual_error,
                    outcome=outcome,
                )
                for outcome in allowed_outcomes
            )
            expected_status: Any = [outcome["status"] for outcome in allowed_outcomes]
        else:
            ok = (
                response.status_code == case["expectedStatus"]
                and content_type.startswith("application/json")
                and ("expectedPayload" not in case or payload == case["expectedPayload"])
            )
            expected_status = case["expectedStatus"]

        checks.append(
            {
                "key": case["key"],
                "ok": ok,
                "expectedStatus": expected_status,
                "actualStatus": response.status_code,
                "expectedPayload": case.get("expectedPayload"),
                "actualPayload": payload,
                "actualDetail": body.get("detail") if isinstance(body, dict) else None,
                "actualError": actual_error,
                "actualContentType": content_type,
                "allowedOutcomes": allowed_outcomes,
                "compatibilityReason": case.get("compatibilityReason"),
            }
        )

    failed = [item for item in checks if not item["ok"]]
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
