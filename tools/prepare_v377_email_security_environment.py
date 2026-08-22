#!/usr/bin/env python3
"""Plan or apply the secret-safe v377 email security environment defaults.

The default command is read-only and refuses to read a dotenv file whose private
filesystem permissions have not already been verified. ``--apply`` is the only
mode that repairs permissions or writes the two Git-ignored dotenv files. Both
files are validated and staged before replacement. Secret values are never
accepted as command-line arguments or included in reports/errors.
"""

from __future__ import annotations

from dataclasses import dataclass
import codecs
import hmac
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from typing import Callable

from private_artifacts import (
    PrivatePathError,
    create_private_file,
    ensure_private_path_location,
    harden_private_file,
    harden_private_tree,
    verify_private_file,
    verify_private_tree,
)


ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV_PATH = Path("backend/.env")
PRODUCTION_ENV_PATH = Path("deploy/.env.production")
PRIVATE_ARTIFACT_DIRECTORIES = (
    Path("local-backups/postgres"),
    Path("local-review-artifacts/alembic"),
    Path("local-review-artifacts/neon"),
)
PRIVATE_ARTIFACT_ROOT_DIRECTORIES = (
    Path("local-backups"),
    Path("local-review-artifacts"),
)

EMAIL_TOKEN_SECRET = "EMAIL_TOKEN_SECRET"
AUTH_ABUSE_SECRET = "AUTH_ABUSE_SECRET"
GENERATED_SECRET_KEYS = (EMAIL_TOKEN_SECRET, AUTH_ABUSE_SECRET)
COMPARISON_SECRET_KEYS = (
    "JWT_SECRET_KEY",
    "ADMIN_WRITE_DEV_KEY",
    *GENERATED_SECRET_KEYS,
)
EXTERNAL_SECRET_KEYS = ("BREVO_API_KEY", "BREVO_FROM_EMAIL")
LOCAL_SECRET_DEFAULTS = {
    "change-me-before-production-email-token",
    "change-me-before-production-auth-abuse",
}
PLACEHOLDER_RE = re.compile(r"^<[^\r\n>]+>$")
ASSIGNMENT_RE = re.compile(
    r"^(?P<prefix>[ \t]*(?:export[ \t]+)?"
    r"(?P<key>[A-Z][A-Z0-9_]*)[ \t]*=[ \t]*)(?P<raw>.*)$"
)

COMMON_DEFAULTS = {
    "EMAIL_PROVIDER": "brevo",
    "BREVO_FROM_NAME": "Upgrade RPG",
    "EMAIL_DELIVERY_TIMEOUT_SECONDS": "10",
    "EMAIL_VERIFICATION_EXPIRE_MINUTES": "1440",
    "PASSWORD_RESET_EXPIRE_MINUTES": "30",
    "ACCOUNT_DELETION_EXPIRE_MINUTES": "30",
    "EMAIL_OUTBOX_WORKER_ENABLED": "true",
    "EMAIL_OUTBOX_POLL_SECONDS": "1",
    "EMAIL_OUTBOX_MAINTENANCE_INTERVAL_SECONDS": "300",
    "EMAIL_OUTBOX_PREPARING_TIMEOUT_SECONDS": "300",
    "EMAIL_OUTBOX_SENDING_TIMEOUT_SECONDS": "120",
    "EMAIL_OUTBOX_RETENTION_DAYS": "30",
    "REQUEST_BODY_LIMIT_BYTES": "2100000",
    "AUTH_REQUEST_BODY_LIMIT_BYTES": "16384",
    "AUTH_DISCOVERY_RESPONSE_FLOOR_MS": "350",
    "AUTH_DISCOVERY_RESPONSE_JITTER_MS": "100",
    "AUTH_RATE_LIMIT_RETENTION_DAYS": "30",
    "UNVERIFIED_ACCOUNT_TTL_HOURS": "168",
}


class EmailEnvironmentError(RuntimeError):
    """A failure message that is safe to display without secret redaction."""


@dataclass(frozen=True)
class EnvironmentSpec:
    label: str
    relative_path: Path
    defaults: dict[str, str]


@dataclass(frozen=True)
class Assignment:
    key: str
    line_index: int
    prefix: str
    suffix: str
    newline: str
    value: str


