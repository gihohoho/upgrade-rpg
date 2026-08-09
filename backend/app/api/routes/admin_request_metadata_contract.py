from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.routes.admin_response_metadata_contract import ADMIN_RESPONSE_METADATA_CONTRACT
from app.api.routes.admin_route_operation_contract import ADMIN_ROUTE_OPERATION_CONTRACT
from app.api.routes.admin_runtime_route_contract import (
    ADMIN_RUNTIME_ROUTE_CONTRACT,
    collect_admin_runtime_route_entries,
)


_BASE_PREFIX = f'{ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]}'
_SCHEMA_RE = re.compile(r"Admin[A-Za-z0-9]+Request")


def _query(name: str, *, alias: str | None = None, required: bool = False, default: Any = None, constraints: list[str] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "alias": alias or name,
        "required": required,
        "default": default,
        "constraints": constraints or [],
    }


def _path(name: str, *, alias: str | None = None) -> dict[str, Any]:
    return {"name": name, "alias": alias or name, "required": True, "default": "PydanticUndefined", "constraints": []}


def _body(model: str, *, required: bool) -> dict[str, Any]:
    return {"name": "payload", "required": required, "model": model}


AUTH_ONLY = ["require_admin_user"]
AUTH_DB = ["require_admin_user", "get_db_session"]
WRITE_AUTH_DB = ["require_admin_write_dev_key", "require_admin_user", "get_db_session"]

DOMAIN_QUERY = [_query("domain", default="itemTemplates", constraints=["MaxLen(max_length=80)"])]
CHANGE_LOG_ID_PATH = [_path("change_log_id")]


