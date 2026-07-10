from __future__ import annotations

from typing import Any, get_args, get_origin

from fastapi import FastAPI
from pydantic import BaseModel

from app.api.routes.admin_request_metadata_contract import ADMIN_REQUEST_METADATA_CONTRACT
from app.api.routes.admin_runtime_route_contract import (
    ADMIN_RUNTIME_ROUTE_CONTRACT,
    collect_admin_runtime_route_entries,
)
from app.schemas import admin as admin_schemas


ADMIN_SCHEMA_MODEL_CONTRACT: dict[str, Any] = {
    "version": "v235.backend-admin-schema-model-contract",
    "status": "admin-schema-model-metadata-v235",
    "policy": "Admin request schema classes, route body models, OpenAPI component schemas, aliases, and guarded fields must not drift",
    "schemaModule": "backend/app/schemas/admin.py",
    "expectedSchemaCount": 11,
    "allowedUnexposedSchemaClasses": ["AdminChangeApplyRequest"],
    "expectedSchemas": [
        "AdminChangePreviewRequest",
        "AdminMasterDataCreatePreviewRequest",
        "AdminMasterDataCreateApplyRequest",
        "AdminMasterDataEditPreviewRequest",
        "AdminMasterDataEditApplyRequest",
        "AdminChangeLogRollbackPreviewRequest",
        "AdminChangeLogRollbackApplyRequest",
        "AdminCreateDeletePreviewRequest",
        "AdminCreateDeleteApplyRequest",
        "AdminCreateDeleteRestorePreviewRequest",
        "AdminCreateDeleteRestoreApplyRequest",
    ],
    "guardedApplySchemas": [
        "AdminMasterDataCreateApplyRequest",
        "AdminMasterDataEditApplyRequest",
        "AdminChangeLogRollbackApplyRequest",
        "AdminCreateDeleteApplyRequest",
        "AdminCreateDeleteRestoreApplyRequest",
    ],
    "requiredGuardedAliases": ["confirmText", "reason"],
}


def _admin_routes(app: FastAPI) -> dict[tuple[str, str], Any]:
    """Return concrete admin routes using the shared runtime collector.

    Windows/FastAPI/Pydantic combinations can expose assembled routes through
    different internal containers. The schema/model contract must not use its
    own ``app.routes`` scan; it should reuse the same collector that runtime,
    operation, response metadata, and request metadata contracts use.
    """

    api_prefix = ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]
    admin_prefix = ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]
    prefix = f"{api_prefix}{admin_prefix}"
    result: dict[tuple[str, str], Any] = {}
    entries, _source = collect_admin_runtime_route_entries(app)
    for entry in entries:
        path = entry.get("path", "")
        method = str(entry.get("method", "")).upper()
        route = entry.get("route")
        if not isinstance(path, str) or not path.startswith(prefix) or not method or route is None:
            continue
        relative_path = path[len(prefix):] or "/"
        result[(method, relative_path)] = route
    return result


def _model_name_from_annotation(annotation: Any) -> str | None:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation.__name__
    for arg in get_args(annotation):
        name = _model_name_from_annotation(arg)
        if name is not None:
            return name
    return None


def _runtime_body_model_name(route: Any) -> str | None:
    body_field = getattr(route, "body_field", None)
    if body_field is None:
        return None
    return _model_name_from_annotation(body_field.field_info.annotation)


def _schema_class_names() -> list[str]:
    names: list[str] = []
    for name, value in vars(admin_schemas).items():
        if name.startswith("Admin") and name.endswith("Request") and isinstance(value, type) and issubclass(value, BaseModel):
            names.append(name)
    return sorted(names)


def _openapi_admin_schema_names(app: FastAPI) -> list[str]:
    schemas = app.openapi().get("components", {}).get("schemas", {})
    return sorted(name for name in schemas if name.startswith("Admin") and name.endswith("Request"))


def _schema_field_aliases(model_name: str) -> list[str]:
    model = getattr(admin_schemas, model_name)
    return sorted(field.alias or field_name for field_name, field in model.model_fields.items())


