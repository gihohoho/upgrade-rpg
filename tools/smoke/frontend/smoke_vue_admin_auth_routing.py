from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/stores/pinia.ts",
    "src/stores/admin.ts",
    "src/components/admin/AdminAccessGate.vue",
    "src/pages/AdminAccessPage.vue",
    "src/pages/AdminShell.vue",
    "src/router/index.ts",
    "src/api/readOnlyClient.js",
]


def read(relative_path: str) -> str:
    return (VUE_APP / relative_path).read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (VUE_APP / path).is_file()]
    if missing:
        raise AssertionError(f"Missing Vue admin auth files: {missing}")

    router = read("src/router/index.ts")
    for marker in [
        "path: '/admin'",
        "requiresAdmin: true",
        "path: '/admin/access'",
        "router.beforeEach",
        "await admin.checkAccess()",
        "name: 'admin-access'",
    ]:
        assert_contains(router, marker, "admin route guard")

    account = read("src/stores/account.ts")
    for marker in ["ensureSession", "loginSession", "accessToken", "isAdmin", "invalidateSession", "markAdminDenied"]:
        assert_contains(account, marker, "account session boundary")

    admin = read("src/stores/admin.ts")
    for marker in [
        "defineStore('admin'",
        "account.ensureSession()",
        "account.isAdmin",
        "token: account.accessToken",
        "status === 401 || status === 403",
        "fetchMasterDomains",
        "fetchMasterCatalog",
        "fetchMasterDetail",
        "fetchMasterRelations",
    ]:
        assert_contains(admin, marker, "typed admin store")

    client = read("src/api/readOnlyClient.js")
    assert_contains(client, "cache: 'no-store'", "admin GET no-store policy")
    assert_contains(client, "Authorization: `Bearer ${token}`", "admin GET bearer header")

    gate = read("src/components/admin/AdminAccessGate.vue")
    for marker in [
        'autocomplete="username"',
        'autocomplete="current-password"',
        "admin.accessStage === 'forbidden'",
        "관리자 컴포넌트를 렌더링하지 않으며",
        "실제 변경 기능과 dev key는 아직 연결하지 않습니다",
    ]:
        assert_contains(gate, marker, "admin access gate")

    shell = read("src/pages/AdminShell.vue")
    assert_contains(shell, '<script setup lang="ts">', "typed admin shell")
    assert_contains(shell, "admin.fetchRequirements()", "authenticated requirements call")
    assert_contains(shell, "stage !== 'ready'", "runtime access loss redirect")
    if "AdminAccessGate" in shell:
        raise AssertionError("AdminShell must not render the access gate inside the protected admin component tree")

    combined = "\n".join(read(path) for path in REQUIRED_FILES)
    for forbidden in ["X-Admin-Dev-Key", "ADMIN_WRITE_DEV_KEY", "create-apply", "edit-apply", "rollback-apply"]:
        if forbidden in combined:
            raise AssertionError(f"Vue admin auth stage must not connect admin write boundary: {forbidden}")

    print("OK: Vue admin auth routing and Bearer GET boundary smoke passed")


if __name__ == "__main__":
    main()
