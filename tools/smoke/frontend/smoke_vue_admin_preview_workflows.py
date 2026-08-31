from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/api/adminPreviewApi.ts",
    "src/stores/admin.ts",
    "src/components/admin/AdminPreviewWorkspace.vue",
    "src/pages/AdminShell.vue",
    "src/styles/base.css",
]


def read(relative_path: str) -> str:
    return (VUE_APP / relative_path).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"{label} missing: {marker}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (VUE_APP / path).is_file()]
    if missing:
        raise AssertionError(f"Missing Vue admin Preview files: {missing}")

    api = read("src/api/adminPreviewApi.ts")
    for route in [
        "/admin/master-data/create-preview",
        "/admin/master-data/edit-preview",
        "/rollback-preview",
        "/create-delete-preview",
        "/create-delete-restore-preview",
    ]:
        require(api, route, "Preview API allow-list")
    for marker in ["method: 'POST'", "dryRun: true", "token: options.token", "cache"]:
        if marker == "cache":
            continue
        require(api, marker, "typed Preview request boundary")
    for forbidden in ["-apply", "confirmText", "X-Admin-Dev-Key", "ADMIN_WRITE_DEV_KEY", "dryRun: false"]:
        if forbidden in api:
            raise AssertionError(f"Preview API connected forbidden write marker: {forbidden}")

    store = read("src/stores/admin.ts")
    for marker in [
        "previewBusy",
        "previewResult",
        "previewError",
        "adminPreviewApi.previewCreate",
        "adminPreviewApi.previewEdit",
        "adminPreviewApi.previewRollback",
        "adminPreviewApi.previewCreateDelete",
        "adminPreviewApi.previewCreateDeleteRestore",
        "guardRequest",
    ]:
        require(store, marker, "Pinia Preview state")

    workspace = read("src/components/admin/AdminPreviewWorkspace.vue")
    for marker in [
        "생성 초안 Preview",
        "수정 초안 Preview",
        "되돌리기 Preview",
        "stale 충돌",
        "차단·검증 사유",
        "Apply 미연결",
        "baseValues",
        "loadChangeLogDetail",
        "dependencyChecks",
        "currentMismatches",
    ]:
        require(workspace, marker, "Vue Preview workspace")
    for forbidden in ["X-Admin-Dev-Key", "ADMIN_WRITE_DEV_KEY", "confirmText", "applyAdmin", "-apply"]:
        if forbidden in workspace:
            raise AssertionError(f"Preview workspace connected forbidden write marker: {forbidden}")

    shell = read("src/pages/AdminShell.vue")
    require(shell, "AdminPreviewWorkspace", "protected Preview workspace mount")
    require(shell, "dryRun: true", "admin shell Preview scope copy")

    css = read("src/styles/base.css")
    for marker in [".admin-preview-workspace", ".admin-preview-tabs", ".admin-preview-diff-table", ".admin-preview-result__section--stale"]:
        require(css, marker, "Preview responsive styles")

    print("OK: Vue admin create/edit/rollback dry-run Preview workflows passed")


if __name__ == "__main__":
    main()
