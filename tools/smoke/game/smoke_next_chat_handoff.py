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
        "tools/stamp_postgres_source_database.py",
        "tools/check_postgres_baseline_completion_state.py",
        "tools/check_postgres_next_revision_preflight.py",
        "tools/smoke/backend/smoke_postgres_initial_alembic_revision_creation.py",
        "tools/smoke/backend/smoke_postgres_initial_alembic_revision_manual_review.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_upgrade.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_downgrade.py",
        "tools/smoke/backend/smoke_postgres_migration_test_database_roundtrip.py",
        "tools/smoke/backend/smoke_postgres_source_baseline_stamp_preflight.py",
        "tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py",
        "tools/smoke/backend/smoke_postgres_source_baseline_stamp_guard.py",
        "tools/smoke/backend/smoke_postgres_baseline_completion_state.py",
        "tools/smoke/backend/smoke_postgres_next_revision_preflight.py",
        "tools/check_postgres_deployment_runtime_readiness.py",
        "tools/smoke/backend/smoke_postgres_deployment_runtime_readiness.py",
        "tools/check_runtime_config_hardening.py",
        "tools/smoke/backend/smoke_runtime_config_hardening.py",
        "backend/Dockerfile",
        "deploy/docker-compose.production.yml",
        "deploy/README.md",
        "docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md",
        "docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md",
        "docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md",
        "docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md",
        "docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md",
        "docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md",
        "docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md",
        "docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md",
        "docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md",
        "docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md",
        "docs/current/POSTGRES_BASELINE_COMPLETION_STATE.md",
        "docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md",
        "docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md",
        "docs/current/POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md",
        "docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md",
        "docs/current/review/v295_initial_schema.manual-review.json",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "rpg_v308_runtime_config_hardening_ready.zip",
        "v308.runtime-config-hardening-ready",
        "backend/.venv",
        "check_runtime_config_hardening.py --strict --require-health",
        "v295_initial_schema",
        "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa",
        "rpg_game_restore_rehearsal_v290",
        "postgres-baseline-completion-state-verified",
        "next-revision-not-required-current-schema-equivalent",
        "runtime-config-hardening-verified-local-runtime-preserved",
        "7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "application tables/rows 22/748",
        "public tables/rows 23/749",
        "migration rpg_game_migration_empty_v290",
        "v304 source post-check",
        "check_runtime_config_hardening.py",
        "alembic-managed-baseline-complete",
        "v307 Docker PostgreSQL: running/healthy",
        "runtime-config-hardening-verified-local-runtime-preserved",
    )
    assert_contains(
        "README.md",
        "v308.runtime-config-hardening-ready",
        "check_runtime_config_hardening.py",
        "v295_initial_schema",
        "alembic-managed-baseline-complete",
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
        "v303",
        "rpg_game_restore_rehearsal_v290",
        "v295_initial_schema",
        "approved pre-stamp application digests preserved",
        "alembic_version",
        "stamp를 다시 실행하지 않습니다",
    )
    assert_contains(
        "docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md",
        "v304",
        "rpg_game",
        "source-baseline-stamp-current-state-verified",
        "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481",
        "restore-rehearsal-stamp-current-state-verified",
        "source stamp는 완료됐으므로 `--execute`를 다시 실행하지 않습니다",
    )
    assert_contains(
        "docs/current/POSTGRES_BASELINE_COMPLETION_STATE.md",
        "v305",
        "alembic-managed-baseline-complete",
        "postgres-baseline-completion-state-verified",
        "v304 source execution report",
        "새 Alembic revision 생성",
    )
    assert_contains(
        "docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md",
        "v306",
        "compare_metadata()",
        "read-only transaction",
        "next-revision-not-required-current-schema-equivalent",
        "sequence ownership",
    )
    assert_contains(
        "docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md",
        "v306",
        "autogenerate",
        "compare_metadata()",
        "별도 승인",
    )
    assert_contains(
        "docs/current/POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md",
        "v307",
        "postgresql+asyncpg",
        "docker compose ps --format json",
        "local-runtime-readiness-verified-production-hardening-required",
        "비밀번호, JWT secret",
    )
    assert_contains(
        "docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md",
        "v307",
        "서버 시작 시 자동 migration",
        "migration 전 source DB backup",
        "isolated migration DB",
        "별도 승인",
    )
    assert_contains(
        "docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md",
        "v308",
        "DB_POOL_PRE_PING",
        "engine.dispose()",
        "runtime-config-hardening-verified-local-runtime-preserved",
    )
    assert_contains(
        "docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md",
        "v308",
        "Adminer",
        "digest",
        "TLS",
        "자동 migration",
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
