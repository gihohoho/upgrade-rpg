#!/usr/bin/env python3
"""Fail-closed static validation for the separated Render and Neon plans."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RENDER_PLAN = ROOT / "deploy/render-service-settings.example.json"
NEON_PLAN = ROOT / "deploy/neon-database-initialization-migration.example.json"
RENDER_DOC = ROOT / "docs/current/RENDER_SERVICE_SETTINGS_PLAN.md"
NEON_DOC = ROOT / "docs/current/NEON_DATABASE_INITIALIZATION_MIGRATION_PLAN.md"
RENDER_ENV = ROOT / "deploy/render.production.env.example"
CONFIG_SOURCE = ROOT / "backend/app/core/config.py"
SESSION_SOURCE = ROOT / "backend/app/db/session.py"
ALEMBIC_SOURCE = ROOT / "backend/alembic/env.py"
BOOTSTRAP_SMOKE = ROOT / "tools/smoke/backend/smoke_neon_production_database_bootstrap.py"
NEON_INITIALIZER = ROOT / "tools/initialize_neon_database.py"
NEON_INITIALIZER_SMOKE = (
    ROOT / "tools/smoke/backend/smoke_neon_database_initialization_guard.py"
)
NEON_RESTORE_EVIDENCE = ROOT / "deploy/review/neon-restore-prestamp-verification-v344.json"

RENDER_VERSION = "v340.render-service-settings-reviewed-creation-blocked"
NEON_VERSION = "v344.neon-restore-verified-stamp-recovery-preparation-ready"
STATE_VERSION = "v344.neon-restore-verified-stamp-recovery-preparation-ready"
RESULT = "neon-restore-verified-stamp-recovery-preparation-ready"
NEXT_STAGE = "owner-approve-neon-stamp-recovery-preparation-sha"
IMAGE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
)
BACKUP_SHA = "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481"
REVISION_SHA = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"
UTC_DATA_DIGEST = "4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c"

STATE_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "NEXT_CHAT_PROMPT.md",
    ROOT / "NEXT_CHAT_HANDOFF.md",
    ROOT / "docs/current/CURRENT_STATUS.md",
    ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md",
    ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md",
)


class PlanError(RuntimeError):
    """Safe-to-display static plan validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing plan: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"invalid plan JSON: {path.name} ({type(exc).__name__})") from None
    require(isinstance(payload, dict), f"plan root must be an object: {path.name}")
    return payload


def flattened_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [item for child in value.values() for item in flattened_strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in flattened_strings(child)]
    return []


def verify_no_secret_values(payload: dict[str, Any], label: str) -> None:
    text = "\n".join(flattened_strings(payload))
    forbidden = (
        r"postgres(?:ql)?://",
        r"\bnpg_[A-Za-z0-9]+",
        r"\bghp_[A-Za-z0-9]+",
        r"\bgithub_pat_[A-Za-z0-9_]+",
        r"\bep-[a-z0-9-]+\.(?:c-\d+\.)?ap-southeast-1\.aws\.neon\.tech\b",
    )
    for pattern in forbidden:
        require(re.search(pattern, text, re.IGNORECASE) is None, f"{label} contains a secret or endpoint-shaped value")


