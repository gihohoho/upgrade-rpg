from __future__ import annotations

import re
from typing import Any

from fastapi import FastAPI

from app.api.routes.admin_route_operation_contract import ADMIN_ROUTE_OPERATION_CONTRACT
from app.api.routes.admin_runtime_route_contract import ADMIN_RUNTIME_ROUTE_CONTRACT


ADMIN_OPENAPI_ROUTE_CONTRACT: dict[str, Any] = {
    "version": "v229.backend-admin-openapi-route-contract",
    "status": "openapi-route-metadata-v229",
    "policy": "FastAPI OpenAPI /api/v1/admin operation metadata must stay aligned with runtime route operation contracts",
    "apiPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"],
    "adminPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"],
    "sourceOperationContract": "backend/app/api/routes/admin_route_operation_contract.py",
    "sourceRuntimeContract": "backend/app/api/routes/admin_runtime_route_contract.py",
    "requiredTag": "admin",
}


def _full_admin_path(path: str) -> str:
    return f'{ADMIN_OPENAPI_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_OPENAPI_ROUTE_CONTRACT["adminPrefix"]}{path}'


def _operation_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def _expected_openapi_operation_id(endpoint: str, full_path: str, method: str) -> str:
    # Mirrors FastAPI's default unique-id shape for this project:
    # <endpoint><path-with-non-word-chars-as-underscores>_<method>
    return f'{endpoint}{re.sub(r"\W", "_", full_path)}_{method.lower()}'


def _expected_openapi_operations() -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    for operation in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]:
        method = operation["method"].upper()
        full_path = _full_admin_path(operation["path"])
        expected.append(
            {
                "method": method,
                "path": full_path,
                "sourcePath": operation["path"],
                "key": _operation_key(method, full_path),
                "endpoint": operation["endpoint"],
                "type": operation["type"],
                "owner": operation["owner"],
                "ownerFile": operation["ownerFile"],
                "operationId": _expected_openapi_operation_id(operation["endpoint"], full_path, method),
                "requiredTag": ADMIN_OPENAPI_ROUTE_CONTRACT["requiredTag"],
            }
        )
    return expected


def _openapi_admin_operations(app: FastAPI) -> list[dict[str, Any]]:
    schema = app.openapi()
    paths = schema.get("paths", {}) if isinstance(schema, dict) else {}
    base = f'{ADMIN_OPENAPI_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_OPENAPI_ROUTE_CONTRACT["adminPrefix"]}'
    actual: list[dict[str, Any]] = []
    for path, method_map in paths.items():
        if not isinstance(path, str) or not path.startswith(base):
            continue
        if not isinstance(method_map, dict):
            continue
        for method, meta in method_map.items():
            if not isinstance(meta, dict):
                continue
            method_upper = method.upper()
            actual.append(
                {
                    "method": method_upper,
                    "path": path,
                    "key": _operation_key(method_upper, path),
                    "operationId": meta.get("operationId"),
                    "summary": meta.get("summary"),
                    "tags": meta.get("tags") or [],
                    "responseCodes": sorted((meta.get("responses") or {}).keys()),
                }
            )
    return sorted(actual, key=lambda item: item["key"])


