#!/usr/bin/env python3
"""Prepare and validate the Git-ignored Render environment without leaking values."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from check_neon_readonly_connectivity import (
    ConnectionTarget,
    NeonCheckError,
    _load_local_values,
    _validate_pair,
)


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "deploy/.env.production"
PLAN_FILE = ROOT / "deploy/render-service-settings.example.json"
VERSION = "v346.render-service-creation-preparation-ready-exact-sha-gated"
RESULT = "render-service-creation-preparation-ready-exact-sha-gated"
NEXT_STAGE = "owner-approve-render-service-creation-preparation-sha"
SERVICE_NAME = "upgrade-rpg-api"
IMAGE_REFERENCE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
)
EXECUTION_ACTION = "create-inject-deploy-once-and-read-health"

NON_SECRET_VALUES = {
    "APP_NAME": "Upgrade RPG Backend",
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "PORT": "8000",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "1440",
    "CORS_ORIGINS": "[]",
    "DB_POOL_PRE_PING": "true",
    "DB_POOL_SIZE": "2",
    "DB_MAX_OVERFLOW": "0",
    "DB_POOL_TIMEOUT_SECONDS": "30",
    "DB_POOL_RECYCLE_SECONDS": "300",
}
SECRET_KEYS = ("DATABASE_URL", "JWT_SECRET_KEY", "ADMIN_WRITE_DEV_KEY")
NEON_KEYS = ("NEON_DIRECT_DATABASE_URL", "NEON_POOLED_DATABASE_URL")
LOCAL_UNSAFE_VALUES = {"change-me-before-production", "local-admin-dev-key"}


class RenderEnvironmentError(RuntimeError):
    """A safe-to-display local preparation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderEnvironmentError(message)


def build_asyncpg_url(target: ConnectionTarget) -> str:
    """Convert the validated direct Neon target to a query-free SQLAlchemy URL."""
    user = quote(target.user, safe="")
    password = quote(target.password, safe="")
    database = quote(target.database, safe="")
    return f"postgresql+asyncpg://{user}:{password}@{target.host}:{target.port}/{database}"


def generate_secret() -> str:
    return secrets.token_urlsafe(48)


def validate_secret(name: str, value: str) -> None:
    require(len(value.strip()) >= 43, f"{name} must contain at least 43 characters")
    require(value == value.strip(), f"{name} must not contain surrounding whitespace")
    require(value not in LOCAL_UNSAFE_VALUES, f"{name} uses a local unsafe default")
    require("\n" not in value and "\r" not in value, f"{name} must remain one line")


def validate_render_values(
    values: dict[str, str], direct: ConnectionTarget
) -> dict[str, object]:
    for key, expected in NON_SECRET_VALUES.items():
        require(values.get(key) == expected, f"Render environment differs: {key}")
    for key in (*NEON_KEYS, *SECRET_KEYS):
        require(bool(values.get(key)), f"Render local environment is missing {key}")

    parsed = urlsplit(values["DATABASE_URL"])
    require(parsed.scheme == "postgresql+asyncpg", "DATABASE_URL scheme differs")
    require(not parsed.query and not parsed.fragment, "DATABASE_URL must not contain query or fragment")
    require((parsed.hostname or "").lower() == direct.host, "DATABASE_URL host differs from Neon direct")
    require((parsed.port or 5432) == direct.port, "DATABASE_URL port differs from Neon direct")
    require(unquote(parsed.username or "") == direct.user, "DATABASE_URL role differs from Neon direct")
    require(unquote(parsed.password or "") == direct.password, "DATABASE_URL credential differs from Neon direct")
    require(unquote(parsed.path.lstrip("/")) == direct.database, "DATABASE_URL database differs from Neon direct")

    validate_secret("JWT_SECRET_KEY", values["JWT_SECRET_KEY"])
    validate_secret("ADMIN_WRITE_DEV_KEY", values["ADMIN_WRITE_DEV_KEY"])
    require(
        values["JWT_SECRET_KEY"] != values["ADMIN_WRITE_DEV_KEY"],
        "JWT_SECRET_KEY and ADMIN_WRITE_DEV_KEY must differ",
    )
    return {
        "schemaVersion": VERSION,
        "requiredKeyCount": len(NON_SECRET_VALUES) + len(SECRET_KEYS),
        "secretKeyCount": len(SECRET_KEYS),
        "databaseUrlUsesDirectAsyncpgWithoutQuery": True,
        "productionSecretsStrongAndDistinct": True,
        "actualValuesDisplayed": False,
        "result": RESULT,
        "nextSafeStage": NEXT_STAGE,
    }


