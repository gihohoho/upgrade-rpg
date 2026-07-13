from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/components/AdminMasterDomainPanel.vue",
    "src/components/AdminMasterCatalogMiniPanel.vue",
    "src/pages/AdminShell.vue",
    "src/styles/base.css",
    "docs/current/VUE_ADMIN_READONLY_CATALOG.md",
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
    assert_contains(domain_panel, "adminReadOnlyApi.fetchMasterDomains()", "domain GET wrapper call")
    assert_contains(domain_panel, "response?.payload", "domain response payload parsing")
    assert_contains(domain_panel, "payload.domains", "domain list payload path")
    assert_contains(domain_panel, "defaultDomain", "default domain selection")
    assert_contains(domain_panel, "status === 'loading'", "domain loading state")
    assert_contains(domain_panel, "status === 'error'", "domain error state")
    assert_contains(domain_panel, "status === 'empty'", "domain empty state")
    assert_contains(domain_panel, "status === 'success'", "domain success state")
    assert_contains(domain_panel, "domain-selected", "domain selection event")
    assert_read_only("src/components/AdminMasterDomainPanel.vue")

    catalog_panel = read("src/components/AdminMasterCatalogMiniPanel.vue")
    assert_contains(catalog_panel, "adminReadOnlyApi.fetchMasterCatalog", "catalog GET wrapper call")
    assert_contains(catalog_panel, "limit: 20", "catalog safe first-page limit")
    assert_contains(catalog_panel, "page: 1", "catalog first page")
    assert_contains(catalog_panel, "sort: 'id_asc'", "catalog stable sort")
    assert_contains(catalog_panel, "payload.columns", "catalog columns payload path")
    assert_contains(catalog_panel, "payload.rows", "catalog rows payload path")
    assert_contains(catalog_panel, "AbortController", "catalog stale request guard")
    assert_contains(catalog_panel, "watch(", "catalog domain watcher")
    assert_contains(catalog_panel, "검색·페이지 이동·상세·관계·수정 기능은 아직 연결하지 않습니다", "catalog scope note")
    assert_read_only("src/components/AdminMasterCatalogMiniPanel.vue")

    admin_shell = read("src/pages/AdminShell.vue")
    assert_contains(admin_shell, "AdminMasterDomainPanel", "admin domain component mount")
    assert_contains(admin_shell, "AdminMasterCatalogMiniPanel", "admin catalog component mount")
    assert_contains(admin_shell, "handleDomainSelected", "admin selected domain bridge")
    assert_contains(admin_shell, "Preview/Apply/write", "admin mutation exclusion note")
    assert_read_only("src/pages/AdminShell.vue")

    app = read("src/App.vue")
    assert_contains(app, "Upgrade RPG v277", "Vue shell visible version")

    css = read("src/styles/base.css")
    assert_contains(css, ".admin-readonly-panel", "admin read-only panel CSS")
    assert_contains(css, ".admin-domain-list", "admin domain list CSS")
    assert_contains(css, ".admin-catalog-table", "admin catalog table CSS")

    docs = read("docs/current/VUE_ADMIN_READONLY_CATALOG.md")
    assert_contains(docs, "v276", "domain panel doc version")
    assert_contains(docs, "v277", "catalog panel doc version")
    assert_contains(docs, "payload.domains", "domain response contract note")
    assert_contains(docs, "limit=20", "catalog request boundary")
    assert_contains(docs, "Preview/Apply/write", "write exclusion note")
    assert_contains(docs, "`.venv` 상태", "venv guidance")
    assert_contains(docs, "npm run dev", "Vue run guidance")

    print("OK: Vue admin read-only domain/catalog mini panels smoke passed")


if __name__ == "__main__":
    main()
