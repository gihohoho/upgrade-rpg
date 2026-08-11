#!/usr/bin/env python3
"""DB-free parity smoke for the v371 email identity Alembic source."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
from typing import Any

import sqlalchemy as sa


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
REVISION = BACKEND / "alembic/versions/v371_email_identity_lifecycle.py"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.models import User, UserEmailActionToken  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class OperationRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _record(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((name, args, kwargs))

    def f(self, name: str) -> str:
        return name

    def add_column(self, *args: Any, **kwargs: Any) -> None:
        self._record("add_column", *args, **kwargs)

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        self._record("create_index", *args, **kwargs)

    def create_table(self, *args: Any, **kwargs: Any) -> None:
        self._record("create_table", *args, **kwargs)

    def drop_index(self, *args: Any, **kwargs: Any) -> None:
        self._record("drop_index", *args, **kwargs)

    def drop_table(self, *args: Any, **kwargs: Any) -> None:
        self._record("drop_table", *args, **kwargs)

    def drop_column(self, *args: Any, **kwargs: Any) -> None:
        self._record("drop_column", *args, **kwargs)


def load_revision():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("v371_email_identity_lifecycle", REVISION)
    require(spec is not None and spec.loader is not None, "cannot load v371 revision source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def column_signature(column: sa.Column[Any]) -> tuple[str, str, bool, str | None]:
    default = None
    if column.server_default is not None:
        default = str(column.server_default.arg).strip("'\"")
    return column.name, str(column.type), bool(column.nullable), default


def main() -> None:
    require(REVISION.is_file(), "v371 revision file is missing")
    source = REVISION.read_text(encoding="utf-8")
    for forbidden in ("op.execute(", "op.bulk_insert(", "autogenerate", "UPDATE users", "INSERT INTO"):
        require(forbidden not in source, f"migration contains forbidden mutation helper: {forbidden}")

    module = load_revision()
    require(module.revision == "v371_email_identity_lifecycle", "unexpected v371 revision id")
    require(module.down_revision == "v295_initial_schema", "v371 must directly revise v295")
    require(module.branch_labels is None and module.depends_on is None, "unexpected Alembic branch")

    upgrade = OperationRecorder()
    module.op = upgrade
    module.upgrade()

    added = {
        args[1].name: column_signature(args[1])
        for name, args, _kwargs in upgrade.calls
        if name == "add_column" and args[0] == "users"
    }
    require(set(added) == {"email_original", "email_canonical", "email_verified_at", "auth_version"}, "users email columns mismatch")
    require(added["email_original"] == ("email_original", "VARCHAR(254)", True, None), "email_original contract mismatch")
    require(added["email_canonical"] == ("email_canonical", "VARCHAR(254)", True, None), "email_canonical contract mismatch")
    require(added["email_verified_at"][2] is True, "legacy email verification must remain nullable")
    require(added["auth_version"][2:] == (False, "0"), "auth_version must be not-null with server default 0")

    table_calls = [call for call in upgrade.calls if call[0] == "create_table"]
    require(len(table_calls) == 1, "v371 must create exactly one table")
    _, table_args, _ = table_calls[0]
    require(table_args[0] == "user_email_action_tokens", "unexpected v371 table name")
    parts = table_args[1:]
    columns = {part.name: column_signature(part) for part in parts if isinstance(part, sa.Column)}
    expected_columns = {
        "id", "user_id", "purpose", "token_digest", "expires_at", "consumed_at",
        "delivery_status", "delivery_attempted_at", "delivered_at", "provider_message_id",
        "delivery_error_code", "created_at", "updated_at",
    }
    require(set(columns) == expected_columns, "email action token columns mismatch")
    require(columns["token_digest"][:3] == ("token_digest", "VARCHAR(64)", False), "token digest contract mismatch")
    require(columns["delivery_status"][2:] == (False, "pending"), "delivery status default mismatch")

    check_names = {part.name for part in parts if isinstance(part, sa.CheckConstraint)}
    require(check_names == {"ck_user_email_action_tokens_purpose", "ck_user_email_action_tokens_delivery_status"}, "token check constraints mismatch")
    foreign_keys = [part for part in parts if isinstance(part, sa.ForeignKeyConstraint)]
    require(len(foreign_keys) == 1 and foreign_keys[0].ondelete == "CASCADE", "token user FK must cascade")

    indexes = {
        (args[0], args[1], tuple(args[2]), bool(kwargs.get("unique", False)))
        for name, args, kwargs in upgrade.calls
        if name == "create_index"
    }
    required_indexes = {
        ("ix_users_email_canonical", "users", ("email_canonical",), True),
        ("ix_user_email_action_tokens_token_digest", "user_email_action_tokens", ("token_digest",), True),
        ("ix_user_email_action_tokens_user_purpose_expires", "user_email_action_tokens", ("user_id", "purpose", "expires_at"), False),
        ("ix_user_email_action_tokens_expires_at", "user_email_action_tokens", ("expires_at",), False),
    }
    require(required_indexes <= indexes, "required v371 indexes are missing")

    user_model_columns = set(User.__table__.columns.keys())
    require(set(added) <= user_model_columns, "User model/revision columns differ")
    token_model_columns = set(UserEmailActionToken.__table__.columns.keys())
    require(token_model_columns == expected_columns, "UserEmailActionToken model/revision columns differ")

    downgrade = OperationRecorder()
    module.op = downgrade
    module.downgrade()
    dropped_columns = [args[1] for name, args, _kwargs in downgrade.calls if name == "drop_column" and args[0] == "users"]
    require(dropped_columns == ["auth_version", "email_verified_at", "email_canonical", "email_original"], "downgrade users column order mismatch")
    require(any(name == "drop_table" and args[0] == "user_email_action_tokens" for name, args, _kwargs in downgrade.calls), "downgrade token table drop missing")

    print("OK: v371 email identity migration source parity smoke passed")


if __name__ == "__main__":
    main()