@dataclass(frozen=True)
class EnvironmentDocument:
    spec: EnvironmentSpec
    path: Path
    original: bytes
    had_bom: bool
    lines: tuple[str, ...]
    assignments: dict[str, Assignment]
    newline: str


@dataclass(frozen=True)
class PreparationSummary:
    mode: str
    file_change_count: int
    secret_generation_count: int
    strong_secret_preserve_count: int
    nonsecret_update_count: int
    missing_external_actions: tuple[str, ...]
    file_write_count: int


@dataclass(frozen=True)
class _PreparedDocument:
    document: EnvironmentDocument
    content: bytes
    secret_generation_count: int
    strong_secret_preserve_count: int
    nonsecret_update_count: int


LOCAL_SPEC = EnvironmentSpec(
    label="local",
    relative_path=LOCAL_ENV_PATH,
    defaults={
        **COMMON_DEFAULTS,
        "PUBLIC_FRONTEND_ORIGIN": "http://127.0.0.1:5500",
        "AUTH_TRUSTED_PROXY_MODE": "direct",
    },
)
PRODUCTION_SPEC = EnvironmentSpec(
    label="production",
    relative_path=PRODUCTION_ENV_PATH,
    defaults={
        **COMMON_DEFAULTS,
        "PUBLIC_FRONTEND_ORIGIN": "https://gihohoho-upgrade-rpg.onrender.com",
        "AUTH_TRUSTED_PROXY_MODE": "render",
        "CORS_ORIGINS": '["https://gihohoho-upgrade-rpg.onrender.com"]',
    },
)
ENVIRONMENT_SPECS = (LOCAL_SPEC, PRODUCTION_SPEC)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EmailEnvironmentError(message)


def _split_raw_value(raw: str) -> tuple[str, str]:
    """Return the dotenv value token and untouched whitespace/comment suffix."""
    if not raw:
        return "", ""
    if raw[0] in {'"', "'"}:
        quote = raw[0]
        escaped = False
        for index in range(1, len(raw)):
            character = raw[index]
            if quote == '"' and character == "\\" and not escaped:
                escaped = True
                continue
            if character == quote and not escaped:
                return raw[: index + 1], raw[index + 1 :]
            escaped = False
        return raw, ""
    comment = re.search(r"(?:[ \t]+#|^#)", raw)
    if comment is None:
        return raw.rstrip(" \t"), raw[len(raw.rstrip(" \t")) :]
    return raw[: comment.start()].rstrip(" \t"), raw[comment.start() :]


def _decode_value(token: str) -> str:
    stripped = token.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {'"', "'"}:
        return stripped[1:-1]
    return stripped


