"""Fail-closed process boundaries for offline PostgreSQL client operations."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import stat
from typing import Any, Iterator, Mapping


class PostgresClientSafetyError(RuntimeError):
    """Raised when an inherited libpq or executable boundary is unsafe."""


def filtered_libpq_environment(
    additions: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Copy the process environment without any libpq ``PG*`` defaults."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith("PG")
    }
    if additions:
        environment.update(additions)
    return environment


@contextmanager
def without_libpq_environment() -> Iterator[None]:
    """Temporarily remove inherited libpq defaults around a sync connection."""
    preserved = {
        key: value
        for key, value in os.environ.items()
        if key.upper().startswith("PG")
    }
    for key in preserved:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        for key in tuple(os.environ):
            if key.upper().startswith("PG"):
                os.environ.pop(key, None)
        os.environ.update(preserved)


def guard_sqlalchemy_libpq_engine(engine: Any) -> Any:
    """Ensure every lazy psycopg connection is opened without inherited PG vars."""
    from sqlalchemy import event  # noqa: PLC0415

    @event.listens_for(engine, "do_connect", retval=True)
    def connect_without_libpq_defaults(  # type: ignore[no-untyped-def]
        dialect: Any,
        _connection_record: Any,
        connection_args: list[Any],
        connection_parameters: dict[str, Any],
    ) -> Any:
        with without_libpq_environment():
            return dialect.connect(*connection_args, **connection_parameters)

    return engine


def trusted_posix_executable(name: str) -> Path:
    """Resolve a PATH tool only through root/current-owned non-writable hops."""
    found = shutil.which(name)
    if not found:
        raise PostgresClientSafetyError("PostgreSQL client executable is missing")
    try:
        selected = Path(found).resolve(strict=True)
        metadata = selected.stat(follow_symlinks=False)
    except OSError:
        raise PostgresClientSafetyError(
            "PostgreSQL client executable path is unsafe"
        ) from None
    if not selected.is_absolute() or not stat.S_ISREG(metadata.st_mode):
        raise PostgresClientSafetyError("PostgreSQL client executable type is unsafe")
    if not os.access(selected, os.X_OK):
        raise PostgresClientSafetyError("PostgreSQL client executable is not executable")

    effective_uid = os.geteuid()
    trusted_owners = {0, effective_uid}
    current = selected
    while True:
        try:
            item = current.stat(follow_symlinks=False)
        except OSError:
            raise PostgresClientSafetyError(
                "PostgreSQL client executable path is unsafe"
            ) from None
        if item.st_uid not in trusted_owners:
            raise PostgresClientSafetyError(
                "PostgreSQL client executable owner is unsafe"
            )
        if item.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise PostgresClientSafetyError(
                "PostgreSQL client executable path is group/world-writable"
            )
        if current.parent == current:
            break
        current = current.parent
    return selected
