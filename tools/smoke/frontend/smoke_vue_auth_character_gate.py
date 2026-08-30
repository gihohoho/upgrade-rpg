from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VUE_APP = ROOT / "frontend" / "vue-app"

REQUIRED_FILES = [
    "src/api/contracts.ts",
    "src/api/http.ts",
    "src/api/authApi.ts",
    "src/api/accountApi.ts",
    "src/stores/account.ts",
    "src/components/account/AccountGate.vue",
    "src/components/account/AuthPanel.vue",
    "src/components/account/CharacterPanel.vue",
    "src/pages/GameShell.vue",
    "src/styles/base.css",
]


def read(relative_path: str) -> str:
    return (VUE_APP / relative_path).read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (VUE_APP / path).is_file()]
    if missing:
        raise AssertionError(f"Missing Vue account gate files: {missing}")

    http = read("src/api/http.ts")
    for marker in [
        "cache: 'no-store'",
        "Authorization: `Bearer ${options.token}`",
        "AbortController",
        "retryAfterSeconds",
    ]:
        assert_contains(http, marker, "typed API client")

    auth_api = read("src/api/authApi.ts")
    for route in [
        "/auth/register",
        "/auth/login",
        "/auth/me",
        "/auth/logout",
        "/auth/verify-email",
        "/auth/resend-verification",
    ]:
        assert_contains(auth_api, route, "auth API route")

    account_api = read("src/api/accountApi.ts")
    assert_contains(account_api, "/account/characters", "character API route")
    assert_contains(account_api, "encodeURIComponent(accountCharacterId)", "safe character delete path")
    assert_contains(account_api, "/game/master-data", "character option source")

    store = read("src/stores/account.ts")
    for marker in [
        "upgradeRpgAccountAccessToken",
        "upgradeRpgSelectedAccountCharacter",
        "EMAIL_ACTION_TOKEN_PATTERN",
        "SESSION_INVALID_CODES",
        "window.sessionStorage",
        "window.localStorage",
        "Promise.allSettled",
        "accountCharacterId",
        "slot.slotIndex",
        "stage.value = 'ready'",
        "stage.value = 'retry'",
        "request_body_too_large",
    ]:
        assert_contains(store, marker, "account Pinia store")
    if "confirm(" in store or "alert(" in store:
        raise AssertionError("Vue account store must not use browser confirm/alert")

    auth_panel = read("src/components/account/AuthPanel.vue")
    for marker in [
        'autocomplete="username"',
        'autocomplete="current-password"',
        'autocomplete="new-password"',
        'type="email"',
        "account.login",
        "account.register",
        "account.resendVerification",
        'role="status"',
    ]:
        assert_contains(auth_panel, marker, "auth panel")

    character_panel = read("src/components/account/CharacterPanel.vue")
    for marker in [
        'aria-label="캐릭터 슬롯 8개"',
        "v-for=\"slot in account.slots\"",
        "account.selectCharacter(slot)",
        "account.createCharacter",
        "account.deleteCharacter",
        'role="dialog"',
        'aria-modal="true"',
        "deleteConfirm !== deleteTarget?.accountCharacter?.name",
        "event.key === 'Escape'",
    ]:
        assert_contains(character_panel, marker, "character panel")
    if "confirm(" in character_panel or "alert(" in character_panel:
        raise AssertionError("Vue character panel must use the game modal, not browser confirm/alert")

    gate = read("src/components/account/AccountGate.vue")
    assert_contains(gate, "account.initialize()", "account restore on mount")
    assert_contains(gate, "account.stage === 'retry'", "network retry state")
    assert_contains(gate, "로그인 정보는 삭제하지 않았습니다", "network token preservation copy")
    assert_contains(gate, "게임 시작 준비 중", "runtime boot remains disabled")
    assert_contains(gate, "실제 게임 snapshot load와 자동 저장은 다음", "runtime boundary copy")

    game_shell = read("src/pages/GameShell.vue")
    assert_contains(game_shell, "<AccountGate />", "game shell account gate mount")

    css = read("src/styles/base.css")
    for selector in [
        ".account-card",
        ".account-tabs",
        ".character-grid",
        ".character-slot",
        ".account-modal-backdrop",
        ".account-button--danger",
    ]:
        assert_contains(css, selector, "account gate CSS")

    backend_auth = (ROOT / "backend/app/api/routes/auth.py").read_text(encoding="utf-8")
    backend_account = (ROOT / "backend/app/api/routes/account.py").read_text(encoding="utf-8")
    for route in ["/register", "/login", "/verify-email", "/resend-verification", "/me", "/logout"]:
        assert_contains(backend_auth, route, "backend auth contract")
    for route in ['@router.get("/characters")', '@router.post("/characters")', '@router.delete("/characters/{account_character_id}")']:
        assert_contains(backend_account, route, "backend character contract")

    print("OK: Vue auth and 8-slot character gate smoke passed")


if __name__ == "__main__":
    main()
