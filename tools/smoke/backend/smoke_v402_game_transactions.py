# ruff: noqa: E402
"""Real PostgreSQL concurrency/rollback smoke in a disposable LOCAL schema only.

Creates four synthetic tables in v402_game_test_<random>, tests the additive
migration up/down/up there, then removes that exact schema. Public data is untouched.
"""

import asyncio
from datetime import UTC, datetime, timedelta
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT / "backend")
from app.core.config import settings
from app.core.security import CurrentUser
from app.db.base import Base
from app.models import User, UserSaveSnapshot, GameSession, GameActionReceipt
from app.schemas.game_session import GameCommand, GameSessionIdentity, GameSessionResume
from app.services import game_session_service as service
from app.services.game_service import GameService


class Clock:
    value = datetime.now(UTC)

    @classmethod
    def now(cls, _tz=None):
        return cls.value

    @classmethod
    def advance(cls, seconds):
        cls.value += timedelta(seconds=seconds)


async def main():
    url = make_url(settings.database_url)
    assert (
        url.host in {"127.0.0.1", "localhost"}
        and url.port == 55432
        and url.database == "rpg_game"
    ), "local test target required"
    schema = "v402_game_test_" + uuid4().hex
    assert re.fullmatch(r"v402_game_test_[0-9a-f]{32}", schema)
    admin = create_async_engine(url, echo=False, hide_parameters=True)
    db_engine = create_async_engine(
        url,
        echo=False,
        hide_parameters=True,
        connect_args={
            "server_settings": {
                "search_path": schema,
                "statement_timeout": "15000",
                "lock_timeout": "10000",
            }
        },
    )
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    created = False
    old_enabled = settings.game_server_authority_enabled
    old_cache = service._master_cache
    try:
        async with admin.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA "{schema}"'))
        created = True
        async with db_engine.begin() as conn:

            def prepare(sync):
                Base.metadata.create_all(
                    sync, tables=[User.__table__, UserSaveSnapshot.__table__]
                )
                spec = importlib.util.spec_from_file_location(
                    "v402_migration",
                    ROOT / "backend/alembic/versions/v402_server_gameplay.py",
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                with Operations.context(MigrationContext.configure(sync)):
                    module.upgrade()
                    module.downgrade()
                    module.upgrade()

            await conn.run_sync(prepare)
        print("isolated migration up/down/up: PASS", flush=True)
        settings.game_server_authority_enabled = True
        # Static committed game data is sufficient for transaction semantics.
        service._master_cache = (time.monotonic() + 10000, None)
        identity = GameSessionIdentity(
            slotKey="character-1", accountCharacterId="a" * 32
        )
        async with factory() as db:
            user_row = User(
                username="v402-test",
                password_hash=None,
                is_active=True,
                is_admin=False,
                auth_version=0,
            )
            db.add(user_row)
            await db.flush()
            row = UserSaveSnapshot(
                user_id=user_row.id,
                slot_key="character-1",
                snapshot_json={"player": {"gold": 10**9, "farmAtkBonus": 10**12}},
                summary_json={
                    "accountCharacter": {
                        "id": "a" * 32,
                        "slotIndex": 1,
                        "name": "synthetic",
                        "characterCode": "weapon_master",
                        "createdAt": Clock.value.isoformat(),
                    }
                },
            )
            db.add(row)
            await db.commit()
            user = CurrentUser(id=user_row.id, username=user_row.username)
            snapshot_id = row.id
        with patch.object(service, "datetime", Clock):
            async with factory() as db:
                opened = await service.open_session(db, user, identity)
            key = opened["sessionKey"]
            async with factory() as db:
                await service.pulse(db, user, identity, key, "c" * 64, opening=True)

            def command(kind, request_id=None, **args):
                return GameCommand(
                    **identity.model_dump(by_alias=True),
                    sessionKey=key,
                    requestId=request_id or uuid4().hex,
                    kind=kind,
                    args=args,
                )

            async def execute(cmd):
                async with factory() as db:
                    return await service.execute_command(db, user, cmd)

            async def saved():
                async with factory() as db:
                    row = await db.get(UserSaveSnapshot, snapshot_id)
                    state = await db.scalar(
                        select(GameSession).where(
                            GameSession.snapshot_id == snapshot_id
                        )
                    )
                    return (
                        json.loads(json.dumps(row.snapshot_json)),
                        state.rng_cursor,
                        state.revision,
                    )

            Clock.advance(1)
            given = await execute(command("beginner"))
            item_id = given["snapshot"]["player"]["inventory"][0]["id"]
            Clock.advance(1)
            cmd = command("enhance", slotType="inv", index=0, itemId=item_id, times=20)
            first = await execute(cmd)
            before = await saved()
            second = await execute(cmd)
            assert (
                second["replayed"]
                and first["result"] == second["result"]
                and before == await saved()
            )
            assert before[0]["player"]["gold"] < 10**9
            print("commit then lost response/retry: PASS", flush=True)
            Clock.advance(1)
            concurrent = command(
                "enhance", slotType="inv", index=0, itemId=item_id, times=20
            )
            outcomes = await asyncio.gather(execute(concurrent), execute(concurrent))
            assert sorted(o["replayed"] for o in outcomes) == [False, True]
            assert outcomes[0]["result"] == outcomes[1]["result"]
            print("concurrent identical requests apply once: PASS", flush=True)
            Clock.advance(1)
            failed = command(
                "enhance", slotType="inv", index=0, itemId=item_id, times=20
            )
            before = await saved()
            async with factory() as db:

                async def fail_commit():
                    raise ConnectionError("synthetic commit failure")

                with patch.object(db, "commit", fail_commit):
                    try:
                        await service.execute_command(db, user, failed)
                    except ConnectionError:
                        pass
                    else:
                        raise AssertionError(
                            "commit failure should propagate without result"
                        )
            assert before == await saved()
            async with factory() as db:
                assert (
                    await db.scalar(
                        select(GameActionReceipt).where(
                            GameActionReceipt.request_id == failed.request_id
                        )
                    )
                    is None
                )
            retry = await execute(failed)
            assert not retry["replayed"]
            print(
                "rollback preserves material/gold/result/RNG together: PASS", flush=True
            )
            Clock.advance(1)
            lost_commit = command(
                "enhance", slotType="inv", index=0, itemId=item_id, times=20
            )
            async with factory() as db:
                real_commit = db.commit

                async def commit_then_disconnect():
                    await real_commit()
                    raise ConnectionError("synthetic lost commit acknowledgement")

                with patch.object(db, "commit", commit_then_disconnect):
                    try:
                        await service.execute_command(db, user, lost_commit)
                    except ConnectionError:
                        pass
            before = await saved()
            assert (await execute(lost_commit))["replayed"] and before == await saved()
            for changed in [
                cmd.model_copy(update={"kind": "beginner", "args": {}}),
                command("save").model_copy(update={"account_character_id": "b" * 32}),
            ]:
                try:
                    await execute(changed)
                except HTTPException as error:
                    assert error.status_code in {404, 409}
                else:
                    raise AssertionError("identity/request reuse must be rejected")
            async with factory() as db:
                try:
                    await GameService().save_game_snapshot(
                        db,
                        user_id=user.id,
                        payload=SimpleNamespace(snapshot={"player": {"gold": 10**100}}),
                    )
                except HTTPException as error:
                    assert error.status_code == 409
                else:
                    raise AssertionError("raw snapshot bypass")
            print(
                "ownership, request hash and raw-save bypass blocked: PASS", flush=True
            )
            Clock.advance(1)
            await execute(command("boss_zone"))
            Clock.advance(1)
            await execute(command("summon", bossId=1, special=False))
            Clock.advance(20)
            async with factory() as db:
                await service.pulse(db, user, identity, key, "c" * 64)
            Clock.advance(20)
            async with factory() as db:
                await service.pulse(db, user, identity, key, "c" * 64)
            Clock.advance(20)
            async with factory() as db:
                live = await service.pulse(db, user, identity, key, "c" * 64)
            assert live["snapshot"]["player"]["records"]["totalBossKills"] > 0
            Clock.advance(100)
            async with factory() as db:
                row, state = await service.owned_locked(db, user.id, identity)
                expected_until = state.lease_until
                await service.settle(db, row, state, Clock.now())
                assert state.settled_at == expected_until
                state.active = False
                state.connected = False
                await db.commit()
            before = await saved()
            try:
                await execute(command("save"))
            except HTTPException as error:
                assert error.status_code == 409
            else:
                raise AssertionError("expired session cannot play")
            Clock.advance(86400)
            async with factory() as db:
                resumed = await service.resume_session(
                    db,
                    user,
                    GameSessionResume(
                        **identity.model_dump(by_alias=True), sessionKey=key
                    ),
                )
            assert (
                resumed["snapshot"]["player"]["records"]["totalBossKills"]
                == before[0]["player"]["records"]["totalBossKills"]
            )
            assert resumed["snapshot"]["currentZoneType"] == "boss_fight"
            async with factory() as db:
                new = await service.open_session(db, user, identity)
            assert (
                new["snapshot"]["player"]["records"]["totalBossKills"]
                == before[0]["player"]["records"]["totalBossKills"]
            )
            assert new["snapshot"]["currentZoneType"] == "town"
            assert (
                new["snapshot"]["player"]["records"]["playTimeMs"]
                == before[0]["player"]["records"]["playTimeMs"]
            )
            try:
                await execute(command("save"))
            except HTTPException as error:
                assert error.status_code == 409
            else:
                raise AssertionError("replaced session must be invalid")
            print(
                "minute hunting, lease cutoff, 24h offline exclusion and tab replacement: PASS",
                flush=True,
            )
        print("v402 PostgreSQL transaction smoke: PASS", flush=True)
    finally:
        settings.game_server_authority_enabled = old_enabled
        service._master_cache = old_cache
        await db_engine.dispose()
        if created:
            # Literal identifier is generated here and checked before any removal.
            assert re.fullmatch(r"v402_game_test_[0-9a-f]{32}", schema)
            async with admin.begin() as conn:
                await conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


if __name__ == "__main__":
    asyncio.run(main())
