from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.api.routes.admin_openapi_route_contract import (
    ADMIN_OPENAPI_ROUTE_CONTRACT,
    _expected_openapi_operations,
    _openapi_admin_operations,
)
from app.api.routes.admin_route_operation_contract import ADMIN_ROUTE_OPERATION_CONTRACT
from app.api.routes.admin_runtime_route_contract import (
    ADMIN_RUNTIME_ROUTE_CONTRACT,
    _runtime_admin_routes,
)


ADMIN_RESPONSE_METADATA_CONTRACT: dict[str, Any] = {
    "version": "v231.backend-admin-route-response-metadata-contract",
    "status": "route-response-metadata-v231",
    "policy": "Admin route response status/model/OpenAPI response-code metadata must stay stable while route modules are refactored",
    "apiPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"],
    "adminPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"],
    "sourceOperationContract": "backend/app/api/routes/admin_route_operation_contract.py",
    "sourceOpenApiContract": "backend/app/api/routes/admin_openapi_route_contract.py",
    "expectedRouteCount": 21,
    "defaultStatusCode": 200,
    "explicitResponseModel": None,
    "requiredSuccessResponseCode": "200",
    "validationResponseCode": "422",
    "noValidationResponsePaths": [
        "/requirements",
        "/overview",
        "/master-data/domains",
    ],
    "forbiddenRouteDecoratorOptions": [
        "response_model=",
        "status_code=",
        "responses=",
        "summary=",
        "operation_id=",
    ],
}


def _full_admin_path(path: str) -> str:
    return f'{ADMIN_RESPONSE_METADATA_CONTRACT["apiPrefix"]}{ADMIN_RESPONSE_METADATA_CONTRACT["adminPrefix"]}{path}'


def _operation_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def _expected_summary(endpoint: str) -> str:
    # Mirrors FastAPI's default summary generated from a path operation function name.
    return endpoint.replace("_", " ").title()


def _expected_response_codes(source_path: str) -> list[str]:
    codes = [ADMIN_RESPONSE_METADATA_CONTRACT["requiredSuccessResponseCode"]]
    if source_path not in ADMIN_RESPONSE_METADATA_CONTRACT["noValidationResponsePaths"]:
        codes.append(ADMIN_RESPONSE_METADATA_CONTRACT["validationResponseCode"])
    return codes


def _runtime_admin_route_metadata(app: FastAPI) -> list[dict[str, Any]]:
    base = f'{ADMIN_RESPONSE_METADATA_CONTRACT["apiPrefix"]}{ADMIN_RESPONSE_METADATA_CONTRACT["adminPrefix"]}'
    metadata: list[dict[str, Any]] = []
    ignored_methods = {"HEAD", "OPTIONS"}
    for route in app.routes:
        path = getattr(route, "path", "")
        if not isinstance(path, str) or not path.startswith(base):
            continue
        methods = sorted((getattr(route, "methods", set()) or set()) - ignored_methods)
        for method in methods:
            metadata.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "key": _operation_key(method, path),
                    "endpoint": getattr(getattr(route, "endpoint", None), "__name__", None),
                    "name": getattr(route, "name", None),
                    "statusCode": getattr(route, "status_code", None),
                    "responseModel": getattr(route, "response_model", None),
                    "responseDescription": getattr(route, "response_description", None),
                    "includeInSchema": getattr(route, "include_in_schema", None),
                }
            )
    return sorted(metadata, key=lambda item: item["key"])


def _openapi_admin_response_metadata(app: FastAPI) -> list[dict[str, Any]]:
    schema = app.openapi()
    paths = schema.get("paths", {}) if isinstance(schema, dict) else {}
    base = f'{ADMIN_RESPONSE_METADATA_CONTRACT["apiPrefix"]}{ADMIN_RESPONSE_METADATA_CONTRACT["adminPrefix"]}'
    metadata: list[dict[str, Any]] = []
    for path, method_map in paths.items():
        if not isinstance(path, str) or not path.startswith(base):
            continue
        if not isinstance(method_map, dict):
            continue
        for method, meta in method_map.items():
            if not isinstance(meta, dict):
                continue
            method_upper = method.upper()
            responses = meta.get("responses") or {}
            response_codes = sorted(str(code) for code in responses.keys())
            metadata.append(
                {
                    "method": method_upper,
                    "path": path,
                    "key": _operation_key(method_upper, path),
                    "operationId": meta.get("operationId"),
                    "summary": meta.get("summary"),
                    "responseCodes": response_codes,
                    "successDescription": (responses.get("200") or {}).get("description"),
                    "validationDescription": (responses.get("422") or {}).get("description"),
                }
            )
    return sorted(metadata, key=lambda item: item["key"])


