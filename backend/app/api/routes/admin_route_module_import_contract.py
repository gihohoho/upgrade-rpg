from __future__ import annotations

from pathlib import Path
from typing import Any


ADMIN_ROUTE_MODULE_IMPORT_CONTRACT: dict[str, Any] = {
    "version": "v224.backend-admin-route-module-import-contract",
    "status": "route-module-imports-frozen-v224",
    "policy": "feature route modules use the shared create_admin_service factory and never import AdminService directly",
    "modules": [
        {
            "key": "overview-snapshot",
            "file": "backend/app/api/routes/admin_overview_snapshot_routes.py",
            "requiredImports": [
                "from app.api.routes.admin_response_helpers import admin_ok_response",
                "from app.api.routes.admin_response_meta_helpers import admin_route_meta",
                "from app.api.routes.admin_route_services import create_admin_service",
            ],
            "forbiddenImports": [
                "from app.services.admin_service import AdminService",
                "AdminService()",
            ],
        },
        {
            "key": "master-data",
            "file": "backend/app/api/routes/admin_master_data_routes.py",
            "requiredImports": [
                "from app.api.routes.admin_response_helpers import admin_ok_response",
                "from app.api.routes.admin_response_meta_helpers import admin_route_meta",
                "from app.api.routes.admin_route_services import create_admin_service",
            ],
            "forbiddenImports": [
                "from app.services.admin_service import AdminService",
                "AdminService()",
            ],
        },
        {
            "key": "change-log",
            "file": "backend/app/api/routes/admin_change_log_routes.py",
            "requiredImports": [
                "from app.api.routes.admin_response_helpers import admin_ok_response",
                "from app.api.routes.admin_response_meta_helpers import admin_route_meta",
                "from app.api.routes.admin_route_services import create_admin_service",
                "from app.api.routes.admin_route_error_helpers import build_admin_change_logs_unavailable_payload",
            ],
            "forbiddenImports": [
                "from app.services.admin_service import AdminService",
                "AdminService()",
            ],
        },
    ],
}


def _check_import_order(source: str, required_imports: list[str]) -> dict[str, Any]:
    indexes = [source.find(item) for item in required_imports]
    return {
        "requiredImports": required_imports,
        "indexes": indexes,
        "ok": all(index >= 0 for index in indexes) and indexes == sorted(indexes),
    }


def get_admin_route_module_import_contract_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    """Return a static readiness report for admin route module import/dependency style."""

    contract = ADMIN_ROUTE_MODULE_IMPORT_CONTRACT
    root_path = Path(root) if root is not None else None
    module_checks: list[dict[str, Any]] = []

    for module in contract["modules"]:
        source = ""
        file_ok = True
        if root_path is not None:
            file_path = root_path / module["file"]
            file_ok = file_path.exists()
            source = file_path.read_text(encoding="utf-8") if file_ok else ""
        import_order = _check_import_order(source, module["requiredImports"]) if root_path is not None else {"ok": True}
        service_factory_ok = True
        router_ok = True
        forbidden_hits: list[str] = []
        if root_path is not None:
            service_factory_ok = "service = create_admin_service()" in source
            router_ok = "router = APIRouter()" in source
            forbidden_hits = [item for item in module["forbiddenImports"] if item in source]
        module_checks.append({
            "key": module["key"],
            "file": module["file"],
            "fileOk": file_ok,
            "importOrder": import_order,
            "serviceFactoryOk": service_factory_ok,
            "routerOk": router_ok,
            "forbiddenHits": forbidden_hits,
            "ok": file_ok and import_order["ok"] and service_factory_ok and router_ok and not forbidden_hits,
        })

    failed_modules = [check for check in module_checks if not check["ok"]]
    ok = contract["status"] == "route-module-imports-frozen-v224" and not failed_modules
    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "policy": contract["policy"],
        "contract": contract,
        "moduleCount": len(contract["modules"]),
        "moduleChecks": module_checks,
        "failedModules": failed_modules,
    }
