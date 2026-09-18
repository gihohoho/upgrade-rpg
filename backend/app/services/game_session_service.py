"""One locked transaction settles time, applies a command, and records its receipt."""

import asyncio
import hashlib
import json
import logging
import math
import secrets
import time
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import CurrentUser
from app.models import GameActionReceipt, GameSession, User, UserSaveSnapshot
from app.schemas.game_session import GameCommand, GameSessionIdentity
from app.services.account_character_service import account_character_metadata
from app.services.game_engine import simulate
from app.services.game_service import GameService

logger = logging.getLogger(__name__)
LEASE_SECONDS = 45
SETTLEMENT_SECONDS = 60
_engine_limit = asyncio.Semaphore(2)
_master_cache: tuple[float, dict] | None = None


def enabled():
    if not settings.game_server_authority_enabled:
        raise HTTPException(503, "서버 사냥을 준비 중입니다. 잠시 후 다시 접속해 주세요.")


def milliseconds(value: datetime) -> int:
    return int(value.timestamp() * 1000)


async def master_data(db: AsyncSession) -> dict:
    global _master_cache
    if _master_cache is None or time.monotonic() - _master_cache[0] > 60:
        _master_cache = (
            time.monotonic(),
            await GameService().get_master_data(db, include_assets=False),
        )
    return _master_cache[1]


async def owned_locked(db: AsyncSession, user_id: int, identity: GameSessionIdentity):
    row = await db.scalar(
        select(UserSaveSnapshot)
        .where(
            UserSaveSnapshot.user_id == user_id,
            UserSaveSnapshot.slot_key == identity.slot_key,
        )
        .with_for_update()
    )
    metadata = account_character_metadata(row) if row else None
    if not metadata or metadata["id"] != identity.account_character_id:
        raise HTTPException(404, "선택한 캐릭터를 찾을 수 없습니다.")
    state = await db.scalar(select(GameSession).where(GameSession.snapshot_id == row.id))
    return row, state


async def valid_user(db: AsyncSession, row: UserSaveSnapshot, state: GameSession) -> bool:
    user = await db.get(User, row.user_id)
    return bool(
        user
        and user.is_active
        and user.auth_version == state.auth_version
        and (not user.email_canonical or user.email_verified_at)
    )


async def run_engine(db, row, state, target: datetime, command=None):
    master = await master_data(db)
    async with _engine_limit:
        outcome = await asyncio.to_thread(
            simulate,
            row.snapshot_json,
            state.runtime_json,
            master,
            now_ms=milliseconds(target),
            seed=state.rng_seed,
            rng_cursor=state.rng_cursor,
            command=command,
        )
    row.snapshot_json = outcome["snapshot"]
    row.source = "server-gameplay"
    row.save_version = 5
    player = row.snapshot_json["player"]
    row.summary_json = {
        **row.summary_json,
        "gold": player.get("gold", 0),
        "currentZoneType": row.snapshot_json.get("currentZoneType"),
        "inventoryCount": sum(bool(item) for item in player.get("inventory", [])),
    }
    state.runtime_json = outcome["runtime"]
    combat = state.runtime_json["game"]["combat"]
    for name in ("currentBoss", "lastSummonedBoss"):
        boss = combat.get(name)
        if boss:
            combat[name] = {"id": boss["id"], "isSpecial": bool(boss.get("isSpecial"))}
    state.rng_cursor = outcome["rngCursor"]
    state.settled_at = target
    state.revision += 1
    return {"result": outcome["result"], "logs": outcome["logs"]}


async def settle(db, row, state, target: datetime):
    outcome = {"result": None, "logs": []}
    # Even recovery after a long server outage is bounded by the last live lease.
    target = min(target, state.lease_until)
    if state.active and target > state.settled_at:
        outcome = await run_engine(db, row, state, target)
    return outcome


def response(row, state, outcome=None):
    return {
        "sessionKey": state.session_key,
        "revision": state.revision,
        "active": state.active,
        "connected": state.connected,
        "snapshot": row.snapshot_json,
        "runtime": state.runtime_json,
        "settledAt": milliseconds(state.settled_at),
        "serverNow": milliseconds(datetime.now(UTC)),
        "nextSettlementAt": milliseconds(state.settled_at + timedelta(seconds=SETTLEMENT_SECONDS)),
        **(outcome or {"result": None, "logs": []}),
    }