ADMIN_REQUEST_METADATA_CONTRACT: dict[str, Any] = {
    "version": "v233.backend-admin-route-request-metadata-contract",
    "status": "route-request-dependency-metadata-v233",
    "policy": "Admin route request parameters, request bodies, and write-guard dependencies must stay aligned with runtime/OpenAPI metadata",
    "apiPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"],
    "adminPrefix": ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"],
    "sourceOperationContract": "backend/app/api/routes/admin_route_operation_contract.py",
    "sourceResponseMetadataContract": "backend/app/api/routes/admin_response_metadata_contract.py",
    "expectedRouteCount": 21,
    "authHeader": "Authorization",
    "writeGuardHeader": "X-Admin-Dev-Key",
    "requests": [
        {"method": "GET", "path": "/requirements", "endpoint": "get_admin_requirements", "dependencies": AUTH_ONLY, "pathParams": [], "queryParams": [], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/overview", "endpoint": "get_admin_readonly_overview", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/save-snapshots", "endpoint": "list_admin_save_snapshots", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [
            _query("limit", default=20, constraints=["Ge(ge=1)", "Le(le=100)"]),
            _query("user_id", alias="userId", default=None, constraints=["Ge(ge=1)"]),
            _query("slot_key", alias="slotKey", default=None, constraints=["MaxLen(max_length=80)"]),
            _query("source", default=None, constraints=["MaxLen(max_length=80)"]),
            _query("default_only", alias="defaultOnly", default=False),
            _query("sort", default="updated_desc", constraints=["MaxLen(max_length=30)"]),
        ], "body": None, "writeGuard": False},
        {"method": "POST", "path": "/change-preview", "endpoint": "preview_admin_change", "dependencies": AUTH_ONLY, "pathParams": [], "queryParams": [], "body": _body("AdminChangePreviewRequest", required=False), "writeGuard": False},
        {"method": "GET", "path": "/master-data/domains", "endpoint": "list_admin_master_catalog_domains", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/master-data/catalog", "endpoint": "list_admin_master_catalog_rows", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [
            *DOMAIN_QUERY,
            _query("limit", default=20, constraints=["Ge(ge=1)", "Le(le=200)"]),
            _query("page", default=1, constraints=["Ge(ge=1)", "Le(le=100000)"]),
            _query("query", default=None, constraints=["MaxLen(max_length=120)"]),
            _query("enabled", default="all", constraints=["MaxLen(max_length=20)"]),
            _query("sort", default="id_asc", constraints=["MaxLen(max_length=30)"]),
        ], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/master-data/create-blueprint", "endpoint": "get_admin_master_create_blueprint", "dependencies": AUTH_DB, "pathParams": [], "queryParams": DOMAIN_QUERY, "body": None, "writeGuard": False},
        {"method": "POST", "path": "/master-data/create-preview", "endpoint": "preview_admin_master_data_create", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [], "body": _body("AdminMasterDataCreatePreviewRequest", required=True), "writeGuard": False},
        {"method": "POST", "path": "/master-data/create-apply", "endpoint": "apply_admin_master_data_create", "dependencies": WRITE_AUTH_DB, "pathParams": [], "queryParams": [], "body": _body("AdminMasterDataCreateApplyRequest", required=True), "writeGuard": True},
        {"method": "GET", "path": "/master-data/detail", "endpoint": "get_admin_master_catalog_detail", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [*DOMAIN_QUERY, _query("id", required=True, default="PydanticUndefined", constraints=["Ge(ge=1)"])], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/master-data/relations", "endpoint": "get_admin_master_catalog_relations", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [*DOMAIN_QUERY, _query("id", required=True, default="PydanticUndefined", constraints=["Ge(ge=1)"]), _query("limit", default=20, constraints=["Ge(ge=1)", "Le(le=80)"])], "body": None, "writeGuard": False},
        {"method": "POST", "path": "/master-data/edit-preview", "endpoint": "preview_admin_master_data_edit", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [], "body": _body("AdminMasterDataEditPreviewRequest", required=True), "writeGuard": False},
        {"method": "POST", "path": "/master-data/edit-apply", "endpoint": "apply_admin_master_data_edit", "dependencies": WRITE_AUTH_DB, "pathParams": [], "queryParams": [], "body": _body("AdminMasterDataEditApplyRequest", required=True), "writeGuard": True},
        {"method": "GET", "path": "/change-logs", "endpoint": "list_admin_change_logs", "dependencies": AUTH_DB, "pathParams": [], "queryParams": [
            _query("limit", default=20, constraints=["Ge(ge=1)", "Le(le=100)"]),
            _query("target_type", alias="targetType", default=None, constraints=["MaxLen(max_length=120)"]),
            _query("target_id", alias="targetId", default=None, constraints=["MaxLen(max_length=160)"]),
            _query("action", default=None, constraints=["MaxLen(max_length=80)"]),
            _query("changed_key", alias="changedKey", default=None, constraints=["MaxLen(max_length=120)"]),
            _query("applied", default=None),
            _query("sort", default="created_desc", constraints=["MaxLen(max_length=40)"]),
        ], "body": None, "writeGuard": False},
        {"method": "GET", "path": "/change-logs/{change_log_id}", "endpoint": "get_admin_change_log_detail", "dependencies": AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": None, "writeGuard": False},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-preview", "endpoint": "preview_admin_create_delete_rollback", "dependencies": AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminCreateDeletePreviewRequest", required=False), "writeGuard": False},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-apply", "endpoint": "apply_admin_create_delete_rollback", "dependencies": WRITE_AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminCreateDeleteApplyRequest", required=True), "writeGuard": True},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-preview", "endpoint": "preview_admin_create_delete_restore", "dependencies": AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminCreateDeleteRestorePreviewRequest", required=False), "writeGuard": False},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-apply", "endpoint": "apply_admin_create_delete_restore", "dependencies": WRITE_AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminCreateDeleteRestoreApplyRequest", required=True), "writeGuard": True},
        {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-preview", "endpoint": "preview_admin_change_log_rollback", "dependencies": AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminChangeLogRollbackPreviewRequest", required=False), "writeGuard": False},
        {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-apply", "endpoint": "apply_admin_change_log_rollback", "dependencies": WRITE_AUTH_DB, "pathParams": CHANGE_LOG_ID_PATH, "queryParams": [], "body": _body("AdminChangeLogRollbackApplyRequest", required=True), "writeGuard": True},
    ],
}


def _route_key(method: str, path: str) -> str:
    return f"{method.upper()} {_BASE_PREFIX}{path}"


def _source_route_path(full_path: str) -> str:
    return full_path[len(_BASE_PREFIX):] if full_path.startswith(_BASE_PREFIX) else full_path


def _default_value(value: Any) -> Any:
    if repr(value) == "PydanticUndefined" or value.__class__.__name__ == "PydanticUndefinedType":
        return "PydanticUndefined"
    return value


def _constraints(field_info: Any) -> list[str]:
    return [repr(item) for item in (getattr(field_info, "metadata", []) or [])]


def _field_info(param: Any) -> Any:
    return getattr(param, "field_info", None)


def _field_name(param: Any) -> str:
    field_info = _field_info(param)
    return str(
        getattr(param, "name", None)
        or getattr(param, "alias", None)
        or getattr(field_info, "alias", None)
        or ""
    )


def _field_alias(param: Any) -> str:
    field_info = _field_info(param)
    name = _field_name(param)
    return str(getattr(field_info, "alias", None) or getattr(param, "alias", None) or name)


def _field_default(param: Any) -> Any:
    field_info = _field_info(param)
    if hasattr(param, "default"):
        return getattr(param, "default")
    if hasattr(field_info, "default"):
        return getattr(field_info, "default")
    return None


def _field_required(param: Any) -> bool:
    """Return required metadata across FastAPI/Pydantic compatibility layers.

    FastAPI can expose params as Pydantic v1 ``ModelField`` objects, Pydantic
    v2 compatibility ``ModelField`` objects, or thin wrapper objects depending
    on the installed versions. Some expose ``.required`` while newer wrappers
    expose ``.is_required()`` only. The contract must read both shapes.
    """

    required = getattr(param, "required", None)
    if required is not None:
        return bool(required)

    is_required = getattr(param, "is_required", None)
    if callable(is_required):
        return bool(is_required())

    field_info = _field_info(param)
    field_info_required = getattr(field_info, "is_required", None)
    if callable(field_info_required):
        return bool(field_info_required())

    return _default_value(_field_default(param)) == "PydanticUndefined"


def _field_annotation(param: Any) -> str:
    field_info = _field_info(param)
    annotation = (
        getattr(field_info, "annotation", None)
        or getattr(param, "annotation", None)
        or getattr(param, "type_", None)
        or getattr(param, "outer_type_", None)
        or ""
    )
    return str(annotation)


def _param_metadata(param: Any) -> dict[str, Any]:
    field_info = _field_info(param)
    return {
        "name": _field_name(param),
        "alias": _field_alias(param),
        "required": _field_required(param),
        "default": _default_value(_field_default(param)),
        "constraints": _constraints(field_info),
    }


def _body_metadata(param: Any) -> dict[str, Any]:
    annotation = _field_annotation(param)
    models = _SCHEMA_RE.findall(annotation)
    return {
        "name": _field_name(param),
        "required": _field_required(param),
        "model": models[0] if models else annotation,
    }



def _runtime_request_routes(app: FastAPI) -> list[dict[str, Any]]:
    # Reuse the runtime route collector so request metadata checks see the same
    # app/api_router/owner-router fallback chain as v225 runtime registration.
    entries, _source = collect_admin_runtime_route_entries(app)
    routes: list[dict[str, Any]] = []
    for entry in entries:
        route = entry.get("route")
        dependant = getattr(route, "dependant", None)
        if dependant is None:
            continue
        dependency_calls = [getattr(dep.call, "__name__", repr(dep.call)) for dep in dependant.dependencies]
        path_params = [_param_metadata(param) for param in dependant.path_params]
        query_params = [_param_metadata(param) for param in dependant.query_params]
        body_params = [_body_metadata(param) for param in dependant.body_params]
        routes.append(
            {
                "key": entry["key"],
                "method": entry["method"],
                "path": entry["path"],
                "sourcePath": _source_route_path(entry["path"]),
                "endpoint": entry.get("endpoint") or getattr(getattr(route, "endpoint", None), "__name__", None),
                "dependencies": dependency_calls,
                "pathParams": path_params,
                "queryParams": query_params,
                "body": body_params[0] if body_params else None,
                "bodyParamCount": len(body_params),
                "writeGuard": "require_admin_write_dev_key" in dependency_calls,
            }
        )
    return sorted(routes, key=lambda item: item["key"])


def _schema_ref_name(schema: dict[str, Any]) -> str | None:
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", 1)[-1]
    for item in schema.get("anyOf", []) or []:
        if "$ref" in item:
            return str(item["$ref"]).rsplit("/", 1)[-1]
    return None


def _openapi_request_routes(app: FastAPI) -> list[dict[str, Any]]:
    schema = app.openapi()
    routes: list[dict[str, Any]] = []
    for path, methods in schema.get("paths", {}).items():
        if not isinstance(path, str) or not path.startswith(_BASE_PREFIX):
            continue
        for method, operation in methods.items():
            method_upper = method.upper()
            if method_upper in {"HEAD", "OPTIONS"}:
                continue
            parameters = operation.get("parameters", []) or []
            route_parameters = [
                {"name": param.get("name"), "in": param.get("in"), "required": bool(param.get("required", False))}
                for param in parameters
            ]
            request_body = operation.get("requestBody")
            body = None
            if request_body:
                content = request_body.get("content", {}).get("application/json", {})
                body = {
                    "required": bool(request_body.get("required", False)),
                    "model": _schema_ref_name(content.get("schema", {}) or {}),
                }
            routes.append(
                {
                    "key": f"{method_upper} {path}",
                    "method": method_upper,
                    "path": path,
                    "sourcePath": _source_route_path(path),
                    "parameters": route_parameters,
                    "queryParameterNames": [param["name"] for param in route_parameters if param["in"] == "query"],
                    "pathParameterNames": [param["name"] for param in route_parameters if param["in"] == "path"],
                    "headerParameterNames": [param["name"] for param in route_parameters if param["in"] == "header"],
                    "body": body,
                }
            )
    return sorted(routes, key=lambda item: item["key"])


def _read_owner_sources(root: Path | None) -> dict[str, str]:
    if root is None:
        return {}
    files = sorted({item["ownerFile"] for item in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]})
    return {file: (root / file).read_text(encoding="utf-8") if (root / file).exists() else "" for file in files}