def _render_value(value: str) -> str:
    if re.search(r"[\r\n]", value):
        raise EmailEnvironmentError("a managed value is not a safe single-line value")
    if re.search(r"[ \t]", value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _read_document(root: Path, spec: EnvironmentSpec) -> EnvironmentDocument:
    path = root / spec.relative_path
    try:
        original = path.read_bytes() if path.exists() else b""
        had_bom = original.startswith(codecs.BOM_UTF8)
        payload = original[len(codecs.BOM_UTF8) :] if had_bom else original
        text = payload.decode("utf-8")
    except (OSError, UnicodeError):
        raise EmailEnvironmentError(f"{spec.label} environment could not be read safely") from None

    lines = tuple(text.splitlines(keepends=True))
    newline = "\r\n" if "\r\n" in text else "\n"
    assignments: dict[str, Assignment] = {}
    for line_index, line in enumerate(lines):
        line_without_newline = line.rstrip("\r\n")
        line_newline = line[len(line_without_newline) :]
        match = ASSIGNMENT_RE.match(line_without_newline)
        if match is None:
            continue
        key = match.group("key")
        if key in assignments:
            raise EmailEnvironmentError(
                f"{spec.label} environment has a duplicate assignment for {key}"
            )
        token, suffix = _split_raw_value(match.group("raw"))
        assignments[key] = Assignment(
            key=key,
            line_index=line_index,
            prefix=match.group("prefix"),
            suffix=suffix,
            newline=line_newline,
            value=_decode_value(token),
        )
    return EnvironmentDocument(
        spec=spec,
        path=path,
        original=original,
        had_bom=had_bom,
        lines=lines,
        assignments=assignments,
        newline=newline,
    )


def _prepare_environment_paths(root: Path, *, harden: bool) -> None:
    """Validate all Git paths, then protect env and existing DB evidence."""
    try:
        environment_paths: list[Path] = []
        for spec in ENVIRONMENT_SPECS:
            path = root / spec.relative_path
            ensure_private_path_location(root, path)
            _require_ignored_untracked(root, spec)
            environment_paths.append(path)

        artifact_root_paths: list[Path] = []
        artifact_paths: list[Path] = []
        for relative_path in (
            *PRIVATE_ARTIFACT_ROOT_DIRECTORIES,
            *PRIVATE_ARTIFACT_DIRECTORIES,
        ):
            path = root / relative_path
            ensure_private_path_location(root, path)
            if not os.path.lexists(os.fspath(path)):
                continue
            _require_ignored_untracked_directory(root, relative_path)
            if not path.is_dir():
                raise PrivatePathError("private artifact path type is unsafe")
            if relative_path in PRIVATE_ARTIFACT_ROOT_DIRECTORIES:
                artifact_root_paths.append(path)
            else:
                artifact_paths.append(path)

        for path in environment_paths:
            if os.path.lexists(os.fspath(path)):
                if harden:
                    harden_private_file(path)
                else:
                    verify_private_file(path)
        for path in (*artifact_root_paths, *artifact_paths):
            if harden:
                harden_private_tree(path)
            else:
                verify_private_tree(path)
    except PrivatePathError:
        raise EmailEnvironmentError(
            "environment or private-artifact permission verification failed"
        ) from None


def _current_value(document: EnvironmentDocument, key: str) -> str:
    assignment = document.assignments.get(key)
    return assignment.value if assignment is not None else ""


def _is_replaceable_secret(value: str) -> bool:
    return not value or value in LOCAL_SECRET_DEFAULTS


def _validate_strong_secret(label: str, key: str, value: str) -> None:
    _require(len(value) >= 32, f"{label}.{key} is not a strong existing secret")
    _require(value == value.strip(), f"{label}.{key} has unsafe surrounding whitespace")
    _require(not re.search(r"[\r\n]", value), f"{label}.{key} must be one line")
    _require(not PLACEHOLDER_RE.fullmatch(value), f"{label}.{key} is a placeholder")


def _known_secret_entries(
    documents: tuple[EnvironmentDocument, ...],
    overrides: dict[tuple[str, str], str] | None = None,
) -> list[tuple[str, str]]:
    overrides = overrides or {}
    entries: list[tuple[str, str]] = []
    for document in documents:
        for key in COMPARISON_SECRET_KEYS:
            value = overrides.get(
                (document.spec.label, key),
                _current_value(document, key),
            )
            if (
                key in GENERATED_SECRET_KEYS
                and (document.spec.label, key) not in overrides
                and _is_replaceable_secret(value)
            ):
                continue
            if value:
                entries.append((f"{document.spec.label}.{key}", value))
    return entries


def _validate_distinct(entries: list[tuple[str, str]]) -> None:
    for index, (left_label, left_value) in enumerate(entries):
        for right_label, right_value in entries[index + 1 :]:
            if hmac.compare_digest(left_value, right_value):
                raise EmailEnvironmentError(
                    f"application secrets must be distinct: {left_label} and {right_label}"
                )


def _is_external_action_missing(value: str) -> bool:
    stripped = value.strip()
    return not stripped or PLACEHOLDER_RE.fullmatch(stripped) is not None


def _render_document(
    document: EnvironmentDocument,
    updates: dict[str, str],
) -> bytes:
    lines = list(document.lines)
    missing: list[tuple[str, str]] = []
    for key, value in updates.items():
        rendered = _render_value(value)
        assignment = document.assignments.get(key)
        if assignment is None:
            missing.append((key, rendered))
            continue
        lines[assignment.line_index] = (
            f"{assignment.prefix}{rendered}{assignment.suffix}{assignment.newline}"
        )

    if missing:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] = f"{lines[-1]}{document.newline}"
        if lines and lines[-1].strip():
            lines.append(document.newline)
        lines.append(
            f"# v377 email security defaults (managed; secret values stay local)"
            f"{document.newline}"
        )
        lines.extend(f"{key}={value}{document.newline}" for key, value in missing)

    payload = "".join(lines).encode("utf-8")
    return (codecs.BOM_UTF8 if document.had_bom else b"") + payload


def _git_command(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
        )
    except OSError:
        raise EmailEnvironmentError("Git ignore verification could not run") from None


