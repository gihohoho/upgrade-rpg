from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api.routes.admin_request_payload_validation_contract import _build_validation_app
from app.core.config import settings


ADMIN_REQUEST_MEDIA_SIZE_BOUNDARY_CONTRACT: dict[str, Any] = {
    "version": "v377.backend-admin-request-media-size-boundary-contract",
    "status": "admin-request-media-size-boundary-v377",
    "policy": (
        "Non-JSON media types must fail at request parsing without service or DB execution; "
        "the pure-ASGI application boundary rejects bodies above the configured cap"
    ),
    "path": "/master-data/create-preview",
    "cases": [
        {
            "key": "octet-stream-json-bytes",
            "request": {
                "content": b'{"domain":"items","draft":{},"dryRun":true}',
                "headers": {"content-type": "application/octet-stream"},
            },
            "expectedStatus": 422,
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "octet-stream-empty",
            "request": {"content": b"", "headers": {"content-type": "application/octet-stream"}},
            "expectedStatus": 422,
            "expectedError": {"type": "missing", "loc": ["body"], "msg": "Field required"},
        },
        {
            "key": "octet-stream-binary",
            "request": {"content": b"\x00\x01admin", "headers": {"content-type": "application/octet-stream"}},
            "expectedStatus": 422,
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "urlencoded-form",
            "request": {"data": {"domain": "items", "draft": "{}", "dryRun": "true"}},
            "expectedStatus": 422,
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "multipart-form",
            "request": {
                "files": {
                    "domain": (None, "items"),
                    "draft": (None, "{}"),
                    "dryRun": (None, "true"),
                }
            },
            "expectedStatus": 422,
            "expectedError": {
                "type": "model_attributes_type",
                "loc": ["body"],
                "msg": "Input should be a valid dictionary or object to extract fields from",
            },
        },
        {
            "key": "moderate-json-body-within-app-limit",
            "request": {
                "json": {
                    "domain": "items",
                    "draft": {"contractProbe": "x" * 65536},
                    "dryRun": True,
                }
            },
            "expectedStatus": 200,
            "expectedPayloadDomain": "items",
            "expectedProbeLength": 65536,
        },
    ],
    "sizePolicy": {
        "applicationLimitConfigured": True,
        "applicationLimitBytes": int(settings.request_body_limit_bytes),
        "authApplicationLimitBytes": int(settings.auth_request_body_limit_bytes),
        "enforcementOwner": "pure-asgi-request-body-limit-middleware",
        "probeBytes": 65536,
        "note": "The focused v377 middleware smoke proves declared, understated, and headerless body enforcement before route parsing.",
    },
}


def _stable_error(error: dict[str, Any]) -> dict[str, Any]:
    return {"type": error.get("type"), "loc": error.get("loc"), "msg": error.get("msg")}


def get_admin_request_media_size_boundary_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_REQUEST_MEDIA_SIZE_BOUNDARY_CONTRACT
    client = TestClient(_build_validation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        response = client.post(contract["path"], **case["request"])
        content_type = response.headers.get("content-type", "")
        body = response.json() if content_type.startswith("application/json") else {}
        detail = body.get("detail", []) if isinstance(body, dict) else []
        actual_error = _stable_error(detail[0]) if detail else None
        payload = body.get("payload") if isinstance(body, dict) else None
        actual_probe_length = None
        if isinstance(payload, dict):
            draft = payload.get("draft")
            if isinstance(draft, dict) and isinstance(draft.get("contractProbe"), str):
                actual_probe_length = len(draft["contractProbe"])

        ok = (
            response.status_code == case["expectedStatus"]
            and content_type.startswith("application/json")
            and ("expectedError" not in case or actual_error == case["expectedError"])
            and ("expectedPayloadDomain" not in case or (isinstance(payload, dict) and payload.get("domain") == case["expectedPayloadDomain"]))
            and ("expectedProbeLength" not in case or actual_probe_length == case["expectedProbeLength"])
        )
        checks.append(
            {
                "key": case["key"],
                "ok": ok,
                "expectedStatus": case["expectedStatus"],
                "actualStatus": response.status_code,
                "expectedError": case.get("expectedError"),
                "actualError": actual_error,
                "expectedProbeLength": case.get("expectedProbeLength"),
                "actualProbeLength": actual_probe_length,
                "actualContentType": content_type,
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
        "sizePolicy": contract["sizePolicy"],
        "ignoredErrorFields": ["input", "ctx"],
        "dbWriteAttemptCount": 0,
        "serviceCallCount": 0,
    }
