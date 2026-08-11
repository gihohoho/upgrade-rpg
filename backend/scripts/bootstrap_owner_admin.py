"""Inspect or explicitly bootstrap the first owner administrator once.

This command never runs from the FastAPI lifespan.  The default mode is a
read-only preflight.  ``--apply`` is accepted only when the ignored backend
``.env`` explicitly enables the operation, ``--approved-sha`` names the exact
clean tracked Git HEAD, the database is at the local Alembic head, no
initialized administrator exists, and the source- and identity-bound
confirmation phrase matches exactly.

Exit status 0 means the read-only preflight is ready or the one-shot apply
succeeded.  Exit status 3 means the operation is safely blocked, including the
normal default where bootstrap is disabled.  Exit status 2 is reserved for an
unexpected failure or argparse usage error.  The disabled default still emits
a sanitized read-only report and never opens a database connection.

Run from any directory with ``backend/.venv`` Python.  Do not pass a password
on the command line: the process reads it from ``OWNER_ADMIN_PASSWORD`` and
never prints the password or its bcrypt hash.
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from pydantic import SecretStr
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT = BACKEND_DIR.parent
SCRIPT_RELATIVE_PATH = Path("backend/scripts/bootstrap_owner_admin.py")
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import Settings, build_database_connect_args  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import AdminChangeLog, User, UserProfile  # noqa: E402
from app.schemas.auth import (  # noqa: E402
    EmailValidationUnavailable,
    normalize_email_identity,
    normalize_username,
)


TOOL_VERSION = "v371.owner-admin-explicit-one-shot"
CONFIRM_PREFIX = "bootstrap-owner-admin-once"
BLOCKED_RESULT = "owner-admin-bootstrap-blocked"
READY_RESULT = "owner-admin-bootstrap-readonly-ready"
APPLIED_RESULT = "owner-admin-bootstrap-applied"
EXIT_SUCCESS = 0
EXIT_ERROR = 2
EXIT_BLOCKED = 3
FULL_GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDER_PASSWORDS = {
    "change-me",
    "change-me-before-production",
    "owner-admin-password",
    "password",
}


class OwnerAdminBootstrapError(RuntimeError):
    """Safe-to-display bootstrap contract failure."""


@dataclass(frozen=True)
class OwnerBootstrapValues:
    enabled: bool
    username: str
    email_original: str
    email_canonical: str
    password: str
    environment: str

    @property
    def identity_fingerprint(self) -> str:
        """Return a stable digest without exposing the username or email."""
        material = (
            "upgrade-rpg-owner-admin-identity-v1\0"
            f"{len(self.username)}:{self.username}\0"
            f"{len(self.email_canonical)}:{self.email_canonical}"
        ).encode("utf-8")
        return hashlib.sha256(material).hexdigest()

    def confirmation_for(self, approved_sha: str) -> str:
        return (
            f"{CONFIRM_PREFIX}:{self.environment}:sha-{approved_sha}:"
            f"identity-{self.identity_fingerprint}"
        )

    @property
    def confirmation_template(self) -> str:
        return (
            f"{CONFIRM_PREFIX}:{self.environment}:sha-<approved-sha>:"
            f"identity-{self.identity_fingerprint}"
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerAdminBootstrapError(message)


def load_local_settings() -> Settings:
    """Load the ignored backend .env regardless of the caller's working directory."""
    return Settings(_env_file=BACKEND_DIR / ".env")


def _secret_value(value: object) -> str:
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    return str(value or "")


def normalize_owner_email(value: str) -> tuple[str, str]:
    """Validate syntax and return display/canonical forms without claiming ownership."""
    try:
        normalized = normalize_email_identity(value)
    except EmailValidationUnavailable as exc:
        raise OwnerAdminBootstrapError(
            "email-validator dependency is required before owner bootstrap"
        ) from exc
    except ValueError as exc:
        raise OwnerAdminBootstrapError("OWNER_ADMIN_EMAIL is not a valid email address") from exc
    return normalized.original, normalized.canonical


