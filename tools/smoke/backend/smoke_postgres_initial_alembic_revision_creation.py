#!/usr/bin/env python3
"""Smoke checks for the v297 Alembic op.f parser recovery boundary."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/create_postgres_initial_alembic_revision.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("create_postgres_initial_alembic_revision", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load initial Alembic revision tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def counts() -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    values["table_00"] = 748
    return values


def evidence() -> dict[str, Any]:
    values = counts()
    return {
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def source_state() -> dict[str, Any]:
    values = counts()
    tables = sorted(values)
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": tables,
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": values,
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def rehearsal_state() -> dict[str, Any]:
    values = counts()
    tables = sorted(values)
    return {
        "connected": True,
        "database": "rpg_game_restore_rehearsal_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": tables,
        "tableCountsCollected": True,
        "tableCounts": values,
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
        "schemaClassification": "structurally-equivalent",
        "differenceCount": 0,
    }


def migration_state() -> dict[str, Any]:
    return {
        "connected": True,
        "database": "rpg_game_migration_empty_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 1,
        "publicTables": ["alembic_version"],
        "tableCountsCollected": True,
        "tableCounts": {"alembic_version": 0},
        "totalRows": 0,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [],
        "classification": "alembic-managed",
        "schemaClassification": "review-required",
        "differenceCount": 22,
    }


def pristine_migration_state() -> dict[str, Any]:
    state = migration_state()
    state.update({
        "publicTableCount": 0,
        "publicTables": [],
        "tableCounts": {},
        "alembicVersionTableExists": False,
        "classification": "empty-database",
    })
    return state


def unsafe_migration_state() -> dict[str, Any]:
    state = migration_state()
    state.update({
        "publicTableCount": 2,
        "publicTables": ["alembic_version", "users"],
        "tableCounts": {"alembic_version": 0, "users": 1},
        "totalRows": 1,
    })
    return state


def quote(value: str) -> str:
    return repr(value)


def fake_revision_source(module: Any, root: Path, *, forbidden: bool = False) -> str:
    baseline = module.model_review_baseline(root)
    lines = [
        '"""initial PostgreSQL schema"""',
        "from typing import Sequence, Union",
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        f"revision: str = {module.REVISION_ID!r}",
        "down_revision: Union[str, Sequence[str], None] = None",
        "branch_labels: Union[str, Sequence[str], None] = None",
        "depends_on: Union[str, Sequence[str], None] = None",
        "",
        "def upgrade() -> None:",
    ]
    for table_name, table in baseline.items():
        lines.append(f"    op.create_table({quote(table_name)},")
        for column_name, column in table["columns"].items():
            lines.append(
                f"        sa.Column({quote(column_name)}, sa.Integer(), nullable={column['nullable']!r}),"
            )
        for fk in table["foreignKeys"]:
            local = repr(list(fk["localColumns"]))
            remote = repr(list(fk["remoteColumns"]))
            kwargs = ""
            if fk["onDelete"]:
                kwargs += f", ondelete={fk['onDelete']!r}"
            if fk["onUpdate"]:
                kwargs += f", onupdate={fk['onUpdate']!r}"
            lines.append(f"        sa.ForeignKeyConstraint({local}, {remote}{kwargs}),")
        for columns in table["primaryKeys"]:
            args = ", ".join(quote(item) for item in columns)
            lines.append(f"        sa.PrimaryKeyConstraint({args}),")
        for columns in table["uniqueConstraints"]:
            args = ", ".join(quote(item) for item in columns)
            lines.append(f"        sa.UniqueConstraint({args}),")
        lines.append("    )")
        for index_number, index in enumerate(table["indexes"], start=1):
            lines.append(
                "    op.create_index("
                f"op.f('ix_{table_name}_{index_number}'), {quote(table_name)}, "
                f"{list(index['columns'])!r}, unique={index['unique']!r})"
            )
    if forbidden:
        lines.append("    op.execute('DELETE FROM users')")
    lines.extend(["", "def downgrade() -> None:"])
    for table_name, table in reversed(list(baseline.items())):
        for index_number, _ in reversed(list(enumerate(table["indexes"], start=1))):
            lines.append(
                f"    op.drop_index(op.f('ix_{table_name}_{index_number}'), table_name={quote(table_name)})"
            )
        lines.append(f"    op.drop_table({quote(table_name)})")
    lines.append("")
    return "\n".join(lines)


class FakeAlembicRunner:
    def __init__(self, module: Any, project_root: Path, *, forbidden: bool = False) -> None:
        self.module = module
        self.project_root = project_root
        self.forbidden = forbidden
        self.calls = 0
        self.commands: list[list[str]] = []
        self.envs: list[dict[str, str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.calls += 1
        self.commands.append(command)
        self.envs.append(dict(kwargs.get("env") or {}))
        cwd = Path(kwargs["cwd"])
        revision_path = cwd / "alembic/versions" / self.module.REVISION_FILENAME
        revision_path.write_text(
            fake_revision_source(self.module, self.project_root, forbidden=self.forbidden),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout=b"Generating revision\n", stderr=None)


def copy_project_for_test(destination: Path) -> None:
    shutil.copytree(ROOT / "backend", destination / "backend")
    # v298 commits the exact reviewed first revision. This smoke still tests the
    # historical generation tool, so each isolated fixture must start with an
    # empty versions directory just like the pre-generation workspace.
    versions_dir = destination / "backend/alembic/versions"
    for path in versions_dir.glob("*.py"):
        if path.name != "__init__.py":
            path.unlink()
    (destination / "local-review-artifacts").mkdir(parents=True, exist_ok=True)


def main() -> int:
    if not TOOL.exists():
        return fail("missing initial Alembic revision tool")
    template = ROOT / "backend/alembic/script.py.mako"
    if not template.exists():
        return fail("missing Alembic script.py.mako template")

    source = TOOL.read_text(encoding="utf-8")
    for marker in (
        "v295_initial_schema",
        "v297.postgres-initial-alembic-op-f-parser-recovery",
        "empty-alembic-version-placeholder",
        "ALEMBIC_NON_OPERATION_HELPERS",
        "--inspect-workspace",
        "safeRecoveryPlaceholder",
        "--autogenerate",
        "DATABASE_URL",
        "MIGRATION_TEST_DATABASE",
        "manualReviewRequiredBeforeUpgrade",
        "upgradeExecuted",
        "downgradeExecuted",
        "stampExecuted",
        "local-review-artifacts/alembic",
        "review_bundle.zip",
    ):
        if marker not in source:
            return fail(f"tool missing safety marker: {marker}")

    module = load_tool()
    guard = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if guard.returncode != 2 or "--execute" not in guard.stdout:
        return fail("tool must refuse generation without --execute")

    command = module.build_revision_command()
    command_text = " ".join(command)
    for required in ("revision", "--autogenerate", "--rev-id", module.REVISION_ID):
        if required not in command_text:
            return fail(f"revision command missing required token: {required}")
    for forbidden in ("upgrade", "downgrade", "stamp", "createdb", "dropdb", "pg_restore"):
        if forbidden in command:
            return fail(f"revision command contains forbidden operation: {forbidden}")

    with tempfile.TemporaryDirectory(prefix="v297_revision_parser_recovery_smoke_") as temporary:
        test_root = Path(temporary)
        copy_project_for_test(test_root)
        runner = FakeAlembicRunner(module, test_root)
        result = module.execute_generation(
            test_root,
            evidence=evidence(),
            source_before_raw=source_state(),
            source_after_raw=source_state(),
            rehearsal_before_raw=rehearsal_state(),
            rehearsal_after_raw=rehearsal_state(),
            migration_before_raw=migration_state(),
            migration_after_raw=migration_state(),
            run_process=runner,
        )
        if runner.calls != 1:
            return fail(f"Alembic revision command must run once, actual={runner.calls}")
        if not runner.envs or "rpg_game_migration_empty_v290" not in runner.envs[0].get("DATABASE_URL", ""):
            return fail("child DATABASE_URL must target only the empty migration DB")
        if result.get("result") != "initial-alembic-revision-created-and-automatically-reviewed":
            return fail("unexpected v297 parser recovery success classification")
        review = result.get("automatedReview") or {}
        if review.get("tableCount") != 22 or review.get("columnCount") != 209:
            return fail(f"automated review baseline mismatch: {review}")
        if (review.get("upgradeOperationCounts") or {}).get("create_table") != 22:
            return fail("upgrade must create exactly 22 tables")
        if (review.get("downgradeOperationCounts") or {}).get("drop_table") != 22:
            return fail("downgrade must drop exactly 22 tables")
        if "f" in (review.get("upgradeOperationCounts") or {}):
            return fail("nested op.f naming helper must not be counted as an upgrade operation")
        if "f" in (review.get("downgradeOperationCounts") or {}):
            return fail("nested op.f naming helper must not be counted as a downgrade operation")
        if result.get("migrationBefore") != result.get("migrationAfter"):
            return fail("autogenerate must preserve the empty Alembic placeholder workspace")
        if result.get("existingAlembicVersionPlaceholderReused") is not True:
            return fail("v297 must report reuse of the existing Alembic placeholder")
        if result.get("alembicVersionRowsWritten") is not False:
            return fail("v297 must not record any Alembic revision row")
        if result["migrationBefore"].get("revisionWorkspaceClassification") != "empty-alembic-version-placeholder":
            return fail("unexpected migration recovery workspace classification")
        for key in ("upgradeExecuted", "downgradeExecuted", "stampExecuted", "databaseCreateDropRestoreExecuted"):
            if result.get(key) is not False:
                return fail(f"forbidden execution boundary changed: {key}")
        revision_path = test_root / result["revisionRelativePath"]
        bundle_path = test_root / result["reviewBundleRelativePath"]
        if not revision_path.is_file() or not bundle_path.is_file():
            return fail("revision or review bundle was not created")
        if module.sha256_file(bundle_path) != result.get("reviewBundleSha256"):
            return fail("review bundle SHA-256 mismatch")
        with zipfile.ZipFile(bundle_path, "r") as archive:
            if archive.testzip() is not None:
                return fail("review bundle CRC failed")
            names = set(archive.namelist())
        if f"backend/alembic/versions/{module.REVISION_FILENAME}" not in names:
            return fail("review bundle missing revision file")
        if f"review/{module.REVIEW_JSON_FILENAME}" not in names:
            return fail("review bundle missing JSON report")

    with tempfile.TemporaryDirectory(prefix="v297_revision_pristine_block_") as temporary:
        test_root = Path(temporary)
        copy_project_for_test(test_root)
        runner = FakeAlembicRunner(module, test_root)
        try:
            module.execute_generation(
                test_root,
                evidence=evidence(),
                source_before_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                migration_before_raw=pristine_migration_state(),
                run_process=runner,
            )
        except module.InitialRevisionError as exc:
            if "requires the sole empty alembic_version placeholder" not in str(exc):
                return fail(f"pristine workspace guard returned unclear error: {exc}")
        else:
            return fail("v297 recovery must not create a new Alembic control table")
        if runner.calls != 0:
            return fail("pristine workspace guard must run no Alembic command")

    with tempfile.TemporaryDirectory(prefix="v297_revision_unsafe_block_") as temporary:
        test_root = Path(temporary)
        copy_project_for_test(test_root)
        runner = FakeAlembicRunner(module, test_root)
        try:
            module.execute_generation(
                test_root,
                evidence=evidence(),
                source_before_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                migration_before_raw=unsafe_migration_state(),
                run_process=runner,
            )
        except module.InitialRevisionError as exc:
            if "contains unexpected objects" not in str(exc):
                return fail(f"unsafe workspace guard returned unclear error: {exc}")
        else:
            return fail("unexpected application tables must block v297 recovery")
        if runner.calls != 0:
            return fail("unsafe workspace guard must run no Alembic command")

    with tempfile.TemporaryDirectory(prefix="v297_revision_forbidden_") as temporary:
        test_root = Path(temporary)
        copy_project_for_test(test_root)
        runner = FakeAlembicRunner(module, test_root, forbidden=True)
        try:
            module.execute_generation(
                test_root,
                evidence=evidence(),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=migration_state(),
                migration_after_raw=migration_state(),
                run_process=runner,
            )
        except module.InitialRevisionError as exc:
            if "forbidden upgrade operation" not in str(exc):
                return fail(f"forbidden-operation guard returned unclear error: {exc}")
        else:
            return fail("op.execute must fail automated revision review")
        revision_path = test_root / "backend/alembic/versions" / module.REVISION_FILENAME
        if revision_path.exists():
            return fail("failed generated revision must be cleaned up")

    with tempfile.TemporaryDirectory(prefix="v297_revision_existing_") as temporary:
        test_root = Path(temporary)
        copy_project_for_test(test_root)
        existing = test_root / "backend/alembic/versions/existing.py"
        existing.write_text("revision = 'existing'\n", encoding="utf-8")
        runner = FakeAlembicRunner(module, test_root)
        try:
            module.execute_generation(
                test_root,
                evidence=evidence(),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=migration_state(),
                migration_after_raw=migration_state(),
                run_process=runner,
            )
        except module.InitialRevisionError as exc:
            if "already contains revision files" not in str(exc):
                return fail(f"existing-revision guard returned unclear error: {exc}")
        else:
            return fail("existing revision must block v297 generation")
        if runner.calls != 0:
            return fail("existing revision guard must run no Alembic command")

    print("OK: PostgreSQL initial Alembic op.f parser recovery smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
