from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "package.json",
    "index.html",
    "vite.config.js",
    "README.md",
    "src/main.js",
    "src/App.vue",
    "src/router/index.js",
    "src/pages/AdminShell.vue",
    "src/pages/GameShell.vue",
    "src/components/ShellCard.vue",
    "src/styles/base.css",
    "src/api/README.md",
    "src/app/README.md",
    "src/stores/README.md",
]

FORBIDDEN_PATTERNS = [
    "../src/",
    "../../src/",
    "../../../src/",
    "../../../../src/",
]


def read(relative_path: str) -> str:
    return (VUE_APP / relative_path).read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (VUE_APP / path).is_file()]
    if missing:
        raise AssertionError(f"Missing Vue shell files: {missing}")

    package = json.loads(read("package.json"))
    if package.get("private") is not True:
        raise AssertionError("Vue package must stay private")

    expected_dependencies = ["vue", "vue-router", "vite", "@vitejs/plugin-vue"]
    dependencies = package.get("dependencies", {})
    for dependency in expected_dependencies:
        if dependency not in dependencies:
            raise AssertionError(f"Missing Vue dependency: {dependency}")

    scripts = package.get("scripts", {})
    for script in ["dev", "build", "preview"]:
        if script not in scripts:
            raise AssertionError(f"Missing npm script: {script}")

    router = read("src/router/index.js")
    assert_contains(router, "path: '/game'", "router game route")
    assert_contains(router, "path: '/admin'", "router admin route")
    assert_contains(router, "legacyEntry: 'index.html'", "game legacy entry metadata")
    assert_contains(router, "legacyEntry: 'admin.html'", "admin legacy entry metadata")

    app_vue = read("src/App.vue")
    assert_contains(app_vue, "<RouterLink to=\"/game\">", "App game navigation")
    assert_contains(app_vue, "<RouterLink to=\"/admin\">", "App admin navigation")
    assert_contains(app_vue, "<RouterView />", "App router view")

    for vue_file in ["src/pages/AdminShell.vue", "src/pages/GameShell.vue"]:
        text = read(vue_file)
        assert_contains(text, "ShellCard", vue_file)
        assert_contains(text, "legacy", vue_file)

    all_source_files = list((VUE_APP / "src").rglob("*"))
    for source_file in all_source_files:
        if not source_file.is_file():
            continue
        text = source_file.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                raise AssertionError(f"Vue shell must not import root legacy src directly yet: {source_file}")

    project_structure = (ROOT / "docs" / "current" / "PROJECT_STRUCTURE.md").read_text(encoding="utf-8")
    assert_contains(project_structure, "frontend/vue-app/", "PROJECT_STRUCTURE Vue app path")
    assert_contains(project_structure, "v270", "PROJECT_STRUCTURE version")

    transition_plan = (ROOT / "docs" / "current" / "VUE_FASTAPI_DB_TRANSITION_PLAN.md").read_text(encoding="utf-8")
    assert_contains(transition_plan, "Vue shell", "transition plan Vue shell note")
    assert_contains(transition_plan, "npm install", "transition plan install guide")

    if re.search(r"route path.*변경", transition_plan) and "변경하지 않았" not in transition_plan:
        raise AssertionError("Transition plan must explicitly preserve route paths")

    print("OK: Vue shell structure smoke passed")


if __name__ == "__main__":
    main()
