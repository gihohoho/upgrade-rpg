from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"


def read(relative_path: str) -> str:
    return (VUE_APP / relative_path).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"{label} missing: {marker}")


def reject(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"{label} connected forbidden write marker: {marker}")


def main() -> None:
    component_path = VUE_APP / "src/components/admin/AdminApplyConfirmationGate.vue"
    if not component_path.is_file():
        raise AssertionError("Apply confirmation gate component is missing")

    gate = read("src/components/admin/AdminApplyConfirmationGate.vue")
    for marker in [
        'role="dialog"',
        'aria-modal="true"',
        "Preview 다시 검증",
        "서버가 지정한 확인 문구",
        "현재 비밀번호",
        "관리자 dev key",
        "미전송",
        "저장·로그·네트워크 전송 없이",
        'data-testid="admin-apply-locked-button"',
        "disabled",
        "clearSensitiveInputs",
        "window.removeEventListener('keydown', handleKeydown)",
    ]:
        require(gate, marker, "confirmation gate")
    for forbidden in ["requestApi", "fetch(", "localStorage", "sessionStorage", "/master-data/create-apply", "/master-data/edit-apply", "/rollback-apply", "/create-delete-apply", "/create-delete-restore-apply", "X-Admin-Dev-Key"]:
        reject(gate, forbidden, "confirmation gate")

    workspace = read("src/components/admin/AdminPreviewWorkspace.vue")
    for marker in [
        "AdminApplyConfirmationGate",
        "confirmTextRequired",
        "revalidateLatestPreview",
        "fingerprintPayload",
        "window.crypto.subtle.digest('SHA-256'",
        "lastPreviewRequest",
        "invalidatePreview",
        "Apply 쓰기 잠금",
    ]:
        require(workspace, marker, "Preview confirmation orchestration")
    for forbidden in ["X-Admin-Dev-Key", "ADMIN_WRITE_DEV_KEY", "dryRun: false", "/master-data/create-apply", "/master-data/edit-apply", "/rollback-apply", "/create-delete-apply", "/create-delete-restore-apply"]:
        reject(workspace, forbidden, "Preview confirmation orchestration")

    api = read("src/api/adminPreviewApi.ts")
    require(api, "confirmTextRequired?: string", "typed Preview response")
    require(api, "dryRun: true", "Preview-only request")
    for forbidden in ["X-Admin-Dev-Key", "ADMIN_WRITE_DEV_KEY", "dryRun: false", "/master-data/create-apply", "/master-data/edit-apply", "/rollback-apply", "/create-delete-apply", "/create-delete-restore-apply"]:
        reject(api, forbidden, "Preview API")

    styles = read("src/styles/base.css")
    for marker in [
        ".admin-preview-apply-preparation",
        ".admin-apply-gate-backdrop",
        ".admin-apply-gate__steps",
        ".admin-apply-gate__field-grid",
        "@media (max-width: 720px)",
    ]:
        require(styles, marker, "confirmation responsive styles")

    package = read("package.json")
    app = read("src/App.vue")
    require(package, '"version": "0.0.0-v393"', "Vue package version")
    require(app, "Upgrade RPG · v393", "Vue shell version")

    print("OK: Vue admin Apply confirmation gates remain preview-only and write-locked")


if __name__ == "__main__":
    main()