def verify_render(plan: dict[str, Any]) -> None:
    require(plan.get("schemaVersion") == RENDER_VERSION, "Render schemaVersion differs")
    require(plan.get("nextSafeStage") == NEXT_STAGE, "Render next stage differs")
    require(plan.get("productionResourcesMutated") is False, "Render mutation flag must be false")

    service = plan.get("service") or {}
    require(service.get("type") == "web-service", "Render service type differs")
    require(service.get("source") == "existing-image", "Render source differs")
    require(service.get("recommendedName") == "upgrade-rpg-api", "Render recommended name differs")
    require(service.get("ownerConfirmedName") is True, "Render service name must be owner-confirmed")
    require(service.get("region") == "singapore", "Render region differs")
    require(service.get("instanceType") == "free", "Render instance type differs")
    require(service.get("instanceCount") == 1, "Render instance count differs")
    require(service.get("healthCheckPath") == "/api/v1/health", "Render health path differs")
    require(service.get("databaseHealthUsedAsPlatformProbe") is False, "DB health must not be the platform probe")
    require(service.get("port") == 8000, "Render port differs")
    require(service.get("preDeployCommand") is None, "Render pre-deploy command must remain empty")
    require(service.get("dockerCommandOverride") is None, "Render Docker command override must remain empty")
    require(service.get("autoDeploy") is False, "Render auto-deploy must remain false")

    image = plan.get("image") or {}
    require(image.get("reviewedReference") == IMAGE, "Render reviewed image differs")
    require(image.get("currentReferenceDeployable") is True, "verified v341 image must be deployable")
    require(image.get("replacementExactDigestRequired") is False, "replacement image must no longer be required")
    require(image.get("bootstrapSourceFixCompleted") is True, "bootstrap source fix must be complete")

    runtime = plan.get("databaseRuntime") or {}
    require(runtime.get("connectionMode") == "direct", "runtime connection must be direct")
    require(runtime.get("tls") == "system-ca-verify-full", "runtime TLS policy differs")
    require(runtime.get("poolSize") == 2 and runtime.get("maxOverflow") == 0, "runtime pool boundary differs")

    inventory = plan.get("environmentInventory") or {}
    require(
        inventory.get("sourceFile") == "deploy/render.production.env.example",
        "Render env inventory source differs",
    )
    non_secret = inventory.get("nonSecret") or {}
    expected = {
        "ENVIRONMENT": "production",
        "DEBUG": "false",
        "PORT": "8000",
        "CORS_ORIGINS": "[]",
        "DB_POOL_SIZE": "2",
        "DB_MAX_OVERFLOW": "0",
    }
    for key, value in expected.items():
        require(non_secret.get(key) == value, f"Render env inventory differs: {key}")
    require(
        inventory.get("secretKeysOnly") == ["DATABASE_URL", "JWT_SECRET_KEY", "ADMIN_WRITE_DEV_KEY"],
        "Render secret key inventory differs",
    )
    require(inventory.get("actualSecretValuesRecorded") is False, "Render secret values must not be recorded")

    gate = plan.get("creationGate") or {}
    require(gate.get("settingsReviewed") is True, "Render settings review must be complete")
    require(gate.get("ownerServiceNameRequired") is False, "Render service name must not remain unresolved")
    require(gate.get("runtimeFixCompleted") is True, "Render runtime fix must be complete")
    require(
        gate.get("replacementImagePublishedAndIsolatedValidated") is True,
        "Render gate must record the verified replacement image",
    )
    for key in (
        "neonInitializationCompleted",
        "webServiceCreationApproved",
        "webServiceCreated",
        "deploymentExecuted",
    ):
        require(gate.get(key) is False, f"Render gate must remain false: {key}")
    require(gate.get("exactPreparationShaApprovalRequired") is True, "Render exact-SHA approval must be required")
    verify_no_secret_values(plan, "Render plan")


