from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import ValidationError

from app.schemas import admin as admin_schemas


ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT: dict[str, Any] = {
    "version": "v237.backend-admin-schema-field-constraint-contract",
    "status": "admin-schema-field-constraints-v237",
    "policy": "Admin request required fields, defaults, length/range constraints, aliases, and model normalization settings must not drift",
    "configuredModels": [
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
    "expectedRequired": {
        "AdminChangePreviewRequest": ["target_type", "target_id"],
        "AdminMasterDataCreatePreviewRequest": ["domain"],
        "AdminMasterDataCreateApplyRequest": ["domain"],
        "AdminMasterDataEditPreviewRequest": ["domain", "id"],
        "AdminMasterDataEditApplyRequest": ["domain", "id"],
        "AdminChangeLogRollbackPreviewRequest": [],
        "AdminChangeLogRollbackApplyRequest": [],
        "AdminCreateDeletePreviewRequest": [],
        "AdminCreateDeleteApplyRequest": [],
        "AdminCreateDeleteRestorePreviewRequest": [],
        "AdminCreateDeleteRestoreApplyRequest": [],
    },
    "expectedFieldConstraints": {
        "AdminMasterDataCreatePreviewRequest": {
            "domain": {"type": "string", "minLength": 1, "maxLength": 80},
            "reason": {"nullableType": "string", "maxLength": 500},
            "dryRun": {"type": "boolean", "default": True},
        },
        "AdminMasterDataCreateApplyRequest": {
            "domain": {"type": "string", "minLength": 1, "maxLength": 80},
            "reason": {"nullableType": "string", "maxLength": 500},
            "confirmText": {"type": "string", "maxLength": 80, "default": ""},
            "dryRun": {"type": "boolean", "default": False},
        },
        "AdminMasterDataEditPreviewRequest": {
            "domain": {"type": "string", "minLength": 1, "maxLength": 80},
            "id": {"type": "integer", "minimum": 1.0},
            "reason": {"nullableType": "string", "maxLength": 500},
            "dryRun": {"type": "boolean", "default": True},
        },
        "AdminMasterDataEditApplyRequest": {
            "domain": {"type": "string", "minLength": 1, "maxLength": 80},
            "id": {"type": "integer", "minimum": 1.0},
            "reason": {"nullableType": "string", "maxLength": 500},
            "confirmText": {"type": "string", "maxLength": 80, "default": ""},
            "dryRun": {"type": "boolean", "default": False},
        },
        "AdminChangeLogRollbackPreviewRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "dryRun": {"type": "boolean", "default": True},
        },
        "AdminChangeLogRollbackApplyRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "confirmText": {"type": "string", "maxLength": 80, "default": ""},
            "dryRun": {"type": "boolean", "default": False},
        },
        "AdminCreateDeletePreviewRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "dryRun": {"type": "boolean", "default": True},
        },
        "AdminCreateDeleteApplyRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "confirmText": {"type": "string", "maxLength": 80, "default": ""},
            "dryRun": {"type": "boolean", "default": False},
        },
        "AdminCreateDeleteRestorePreviewRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "dryRun": {"type": "boolean", "default": True},
        },
        "AdminCreateDeleteRestoreApplyRequest": {
            "reason": {"nullableType": "string", "maxLength": 500},
            "confirmText": {"type": "string", "maxLength": 80, "default": ""},
            "dryRun": {"type": "boolean", "default": False},
        },
    },
}


