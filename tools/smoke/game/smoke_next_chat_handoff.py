from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


def read_required(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"missing required handoff file: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(relative_path: str, *needles: str) -> None:
    text = read_required(relative_path)
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{relative_path} missing expected text: {needle}")


def assert_same(first: str, second: str) -> None:
    if read_required(first) != read_required(second):
        raise AssertionError(f"handoff mirror differs: {first} != {second}")


def main() -> int:
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
        "docs/current/PROJECT_STRUCTURE.md",
        "docs/current/ROADMAP.md",
        "docs/current/POSTGRES_ALEMBIC_READINESS.md",
        "docs/current/POSTGRES_BASELINE_COMPLETION_STATE.md",
        "docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md",
        "docs/current/POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md",
        "docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md",
        "docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md",
        "docs/current/POSTGRES_PRODUCTION_STATIC_VALIDATION.md",
        "docs/archive/postgres-baseline/README.md",
        "docs/archive/postgres-baseline/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md",
        "docs/archive/postgres-baseline/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md",
        "docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md",
        "docs/archive/postgres-baseline/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md",
        "docs/archive/runtime-hardening/README.md",
        "docs/archive/runtime-hardening/POSTGRES_RUNTIME_ENGINE_BINDING_INSPECTOR_FIX.md",
        "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py",
        "backend/Dockerfile",
        "deploy/docker-compose.production.yml",
        "deploy/production.env.example",
        "deploy/secrets/README.md",
        "tools/check_postgres_baseline_completion_state.py",
        "tools/check_postgres_next_revision_preflight.py",
        "tools/check_postgres_deployment_runtime_readiness.py",
        "tools/check_runtime_config_hardening.py",
        "tools/check_production_secrets_tls_container_static.py",
        "tools/smoke/backend/smoke_production_secrets_tls_container_static.py",
        "deploy/production-capacity-plan.example.json",
        "deploy/isolated-validation/README.md",
        "docs/current/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md",
        "tools/check_production_capacity_tls_network_plan.py",
        "tools/smoke/backend/smoke_production_capacity_tls_network_plan.py",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_same("NEXT_CHAT_PROMPT.md", "docs/handoff/NEXT_CHAT_PROMPT.md")
    assert_same("NEXT_CHAT_HANDOFF.md", "docs/handoff/NEXT_CHAT_HANDOFF.md")
    assert_same("docs/README.md", "docs/current/README.md")
    assert_same("docs/CURRENT_STATUS.md", "docs/current/CURRENT_STATUS.md")
    assert_same("docs/PROJECT_STRUCTURE.md", "docs/current/PROJECT_STRUCTURE.md")

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "rpg_v311_production_capacity_tls_network_plan_handoff_ready.zip",
        "v311.production-capacity-tls-network-isolated-plan",
        "backend/.venv",
        "check_production_capacity_tls_network_plan.py --strict",
        "runtime-config-hardening-verified-local-runtime-preserved",
        "remaining production warnings: 9",
        "production-static-validation-template-verified-runtime-application-blocked",
        "production-capacity-tls-network-plan-verified-execution-blocked",
        "recommended/candidate max_connections: 30/40",
        "isolated container execution approved: no",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "source rpg_game: public 23/749, application 22/748",
        "v310 production static validation: passed",
        "production-capacity-plan.example.json",
        "recommended minimum `max_connections=30`, review 후보 `40`",
        "check_production_capacity_tls_network_plan.py --strict",
    )
    assert_contains(
        "docs/current/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md",
        "v311",
        "managed-postgresql-preferred",
        "bundled PostgreSQL TLS",
        "HTTPS `443`",
        "recommended minimum: 30",
        "review candidate max_connections: 40",
        "production-capacity-tls-network-plan-verified-execution-blocked",
    )
    assert_contains(
        "deploy/production-capacity-plan.example.json",
        '"schemaVersion": "v311.production-capacity-plan"',
        '"postgresMaxConnectionsCandidate": 40',
        '"tlsDatabaseMode": "managed-postgresql-preferred"',
        '"isolatedContainerExecutionApproved": false',
    )
    assert_contains(
        "deploy/isolated-validation/README.md",
        "Stage 0",
        "Stage 1",
        "config render only",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "actual Docker command executed: no",
    )
    assert_contains(
        "deploy/docker-compose.production.yml",
        "POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password",
        "postgres_ca",
        "/api/v1/health",
        "read_only: true",
        "no-new-privileges:true",
    )
    assert_contains(
        "deploy/production.env.example",
        "postgres:16-alpine@sha256:<approved-64-hex-digest>",
        "sslmode=verify-full",
        "sslrootcert=/run/secrets/postgres_ca.pem",
        "<generate-a-random-secret-of-at-least-32-characters>",
    )
    assert_contains(
        ".gitignore",
        "/local-backups/",
        "/local-review-artifacts/",
        "/deploy/production.env",
        "/deploy/secrets/*",
    )
    assert_contains(
        "tools/run_smoke_core.sh",
        "smoke_production_secrets_tls_container_static.py",
        "smoke_production_capacity_tls_network_plan.py",
        "smoke_next_chat_handoff.py",
    )

    revision = ROOT / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    actual_sha = hashlib.sha256(revision.read_bytes()).hexdigest()
    if actual_sha != REVISION_SHA256:
        raise AssertionError(f"reviewed revision SHA-256 differs: {actual_sha}")

    print("OK: v311 next-chat handoff and document structure are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
