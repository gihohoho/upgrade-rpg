"""Exercise the production v402 migration transaction in a disposable LOCAL schema."""

# ruff: noqa: E402
from datetime import UTC, datetime
from pathlib import Path
import os
import re
import sys
from uuid import uuid4

os.environ["DEBUG"] = "false"
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "backend"))
import apply_v402_server_gameplay as guard
from sqlalchemy import text
from app.models import User, UserSaveSnapshot


def main():
    target = guard.connection_guard.load_target("local")
    engine = guard.connection_guard.build_target_sync_engine(target)
    engine.hide_parameters = True
    schema = "v402_preservation_" + uuid4().hex
    assert re.fullmatch(r"v402_preservation_[0-9a-f]{32}", schema)
    created = False
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            created = True
            conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            guard.Base.metadata.create_all(
                conn,
                tables=[
                    t
                    for t in guard.Base.metadata.sorted_tables
                    if t.name in guard.EXISTING
                ],
            )
            conn.execute(
                text(
                    "CREATE TABLE alembic_version (version_num varchar(32) PRIMARY KEY)"
                )
            )
            conn.execute(
                text("INSERT INTO alembic_version VALUES (:revision)"),
                {"revision": guard.PREVIOUS},
            )
            now = datetime.now(UTC)
            conn.execute(
                User.__table__.insert().values(
                    id=17,
                    username="synthetic-v402",
                    password_hash="not-a-real-login",
                    is_active=True,
                    is_admin=False,
                    auth_version=0,
                    created_at=now,
                    updated_at=now,
                )
            )
            conn.execute(
                UserSaveSnapshot.__table__.insert().values(
                    user_id=17,
                    slot_key="character-1",
                    save_version=5,
                    snapshot_json={
                        "player": {
                            "gold": 123456,
                            "inventory": [{"id": 1, "level": 7, "name": "보존 검증"}],
                        }
                    },
                    summary_json={},
                    created_at=now,
                    updated_at=now,
                )
            )
        with engine.begin() as conn:
            conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            result = guard.migrate_locked(conn, target)
            assert result["preservedTables"] == 25 and result["preservedRows"] == 2
        print(
            "v402 production migration transaction: 25 tables preserved, two added, model parity PASS"
        )
    finally:
        if created:
            assert re.fullmatch(r"v402_preservation_[0-9a-f]{32}", schema)
            with engine.begin() as conn:
                conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()


if __name__ == "__main__":
    main()