async def open_session(db: AsyncSession, user: CurrentUser, identity: GameSessionIdentity):
    enabled()
    row, state = await owned_locked(db, user.id, identity)
    now = datetime.now(UTC)
    if state is None:
        state = GameSession(
            snapshot_id=row.id,
            session_key=secrets.token_hex(32),
            auth_version=user.auth_version,
            active=False,
            connected=False,
            lease_until=now,
            settled_at=now,
            revision=0,
            rng_seed=secrets.token_hex(32),
            rng_cursor=0,
            runtime_json={},
        )
        db.add(state)
    else:
        await settle(db, row, state, now)
        state.session_key = secrets.token_hex(32)
    if not row.snapshot_json.get("player"):
        row.snapshot_json = {
            "player": {"currentCharacterId": account_character_metadata(row)["characterCode"]}
        }
    # Opening a tab always starts in town; no closed/offline interval is credited.
    state.runtime_json = {}
    state.active = False
    state.connected = False
    state.connection_key = None
    state.auth_version = user.auth_version
    state.lease_until = now
    await run_engine(db, row, state, now, {"kind": "start"})
    await db.commit()
    return response(row, state)


def shift_runtime_clock(state, now):
    runtime = json.loads(json.dumps(state.runtime_json))
    clock = runtime["clock"]
    offset = milliseconds(now) - clock["cursor"]
    for key in ("cursor", "nextBuffAt", "nextMaintenanceAt", "nextAttackAt"):
        if clock.get(key) is not None:
            clock[key] += offset
    state.runtime_json = runtime
    state.settled_at = now


async def resume_session(db, user, identity):
    enabled()
    row, state = await owned_locked(db, user.id, identity)
    if (
        not state
        or state.session_key != identity.session_key
        or state.auth_version != user.auth_version
        or not state.runtime_json.get("clock", {}).get("running")
    ):
        raise HTTPException(409, "게임 접속이 종료되었거나 다른 탭으로 바뀌었습니다.")
    now = datetime.now(UTC)
    outcome = await settle(db, row, state, now)
    shift_runtime_clock(state, now)
    state.active = False
    state.connected = False
    state.connection_key = None
    state.lease_until = now
    state.revision += 1
    await db.commit()
    return response(row, state, outcome)


def validate_args(command: GameCommand):
    args = command.args
    required = {
        "field": {"index"},
        "summon": {"bossId", "special"},
        "auto_special": {"bossId"},
        "equip": {"slotType", "index", "itemId"},
        "unequip": {"slotType", "index", "itemId"},
        "enhance": {"slotType", "index", "itemId", "times"},
        "move": {"slotType", "index", "itemId"},
        "trash": {"slotType", "index", "itemId"},
        "reset_special": {"slotType", "index", "itemId"},
        "compact": {"slotType"},
        "mail": {"index", "mailId"},
        "trash_all": {"items"},
        "empty_trash": {"items"},
    }.get(command.kind, set())
    if set(args) != required:
        raise HTTPException(422, "게임 행동의 입력 값이 올바르지 않습니다.")
    for key, value in args.items():
        good = False
        if key in {"index", "times"}:
            good = type(value) is int and 0 <= value <= 10000
        elif key == "special":
            good = type(value) is bool
        elif key == "slotType":
            good = value in ("inv", "equip", "storage", "trash")
        elif key in {"itemId", "mailId", "bossId"}:
            good = type(value) in (str, int, float) and len(str(value)) <= 80
            if type(value) is float and not math.isfinite(value):
                good = False
            if key == "bossId" and command.kind == "auto_special" and value is None:
                good = True
        elif key == "items":
            good = (
                isinstance(value, list)
                and len(value) <= 10000
                and all(
                    isinstance(item, dict)
                    and set(item) == {"id", "count", "level"}
                    and isinstance(item["id"], str)
                    and len(item["id"]) <= 80
                    and type(item["count"]) is int
                    and 1 <= item["count"] <= 10**15
                    and type(item["level"]) is int
                    and 0 <= item["level"] <= 100
                    for item in value
                )
            )
        if not good:
            raise HTTPException(422, "게임 행동의 입력 값이 올바르지 않습니다.")