def get_admin_response_metadata_contract_readiness(app: FastAPI | None = None) -> dict[str, Any]:
    """Freeze response metadata for admin routes without changing the response body.

    The existing admin endpoints intentionally return the shared game API envelope
    through admin_ok_response() without per-route response_model/status_code
    options. This contract catches accidental decorator/OpenAPI drift during later
    router cleanup while keeping all public route paths and payload shapes stable.
    """

    expected_operations = sorted(_expected_openapi_operations(), key=lambda item: item["key"])
    runtime_routes = _runtime_admin_route_metadata(app) if app is not None else []
    openapi_routes = _openapi_admin_response_metadata(app) if app is not None else []

    expected_by_key = {item["key"]: item for item in expected_operations}
    runtime_by_key = {item["key"]: item for item in runtime_routes}
    openapi_by_key = {item["key"]: item for item in openapi_routes}

    runtime_checks: list[dict[str, Any]] = []
    openapi_checks: list[dict[str, Any]] = []
    for expected in expected_operations:
        key = expected["key"]
        runtime_item = runtime_by_key.get(key)
        openapi_item = openapi_by_key.get(key)
        source_path = expected["sourcePath"]
        expected_codes = _expected_response_codes(source_path)
        expected_summary = _expected_summary(expected["endpoint"])
        runtime_checks.append(
            {
                "key": key,
                "endpoint": expected["endpoint"],
                "runtimeStatusCode": runtime_item.get("statusCode") if runtime_item else None,
                "runtimeResponseModel": repr(runtime_item.get("responseModel")) if runtime_item else None,
                "includeInSchema": runtime_item.get("includeInSchema") if runtime_item else None,
                "statusCodeDefaultOk": bool(runtime_item and runtime_item.get("statusCode") is None),
                "responseModelDefaultOk": bool(runtime_item and runtime_item.get("responseModel") is None),
                "includeInSchemaOk": bool(runtime_item and runtime_item.get("includeInSchema") is True),
            }
        )
        openapi_checks.append(
            {
                "key": key,
                "endpoint": expected["endpoint"],
                "expectedSummary": expected_summary,
                "actualSummary": openapi_item.get("summary") if openapi_item else None,
                "expectedResponseCodes": expected_codes,
                "actualResponseCodes": openapi_item.get("responseCodes") if openapi_item else [],
                "summaryOk": bool(openapi_item and openapi_item.get("summary") == expected_summary),
                "responseCodesOk": bool(openapi_item and openapi_item.get("responseCodes") == expected_codes),
                "successDescriptionOk": bool(openapi_item and openapi_item.get("successDescription") == "Successful Response"),
                "validationDescriptionOk": bool(
                    source_path in ADMIN_RESPONSE_METADATA_CONTRACT["noValidationResponsePaths"]
                    or (openapi_item and openapi_item.get("validationDescription") == "Validation Error")
                ),
            }
        )
    for check in runtime_checks:
        check["ok"] = check["statusCodeDefaultOk"] and check["responseModelDefaultOk"] and check["includeInSchemaOk"]
    for check in openapi_checks:
        check["ok"] = check["summaryOk"] and check["responseCodesOk"] and check["successDescriptionOk"] and check["validationDescriptionOk"]

    missing_runtime_routes = [item for item in expected_operations if item["key"] not in runtime_by_key]
    unexpected_runtime_routes = [item for item in runtime_routes if item["key"] not in expected_by_key]
    missing_openapi_routes = [item for item in expected_operations if item["key"] not in openapi_by_key]
    unexpected_openapi_routes = [item for item in openapi_routes if item["key"] not in expected_by_key]
    failed_runtime_checks = [item for item in runtime_checks if not item["ok"]]
    failed_openapi_checks = [item for item in openapi_checks if not item["ok"]]
    count_check = {
        "expected": len(expected_operations),
        "runtime": len(runtime_routes),
        "openapi": len(openapi_routes),
        "ok": len(expected_operations) == len(runtime_routes) == len(openapi_routes) == ADMIN_RESPONSE_METADATA_CONTRACT["expectedRouteCount"],
    }

    ok = (
        app is not None
        and ADMIN_RESPONSE_METADATA_CONTRACT["status"] == "route-response-metadata-v231"
        and ADMIN_OPENAPI_ROUTE_CONTRACT["status"] == "openapi-route-metadata-v229"
        and ADMIN_ROUTE_OPERATION_CONTRACT["status"] == "route-operation-metadata-v227"
        and count_check["ok"]
        and not missing_runtime_routes
        and not unexpected_runtime_routes
        and not missing_openapi_routes
        and not unexpected_openapi_routes
        and not failed_runtime_checks
        and not failed_openapi_checks
    )

    return {
        "ok": ok,
        "version": ADMIN_RESPONSE_METADATA_CONTRACT["version"],
        "status": ADMIN_RESPONSE_METADATA_CONTRACT["status"],
        "policy": ADMIN_RESPONSE_METADATA_CONTRACT["policy"],
        "contract": ADMIN_RESPONSE_METADATA_CONTRACT,
        "sourceOpenApiStatus": ADMIN_OPENAPI_ROUTE_CONTRACT["status"],
        "sourceOperationStatus": ADMIN_ROUTE_OPERATION_CONTRACT["status"],
        "expectedRouteCount": len(expected_operations),
        "runtimeRouteCount": len(runtime_routes),
        "openApiRouteCount": len(openapi_routes),
        "countCheck": count_check,
        "runtimeChecks": runtime_checks,
        "openApiChecks": openapi_checks,
        "missingRuntimeRoutes": missing_runtime_routes,
        "unexpectedRuntimeRoutes": unexpected_runtime_routes,
        "missingOpenApiRoutes": missing_openapi_routes,
        "unexpectedOpenApiRoutes": unexpected_openapi_routes,
        "failedRuntimeChecks": failed_runtime_checks,
        "failedOpenApiChecks": failed_openapi_checks,
    }
