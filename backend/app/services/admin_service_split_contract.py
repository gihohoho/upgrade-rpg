from __future__ import annotations

from pathlib import Path
from typing import Any


ADMIN_SERVICE_SPLIT_CONTRACT: dict[str, Any] = {
    "version": "v198.backend-admin-service-split-contract",
    "status": "contract-frozen-v198",
    "splitStatus": "admin-schema-field-constraint-contract-v238",
    "extractedFiles": [
        "backend/app/services/admin/admin_overview_snapshots_service.py",
        "backend/app/services/admin/admin_master_catalog_service.py",
        "backend/app/services/admin/admin_create_lifecycle_service.py",
        "backend/app/services/admin/admin_change_log_service.py",
        "backend/app/services/admin/admin_edit_draft_service.py",
        "backend/app/services/admin/admin_shared_utils.py",
        "backend/app/services/admin/admin_config.py",
        "backend/app/services/admin/admin_readiness_service.py",
        "backend/app/api/routes/admin_response_helpers.py",
        "backend/app/api/routes/admin_route_params.py",
        "backend/app/api/routes/admin_route_error_helpers.py",
        "backend/app/api/routes/admin_response_data_helpers.py",
        "backend/app/api/routes/admin_response_meta_helpers.py",
        "backend/app/api/routes/admin_master_data_routes.py",
        "backend/app/api/routes/admin_change_log_routes.py",
        "backend/app/api/routes/admin_overview_snapshot_routes.py",
        "backend/app/api/routes/admin_route_map_contract.py",
        "backend/app/api/routes/admin_route_module_import_contract.py",
        "backend/app/api/routes/admin_runtime_route_contract.py",
        "backend/app/api/routes/admin_route_operation_contract.py",
        "backend/app/api/routes/admin_openapi_route_contract.py",
        "backend/app/api/routes/admin_response_metadata_contract.py",
        "backend/app/api/routes/admin_request_metadata_contract.py",
        "backend/app/api/routes/admin_schema_model_contract.py",
        "backend/app/api/routes/admin_schema_field_constraint_contract.py",
        "backend/app/api/routes/admin_route_services.py",
        "backend/app/services/admin_service_legacy_markers.py",
        "backend/app/services/admin_service_facade_contract.py",
    ],
    "currentFile": "backend/app/services/admin_service.py",
    "facadeFile": "backend/app/services/admin_service.py",
    "routeFile": "backend/app/api/routes/admin.py",
    "schemaFile": "backend/app/schemas/admin.py",
    "splitPolicy": "route-schema-stable-service-internal-split",
    "splitGroups": [
        {
            "key": "overview-snapshots",
            "label": "Overview/save snapshots",
            "candidateFile": "backend/app/services/admin/admin_overview_snapshots_service.py",
            "publicMethods": ["get_readonly_overview", "list_save_snapshot_summaries"],
            "helperMethods": [
                "_get_master_data_counts",
                "_get_save_snapshot_summary",
                "_get_user_summary",
                "_build_snapshot_filters",
                "_build_snapshot_where_clauses",
                "_snapshot_order_by",
                "_count_save_snapshots",
                "_serialize_save_snapshot_summary",
            ],
        },
        {
            "key": "master-catalog",
            "label": "Master catalog/detail/relations",
            "candidateFile": "backend/app/services/admin/admin_master_catalog_service.py",
            "publicMethods": [
                "list_master_catalog_domains",
                "list_master_catalog_rows",
                "get_master_catalog_detail",
                "get_master_catalog_relations",
            ],
            "helperMethods": [
                "_build_master_catalog_where_clauses",
                "_master_catalog_order_by",
                "_count_master_catalog_rows",
                "_master_catalog_columns",
                "_serialize_master_catalog_row",
                "_serialize_master_detail_scalar_fields",
                "_serialize_master_detail_json_fields",
                "_build_master_detail_relation_hints",
                "_build_master_relation_edit_options",
                "_build_master_relation_groups",
                "_fetch_master_relation_group",
                "_serialize_master_relation_row",
            ],
        },
        {
            "key": "edit-draft",
            "label": "Master edit preview/apply",
            "candidateFile": "backend/app/services/admin/admin_edit_draft_service.py",
            "publicMethods": ["preview_master_data_edit", "apply_master_data_edit"],
            "helperMethods": [
                "_empty_edit_preview",
                "_master_edit_column_map",
                "_master_edit_field_is_readonly",
                "_master_edit_field_is_allowed",
                "_master_relation_edit_field_is_open",
                "_validate_master_relation_edit_value",
                "_describe_master_relation_edit_value",
                "_build_proposed_combo_values",
                "_normalize_master_edit_value",
                "_master_edit_column_type",
            ],
        },
        {
            "key": "create-lifecycle",
            "label": "Create/delete/restore lifecycle",
            "candidateFile": "backend/app/services/admin/admin_create_lifecycle_service.py",
            "publicMethods": [
                "get_master_create_blueprint",
                "preview_master_data_create",
                "apply_master_data_create",
                "preview_admin_create_delete_rollback",
                "apply_admin_create_delete_rollback",
                "preview_admin_create_delete_restore",
                "apply_admin_create_delete_restore",
            ],
            "helperMethods": [
                "_master_create_lifecycle_dependency_guards",
                "_master_create_lifecycle_payload",
                "_empty_create_preview",
                "_empty_create_delete_preview",
                "_empty_create_delete_restore_preview",
                "_build_create_delete_dependency_checks",
                "_master_create_column_map",
                "_exists_duplicate_unique_value",
                "_create_combo_guard_labels",
                "_validate_master_create_relations",
                "_describe_master_create_relation_value",
                "_build_master_create_relation_options",
            ],
        },
        {
            "key": "change-logs",
            "label": "Admin change logs/rollback",
            "candidateFile": "backend/app/services/admin/admin_change_log_service.py",
            "publicMethods": [
                "list_admin_change_logs",
                "get_admin_change_log_detail",
                "preview_admin_change_log_rollback",
                "apply_admin_change_log_rollback",
            ],
            "helperMethods": [
                "_clean_admin_change_log_filters",
                "_build_admin_change_log_where_clauses",
                "_admin_change_log_order_by",
                "_get_admin_change_log",
                "_empty_change_log_detail",
                "_empty_rollback_preview",
                "_serialize_admin_change_log_detail",
                "_build_change_log_changes",
                "_build_change_log_changes_with_relations",
                "_enrich_rollback_mismatches_with_relations",
                "_describe_change_log_relation_value",
                "_extract_master_change_target",
                "_current_master_values",
                "_count_admin_change_logs",
                "_serialize_admin_change_log",
            ],
        },
        {
            "key": "shared-utils",
            "label": "Shared relation/count/serialization helpers",
            "candidateFile": "backend/app/services/admin/admin_shared_utils.py",
            "publicMethods": [],
            "helperMethods": [
                "_exists_by_code",
                "_fetch_code_name",
                "_exists_duplicate_combo",
                "_fetch_relation_code_options",
                "_serialize_relation_option",
                "_count_where",
                "_get_master_row",
                "_count",
                "_is_safe_admin_change_key",
                "_clean_filter_text",
                "_is_safe_slot_key",
                "_is_asset_field",
                "_serialize_asset_field",
                "_safe_detail_scalar_value",
                "_sanitize_json_preview",
                "_sanitize_json_value",
                "_humanize_field_name",
                "_join_json_keys",
                "_count_filled_items",
            ],
        },
        {
            "key": "config",
            "label": "Static admin domain/config definitions",
            "candidateFile": "backend/app/services/admin/admin_config.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "readiness",
            "label": "Admin readiness/preview helpers",
            "candidateFile": "backend/app/services/admin/admin_readiness_service.py",
            "publicMethods": ["preview_change"],
            "helperMethods": ["_build_readiness"],
        },
        {
            "key": "route-response-helper",
            "label": "Admin route response wrapper",
            "candidateFile": "backend/app/api/routes/admin_response_helpers.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-params",
            "label": "Admin route dependency/query defaults",
            "candidateFile": "backend/app/api/routes/admin_route_params.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-error-helpers",
            "label": "Admin route local fallback payload helpers",
            "candidateFile": "backend/app/api/routes/admin_route_error_helpers.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-response-data",
            "label": "Admin route response data builders",
            "candidateFile": "backend/app/api/routes/admin_response_data_helpers.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-response-meta",
            "label": "Admin route response metadata builders",
            "candidateFile": "backend/app/api/routes/admin_response_meta_helpers.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-master-data-module",
            "label": "Admin master-data route module",
            "candidateFile": "backend/app/api/routes/admin_master_data_routes.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-change-log-module",
            "label": "Admin change-log route module",
            "candidateFile": "backend/app/api/routes/admin_change_log_routes.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-overview-snapshot-module",
            "label": "Admin overview/save-snapshot route module",
            "candidateFile": "backend/app/api/routes/admin_overview_snapshot_routes.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-map-contract",
            "label": "Admin strict route ownership map contract",
            "candidateFile": "backend/app/api/routes/admin_route_map_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-module-import-contract",
            "label": "Admin route module import/dependency contract",
            "candidateFile": "backend/app/api/routes/admin_route_module_import_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "runtime-route-contract",
            "label": "Admin FastAPI runtime route registration contract",
            "candidateFile": "backend/app/api/routes/admin_runtime_route_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-operation-contract",
            "label": "Admin route operation endpoint/type metadata contract",
            "candidateFile": "backend/app/api/routes/admin_route_operation_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "openapi-route-contract",
            "label": "Admin OpenAPI route operation metadata contract",
            "candidateFile": "backend/app/api/routes/admin_openapi_route_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-response-metadata",
            "label": "Admin route response status/model/OpenAPI metadata contract",
            "candidateFile": "backend/app/api/routes/admin_response_metadata_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-request-metadata",
            "label": "Admin route request/query/body/dependency metadata contract",
            "candidateFile": "backend/app/api/routes/admin_request_metadata_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "route-service-dependency",
            "label": "Admin route service factory dependency",
            "candidateFile": "backend/app/api/routes/admin_route_services.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "service-legacy-markers",
            "label": "Legacy static smoke markers outside AdminService facade",
            "candidateFile": "backend/app/services/admin_service_legacy_markers.py",
            "publicMethods": [],
            "helperMethods": [],
        },
        {
            "key": "service-facade-contract",
            "label": "AdminService facade MRO/import contract",
            "candidateFile": "backend/app/services/admin_service_facade_contract.py",
            "publicMethods": [],
            "helperMethods": [],
        },
    ],
    "facadeMustKeep": [
        "AdminService",
        "MASTER_DATA_MODELS",
        "MASTER_CATALOG_DOMAINS",
        "MASTER_EDIT_ALLOWED_FIELDS",
        "MASTER_CREATE_BLUEPRINT_FIELDS",
        "MASTER_CREATE_APPLY_ALLOWED_DOMAINS",
        "MASTER_CREATE_DELETE_ALLOWED_DOMAINS",
        "ADMIN_CHANGE_LOG_ACTION_FILTERS",
        "MASTER_EDIT_APPLY_CONFIRM_TEXT",
        "MASTER_EDIT_ROLLBACK_CONFIRM_TEXT",
        "MASTER_CREATE_APPLY_CONFIRM_TEXT",
        "MASTER_CREATE_DELETE_CONFIRM_TEXT",
        "MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT",
    ],
    "routeContract": [
        "No route path changes through v234",
        "No schema changes through v234",
        "Master-data routes live in admin_master_data_routes.py",
        "Change-log routes live in admin_change_log_routes.py",
        "Overview/save-snapshot routes live in admin_overview_snapshot_routes.py",
        "admin.py stays as a thin include-router facade",
        "Legacy static smoke checks read actual route modules instead of admin.py comments",
        "Admin route ownership map lives in admin_route_map_contract.py",
        "Admin route ownership map verifies exact module-only ownership",
        "Admin route modules create service facade through admin_route_services.py",
        "Admin route module import/dependency style is tracked by admin_route_module_import_contract.py",
        "FastAPI runtime route registration is checked against static ownership map",
        "Runtime admin route contract lives in admin_runtime_route_contract.py",
        "Admin route operation metadata lives in admin_route_operation_contract.py",
        "Runtime route endpoint metadata is checked against static response type markers",
        "FastAPI OpenAPI admin route metadata is checked against operation contract",
        "OpenAPI operationId metadata is checked against runtime endpoint names",
        "Admin route response metadata contract lives in admin_response_metadata_contract.py",
        "Runtime response defaults keep default 200 status_code and no response_model",
        "OpenAPI response codes and summaries are checked against runtime route defaults",
        "Admin route request metadata contract lives in admin_request_metadata_contract.py",
        "Runtime query/path/body params are checked against request metadata contract",
        "OpenAPI query/path/header/body request metadata is checked against runtime routes",
        "Write apply routes keep require_admin_write_dev_key through ADMIN_WRITE_GUARD_DEP",
        "Admin request schema classes and OpenAPI components.schemas are checked for drift; Admin request field constraints, defaults, required fields, and Pydantic normalization behavior are checked for drift",
        "Route body models are checked against backend/app/schemas/admin.py class names",
        "Guarded apply schemas keep confirmText and reason fields",
        "Legacy service smoke markers live outside admin_service.py",
        "AdminService facade MRO/import order is tracked by admin_service_facade_contract.py",
        "Admin route responses go through admin_ok_response helper",
        "Admin route response data summaries go through admin_response_data_helpers.py",
        "Admin route response metadata goes through admin_response_meta_helpers.py",
        "Admin route dependency/query defaults go through admin_route_params.py",
        "Admin route local fallback payloads go through admin_route_error_helpers.py",
        "AdminService remains the facade imported by route modules",
        "Actual service file moves must keep every existing public method name",
    ],
}


