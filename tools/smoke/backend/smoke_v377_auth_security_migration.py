#!/usr/bin/env python3
"""DB/network-free parity and guard smoke for the v377 auth migration."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import inspect as python_inspect
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import sys
from typing import Any, Callable

import sqlalchemy as sa
from sqlalchemy.engine import URL, make_url


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
TOOLS = ROOT / "tools"
REVISION = BACKEND / "alembic/versions/v377_auth_email_public_security.py"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(BACKEND))

from app.core.config import Settings  # noqa: E402
from app.models import AuthEmailOutbox, AuthRateLimitBucket  # noqa: E402
from check_postgres_schema_equivalence import normalized_type  # noqa: E402
import apply_v377_auth_security_migration as target_guard  # noqa: E402
import postgres_client_safety as pg_safety  # noqa: E402
import private_artifacts as private_artifacts  # noqa: E402
from private_artifacts import (  # noqa: E402
    PrivatePathError,
    write_private_text_exclusive,
)
import run_v377_auth_security_migration_roundtrip as roundtrip  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(callback: Callable[[], Any], message: str) -> None:
    try:
        callback()
    except roundtrip.V377RoundTripError:
        return
    raise AssertionError(message)


class OperationRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _record(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((name, args, kwargs))

    def f(self, name: str) -> str:
        return name

    def create_table(self, *args: Any, **kwargs: Any) -> None:
        self._record("create_table", *args, **kwargs)

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        self._record("create_index", *args, **kwargs)

    def drop_index(self, *args: Any, **kwargs: Any) -> None:
        self._record("drop_index", *args, **kwargs)

    def drop_table(self, *args: Any, **kwargs: Any) -> None:
        self._record("drop_table", *args, **kwargs)


def load_revision():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        "v377_auth_email_public_security",
        REVISION,
    )
    require(spec is not None and spec.loader is not None, "cannot load v377 revision")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_sql(value: Any) -> str:
    return " ".join(str(value).split())


def server_default(column: sa.Column[Any]) -> str | None:
    if column.server_default is None:
        return None
    return str(column.server_default.arg).strip().strip("'\"")


def exact_table_signature(table: sa.Table) -> dict[str, Any]:
    columns = [
        (
            column.name,
            normalized_type(column.type),
            bool(column.nullable),
            bool(column.primary_key),
            server_default(column),
        )
        for column in table.columns
    ]
    primary_key = (
        table.primary_key.name,
        tuple(column.name for column in table.primary_key.columns),
    )
    foreign_keys = sorted(
        (
            constraint.name,
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            (constraint.ondelete or "").upper(),
            (constraint.onupdate or "").upper(),
        )
        for constraint in table.foreign_key_constraints
    )
    checks = sorted(
        (constraint.name, normalized_sql(constraint.sqltext))
        for constraint in table.constraints
        if isinstance(constraint, sa.CheckConstraint)
    )
    indexes = sorted(
        (
            index.name,
            tuple(column.name for column in index.columns),
            bool(index.unique),
            (
                normalized_sql(index.dialect_options["postgresql"].get("where"))
                if index.dialect_options["postgresql"].get("where") is not None
                else None
            ),
        )
        for index in table.indexes
    )
    return {
        "columns": columns,
        "primaryKey": primary_key,
        "foreignKeys": foreign_keys,
        "checks": checks,
        "indexes": indexes,
    }


def recorded_tables(recorder: OperationRecorder) -> dict[str, sa.Table]:
    metadata = sa.MetaData()
    tables: dict[str, sa.Table] = {}
    for name, args, kwargs in recorder.calls:
        if name != "create_table":
            continue
        require(not kwargs, "v377 create_table has unexpected keyword options")
        table_name = str(args[0])
        tables[table_name] = sa.Table(table_name, metadata, *args[1:])
    for name, args, kwargs in recorder.calls:
        if name != "create_index":
            continue
        require(
            set(kwargs) <= {"unique", "postgresql_where"},
            "v377 index has unexpected options",
        )
        index_name, table_name, column_names = args[:3]
        table = tables[str(table_name)]
        sa.Index(
            str(index_name),
            *(table.c[str(column_name)] for column_name in column_names),
            unique=bool(kwargs.get("unique", False)),
            postgresql_where=kwargs.get("postgresql_where"),
        )
    return tables


def test_revision_model_parity() -> None:
    source = REVISION.read_text(encoding="utf-8")
    for forbidden in (
        "op.execute(",
        "op.bulk_insert(",
        "INSERT INTO",
        "UPDATE users",
        "DELETE FROM",
    ):
        require(forbidden not in source, f"v377 revision contains data DML: {forbidden}")

    module = load_revision()
    require(module.revision == roundtrip.HEAD_REVISION, "unexpected v377 revision id")
    require(module.down_revision == roundtrip.EMAIL_REVISION, "v377 must directly revise v371")
    require(module.branch_labels is None and module.depends_on is None, "unexpected v377 branch")

    upgrade = OperationRecorder()
    module.op = upgrade
    module.upgrade()
    call_sequence = [
        (name, str(args[0]))
        for name, args, _kwargs in upgrade.calls
    ]
    require(
        call_sequence
        == [
            ("create_table", "auth_rate_limit_buckets"),
            ("create_index", "ix_auth_rate_limit_buckets_updated_at"),
            ("create_index", "ix_auth_rate_limit_buckets_blocked_until"),
            ("create_table", "auth_email_outbox"),
            ("create_index", "ix_auth_email_outbox_id"),
            ("create_index", "ix_auth_email_outbox_pending"),
            ("create_index", "ix_auth_email_outbox_user_purpose"),
            ("create_index", "ix_auth_email_outbox_target_purpose"),
            ("create_index", "uq_auth_email_outbox_pending_target_purpose"),
            ("create_index", "uq_auth_email_outbox_inflight_target_purpose"),
        ],
        "v377 upgrade operation order differs",
    )

    migration_tables = recorded_tables(upgrade)
    model_tables = {
        "auth_rate_limit_buckets": AuthRateLimitBucket.__table__,
        "auth_email_outbox": AuthEmailOutbox.__table__,
    }
    require(set(migration_tables) == set(model_tables), "v377 table set differs")
    for table_name, model_table in model_tables.items():
        require(
            exact_table_signature(migration_tables[table_name])
            == exact_table_signature(model_table),
            f"v377 revision/model parity differs: {table_name}",
        )

    outbox_checks = {
        constraint.name
        for constraint in migration_tables["auth_email_outbox"].constraints
        if isinstance(constraint, sa.CheckConstraint)
    }
    require(
        {
            "ck_auth_email_outbox_target_digest_length",
            "ck_auth_email_outbox_state_shape",
        }
        <= outbox_checks,
        "v377 outbox digest/state-shape constraints are missing",
    )

    all_model_tables = {
        table.name: table
        for table in AuthEmailOutbox.metadata.sorted_tables
    }
    legacy_names = set(all_model_tables) - {
        "user_email_action_tokens",
        "auth_email_outbox",
        "auth_rate_limit_buckets",
    }
    require(
        len(legacy_names) == roundtrip.EXPECTED_BASE_APPLICATION_TABLES,
        "legacy application table count differs",
    )
    require(
        all(
            len(all_model_tables[name].primary_key.columns) > 0
            for name in legacy_names
        ),
        "legacy fingerprint requires a primary key on every table",
    )

    downgrade = OperationRecorder()
    module.op = downgrade
    module.downgrade()
    observed_downgrade = [
        (name, str(args[0]), kwargs.get("table_name"))
        for name, args, kwargs in downgrade.calls
    ]
    require(
        observed_downgrade
        == [
            (
                "drop_index",
                "uq_auth_email_outbox_inflight_target_purpose",
                "auth_email_outbox",
            ),
            (
                "drop_index",
                "uq_auth_email_outbox_pending_target_purpose",
                "auth_email_outbox",
            ),
            ("drop_index", "ix_auth_email_outbox_target_purpose", "auth_email_outbox"),
            ("drop_index", "ix_auth_email_outbox_user_purpose", "auth_email_outbox"),
            ("drop_index", "ix_auth_email_outbox_pending", "auth_email_outbox"),
            ("drop_index", "ix_auth_email_outbox_id", "auth_email_outbox"),
            ("drop_table", "auth_email_outbox", None),
            (
                "drop_index",
                "ix_auth_rate_limit_buckets_blocked_until",
                "auth_rate_limit_buckets",
            ),
            (
                "drop_index",
                "ix_auth_rate_limit_buckets_updated_at",
                "auth_rate_limit_buckets",
            ),
            ("drop_table", "auth_rate_limit_buckets", None),
        ],
        "v377 downgrade must be the exact reverse table/index boundary",
    )


def catalog_fixture(*, include_isolated: bool) -> dict[str, dict[str, Any]]:
    source = {
        "database": roundtrip.SOURCE_DATABASE,
        "owner": roundtrip.SOURCE_DATABASE_USER,
        "encoding": "UTF8",
        "collate": "C",
        "ctype": "C",
        "locale_provider": "c",
        "icu_locale": "",
    }
    catalog = {roundtrip.SOURCE_DATABASE: source}
    if include_isolated:
        catalog[roundtrip.ISOLATED_DATABASE] = {
            **source,
            "database": roundtrip.ISOLATED_DATABASE,
        }
    return catalog


def source_state_fixture() -> dict[str, Any]:
    return {
        "database": roundtrip.SOURCE_DATABASE,
        "revision": [roundtrip.BASE_REVISION],
        "publicTableCount": roundtrip.EXPECTED_BASE_PUBLIC_TABLES,
        "schemaDigest": roundtrip.EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "publicTables": [
            "alembic_version",
            "users",
            *(f"legacy_table_{index}" for index in range(21)),
        ],
    }


def test_isolated_roundtrip_guard() -> None:
    contract = roundtrip.validate_revision_contract(ROOT)
    require(contract["head"] == roundtrip.HEAD_REVISION, "revision contract head differs")
    require(
        contract["revisionSha256"] == roundtrip.REVISION_SHA256,
        "revision hash contract differs",
    )
    require(
        roundtrip.build_alembic_command("upgrade", roundtrip.BASE_REVISION)[-2:]
        == ["upgrade", roundtrip.BASE_REVISION],
        "exact v295 upgrade command differs",
    )
    require(
        roundtrip.build_alembic_command("upgrade", roundtrip.HEAD_REVISION)[-2:]
        == ["upgrade", roundtrip.HEAD_REVISION],
        "exact v377 upgrade command differs",
    )
    require(
        roundtrip.build_alembic_command("downgrade", roundtrip.BASE_REVISION)[-2:]
        == ["downgrade", roundtrip.BASE_REVISION],
        "exact v295 downgrade command differs",
    )
    expect_error(
        lambda: roundtrip.build_alembic_command("upgrade", "head"),
        "roundtrip guard accepted the moving head alias",
    )
    expect_error(
        lambda: roundtrip.build_alembic_command("downgrade", "base"),
        "roundtrip guard accepted downgrade base",
    )

    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-v377-readiness-") as temp:
        report_root = Path(temp)
        report_path = report_root / "roundtrip.json"
        readiness = roundtrip.inspect_readiness(
            catalog=catalog_fixture(include_isolated=False),
            source_state=source_state_fixture(),
            report_root=report_root,
            report_path=report_path,
        )
        require(readiness["syntheticFixtureOnly"], "roundtrip fixture is not synthetic-only")
        require(not readiness["restoreExecuted"], "roundtrip guard permits a real restore")
        expect_error(
            lambda: roundtrip.inspect_readiness(
                catalog=catalog_fixture(include_isolated=True),
                source_state=source_state_fixture(),
                report_root=report_root,
                report_path=report_path,
            ),
            "roundtrip guard accepted an existing fixed target",
        )

    created_catalog = catalog_fixture(include_isolated=True)
    roundtrip.validate_isolated_catalog(
        created_catalog,
        created_catalog[roundtrip.SOURCE_DATABASE],
    )
    create_command = roundtrip.build_create_command(
        created_catalog[roundtrip.SOURCE_DATABASE]
    )
    require(create_command[-1] == roundtrip.ISOLATED_DATABASE, "createdb target differs")
    require("--template=template0" in create_command, "isolated DB is not template0-based")
    require("dropdb" not in create_command, "isolated guard contains a drop path")
    require("automatic retry" in roundtrip.render_plan(), "no-retry boundary missing")

    synthetic_settings = type(
        "SyntheticSettings",
        (),
        {
            "database_url": (
                "postgresql+asyncpg://rpg_user:synthetic-password@"
                "127.0.0.1:55432/rpg_game"
            )
        },
    )()
    hostile_pg_environment = {
        "PGHOSTADDR": "203.0.113.20",
        "PGSERVICE": "attacker-service",
        "PGOPTIONS": "-c search_path=attacker",
    }
    with (
        patch.dict(os.environ, hostile_pg_environment, clear=False),
        patch.object(roundtrip, "verify_local_environment_file"),
        patch.object(
            roundtrip,
            "load_backend_objects",
            return_value=(synthetic_settings, None),
        ),
    ):
        environment = roundtrip.isolated_alembic_environment()
    require(
        not set(hostile_pg_environment) & set(environment),
        "isolated Alembic subprocess inherited hostile libpq defaults",
    )
    isolated_url = make_url(environment["DATABASE_URL"])
    require(not isolated_url.query, "isolated raw URL carries asyncpg server settings")
    require(
        isolated_url.database == roundtrip.ISOLATED_DATABASE,
        "isolated Alembic database differs",
    )
    require(
        {
            name: environment[name]
            for name in (
                "ALEMBIC_GUARD_MODE",
                "ALEMBIC_LOCK_TIMEOUT_MS",
                "ALEMBIC_STATEMENT_TIMEOUT_MS",
                "ALEMBIC_APPLICATION_NAME",
            )
        }
        == {
            "ALEMBIC_GUARD_MODE": "v377",
            "ALEMBIC_LOCK_TIMEOUT_MS": str(roundtrip.LOCK_TIMEOUT_MS),
            "ALEMBIC_STATEMENT_TIMEOUT_MS": str(roundtrip.STATEMENT_TIMEOUT_MS),
            "ALEMBIC_APPLICATION_NAME": roundtrip.ALEMBIC_ISOLATED_APPLICATION_NAME,
        },
        "isolated Alembic guard environment differs",
    )
    require(
        roundtrip.isolated_sync_connect_args()
        == {
            "connect_timeout": 20,
            "application_name": "upgrade-rpg-v377-isolated-verification",
            "options": (
                f"-c lock_timeout={roundtrip.LOCK_TIMEOUT_MS}ms "
                f"-c statement_timeout={roundtrip.STATEMENT_TIMEOUT_MS}ms"
            ),
        },
        "isolated verification connection timeouts differ",
    )

    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-v377-report-guard-") as temp:
        temp_root = Path(temp)
        report_path = temp_root / "evidence/roundtrip.json"
        roundtrip.validate_roundtrip_report_absent(temp_root, report_path)
        report_path.parent.mkdir()
        report_path.write_text("in-progress", encoding="utf-8")
        expect_error(
            lambda: roundtrip.validate_roundtrip_report_absent(
                temp_root,
                report_path,
            ),
            "round-trip guard accepted an existing one-attempt report",
        )


def target_fixture(*, tls: bool) -> target_guard.TargetSpec:
    return target_guard.TargetSpec(
        label="neon" if tls else "local",
        database="neondb" if tls else roundtrip.SOURCE_DATABASE,
        role="neondb_owner" if tls else roundtrip.SOURCE_DATABASE_USER,
        host=(
            "ep-v377-direct.ap-southeast-1.aws.neon.tech"
            if tls
            else "127.0.0.1"
        ),
        port=5432 if tls else 55432,
        password="process-only-not-a-real-database-password",
        async_url=URL.create(
            "postgresql+asyncpg",
            username="neondb_owner" if tls else roundtrip.SOURCE_DATABASE_USER,
            password="process-only-not-a-real-database-password",
            host=(
                "ep-v377-direct.ap-southeast-1.aws.neon.tech"
                if tls
                else "127.0.0.1"
            ),
            port=5432 if tls else 55432,
            database="neondb" if tls else roundtrip.SOURCE_DATABASE,
        ),
        tls=tls,
    )


class FakeQuiescentConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.locked_tables: set[str] = set()

    def exec_driver_sql(self, statement: str) -> None:
        self.statements.append(statement)
        prefix = 'LOCK TABLE "public"."'
        suffix = f'" IN {target_guard.LEGACY_WRITE_LOCK_MODE} MODE'
        if statement.startswith(prefix) and statement.endswith(suffix):
            self.locked_tables.add(statement[len(prefix) : -len(suffix)])

    def reader_allowed(self, table_name: str) -> bool:
        return table_name in self.locked_tables

    def writer_allowed(self, table_name: str) -> bool:
        return table_name not in self.locked_tables


class FakeTransactionContext:
    def __init__(self, engine: "FakeTransactionEngine") -> None:
        self.engine = engine

    def __enter__(self) -> FakeQuiescentConnection:
        self.engine.begin_calls += 1
        return self.engine.connection

    def __exit__(self, exc_type, _exc, _traceback) -> bool:  # type: ignore[no-untyped-def]
        if exc_type is None:
            self.engine.commit_calls += 1
        else:
            self.engine.rollback_calls += 1
        return False


class FakeTransactionEngine:
    def __init__(self) -> None:
        self.connection = FakeQuiescentConnection()
        self.begin_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.dispose_calls = 0

    def begin(self) -> FakeTransactionContext:
        return FakeTransactionContext(self)

    def dispose(self) -> None:
        self.dispose_calls += 1


def completed_roundtrip_payload(source_sha: str) -> dict[str, Any]:
    return {
        "toolVersion": roundtrip.TOOL_VERSION,
        "result": "v377-isolated-upgrade-downgrade-reupgrade-verified",
        "startedAtUtc": "2026-08-15T01:00:00Z",
        "preparationCommitSha": source_sha,
        "sourceDatabase": roundtrip.SOURCE_DATABASE,
        "sourceCurrentRevision": roundtrip.BASE_REVISION,
        "targetDatabase": roundtrip.ISOLATED_DATABASE,
        "revisionContract": roundtrip.validate_revision_contract(ROOT),
        "syntheticFixtureOnly": True,
        "restoreExecuted": False,
        "dropDatabaseExecuted": False,
        "automaticRetry": False,
        "completedStages": list(target_guard.ROUNDTRIP_COMPLETED_STAGES),
        "completedAtUtc": "2026-08-15T01:01:00Z",
        "alembicCommands": [
            {
                "command": f"alembic upgrade {roundtrip.BASE_REVISION}",
                "exitCode": 0,
                "outputSha256": "1" * 64,
            },
            {
                "command": f"alembic upgrade {roundtrip.HEAD_REVISION}",
                "exitCode": 0,
                "outputSha256": "2" * 64,
            },
            {
                "command": f"alembic downgrade {roundtrip.BASE_REVISION}",
                "exitCode": 0,
                "outputSha256": "3" * 64,
            },
            {
                "command": f"alembic upgrade {roundtrip.HEAD_REVISION}",
                "exitCode": 0,
                "outputSha256": "4" * 64,
            },
        ],
        "baselineFixtureDigest": "5" * 64,
        "firstHeadSchemaDigest": "6" * 64,
        "secondHeadSchemaDigest": "6" * 64,
        "firstModelParity": {
            "modelTableCount": target_guard.EXPECTED_HEAD_APPLICATION_TABLES,
            "differenceCount": 0,
        },
        "secondModelParity": {
            "modelTableCount": target_guard.EXPECTED_HEAD_APPLICATION_TABLES,
            "differenceCount": 0,
        },
        "syntheticHeadRowsBeforeDowngrade": {
            "authRateLimitBuckets": 1,
            "authEmailOutbox": 1,
        },
        "syntheticHeadRowsAfterReupgrade": {
            "authRateLimitBuckets": 0,
            "authEmailOutbox": 0,
        },
        "sourcePreserved": True,
        "finalTargetRevision": roundtrip.HEAD_REVISION,
    }


def test_target_apply_guard() -> None:
    source_sha = "0" * 40
    roundtrip_payload = completed_roundtrip_payload(source_sha)
    target_guard.validate_roundtrip_payload(
        roundtrip_payload,
        source_sha=source_sha,
    )
    expect_error(
        lambda: target_guard.validate_roundtrip_payload(
            {**roundtrip_payload, "result": "v377-isolated-roundtrip-in-progress"},
            source_sha=source_sha,
        ),
        "target guard accepted an in-progress round-trip report",
    )
    expect_error(
        lambda: target_guard.validate_roundtrip_payload(
            roundtrip_payload,
            source_sha="f" * 40,
        ),
        "target guard accepted round-trip evidence from another source SHA",
    )
    require(
        "roundtrip_report"
        in python_inspect.signature(target_guard.create_fresh_backup).parameters,
        "fresh backup does not require round-trip evidence",
    )
    require(
        "roundtrip_report"
        in python_inspect.signature(target_guard.apply_exact_upgrade).parameters,
        "target apply does not require round-trip evidence",
    )

    utc_instant = datetime(2026, 8, 22, 3, 4, 5, 123456, tzinfo=timezone.utc)
    seoul_instant = datetime(
        2026,
        8,
        22,
        12,
        4,
        5,
        123456,
        tzinfo=timezone(timedelta(hours=9)),
    )
    utc_row = target_guard._stable_row_bytes((utc_instant,))  # noqa: SLF001
    seoul_row = target_guard._stable_row_bytes((seoul_instant,))  # noqa: SLF001
    require(
        utc_row == seoul_row,
        "same timestamptz instant differs across driver timezone offsets",
    )
    require(
        hashlib.sha256(utc_row).digest() == hashlib.sha256(seoul_row).digest(),
        "same timestamptz instant produces different legacy data digests",
    )
    naive_wall_clock = datetime(2026, 8, 22, 3, 4, 5, 123456)
    require(
        target_guard._stable_json_default(naive_wall_clock)  # noqa: SLF001
        == {
            "type": "datetime",
            "value": "2026-08-22T03:04:05.123456",
        },
        "naive datetime must remain a timezone-free wall-clock value",
    )
    require(
        target_guard._stable_row_bytes((naive_wall_clock,)) != utc_row,  # noqa: SLF001
        "naive datetime was silently treated as a UTC instant",
    )

    exponent_numeric = Decimal("1E+28")
    fixed_numeric = Decimal("10000000000000000000000000000")
    require(exponent_numeric == fixed_numeric, "numeric regression fixture differs")
    exponent_row = target_guard._stable_row_bytes((exponent_numeric,))  # noqa: SLF001
    fixed_row = target_guard._stable_row_bytes((fixed_numeric,))  # noqa: SLF001
    require(
        exponent_row == fixed_row,
        "equal Decimal values differ across driver exponent representations",
    )
    require(
        hashlib.sha256(exponent_row).digest() == hashlib.sha256(fixed_row).digest(),
        "equal Decimal values produce different legacy data digests",
    )
    require(
        target_guard._stable_row_bytes((Decimal("123.45000"),))  # noqa: SLF001
        == target_guard._stable_row_bytes((Decimal("123.45"),)),  # noqa: SLF001
        "Decimal fractional trailing zeros were not canonicalized",
    )
    require(
        target_guard._stable_row_bytes((Decimal("-0.000"),))  # noqa: SLF001
        == target_guard._stable_row_bytes((Decimal("0E+28"),)),  # noqa: SLF001
        "signed or exponent-form Decimal zero was not canonicalized",
    )
    with localcontext() as decimal_context:
        decimal_context.prec = 2
        exact_decimal = target_guard._stable_json_default(  # noqa: SLF001
            Decimal("123456789.12345000")
        )
    require(
        exact_decimal == {"type": "Decimal", "value": "123456789.12345"},
        "Decimal fingerprint was rounded through the active context",
    )
    require(
        target_guard._stable_json_default(Decimal("-NaN123"))  # noqa: SLF001
        == target_guard._stable_json_default(Decimal("sNaN")),  # noqa: SLF001
        "Decimal NaN forms were not canonicalized",
    )
    require(
        target_guard._stable_json_default(Decimal("+Infinity"))  # noqa: SLF001
        == {"type": "Decimal", "value": "Infinity"}
        and target_guard._stable_json_default(Decimal("-Infinity"))  # noqa: SLF001
        == {"type": "Decimal", "value": "-Infinity"},
        "Decimal infinity signs were not canonicalized",
    )

    normalized_neon = target_guard._strip_verified_neon_query(  # noqa: SLF001
        target_guard._normalize_async_url(  # noqa: SLF001
            "postgresql://neondb_owner:synthetic@"
            "ep-v377-direct.ap-southeast-1.aws.neon.tech/neondb"
            "?sslmode=require&channel_binding=require"
        )
    )
    require(not normalized_neon.query, "verified Neon TLS query was not stripped")
    expect_error(
        lambda: target_guard._strip_verified_neon_query(  # noqa: SLF001
            normalized_neon.update_query_dict({"sslmode": "require"})
        ),
        "target guard accepted an incomplete Neon TLS query",
    )

    local = target_fixture(tls=False)
    base_state = {
        "label": local.label,
        "database": local.database,
        "currentRevision": [roundtrip.BASE_REVISION],
        "applicationTableCount": target_guard.EXPECTED_BASE_APPLICATION_TABLES,
        "publicTableCount": target_guard.EXPECTED_BASE_PUBLIC_TABLES,
        "applicationSchemaDigest": target_guard.EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "legacyData": {
            "tableCount": target_guard.EXPECTED_BASE_APPLICATION_TABLES,
            "rowCount": 751,
            "aggregateSha256": "1" * 64,
            "tableNames": [],
            "tables": {},
        },
    }
    target_guard.validate_base_target(base_state, local)
    expect_error(
        lambda: target_guard.validate_base_target(
            {**base_state, "currentRevision": [roundtrip.HEAD_REVISION]},
            local,
        ),
        "target guard accepted a non-v295 apply base",
    )
    preserved = {
        "tableNames": ["users"],
        "tables": {
            "users": {
                "columns": ["id", "username"],
                "primaryKey": ["id"],
                "rowCount": 1,
                "contentSha256": "2" * 64,
            }
        },
        "tableCount": 1,
        "rowCount": 1,
        "aggregateSha256": "3" * 64,
    }
    comparison = target_guard.compare_legacy_data(preserved, dict(preserved))
    require(comparison["legacyDataDifferenceCount"] == 0, "legacy comparison differs")
    expect_error(
        lambda: target_guard.compare_legacy_data(
            preserved,
            {
                **preserved,
                "tables": {
                    "users": {
                        **preserved["tables"]["users"],
                        "contentSha256": "4" * 64,
                    }
                },
            },
        ),
        "target guard accepted changed legacy row content",
    )

    expected_legacy_lock_tables = (
        "admin_change_logs",
        "admin_roles",
        "admin_user_roles",
        "bosses",
        "character_skills",
        "characters",
        "drop_table_items",
        "drop_tables",
        "enhancement_groups",
        "enhancement_levels",
        "field_zones",
        "item_instances",
        "item_templates",
        "skill_levels",
        "skills",
        "user_character_skills",
        "user_equipment_slots",
        "user_inventory_slots",
        "user_mailbox_messages",
        "user_profiles",
        "user_save_snapshots",
        "users",
    )
    require(
        target_guard.LEGACY_WRITE_LOCK_TABLES == expected_legacy_lock_tables,
        "legacy write-lock set/order differs",
    )
    require(
        target_guard.LEGACY_WRITE_LOCK_MODE == "SHARE ROW EXCLUSIVE",
        "legacy lock must block writers/other migration guards while permitting reads",
    )
    lock_connection = FakeQuiescentConnection()
    target_guard.prepare_quiescent_apply_transaction(lock_connection)  # type: ignore[arg-type]
    expected_preamble = [
        "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
        f"SET LOCAL lock_timeout = '{roundtrip.LOCK_TIMEOUT_MS}ms'",
        f"SET LOCAL statement_timeout = '{roundtrip.STATEMENT_TIMEOUT_MS}ms'",
    ]
    require(
        lock_connection.statements
        == [*expected_preamble, *target_guard.legacy_write_lock_statements()],
        "transaction settings and exact table-lock order differ",
    )
    require(
        all(lock_connection.reader_allowed(name) for name in expected_legacy_lock_tables),
        "SHARE ROW EXCLUSIVE fake contract blocked a plain reader",
    )
    require(
        not any(lock_connection.writer_allowed(name) for name in expected_legacy_lock_tables),
        "concurrent writer was not excluded from every legacy table",
    )

    backup_contract = {
        "applicationSchemaDigest": base_state["applicationSchemaDigest"],
        "legacyApplicationTableCount": base_state["legacyData"]["tableCount"],
        "legacyRowCount": base_state["legacyData"]["rowCount"],
        "legacyDataAggregateSha256": base_state["legacyData"]["aggregateSha256"],
    }
    verified_head = {
        "state": {
            **base_state,
            "currentRevision": [roundtrip.HEAD_REVISION],
            "applicationTableCount": target_guard.EXPECTED_HEAD_APPLICATION_TABLES,
            "publicTableCount": target_guard.EXPECTED_HEAD_PUBLIC_TABLES,
        },
        "modelParity": {
            "modelTableCount": target_guard.EXPECTED_HEAD_APPLICATION_TABLES,
            "differenceCount": 0,
        },
    }
    successful_engine = FakeTransactionEngine()
    migration_result = {
        "command": f"alembic upgrade {roundtrip.HEAD_REVISION}",
        "exitCode": 0,
        "outputSha256": "9" * 64,
        "existingSyncConnection": True,
    }
    with (
        patch.object(target_guard, "build_target_sync_engine", return_value=successful_engine),
        patch.object(target_guard, "_state_from_connection", return_value=base_state) as state_call,
        patch.object(target_guard, "run_exact_upgrade", return_value=migration_result) as upgrade_call,
        patch.object(
            target_guard,
            "_verified_head_from_connection",
            return_value=verified_head,
        ) as verify_call,
    ):
        transaction_result = target_guard.execute_quiescent_upgrade(
            local,
            backup_contract,
        )
    require(transaction_result["migration"] == migration_result, "transaction result differs")
    require(
        successful_engine.begin_calls == successful_engine.commit_calls == 1
        and successful_engine.rollback_calls == 0
        and successful_engine.dispose_calls == 1,
        "successful apply was not one committed transaction",
    )
    require(
        state_call.call_args.args[0] is successful_engine.connection
        and upgrade_call.call_args.args[0] is successful_engine.connection
        and verify_call.call_args.args[0] is successful_engine.connection,
        "fingerprint, Alembic, and post-check did not share one connection",
    )

    failed_engine = FakeTransactionEngine()
    with (
        patch.object(target_guard, "build_target_sync_engine", return_value=failed_engine),
        patch.object(target_guard, "_state_from_connection", return_value=base_state),
        patch.object(target_guard, "run_exact_upgrade", side_effect=RuntimeError("synthetic")),
    ):
        expect_error(
            lambda: target_guard.execute_quiescent_upgrade(local, backup_contract),
            "failed migration did not raise the transactional guard error",
        )
    require(
        failed_engine.begin_calls == failed_engine.rollback_calls == 1
        and failed_engine.commit_calls == 0
        and failed_engine.dispose_calls == 1,
        "failed apply did not roll back the one transaction",
    )

    neon = target_fixture(tls=True)
    require(
        target_guard.sync_database_url(local).drivername == "postgresql+psycopg",
        "target apply is not using the synchronous psycopg driver",
    )
    local_sync_args = target_guard.target_sync_connect_args(local)
    require(
        local_sync_args
        == {
            "connect_timeout": 20,
            "application_name": target_guard.ALEMBIC_TARGET_APPLICATION_NAME,
            "options": (
                f"-c lock_timeout={roundtrip.LOCK_TIMEOUT_MS}ms "
                f"-c statement_timeout={roundtrip.STATEMENT_TIMEOUT_MS}ms"
            ),
            "sslmode": "disable",
        },
        "local sync apply connection guard differs",
    )
    synthetic_ca = ROOT / "never-created-synthetic-ca.pem"
    with patch.object(target_guard, "_ensure_neon_ca_bundle", return_value=synthetic_ca):
        neon_sync_args = target_guard.target_sync_connect_args(neon)
    require(
        neon_sync_args["sslmode"] == "verify-full"
        and neon_sync_args["sslrootcert"] == str(synthetic_ca)
        and neon_sync_args["channel_binding"] == "require",
        "Neon sync apply TLS guard differs",
    )
    hostile_pg_environment = {
        "PGHOSTADDR": "203.0.113.20",
        "PGSERVICE": "attacker-service",
        "PGOPTIONS": "-c search_path=attacker",
        "PGPASSFILE": "attacker.pgpass",
    }
    with patch.dict(os.environ, hostile_pg_environment, clear=False):
        local_pg_environment = target_guard.pg_environment(local)
    require(
        set(local_pg_environment)
        & set(hostile_pg_environment)
        == set(),
        "backup subprocess inherited hostile libpq defaults",
    )
    require(
        {
            key
            for key in local_pg_environment
            if key.upper().startswith("PG")
        }
        == {
            "PGHOST",
            "PGPORT",
            "PGDATABASE",
            "PGUSER",
            "PGPASSWORD",
            "PGAPPNAME",
            "PGCONNECT_TIMEOUT",
            "PGSSLMODE",
        },
        "backup subprocess libpq allowlist differs",
    )
    guarded_url = make_url(target_guard.alembic_database_url(neon))
    require(
        not guarded_url.query,
        "raw target URL must not carry asyncpg server settings",
    )
    with patch.dict(os.environ, hostile_pg_environment, clear=False):
        environment = target_guard.alembic_environment(neon)
    require(
        not set(hostile_pg_environment) & set(environment),
        "target Alembic environment inherited hostile libpq defaults",
    )
    require(
        {
            name: environment[name]
            for name in (
                "ALEMBIC_GUARD_MODE",
                "ALEMBIC_LOCK_TIMEOUT_MS",
                "ALEMBIC_STATEMENT_TIMEOUT_MS",
                "ALEMBIC_APPLICATION_NAME",
            )
        }
        == {
            "ALEMBIC_GUARD_MODE": "v377",
            "ALEMBIC_LOCK_TIMEOUT_MS": str(roundtrip.LOCK_TIMEOUT_MS),
            "ALEMBIC_STATEMENT_TIMEOUT_MS": str(roundtrip.STATEMENT_TIMEOUT_MS),
            "ALEMBIC_APPLICATION_NAME": target_guard.ALEMBIC_TARGET_APPLICATION_NAME,
        },
        "target Alembic guard environment differs",
    )
    require(environment["AUTH_TRUSTED_PROXY_MODE"] == "render", "migration proxy guard differs")
    require(environment["EMAIL_OUTBOX_WORKER_ENABLED"] == "true", "outbox production guard differs")
    require(
        len(environment["AUTH_ABUSE_SECRET"]) >= 32,
        "process-only abuse secret does not satisfy Settings",
    )
    with patch.dict(os.environ, environment, clear=True):
        settings = Settings(_env_file=None)
    require(settings.auth_abuse_ready, "process-only migration Settings fail abuse guard")
    require(settings.brevo_ready, "process-only migration Settings fail email guard")

    env_source = (BACKEND / "alembic/env.py").read_text(encoding="utf-8")
    for required in (
        'ALEMBIC_V377_GUARD_MODE = "v377"',
        'ALEMBIC_V377_LOCK_TIMEOUT_MS = "5000"',
        'ALEMBIC_V377_STATEMENT_TIMEOUT_MS = "120000"',
        '"upgrade-rpg-v377-isolated-migration"',
        '"upgrade-rpg-v377-target-migration"',
        'connect_args["server_settings"]',
        'config.attributes.get("connection")',
        "build_alembic_connect_args(guard_required=True)",
        "do_run_migrations(existing_connection)",
    ):
        require(required in env_source, f"Alembic env guard is missing {required}")

    expect_error(
        lambda: target_guard.validate_execution_confirmation(
            source_sha="0" * 40,
            target=local,
            target_database=local.database,
            current_revision=roundtrip.BASE_REVISION,
            head_revision=roundtrip.HEAD_REVISION,
            head_sha256=roundtrip.REVISION_SHA256[roundtrip.HEAD_REVISION],
            action="wrong-action",
            expected_action=target_guard.APPLY_ACTION,
        ),
        "target guard accepted an incorrect mutation action",
    )
    upgrade_source = python_inspect.getsource(target_guard.run_exact_upgrade)
    require("alembic_command.upgrade" in upgrade_source, "programmatic exact upgrade is missing")
    require(
        'config.attributes["connection"] = connection' in upgrade_source,
        "Alembic did not receive the guarded existing connection",
    )
    require("subprocess" not in upgrade_source, "target upgrade still uses a subprocess")
    for forbidden in ('"downgrade"', '"stamp"', '"restore"'):
        require(forbidden not in upgrade_source, f"target upgrade contains {forbidden}")
    apply_source = python_inspect.getsource(target_guard.execute_quiescent_upgrade)
    ordered_calls = (
        "prepare_quiescent_apply_transaction",
        "_state_from_connection",
        "validate_backup_matches_target",
        "run_exact_upgrade",
        "_verified_head_from_connection",
        "compare_legacy_data",
    )
    require(
        [apply_source.index(name) for name in ordered_calls]
        == sorted(apply_source.index(name) for name in ordered_calls),
        "locked apply sequence differs",
    )
    require("with engine.begin() as connection" in apply_source, "single transaction boundary missing")
    require("collect_target_state" not in apply_source, "apply uses a pre-transaction fingerprint")
    require("verify_head(" not in apply_source, "apply uses a post-commit verifier")
    plan = target_guard.render_plan()
    require("fresh-backup" in plan, "fresh backup boundary missing")
    require("SHARE ROW EXCLUSIVE" in plan, "quiescent legacy write-lock boundary missing")
    require("no downgrade/stamp/restore/retry" in plan, "no-downgrade boundary missing")

    roundtrip_engine_source = python_inspect.getsource(roundtrip.engine_for)
    target_engine_source = python_inspect.getsource(target_guard.build_target_sync_engine)
    require(
        "guard_sqlalchemy_libpq_engine" in roundtrip_engine_source
        and "guard_sqlalchemy_libpq_engine" in target_engine_source,
        "sync psycopg engines do not strip inherited libpq defaults at connect time",
    )

    trusted_tool_source = python_inspect.getsource(pg_safety.trusted_posix_executable)
    for marker in ("resolve(strict=True)", "st_uid", "stat.S_IWGRP", "stat.S_IWOTH"):
        require(marker in trusted_tool_source, f"POSIX tool trust check is missing: {marker}")
    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-v377-pg-tool-") as temp:
        shim = Path(temp) / "pg_dump"
        shim.write_text("synthetic executable shim", encoding="utf-8")
        shim.chmod(0o777)
        with (
            patch.object(pg_safety.shutil, "which", return_value=str(shim)),
            patch.object(pg_safety.os, "access", return_value=True),
            patch.object(
                pg_safety.os,
                "geteuid",
                return_value=shim.stat().st_uid,
                create=True,
            ),
        ):
            try:
                pg_safety.trusted_posix_executable("pg_dump")
            except pg_safety.PostgresClientSafetyError:
                pass
            else:
                raise AssertionError("group/world-writable PostgreSQL PATH shim was trusted")


def test_private_artifact_boundaries() -> None:
    roundtrip_local = python_inspect.getsource(roundtrip.local_database_url)
    require(
        roundtrip_local.index("verify_local_environment_file")
        < roundtrip_local.index("load_backend_objects"),
        "round-trip reads backend/.env before private-permission verification",
    )
    roundtrip_model = python_inspect.getsource(roundtrip.validate_model_parity)
    require(
        roundtrip_model.index("verify_local_environment_file")
        < roundtrip_model.index("load_backend_objects"),
        "round-trip model parity reads backend/.env before permission verification",
    )
    target_model = python_inspect.getsource(target_guard._model_parity_from_connection)
    require(
        target_model.index("_verify_private_input(LOCAL_ENV_FILE")
        < target_model.index("load_backend_objects"),
        "target model parity reads backend/.env before permission verification",
    )
    roundtrip_inspect = python_inspect.getsource(roundtrip.inspect_readiness)
    require(
        "prepare_private_report_storage" not in roundtrip_inspect
        and "harden_private" not in roundtrip_inspect,
        "round-trip inspect mutates private artifact permissions",
    )
    roundtrip_execute = python_inspect.getsource(roundtrip.execute_roundtrip)
    require(
        roundtrip_execute.index("inspect_readiness")
        < roundtrip_execute.index("prepare_private_report_storage")
        < roundtrip_execute.index("write_report"),
        "round-trip evidence storage is not prepared after readiness and before writing",
    )
    require(
        "write_report(checkpoint, create_only=True)" in roundtrip_execute
        and roundtrip_execute.index("write_report(checkpoint, create_only=True)")
        < roundtrip_execute.index("create_isolated_database"),
        "round-trip one-attempt report is not created exclusively before DB creation",
    )
    roundtrip_storage = python_inspect.getsource(roundtrip.prepare_private_report_storage)
    require(
        "harden_private_directory(REVIEW_ARTIFACT_ROOT)" in roundtrip_storage
        and "verify_private_directory(REVIEW_ARTIFACT_ROOT)" in roundtrip_storage,
        "round-trip evidence root is not protected against ancestor replacement",
    )

    target_load = python_inspect.getsource(target_guard.load_target)
    local_branch = target_load[target_load.index('if label == "local"') :]
    require(
        local_branch.index("_verify_private_input(LOCAL_ENV_FILE")
        < local_branch.index("load_backend_objects"),
        "target guard reads backend/.env before private-permission verification",
    )
    require(
        target_load.index('require(label == "neon"')
        < target_load.index("_load_env_keys(NEON_ENV_FILE)"),
        "target guard Neon environment flow differs",
    )
    target_inspect = python_inspect.getsource(target_guard.inspect_target_readiness)
    require(
        "_prepare_private_artifact_storage" not in target_inspect
        and "harden_private" not in target_inspect,
        "target inspect mutates private artifact permissions",
    )
    target_storage = python_inspect.getsource(target_guard._prepare_private_artifact_storage)
    require(
        "harden_private_directory(parent)" in target_storage
        and "verify_private_directory(parent)" in target_storage,
        "target artifact roots are not protected against ancestor replacement",
    )

    backup_source = python_inspect.getsource(target_guard.create_fresh_backup)
    require(
        backup_source.index("_prepare_private_artifact_storage")
        < backup_source.index("load_verified_roundtrip_evidence")
        < backup_source.index("collect_target_state"),
        "backup does not prepare private storage before evidence/DB work",
    )
    require(
        backup_source.index("_write_attempt_marker")
        < backup_source.index("pg_environment(target)")
        < backup_source.index("create_private_file(partial_dump_path)"),
        "backup durable one-attempt marker is not created before client setup/staging",
    )
    require(
        backup_source.index("create_private_file(partial_dump_path)")
        < backup_source.index("_run_backup_command"),
        "pg_dump can write before its private output file exists",
    )
    for required in (
        "write_private_text_atomic(\n            checksum_path",
        "write_private_text_atomic(\n            manifest_path",
    ):
        require(required in backup_source, f"backup private writer is missing: {required}")

    evidence_source = python_inspect.getsource(
        target_guard.load_verified_roundtrip_evidence
    )
    require(
        evidence_source.index("_verify_private_input")
        < evidence_source.index("read_bytes"),
        "round-trip evidence is read before private-permission verification",
    )
    verified_backup = python_inspect.getsource(target_guard.load_verified_backup)
    for path_name, read_call in (
        ("manifest_path", "manifest_path.read_text"),
        ("checksum_path", "checksum_path.read_text"),
    ):
        require(
            verified_backup.index(f"_verify_private_input({path_name}")
            < verified_backup.index(read_call),
            f"{path_name} is read before private-permission verification",
        )

    apply_source = python_inspect.getsource(target_guard.apply_exact_upgrade)
    require(
        apply_source.index("_prepare_private_artifact_storage")
        < apply_source.index("load_verified_roundtrip_evidence")
        < apply_source.index("_write_attempt_marker")
        < apply_source.index("execute_quiescent_upgrade")
        < apply_source.index("write_private_text_atomic"),
        "apply private-storage/read/migrate/report order differs",
    )

    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-v377-attempt-marker-") as temp:
        marker = Path(temp) / "attempt.json"
        with patch.object(private_artifacts, "_fsync_parent_directory") as durable_sync:
            write_private_text_exclusive(marker, "started\n", encoding="utf-8")
            require(
                durable_sync.call_args_list == [((marker,), {})],
                "one-attempt marker did not sync its parent directory entry",
            )
            try:
                write_private_text_exclusive(marker, "retry\n", encoding="utf-8")
            except PrivatePathError:
                pass
            else:
                raise AssertionError("private one-attempt marker allowed an overwrite")
    exclusive_source = python_inspect.getsource(private_artifacts.write_private_bytes_exclusive)
    atomic_source = python_inspect.getsource(private_artifacts.write_private_bytes_atomic)
    parent_sync_source = python_inspect.getsource(private_artifacts._fsync_parent_directory)
    require(
        "_fsync_parent_directory(selected)" in exclusive_source
        and "_fsync_parent_directory(selected)" in atomic_source,
        "private evidence writers do not persist their directory entries",
    )
    require(
        'if os.name == "nt"' in parent_sync_source
        and 'getattr(os, "O_DIRECTORY", 0)' in parent_sync_source
        and "os.fsync(descriptor)" in parent_sync_source,
        "POSIX parent-directory durability boundary differs",
    )


def main() -> None:
    test_revision_model_parity()
    test_isolated_roundtrip_guard()
    test_target_apply_guard()
    test_private_artifact_boundaries()
    print("OK: v377 auth security migration parity/guard smoke passed")


if __name__ == "__main__":
    main()
