from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from app.api.routes.admin_route_map_contract import ADMIN_ROUTE_MODULE_CONTRACT
from app.api.routes.admin_runtime_route_contract import (
    ADMIN_RUNTIME_ROUTE_CONTRACT,
    _runtime_admin_routes,
)


ADMIN_ROUTE_OPERATION_CONTRACT: dict[str, Any] = {
    "version": "v227.backend-admin-route-operation-contract",
    "status": "route-operation-metadata-v227",
    "policy": "Admin route endpoint names, response type markers, static ownership, and FastAPI runtime metadata must stay aligned",
    "sourceRouteMap": "backend/app/api/routes/admin_route_map_contract.py",
    "sourceRuntimeContract": "backend/app/api/routes/admin_runtime_route_contract.py",
    "operations": [
        {"method": "GET", "path": "/requirements", "type": "admin.requirements", "endpoint": "get_admin_requirements", "owner": "overview-snapshot", "ownerFile": "backend/app/api/routes/admin_overview_snapshot_routes.py"},
        {"method": "GET", "path": "/overview", "type": "admin.overview", "endpoint": "get_admin_readonly_overview", "owner": "overview-snapshot", "ownerFile": "backend/app/api/routes/admin_overview_snapshot_routes.py"},
        {"method": "GET", "path": "/save-snapshots", "type": "admin.save_snapshots", "endpoint": "list_admin_save_snapshots", "owner": "overview-snapshot", "ownerFile": "backend/app/api/routes/admin_overview_snapshot_routes.py"},
        {"method": "POST", "path": "/change-preview", "type": "admin.change.preview", "endpoint": "preview_admin_change", "owner": "overview-snapshot", "ownerFile": "backend/app/api/routes/admin_overview_snapshot_routes.py"},
        {"method": "GET", "path": "/master-data/domains", "type": "admin.master_data.domains", "endpoint": "list_admin_master_catalog_domains", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "GET", "path": "/master-data/catalog", "type": "admin.master_data.catalog", "endpoint": "list_admin_master_catalog_rows", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "GET", "path": "/master-data/create-blueprint", "type": "admin.master_data.create_blueprint", "endpoint": "get_admin_master_create_blueprint", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "POST", "path": "/master-data/create-preview", "type": "admin.master_data.create_preview", "endpoint": "preview_admin_master_data_create", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "POST", "path": "/master-data/create-apply", "type": "admin.master_data.create_apply", "endpoint": "apply_admin_master_data_create", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "GET", "path": "/master-data/detail", "type": "admin.master_data.detail", "endpoint": "get_admin_master_catalog_detail", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "GET", "path": "/master-data/relations", "type": "admin.master_data.relations", "endpoint": "get_admin_master_catalog_relations", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "POST", "path": "/master-data/edit-preview", "type": "admin.master_data.edit_preview", "endpoint": "preview_admin_master_data_edit", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "POST", "path": "/master-data/edit-apply", "type": "admin.master_data.edit_apply", "endpoint": "apply_admin_master_data_edit", "owner": "master-data", "ownerFile": "backend/app/api/routes/admin_master_data_routes.py"},
        {"method": "GET", "path": "/change-logs", "type": "admin.change_logs", "endpoint": "list_admin_change_logs", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "GET", "path": "/change-logs/{change_log_id}", "type": "admin.change_log.detail", "endpoint": "get_admin_change_log_detail", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-preview", "type": "admin.change_log.create_delete_preview", "endpoint": "preview_admin_create_delete_rollback", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-apply", "type": "admin.change_log.create_delete_apply", "endpoint": "apply_admin_create_delete_rollback", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-preview", "type": "admin.change_log.create_delete_restore_preview", "endpoint": "preview_admin_create_delete_restore", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-apply", "type": "admin.change_log.create_delete_restore_apply", "endpoint": "apply_admin_create_delete_restore", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-preview", "type": "admin.change_log.rollback_preview", "endpoint": "preview_admin_change_log_rollback", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
        {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-apply", "type": "admin.change_log.rollback_apply", "endpoint": "apply_admin_change_log_rollback", "owner": "change-log", "ownerFile": "backend/app/api/routes/admin_change_log_routes.py"},
    ],
}

_ROUTE_BLOCK_RE = re.compile(
    r'(?P<block>@router\.(?P<method>get|post)\("(?P<path>[^"]+)"\)[\s\S]*?)(?=\n@router\.(?:get|post)\("|\Z)'
)
_ENDPOINT_RE = re.compile(r"async\s+def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _operation_key(operation: dict[str, str]) -> str:
    return f'{operation["method"].upper()} {operation["path"]}'


def _runtime_key(operation: dict[str, str]) -> str:
    base = f'{ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]}'
    return f'{operation["method"].upper()} {base}{operation["path"]}'


def _route_map_operations() -> list[dict[str, str]]:
    operations: list[dict[str, str]] = []
    for module in ADMIN_ROUTE_MODULE_CONTRACT["modules"]:
        for route in module["routes"]:
            operations.append({
                "method": route["method"].upper(),
                "path": route["path"],
                "type": route["type"],
                "owner": module["key"],
                "ownerFile": module["file"],
            })
    return operations


def _read_module_sources(root: Path | None) -> dict[str, str]:
    if root is None:
        return {}
    files = sorted({operation["ownerFile"] for operation in ADMIN_ROUTE_OPERATION_CONTRACT["operations"]})
    return {
        file: (root / file).read_text(encoding="utf-8") if (root / file).exists() else ""
        for file in files
    }


def _extract_operation_blocks(source: str, *, file: str) -> dict[str, dict[str, Any]]:
    blocks: dict[str, dict[str, Any]] = {}
    for match in _ROUTE_BLOCK_RE.finditer(source):
        method = match.group("method").upper()
        path = match.group("path")
        block = match.group("block")
        endpoint_match = _ENDPOINT_RE.search(block)
        key = f"{method} {path}"
        blocks[key] = {
            "key": key,
            "method": method,
            "path": path,
            "file": file,
            "endpoint": endpoint_match.group(1) if endpoint_match else None,
            "block": block,
            "hasAdminResponseWrapper": "admin_ok_response(" in block,
        }
    return blocks


def get_admin_route_operation_contract_readiness(
    *,
    root: str | Path | None = None,
    app: FastAPI | None = None,
) -> dict[str, Any]:
    """Return a static/runtime route operation metadata readiness report.

    v227 sits on top of the route ownership and runtime-registration contracts.
    It fixes the endpoint/function names and response type markers for each admin
    route so a later refactor cannot accidentally swap handlers while keeping the
    same method/path pair.
    """

    contract = ADMIN_ROUTE_OPERATION_CONTRACT
    root_path = Path(root) if root is not None else None
    expected = list(contract["operations"])
    expected_by_key = {_operation_key(item): item for item in expected}

    route_map = _route_map_operations()
    route_map_by_key = {_operation_key(item): item for item in route_map}
    route_map_alignment_checks = []
    for operation in expected:
        key = _operation_key(operation)
        route_map_item = route_map_by_key.get(key)
        route_map_alignment_checks.append({
            "key": key,
            "endpoint": operation["endpoint"],
            "ok": bool(
                route_map_item
                and route_map_item.get("type") == operation["type"]
                and route_map_item.get("owner") == operation["owner"]
                and route_map_item.get("ownerFile") == operation["ownerFile"]
            ),
        })

    duplicate_operation_keys = sorted({key for key in expected_by_key if [_operation_key(item) for item in expected].count(key) > 1})
    route_map_missing = [item for item in expected if _operation_key(item) not in route_map_by_key]
    route_map_unexpected = [item for item in route_map if _operation_key(item) not in expected_by_key]

    sources = _read_module_sources(root_path)
    static_blocks: dict[str, dict[str, Any]] = {}
    for file, source in sources.items():
        static_blocks.update(_extract_operation_blocks(source, file=file))

    static_operation_checks = []
    for operation in expected:
        key = _operation_key(operation)
        block = static_blocks.get(key)
        block_source = block["block"] if block else ""
        static_operation_checks.append({
            "key": key,
            "endpoint": operation["endpoint"],
            "type": operation["type"],
            "owner": operation["owner"],
            "ownerFile": operation["ownerFile"],
            "actualEndpoint": block.get("endpoint") if block else None,
            "endpointOk": bool(block and block.get("endpoint") == operation["endpoint"]),
            "typeMarkerOk": bool(block and f'type="{operation["type"]}"' in block_source),
            "responseWrapperOk": bool(block and block.get("hasAdminResponseWrapper")),
            "ownerFileOk": bool(block and block.get("file") == operation["ownerFile"]),
        })
    for item in static_operation_checks:
        item["ok"] = item["endpointOk"] and item["typeMarkerOk"] and item["responseWrapperOk"] and item["ownerFileOk"]

    actual_runtime = _runtime_admin_routes(app) if app is not None else []
    actual_runtime_by_key = {item["key"]: item for item in actual_runtime}
    runtime_operation_checks = []
    for operation in expected:
        key = _runtime_key(operation)
        actual = actual_runtime_by_key.get(key)
        runtime_operation_checks.append({
            "key": key,
            "sourceKey": _operation_key(operation),
            "endpoint": operation["endpoint"],
            "type": operation["type"],
            "owner": operation["owner"],
            "actualEndpoint": actual.get("endpoint") if actual else None,
            "actualName": actual.get("name") if actual else None,
            "ok": bool(actual and actual.get("endpoint") == operation["endpoint"] and actual.get("name") == operation["endpoint"]),
        })

    failed_route_map_alignment_checks = [item for item in route_map_alignment_checks if not item["ok"]]
    failed_static_operation_checks = [item for item in static_operation_checks if not item["ok"]]
    failed_runtime_operation_checks = [item for item in runtime_operation_checks if not item["ok"]]

    ok = (
        contract["status"] == "route-operation-metadata-v227"
        and len(expected) == 21
        and not duplicate_operation_keys
        and not route_map_missing
        and not route_map_unexpected
        and not failed_route_map_alignment_checks
        and root_path is not None
        and not failed_static_operation_checks
        and app is not None
        and not failed_runtime_operation_checks
    )

    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "policy": contract["policy"],
        "contract": contract,
        "sourceRouteMapStatus": ADMIN_ROUTE_MODULE_CONTRACT["status"],
        "sourceRuntimeStatus": ADMIN_RUNTIME_ROUTE_CONTRACT["status"],
        "operationCount": len(expected),
        "routeMapCount": len(route_map),
        "runtimeRouteCount": len(actual_runtime),
        "duplicateOperationKeys": duplicate_operation_keys,
        "routeMapMissing": route_map_missing,
        "routeMapUnexpected": route_map_unexpected,
        "routeMapAlignmentChecks": route_map_alignment_checks,
        "staticOperationChecks": static_operation_checks,
        "runtimeOperationChecks": runtime_operation_checks,
        "failedRouteMapAlignmentChecks": failed_route_map_alignment_checks,
        "failedStaticOperationChecks": failed_static_operation_checks,
        "failedRuntimeOperationChecks": failed_runtime_operation_checks,
    }