def _all_method_names(contract: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for group in contract["splitGroups"]:
        names.extend(group.get("publicMethods", []))
        names.extend(group.get("helperMethods", []))
    return names


def get_admin_service_split_contract_readiness(
    service_cls: type[Any] | None = None,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Return a static readiness report for splitting AdminService later.

    v198 deliberately does not move backend code yet. This helper freezes the split
    boundary first so future service moves can be checked without changing admin
    routes or request/response schemas.
    """

    contract = ADMIN_SERVICE_SPLIT_CONTRACT
    root_path = Path(root) if root is not None else None

    required_methods = _all_method_names(contract)
    method_checks = []
    for method in required_methods:
        ok = bool(service_cls is not None and hasattr(service_cls, method))
        method_checks.append({"key": method, "ok": ok})

    constant_checks = []
    for key in contract["facadeMustKeep"]:
        ok = key == "AdminService" or bool(service_cls is not None and hasattr(service_cls, key))
        constant_checks.append({"key": key, "ok": ok})

    file_checks = []
    if root_path is not None:
        for key in ("currentFile", "routeFile", "schemaFile"):
            relative = contract[key]
            file_checks.append({"key": key, "path": relative, "ok": (root_path / relative).exists()})
        for relative in contract.get("extractedFiles", []):
            file_checks.append({"key": "extractedFile", "path": relative, "ok": (root_path / relative).exists()})

    group_keys = [group["key"] for group in contract["splitGroups"]]
    candidate_files = [group["candidateFile"] for group in contract["splitGroups"]]
    missing_methods = [item["key"] for item in method_checks if not item["ok"]]
    missing_constants = [item["key"] for item in constant_checks if not item["ok"]]
    missing_files = [item["path"] for item in file_checks if not item["ok"]]
    duplicate_group_keys = sorted({key for key in group_keys if group_keys.count(key) > 1})
    duplicate_candidate_files = sorted({path for path in candidate_files if candidate_files.count(path) > 1})

    line_count = None
    if root_path is not None:
        current_file = root_path / contract["currentFile"]
        if current_file.exists():
            line_count = len(current_file.read_text(encoding="utf-8").splitlines())

    ok = (
        contract["status"] == "contract-frozen-v198"
        and service_cls is not None
        and not missing_methods
        and not missing_constants
        and not missing_files
        and not duplicate_group_keys
        and not duplicate_candidate_files
    )

    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "splitStatus": contract.get("splitStatus"),
        "extractedFiles": contract.get("extractedFiles", []),
        "contract": contract,
        "groupCount": len(contract["splitGroups"]),
        "candidateFileCount": len(candidate_files),
        "methodCount": len(required_methods),
        "publicMethodCount": sum(len(group.get("publicMethods", [])) for group in contract["splitGroups"]),
        "helperMethodCount": sum(len(group.get("helperMethods", [])) for group in contract["splitGroups"]),
        "constantCount": len(contract["facadeMustKeep"]),
        "routeContractCount": len(contract["routeContract"]),
        "lineCount": line_count,
        "methodChecks": method_checks,
        "constantChecks": constant_checks,
        "fileChecks": file_checks,
        "missingMethods": missing_methods,
        "missingConstants": missing_constants,
        "missingFiles": missing_files,
        "duplicateGroupKeys": duplicate_group_keys,
        "duplicateCandidateFiles": duplicate_candidate_files,
    }
