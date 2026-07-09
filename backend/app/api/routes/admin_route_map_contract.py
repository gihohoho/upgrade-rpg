from __future__ import annotations

from pathlib import Path
from typing import Any


ADMIN_ROUTE_MODULE_CONTRACT: dict[str, Any] = {
    "version": "v218.backend-admin-route-map-contract",
    "status": "route-map-frozen-v218",
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


def _decorator_for(route: dict[str, str]) -> str:
    method = route["method"].lower()
    return f'@router.{method}("{route["path"]}")'


def get_admin_route_module_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    """Return a static readiness report for admin route module ownership.

    This contract is intentionally independent of runtime FastAPI registration so
    static smoke tests can verify route ownership after admin.py became a thin
    include-router facade.
    """

    contract = ADMIN_ROUTE_MODULE_CONTRACT
    root_path = Path(root) if root is not None else None
    module_checks: list[dict[str, Any]] = []
    route_checks: list[dict[str, Any]] = []
    facade_checks: list[dict[str, Any]] = []

    for module in contract["modules"]:
        file_ok = True
        source = ""
        if root_path is not None:
            file_path = root_path / module["file"]
            file_ok = file_path.exists()
            source = file_path.read_text(encoding="utf-8") if file_ok else ""
        module_checks.append({"key": module["key"], "file": module["file"], "ok": file_ok})
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

    duplicate_paths = sorted({check["path"] for check in route_checks if [item["path"] for item in route_checks].count(check["path"]) > 1})
    missing_modules = [check for check in module_checks if not check["ok"]]
    missing_routes = [check for check in route_checks if not check["ok"]]
    failed_facade_checks = [check for check in facade_checks if not check["ok"]]
    ok = (
        contract["status"] == "route-map-frozen-v218"
        and not duplicate_paths
        and not missing_modules
        and not missing_routes
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
        "moduleChecks": module_checks,
        "routeChecks": route_checks,
        "facadeChecks": facade_checks,
        "duplicatePaths": duplicate_paths,
        "missingModules": missing_modules,
        "missingRoutes": missing_routes,
        "failedFacadeChecks": failed_facade_checks,
    }