def prepare_values(existing: dict[str, str]) -> tuple[dict[str, str], dict[str, bool]]:
    try:
        direct, _pooled = _validate_pair(existing)
    except NeonCheckError as exc:
        raise RenderEnvironmentError(str(exc)) from None

    prepared = dict(existing)
    generated: dict[str, bool] = {}
    prepared["DATABASE_URL"] = build_asyncpg_url(direct)
    for key in ("JWT_SECRET_KEY", "ADMIN_WRITE_DEV_KEY"):
        current = prepared.get(key, "")
        if current:
            validate_secret(key, current)
            generated[key] = False
        else:
            prepared[key] = generate_secret()
            generated[key] = True
    prepared.update(NON_SECRET_VALUES)
    validate_render_values(prepared, direct)
    return prepared, generated


def render_env_file(values: dict[str, str]) -> str:
    lines = [
        "# Local-only Render/Neon values. Git and Docker context excluded.",
        "# Never print, commit, archive, or paste this file.",
        "",
        *(f"{key}={values[key]}" for key in NEON_KEYS),
        "",
        *(f"{key}={values[key]}" for key in NON_SECRET_VALUES),
        "",
        *(f"{key}={values[key]}" for key in SECRET_KEYS),
        "",
    ]
    return "\n".join(lines)


def write_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def verify_local_values_absent_from_git(values: dict[str, str]) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    require(completed.returncode == 0, "Git tracked-file inventory failed")
    sensitive = {
        values[key].encode("utf-8")
        for key in (*NEON_KEYS, *SECRET_KEYS)
        if values.get(key)
    }
    for key in (*NEON_KEYS, "DATABASE_URL"):
        parsed = urlsplit(values[key])
        for component in (parsed.hostname, unquote(parsed.password or "")):
            if component:
                sensitive.add(component.encode("utf-8"))
    for relative_bytes in completed.stdout.split(b"\0"):
        if not relative_bytes:
            continue
        path = ROOT / os.fsdecode(relative_bytes)
        try:
            content = path.read_bytes()
        except OSError:
            raise RenderEnvironmentError("a Git tracked file could not be inspected") from None
        require(
            not any(value in content for value in sensitive),
            "a local Render or Neon value appears in a Git tracked file",
        )


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(completed.returncode == 0, "Git approval preflight failed")
    return completed.stdout.strip()


def require_exact_execution_approval(
    *,
    preparation_sha: str,
    service: str,
    image: str,
    action: str,
) -> None:
    require(
        re.fullmatch(r"[0-9a-f]{40}", preparation_sha) is not None,
        "preparation SHA must be exactly 40 lowercase hexadecimal characters",
    )
    require(service == SERVICE_NAME, "confirmed Render service name differs")
    require(image == IMAGE_REFERENCE, "confirmed exact image reference differs")
    require(action == EXECUTION_ACTION, "confirmed Render execution action differs")
    require(git_output("branch", "--show-current") == "main", "Render execution requires main")
    require(git_output("status", "--porcelain") == "", "Render execution requires a clean worktree")
    require(git_output("rev-parse", "HEAD") == preparation_sha, "approved SHA differs from HEAD")
    require(
        git_output("rev-parse", "--verify", "origin/main") == preparation_sha,
        "approved SHA differs from origin/main",
    )

    try:
        plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise RenderEnvironmentError("Render service plan is invalid") from None
    gate = plan.get("creationGate") or {}
    require(plan.get("schemaVersion") == VERSION, "Render service plan version differs")
    require(gate.get("exactPreparationShaApprovalRequired") is True, "exact-SHA gate is missing")
    require(gate.get("webServiceCreated") is False, "Render service is already recorded as created")
    require(gate.get("deploymentExecuted") is False, "Render deployment is already recorded as executed")


