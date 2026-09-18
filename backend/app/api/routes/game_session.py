import asyncio
import json
import secrets
import time
from contextlib import suppress

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.response import ok_response
from app.core.security import CurrentUser, create_access_token, get_current_user
from app.db.session import AsyncSessionLocal, get_db_session
from app.schemas.game_session import GameCommand, GameSessionIdentity, GameSessionResume
from app.services import game_session_service as service

router = APIRouter()


@router.get("/capabilities")
async def capabilities():
    return ok_response(
        type="game.capabilities",
        payload={
            "serverAuthority": settings.game_server_authority_enabled,
            "settlementSeconds": service.SETTLEMENT_SECONDS,
            "connectionGraceSeconds": service.LEASE_SECONDS,
        },
    )


@router.post("/open")
async def open_game(
    payload: GameSessionIdentity,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return ok_response(type="game.session", payload=await service.open_session(db, user, payload))


@router.post("/command")
async def command(
    payload: GameCommand,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return ok_response(
        type="game.command", payload=await service.execute_command(db, user, payload)
    )


@router.post("/resume")
async def resume_game(
    payload: GameSessionResume,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return ok_response(type="game.session", payload=await service.resume_session(db, user, payload))


@router.websocket("/live")
async def live(socket: WebSocket):
    # CORS middleware does not protect WebSockets. Authenticate without URL tokens.
    if (
        not settings.game_server_authority_enabled
        or socket.headers.get("origin") not in settings.cors_origins
    ):
        await socket.close(code=1008)
        return
    await socket.accept()
    connected = False
    connection_key = secrets.token_hex(32)
    user = identity = session_key = None
    receive_task = None
    try:
        raw = await asyncio.wait_for(socket.receive_text(), timeout=10)
        if len(raw) > 5000:
            raise ValueError("auth_message_too_large")
        auth = json.loads(raw)
        identity = GameSessionIdentity.model_validate(auth["identity"])
        session_key = auth["sessionKey"]
        if not isinstance(session_key, str) or len(session_key) != 64:
            raise ValueError("invalid_session")
        async with AsyncSessionLocal() as db:
            user = await get_current_user("Bearer " + str(auth["token"]), db)
            initial = await service.pulse(
                db, user, identity, session_key, connection_key, opening=True
            )
        if settings.access_token_expire_minutes == 0:
            # Upgrade a still-valid old login on connection; expired tokens cannot enter.
            initial["accessToken"] = create_access_token(user.id, auth_version=user.auth_version)[0]
        connected = True
        await socket.send_json(initial)
        # A pending receive lets protocol ping/pong detect closed/offline tabs even
        # when background JavaScript is throttled. No client timer is required.
        receive_task = asyncio.create_task(socket.receive_text())
        renewed_at = time.monotonic()
        while True:
            done, _ = await asyncio.wait({receive_task}, timeout=20)
            if done:
                message = receive_task.result()
                if message == "close":
                    break
                # Clients have no commands or heartbeat claims on this channel.
                raise ValueError("unexpected_socket_message")
            async with AsyncSessionLocal() as db:
                update = await service.pulse(db, user, identity, session_key, connection_key)
            # Only a still-live, database-validated login can extend its access token.
            # This allows a connected 24h idle tab without granting offline hunting.
            if (
                settings.access_token_expire_minutes > 0
                and update["active"]
                and time.monotonic() - renewed_at >= 3600
            ):
                update["accessToken"] = create_access_token(
                    user.id, auth_version=user.auth_version
                )[0]
                renewed_at = time.monotonic()
            await socket.send_json(update)
            if not update["active"]:
                break
    except (
        WebSocketDisconnect,
        HTTPException,
        ValueError,
        KeyError,
        ValidationError,
        TimeoutError,
    ):
        pass
    finally:
        if receive_task:
            receive_task.cancel()
            with suppress(asyncio.CancelledError, WebSocketDisconnect, RuntimeError):
                await receive_task
        if connected:
            with suppress(Exception):
                async with AsyncSessionLocal() as db:
                    await service.pulse(
                        db, user, identity, session_key, connection_key, closing=True
                    )
        with suppress(RuntimeError):
            await socket.close(code=1000)