def owner_values(settings: Settings) -> OwnerBootstrapValues:
    enabled = bool(getattr(settings, "owner_admin_bootstrap_enabled", False))
    environment = str(settings.environment or "local").strip().lower() or "local"
    if not enabled:
        return OwnerBootstrapValues(False, "", "", "", "", environment)

    raw_username = str(getattr(settings, "owner_admin_username", "") or "").strip()
    raw_email = str(getattr(settings, "owner_admin_email", "") or "").strip()
    password = _secret_value(getattr(settings, "owner_admin_password", SecretStr("")))

    try:
        username = normalize_username(raw_username)
    except ValueError as exc:
        raise OwnerAdminBootstrapError("OWNER_ADMIN_USERNAME is invalid") from exc
    email_original, email_canonical = normalize_owner_email(raw_email)

    require(len(password) >= 16, "OWNER_ADMIN_PASSWORD must contain at least 16 characters")
    require(len(password.encode("utf-8")) <= 72, "OWNER_ADMIN_PASSWORD exceeds bcrypt's 72-byte limit")
    require(any(character.isalpha() for character in password), "OWNER_ADMIN_PASSWORD must contain a letter")
    require(any(character.isdigit() for character in password), "OWNER_ADMIN_PASSWORD must contain a number")
    require(
        any(not character.isalnum() for character in password),
        "OWNER_ADMIN_PASSWORD must contain a symbol",
    )
    require(password.strip().lower() not in PLACEHOLDER_PASSWORDS, "OWNER_ADMIN_PASSWORD uses a blocked placeholder")

    return OwnerBootstrapValues(
        True,
        username,
        email_original,
        email_canonical,
        password,
        environment,
    )


