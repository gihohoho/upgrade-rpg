#!/usr/bin/env python3
"""Temp-fixture smoke for the v377 secret-safe email environment preparer."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
PRIVATE_HELPER = ROOT / "tools/private_artifacts.py"
ENVIRONMENT_TOOL = ROOT / "tools/prepare_v377_email_security_environment.py"

from prepare_v377_email_security_environment import (  # noqa: E402
    AUTH_ABUSE_SECRET,
    EMAIL_TOKEN_SECRET,
    EmailEnvironmentError,
    apply_environment,
    main as tool_main,
    plan_environment,
    print_summary,
)
from private_artifacts import (  # noqa: E402
    PrivatePathError,
    harden_private_file,
    verify_private_directory,
    verify_private_file,
)


LOCAL_EMAIL = "local-email-generated-secret-000000000000000000000001"
LOCAL_ABUSE = "local-abuse-generated-secret-000000000000000000000002"
PRODUCTION_ABUSE = "production-abuse-generated-secret-00000000000000000003"
PRESERVED_PRODUCTION_EMAIL = "production-email-preserved-secret-0000000000000000004"
LOCAL_JWT = "local-jwt-existing-secret-000000000000000000000000005"
LOCAL_ADMIN = "local-admin-existing-secret-00000000000000000000000006"
PRODUCTION_JWT = "production-jwt-existing-secret-00000000000000000000007"
PRODUCTION_ADMIN = "production-admin-existing-secret-000000000000000000008"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def initialize_fixture(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True)
    (root / "backend").mkdir()
    (root / "deploy").mkdir()
    (root / ".gitignore").write_text(
        "backend/.env\ndeploy/.env.production\n"
        "local-backups/\nlocal-review-artifacts/\n",
        encoding="utf-8",
        newline="\n",
    )
    require(git(root, "init", "--quiet").returncode == 0, "fixture git init failed")

    local_path = root / "backend/.env"
    production_path = root / "deploy/.env.production"
    local_path.write_text(
        "# local comment must survive\n"
        "CUSTOM_LOCAL=keep-this-exactly # untouched\n"
        f'JWT_SECRET_KEY="{LOCAL_JWT}"\n'
        f"ADMIN_WRITE_DEV_KEY={LOCAL_ADMIN}\n"
        'EMAIL_TOKEN_SECRET="change-me-before-production-email-token" # rotate\n'
        "AUTH_ABUSE_SECRET=\n"
        "BREVO_API_KEY=\n"
        "BREVO_FROM_EMAIL=\n"
        "EMAIL_PROVIDER=wrong-provider\n",
        encoding="utf-8",
        newline="\n",
    )
    production_path.write_text(
        "# production comment must survive\n"
        "CUSTOM_PRODUCTION=preserve-me\n"
        f"JWT_SECRET_KEY={PRODUCTION_JWT}\n"
        f"ADMIN_WRITE_DEV_KEY={PRODUCTION_ADMIN}\n"
        f"EMAIL_TOKEN_SECRET={PRESERVED_PRODUCTION_EMAIL}\n"
        "AUTH_ABUSE_SECRET=change-me-before-production-auth-abuse\n"
        "CORS_ORIGINS=[\"https://old.invalid\"]\n",
        encoding="utf-8",
        newline="\n",
    )
    return local_path, production_path


def dotenv_value(path: Path, key: str) -> str:
    prefix = f"{key}="
    matches = [line[len(prefix) :] for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    require(len(matches) == 1, f"fixture assignment count differs: {key}")
    value = matches[0].split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def test_plan_apply_and_idempotence(root: Path) -> None:
    local_path, production_path = initialize_fixture(root)
    local_before = local_path.read_bytes()
    production_before = production_path.read_bytes()

    try:
        plan_environment(root)
    except EmailEnvironmentError as exc:
        require(
            "permission verification failed" in str(exc),
            "read-only plan did not fail closed on a broad ACL",
        )
    else:
        raise AssertionError("read-only plan repaired a broad ACL implicitly")
    for path in (local_path, production_path):
        try:
            verify_private_file(path)
        except PrivatePathError:
            pass
        else:
            raise AssertionError("read-only plan mutated a broad ACL")
        harden_private_file(path)

    plan = plan_environment(root)
    require(plan.mode == "plan", "default plan mode differs")
    require(plan.file_write_count == 0, "plan reported a write")
    require(plan.secret_generation_count == 3, "plan generation count differs")
    require(plan.strong_secret_preserve_count == 1, "plan preservation count differs")
    require(local_path.read_bytes() == local_before, "plan changed local env")
    require(production_path.read_bytes() == production_before, "plan changed production env")

    artifact_directory = root / "local-backups/postgres"
    artifact_directory.mkdir(parents=True)
    artifact_file = artifact_directory / "synthetic-old.custom.dump"
    artifact_file.write_bytes(b"synthetic non-secret backup fixture")
    try:
        plan_environment(root)
    except EmailEnvironmentError as exc:
        require(
            "private-artifact permission verification failed" in str(exc),
            "read-only plan did not fail closed on a broad backup tree",
        )
    else:
        raise AssertionError("read-only plan repaired a broad backup tree implicitly")
    for path, verifier in (
        (artifact_directory, verify_private_directory),
        (artifact_file, verify_private_file),
    ):
        try:
            verifier(path)
        except PrivatePathError:
            pass
        else:
            raise AssertionError("read-only plan mutated a broad backup tree")

    generated = iter((LOCAL_EMAIL, LOCAL_ABUSE, PRODUCTION_ABUSE))
    applied = apply_environment(root, secret_factory=lambda: next(generated))
    require(applied.file_write_count == 2, "apply did not atomically replace both changed files")
    require(applied.secret_generation_count == 3, "apply generation count differs")
    verify_private_file(local_path)
    verify_private_file(production_path)
    verify_private_directory(root / "local-backups")
    verify_private_directory(artifact_directory)
    verify_private_file(artifact_file)

    local_after = local_path.read_text(encoding="utf-8")
    production_after = production_path.read_text(encoding="utf-8")
    require("# local comment must survive" in local_after, "local comment was lost")
    require("CUSTOM_LOCAL=keep-this-exactly # untouched" in local_after, "local unknown line changed")
    require("# rotate" in local_after, "inline comment was lost")
    require("# production comment must survive" in production_after, "production comment was lost")
    require("CUSTOM_PRODUCTION=preserve-me" in production_after, "production unknown line changed")

    local_email = dotenv_value(local_path, EMAIL_TOKEN_SECRET)
    local_abuse = dotenv_value(local_path, AUTH_ABUSE_SECRET)
    production_email = dotenv_value(production_path, EMAIL_TOKEN_SECRET)
    production_abuse = dotenv_value(production_path, AUTH_ABUSE_SECRET)
    require(local_email == LOCAL_EMAIL, "local email token secret was not generated")
    require(local_abuse == LOCAL_ABUSE, "local abuse secret was not generated")
    require(production_email == PRESERVED_PRODUCTION_EMAIL, "strong production secret changed")
    require(production_abuse == PRODUCTION_ABUSE, "production abuse secret was not generated")
    all_secrets = {
        local_email,
        local_abuse,
        production_email,
        production_abuse,
        LOCAL_JWT,
        LOCAL_ADMIN,
        PRODUCTION_JWT,
        PRODUCTION_ADMIN,
    }
    require(len(all_secrets) == 8, "application secrets are not distinct")

    require(dotenv_value(local_path, "EMAIL_PROVIDER") == "brevo", "local provider default differs")
    require(
        dotenv_value(local_path, "PUBLIC_FRONTEND_ORIGIN") == "http://127.0.0.1:5500",
        "local frontend origin differs",
    )
    require(dotenv_value(local_path, "AUTH_TRUSTED_PROXY_MODE") == "direct", "local proxy mode differs")
    require(dotenv_value(local_path, "REQUEST_BODY_LIMIT_BYTES") == "2100000", "local body cap differs")
    require(
        dotenv_value(production_path, "PUBLIC_FRONTEND_ORIGIN")
        == "https://gihohoho-upgrade-rpg.onrender.com",
        "production frontend origin differs",
    )
    require(
        dotenv_value(production_path, "AUTH_TRUSTED_PROXY_MODE") == "render",
        "production proxy mode differs",
    )
    require(
        dotenv_value(production_path, "CORS_ORIGINS")
        == '["https://gihohoho-upgrade-rpg.onrender.com"]',
        "production CORS differs",
    )
    require("BREVO_API_KEY=" not in production_after, "missing Brevo API key placeholder was inserted")
    require("BREVO_FROM_EMAIL=" not in production_after, "missing Brevo sender placeholder was inserted")
    require(
        set(applied.missing_external_actions)
        == {
            "local.BREVO_API_KEY",
            "local.BREVO_FROM_EMAIL",
            "production.BREVO_API_KEY",
            "production.BREVO_FROM_EMAIL",
        },
        "missing Brevo actions differ",
    )

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        print_summary(applied)
    emitted = stdout.getvalue() + stderr.getvalue() + repr(applied)
    for secret in all_secrets:
        require(secret not in emitted, "a secret leaked through summary/report output")

    final_local = local_path.read_bytes()
    final_production = production_path.read_bytes()

    def fail_if_generated() -> str:
        raise AssertionError("idempotent apply unexpectedly generated a secret")

    repeated = apply_environment(root, secret_factory=fail_if_generated)
    require(repeated.file_write_count == 0, "idempotent apply rewrote files")
    require(local_path.read_bytes() == final_local, "idempotent apply changed local bytes")
    require(production_path.read_bytes() == final_production, "idempotent apply changed production bytes")


def test_duplicate_error_is_secret_safe(root: Path) -> None:
    local_path, production_path = initialize_fixture(root)
    duplicate_marker = "duplicate-marker-secret-000000000000000000000000009"
    text = local_path.read_text(encoding="utf-8")
    text = text.replace(LOCAL_JWT, duplicate_marker).replace(
        '"change-me-before-production-email-token"',
        f'"{duplicate_marker}"',
    )
    local_path.write_text(text, encoding="utf-8", newline="\n")
    harden_private_file(local_path)
    harden_private_file(production_path)
    try:
        plan_environment(root)
    except EmailEnvironmentError as exc:
        require(duplicate_marker not in str(exc), "duplicate error leaked a secret")
        require("local.JWT_SECRET_KEY" in str(exc), "duplicate error omitted safe key context")
    else:
        raise AssertionError("duplicate application secret was accepted")


def test_tracked_target_refused(root: Path) -> None:
    local_path, _production_path = initialize_fixture(root)
    require(git(root, "add", "-f", "backend/.env").returncode == 0, "tracked fixture add failed")
    original = local_path.read_bytes()
    try:
        apply_environment(root, secret_factory=lambda: LOCAL_EMAIL)
    except EmailEnvironmentError as exc:
        require("tracked file" in str(exc), "tracked refusal reason differs")
        require(LOCAL_EMAIL not in str(exc), "tracked refusal leaked a generated secret")
    else:
        raise AssertionError("tracked environment target was writable")
    require(local_path.read_bytes() == original, "tracked target changed before refusal")
    try:
        verify_private_file(local_path)
    except PrivatePathError:
        pass
    else:
        raise AssertionError("tracked target ACL changed before refusal")


def test_invalid_argv_is_not_echoed() -> None:
    argv_marker = "argv-secret-marker-0000000000000000000000000010"
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        result = tool_main(["--unknown-secret-option", argv_marker])
    require(result == 2, "invalid argv did not fail safely")
    require(argv_marker not in stdout.getvalue() + stderr.getvalue(), "invalid argv leaked a value")


def test_private_creation_source_contract() -> None:
    helper_source = PRIVATE_HELPER.read_text(encoding="utf-8")
    environment_source = ENVIRONMENT_TOOL.read_text(encoding="utf-8")
    for marker in (
        "[IO.FileStream]::new(",
        "[IO.FileMode]::CreateNew",
        "Security.AccessControl.FileSecurity",
        "$security.SetOwner($currentSid)",
        "GetSystemDirectoryW",
        "AreAccessRulesProtected",
        "ensure_private_path_location",
        "verify_private_tree",
    ):
        require(marker in helper_source, f"private create/verify contract missing: {marker}")
    stage_start = environment_source.index("def _stage_atomic(")
    create_index = environment_source.index("create_private_file(temporary)", stage_start)
    write_index = environment_source.index("stream.write(content)", stage_start)
    require(create_index < write_index, "secret content can be written before private staging")
    require(
        "harden_private_tree(path)" in environment_source,
        "existing DB security artifacts are not hardened by apply",
    )
    plan_start = environment_source.index("def plan_environment(")
    plan_end = environment_source.index("def _stage_atomic(", plan_start)
    plan_source = environment_source[plan_start:plan_end]
    require("harden_private" not in plan_source, "read-only plan still repairs permissions")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-v377-email-env-") as temp:
        test_plan_apply_and_idempotence(Path(temp) / "plan-apply")
        test_duplicate_error_is_secret_safe(Path(temp) / "duplicate")
        test_tracked_target_refused(Path(temp) / "tracked")
        test_invalid_argv_is_not_echoed()
        test_private_creation_source_contract()
    print("v377 email security environment smoke passed")


if __name__ == "__main__":
    main()
