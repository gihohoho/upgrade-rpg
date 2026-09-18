"""Exact additive v402 migration with private backup and existing-data preservation.

Default: source plan only. --inspect reads the named target. --apply backs it up
and adds only the two gameplay tables under one transaction. No reset, seed,
restore, stamp or production downgrade is provided.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import MetaData, Table, inspect, select, text

os.environ["DEBUG"] = "false"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import apply_v377_auth_security_migration as connection_guard  # noqa: E402
from app.db.base import Base  # noqa: E402
from app import models  # noqa: E402,F401
from private_artifacts import (  # noqa: E402
    create_private_file,
    harden_private_directory,
    verify_private_file,
    write_private_text_exclusive,
)

PREVIOUS = "v377_auth_email_public_security"
REVISION = "v402_server_gameplay"
ADDED = {"game_sessions", "game_action_receipts"}
EXISTING = set(Base.metadata.tables) - ADDED
ARTIFACTS = ROOT / "local-backups/postgres/v402"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def validate_source(sha):
    require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "exact source SHA required")

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    require(git("branch", "--show-current") == "main", "main branch required")
    require(
        git("rev-parse", "HEAD") == sha == git("rev-parse", "@{upstream}"),
        "pushed source SHA differs",
    )
    require(
        not git("status", "--porcelain", "--untracked-files=no"),
        "tracked source must be clean",
    )


def read_revision(conn):
    return conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


def validate_tables(conn, *, applied=False):
    expected = EXISTING | {"alembic_version"} | (ADDED if applied else set())
    require(
        set(inspect(conn).get_table_names()) == expected, "target table set differs"
    )
    require(
        read_revision(conn) == (REVISION if applied else PREVIOUS),
        "target revision differs",
    )


def fingerprints(conn):
    result = {}
    for name in sorted(EXISTING):
        table = Table(name, MetaData(), autoload_with=conn)
        require(
            bool(list(table.primary_key.columns)), "existing table requires primary key"
        )
        digest = hashlib.sha256()
        count = 0
        for row in conn.execute(
            select(table).order_by(*table.primary_key.columns)
        ).yield_per(500):
            value = connection_guard._stable_row_bytes(row)
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)
            count += 1
        result[name] = {"rows": count, "sha256": digest.hexdigest()}
    return result


def migrate_locked(conn, target):
    """Caller owns the transaction. Tests use a separate schema/search_path."""
    validate_tables(conn)
    for name in sorted(EXISTING | {"alembic_version"}):
        require(bool(re.fullmatch(r"[a-z_]+", name)), "unexpected table identifier")
        conn.execute(text(f'LOCK TABLE "{name}" IN SHARE ROW EXCLUSIVE MODE'))
    before = fingerprints(conn)
    config = Config(str(ROOT / "backend/alembic.ini"), stdout=io.StringIO())
    config.set_main_option("script_location", str(ROOT / "backend/alembic"))
    config.attributes["connection"] = conn
    # Reuse the existing verified target/TLS/environment guard; exact revision is below.
    with connection_guard._temporary_alembic_environment(target):
        command.upgrade(config, REVISION)
    validate_tables(conn, applied=True)
    require(
        fingerprints(conn) == before, "existing row content changed; rollback required"
    )
    require(
        not compare_metadata(MigrationContext.configure(conn), Base.metadata),
        "model/schema parity failed",
    )
    for name in ADDED:
        require(
            conn.execute(text(f'SELECT count(*) FROM "{name}"')).scalar_one() == 0,
            "new table is not empty",
        )
    return {
        "preservedTables": len(EXISTING),
        "preservedRows": sum(x["rows"] for x in before.values()),
        "dataSha256": hashlib.sha256(
            json.dumps(before, sort_keys=True).encode()
        ).hexdigest(),
    }


def apply(target, sha):
    validate_source(sha)
    connection_guard._prepare_private_artifact_storage()
    harden_private_directory(ARTIFACTS, create=True)
    marker = ARTIFACTS / f"{target.label}.attempt.json"
    dump = ARTIFACTS / f"{target.label}.before-v402.custom.dump"
    report = ARTIFACTS / f"{target.label}.completed.json"
    require(
        not any(p.exists() for p in (marker, dump, report)),
        "existing v402 attempt; inspect it without automatic retry",
    )
    engine = connection_guard.build_target_sync_engine(target)
    engine.hide_parameters = True
    try:
        with engine.connect() as conn:
            validate_tables(conn)
        write_private_text_exclusive(
            marker,
            json.dumps(
                {
                    "sourceSha": sha,
                    "target": target.label,
                    "startedAt": datetime.now(UTC).isoformat(),
                }
            ),
            encoding="utf-8",
        )
        os.close(create_private_file(dump))
        environment = connection_guard.pg_environment(target)
        connection_guard._run_backup_command(
            [
                str(connection_guard._postgres_tool("pg_dump")),
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                "--file",
                str(dump),
            ],
            environment=environment,
            label="v402 fresh backup",
        )
        verify_private_file(dump)
        require(dump.stat().st_size > 0, "empty backup")
        toc = connection_guard._run_backup_command(
            [str(connection_guard._postgres_tool("pg_restore")), "--list", str(dump)],
            environment=environment,
            label="v402 backup TOC",
        ).decode("utf-8")
        for name in EXISTING | {"alembic_version"}:
            require(f" TABLE DATA public {name} " in toc, "backup table data missing")
        backup_hash = hashlib.sha256(dump.read_bytes()).hexdigest()
        with engine.begin() as conn:
            outcome = migrate_locked(conn, target)
        write_private_text_exclusive(
            report,
            json.dumps(
                {
                    "sourceSha": sha,
                    "target": target.label,
                    "revision": REVISION,
                    "backupSha256": backup_hash,
                    "completedAt": datetime.now(UTC).isoformat(),
                    "applyCount": 1,
                    "stampCount": 0,
                    "downgradeCount": 0,
                    **outcome,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            f"{target.label}: v402 applied once; {outcome['preservedTables']} existing tables preserved; report {report.relative_to(ROOT)}"
        )
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("local", "neon"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha", default="")
    args = parser.parse_args()
    if not args.inspect and not args.apply:
        print(
            f"Plan only: {PREVIOUS} -> {REVISION}; add {', '.join(sorted(ADDED))}; preserve 25 tables. No DB connection."
        )
        return
    require(args.target, "explicit target required")
    target = connection_guard.load_target(args.target)
    if args.apply:
        apply(target, args.source_sha)
    else:
        engine = connection_guard.build_target_sync_engine(target)
        try:
            with engine.connect() as conn:
                print(
                    json.dumps(
                        {
                            "target": args.target,
                            "revision": read_revision(conn),
                            "tables": len(inspect(conn).get_table_names()),
                        }
                    )
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Never print a driver exception, connection string or SQL parameters.
        print(
            f"v402 migration stopped ({type(error).__name__}); inspect private attempt evidence.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
