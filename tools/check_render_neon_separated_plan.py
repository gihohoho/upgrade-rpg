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
NEON_DOC = ROOT / "docs/reference/database/NEON_DATABASE_INITIALIZATION_MIGRATION_PLAN.md"
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
NEON_COMPLETION_EVIDENCE = ROOT / "deploy/review/neon-initialization-completed-v345.json"
RENDER_PREPARER = ROOT / "tools/prepare_render_local_environment.py"
RENDER_PREPARER_SMOKE = (
    ROOT / "tools/smoke/backend/smoke_render_service_creation_preparation.py"
)
RENDER_DEPLOY_EVIDENCE = ROOT / "deploy/review/render-service-initial-deploy-v347.json"

RENDER_VERSION = "v347.render-service-created-initial-deploy-verified"
NEON_VERSION = "v345.neon-initialization-completed-verified-render-preparation-required"
STATE_VERSION = "v347.render-service-created-initial-deploy-verified"
RESULT = "render-service-created-initial-deploy-verified"
NEXT_STAGE = "review-render-live-service-and-prepare-frontend-deployment-plan"
IMAGE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
)
BACKUP_SHA = "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481"
REVISION_SHA = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"
UTC_DATA_DIGEST = "4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c"
RENDER_PREPARATION_SHA = "81d1c4faa59194e8928d54fbecac28694ab139ab"
RENDER_SERVICE_ID = "srv-d9iro458nd3s73acgmsg"
RENDER_DEPLOY_ID = "dep-d9iro4l8nd3s73acgnmg"
RENDER_PUBLIC_URL = "https://upgrade-rpg-api.onrender.com"
PRESTAMP_VERSION = "v344.neon-restore-verified-stamp-recovery-preparation-ready"
PRESTAMP_RESULT = "neon-restore-verified-stamp-recovery-preparation-ready"
PRESTAMP_NEXT_STAGE = "owner-approve-neon-stamp-recovery-preparation-sha"
NEON_COMPLETION_NEXT_STAGE = "prepare-render-service-creation-exact-sha-approval"
NEON_COMPLETION_RESULT = "neon-database-initialization-completed-verified-render-preparation-required"