def get_admin_schema_model_contract_readiness(app: FastAPI) -> dict[str, Any]:
    contract = ADMIN_SCHEMA_MODEL_CONTRACT
    expected_names = sorted(contract["expectedSchemas"])
    class_names = _schema_class_names()
    openapi_names = _openapi_admin_schema_names(app)
    routes = _admin_routes(app)

    route_body_checks: list[dict[str, Any]] = []
    for request in ADMIN_REQUEST_METADATA_CONTRACT["requests"]:
        expected_body = request.get("body")
        if expected_body is None:
            continue
        key = (request["method"], request["path"])
        route = routes.get(key)
        actual_model = _runtime_body_model_name(route) if route is not None else None
        expected_model = expected_body["model"]
        route_body_checks.append({
            "method": key[0],
            "path": key[1],
            "expectedModel": expected_model,
            "actualModel": actual_model,
            "ok": actual_model == expected_model,
        })

    openapi_schemas = app.openapi().get("components", {}).get("schemas", {})
    schema_checks: list[dict[str, Any]] = []
    for model_name in expected_names:
        model = getattr(admin_schemas, model_name, None)
        component = openapi_schemas.get(model_name, {})
        expected_aliases = _schema_field_aliases(model_name) if model is not None else []
        actual_aliases = sorted(component.get("properties", {}).keys())
        schema_checks.append({
            "model": model_name,
            "classExists": model is not None,
            "openApiExists": bool(component),
            "expectedAliases": expected_aliases,
            "actualAliases": actual_aliases,
            "aliasesOk": expected_aliases == actual_aliases,
            "ok": model is not None and bool(component) and expected_aliases == actual_aliases,
        })

    guarded_field_checks: list[dict[str, Any]] = []
    for model_name in contract["guardedApplySchemas"]:
        model = getattr(admin_schemas, model_name)
        aliases = _schema_field_aliases(model_name)
        component_properties = openapi_schemas.get(model_name, {}).get("properties", {})
        confirm_field = model.model_fields.get("confirm_text")
        reason_field = model.model_fields.get("reason")
        guarded_field_checks.append({
            "model": model_name,
            "confirmTextModelOk": bool(confirm_field and confirm_field.alias == "confirmText"),
            "reasonModelOk": reason_field is not None,
            "confirmTextOpenApiOk": "confirmText" in component_properties,
            "reasonOpenApiOk": "reason" in component_properties,
            "aliases": aliases,
            "ok": bool(confirm_field and confirm_field.alias == "confirmText")
                and reason_field is not None
                and "confirmText" in component_properties
                and "reason" in component_properties,
        })

    missing_classes = sorted(set(expected_names) - set(class_names))
    allowed_unexposed = set(contract["allowedUnexposedSchemaClasses"])
    unexpected_classes = sorted(set(class_names) - set(expected_names) - allowed_unexposed)
    missing_openapi = sorted(set(expected_names) - set(openapi_names))
    unexpected_openapi = sorted(set(openapi_names) - set(expected_names))
    failed_route_bodies = [item for item in route_body_checks if not item["ok"]]
    failed_schemas = [item for item in schema_checks if not item["ok"]]
    failed_guarded_fields = [item for item in guarded_field_checks if not item["ok"]]

    ok = not any((missing_classes, unexpected_classes, missing_openapi, unexpected_openapi, failed_route_bodies, failed_schemas, failed_guarded_fields))
    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "expectedSchemaCount": contract["expectedSchemaCount"],
        "classSchemaCount": len(class_names),
        "openApiSchemaCount": len(openapi_names),
        "routeBodyCount": len(route_body_checks),
        "guardedApplySchemaCount": len(guarded_field_checks),
        "classSchemaNames": class_names,
        "openApiSchemaNames": openapi_names,
        "missingClasses": missing_classes,
        "unexpectedClasses": unexpected_classes,
        "missingOpenApiSchemas": missing_openapi,
        "unexpectedOpenApiSchemas": unexpected_openapi,
        "routeBodyChecks": route_body_checks,
        "failedRouteBodyChecks": failed_route_bodies,
        "schemaChecks": schema_checks,
        "failedSchemaChecks": failed_schemas,
        "guardedFieldChecks": guarded_field_checks,
        "failedGuardedFieldChecks": failed_guarded_fields,
    }