def _source_write_guard_checks(root: Path | None, expected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = _read_owner_sources(root)
    operations_by_key = {f'{item["method"]} {item["path"]}': item for item in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]}
    checks: list[dict[str, Any]] = []
    for item in expected:
        operation = operations_by_key.get(f'{item["method"]} {item["path"]}', {})
        source = sources.get(operation.get("ownerFile", ""), "")
        block_pattern = re.compile(rf'@router\.{item["method"].lower()}\("{re.escape(item["path"])}"\)[\s\S]*?(?=\n@router\.(?:get|post)\("|\Z)')
        match = block_pattern.search(source)
        block = match.group(0) if match else ""
        has_write_guard = "ADMIN_WRITE_GUARD_DEP" in block and "_write_guard" in block
        checks.append(
            {
                "key": _route_key(item["method"], item["path"]),
                "ownerFile": operation.get("ownerFile"),
                "expectedWriteGuard": item["writeGuard"],
                "sourceBlockFound": bool(block),
                "sourceHasWriteGuard": has_write_guard,
                "ok": bool(block) and has_write_guard == item["writeGuard"],
            }
        )
    return checks


def get_admin_request_metadata_contract_readiness(
    app: FastAPI | None = None,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Return a runtime/OpenAPI request/dependency metadata readiness report.

    This contract guards the request side of the admin routes: query/path/body
    metadata, auth/session dependencies, and the temporary write-dev-key guard.
    It complements v231 response metadata without changing route paths or schemas.
    """

    root_path = Path(root) if root is not None else None
    expected = list(ADMIN_REQUEST_METADATA_CONTRACT["requests"])
    expected_by_key = {_route_key(item["method"], item["path"]): item for item in expected}
    operation_by_key = {_route_key(item["method"], item["path"]): item for item in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]}

    runtime_routes = _runtime_request_routes(app) if app is not None else []
    openapi_routes = _openapi_request_routes(app) if app is not None else []
    runtime_by_key = {item["key"]: item for item in runtime_routes}
    openapi_by_key = {item["key"]: item for item in openapi_routes}

    operation_checks = []
    runtime_checks = []
    openapi_checks = []
    for key, expected_item in expected_by_key.items():
        operation_item = operation_by_key.get(key)
        runtime_item = runtime_by_key.get(key)
        openapi_item = openapi_by_key.get(key)
        expected_query_aliases = [param["alias"] for param in expected_item["queryParams"]]
        expected_path_aliases = [param["alias"] for param in expected_item["pathParams"]]
        expected_header_names = (
            [ADMIN_REQUEST_METADATA_CONTRACT["writeGuardHeader"]]
            if expected_item["writeGuard"]
            else []
        ) + [ADMIN_REQUEST_METADATA_CONTRACT["authHeader"]]
        expected_body = expected_item["body"]
        operation_checks.append(
            {
                "key": key,
                "expectedEndpoint": expected_item["endpoint"],
                "operationEndpoint": operation_item.get("endpoint") if operation_item else None,
                "ok": bool(operation_item and operation_item.get("endpoint") == expected_item["endpoint"]),
            }
        )
        runtime_checks.append(
            {
                "key": key,
                "endpointOk": bool(runtime_item and runtime_item.get("endpoint") == expected_item["endpoint"]),
                "dependenciesOk": bool(runtime_item and runtime_item.get("dependencies") == expected_item["dependencies"]),
                "pathParamsOk": bool(runtime_item and runtime_item.get("pathParams") == expected_item["pathParams"]),
                "queryParamsOk": bool(runtime_item and runtime_item.get("queryParams") == expected_item["queryParams"]),
                "bodyOk": bool(runtime_item and runtime_item.get("body") == expected_body and runtime_item.get("bodyParamCount") == (1 if expected_body else 0)),
                "writeGuardOk": bool(runtime_item and runtime_item.get("writeGuard") == expected_item["writeGuard"]),
                "expected": expected_item,
                "actual": runtime_item,
            }
        )
        openapi_checks.append(
            {
                "key": key,
                "queryParameterNamesOk": bool(openapi_item and openapi_item.get("queryParameterNames") == expected_query_aliases),
                "pathParameterNamesOk": bool(openapi_item and openapi_item.get("pathParameterNames") == expected_path_aliases),
                "headerParameterNamesOk": bool(openapi_item and openapi_item.get("headerParameterNames") == expected_header_names),
                "bodyOk": bool(openapi_item and openapi_item.get("body") == ({"required": expected_body["required"], "model": expected_body["model"]} if expected_body else None)),
                "expectedQueryParameterNames": expected_query_aliases,
                "expectedPathParameterNames": expected_path_aliases,
                "expectedHeaderParameterNames": expected_header_names,
                "expectedBody": {"required": expected_body["required"], "model": expected_body["model"]} if expected_body else None,
                "actual": openapi_item,
            }
        )

    for check in runtime_checks:
        check["ok"] = check["endpointOk"] and check["dependenciesOk"] and check["pathParamsOk"] and check["queryParamsOk"] and check["bodyOk"] and check["writeGuardOk"]
    for check in openapi_checks:
        check["ok"] = check["queryParameterNamesOk"] and check["pathParameterNamesOk"] and check["headerParameterNamesOk"] and check["bodyOk"]

    source_write_guard_checks = _source_write_guard_checks(root_path, expected)
    missing_runtime_routes = [item for key, item in expected_by_key.items() if key not in runtime_by_key]
    unexpected_runtime_routes = [item for item in runtime_routes if item["key"] not in expected_by_key]
    missing_openapi_routes = [item for key, item in expected_by_key.items() if key not in openapi_by_key]
    unexpected_openapi_routes = [item for item in openapi_routes if item["key"] not in expected_by_key]
    failed_operation_checks = [item for item in operation_checks if not item["ok"]]
    failed_runtime_checks = [item for item in runtime_checks if not item["ok"]]
    failed_openapi_checks = [item for item in openapi_checks if not item["ok"]]
    failed_source_write_guard_checks = [item for item in source_write_guard_checks if not item["ok"]]
    write_guard_routes = [item for item in expected if item["writeGuard"]]
    request_body_routes = [item for item in expected if item["body"]]

    count_check = {
        "expected": len(expected),
        "runtime": len(runtime_routes),
        "openapi": len(openapi_routes),
        "ok": len(expected) == len(runtime_routes) == len(openapi_routes) == ADMIN_REQUEST_METADATA_CONTRACT["expectedRouteCount"],
    }

    ok = (
        app is not None
        and ADMIN_REQUEST_METADATA_CONTRACT["status"] == "route-request-dependency-metadata-v233"
        and ADMIN_RESPONSE_METADATA_CONTRACT["status"] == "route-response-metadata-v231"
        and ADMIN_ROUTE_OPERATION_CONTRACT["status"] == "route-operation-metadata-v227"
        and count_check["ok"]
        and not missing_runtime_routes
        and not unexpected_runtime_routes
        and not missing_openapi_routes
        and not unexpected_openapi_routes
        and not failed_operation_checks
        and not failed_runtime_checks
        and not failed_openapi_checks
        and not failed_source_write_guard_checks
    )

    return {
        "ok": ok,
        "version": ADMIN_REQUEST_METADATA_CONTRACT["version"],
        "status": ADMIN_REQUEST_METADATA_CONTRACT["status"],
        "policy": ADMIN_REQUEST_METADATA_CONTRACT["policy"],
        "contract": ADMIN_REQUEST_METADATA_CONTRACT,
        "sourceResponseMetadataStatus": ADMIN_RESPONSE_METADATA_CONTRACT["status"],
        "sourceOperationStatus": ADMIN_ROUTE_OPERATION_CONTRACT["status"],
        "expectedRouteCount": len(expected),
        "runtimeRouteCount": len(runtime_routes),
        "openApiRouteCount": len(openapi_routes),
        "writeGuardRouteCount": len(write_guard_routes),
        "requestBodyRouteCount": len(request_body_routes),
        "countCheck": count_check,
        "operationChecks": operation_checks,
        "runtimeChecks": runtime_checks,
        "openApiChecks": openapi_checks,
        "sourceWriteGuardChecks": source_write_guard_checks,
        "missingRuntimeRoutes": missing_runtime_routes,
        "unexpectedRuntimeRoutes": unexpected_runtime_routes,
        "missingOpenApiRoutes": missing_openapi_routes,
        "unexpectedOpenApiRoutes": unexpected_openapi_routes,
        "failedOperationChecks": failed_operation_checks,
        "failedRuntimeChecks": failed_runtime_checks,
        "failedOpenApiChecks": failed_openapi_checks,
        "failedSourceWriteGuardChecks": failed_source_write_guard_checks,
    }
