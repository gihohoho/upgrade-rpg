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


def _join_route_path(parent: str, child: str) -> str:
    """Join nested FastAPI/APIRouter prefixes without duplicating slashes."""

    parent = parent.strip()
    child = child.strip()
    if not parent:
        return child or ""
    if not child:
        return parent
    if child == parent or child.startswith(f"{parent}/"):
        return child
    return f"{parent.rstrip('/')}/{child.lstrip('/')}"


def _iter_runtime_route_nodes(container: Any) -> list[tuple[Any, str]]:
    """Flatten both classic and nested FastAPI router registrations.

    FastAPI/Starlette versions normally flatten ``include_router`` calls, but
    some local dependency combinations keep included routers as nested route
    containers. The runtime contract must inspect both forms.
    """

    flattened: list[tuple[Any, str]] = []
    visited: set[int] = set()

    def visit(node: Any, parent_path: str = "") -> None:
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)

        raw_path = getattr(node, "path", "")
        raw_prefix = getattr(node, "prefix", "")
        segment = raw_path if isinstance(raw_path, str) and raw_path else raw_prefix
        if not isinstance(segment, str):
            segment = ""
        full_path = _join_route_path(parent_path, segment)

        methods = (getattr(node, "methods", set()) or set()) - _IGNORED_METHODS
        if methods:
            flattened.append((node, full_path))

        child_groups: list[Any] = []
        direct_children = getattr(node, "routes", None)
        if direct_children is not None:
            child_groups.append(direct_children)
        nested_router = getattr(node, "router", None)
        nested_children = getattr(nested_router, "routes", None)
        if nested_children is not None and nested_children is not direct_children:
            child_groups.append(nested_children)

        # Starlette Mount and some FastAPI/Starlette combinations keep the
        # included application below ``node.app`` instead of exposing its
        # routes directly on the container. Windows environments using a
        # different dependency build can therefore present a valid nested
        # admin router as a path="" node whose children live at app.routes.
        nested_app = getattr(node, "app", None)
        app_children = getattr(nested_app, "routes", None)
        if app_children is not None and all(app_children is not group for group in child_groups):
            child_groups.append(app_children)
        app_router = getattr(nested_app, "router", None)
        app_router_children = getattr(app_router, "routes", None)
        if app_router_children is not None and all(app_router_children is not group for group in child_groups):
            child_groups.append(app_router_children)

        for children in child_groups:
            for child in list(children):
                visit(child, full_path)

    visit(container)
    return flattened



def _route_public_metadata(route: Any, path: str, method: str) -> dict[str, Any]:
    method_upper = method.upper()
    return {
        "method": method_upper,
        "path": path,
        "name": getattr(route, "name", None),
        "endpoint": getattr(getattr(route, "endpoint", None), "__name__", None),
        "statusCode": getattr(route, "status_code", None),
        "responseModel": getattr(route, "response_model", None),
        "responseDescription": getattr(route, "response_description", None),
        "includeInSchema": getattr(route, "include_in_schema", None),
        "key": f"{method_upper} {path}",
    }


def _append_entries(entries: list[dict[str, Any]], *, route: Any, path: str, source: str) -> None:
    methods = sorted((getattr(route, "methods", set()) or set()) - _IGNORED_METHODS)
    for method in methods:
        entries.append({
            "route": route,
            "source": source,
            **_route_public_metadata(route, path, method),
        })


def collect_admin_runtime_route_entries(app: FastAPI | None = None) -> tuple[list[dict[str, Any]], str]:
    """Collect concrete admin route objects using one shared fallback chain.

    Runtime, operation, response, and request metadata contracts must all inspect
    the same set of concrete APIRoute objects. FastAPI/Starlette versions can
    expose included routers in different shapes, so this collector tries the
    assembled app first, then the canonical api_router, then the concrete admin
    owner routers that hold the actual path-operation decorators.
    """

    base = f'{ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"]}{ADMIN_RUNTIME_ROUTE_CONTRACT["adminPrefix"]}'

    if app is not None:
        app_entries: list[dict[str, Any]] = []
        for route, path in _iter_runtime_route_nodes(app):
            if isinstance(path, str) and path.startswith(base):
                _append_entries(app_entries, route=route, path=path, source="fastapi-app")
        if app_entries:
            return sorted(app_entries, key=lambda item: item["key"]), "fastapi-app"

    from app.api.router import api_router

    fallback_entries: list[dict[str, Any]] = []
    api_prefix = str(ADMIN_RUNTIME_ROUTE_CONTRACT["apiPrefix"])
    for route, path in _iter_runtime_route_nodes(api_router):
        full_path = _join_route_path(api_prefix, path)
        if isinstance(full_path, str) and full_path.startswith(base):
            _append_entries(fallback_entries, route=route, path=full_path, source="canonical-api-router-fallback")
    if fallback_entries:
        return sorted(fallback_entries, key=lambda item: item["key"]), "canonical-api-router-fallback"

    from app.api.routes.admin_change_log_routes import router as change_log_router
    from app.api.routes.admin_master_data_routes import router as master_data_router
    from app.api.routes.admin_overview_snapshot_routes import router as overview_router

    owner_entries: list[dict[str, Any]] = []
    for owner_router in (overview_router, master_data_router, change_log_router):
        for route, path in _iter_runtime_route_nodes(owner_router):
            full_path = _join_route_path(base, path)
            if isinstance(full_path, str) and full_path.startswith(base):
                _append_entries(owner_entries, route=route, path=full_path, source="canonical-owner-routers-fallback")
    return sorted(owner_entries, key=lambda item: item["key"]), "canonical-owner-routers-fallback"


def _strip_runtime_route_object(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key != "route"}


def _runtime_admin_routes_with_source(app: FastAPI) -> tuple[list[dict[str, Any]], str]:
    entries, source = collect_admin_runtime_route_entries(app)
    return [_strip_runtime_route_object(entry) for entry in entries], source


def _runtime_admin_routes(app: FastAPI) -> list[dict[str, Any]]:
    """Backward-compatible list-only collector used by later contracts."""

    routes, _source = _runtime_admin_routes_with_source(app)
    return routes


def get_admin_runtime_route_contract_readiness(app: FastAPI | None = None) -> dict[str, Any]:
    """Compare static admin route ownership with routes registered on the FastAPI app.

    Static route checks catch misplaced decorators. This runtime check catches the
    next class of mistakes: routers not included, wrong prefixes, or duplicate
    FastAPI registrations that only show up after the application is assembled.
    """

    expected = sorted(_expected_runtime_routes(), key=lambda item: item["key"])
    actual, route_source = _runtime_admin_routes_with_source(app) if app is not None else ([], "none")

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
        "routeSource": route_source,
        "countCheck": count_check,
        "prefixChecks": prefix_checks,
        "methodPathChecks": method_path_checks,
        "expectedRoutes": expected,
        "actualRoutes": actual,
        "missingRoutes": missing_routes,
        "unexpectedRoutes": unexpected_routes,
        "duplicateRouteKeys": duplicate_route_keys,
    }
