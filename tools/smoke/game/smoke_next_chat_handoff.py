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
        "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
        "docs/current/POSTGRES_PRODUCTION_MANAGED_DB_PROXY_SELECTION.md",
        "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py",
        "backend/Dockerfile",
        "deploy/docker-compose.production.yml",
        "deploy/production.env.example",
        "deploy/production-capacity-plan.example.json",
        "deploy/production-architecture-selection.example.json",
        "deploy/backend-image-source-digest-policy.example.json",
        "deploy/review/production-compose-config-render-v312.json",
        "deploy/reverse-proxy/README.md",
        "deploy/isolated-validation/README.md",
        "deploy/secrets/README.md",
        "tools/check_production_secrets_tls_container_static.py",
        "tools/check_production_capacity_tls_network_plan.py",
        "tools/check_production_managed_postgres_reverse_proxy_selection.py",
        "tools/render_production_compose_config.py",
        "tools/check_backend_image_source_digest_policy.py",
        "tools/smoke/backend/smoke_backend_image_source_digest_policy.py",
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
        "rpg_v313_backend_image_source_digest_policy_handoff_ready.zip",
        "v313.backend-image-source-digest-policy",
        "backend/.venv",
        "managed-postgresql-selected",
        "external-reverse-proxy-https-selected",
        "backend replicas/workers: 1/1",
        "production-compose-config-render-verified-no-runtime-mutation",
        "check_backend_image_source_digest_policy.py --strict",
        "backend-image-source-digest-policy-verified-provider-and-build-blocked",
        "Docker image pull/build/push",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "source rpg_game: public 23/749, application 22/748",
        "revision SHA-256: " + REVISION_SHA256,
        "config render approved/executed: yes/yes",
        "production reference mode: digest-only",
        "pull/build/push approved: no/no/no",
        "select-registry-repository-platform-and-base-image-digest",
    )
    assert_contains(
        "deploy/production-architecture-selection.example.json",
        '"schemaVersion": "v312.production-architecture-selection"',
        '"databaseMode": "managed-postgresql-selected"',
        '"publicEntrypoint": "external-reverse-proxy-https-selected"',
        '"backendReplicas": 1',
        '"uvicornWorkersPerReplica": 1',
        '"composeConfigRenderApproved": true',
        '"composeConfigRenderExecuted": true',
        '"imagePullBuildApproved": false',
        '"containerStartApproved": false',
        '"composeConfigRenderEvidence": "deploy/review/production-compose-config-render-v312.json"',
    )
    assert_contains(
        "deploy/production-capacity-plan.example.json",
        '"schemaVersion": "v311.production-capacity-plan"',
        '"postgresMaxConnectionsCandidate": 40',
        '"tlsDatabaseMode": "managed-postgresql-selected"',
        '"composeConfigRenderExecuted": true',
        '"isolatedContainerExecutionApproved": false',
    )
    assert_contains(
        "deploy/backend-image-source-digest-policy.example.json",
        '"schemaVersion": "v313.backend-image-source-digest-policy"',
        '"registryProvider": "deferred"',
        '"productionReferenceMode": "digest-only"',
        '"targetPlatform": "deferred"',
        '"currentBaseImageReference": "python:3.11-slim"',
        '"baseImageDigestApproved": false',
        '"imagePullApproved": false',
        '"imageBuildApproved": false',
        '"imagePushApproved": false',
    )
    assert_contains(
        "deploy/review/production-compose-config-render-v312.json",
        '"recordedFromUserOutput": true',
        '"renderedServices": [',
        '"hostPortsAbsent": true',
        '"buildAbsent": true',
        '"imagePullBuildExecuted": false',
        '"result": "production-compose-config-render-verified-no-runtime-mutation"',
    )
    assert_contains(
        "deploy/docker-compose.production.yml",
        "services:\n  backend:",
        "image: ${BACKEND_IMAGE:?",
        "DATABASE_URL: ${DATABASE_URL:?",
        "postgres_ca",
        "external: true",
        "replicas: 1",
        "read_only: true",
        "no-new-privileges:true",
    )
    compose = read_required("deploy/docker-compose.production.yml")
    for forbidden in ("  postgres:", "adminer:", "ports:", "build:", "volumes:"):
        if forbidden in compose.lower():
            raise AssertionError(f"production Compose contains forbidden current marker: {forbidden}")

    assert_contains(
        "deploy/production.env.example",
        "<approved-registry>/<approved-namespace>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>",
        "sslmode=verify-full",
        "sslrootcert=/run/secrets/postgres_ca.pem",
        "<pre-created-reverse-proxy-network-name>",
    )
    assert_contains(
        "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
        "digest-only",
        "registry provider: deferred",
        "target platform: deferred",
        "base image digest approved: no",
        "image pull/build/push approved: no/no/no",
        "select-registry-repository-platform-and-base-image-digest",
    )
    assert_contains(
        "deploy/isolated-validation/README.md",
        "Stage 1 — 완료: config render only",
        "Stage 2A — 완료: image source/digest policy",
        "pull/build/push approved: no/no/no",
        "actual Docker config command executed on user PC: yes (config only)",
    )
    assert_contains(
        "tools/run_smoke_core.sh",
        "smoke_production_secrets_tls_container_static.py",
        "smoke_production_capacity_tls_network_plan.py",
        "smoke_production_managed_postgres_reverse_proxy_selection.py",
        "smoke_production_compose_config_render.py",
        "smoke_backend_image_source_digest_policy.py",
        "smoke_next_chat_handoff.py",
    )
    assert_contains(
        ".gitignore",
        "/local-backups/",
        "/local-review-artifacts/",
        "/deploy/production.env",
        "/deploy/secrets/*",
    )

    revision = ROOT / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    actual_sha = hashlib.sha256(revision.read_bytes()).hexdigest()
    if actual_sha != REVISION_SHA256:
        raise AssertionError(f"reviewed revision SHA-256 differs: {actual_sha}")

    print("OK: v313 next-chat handoff and document structure are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