def verify_neon(plan: dict[str, Any]) -> None:
    require(plan.get("schemaVersion") == NEON_VERSION, "Neon schemaVersion differs")
    require(plan.get("nextSafeStage") == NEXT_STAGE, "Neon next stage differs")
    require(plan.get("productionResourcesMutated") is True, "Neon restore mutation must be recorded")

    target = plan.get("target") or {}
    require(target.get("region") == "aws-ap-southeast-1", "Neon region differs")
    require(target.get("postgresMajor") == 16, "Neon major differs")
    require(target.get("database") == "neondb", "Neon database differs")
    require(target.get("role") == "neondb_owner", "Neon role differs")
    require(target.get("createDatabaseRequired") is False, "Neon DB creation must remain unnecessary")
    require(target.get("readOnlyObservedPublicTables") == 0, "Neon target must remain observed empty")
    require(target.get("readOnlyObservedAlembicVersion") is False, "Neon target Alembic must be absent")

    source = plan.get("source") or {}
    require(source.get("backupSha256") == BACKUP_SHA, "backup SHA differs")
    require(source.get("backupSizeBytes") == 129635, "backup size differs")
    require(source.get("applicationTables") == 22 and source.get("applicationRows") == 748, "source counts differ")
    require(source.get("backupContainsAlembicVersion") is False, "backup Alembic boundary differs")
    require(source.get("reviewedRevision") == "v295_initial_schema", "reviewed revision differs")
    require(source.get("reviewedRevisionSha256") == REVISION_SHA, "reviewed revision SHA differs")
    require(source.get("expectedDataDigest") == UTC_DATA_DIGEST, "UTC-canonical data digest differs")
    require(
        source.get("dataDigestNormalization")
        == "timezone-aware datetime values are converted to UTC before canonical JSON hashing",
        "data digest normalization differs",
    )

    connection = plan.get("connectionPolicy") or {}
    require(connection.get("restoreAndAlembicConnection") == "direct-only", "Neon restore must use direct")
    require(connection.get("pooledConnectionAllowedForRestoreOrAlembic") is False, "pooled restore must be forbidden")
    require(connection.get("libpqMinimumMajor") == 16, "libpq minimum differs")
    require(
        connection.get("tls") == "windows-system-ca-export-plus-verify-full",
        "Neon TLS policy differs",
    )
    require(
        "Git-ignored local PEM" in str(connection.get("windowsLibpqCompatibility")),
        "Neon Windows libpq compatibility boundary differs",
    )
    require(connection.get("actualConnectionValuesRecorded") is False, "Neon connection values must not be recorded")

    gate = plan.get("executionGate") or {}
    require(gate.get("planReviewed") is True, "Neon plan review must be complete")
    require(gate.get("runtimeFixCompleted") is True, "Neon runtime fix must be complete")
    require(
        gate.get("replacementImagePublishedAndIsolatedValidated") is True,
        "Neon gate must record the verified replacement image",
    )
    require(gate.get("preparationToolReviewed") is True, "Neon preparation tool must be reviewed")
    require(gate.get("readOnlyPreflightRequired") is True, "Neon read-only preflight must be required")
    require(gate.get("stampRecoveryPreparationReady") is True, "Neon stamp recovery must be ready")
    require(
        gate.get("restoreVerifiedWithUtcCanonicalDigest") is True,
        "Neon restored data must be UTC-canonical verified",
    )
    require(
        gate.get("preparationTool") == "tools/initialize_neon_database.py",
        "Neon preparation tool path differs",
    )
    require(
        gate.get("focusedSmoke")
        == "tools/smoke/backend/smoke_neon_database_initialization_guard.py",
        "Neon preparation smoke path differs",
    )
    require(gate.get("databaseInitializationApproved") is True, "Neon initialization approval must be recorded")
    require(gate.get("restoreExecuted") is True, "Neon restore execution must be recorded")
    for key in ("stampExecuted", "stampRecoveryApproved", "renderServiceExists"):
        require(gate.get(key) is False, f"Neon gate must remain false: {key}")
    require(gate.get("exactPreparationShaApprovalRequired") is True, "Neon exact-SHA approval must be required")
    verify_no_secret_values(plan, "Neon plan")

    evidence = load_json(NEON_RESTORE_EVIDENCE)
    require(evidence.get("schemaVersion") == NEON_VERSION, "Neon restore evidence version differs")
    require(evidence.get("result") == RESULT, "Neon restore evidence result differs")
    require(evidence.get("nextSafeStage") == NEXT_STAGE, "Neon restore evidence next stage differs")
    verification = evidence.get("readOnlyVerification") or {}
    require(
        verification.get("applicationTableCount") == 22
        and verification.get("applicationRowCount") == 748,
        "Neon restored application counts differ",
    )
    require(
        verification.get("applicationDataDigestUtcCanonical") == UTC_DATA_DIGEST
        and verification.get("verifiedRehearsalDataDigestUtcCanonical") == UTC_DATA_DIGEST,
        "Neon restored UTC-canonical digest differs",
    )
    require(verification.get("alembicVersionPresent") is False, "Neon stamp must remain absent")
    mutations = evidence.get("mutations") or {}
    require(mutations.get("databaseRestoreExecuted") is True, "Neon restore evidence must be true")
    require(mutations.get("alembicStampExecuted") is False, "Neon stamp evidence must remain false")
    require(evidence.get("secretOrEndpointRecorded") is False, "Neon evidence contains secret marker")
    verify_no_secret_values(evidence, "Neon restore evidence")


