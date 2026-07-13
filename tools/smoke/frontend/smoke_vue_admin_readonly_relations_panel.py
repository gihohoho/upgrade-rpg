from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/components/AdminMasterRelationsPanel.vue",
    "src/components/AdminMasterDetailPanel.vue",
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
        raise AssertionError(f"Missing Vue relations files: {missing}")

    relations = read("src/components/AdminMasterRelationsPanel.vue")
    assert_contains(relations, "adminReadOnlyApi.fetchMasterRelations", "relations GET wrapper call")
    assert_contains(relations, "{ domain: props.domain, rowId: props.rowId, limit: 20 }", "relations safe query args")
    assert_contains(relations, "payload.groups", "relations groups payload")
    assert_contains(relations, "group.columns", "relations group columns")
    assert_contains(relations, "group.rows", "relations group rows")
    assert_contains(relations, "limited", "relations limited indicator")
    assert_contains(relations, "AbortController", "relations stale request guard")
    assert_contains(relations, "related-row-selected", "related row selection event")
    assert_contains(relations, "DB나 관계 값을 수정하지 않습니다", "relations read-only boundary text")
    assert_read_only("src/components/AdminMasterRelationsPanel.vue")

    detail = read("src/components/AdminMasterDetailPanel.vue")
    assert_contains(detail, "navigationDepth", "detail history depth prop")
    assert_contains(detail, "이전 상세로", "detail back button")
    assert_contains(detail, "back-selection", "detail back event")
    assert_read_only("src/components/AdminMasterDetailPanel.vue")

    shell = read("src/pages/AdminShell.vue")
    assert_contains(shell, "AdminMasterRelationsPanel", "relations panel mount")
    assert_contains(shell, "selectionHistory", "selection history state")
    assert_contains(shell, "handleRelatedRowSelected", "related selection handler")
    assert_contains(shell, "handleBackSelection", "related selection back handler")
    assert_contains(shell, "관계 편집과 Preview/Apply/write는 계속 제외", "write exclusion note")
    assert_read_only("src/pages/AdminShell.vue")

    css = read("src/styles/base.css")
    assert_contains(css, ".admin-relations-groups", "relations groups CSS")
    assert_contains(css, ".admin-relations-group__header", "relations header CSS")
    assert_contains(css, ".admin-relations-group__limited", "relations limited CSS")

    app = read("src/App.vue")
    assert_contains(app, "Upgrade RPG v281", "Vue shell visible version")

    docs = read("docs/current/VUE_ADMIN_READONLY_CATALOG.md")
    assert_contains(docs, "v280", "relations panel doc version")
    assert_contains(docs, "v281", "related detail navigation doc version")
    assert_contains(docs, "GET /api/v1/admin/master-data/relations", "relations endpoint doc")
    assert_contains(docs, "이전 상세로", "history navigation doc")
    assert_contains(docs, "Preview/Apply/write", "write exclusion doc")

    print("OK: Vue admin read-only relations/navigation smoke passed")


if __name__ == "__main__":
    main()
