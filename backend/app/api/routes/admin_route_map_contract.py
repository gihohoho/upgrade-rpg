from __future__ import annotations

import re
from pathlib import Path
from typing import Any


ADMIN_ROUTE_MODULE_CONTRACT: dict[str, Any] = {
    "version": "v223.backend-admin-route-ownership-contract",
    "status": "route-ownership-strict-v223",
    "facadeFile": "backend/app/api/routes/admin.py",
    "facadePolicy": "admin.py only includes feature routers; route bodies live in modules",
    "modules": [
        {
            "key": "overview-snapshot",
            "file": "backend/app/api/routes/admin_overview_snapshot_routes.py",
            "routes": [
                {"method": "GET", "path": "/requirements", "type": "admin.requirements"},
                {"method": "GET", "path": "/overview", "type": "admin.overview"},
                {"method": "GET", "path": "/save-snapshots", "type": "admin.save_snapshots"},
                {"method": "POST", "path": "/change-preview", "type": "admin.change.preview"},
            ],
        },
        {
            "key": "master-data",
            "file": "backend/app/api/routes/admin_master_data_routes.py",
            "routes": [
                {"method": "GET", "path": "/master-data/domains", "type": "admin.master_data.domains"},
                {"method": "GET", "path": "/master-data/catalog", "type": "admin.master_data.catalog"},
                {"method": "GET", "path": "/master-data/create-blueprint", "type": "admin.master_data.create_blueprint"},
                {"method": "POST", "path": "/master-data/create-preview", "type": "admin.master_data.create_preview"},
                {"method": "POST", "path": "/master-data/create-apply", "type": "admin.master_data.create_apply"},
                {"method": "GET", "path": "/master-data/detail", "type": "admin.master_data.detail"},
                {"method": "GET", "path": "/master-data/relations", "type": "admin.master_data.relations"},
                {"method": "POST", "path": "/master-data/edit-preview", "type": "admin.master_data.edit_preview"},
                {"method": "POST", "path": "/master-data/edit-apply", "type": "admin.master_data.edit_apply"},
            ],
        },
        {
            "key": "change-log",
            "file": "backend/app/api/routes/admin_change_log_routes.py",
            "routes": [
                {"method": "GET", "path": "/change-logs", "type": "admin.change_logs"},
                {"method": "GET", "path": "/change-logs/{change_log_id}", "type": "admin.change_log.detail"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-preview", "type": "admin.change_log.create_delete_preview"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-apply", "type": "admin.change_log.create_delete_apply"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-preview", "type": "admin.change_log.create_delete_restore_preview"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/create-delete-restore-apply", "type": "admin.change_log.create_delete_restore_apply"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-preview", "type": "admin.change_log.rollback_preview"},
                {"method": "POST", "path": "/change-logs/{change_log_id}/rollback-apply", "type": "admin.change_log.rollback_apply"},
            ],
        },
    ],
}

_ROUTE_DECORATOR_RE = re.compile(r'@router\.(get|post)\("([^"]+)"\)')


def _decorator_for(route: dict[str, str]) -> str:
    method = route["method"].lower()
    return f'@router.{method}("{route["path"]}")'


def _route_key(route: dict[str, str]) -> str:
    return f'{route["method"].upper()} {route["path"]}'


def _extract_route_decorators(source: str, *, file: str) -> list[dict[str, str]]:
    return [
        {
            "method": match.group(1).upper(),
            "path": match.group(2),
            "file": file,
            "decorator": match.group(0),
            "key": f"{match.group(1).upper()} {match.group(2)}",
        }
        for match in _ROUTE_DECORATOR_RE.finditer(source)
    ]


def get_admin_route_module_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    """Return a static readiness report for admin route module ownership.

    v223 makes the route map stricter than the original v218 check: each route
    must exist in its assigned module and must not appear in any other admin
    route module. This catches accidental duplicate route registration before
    the browser sees a changed API surface.
    """

    contract = ADMIN_ROUTE_MODULE_CONTRACT
    root_path = Path(root) if root is not None else None
    module_checks: list[dict[str, Any]] = []
    route_checks: list[dict[str, Any]] = []
    ownership_checks: list[dict[str, Any]] = []
    type_checks: list[dict[str, Any]] = []
    module_route_count_checks: list[dict[str, Any]] = []
    facade_checks: list[dict[str, Any]] = []
    module_sources: dict[str, str] = {}
    actual_routes: list[dict[str, str]] = []

    expected_by_key: dict[str, dict[str, str]] = {}
    expected_owner_by_key: dict[str, str] = {}
    for module in contract["modules"]:
        for route in module["routes"]:
            key = _route_key(route)
            expected_by_key[key] = {**route, "key": key}
            expected_owner_by_key[key] = module["file"]

    # First pass: read every module and collect all actual decorators so
    # ownership/type checks can compare against the complete module set.
    for module in contract["modules"]:
        file_ok = True
        source = ""
        if root_path is not None:
            file_path = root_path / module["file"]
            file_ok = file_path.exists()
            source = file_path.read_text(encoding="utf-8") if file_ok else ""
        module_sources[module["file"]] = source
        module_checks.append({"key": module["key"], "file": module["file"], "ok": file_ok})
        module_actual_routes = _extract_route_decorators(source, file=module["file"]) if root_path is not None else []
        actual_routes.extend(module_actual_routes)
        if root_path is not None:
            module_route_count_checks.append({
                "module": module["key"],
                "file": module["file"],
                "expected": len(module["routes"]),
                "actual": len(module_actual_routes),
                "ok": len(module_actual_routes) == len(module["routes"]),
            })

    # Second pass: every route/type marker must live in exactly its assigned file.
    for module in contract["modules"]:
        source = module_sources[module["file"]]
        for route in module["routes"]:
            decorator = _decorator_for(route)
            type_marker = f'type="{route["type"]}"'
            route_ok = True
            if root_path is not None:
                route_ok = decorator in source and type_marker in source
            route_checks.append({
                "module": module["key"],
                "file": module["file"],
                "method": route["method"],
                "path": route["path"],
                "type": route["type"],
                "decorator": decorator,
                "ok": route_ok,
            })
            if root_path is not None:
                route_key = _route_key(route)
                actual_owners = [item["file"] for item in actual_routes if item["key"] == route_key]
                type_owners = [file for file, module_source in module_sources.items() if type_marker in module_source]
                ownership_checks.append({
                    "key": route_key,
                    "expectedFile": module["file"],
                    "actualFiles": actual_owners,
                    "ok": actual_owners == [module["file"]],
                })
                type_checks.append({
                    "type": route["type"],
                    "expectedFile": module["file"],
                    "actualFiles": type_owners,
                    "ok": type_owners == [module["file"]],
                })

    if root_path is not None:
        facade_path = root_path / contract["facadeFile"]
        facade_source = facade_path.read_text(encoding="utf-8") if facade_path.exists() else ""
        facade_checks.extend([
            {"key": "facadeFileExists", "ok": facade_path.exists()},
            {"key": "overviewIncluded", "ok": "router.include_router(admin_overview_snapshot_router)" in facade_source},
            {"key": "masterIncluded", "ok": "router.include_router(admin_master_data_router)" in facade_source},
            {"key": "changeLogIncluded", "ok": "router.include_router(admin_change_log_router)" in facade_source},
            {"key": "noInlineRouteDecorators", "ok": "@router.get(" not in facade_source and "@router.post(" not in facade_source},
            {"key": "noLegacyStaticSmokeMarkers", "ok": "Legacy static-smoke" not in facade_source and "# @router." not in facade_source},
        ])

    actual_route_keys = [item["key"] for item in actual_routes]
    duplicate_route_keys = sorted({key for key in actual_route_keys if actual_route_keys.count(key) > 1})
    unexpected_routes = [item for item in actual_routes if item["key"] not in expected_by_key]
    missing_modules = [check for check in module_checks if not check["ok"]]
    missing_routes = [check for check in route_checks if not check["ok"]]
    failed_ownership_checks = [check for check in ownership_checks if not check["ok"]]
    failed_type_checks = [check for check in type_checks if not check["ok"]]
    failed_module_route_count_checks = [check for check in module_route_count_checks if not check["ok"]]
    failed_facade_checks = [check for check in facade_checks if not check["ok"]]
    ok = (
        contract["status"] == "route-ownership-strict-v223"
        and not duplicate_route_keys
        and not unexpected_routes
        and not missing_modules
        and not missing_routes
        and not failed_ownership_checks
        and not failed_type_checks
        and not failed_module_route_count_checks
        and not failed_facade_checks
    )
    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "facadeFile": contract["facadeFile"],
        "facadePolicy": contract["facadePolicy"],
        "contract": contract,
        "moduleCount": len(contract["modules"]),
        "routeCount": len(route_checks),
        "actualRouteCount": len(actual_routes),
        "moduleChecks": module_checks,
        "routeChecks": route_checks,
        "ownershipChecks": ownership_checks,
        "typeChecks": type_checks,
        "moduleRouteCountChecks": module_route_count_checks,
        "facadeChecks": facade_checks,
        "duplicatePaths": duplicate_route_keys,
        "duplicateRouteKeys": duplicate_route_keys,
        "unexpectedRoutes": unexpected_routes,
        "missingModules": missing_modules,
        "missingRoutes": missing_routes,
        "failedOwnershipChecks": failed_ownership_checks,
        "failedTypeChecks": failed_type_checks,
        "failedModuleRouteCountChecks": failed_module_route_count_checks,
        "failedFacadeChecks": failed_facade_checks,
    }
