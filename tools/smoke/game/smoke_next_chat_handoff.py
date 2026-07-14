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
        "backend/alembic/script.py.mako",
        "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py",
        "tools/check_postgres_backup_restore_preflight.py",
        "tools/create_postgres_backup.py",
        "tools/create_postgres_restore_rehearsal_database.py",
        "tools/restore_postgres_rehearsal_database.py",
        "tools/create_postgres_migration_test_database.py",
        "tools/create_postgres_initial_alembic_revision.py",
        "tools/upgrade_postgres_migration_test_database.py",
        "tools/downgrade_postgres_migration_test_database.py",
        "tools/reupgrade_postgres_migration_test_database.py",
        "tools/check_postgres_source_baseline_stamp_preflight.py",
        "tools/stamp_postgres_restore_rehearsal_database.py",
        "tools/smoke/backend/smoke_postgres_initial_alembic_revision_creation.py",
        "tools/smoke/backend/smoke_postgres_initial_alembic_revision_manual_review.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_upgrade.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_downgrade.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_roundtrip.py",
        "tools/smoke/backend/smoke_postgres_source_baseline_stamp_preflight.py",
        "tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py",
        "docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md",
        "docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md",
        "docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md",
        "docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md",
        "docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md",
        "docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md",
        "docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md",
        "docs/current/review/v295_initial_schema.manual-review.json",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "rpg_v302_postgres_restore_rehearsal_stamp_guard_ready.zip",
        "v302.postgres-restore-rehearsal-stamp-head-guard-ready",
        "backend/.venv",
        "stamp_postgres_restore_rehearsal_database.py --inspect",
        "v295_initial_schema",
        "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa",
        "rpg_game_restore_rehearsal_v290",
        "first/second upgrade signatures: identical",
        "ready-for-separate-restore-rehearsal-stamp-execution-approval",
        "row-content SHA-256",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "22 tables / 748 rows",
        "public tables 23",
        "migration current revision v295_initial_schema",
        "v301 사용자 실제 결과",
        "ready-for-separate-restore-rehearsal-stamp-approval",
        "stamp_postgres_restore_rehearsal_database.py",
        "fake subprocess",
    )
    assert_contains(
        "README.md",
        "v302.postgres-restore-rehearsal-stamp-head-guard-ready",
        "stamp_postgres_restore_rehearsal_database.py",
        "v295_initial_schema",
        "row-content SHA-256",
    )
    assert_contains(
        "docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md",
        "수동 검토 통과",
        "22 / 22",
        "209 / 209",
        "42 / 42",
        "user_profiles.farm_atk_bonus",
        "exact reverse create order",
    )
    assert_contains(
        "docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md",
        "rpg_game_migration_empty_v290",
        "upgrade head",
        "public tables: 23",
        "differences: 0",
        "사용자 PC 실제 실행 결과",
    )
    assert_contains(
        "docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md",
        "rpg_game_migration_empty_v290",
        "downgrade base",
        "application tables remaining: 0",
        "differences: 22",
        "v295_initial_schema.upgrade-v298.json",
    )
    assert_contains(
        "docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md",
        "v298 first upgrade",
        "v299 downgrade",
        "upgrade head",
        "first/second upgrade signatures: identical",
        "v295_initial_schema.roundtrip-upgrade-v300.json",
    )
    assert_contains(
        "docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md",
        "v301",
        "읽기 전용",
        "ready-for-separate-restore-rehearsal-stamp-approval",
        "rpg_game_restore_rehearsal_v290",
        "source rpg_game stamp/upgrade/downgrade",
        "사용자 PC 실제 결과",
    )
    assert_contains(
        "docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md",
        "v302",
        "rpg_game_restore_rehearsal_v290",
        "v295_initial_schema",
        "row-content SHA-256",
        "alembic_version",
        "별도 승인",
    )
    assert_contains(
        ".gitignore",
        "/local-backups/",
        "/local-review-artifacts/",
    )
    assert_contains(
        ".dockerignore",
        "local-backups/",
        "local-review-artifacts/",
    )

    if read_required("NEXT_CHAT_PROMPT.md") != read_required("docs/handoff/NEXT_CHAT_PROMPT.md"):
        raise AssertionError("root/docs handoff prompt copies differ")
    if read_required("NEXT_CHAT_HANDOFF.md") != read_required("docs/handoff/NEXT_CHAT_HANDOFF.md"):
        raise AssertionError("root/docs handoff copies differ")
    if read_required("docs/CURRENT_STATUS.md") != read_required("docs/current/CURRENT_STATUS.md"):
        raise AssertionError("current status copies differ")
    if read_required("docs/PROJECT_STRUCTURE.md") != read_required("docs/current/PROJECT_STRUCTURE.md"):
        raise AssertionError("project structure copies differ")

    print("next chat handoff smoke test passed")


if __name__ == "__main__":
    main()
