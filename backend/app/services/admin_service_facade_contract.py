from __future__ import annotations

from pathlib import Path
from typing import Any


ADMIN_SERVICE_FACADE_CONTRACT: dict[str, Any] = {
    "version": "v222.backend-admin-service-facade-contract",
    "status": "facade-mro-contract-v222",
    "facadeFile": "backend/app/services/admin_service.py",
    "expectedFacadeClass": "AdminService",
    "expectedMixinOrder": [
        "AdminConfigService",
        "AdminSharedUtilsService",
        "AdminReadinessService",
        "AdminOverviewSnapshotsService",
        "AdminMasterCatalogService",
        "AdminEditDraftService",
        "AdminChangeLogService",
        "AdminCreateLifecycleService",
    ],
    "requiredExports": ["AdminService"],
    "lineLimit": 40,
    "policy": [
        "AdminService remains a thin route facade",
        "Mixin order is explicit and smoke-tested",
        "Route modules continue importing the facade through admin_route_services.py",
        "No route path/schema/API response changes",
    ],
}


def get_admin_service_facade_contract_readiness(
    service_cls: type[Any] | None = None,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Return a static readiness report for the AdminService facade/MRO."""

    contract = ADMIN_SERVICE_FACADE_CONTRACT
    expected_order = list(contract["expectedMixinOrder"])
    actual_order: list[str] = []
    if service_cls is not None:
        actual_order = [base.__name__ for base in service_cls.__bases__]

    root_path = Path(root) if root is not None else None
    facade_exists = True
    line_count: int | None = None
    facade_source = ""
    if root_path is not None:
        facade_path = root_path / contract["facadeFile"]
        facade_exists = facade_path.exists()
        if facade_exists:
            facade_source = facade_path.read_text(encoding="utf-8")
            line_count = len(facade_source.splitlines())

    class_ok = bool(service_cls is not None and service_cls.__name__ == contract["expectedFacadeClass"])
    order_ok = actual_order == expected_order
    export_ok = '__all__ = ["AdminService"]' in facade_source if facade_source else root_path is None
    line_ok = bool(line_count is None or line_count <= int(contract["lineLimit"]))
    legacy_marker_free = "LEGACY_SMOKE_MARKERS" not in facade_source if facade_source else True
    one_line_mro_removed = "class AdminService(AdminConfigService," not in facade_source if facade_source else True

    return {
        "ok": bool(class_ok and order_ok and facade_exists and export_ok and line_ok and legacy_marker_free and one_line_mro_removed),
        "version": contract["version"],
        "status": contract["status"],
        "contract": contract,
        "facadeFile": contract["facadeFile"],
        "expectedFacadeClass": contract["expectedFacadeClass"],
        "classOk": class_ok,
        "expectedMixinOrder": expected_order,
        "actualMixinOrder": actual_order,
        "mixinOrderOk": order_ok,
        "facadeExists": facade_exists,
        "lineCount": line_count,
        "lineLimit": contract["lineLimit"],
        "lineLimitOk": line_ok,
        "exportOk": export_ok,
        "legacyMarkerFree": legacy_marker_free,
        "oneLineMroRemoved": one_line_mro_removed,
        "policy": contract["policy"],
        "policyCount": len(contract["policy"]),
    }
