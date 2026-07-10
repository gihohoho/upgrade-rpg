from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read_required(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        raise AssertionError(f"missing required handoff file: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(relative_path: str, *needles: str) -> None:
    text = read_required(relative_path)
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{relative_path} missing expected text: {needle}")


def main() -> None:
    required_files = [
        "NEXT_CHAT_PROMPT.md",
        "NEXT_CHAT_HANDOFF.md",
        "README.md",
        "README_BACKEND_READY.md",
        "docs/README.md",
        "docs/CURRENT_STATUS.md",
        "docs/NEXT_STEPS.md",
        "docs/PROJECT_STRUCTURE.md",
        "docs/NEXT_CHAT_START_GUIDE.md",
        "docs/BACKEND_ADMIN_SERVICE_MAP.md",
        "docs/BACKEND_ADMIN_CHANGE_LOG_SCHEMA_GUARD.md",
        "backend/app/services/admin/README.md",
        "src/api/admin/README.md",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "v202 backend admin change log service split",
        "backend/app/services/admin/admin_change_log_service.py",
        "rpg_v201_2_change_logs_500_hotfix.zip",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "v201.2 admin change log schema guard hotfix",
        "v202 backend admin change log service split",
        "bash tools/run_smoke_core.sh",
    )
    assert_contains(
        "docs/README.md",
        "Docs Index",
        "지금 자주 보는 문서",
        "보관 문서",
        "docs/archive/stage-notes/",
    )
    assert_contains(
        "docs/BACKEND_ADMIN_SERVICE_MAP.md",
        "AdminChangeLogService",
        "list_admin_change_logs",
        "apply_admin_change_log_rollback",
    )
    assert_contains(
        "docs/NEXT_CHAT_START_GUIDE.md",
        "checkAdminReadOnlyPageReady().version",
        "create-lifecycle-extracted-v201",
    )

    print("next chat handoff smoke test passed")


if __name__ == "__main__":
    main()