def _require_ignored_untracked(root: Path, spec: EnvironmentSpec) -> None:
    relative = spec.relative_path.as_posix()
    tracked = _git_command(root, "ls-files", "--error-unmatch", "--", relative)
    _require(
        tracked.returncode != 0,
        f"refusing to write tracked file: {relative}",
    )
    ignored = _git_command(root, "check-ignore", "--quiet", "--", relative)
    _require(
        ignored.returncode == 0,
        f"refusing to write non-ignored file: {relative}",
    )


def _require_ignored_untracked_directory(root: Path, relative_path: Path) -> None:
    relative = relative_path.as_posix()
    tracked = _git_command(root, "ls-files", "--", relative)
    _require(
        tracked.returncode == 0 and not tracked.stdout.strip(),
        f"refusing to change a directory containing tracked files: {relative}",
    )
    ignored = _git_command(root, "check-ignore", "--quiet", "--", relative)
    _require(
        ignored.returncode == 0,
        f"refusing to change non-ignored directory: {relative}",
    )


def _generate_distinct_secret(
    factory: Callable[[], str],
    reserved: list[str],
) -> str:
    for _attempt in range(128):
        candidate = factory()
        if len(candidate) < 32 or candidate != candidate.strip() or re.search(r"[\r\n]", candidate):
            continue
        if candidate in LOCAL_SECRET_DEFAULTS or PLACEHOLDER_RE.fullmatch(candidate):
            continue
        if any(hmac.compare_digest(candidate, current) for current in reserved):
            continue
        return candidate
    raise EmailEnvironmentError("CSPRNG did not produce a valid distinct secret")


def _prepare(
    documents: tuple[EnvironmentDocument, ...],
    *,
    generate: bool,
    secret_factory: Callable[[], str],
) -> tuple[tuple[_PreparedDocument, ...], PreparationSummary]:
    overrides: dict[tuple[str, str], str] = {}
    generation_needed: list[tuple[EnvironmentDocument, str]] = []
    preserve_count = 0

    for document in documents:
        for key in GENERATED_SECRET_KEYS:
            value = _current_value(document, key)
            if _is_replaceable_secret(value):
                generation_needed.append((document, key))
                continue
            _validate_strong_secret(document.spec.label, key, value)
            preserve_count += 1

    _validate_distinct(_known_secret_entries(documents))
    reserved = [value for _label, value in _known_secret_entries(documents)]
    if generate:
        for document, key in generation_needed:
            generated = _generate_distinct_secret(secret_factory, reserved)
            overrides[(document.spec.label, key)] = generated
            reserved.append(generated)
        _validate_distinct(_known_secret_entries(documents, overrides))

    prepared: list[_PreparedDocument] = []
    nonsecret_update_count = 0
    external_actions: list[str] = []
    generation_needed_by_document = {
        (document.spec.label, key) for document, key in generation_needed
    }
    for document in documents:
        updates: dict[str, str] = {}
        for key, expected in document.spec.defaults.items():
            if _current_value(document, key) != expected:
                updates[key] = expected
                nonsecret_update_count += 1
        document_generation_count = sum(
            (document.spec.label, key) in generation_needed_by_document
            for key in GENERATED_SECRET_KEYS
        )
        for key in GENERATED_SECRET_KEYS:
            generated = overrides.get((document.spec.label, key))
            if generated is not None:
                updates[key] = generated
        for key in EXTERNAL_SECRET_KEYS:
            if _is_external_action_missing(_current_value(document, key)):
                external_actions.append(f"{document.spec.label}.{key}")

        content = _render_document(document, updates) if generate else document.original
        prepared.append(
            _PreparedDocument(
                document=document,
                content=content,
                secret_generation_count=document_generation_count,
                strong_secret_preserve_count=sum(
                    not _is_replaceable_secret(_current_value(document, key))
                    for key in GENERATED_SECRET_KEYS
                ),
                nonsecret_update_count=sum(
                    _current_value(document, key) != expected
                    for key, expected in document.spec.defaults.items()
                ),
            )
        )

    file_change_count = sum(
        bool(item.secret_generation_count or item.nonsecret_update_count)
        for item in prepared
    )
    summary = PreparationSummary(
        mode="apply" if generate else "plan",
        file_change_count=file_change_count,
        secret_generation_count=len(generation_needed),
        strong_secret_preserve_count=preserve_count,
        nonsecret_update_count=nonsecret_update_count,
        missing_external_actions=tuple(external_actions),
        file_write_count=0,
    )
    return tuple(prepared), summary


