#!/usr/bin/env python3
"""DB-free fail-closed smoke for the explicit v371 owner bootstrap tool."""
from __future__ import annotations

import asyncio
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
SCRIPT = BACKEND / "scripts" / "bootstrap_owner_admin.py"
ENV_EXAMPLE = BACKEND / ".env.example"
EXPECTED_ALEMBIC_HEAD = "v377_auth_email_public_security"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND / "scripts"))
sys.path.insert(0, str(BACKEND))

import bootstrap_owner_admin as bootstrap  # noqa: E402
from app.core.config import Settings  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_config_defaults() -> None:
    fields = Settings.model_fields
    require(fields["owner_admin_bootstrap_enabled"].default is False, "owner bootstrap must default off")
    require(fields["owner_admin_username"].default == "", "owner username default must be empty")
    require(fields["owner_admin_email"].default == "", "owner email default must be empty")
    password_default = fields["owner_admin_password"].default
    require(
        password_default.get_secret_value() == "",
        "owner password default must be an empty SecretStr",
    )


def check_example_contract() -> None:
    source = ENV_EXAMPLE.read_text(encoding="utf-8")
    required_lines = {
        "OWNER_ADMIN_BOOTSTRAP_ENABLED=false",
        'OWNER_ADMIN_USERNAME=""',
        'OWNER_ADMIN_EMAIL=""',
        'OWNER_ADMIN_PASSWORD=""',
    }
    for line in required_lines:
        require(line in source, f".env.example is missing safe owner setting: {line}")
    require("OWNER_ADMIN_BOOTSTRAP_ENABLED=true" not in source, ".env.example enables owner bootstrap")


def check_disabled_cli_opens_no_database() -> None:
    env = os.environ.copy()
    env.update(
        {
            "DEBUG": "false",
            "ENVIRONMENT": "local",
            "DATABASE_URL": "postgresql+asyncpg://invalid:invalid@127.0.0.1:1/must_not_connect",
            "OWNER_ADMIN_BOOTSTRAP_ENABLED": "false",
            "OWNER_ADMIN_USERNAME": "",
            "OWNER_ADMIN_EMAIL": "",
            "OWNER_ADMIN_PASSWORD": "",
        }
    )
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=BACKEND,
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=15,
    )
    require(
        completed.returncode == bootstrap.EXIT_BLOCKED,
        "disabled owner bootstrap must use the explicit blocked exit code",
    )
    payload = json.loads(completed.stdout)
    require(payload.get("result") == bootstrap.BLOCKED_RESULT, "disabled preflight result changed")
    require(payload.get("cliExitCode") == bootstrap.EXIT_BLOCKED, "blocked exit code is not reported")
    require(payload.get("bootstrapEnabled") is False, "disabled preflight reported enabled")
    require(payload.get("databaseConnectionOpened") is False, "disabled preflight opened the database")
    require(payload.get("databaseMutationExecuted") is False, "disabled preflight mutated the database")
    require(payload.get("passwordOrHashReported") is False, "disabled preflight reported a secret")


def _bootstrap_values() -> bootstrap.OwnerBootstrapValues:
    return bootstrap.OwnerBootstrapValues(
        enabled=True,
        username="owner_admin",
        email_original="owner@example.invalid",
        email_canonical="owner@example.invalid",
        password="not-used-by-this-smoke",
        environment="production",
    )


def _clean_git_reader(head: str):  # type: ignore[no-untyped-def]
    def read(*arguments: str) -> str:
        if arguments == ("rev-parse", "--show-toplevel"):
            return str(ROOT)
        if arguments == ("rev-parse", "--verify", "HEAD"):
            return head
        if arguments == (
            "ls-files",
            "--error-unmatch",
            "--",
            "backend/scripts/bootstrap_owner_admin.py",
        ):
            return "backend/scripts/bootstrap_owner_admin.py"
        if arguments == (
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
            "--ignore-submodules=none",
        ):
            return ""
        raise AssertionError(f"unexpected Git query: {arguments!r}")

    return read