STATE_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "NEXT_CHAT_PROMPT.md",
    ROOT / "NEXT_CHAT_HANDOFF.md",
    ROOT / "docs/current/CURRENT_STATUS.md",
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
    require(plan.get("productionResourcesMutated") is True, "Render mutation flag must record deployment")

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
    require(service.get("configuredPortHint") == 8000, "Render configured port hint differs")
    require(service.get("observedProviderInjectedPort") == 10000, "Render provider port differs")
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
    require(inventory.get("localValueFile") == "deploy/.env.production", "Render local env path differs")
    for key in (
        "localValueFileGitAndDockerExcluded",
        "localEnvironmentPrepared",
        "exactLocalValuesAbsentFromGitTrackedFiles",
        "databaseUrlConvertedFromValidatedNeonDirect",
        "databaseUrlUsesAsyncpgWithoutTlsQuery",
        "jwtAndAdminSecretsStrongAndDistinct",
    ):
        require(inventory.get(key) is True, f"Render local preparation marker differs: {key}")

    scope = plan.get("approvedExecutionScope") or {}
    for key in (
        "requiresCleanPushedMainExactSha",
        "createOneWebService",
        "injectReviewedEnvironment",
        "initialDeployExactImage",
        "recordManagedHttpsUrlAndSanitizedEvidence",
        "confirmNoCommandOverridePreDeployOrAutoDeploy",
    ):
        require(scope.get(key) is True, f"Render execution scope marker differs: {key}")
    for key in (
        "databaseMutation",
        "imageChange",
        "customDomainOrDns",
        "paymentMethodChange",
        "automaticRetryOrSecondDeploy",
    ):
        require(scope.get(key) is False, f"Render excluded execution scope differs: {key}")
    require(scope.get("waitForPlatformHealth") == "/api/v1/health", "Render platform health scope differs")
    require(scope.get("singleManualDatabaseHealthRead") == "/api/v1/health/db", "Render DB health scope differs")
    require(
        scope.get("failurePolicy") == "stop-with-service-state-preserved-and-request-review",
        "Render failure policy differs",
    )
    contract = plan.get("approvalContract") or {}
    require(contract.get("tool") == "tools/prepare_render_local_environment.py", "Render approval tool differs")
    require(contract.get("mode") == "--verify-execution-approval", "Render approval mode differs")
    require(contract.get("serviceConfirmation") == "upgrade-rpg-api", "Render approval service differs")
    require(contract.get("imageConfirmation") == IMAGE, "Render approval image differs")
    require(
        contract.get("actionConfirmation") == "create-inject-deploy-once-and-read-health",
        "Render approval action differs",
    )
    require(contract.get("cleanPushedMainRequired") is True, "clean pushed main gate must be required")
    require(contract.get("providerMutationDuringGuard") is False, "approval guard must not mutate Render")

    gate = plan.get("creationGate") or {}
    require(gate.get("settingsReviewed") is True, "Render settings review must be complete")
    require(gate.get("ownerServiceNameRequired") is False, "Render service name must not remain unresolved")
    require(gate.get("runtimeFixCompleted") is True, "Render runtime fix must be complete")
    require(
        gate.get("replacementImagePublishedAndIsolatedValidated") is True,
        "Render gate must record the verified replacement image",
    )
    require(
        gate.get("neonInitializationCompleted") is True,
        "Render gate must record completed Neon initialization",
    )
    require(gate.get("localEnvironmentPrepared") is True, "Render local environment must be prepared")
    for key in (
        "exactPreparationShaApproved",
        "webServiceCreationApproved",
        "webServiceCreated",
        "deploymentExecuted",
    ):
        require(gate.get(key) is True, f"Render completed gate must be true: {key}")
    require(
        gate.get("approvedPreparationSha") == RENDER_PREPARATION_SHA,
        "Render approved preparation SHA differs",
    )
    require(gate.get("exactPreparationShaApprovalRequired") is True, "Render exact-SHA approval must be required")

    live = plan.get("liveService") or {}
    require(live.get("serviceId") == RENDER_SERVICE_ID, "Render live service ID differs")
    require(live.get("deployId") == RENDER_DEPLOY_ID, "Render deploy ID differs")
    require(live.get("publicUrl") == RENDER_PUBLIC_URL, "Render public URL differs")
    require(live.get("status") == "live", "Render service must be live")
    require(live.get("firstDeployAttemptCount") == 1, "Render deploy attempt count differs")
    require(live.get("automaticRetryExecuted") is False, "Render automatic retry must remain false")
    require(live.get("publicHealthHttpStatus") == 200, "Render public health differs")
    require(live.get("databaseHealthHttpStatus") == 200, "Render DB health differs")
    require(live.get("databaseHealthRequestCount") == 1, "Render DB health request count differs")
    require(
        live.get("sanitizedEvidence") == "deploy/review/render-service-initial-deploy-v347.json",
        "Render deployment evidence path differs",
    )

    evidence = load_json(RENDER_DEPLOY_EVIDENCE)
    require(evidence.get("schemaVersion") == RENDER_VERSION, "Render evidence version differs")
    require(evidence.get("result") == RESULT, "Render evidence result differs")
    require(evidence.get("nextSafeStage") == NEXT_STAGE, "Render evidence next stage differs")
    require(evidence.get("approvedPreparationSha") == RENDER_PREPARATION_SHA, "Render evidence SHA differs")
    evidence_service = evidence.get("service") or {}
    require(evidence_service.get("id") == RENDER_SERVICE_ID, "Render evidence service ID differs")
    require(evidence_service.get("publicUrl") == RENDER_PUBLIC_URL, "Render evidence URL differs")
    require(evidence_service.get("status") == "live", "Render evidence status differs")
    deployment = evidence.get("deployment") or {}
    require(deployment.get("id") == RENDER_DEPLOY_ID, "Render evidence deploy ID differs")
    require(deployment.get("attemptCount") == 1, "Render evidence attempt count differs")
    require(deployment.get("automaticRetry") is False, "Render evidence retry differs")
    require(deployment.get("exactImageReference") == IMAGE, "Render evidence image differs")
    require(deployment.get("observedProviderInjectedPort") == 10000, "Render evidence port differs")
    verification = evidence.get("verification") or {}
    require(
        verification.get("publicHealthHttpStatus") == 200
        and verification.get("publicHealthStatus") == "ok",
        "Render public health evidence differs",
    )
    require(
        verification.get("databaseHealthHttpStatus") == 200
        and verification.get("databaseHealthStatus") == "ok"
        and verification.get("databaseHealthRequestCount") == 1,
        "Render DB health evidence differs",
    )
    mutations = evidence.get("mutations") or {}
    for key in (
        "renderWebServiceCreated",
        "renderEnvironmentInjected",
        "renderInitialDeployExecuted",
    ):
        require(mutations.get(key) is True, f"Render mutation evidence must be true: {key}")
    for key in (
        "databaseWrite",
        "alembic",
        "imageChange",
        "customDomainOrDns",
        "paymentMethod",
        "secondDeploy",
    ):
        require(mutations.get(key) is False, f"Render excluded mutation differs: {key}")
    require(evidence.get("secretOrEndpointCredentialRecorded") is False, "Render evidence secret marker differs")
    verify_no_secret_values(evidence, "Render deployment evidence")
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
    for key in (
        "databaseInitializationApproved",
        "restoreExecuted",
        "stampExecuted",
        "stampRecoveryApproved",
    ):
        require(gate.get(key) is True, f"Neon completed gate must be true: {key}")
    require(
        gate.get("approvedStampRecoveryPreparationSha")
        == "cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c",
        "Neon approved stamp recovery SHA differs",
    )
    require(gate.get("renderServiceExists") is True, "Render service existence must be recorded")
    require(gate.get("exactPreparationShaApprovalRequired") is True, "Neon exact-SHA approval must be required")
    verify_no_secret_values(plan, "Neon plan")

    evidence = load_json(NEON_RESTORE_EVIDENCE)
    require(evidence.get("schemaVersion") == PRESTAMP_VERSION, "Neon restore evidence version differs")
    require(evidence.get("result") == PRESTAMP_RESULT, "Neon restore evidence result differs")
    require(
        evidence.get("nextSafeStage") == PRESTAMP_NEXT_STAGE,
        "Neon restore evidence next stage differs",
    )
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

    completion = load_json(NEON_COMPLETION_EVIDENCE)
    require(completion.get("schemaVersion") == NEON_VERSION, "Neon completion evidence version differs")
    require(
        completion.get("result") == NEON_COMPLETION_RESULT,
        "Neon completion historical result differs",
    )
    require(
        completion.get("nextSafeStage") == NEON_COMPLETION_NEXT_STAGE,
        "Neon completion historical next stage differs",
    )
    require(completion.get("restoreRetried") is False, "Neon restore retry must remain false")
    require(
        completion.get("finalPublicTableCount") == 23
        and completion.get("finalTotalRowCount") == 749,
        "Neon final table/row counts differ",
    )
    require(
        completion.get("applicationTableCount") == 22
        and completion.get("applicationRowCount") == 748,
        "Neon final application counts differ",
    )
    require(
        completion.get("applicationDataDigestUtcCanonical") == UTC_DATA_DIGEST,
        "Neon final UTC-canonical data digest differs",
    )
    require(
        completion.get("alembicVersionTableRows") == 1
        and completion.get("alembicCurrentRevision") == "v295_initial_schema",
        "Neon final Alembic state differs",
    )
    require(completion.get("renderServiceCreated") is False, "Render service must remain absent")
    require(completion.get("secretOrEndpointRecorded") is False, "Neon completion contains secret marker")
    verify_no_secret_values(completion, "Neon completion evidence")