def verify_docs() -> None:
    require(RENDER_DOC.is_file() and NEON_DOC.is_file(), "separated current docs are missing")
    for path in STATE_FILES:
        require(path.is_file(), f"missing state file: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        for marker in (STATE_VERSION, RENDER_VERSION, NEON_VERSION, RESULT, NEXT_STAGE):
            require(marker in text, f"{path.relative_to(ROOT)} is missing {marker}")
    require(
        (ROOT / "NEXT_CHAT_PROMPT.md").read_bytes()
        == (ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md").read_bytes(),
        "NEXT_CHAT_PROMPT mirror differs",
    )
    require(
        (ROOT / "NEXT_CHAT_HANDOFF.md").read_bytes()
        == (ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md").read_bytes(),
        "NEXT_CHAT_HANDOFF mirror differs",
    )


def verify_bootstrap_sources() -> None:
    for path in (
        RENDER_ENV,
        CONFIG_SOURCE,
        SESSION_SOURCE,
        ALEMBIC_SOURCE,
        BOOTSTRAP_SMOKE,
        NEON_INITIALIZER,
        NEON_INITIALIZER_SMOKE,
        NEON_RESTORE_EVIDENCE,
    ):
        require(path.is_file(), f"missing bootstrap file: {path.relative_to(ROOT)}")

    env_text = RENDER_ENV.read_text(encoding="utf-8")
    for marker in (
        "ENVIRONMENT=production",
        "DEBUG=false",
        "PORT=8000",
        "CORS_ORIGINS=[]",
        "DB_POOL_SIZE=2",
        "DB_MAX_OVERFLOW=0",
        "DB_POOL_RECYCLE_SECONDS=300",
    ):
        require(marker in env_text, f"Render env inventory is missing {marker}")
    require("sslmode=" not in env_text and "sslrootcert=" not in env_text, "Render runtime URL must not contain TLS query settings")
    require("ep-" not in env_text and "npg_" not in env_text, "Render env inventory contains endpoint-shaped data")

    config_text = CONFIG_SOURCE.read_text(encoding="utf-8")
    for marker in (
        "def build_database_connect_args(",
        "ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)",
        "context.check_hostname = True",
        "context.verify_mode = ssl.CERT_REQUIRED",
        'context.cert_store_stats().get("x509_ca", 0) < 1',
        "DATABASE_URL must not contain TLS query parameters in production",
    ):
        require(marker in config_text, f"production TLS bootstrap is missing {marker}")

    for path in (SESSION_SOURCE, ALEMBIC_SOURCE):
        text = path.read_text(encoding="utf-8")
        require("connect_args=build_database_connect_args()" in text, f"{path.relative_to(ROOT)} does not bind shared TLS args")

    initializer_text = NEON_INITIALIZER.read_text(encoding="utf-8")
    for marker in (
        'EXPECTED_ACTION = "verify-restored-and-stamp-once"',
        '"--exit-on-error"',
        '"--single-transaction"',
        '"--no-owner"',
        '"--no-privileges"',
        '"SET TRANSACTION READ ONLY"',
        "export_windows_system_ca_bundle",
        '"PGSSLMODE": "verify-full"',
        '"alembicRevisions"',
        "restore is already recorded and must not be retried",
        'git_output("rev-parse", "--verify", "origin/main")',
        '"stamp",\n        EXPECTED_REVISION',
        "automatic retry/cleanup/reset/Render action: no",
    ):
        require(marker in initializer_text, f"Neon initializer is missing safety marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="validate all fail-closed plan and handoff markers")
    parser.parse_args()
    try:
        verify_render(load_json(RENDER_PLAN))
        verify_neon(load_json(NEON_PLAN))
        verify_bootstrap_sources()
        verify_docs()
    except PlanError as exc:
        print(f"Render/Neon separated plan verification failed: {exc}", file=sys.stderr)
        return 1

    print("Render/Neon separated plan verification (static, no provider mutation)")
    print("- Render: upgrade-rpg-api confirmed / v341 exact image isolated-verified / creation blocked")
    print("- Neon: restore UTC-canonical verified / exact-SHA-gated stamp-only recovery ready / Render blocked")
    print("- secrets/endpoints recorded: no")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