def _check_apply_preflight_blocks(
    *,
    approved_sha: object,
    confirm: str,
    git_reader,  # type: ignore[no-untyped-def]
    expected_reason: str,
) -> None:
    values = _bootstrap_values()
    original_load = bootstrap.load_local_settings
    original_values = bootstrap.owner_values
    original_git_read = bootstrap._git_read
    original_head = bootstrap.local_alembic_head
    original_factory = bootstrap.build_session_factory
    database_factory_called = False
    alembic_head_read = False

    def fail_if_database_factory_runs(_settings):  # type: ignore[no-untyped-def]
        nonlocal database_factory_called
        database_factory_called = True
        raise AssertionError("failed apply preflight reached database setup")

    def record_alembic_head() -> str:
        nonlocal alembic_head_read
        alembic_head_read = True
        return EXPECTED_ALEMBIC_HEAD

    bootstrap.load_local_settings = lambda: object()  # type: ignore[assignment]
    bootstrap.owner_values = lambda _settings: values  # type: ignore[assignment]
    bootstrap._git_read = git_reader  # type: ignore[assignment]
    bootstrap.local_alembic_head = record_alembic_head  # type: ignore[assignment]
    bootstrap.build_session_factory = fail_if_database_factory_runs  # type: ignore[assignment]
    try:
        try:
            asyncio.run(
                bootstrap.run(
                    SimpleNamespace(
                        apply=True,
                        approved_sha=approved_sha,
                        confirm=confirm,
                        json=True,
                    )
                )
            )
        except bootstrap.OwnerAdminBootstrapError as exc:
            require(expected_reason in str(exc), "apply preflight returned the wrong safe reason")
        else:
            raise AssertionError("invalid owner apply preflight was accepted")
    finally:
        bootstrap.load_local_settings = original_load
        bootstrap.owner_values = original_values
        bootstrap._git_read = original_git_read
        bootstrap.local_alembic_head = original_head
        bootstrap.build_session_factory = original_factory
    require(not database_factory_called, "invalid apply preflight opened database setup")
    require(not alembic_head_read, "invalid apply preflight reached Alembic setup")


def check_git_and_confirmation_blocks_before_database() -> None:
    values = _bootstrap_values()
    approved_sha = "a" * 40
    expected_confirmation = values.confirmation_for(approved_sha)
    require(
        values.identity_fingerprint == _bootstrap_values().identity_fingerprint,
        "identity fingerprint is unstable",
    )
    require(values.environment in expected_confirmation, "confirmation is not environment-bound")
    require(approved_sha in expected_confirmation, "confirmation is not approved-SHA-bound")
    require(values.identity_fingerprint in expected_confirmation, "confirmation is not identity-bound")
    require(values.username not in expected_confirmation, "confirmation exposes the owner username")
    require(values.email_canonical not in expected_confirmation, "confirmation exposes the owner email")
    require(values.password not in expected_confirmation, "confirmation exposes the owner password")
    changed_identity = bootstrap.OwnerBootstrapValues(
        enabled=True,
        username="different_owner",
        email_original=values.email_original,
        email_canonical=values.email_canonical,
        password=values.password,
        environment=values.environment,
    )
    require(
        changed_identity.identity_fingerprint != values.identity_fingerprint,
        "identity fingerprint ignores the username",
    )
    changed_email = bootstrap.OwnerBootstrapValues(
        enabled=True,
        username=values.username,
        email_original="other@example.invalid",
        email_canonical="other@example.invalid",
        password=values.password,
        environment=values.environment,
    )
    require(
        changed_email.identity_fingerprint != values.identity_fingerprint,
        "identity fingerprint ignores the email",
    )

    def no_git_queries(*_arguments: str) -> str:
        raise AssertionError("invalid SHA reached Git")
    _check_apply_preflight_blocks(
        approved_sha=None,
        confirm="",
        git_reader=no_git_queries,
        expected_reason="--approved-sha must be exactly",
    )
    _check_apply_preflight_blocks(
        approved_sha="A" * 40,
        confirm="",
        git_reader=no_git_queries,
        expected_reason="--approved-sha must be exactly",
    )
    _check_apply_preflight_blocks(
        approved_sha=approved_sha,
        confirm=expected_confirmation,
        git_reader=_clean_git_reader("b" * 40),
        expected_reason="does not match the current Git HEAD",
    )

    wrong_root_reader = _clean_git_reader(approved_sha)

    def mismatched_root_reader(*arguments: str) -> str:
        if arguments == ("rev-parse", "--show-toplevel"):
            return str(ROOT.parent)
        return wrong_root_reader(*arguments)

    _check_apply_preflight_blocks(
        approved_sha=approved_sha,
        confirm=expected_confirmation,
        git_reader=mismatched_root_reader,
        expected_reason="Git repository root does not match",
    )

    clean_reader = _clean_git_reader(approved_sha)

    def dirty_git_reader(*arguments: str) -> str:
        if arguments and arguments[0] == "status":
            return " M backend/scripts/bootstrap_owner_admin.py"
        return clean_reader(*arguments)

    _check_apply_preflight_blocks(
        approved_sha=approved_sha,
        confirm=expected_confirmation,
        git_reader=dirty_git_reader,
        expected_reason="tracked Git worktree or index is not clean",
    )

    def unavailable_git_reader(*_arguments: str) -> str:
        raise bootstrap.OwnerAdminBootstrapError("Git repository state is unavailable")

    _check_apply_preflight_blocks(
        approved_sha=approved_sha,
        confirm=expected_confirmation,
        git_reader=unavailable_git_reader,
        expected_reason="Git repository state is unavailable",
    )
    _check_apply_preflight_blocks(
        approved_sha=approved_sha,
        confirm="bootstrap-owner-admin-once:production",
        git_reader=clean_reader,
        expected_reason="--confirm must be exactly",
    )


