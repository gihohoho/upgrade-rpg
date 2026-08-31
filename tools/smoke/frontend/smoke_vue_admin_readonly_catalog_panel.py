from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/components/AdminMasterDomainPanel.vue",
    "src/components/AdminMasterCatalogMiniPanel.vue",
    "src/components/AdminMasterDetailPanel.vue",
    "src/components/AdminMasterRelationsPanel.vue",
    "src/pages/AdminShell.vue",
    "src/styles/base.css",
    "docs/reference/frontend/VUE_ADMIN_READONLY_CATALOG.md",
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
    "createApply",
    "editApply",
    "rollbackApply",
]


def read(relative_path: str) -> str:
    base = ROOT if relative_path.startswith("docs/") else VUE_APP
    return (base / relative_path).read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def assert_read_only(relative_path: str) -> None:
    text = read(relative_path)
    for pattern in FORBIDDEN_MUTATION_PATTERNS:
        if pattern in text:
            raise AssertionError(f"Mutation pattern found in {relative_path}: {pattern}")


def main() -> None:
    missing = []
    for path in REQUIRED_FILES:
        base = ROOT if path.startswith("docs/") else VUE_APP
        if not (base / path).is_file():
            missing.append(path)
    if missing:
        raise AssertionError(f"Missing Vue admin read-only catalog files: {missing}")

    domain_panel = read("src/components/AdminMasterDomainPanel.vue")
    assert_contains(domain_panel, "admin.fetchMasterDomains()", "authenticated domain GET store call")
    assert_contains(domain_panel, "payload.domains", "domain list payload path")
    assert_contains(domain_panel, "defaultDomain", "default domain selection")
    assert_contains(domain_panel, "domain-selected", "domain selection event")
    assert_read_only("src/components/AdminMasterDomainPanel.vue")

    catalog_panel = read("src/components/AdminMasterCatalogMiniPanel.vue")
    assert_contains(catalog_panel, "admin.fetchMasterCatalog", "authenticated catalog GET store call")
    assert_contains(catalog_panel, "limit: 20", "catalog safe page size")
    assert_contains(catalog_panel, "query: appliedQuery.value", "catalog search query")
    assert_contains(catalog_panel, "enabled: props.supportsEnabledFilter", "catalog enabled query")
    assert_contains(catalog_panel, "page: page.value", "catalog page query")
    assert_contains(catalog_panel, "sort: sort.value", "catalog sort query")
    assert_contains(catalog_panel, "applySearch", "catalog search submit")
    assert_contains(catalog_panel, "resetFilters", "catalog reset filters")
    assert_contains(catalog_panel, "movePage", "catalog pagination")
    assert_contains(catalog_panel, "hasPrevPage", "catalog previous page contract")
    assert_contains(catalog_panel, "hasNextPage", "catalog next page contract")
    assert_contains(catalog_panel, "AbortController", "catalog stale request guard")
    assert_contains(catalog_panel, "row-selected", "catalog detail selection event")
    assert_contains(catalog_panel, "GET /admin/master-data/catalog", "catalog read-only scope text")
    assert_read_only("src/components/AdminMasterCatalogMiniPanel.vue")

    detail_panel = read("src/components/AdminMasterDetailPanel.vue")
    assert_contains(detail_panel, "admin.fetchMasterDetail", "authenticated detail GET store call")
    assert_contains(detail_panel, "{ domain: props.domain, rowId: props.rowId }", "detail query wrapper args")
    assert_contains(detail_panel, "payload.fields", "detail scalar fields payload")
    assert_contains(detail_panel, "payload.jsonFields", "detail JSON fields payload")
    assert_contains(detail_panel, "payload.assetFields", "detail asset fields payload")
    assert_contains(detail_panel, "payload.relationHints", "detail relation hints payload")
    assert_contains(detail_panel, "sanitizedJsonReturned", "detail sanitized JSON flag")
    assert_contains(detail_panel, "실제 축약 관계 목록은 아래 GET 관계 패널", "relations panel bridge text")
    assert_contains(detail_panel, "AbortController", "detail stale request guard")
    assert_read_only("src/components/AdminMasterDetailPanel.vue")

    admin_shell = read("src/pages/AdminShell.vue")
    assert_contains(admin_shell, "AdminMasterDomainPanel", "admin domain component mount")
    assert_contains(admin_shell, "AdminMasterCatalogMiniPanel", "admin catalog component mount")
    assert_contains(admin_shell, "AdminMasterDetailPanel", "admin detail component mount")
    assert_contains(admin_shell, "supports-enabled-filter", "domain enabled capability bridge")
    assert_contains(admin_shell, "searchable-fields", "domain search metadata bridge")
    assert_contains(admin_shell, "handleRowSelected", "admin selected row bridge")
    assert_contains(admin_shell, "준비 완료", "requirements meaningful summary")
    assert_contains(admin_shell, "Apply API/dev key 헤더/write는 계속 제외", "admin mutation exclusion note")
    assert_contains(admin_shell, "useAdminStore", "typed admin store boundary")
    assert_contains(admin_shell, "isAdmin=true", "server admin identity copy")
    assert_read_only("src/pages/AdminShell.vue")

    app = read("src/App.vue")
    assert_contains(app, "Upgrade RPG · v385", "Vue shell visible version")

    css = read("src/styles/base.css")
    assert_contains(css, ".admin-catalog-controls", "admin catalog controls CSS")
    assert_contains(css, ".admin-catalog-pagination", "admin catalog pagination CSS")
    assert_contains(css, ".admin-detail-grid", "admin detail grid CSS")
    assert_contains(css, ".admin-detail-json-card", "admin detail JSON CSS")

    docs = read("docs/reference/frontend/VUE_ADMIN_READONLY_CATALOG.md")
    assert_contains(docs, "v278", "catalog controls doc version")
    assert_contains(docs, "v279", "detail panel doc version")
    assert_contains(docs, "query", "catalog search query doc")
    assert_contains(docs, "enabled", "catalog enabled query doc")
    assert_contains(docs, "GET /api/v1/admin/master-data/detail", "detail endpoint doc")
    assert_contains(docs, "GET /api/v1/admin/master-data/relations", "relations endpoint note")
    assert_contains(docs, "Apply/write UI 연결", "write exclusion note")
    assert_contains(docs, "`.venv` 상태", "venv guidance")
    assert_contains(docs, "npm run dev", "Vue run guidance")

    print("OK: Vue admin read-only catalog controls/detail smoke passed")


if __name__ == "__main__":
    main()