def plan_environment(root: Path = ROOT) -> PreparationSummary:
    """Inspect content and permissions without mutating either one."""
    _prepare_environment_paths(root, harden=False)
    documents = tuple(_read_document(root, spec) for spec in ENVIRONMENT_SPECS)
    _prepared, summary = _prepare(
        documents,
        generate=False,
        secret_factory=lambda: "",
    )
    return summary


def _stage_atomic(root: Path, document: EnvironmentDocument, content: bytes) -> Path:
    path = document.path
    try:
        ensure_private_path_location(root, path)
        if not path.parent.is_dir():
            raise PrivatePathError("environment source parent is missing")
        temporary = path.with_name(f".{path.name}.v377.{os.getpid()}.{secrets.token_hex(8)}.tmp")
        ensure_private_path_location(root, temporary)
        descriptor = create_private_file(temporary)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            harden_private_file(temporary)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        return temporary
    except (OSError, PrivatePathError):
        raise EmailEnvironmentError(
            f"{document.spec.label} environment could not be staged atomically"
        ) from None


def apply_environment(
    root: Path = ROOT,
    *,
    secret_factory: Callable[[], str] | None = None,
) -> PreparationSummary:
    """Safely update both ignored dotenv files, preserving unrelated content."""
    _prepare_environment_paths(root, harden=True)
    documents = tuple(_read_document(root, spec) for spec in ENVIRONMENT_SPECS)

    prepared, summary = _prepare(
        documents,
        generate=True,
        secret_factory=secret_factory or (lambda: secrets.token_urlsafe(48)),
    )
    changed = tuple(item for item in prepared if item.content != item.document.original)
    staged: list[tuple[_PreparedDocument, Path]] = []
    try:
        for item in changed:
            staged.append((item, _stage_atomic(root, item.document, item.content)))
        for item, _temporary in staged:
            current = item.document.path.read_bytes() if item.document.path.exists() else b""
            _require(
                current == item.document.original,
                f"{item.document.spec.label} environment changed during preparation",
            )
        for item, temporary in staged:
            try:
                os.replace(temporary, item.document.path)
                ensure_private_path_location(root, item.document.path)
                verify_private_file(item.document.path)
            except (OSError, PrivatePathError):
                raise EmailEnvironmentError(
                    f"{item.document.spec.label} environment atomic replace failed"
                ) from None
    finally:
        for _item, temporary in staged:
            temporary.unlink(missing_ok=True)

    return PreparationSummary(
        mode="apply",
        file_change_count=summary.file_change_count,
        secret_generation_count=summary.secret_generation_count,
        strong_secret_preserve_count=summary.strong_secret_preserve_count,
        nonsecret_update_count=summary.nonsecret_update_count,
        missing_external_actions=summary.missing_external_actions,
        file_write_count=len(changed),
    )


def print_summary(summary: PreparationSummary) -> None:
    """Print counts and key names only; never print assignment values."""
    title = "apply" if summary.mode == "apply" else "plan (content read-only)"
    print(f"v377 email security environment {title}")
    print(f"- files requiring change: {summary.file_change_count}")
    print(f"- email security secrets requiring generation: {summary.secret_generation_count}")
    print(f"- existing strong email security secrets preserved: {summary.strong_secret_preserve_count}")
    print(f"- non-secret assignments requiring update: {summary.nonsecret_update_count}")
    if summary.missing_external_actions:
        print("- missing external user actions: " + ", ".join(summary.missing_external_actions))
    else:
        print("- missing external user actions: none")
    print(f"- files written: {summary.file_write_count}")
    print("- actual secret values displayed: no")


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments in (["-h"], ["--help"]):
        print("usage: prepare_v377_email_security_environment.py [--apply]")
        print("default: secret-safe content-read-only plan with ACL verification")
        return 0
    if arguments not in ([], ["--apply"]):
        print("v377 email security environment failed: invalid arguments", file=sys.stderr)
        return 2
    try:
        summary = apply_environment() if arguments else plan_environment()
        print_summary(summary)
    except EmailEnvironmentError as exc:
        print(f"v377 email security environment failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print(
            "v377 email security environment failed: unexpected local operation error",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