def check_source_contract() -> None:
    script_source = SCRIPT.read_text(encoding="utf-8")
    app_imports: set[str] = set()
    for path in (BACKEND / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                app_imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                app_imports.add(node.module)
    require(
        not any("bootstrap_owner_admin" in module for module in app_imports),
        "FastAPI app imports owner bootstrap",
    )
    require("LOCK TABLE public.users IN EXCLUSIVE MODE" in script_source, "first-admin race lock missing")
    require("database is not at the local Alembic head" in script_source, "migration-head gate missing")
    require("an administrator already exists" in script_source, "existing-admin gate missing")
    require('"existingAdminCount"' in script_source, "existing-admin count is not reported")
    legacy_admin_without_password = SimpleNamespace(is_admin=True, password_hash=None)
    require(
        bootstrap._existing_admin(legacy_admin_without_password),
        "owner bootstrap allowed a legacy admin without a password hash",
    )
    require("not any(_existing_admin(user) for user in users)" in script_source, "apply admin gate missing")
    require(script_source.count("await session.commit()") == 1, "owner bootstrap must commit exactly once")
    require("email_verified_at=None" in script_source, "owner bootstrap must not self-verify email")
    require('"emailVerified": False' in script_source, "result must report unverified email")
    require("complete the normal email verification link" in script_source, "verification next action missing")
    require('"--approved-sha"' in script_source, "approved SHA CLI gate missing")
    require("GIT_OPTIONAL_LOCKS" in script_source, "Git read-only lock suppression missing")
    require('"ls-files"' in script_source, "running script tracked-source gate missing")
    require("--untracked-files=no" in script_source, "tracked-only cleanliness gate missing")
    require('parser.add_argument("--password"' not in script_source, "password must not be a CLI argument")
    require("print(values.password" not in script_source, "owner password is printed")
    require("print(password_hash" not in script_source, "owner password hash is printed")
    require(bootstrap.local_alembic_head() == EXPECTED_ALEMBIC_HEAD, "unexpected Alembic head")


def main() -> None:
    check_config_defaults()
    check_example_contract()
    check_disabled_cli_opens_no_database()
    check_git_and_confirmation_blocks_before_database()
    check_source_contract()
    print("OK: v371 owner admin explicit one-shot bootstrap smoke passed")


if __name__ == "__main__":
    main()