async def execute_command(db: AsyncSession, user: CurrentUser, command: GameCommand):
    enabled()
    validate_args(command)
    row, state = await owned_locked(db, user.id, command)
    digest = hashlib.sha256(
        json.dumps(
            {"kind": command.kind, "args": command.args},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    receipt = await db.scalar(
        select(GameActionReceipt).where(
            GameActionReceipt.snapshot_id == row.id,
            GameActionReceipt.request_id == command.request_id,
        )
    )
    if receipt:
        if receipt.request_hash != digest or receipt.session_key != command.session_key:
            raise HTTPException(409, "이미 사용한 요청 번호입니다.")
        # Return the committed result with CURRENT state. Never overwrite newer progress.
        return {**response(row, state, receipt.result_json), "replayed": True}
    now = datetime.now(UTC)
    if (
        not state
        or state.session_key != command.session_key
        or state.auth_version != user.auth_version
    ):
        raise HTTPException(409, "다른 게임 탭에서 접속했습니다. 이 탭을 새로고침해 주세요.")
    if not state.active or not state.connected or state.lease_until <= now:
        raise HTTPException(409, "게임 연결이 끊겼습니다. 다시 연결한 뒤 시도해 주세요.")
    # Rate limit commands per character while holding the same lock as settlement.
    last = await db.scalar(
        select(GameActionReceipt.created_at)
        .where(GameActionReceipt.snapshot_id == row.id)
        .order_by(GameActionReceipt.id.desc())
        .limit(1)
    )
    if last and (now - last).total_seconds() < 0.25:
        raise HTTPException(429, "처리 중입니다. 잠시 후 다시 시도해 주세요.")
    try:
        # One engine invocation settles elapsed combat first, then executes the action.
        outcome = await run_engine(
            db, row, state, now, {"kind": command.kind, "args": command.args}
        )
    except Exception as exc:
        await db.rollback()
        if any(
            code in str(exc) for code in ("selection_stale", "invalid_", "unknown_game_command")
        ):
            raise HTTPException(
                409, "선택한 항목이 변경됐습니다. 최신 상태를 확인하고 다시 선택해 주세요."
            ) from None
        logger.error("game engine rejected command kind=%s", command.kind)
        raise HTTPException(
            503, "게임 처리를 완료하지 못했습니다. 같은 요청으로 다시 확인해 주세요."
        ) from None
    if command.kind == "stop":
        state.active = False
        state.connected = False
        state.lease_until = now
    db.add(
        GameActionReceipt(
            snapshot_id=row.id,
            request_id=command.request_id,
            request_hash=digest,
            session_key=command.session_key,
            result_json=outcome,
        )
    )
    await db.commit()
    return {**response(row, state, outcome), "replayed": False}


async def pulse(db, user, identity, session_key, connection_key, *, opening=False, closing=False):
    row, state = await owned_locked(db, user.id, identity)
    if not state or state.session_key != session_key or not await valid_user(db, row, state):
        raise HTTPException(409, "game_session_replaced")
    now = datetime.now(UTC)
    if opening:
        if state.connection_key is not None:
            raise HTTPException(409, "game_socket_already_connected")
        # The socket can start an opened session once; expired sessions need a new open.
        if state.active and state.lease_until < now:
            raise HTTPException(409, "game_session_expired")
        state.connected = True
        state.active = True
        state.connection_key = connection_key
        shift_runtime_clock(state, now)
    elif state.connection_key != connection_key or not state.active:
        raise HTTPException(409, "game_socket_replaced")
    outcome = None
    if closing or (now - state.settled_at).total_seconds() >= SETTLEMENT_SECONDS:
        outcome = await settle(db, row, state, now)
    if closing or (not opening and state.lease_until < now):
        state.connected = False
        state.active = False
        state.lease_until = min(now, state.lease_until)
    else:
        state.lease_until = now + timedelta(seconds=LEASE_SECONDS)
    await db.commit()
    return (
        response(row, state, outcome)
        if opening or closing or outcome
        else {
            "sessionKey": state.session_key,
            "revision": state.revision,
            "active": state.active,
            "serverNow": milliseconds(now),
            "heartbeat": True,
        }
    )


async def run_game_session_worker(stop_event, session_factory):
    """Settle leases left behind by a crashed server; live sockets settle every minute."""
    while not stop_event.is_set():
        try:
            async with session_factory() as db:
                ids = list(
                    (
                        await db.scalars(
                            select(GameSession.snapshot_id)
                            .where(
                                GameSession.active.is_(True),
                                GameSession.lease_until < datetime.now(UTC),
                            )
                            .limit(100)
                        )
                    ).all()
                )
            for snapshot_id in ids:
                async with session_factory() as db:
                    row = await db.scalar(
                        select(UserSaveSnapshot)
                        .where(UserSaveSnapshot.id == snapshot_id)
                        .with_for_update(skip_locked=True)
                    )
                    if not row:
                        continue
                    state = await db.scalar(
                        select(GameSession).where(GameSession.snapshot_id == row.id)
                    )
                    if not state or not state.active or state.lease_until >= datetime.now(UTC):
                        continue
                    if await valid_user(db, row, state):
                        await settle(db, row, state, state.lease_until)
                    state.active = False
                    state.connected = False
                    await db.commit()
        except Exception:
            logger.error("game lease recovery failed; will retry")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=5)
        except TimeoutError:
            pass
