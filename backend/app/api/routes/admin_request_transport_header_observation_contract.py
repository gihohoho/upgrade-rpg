from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


ADMIN_REQUEST_TRANSPORT_HEADER_OBSERVATION_CONTRACT: dict[str, Any] = {
    "version": "v245.backend-admin-transport-header-observation-contract",
    "status": "admin-request-transport-header-observation-v245",
    "policy": (
        "Duplicate headers and transport metadata are observed at the ASGI/TestClient boundary only; "
        "wire framing and request-smuggling defense remain deployment server or proxy responsibilities, "
        "while the application enforces its own bounded body size"
    ),
    "path": "/observe-request-transport",
    "cases": [
        {
            "key": "duplicate-content-type",
            "content": b"{}",
            "headers": [
                ("content-type", "application/json"),
                ("content-type", "text/plain"),
            ],
            "header": "content-type",
            "expectedRawValues": ["application/json", "text/plain"],
            "expectedSelectedValue": "application/json",
        },
        {
            "key": "duplicate-accept",
            "content": b"{}",
            "headers": [
                ("accept", "application/json"),
                ("accept", "text/plain"),
            ],
            "header": "accept",
            "expectedRawValues": ["application/json", "text/plain"],
            "expectedSelectedValue": "application/json",
        },
        {
            "key": "declared-content-length-mismatch",
            "content": b"{}",
            "headers": [
                ("content-type", "application/json"),
                ("content-length", "999"),
            ],
            "header": "content-length",
            "expectedRawValues": ["999"],
            "expectedSelectedValue": "999",
            "expectedBodyLength": 2,
            "observationOnly": True,
        },
        {
            "key": "transfer-encoding-header-observation",
            "content": b"{}",
            "headers": [
                ("content-type", "application/json"),
                ("transfer-encoding", "chunked"),
            ],
            "header": "transfer-encoding",
            "expectedRawValues": ["chunked"],
            "expectedSelectedValue": "chunked",
            "expectedBodyLength": 2,
            "observationOnly": True,
        },
    ],
    "networkBoundary": {
        "testClientCanObserveRawASGIHeaders": True,
        "testClientCanProveWireChunkFraming": False,
        "testClientCanProveServerContentLengthRejection": False,
        "testClientCanProveRequestSmugglingDefense": False,
        "enforcementOwner": "deployment-proxy-or-asgi-server-configuration",
        "applicationBodyLimitOwner": "pure-asgi-request-body-limit-middleware",
    },
}


def _build_observation_app() -> FastAPI:
    app = FastAPI()

    @app.post(ADMIN_REQUEST_TRANSPORT_HEADER_OBSERVATION_CONTRACT["path"])
    async def observe_request_transport(request: Request) -> dict[str, Any]:
        body = await request.body()
        raw_headers = [
            [key.decode("latin-1"), value.decode("latin-1")]
            for key, value in request.scope.get("headers", [])
        ]
        return {
            "rawHeaders": raw_headers,
            "selectedHeaders": {
                "content-type": request.headers.get("content-type"),
                "accept": request.headers.get("accept"),
                "content-length": request.headers.get("content-length"),
                "transfer-encoding": request.headers.get("transfer-encoding"),
            },
            "bodyLength": len(body),
        }

    return app


def _raw_values(raw_headers: list[list[str]], name: str) -> list[str]:
    lowered = name.lower()
    return [value for key, value in raw_headers if key.lower() == lowered]


def get_admin_request_transport_header_observation_contract_readiness() -> dict[str, Any]:
    contract = ADMIN_REQUEST_TRANSPORT_HEADER_OBSERVATION_CONTRACT
    client = TestClient(_build_observation_app())
    checks: list[dict[str, Any]] = []

    for case in contract["cases"]:
        response = client.post(contract["path"], content=case["content"], headers=case["headers"])
        payload = response.json()
        actual_raw_values = _raw_values(payload.get("rawHeaders", []), case["header"])
        actual_selected_value = payload.get("selectedHeaders", {}).get(case["header"])
        actual_body_length = payload.get("bodyLength")
        ok = (
            response.status_code == 200
            and response.headers.get("content-type", "").startswith("application/json")
            and actual_raw_values == case["expectedRawValues"]
            and actual_selected_value == case["expectedSelectedValue"]
            and ("expectedBodyLength" not in case or actual_body_length == case["expectedBodyLength"])
        )
        checks.append(
            {
                "key": case["key"],
                "ok": ok,
                "actualStatus": response.status_code,
                "header": case["header"],
                "expectedRawValues": case["expectedRawValues"],
                "actualRawValues": actual_raw_values,
                "expectedSelectedValue": case["expectedSelectedValue"],
                "actualSelectedValue": actual_selected_value,
                "expectedBodyLength": case.get("expectedBodyLength"),
                "actualBodyLength": actual_body_length,
                "observationOnly": bool(case.get("observationOnly")),
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
        "networkBoundary": contract["networkBoundary"],
        "dbWriteAttemptCount": 0,
        "serviceCallCount": 0,
    }
