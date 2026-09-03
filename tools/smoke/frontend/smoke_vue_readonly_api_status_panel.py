from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/api/healthReadOnlyApi.js",
    "src/components/ReadOnlyApiStatusPanel.vue",
    "src/pages/AdminShell.vue",
    "src/pages/GameShell.vue",
    "src/styles/base.css",
    "docs/reference/frontend/VUE_READONLY_API_CLIENT.md",
    "docs/reference/frontend/VUE_APP_SHELL.md",
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


def assert_no_mutation_patterns(relative_path: str) -> None:
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
        raise AssertionError(f"Missing Vue read-only API status panel files: {missing}")

    package = json.loads((VUE_APP / "package.json").read_text(encoding="utf-8"))
    if package.get("version") != "0.0.0-v392":
        raise AssertionError("Vue package version must be 0.0.0-v392")

    health_api = read("src/api/healthReadOnlyApi.js")
    assert_contains(health_api, "HEALTH_READONLY_ROUTES", "health API route import")
    assert_contains(health_api, "fetchHealth", "health API wrapper")
    assert_contains(health_api, "fetchDbHealth", "DB health wrapper prepared but not auto-called")
    assert_no_mutation_patterns("src/api/healthReadOnlyApi.js")

    api_index = read("src/api/index.js")
    assert_contains(api_index, "healthReadOnlyApi", "health API export")

    panel = read("src/components/ReadOnlyApiStatusPanel.vue")
    assert_contains(panel, "onMounted", "status panel automatic check")
    assert_contains(panel, "loading", "loading status")
    assert_contains(panel, "success", "success status")
    assert_contains(panel, "error", "error status")
    assert_contains(panel, "다시 확인", "retry button label")
    assert_contains(panel, "check.summarize", "custom status summarizer support")
    assert_no_mutation_patterns("src/components/ReadOnlyApiStatusPanel.vue")

    admin_shell = read("src/pages/AdminShell.vue")
    assert_contains(admin_shell, "ReadOnlyApiStatusPanel", "admin shell status panel")
    assert_contains(admin_shell, "healthReadOnlyApi.fetchHealth", "admin health check")
    assert_contains(admin_shell, "admin.fetchRequirements", "authenticated admin requirements check")
    assert_contains(admin_shell, "준비 완료", "admin requirements meaningful status")
    assert_contains(admin_shell, "Apply API/dev key 헤더/write", "admin write exclusion note")
    assert_no_mutation_patterns("src/pages/AdminShell.vue")

    game_shell = read("src/pages/GameShell.vue")
    assert_contains(game_shell, "AccountGate", "game shell account gate")

    css = read("src/styles/base.css")
    assert_contains(css, ".api-status-panel", "status panel CSS")
    assert_contains(css, "data-status=\"success\"", "success status CSS")
    assert_contains(css, "data-status=\"error\"", "error status CSS")

    docs = read("docs/reference/frontend/VUE_READONLY_API_CLIENT.md")
    assert_contains(docs, "v272", "read-only API doc version")
    assert_contains(docs, "/health", "doc health endpoint")
    assert_contains(docs, "/admin/requirements", "doc admin requirements endpoint")
    assert_contains(docs, "Apply/write와 dev key는 계속 제외", "doc write exclusion")
    assert_contains(docs, "`.venv` 상태", "doc venv guidance")
    assert_contains(docs, "npm run dev", "doc npm dev guidance")

    print("OK: Vue read-only API status panel smoke passed")


if __name__ == "__main__":
    main()
