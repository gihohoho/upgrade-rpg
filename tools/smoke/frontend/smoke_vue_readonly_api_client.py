from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/api/config.js",
    "src/api/readOnlyRoutes.js",
    "src/api/readOnlyClient.js",
    "src/api/adminReadOnlyApi.js",
    "src/api/gameReadOnlyApi.js",
    "src/api/index.js",
    "src/api/README.md",
    "src/pages/AdminShell.vue",
    "src/pages/GameShell.vue",
    "docs/reference/frontend/VUE_READONLY_API_CLIENT.md",
]

EXPECTED_ADMIN_ROUTES = [
    "/admin/requirements",
    "/admin/overview",
    "/admin/save-snapshots",
    "/admin/master-data/domains",
    "/admin/master-data/catalog",
    "/admin/master-data/create-blueprint",
    "/admin/master-data/detail",
    "/admin/master-data/relations",
    "/admin/change-logs",
    "/admin/change-logs/{changeLogId}",
]

EXPECTED_GAME_ROUTES = [
    "/game/master-data",
    "/game/load",
    "/game/save-slots",
]

FORBIDDEN_ROUTE_FRAGMENTS = [
    "/game/save'",
    '"/game/save"',
    "edit-preview",
    "edit-apply",
    "create-preview",
    "create-apply",
    "rollback-preview",
    "rollback-apply",
    "create-delete-preview",
    "create-delete-apply",
    "create-delete-restore-preview",
    "create-delete-restore-apply",
    "change-preview",
]

FORBIDDEN_MUTATION_PATTERNS = [
    "method: 'POST'",
    'method: "POST"',
    "method: 'PUT'",
    'method: "PUT"',
    "method: 'PATCH'",
    'method: "PATCH"',
    "method: 'DELETE'",
    'method: "DELETE"',
    ".post(",
    ".put(",
    ".patch(",
    ".delete(",
]


def read(path: str) -> str:
    base = ROOT if path.startswith("docs/") else VUE_APP
    return (base / path).read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def main() -> None:
    missing = []
    for path in REQUIRED_FILES:
        base = ROOT if path.startswith("docs/") else VUE_APP
        if not (base / path).is_file():
            missing.append(path)
    if missing:
        raise AssertionError(f"Missing Vue read-only API client files: {missing}")

    package = json.loads((VUE_APP / "package.json").read_text(encoding="utf-8"))
    if package.get("version") != "0.0.0-v379":
        raise AssertionError("Vue package version must be 0.0.0-v379")

    config = read("src/api/config.js")
    assert_contains(config, "http://127.0.0.1:8000/api/v1", "default API base URL")
    assert_contains(config, "VITE_API_BASE_URL", "future Vite API base URL hook")

    routes = read("src/api/readOnlyRoutes.js")
    assert_contains(routes, "API_READONLY_METHOD = 'GET'", "GET-only method constant")
    for route in EXPECTED_ADMIN_ROUTES + EXPECTED_GAME_ROUTES:
        assert_contains(routes, route, "read-only route map")

    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        if fragment in routes:
            raise AssertionError(f"Mutation route must not be listed in read-only route map yet: {fragment}")

    api_files = [
        "src/api/readOnlyClient.js",
        "src/api/adminReadOnlyApi.js",
        "src/api/gameReadOnlyApi.js",
        "src/api/index.js",
    ]
    for api_file in api_files:
        text = read(api_file)
        for pattern in FORBIDDEN_MUTATION_PATTERNS:
            if pattern in text:
                raise AssertionError(f"Mutation request pattern found in {api_file}: {pattern}")

    client = read("src/api/readOnlyClient.js")
    assert_contains(client, "method: 'GET'", "read-only fetch method")
    assert_contains(client, "Accept: 'application/json'", "JSON accept header")
    assert_contains(client, "ReadOnlyApiError", "read-only API error type")

    admin_api = read("src/api/adminReadOnlyApi.js")
    assert_contains(admin_api, "fetchMasterCatalog", "admin master catalog wrapper")
    assert_contains(admin_api, "fetchChangeLogDetail", "admin change log detail wrapper")
    assert_contains(admin_api, "sort = 'id_asc'", "admin catalog safe default sort")
    assert_contains(admin_api, "query: { domain, id: rowId }", "master detail rowId-to-id query translation")
    assert_contains(admin_api, "query: { domain, id: rowId, limit }", "master relations rowId-to-id query translation")
    if "query: { domain, rowId }" in admin_api or "query: { domain, rowId, limit }" in admin_api:
        raise AssertionError("Admin read-only API must not send rowId as a backend query name")

    game_api = read("src/api/gameReadOnlyApi.js")
    assert_contains(game_api, "fetchMasterData", "game master data wrapper")
    assert_contains(game_api, "includeAssets = false", "safe asset default")
    assert_contains(game_api, "fetchSaveSlots", "game save slot wrapper")

    for shell in ["src/pages/AdminShell.vue", "src/pages/GameShell.vue"]:
        text = read(shell)
        assert_contains(text, "@/api", f"{shell} imports API route constants")
        assert_contains(text, "GET", f"{shell} labels read-only route method")

    docs = read("docs/reference/frontend/VUE_READONLY_API_CLIENT.md")
    assert_contains(docs, "v272", "read-only API client doc version")
    assert_contains(docs, "POST /game/save", "doc excluded write route")
    assert_contains(docs, "`.venv` 상태", "doc venv guidance")
    assert_contains(docs, "npm install", "doc npm install guidance")
    assert_contains(docs, "npm run dev", "doc npm run dev guidance")

    if re.search(r"실제.*write.*추가", docs) and "아직" not in docs:
        raise AssertionError("Docs must keep write connections explicitly out of v272")

    print("OK: Vue read-only API client smoke passed")


if __name__ == "__main__":
    main()