def local_alembic_head() -> str:
    config = AlembicConfig(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    script = ScriptDirectory.from_config(config)
    head = script.get_current_head()
    require(bool(head), "local Alembic graph must have exactly one head")
    return str(head)


def _git_read(*arguments: str) -> str:
    """Run one local, read-only Git query and return sanitized stdout."""
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OwnerAdminBootstrapError("Git repository state is unavailable") from exc
    require(completed.returncode == 0, "Git repository state is unavailable")
    return completed.stdout.strip()


def validate_apply_source(approved_sha_value: object) -> str:
    """Bind apply to an exact clean tracked commit before any DB setup."""
    approved_sha = str(approved_sha_value or "")
    require(
        FULL_GIT_SHA_PATTERN.fullmatch(approved_sha) is not None,
        "--approved-sha must be exactly 40 lowercase hexadecimal characters",
    )

    repository_root = _git_read("rev-parse", "--show-toplevel")
    try:
        resolved_repository_root = Path(repository_root).resolve(strict=True)
        resolved_expected_root = ROOT.resolve(strict=True)
    except OSError as exc:
        raise OwnerAdminBootstrapError("Git repository state is unavailable") from exc
    require(
        resolved_repository_root == resolved_expected_root,
        "Git repository root does not match the project root",
    )

    current_head = _git_read("rev-parse", "--verify", "HEAD")
    require(
        FULL_GIT_SHA_PATTERN.fullmatch(current_head) is not None,
        "Git HEAD is not an exact 40-character commit SHA",
    )
    require(current_head == approved_sha, "--approved-sha does not match the current Git HEAD")

    script_relative_path = SCRIPT_RELATIVE_PATH.as_posix()
    tracked_script = _git_read(
        "ls-files",
        "--error-unmatch",
        "--",
        script_relative_path,
    )
    require(
        tracked_script == script_relative_path,
        "owner bootstrap script is not tracked by the approved Git HEAD",
    )

    tracked_status = _git_read(
        "status",
        "--porcelain=v1",
        "--untracked-files=no",
        "--ignore-submodules=none",
    )
    require(not tracked_status, "tracked Git worktree or index is not clean")

    confirmed_head = _git_read("rev-parse", "--verify", "HEAD")
    require(
        confirmed_head == approved_sha,
        "Git HEAD changed while validating the approved source",
    )
    return current_head


def build_session_factory(settings: Settings):  # type: ignore[no-untyped-def]
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        hide_parameters=True,
        pool_pre_ping=settings.db_pool_pre_ping,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_recycle=settings.db_pool_recycle_seconds,
        connect_args=build_database_connect_args(settings),
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def database_revision(session: AsyncSession) -> str:
    result = await session.execute(text("SELECT version_num FROM public.alembic_version"))
    revisions = [str(value) for value in result.scalars().all()]
    require(len(revisions) == 1, "database must contain exactly one Alembic revision row")
    return revisions[0]


def _existing_admin(user: User) -> bool:
    """Treat every admin row as initialized for the stricter owner one-shot gate."""
    return bool(user.is_admin)


def _safe_user_state(user: User | None) -> dict[str, bool]:
    if user is None:
        return {"exists": False, "isAdmin": False, "isActive": False, "emailVerified": False}
    return {
        "exists": True,
        "isAdmin": bool(user.is_admin),
        "isActive": bool(user.is_active),
        "emailVerified": bool(user.email_verified_at),
    }


async def inspect_database(
    session: AsyncSession,
    *,
    values: OwnerBootstrapValues,
    expected_head: str,
) -> dict[str, Any]:
    actual_head = await database_revision(session)
    users = list((await session.execute(select(User).order_by(User.id))).scalars().all())
    existing_admin_count = sum(1 for user in users if _existing_admin(user))
    username_matches = [user for user in users if str(user.username) == values.username]
    email_matches = [
        user
        for user in users
        if str(user.email_canonical or "") == values.email_canonical
    ]
    conflicts = bool(
        len(username_matches) > 1
        or len(email_matches) > 1
        or (
            username_matches
            and email_matches
            and int(username_matches[0].id) != int(email_matches[0].id)
        )
        or (
            username_matches
            and username_matches[0].email_canonical
            not in {None, values.email_canonical}
        )
        or (email_matches and str(email_matches[0].username) != values.username)
    )
    ready = actual_head == expected_head and existing_admin_count == 0 and not conflicts
    return {
        "toolVersion": TOOL_VERSION,
        "mode": "inspect",
        "result": READY_RESULT if ready else BLOCKED_RESULT,
        "ready": ready,
        "bootstrapEnabled": True,
        "migrationHeadMatches": actual_head == expected_head,
        "existingAdminCount": existing_admin_count,
        "identityConflict": conflicts,
        "targetMode": "promote" if username_matches or email_matches else "create",
        "identityFingerprint": values.identity_fingerprint,
        "applyConfirmationTemplate": values.confirmation_template,
        "databaseMutationExecuted": False,
        "passwordOrHashReported": False,
    }


async def apply_bootstrap(
    session: AsyncSession,
    *,
    values: OwnerBootstrapValues,
    expected_head: str,
) -> dict[str, Any]:
    # Hash before acquiring the table lock so the write-critical section remains short.
    password_hash = await asyncio.to_thread(hash_password, values.password)

    # PostgreSQL EXCLUSIVE table lock prevents a concurrent first-admin API request
    # or second CLI process from inserting/promoting a different administrator after
    # this transaction checks the one-time precondition.
    await session.execute(text("LOCK TABLE public.users IN EXCLUSIVE MODE"))
    actual_head = await database_revision(session)
    require(actual_head == expected_head, "database is not at the local Alembic head")

    users = list(
        (await session.execute(select(User).order_by(User.id).with_for_update())).scalars().all()
    )
    require(
        not any(_existing_admin(user) for user in users),
        "an administrator already exists",
    )

    username_matches = [user for user in users if str(user.username) == values.username]
    email_matches = [
        user
        for user in users
        if str(user.email_canonical or "") == values.email_canonical
    ]
    require(len(username_matches) <= 1 and len(email_matches) <= 1, "owner identity is not unique")
    if username_matches and email_matches:
        require(
            int(username_matches[0].id) == int(email_matches[0].id),
            "owner username and email belong to different accounts",
        )
    target = (username_matches or email_matches or [None])[0]
    if target is not None:
        require(
            target.email_canonical in {None, values.email_canonical},
            "owner username belongs to another email",
        )
        require(str(target.username) == values.username, "owner email belongs to another username")

    before = _safe_user_state(target)
    action = "promoted"
    if target is None:
        action = "created"
        target = User(
            username=values.username,
            email_original=values.email_original,
            email_canonical=values.email_canonical,
            email_verified_at=None,
            password_hash=password_hash,
            auth_version=1,
            is_active=True,
            is_admin=True,
        )
        session.add(target)
        await session.flush()
        session.add(UserProfile(user_id=int(target.id)))
    else:
        target.email_original = values.email_original
        target.email_canonical = values.email_canonical
        # A value in .env proves neither mailbox ownership nor control. The
        # owner must still complete the normal email-verification link flow.
        target.email_verified_at = None
        target.password_hash = password_hash
        target.auth_version = max(1, int(target.auth_version or 0) + 1)
        target.is_active = True
        target.is_admin = True
        profile_exists = (
            await session.execute(select(UserProfile.id).where(UserProfile.user_id == int(target.id)))
        ).scalar_one_or_none()
        if profile_exists is None:
            session.add(UserProfile(user_id=int(target.id)))

    after = _safe_user_state(target)
    session.add(
        AdminChangeLog(
            admin_user_id=int(target.id),
            target_type="user",
            target_id=str(target.id),
            action="create" if action == "created" else "update",
            reason="explicit owner administrator one-shot bootstrap",
            before_json=before,
            after_json=after,
            rollback_json={},
            applied=True,
        )
    )
    await session.commit()
    return {
        "toolVersion": TOOL_VERSION,
        "mode": "apply",
        "result": APPLIED_RESULT,
        "ready": False,
        "applied": True,
        "action": action,
        "userId": int(target.id),
        "emailVerified": False,
        "isAdmin": True,
        "databaseMutationExecuted": True,
        "commitCount": 1,
        "passwordOrHashReported": False,
        "nextRequiredAction": (
            "set OWNER_ADMIN_BOOTSTRAP_ENABLED=false, remove OWNER_ADMIN_PASSWORD, "
            "then request and complete the normal email verification link before login"
        ),
    }


async def run(args: argparse.Namespace) -> dict[str, Any]:
    settings = load_local_settings()
    values = owner_values(settings)
    if not values.enabled:
        require(not args.apply, "OWNER_ADMIN_BOOTSTRAP_ENABLED must be true for --apply")
        return {
            "toolVersion": TOOL_VERSION,
            "mode": "inspect",
            "result": BLOCKED_RESULT,
            "ready": False,
            "bootstrapEnabled": False,
            "databaseConnectionOpened": False,
            "databaseMutationExecuted": False,
            "passwordOrHashReported": False,
        }

    if args.apply:
        approved_sha = validate_apply_source(getattr(args, "approved_sha", None))
        expected_confirmation = values.confirmation_for(approved_sha)
        require(
            str(args.confirm or "") == expected_confirmation,
            f"--confirm must be exactly {expected_confirmation}",
        )

    expected_head = local_alembic_head()

    engine, session_factory = build_session_factory(settings)
    try:
        async with session_factory() as session:
            if args.apply:
                try:
                    return await apply_bootstrap(
                        session,
                        values=values,
                        expected_head=expected_head,
                    )
                except Exception:
                    await session.rollback()
                    raise
            result = await inspect_database(
                session,
                values=values,
                expected_head=expected_head,
            )
            await session.rollback()
            return result
    finally:
        await engine.dispose()


def print_result(result: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"mode: {result.get('mode')}")
    print(f"bootstrap enabled: {'yes' if result.get('bootstrapEnabled', True) else 'no'}")
    print(f"ready: {'yes' if result.get('ready') else 'no'}")
    print(f"database mutation executed: {'yes' if result.get('databaseMutationExecuted') else 'no'}")
    print(f"password/hash reported: {'yes' if result.get('passwordOrHashReported') else 'no'}")
    if result.get("expectedConfirmation"):
        print(f"apply confirmation: {result['expectedConfirmation']}")
    if result.get("applyConfirmationTemplate"):
        print(f"apply confirmation template: {result['applyConfirmationTemplate']}")
    if result.get("nextRequiredAction"):
        print(f"next required action: {result['nextRequiredAction']}")
    print(f"result: {result.get('result')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="execute the guarded one-shot mutation")
    parser.add_argument(
        "--approved-sha",
        help="required with --apply: exact lowercase 40-hex clean Git HEAD approved by the owner",
    )
    parser.add_argument(
        "--confirm",
        help="exact environment-, approved-SHA-, and identity-fingerprint-bound phrase",
    )
    parser.add_argument("--json", action="store_true", help="print sanitized JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = asyncio.run(run(args))
    except OwnerAdminBootstrapError as exc:
        result = {
            "toolVersion": TOOL_VERSION,
            "mode": "apply" if args.apply else "inspect",
            "result": BLOCKED_RESULT,
            "reason": str(exc),
            "databaseMutationExecuted": False,
            "passwordOrHashReported": False,
        }
        exit_code = EXIT_BLOCKED
    except Exception as exc:
        # Do not render exception values: DB drivers and validation libraries can
        # include connection details or submitted input in their messages.
        result = {
            "toolVersion": TOOL_VERSION,
            "mode": "apply" if args.apply else "inspect",
            "result": BLOCKED_RESULT,
            "reason": f"unexpected {type(exc).__name__}; details suppressed",
            "databaseMutationExecuted": False,
            "passwordOrHashReported": False,
        }
        exit_code = EXIT_ERROR
    else:
        if result.get("result") in {READY_RESULT, APPLIED_RESULT}:
            exit_code = EXIT_SUCCESS
        elif result.get("result") == BLOCKED_RESULT:
            exit_code = EXIT_BLOCKED
        else:
            exit_code = EXIT_ERROR
    result["cliExitCode"] = exit_code
    print_result(result, as_json=args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