def verify_docs() -> None:
    require(RENDER_DOC.is_file() and NEON_DOC.is_file(), "separated current docs are missing")
    for path in STATE_FILES:
        require(path.is_file(), f"missing state file: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        for marker in (STATE_VERSION, RENDER_VERSION, NEON_VERSION, RESULT, NEXT_STAGE):
            require(marker in text, f"{path.relative_to(ROOT)} is missing {marker}")

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
        NEON_COMPLETION_EVIDENCE,
        RENDER_PREPARER,
        RENDER_PREPARER_SMOKE,
        RENDER_DEPLOY_EVIDENCE,
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
        '"--exit-on-error"',
        '"--single-transaction"',
        '"--no-owner"',
        '"--no-privileges"',
        '"SET TRANSACTION READ ONLY"',
        "export_windows_system_ca_bundle",
        '"PGSSLMODE": "verify-full"',
        '"alembicRevisions"',
        "Neon initialization is complete; restore and stamp retries are disabled",
        'git_output("rev-parse", "--verify", "origin/main")',
        '"stamp",\n        EXPECTED_REVISION',
        "automatic retry/cleanup/reset/Render action: no",
    ):
        require(marker in initializer_text, f"Neon initializer is missing safety marker: {marker}")

    preparer_text = RENDER_PREPARER.read_text(encoding="utf-8")
    for marker in (
        "postgresql+asyncpg://",
        "secrets.token_urlsafe(48)",
        "DATABASE_URL must not contain query or fragment",
        "JWT_SECRET_KEY and ADMIN_WRITE_DEV_KEY must differ",
        "exactLocalValuesAbsentFromGitTrackedFiles",
        "require_exact_execution_approval",
        'git_output("rev-parse", "--verify", "origin/main")',
        "actual secret or endpoint displayed: no",
        "Render resource mutation: no",
    ):
        require(marker in preparer_text, f"Render preparer is missing safety marker: {marker}")


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
    print("- Render: Free Singapore service live / exact image / public + DB health 200")
    print("- Neon: 22/748 restored + exact v295 stamped + 23/749 verified")
    print("- secrets/endpoints recorded: no")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