def _property_contract(property_schema: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("type", "minLength", "maxLength", "minimum", "default"):
        if key in property_schema:
            result[key] = property_schema[key]
    any_of = property_schema.get("anyOf", [])
    non_null = next((item for item in any_of if item.get("type") != "null"), None)
    has_null = any(item.get("type") == "null" for item in any_of)
    if non_null is not None and has_null:
        result["nullableType"] = non_null.get("type")
        for key in ("minLength", "maxLength", "minimum"):
            if key in non_null:
                result[key] = non_null[key]
    return result


def _validation_rejects(model: type, payload: dict[str, Any]) -> bool:
    try:
        model.model_validate(payload)
    except ValidationError:
        return True
    return False


def _runtime_behavior_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    create_preview = admin_schemas.AdminMasterDataCreatePreviewRequest.model_validate({"domain": " items "})
    checks.append({"name": "strip-whitespace", "ok": create_preview.domain == "items"})

    create_apply_alias = admin_schemas.AdminMasterDataCreateApplyRequest.model_validate({"domain": "items", "confirmText": " APPLY "})
    create_apply_name = admin_schemas.AdminMasterDataCreateApplyRequest.model_validate({"domain": "items", "confirm_text": " APPLY "})
    checks.append({"name": "populate-by-alias", "ok": create_apply_alias.confirm_text == "APPLY"})
    checks.append({"name": "populate-by-name", "ok": create_apply_name.confirm_text == "APPLY"})
    checks.append({"name": "preview-dry-run-default", "ok": create_preview.dry_run is True})
    checks.append({"name": "apply-dry-run-default", "ok": create_apply_alias.dry_run is False})

    checks.append({"name": "reject-empty-domain", "ok": _validation_rejects(admin_schemas.AdminMasterDataCreatePreviewRequest, {"domain": "   "})})
    checks.append({"name": "reject-long-domain", "ok": _validation_rejects(admin_schemas.AdminMasterDataCreatePreviewRequest, {"domain": "x" * 81})})
    checks.append({"name": "reject-id-below-one", "ok": _validation_rejects(admin_schemas.AdminMasterDataEditPreviewRequest, {"domain": "items", "id": 0})})
    checks.append({"name": "reject-long-reason", "ok": _validation_rejects(admin_schemas.AdminMasterDataCreatePreviewRequest, {"domain": "items", "reason": "x" * 501})})
    checks.append({"name": "reject-long-confirm-text", "ok": _validation_rejects(admin_schemas.AdminMasterDataCreateApplyRequest, {"domain": "items", "confirmText": "x" * 81})})
    return checks


def get_admin_schema_field_constraint_contract_readiness(app: FastAPI) -> dict[str, Any]:
    contract = ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT
    schemas = app.openapi().get("components", {}).get("schemas", {})

    required_checks: list[dict[str, Any]] = []
    for model_name, expected_required in contract["expectedRequired"].items():
        actual_required = schemas.get(model_name, {}).get("required", [])
        required_checks.append({
            "model": model_name,
            "expected": expected_required,
            "actual": actual_required,
            "ok": actual_required == expected_required,
        })

    field_checks: list[dict[str, Any]] = []
    for model_name, expected_fields in contract["expectedFieldConstraints"].items():
        properties = schemas.get(model_name, {}).get("properties", {})
        for alias, expected in expected_fields.items():
            actual = _property_contract(properties.get(alias, {}))
            field_checks.append({
                "model": model_name,
                "field": alias,
                "expected": expected,
                "actual": actual,
                "ok": actual == expected,
            })

    config_checks: list[dict[str, Any]] = []
    for model_name in contract["configuredModels"]:
        model = getattr(admin_schemas, model_name)
        config = model.model_config
        actual = {
            "populate_by_name": config.get("populate_by_name"),
            "str_strip_whitespace": config.get("str_strip_whitespace"),
            "validate_by_alias": config.get("validate_by_alias"),
            "validate_by_name": config.get("validate_by_name"),
        }
        expected = {
            "populate_by_name": True,
            "str_strip_whitespace": True,
            "validate_by_alias": True,
            "validate_by_name": True,
        }
        config_checks.append({"model": model_name, "expected": expected, "actual": actual, "ok": actual == expected})

    runtime_checks = _runtime_behavior_checks()
    failed_required = [item for item in required_checks if not item["ok"]]
    failed_fields = [item for item in field_checks if not item["ok"]]
    failed_configs = [item for item in config_checks if not item["ok"]]
    failed_runtime = [item for item in runtime_checks if not item["ok"]]

    return {
        "ok": not any((failed_required, failed_fields, failed_configs, failed_runtime)),
        "version": contract["version"],
        "status": contract["status"],
        "requiredCheckCount": len(required_checks),
        "fieldConstraintCheckCount": len(field_checks),
        "modelConfigCheckCount": len(config_checks),
        "runtimeBehaviorCheckCount": len(runtime_checks),
        "requiredChecks": required_checks,
        "failedRequiredChecks": failed_required,
        "fieldConstraintChecks": field_checks,
        "failedFieldConstraintChecks": failed_fields,
        "modelConfigChecks": config_checks,
        "failedModelConfigChecks": failed_configs,
        "runtimeBehaviorChecks": runtime_checks,
        "failedRuntimeBehaviorChecks": failed_runtime,
    }
