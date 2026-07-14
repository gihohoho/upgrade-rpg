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
        "docs/current/CURRENT_STATUS.md",
        "docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md",
        "docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md",
        "docs/current/POSTGRES_BACKUP_RESTORE_PREP.md",
        "tools/check_postgres_backup_restore_preflight.py",
        "tools/create_postgres_backup.py",
        "tools/create_postgres_restore_rehearsal_database.py",
        "docs/current/POSTGRES_BACKUP_CREATION.md",
        "docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "rpg_v292_postgres_restore_rehearsal_database_creation_ready.zip",
        "v292.postgres-restore-rehearsal-database-create-tool",
        "backend/.venv",
        "create_postgres_restore_rehearsal_database.py --execute",
        "restore-rehearsal-database-created-empty-and-verified",
        "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "structurally-equivalent",
        "748",
        "backup-created-and-verified",
        "rpg_game_restore_rehearsal_v290",
        "target public tables: 0",
        "pg_restore",
    )
    assert_contains(
        "README.md",
        "v292.postgres-restore-rehearsal-database-create-tool",
        "create_postgres_restore_rehearsal_database.py",
        "template0",
        "local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump",
    )
    assert_contains(
        "docs/NEXT_CHAT_START_GUIDE.md",
        "backend/.venv",
        "create_postgres_restore_rehearsal_database.py --execute",
        "run_smoke_core.sh",
    )
    assert_contains(
        "docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md",
        "target DB 존재 여부 확인",
        "public table 0개",
        "SHA-256",
        "별도 승인",
    )

    print("next chat handoff smoke test passed")


if __name__ == "__main__":
    main()