def get_admin_openapi_route_contract_readiness(app: FastAPI | None = None) -> dict[str, Any]:
    """Compare admin route operation metadata with FastAPI's generated OpenAPI schema.

    Static ownership and runtime route checks can still pass if a future change
    accidentally alters OpenAPI metadata. This readiness freezes the OpenAPI
    method/path/operationId/tag layer used by client-generation and API docs.
    """

    expected = sorted(_expected_openapi_operations(), key=lambda item: item["key"])
    actual = _openapi_admin_operations(app) if app is not None else []

    expected_by_key = {item["key"]: item for item in expected}
    actual_by_key = {item["key"]: item for item in actual}
    actual_keys = [item["key"] for item in actual]
    actual_operation_ids = [item.get("operationId") for item in actual if item.get("operationId")]

    missing_operations = [item for item in expected if item["key"] not in actual_by_key]
    unexpected_operations = [item for item in actual if item["key"] not in expected_by_key]
    duplicate_operation_keys = sorted({key for key in actual_keys if actual_keys.count(key) > 1})
    duplicate_operation_ids = sorted({operation_id for operation_id in actual_operation_ids if actual_operation_ids.count(operation_id) > 1})

    operation_checks = []
    for expected_item in expected:
        actual_item = actual_by_key.get(expected_item["key"])
        operation_id = actual_item.get("operationId") if actual_item else None
        tags = actual_item.get("tags") if actual_item else []
        operation_checks.append(
            {
                "key": expected_item["key"],
                "sourcePath": expected_item["sourcePath"],
                "endpoint": expected_item["endpoint"],
                "type": expected_item["type"],
                "owner": expected_item["owner"],
                "expectedOperationId": expected_item["operationId"],
                "actualOperationId": operation_id,
                "operationIdOk": bool(operation_id == expected_item["operationId"]),
                "operationIdEndpointPrefixOk": bool(isinstance(operation_id, str) and operation_id.startswith(expected_item["endpoint"])),
                "tagOk": bool(ADMIN_OPENAPI_ROUTE_CONTRACT["requiredTag"] in tags),
                "responseShapeOk": bool(actual_item and "200" in (actual_item.get("responseCodes") or [])),
            }
        )
    for item in operation_checks:
        item["ok"] = item["operationIdOk"] and item["operationIdEndpointPrefixOk"] and item["tagOk"] and item["responseShapeOk"]

    failed_operation_checks = [item for item in operation_checks if not item["ok"]]
    prefix_checks = [
        {"key": "apiPrefix", "value": ADMIN_OPENAPI_ROUTE_CONTRACT["apiPrefix"], "ok": ADMIN_OPENAPI_ROUTE_CONTRACT["apiPrefix"] == "/api/v1"},
        {"key": "adminPrefix", "value": ADMIN_OPENAPI_ROUTE_CONTRACT["adminPrefix"], "ok": ADMIN_OPENAPI_ROUTE_CONTRACT["adminPrefix"] == "/admin"},
        {"key": "requiredTag", "value": ADMIN_OPENAPI_ROUTE_CONTRACT["requiredTag"], "ok": ADMIN_OPENAPI_ROUTE_CONTRACT["requiredTag"] == "admin"},
    ]
    count_check = {"expected": len(expected), "actual": len(actual), "ok": len(expected) == len(actual)}

    ok = (
        app is not None
        and ADMIN_OPENAPI_ROUTE_CONTRACT["status"] == "openapi-route-metadata-v229"
        and ADMIN_ROUTE_OPERATION_CONTRACT["status"] == "route-operation-metadata-v227"
        and count_check["ok"]
        and not missing_operations
        and not unexpected_operations
        and not duplicate_operation_keys
        and not duplicate_operation_ids
        and not failed_operation_checks
        and all(item["ok"] for item in prefix_checks)
    )

    return {
        "ok": ok,
        "version": ADMIN_OPENAPI_ROUTE_CONTRACT["version"],
        "status": ADMIN_OPENAPI_ROUTE_CONTRACT["status"],
        "policy": ADMIN_OPENAPI_ROUTE_CONTRACT["policy"],
        "contract": ADMIN_OPENAPI_ROUTE_CONTRACT,
        "sourceOperationStatus": ADMIN_ROUTE_OPERATION_CONTRACT["status"],
        "expectedOperationCount": len(expected),
        "actualOperationCount": len(actual),
        "countCheck": count_check,
        "prefixChecks": prefix_checks,
        "operationChecks": operation_checks,
        "expectedOperations": expected,
        "actualOperations": actual,
        "missingOperations": missing_operations,
        "unexpectedOperations": unexpected_operations,
        "duplicateOperationKeys": duplicate_operation_keys,
        "duplicateOperationIds": duplicate_operation_ids,
        "failedOperationChecks": failed_operation_checks,
    }
