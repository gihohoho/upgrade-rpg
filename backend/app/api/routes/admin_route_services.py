from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.admin_service import AdminService


ADMIN_ROUTE_SERVICE_DEPENDENCY_CONTRACT: dict[str, Any] = {
    "version": "v219.backend-admin-route-service-dependency",
    "status": "route-service-dependency-v219",
    "factoryFile": "backend/app/api/routes/admin_route_services.py",
    "policy": "route modules create AdminService through create_admin_service() only",
    "routeModules": [
        "backend/app/api/routes/admin_overview_snapshot_routes.py",
        "backend/app/api/routes/admin_master_data_routes.py",
        "backend/app/api/routes/admin_change_log_routes.py",
    ],
}


def create_admin_service() -> AdminService:
    """Create the stable admin service facade used by admin route modules.

    Keeping this tiny factory in one file makes the route modules easier to
    split further later without each module manually importing AdminService.
    """

    return AdminService()


def get_admin_route_service_dependency_readiness(*, root: str | Path | None = None) -> dict[str, Any]:
    """Return static readiness for route-module service dependency cleanup."""

    contract = ADMIN_ROUTE_SERVICE_DEPENDENCY_CONTRACT
    root_path = Path(root) if root is not None else None
    module_checks: list[dict[str, Any]] = []

    if root_path is not None:
        factory_path = root_path / contract["factoryFile"]
        factory_source = factory_path.read_text(encoding="utf-8") if factory_path.exists() else ""
        factory_ok = (
            factory_path.exists()
            and "def create_admin_service() -> AdminService" in factory_source
            and "return AdminService()" in factory_source
        )
    else:
        factory_ok = True

    for relative in contract["routeModules"]:
        source = ""
        file_ok = True
        if root_path is not None:
            path = root_path / relative
            file_ok = path.exists()
            source = path.read_text(encoding="utf-8") if file_ok else ""
        module_checks.append(
            {
                "file": relative,
                "ok": file_ok
                and "from app.api.routes.admin_route_services import create_admin_service" in source
                and "service = create_admin_service()" in source
                and "from app.services.admin_service import AdminService" not in source
                and "service = AdminService()" not in source,
            }
        )

    failed_modules = [check for check in module_checks if not check["ok"]]
    ok = contract["status"] == "route-service-dependency-v219" and factory_ok and not failed_modules
    return {
        "ok": ok,
        "version": contract["version"],
        "status": contract["status"],
        "factoryFile": contract["factoryFile"],
        "policy": contract["policy"],
        "routeModuleCount": len(contract["routeModules"]),
        "factoryOk": factory_ok,
        "moduleChecks": module_checks,
        "failedModules": failed_modules,
    }
