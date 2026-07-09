from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.api.routes.admin_route_map_contract import ADMIN_ROUTE_MODULE_CONTRACT


ADMIN_RUNTIME_ROUTE_CONTRACT: dict[str, Any] = {
    "version": "v225.backend-admin-runtime-route-contract",
    "status": "runtime-route-registration-v225",
    "policy": "FastAPI runtime registered /api/v1/admin routes must match the static admin route ownership map",
    "apiPrefix": "/api/v1",
    "adminPrefix": "/admin",
    "sourceContract": "backend/app/api/routes/admin_route_map_contract.py",
}

_IGNORED_METHODS = {"HEAD", "OPTIONS"}


def _expected_runtime_routes() -> list[dict[str, str]]:
    base = f'{ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]}'
    expected: list[dict[str, str]] = []
    for module in ADMIN_ROUTE_MODULE_CONTRACT["modules"]:
        for route in module["routes"]:
            expected.append(
                {
                    "method": route["method"].upper(),
                    "path": f'{base}{route["path"]}',
                    "sourcePath": route["path"],
                    "type": route["type"],
                    "owner": module["key"],
                    "ownerFile": module["file"],
                    "key": f'{route["method"].upper()} {base}{route["path"]}',
                }
            )
    return expected


def _runtime_admin_routes(app: FastAPI) -> list[dict[str, Any]]:
    base = f'{ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]}'
    routes: list[dict[str, Any]] = []
    for route in app.routes:
        path = getattr(route, "path", "")
        if not isinstance(path, str) or not path.startswith(base):
            continue
        methods = sorted((getattr(route, "methods", set()) or set()) - _IGNORED_METHODS)
        for method in methods:
            routes.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "name": getattr(route, "name", None),
                    "endpoint": getattr(getattr(route, "endpoint", None), "__name__", None),
                    "key": f"{method.upper()} {path}",
                }
            )
    return sorted(routes, key=lambda item: item["key"])


def get_admin_runtime_route_contract_readiness(app: FastAPI | None = None) -> dict[str, Any]:
    """Compare static admin route ownership with routes registered on the FastAPI app.

    Static route checks catch misplaced decorators. This runtime check catches the
    next class of mistakes: routers not included, wrong prefixes, or duplicate
    FastAPI registrations that only show up after the application is assembled.
    """

    expected = sorted(_expected_runtime_routes(), key=lambda item: item["key"])
    actual = _runtime_admin_routes(app) if app is not None else []

    expected_by_key = {item["key"]: item for item in expected}
    actual_by_key = {item["key"]: item for item in actual}
    actual_keys = [item["key"] for item in actual]

    missing_routes = [item for item in expected if item["key"] not in actual_by_key]
    unexpected_routes = [item for item in actual if item["key"] not in expected_by_key]
    duplicate_route_keys = sorted({key for key in actual_keys if actual_keys.count(key) > 1})
    prefix_checks = [
        {"key": "apiPrefix", "value": ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"], "ok": ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"] == "/api/v1"},
        {"key": "adminPrefix", "value": ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"], "ok": ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"] == "/admin"},
    ]
    count_check = {
        "expected": len(expected),
        "actual": len(actual),
        "ok": len(expected) == len(actual),
    }
    method_path_checks = [
        {
            "key": item["key"],
            "method": item["method"],
            "path": item["path"],
            "owner": item["owner"],
            "ownerFile": item["ownerFile"],
            "ok": item["key"] in actual_by_key,
        }
        for item in expected
    ]

    ok = (
        app is not None
        and ADMIN_RUNTIME_ROUTE_CONTRACT["status"] == "runtime-route-registration-v225"
        and count_check["ok"]
        and not missing_routes
        and not unexpected_routes
        and not duplicate_route_keys
        and all(item["ok"] for item in prefix_checks)
        and all(item["ok"] for item in method_path_checks)
    )

    return {
        "ok": ok,
        "version": ADMIN_RUNTIME_ROUTE_CONTRACT["version"],
        "status": ADMIN_RUNTIME_ROUTE_CONTRACT["status"],
        "policy": ADMIN_RUNTIME_ROUTE_CONTRACT["policy"],
        "contract": ADMIN_RUNTIME_ROUTE_CONTRACT,
        "sourceContractStatus": ADMIN_ROUTE_MODULE_CONTRACT["status"],
        "expectedRouteCount": len(expected),
        "actualRouteCount": len(actual),
        "countCheck": count_check,
        "prefixChecks": prefix_checks,
        "methodPathChecks": method_path_checks,
        "expectedRoutes": expected,
        "actualRoutes": actual,
        "missingRoutes": missing_routes,
        "unexpectedRoutes": unexpected_routes,
        "duplicateRouteKeys": duplicate_route_keys,
    }