def load_and_validate() -> dict[str, object]:
    try:
        values = _load_local_values(ENV_FILE)
        direct, _pooled = _validate_pair(values)
    except NeonCheckError as exc:
        raise RenderEnvironmentError(str(exc)) from None
    summary = validate_render_values(values, direct)
    verify_local_values_absent_from_git(values)
    summary["exactLocalValuesAbsentFromGitTrackedFiles"] = True
    return summary


def print_summary(summary: dict[str, object], *, generated: dict[str, bool] | None = None) -> None:
    print("Render local environment preparation (secret-safe)")
    print(f"- required Render keys ready: {summary['requiredKeyCount']}")
    print("- database URL: direct asyncpg / TLS query absent")
    print("- JWT/admin secrets: strong / distinct")
    if generated is not None:
        print(f"- JWT secret generated now: {'yes' if generated['JWT_SECRET_KEY'] else 'no (preserved)'}")
        print(f"- admin key generated now: {'yes' if generated['ADMIN_WRITE_DEV_KEY'] else 'no (preserved)'}")
    print("- actual secret or endpoint displayed: no")
    print("- Render resource mutation: no")
    print(f"- result: {summary['result']}")
    print(f"- next safe stage: {summary['nextSafeStage']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute-local", action="store_true", help="prepare the ignored local env file")
    mode.add_argument("--inspect-local", action="store_true", help="validate the ignored local env file")
    mode.add_argument(
        "--verify-execution-approval",
        action="store_true",
        help="verify the exact-SHA Render execution approval without provider mutation",
    )
    parser.add_argument("--confirm-preparation-sha")
    parser.add_argument("--confirm-service")
    parser.add_argument("--confirm-image")
    parser.add_argument("--confirm-action")
    args = parser.parse_args()

    try:
        require(PLAN_FILE.is_file(), "Render service plan is missing")
        if args.execute_local:
            try:
                existing = _load_local_values(ENV_FILE)
            except NeonCheckError as exc:
                raise RenderEnvironmentError(str(exc)) from None
            prepared, generated = prepare_values(existing)
            write_atomic(ENV_FILE, render_env_file(prepared))
            summary = load_and_validate()
            print_summary(summary, generated=generated)
        elif args.inspect_local:
            print_summary(load_and_validate())
        elif args.verify_execution_approval:
            load_and_validate()
            require_exact_execution_approval(
                preparation_sha=args.confirm_preparation_sha or "",
                service=args.confirm_service or "",
                image=args.confirm_image or "",
                action=args.confirm_action or "",
            )
            print("Render execution approval verification (no provider mutation)")
            print("- clean pushed main exact SHA: verified")
            print("- service / exact image / single-deploy action: verified")
            print("- local environment and Git exclusion: verified")
            print("- Render resource mutation: no")
            print(f"- result: {RESULT}")
            print("- next safe stage: create-render-service-and-deploy-once")
        else:
            print("Render local environment preparation (static)")
            print(f"- local target: {ENV_FILE.relative_to(ROOT)} (Git/Docker excluded)")
            print("- execution requested: no")
            print("- Render resource mutation: no")
            print(f"- result: {RESULT}")
            print(f"- next safe stage: {NEXT_STAGE}")
    except RenderEnvironmentError as exc:
        print(f"Render local environment preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
