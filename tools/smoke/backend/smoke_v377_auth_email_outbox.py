#!/usr/bin/env python3
"""DB/network-free state-machine smoke for the v377 semantic email outbox."""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

from sqlalchemy.dialects import postgresql


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(BACKEND))

from app.models import AuthEmailOutbox, User, UserEmailActionToken  # noqa: E402
from app.services.auth_email_delivery import (  # noqa: E402
    EmailDeliveryError,
    EmailDeliveryResult,
)
from app.services.auth_email_outbox import (  # noqa: E402
    EMAIL_PURPOSE_VERIFY,
    AuthEmailOutboxService,
)


NOW = datetime(2026, 8, 15, 6, 0, tzinfo=UTC)
RAW_TOKEN = "R" * 43
TOKEN_SECRET = "t" * 40
ABUSE_SECRET = "a" * 40
RECIPIENT = "owner@example.com"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fake_settings() -> SimpleNamespace:
    return SimpleNamespace(
        jwt_secret_key="j" * 40,
        email_verification_expire_minutes=1440,
        password_reset_expire_minutes=30,
        account_deletion_expire_minutes=30,
        email_outbox_preparing_timeout_seconds=300,
        email_outbox_sending_timeout_seconds=120,
        email_outbox_retention_days=30,
        auth_rate_limit_retention_days=30,
        email_outbox_poll_seconds=1.0,
        email_outbox_maintenance_interval_seconds=300,
        public_frontend_origin="https://game.example.com",
    )


def outbox_row(
    *,
    row_id: int = 1,
    user_id: int | None = 22,
    target_digest: str = "d" * 64,
) -> AuthEmailOutbox:
    return AuthEmailOutbox(
        id=row_id,
        user_id=user_id,
        purpose=EMAIL_PURPOSE_VERIFY,
        target_digest=target_digest,
        status="pending",
        available_at=NOW,
        claimed_at=None,
        attempted_at=None,
        completed_at=None,
        attempt_count=0,
        action_token_id=None,
        provider_message_id=None,
        error_code=None,
        created_at=NOW,
        updated_at=NOW,
    )


def user_row(*, verified: bool = False) -> User:
    return User(
        id=22,
        username="player22",
        email_original="Owner@example.com",
        email_canonical=RECIPIENT,
        email_verified_at=NOW if verified else None,
        password_hash="safe-bcrypt-placeholder",
        auth_version=0,
        is_active=True,
        is_admin=False,
        created_at=NOW,
        updated_at=NOW,
    )


def existing_action_token(*, token_id: int = 700) -> UserEmailActionToken:
    return UserEmailActionToken(
        id=token_id,
        user_id=22,
        purpose=EMAIL_PURPOSE_VERIFY,
        token_digest="o" * 64,
        expires_at=NOW + timedelta(minutes=10),
        consumed_at=None,
        delivery_status="sent",
        delivery_attempted_at=NOW - timedelta(minutes=1),
        delivered_at=NOW - timedelta(minutes=1),
        provider_message_id="previous-provider-message",
        delivery_error_code=None,
        created_at=NOW - timedelta(minutes=1),
        updated_at=NOW - timedelta(minutes=1),
    )


class FakeResult:
    def __init__(self, rows: list[Any]):
        self.rows = list(rows)

    def scalar_one_or_none(self):  # type: ignore[no-untyped-def]
        if not self.rows:
            return None
        require(len(self.rows) == 1, "fake outbox result expected at most one row")
        return self.rows[0]

    def scalar_one(self):  # type: ignore[no-untyped-def]
        require(len(self.rows) == 1, "fake outbox result expected exactly one row")
        return self.rows[0]

    def all(self):  # type: ignore[no-untyped-def]
        return list(self.rows)


class ScriptedSession:
    def __init__(
        self,
        owner: "ScriptedSessionFactory",
        *,
        label: str,
        responses: list[Any],
    ) -> None:
        self.owner = owner
        self.label = label
        self.responses = list(responses)
        self.statements: list[Any] = []
        self.added: list[Any] = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.flush_calls = 0

    async def __aenter__(self):  # type: ignore[no-untyped-def]
        self.owner.active_sessions += 1
        return self

    async def __aexit__(self, *_args):  # type: ignore[no-untyped-def]
        self.owner.active_sessions -= 1
        row = self.owner.outbox
        self.owner.history.append(
            (
                self.label,
                str(row.status),
                int(row.attempt_count or 0),
                row.attempted_at,
            )
        )
        return False

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        self.statements.append(statement)
        require(bool(self.responses), f"unexpected outbox SQL in {self.label}: {statement}")
        response = self.responses.pop(0)
        rows = response(self.owner) if callable(response) else response
        sql = str(statement.compile(dialect=postgresql.dialect())).upper()
        if (
            self.label == "finalize"
            and "UPDATE USER_EMAIL_ACTION_TOKENS" in sql
            and self.owner.old_token is not None
        ):
            self.owner.old_token.consumed_at = NOW
        return FakeResult(list(rows))

    def add(self, value):  # type: ignore[no-untyped-def]
        self.added.append(value)
        if isinstance(value, UserEmailActionToken):
            self.owner.token = value

    async def flush(self) -> None:
        self.flush_calls += 1
        if self.owner.token is not None and self.owner.token.id is None:
            self.owner.token.id = 901

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1


class ScriptedSessionFactory:
    def __init__(
        self,
        *,
        outbox: AuthEmailOutbox,
        scripts: list[tuple[str, list[Any]]],
        old_token: UserEmailActionToken | None = None,
    ) -> None:
        self.outbox = outbox
        self.scripts = list(scripts)
        self.sessions: list[ScriptedSession] = []
        self.active_sessions = 0
        self.history: list[tuple[str, str, int, datetime | None]] = []
        self.token: UserEmailActionToken | None = None
        self.old_token = old_token

    def __call__(self) -> ScriptedSession:
        if self.scripts:
            label, responses = self.scripts.pop(0)
        else:
            label, responses = "claim-empty", [[]]
        session = ScriptedSession(self, label=label, responses=responses)
        self.sessions.append(session)
        return session


class FakeDelivery:
    def __init__(
        self,
        factory: ScriptedSessionFactory | None = None,
        *,
        error_code: str | None = None,
    ) -> None:
        self.factory = factory
        self.error_code = error_code
        self.calls: list[dict[str, Any]] = []
        self.attempt_snapshots: list[tuple[str, int, datetime | None]] = []
        self.old_token_snapshots: list[datetime | None] = []

    async def send(self, **kwargs):  # type: ignore[no-untyped-def]
        if self.factory is not None:
            require(self.factory.active_sessions == 0, "provider call held an outbox DB session")
            row = self.factory.outbox
            self.attempt_snapshots.append(
                (str(row.status), int(row.attempt_count or 0), row.attempted_at)
            )
            if self.factory.old_token is not None:
                self.old_token_snapshots.append(self.factory.old_token.consumed_at)
        self.calls.append(dict(kwargs))
        if self.error_code is not None:
            raise EmailDeliveryError(self.error_code)
        return EmailDeliveryResult(provider="brevo", message_id="provider-message-1")


def build_service(*, delivery: FakeDelivery | None = None) -> AuthEmailOutboxService:
    return AuthEmailOutboxService(
        current_settings=fake_settings(),  # type: ignore[arg-type]
        email_delivery=delivery or FakeDelivery(),
        token_secret=TOKEN_SECRET,
        abuse_secret=ABUSE_SECRET,
        token_factory=lambda: RAW_TOKEN,
        now_factory=lambda: NOW,
        public_frontend_origin="https://game.example.com",
        provider_ready=True,
    )


class EnqueueSession:
    def __init__(self) -> None:
        self.statements: list[Any] = []
        self.added: list[Any] = []
        self.commit_calls = 0

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        self.statements.append(statement)
        return FakeResult([])

    def add(self, value):  # type: ignore[no-untyped-def]
        self.added.append(value)


async def test_semantic_enqueue_persists_no_message_secrets() -> None:
    service = build_service()
    session = EnqueueSession()
    await service.enqueue(
        session,  # type: ignore[arg-type]
        purpose=EMAIL_PURPOSE_VERIFY,
        canonical_email=RECIPIENT,
        user_id=22,
    )
    require(len(session.added) == 1, "semantic outbox row was not added")
    row = session.added[0]
    require(isinstance(row, AuthEmailOutbox), "enqueue added a non-outbox row")
    require(row.target_digest != RECIPIENT and len(row.target_digest) == 64, "recipient was not HMAC-pseudonymized")
    require(row.user_id == 22 and row.status == "pending" and row.attempt_count == 0, "queued state mismatch")
    require(session.commit_calls == 0, "enqueue committed the caller transaction")

    column_names = set(AuthEmailOutbox.__table__.columns.keys())
    forbidden_columns = {
        "recipient",
        "email",
        "email_canonical",
        "raw_token",
        "token",
        "subject",
        "html",
        "html_content",
        "text",
        "text_content",
        "body",
        "rendered",
    }
    require(not (column_names & forbidden_columns), "outbox schema stores recipient/token/body data")
    persisted_repr = repr(vars(row))
    require(RECIPIENT not in persisted_repr and RAW_TOKEN not in persisted_repr, "outbox ORM row retained private message data")

    lock_compiled = session.statements[0].compile(dialect=postgresql.dialect())
    lock_sql = str(lock_compiled).upper()
    require(
        "PG_ADVISORY_XACT_LOCK" in lock_sql,
        "enqueue omitted its domain-separated PostgreSQL transaction lock",
    )
    update_compiled = session.statements[1].compile(dialect=postgresql.dialect())
    sql_bind_repr = repr(update_compiled.params)
    require(RECIPIENT not in sql_bind_repr and RAW_TOKEN not in sql_bind_repr, "enqueue SQL bind retained private message data")
    require(row.target_digest in sql_bind_repr, "enqueue supersession query omitted target digest")
    require(
        service.digest_target("Owner@Example.COM") == service.digest_target("owner@example.com"),
        "outbox target digest does not canonicalize email case",
    )
    lock_bind_repr = repr(lock_compiled.params)
    require(
        row.target_digest not in lock_bind_repr
        and RECIPIENT not in lock_bind_repr
        and RAW_TOKEN not in lock_bind_repr,
        "enqueue advisory lock exposed target material",
    )
    same_lock = service.build_target_lock_statement(
        purpose=EMAIL_PURPOSE_VERIFY,
        target_digest=row.target_digest,
    ).compile(dialect=postgresql.dialect())
    other_purpose_lock = service.build_target_lock_statement(
        purpose="password_reset",
        target_digest=row.target_digest,
    ).compile(dialect=postgresql.dialect())
    require(lock_compiled.params == same_lock.params, "same target/purpose lock is unstable")
    require(
        lock_compiled.params != other_purpose_lock.params,
        "outbox advisory lock is not purpose-domain-separated",
    )

    indexes = {index.name: index for index in AuthEmailOutbox.__table__.indexes}
    pending_unique = indexes["uq_auth_email_outbox_pending_target_purpose"]
    inflight_unique = indexes["uq_auth_email_outbox_inflight_target_purpose"]
    require(pending_unique.unique is True, "queued-successor partial unique index missing")
    require(inflight_unique.unique is True, "in-flight partial unique index missing")
    require(
        "status = 'pending'"
        in str(pending_unique.dialect_options["postgresql"]["where"]),
        "queued-successor partial predicate differs",
    )
    require(
        "'preparing', 'sending'"
        in str(inflight_unique.dialect_options["postgresql"]["where"]),
        "in-flight delivery partial predicate differs",
    )


class ConcurrentClaimStore:
    def __init__(self, rows: list[AuthEmailOutbox]) -> None:
        self.rows = rows
        self.transaction_lock = asyncio.Lock()
        self.observed_sql: list[str] = []

    def session(self) -> "ConcurrentClaimSession":
        return ConcurrentClaimSession(self)


class ConcurrentClaimSession:
    def __init__(self, store: ConcurrentClaimStore) -> None:
        self.store = store
        self.locked = False

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        await self.store.transaction_lock.acquire()
        self.locked = True
        sql = str(statement.compile(dialect=postgresql.dialect())).upper()
        self.store.observed_sql.append(sql)
        require("FOR UPDATE SKIP LOCKED" in sql, "worker claim lost SKIP LOCKED")
        require("NOT (EXISTS" in sql, "worker claim does not exclude an in-flight peer")
        for row in sorted(self.store.rows, key=lambda item: int(item.id)):
            if row.status != "pending" or row.available_at > NOW:
                continue
            has_inflight = any(
                peer.target_digest == row.target_digest
                and peer.purpose == row.purpose
                and peer.status in {"preparing", "sending"}
                for peer in self.store.rows
            )
            if not has_inflight:
                return FakeResult([row])
        return FakeResult([])

    async def commit(self) -> None:
        self._release()

    async def rollback(self) -> None:
        self._release()

    def _release(self) -> None:
        if self.locked:
            self.locked = False
            self.store.transaction_lock.release()


async def test_two_workers_never_overlap_one_target() -> None:
    service = build_service()
    first = outbox_row(row_id=40)
    store = ConcurrentClaimStore([first])

    first_claims = await asyncio.gather(
        service._claim_next(store.session()),  # noqa: SLF001
        service._claim_next(store.session()),  # noqa: SLF001
    )
    require(
        sorted(first_claims, key=lambda value: value is None) == [40, None],
        f"two workers claimed the same target concurrently: {first_claims}",
    )
    require(first.status == "preparing", "first worker did not retain in-flight ownership")

    successor = outbox_row(row_id=41, target_digest=first.target_digest)
    store.rows.append(successor)
    blocked_claims = await asyncio.gather(
        service._claim_next(store.session()),  # noqa: SLF001
        service._claim_next(store.session()),  # noqa: SLF001
    )
    require(
        blocked_claims == [None, None],
        f"a queued successor overlapped an in-flight delivery: {blocked_claims}",
    )
    require(successor.status == "pending", "blocked successor left queued state")


async def test_successful_claim_prepare_send_finalize() -> None:
    row = outbox_row()
    account = user_row(verified=False)
    old_token = existing_action_token()
    factory = ScriptedSessionFactory(
        outbox=row,
        old_token=old_token,
        scripts=[
            ("claim", [[row]]),
            ("prepare", [[row], [account]]),
            ("finalize", [[row], lambda owner: [owner.token], []]),
        ],
    )
    delivery = FakeDelivery(factory)
    service = build_service(delivery=delivery)

    processed = await service.process_one(factory)  # type: ignore[arg-type]
    require(processed, "pending outbox job was not processed")
    require(
        [(label, status, attempts) for label, status, attempts, _ in factory.history]
        == [
            ("claim", "preparing", 0),
            ("prepare", "sending", 1),
            ("finalize", "sent", 1),
        ],
        f"outbox state transition mismatch: {factory.history}",
    )
    require(delivery.attempt_snapshots == [("sending", 1, NOW)], "provider call did not begin from committed sending state")
    require(delivery.old_token_snapshots == [None], "prepare invalidated the previous valid link before delivery succeeded")
    require(len(delivery.calls) == 1, "provider call count mismatch")
    require(delivery.calls[0]["recipient"] == RECIPIENT, "worker did not resolve current recipient in memory")
    rendered = delivery.calls[0]["rendered"]
    require(RAW_TOKEN in rendered.html_content and RAW_TOKEN in rendered.text_content, "fresh action token was not rendered in memory")

    token = factory.token
    require(token is not None and token.id == 901, "worker did not create a token row during prepare")
    require(token.token_digest != RAW_TOKEN and len(token.token_digest) == 64, "raw token reached PostgreSQL token state")
    require(token.delivery_status == "sent", "token delivery audit was not finalized")
    require(token.consumed_at is None, "successful finalize invalidated the newly delivered link")
    require(old_token.consumed_at == NOW, "successful finalize did not retire the previous valid link")
    require(row.provider_message_id == "provider-message-1" and row.error_code is None, "outbox success audit mismatch")
    require(
        [session.commit_calls for session in factory.sessions[:3]] == [1, 1, 1],
        "claim/prepare/finalize did not commit as three short transactions",
    )

    stage_sql = [
        [str(statement.compile(dialect=postgresql.dialect())).upper() for statement in session.statements]
        for session in factory.sessions[:3]
    ]
    require(
        "FOR UPDATE SKIP LOCKED" in stage_sql[0][0]
        and "ORDER BY AUTH_EMAIL_OUTBOX.ID" in stage_sql[0][0],
        "claim is not an ordered skip-locked row claim",
    )
    require("FOR UPDATE" in stage_sql[1][0] and "FOR UPDATE" in stage_sql[1][1], "prepare did not re-lock outbox and user")
    require("FOR UPDATE" in stage_sql[2][0] and "FOR UPDATE" in stage_sql[2][1], "finalize did not re-lock outbox and token")
    require(
        len(stage_sql[1]) == 2 and not any("UPDATE USER_EMAIL_ACTION_TOKENS" in sql for sql in stage_sql[1]),
        "prepare invalidates existing links before the provider outcome is known",
    )
    require(
        len(stage_sql[2]) == 3
        and "UPDATE USER_EMAIL_ACTION_TOKENS" in stage_sql[2][2]
        and "USER_EMAIL_ACTION_TOKENS.ID !=" in stage_sql[2][2]
        and "USER_EMAIL_ACTION_TOKENS.CONSUMED_AT IS NULL" in stage_sql[2][2],
        "successful finalize does not safely retire only prior unconsumed links",
    )
    retire_params = factory.sessions[2].statements[2].compile(dialect=postgresql.dialect()).params
    require(901 in retire_params.values(), "successful finalize did not exclude the newly delivered token")

    persisted_repr = repr({"outbox": vars(row), "token": vars(token)})
    require(RECIPIENT not in persisted_repr and RAW_TOKEN not in persisted_repr, "final persisted state retained recipient or raw token")
    sql_bind_repr = repr(
        [
            statement.compile(dialect=postgresql.dialect()).params
            for session in factory.sessions
            for statement in session.statements
        ]
    )
    require(RECIPIENT not in sql_bind_repr and RAW_TOKEN not in sql_bind_repr, "prepare/finalize SQL binds retained private message data")


async def test_failed_attempt_is_never_automatically_retried() -> None:
    row = outbox_row(row_id=2)
    account = user_row(verified=False)
    old_token = existing_action_token(token_id=701)
    factory = ScriptedSessionFactory(
        outbox=row,
        old_token=old_token,
        scripts=[
            ("claim", [[row]]),
            ("prepare", [[row], [account]]),
            ("finalize", [[row], lambda owner: [owner.token]]),
        ],
    )
    delivery = FakeDelivery(factory, error_code="brevo_network_error")
    service = build_service(delivery=delivery)

    first = await service.process_one(factory)  # type: ignore[arg-type]
    second = await service.process_one(factory)  # type: ignore[arg-type]
    require(first is True and second is False, "failed provider attempt was scheduled again")
    require(len(delivery.calls) == 1, "ambiguous/failed provider call was retried")
    require(row.status == "failed" and row.attempt_count == 1, "failed outbox terminal state mismatch")
    require(row.error_code == "brevo_network_error", "safe provider failure code was not recorded")
    require(factory.token is not None and factory.token.delivery_status == "failed", "token failure audit mismatch")
    require(old_token.consumed_at is None, "failed provider attempt invalidated the previous valid link")
    require(
        not any(
            "UPDATE USER_EMAIL_ACTION_TOKENS"
            in str(statement.compile(dialect=postgresql.dialect())).upper()
            for session in factory.sessions
            for statement in session.statements
        ),
        "failed provider attempt retired an existing valid link",
    )
    require(
        [(label, status) for label, status, _attempts, _attempted_at in factory.history[:3]]
        == [("claim", "preparing"), ("prepare", "sending"), ("finalize", "failed")],
        "failed attempt skipped a required state",
    )


async def test_decoy_is_suppressed_without_provider_or_token() -> None:
    row = outbox_row(row_id=3, user_id=None)
    factory = ScriptedSessionFactory(
        outbox=row,
        scripts=[
            ("claim", [[row]]),
            ("prepare", [[row]]),
        ],
    )
    delivery = FakeDelivery(factory)
    service = build_service(delivery=delivery)

    processed = await service.process_one(factory)  # type: ignore[arg-type]
    require(processed, "decoy work was not consumed")
    require(row.status == "suppressed" and row.error_code == "recipient_not_eligible", "decoy suppression state mismatch")
    require(row.attempt_count == 0 and row.attempted_at is None, "decoy was marked as a provider attempt")
    require(factory.token is None, "decoy created an action token")
    require(not delivery.calls, "decoy reached the provider")
    require(
        [(label, status) for label, status, _attempts, _attempted_at in factory.history]
        == [("claim", "preparing"), ("prepare", "suppressed")],
        "decoy did not follow claim-to-suppressed state",
    )


class MaintenanceSession:
    def __init__(self, rows: list[AuthEmailOutbox]) -> None:
        self.rows = rows
        self.statements: list[Any] = []
        self.commit_calls = 0

    async def execute(self, statement):  # type: ignore[no-untyped-def]
        self.statements.append(statement)
        compiled = statement.compile(dialect=postgresql.dialect())
        sql = str(compiled).upper()
        params = compiled.params
        if sql.startswith("SELECT DISTINCT AUTH_EMAIL_OUTBOX.PURPOSE"):
            targets = sorted(
                {
                    (row.purpose, row.target_digest)
                    for row in self.rows
                    if (
                        row.status == "preparing"
                        and row.claimed_at is not None
                        and row.claimed_at < NOW - timedelta(seconds=300)
                    )
                    or (
                        row.status == "sending"
                        and row.attempted_at is not None
                        and row.attempted_at < NOW - timedelta(seconds=120)
                    )
                }
            )
            return FakeResult(list(targets))
        if "PG_ADVISORY_XACT_LOCK" in sql:
            return FakeResult([])
        if (
            sql.startswith("UPDATE AUTH_EMAIL_OUTBOX")
            and "EXISTS" in sql
            and "NOT (EXISTS" not in sql
        ):
            cutoff = NOW - timedelta(seconds=300)
            for row in self.rows:
                if (
                    row.status == "preparing"
                    and int(row.attempt_count or 0) == 0
                    and row.claimed_at is not None
                    and row.claimed_at < cutoff
                    and any(
                        peer is not row
                        and peer.purpose == row.purpose
                        and peer.target_digest == row.target_digest
                        and peer.status == "pending"
                        for peer in self.rows
                    )
                ):
                    row.status = "suppressed"
                    row.completed_at = NOW
                    row.error_code = "superseded_after_abandoned_claim"
            return FakeResult([])
        if (
            sql.startswith("UPDATE AUTH_EMAIL_OUTBOX")
            and "NOT (EXISTS" in sql
            and "pending" in params.values()
        ):
            cutoff = NOW - timedelta(seconds=300)
            for row in self.rows:
                if (
                    row.status == "preparing"
                    and int(row.attempt_count or 0) == 0
                    and row.claimed_at is not None
                    and row.claimed_at < cutoff
                    and not any(
                        peer is not row
                        and peer.purpose == row.purpose
                        and peer.target_digest == row.target_digest
                        and peer.status == "pending"
                        for peer in self.rows
                    )
                ):
                    row.status = "pending"
                    row.claimed_at = None
                    row.error_code = None
                    row.available_at = NOW
            return FakeResult([])
        if (
            sql.startswith("UPDATE AUTH_EMAIL_OUTBOX")
            and "sending" in params.values()
            and "failed" in params.values()
        ):
            cutoff = NOW - timedelta(seconds=120)
            for row in self.rows:
                if (
                    row.status == "sending"
                    and int(row.attempt_count or 0) == 1
                    and row.attempted_at is not None
                    and row.attempted_at < cutoff
                ):
                    row.status = "failed"
                    row.completed_at = NOW
                    row.error_code = "delivery_outcome_unknown"
        return FakeResult([])

    async def commit(self) -> None:
        self.commit_calls += 1


async def test_abandoned_state_maintenance() -> None:
    preparing = outbox_row(row_id=4)
    preparing.status = "preparing"
    preparing.claimed_at = NOW - timedelta(seconds=301)

    successor = outbox_row(row_id=5)

    recoverable = outbox_row(row_id=6, target_digest="f" * 64)
    recoverable.status = "preparing"
    recoverable.claimed_at = NOW - timedelta(seconds=301)

    sending = outbox_row(row_id=7, target_digest="e" * 64)
    sending.status = "sending"
    sending.claimed_at = NOW - timedelta(seconds=130)
    sending.attempted_at = NOW - timedelta(seconds=121)
    sending.attempt_count = 1
    old_token = existing_action_token(token_id=702)
    sending.action_token_id = old_token.id

    sending_successor = outbox_row(row_id=8, target_digest="e" * 64)

    delivery = FakeDelivery()
    service = build_service(delivery=delivery)
    session = MaintenanceSession(
        [preparing, successor, recoverable, sending, sending_successor]
    )
    await service.maintain(session)  # type: ignore[arg-type]

    require(
        preparing.status == "suppressed"
        and preparing.error_code == "superseded_after_abandoned_claim",
        "abandoned claim was not suppressed in favor of its queued successor",
    )
    require(successor.status == "pending", "queued successor was not preserved")
    require(
        recoverable.status == "pending" and recoverable.claimed_at is None,
        "abandoned preparing job without a successor was not recovered",
    )
    require(
        recoverable.attempt_count == 0 and recoverable.error_code is None,
        "pre-provider recovery changed attempt state",
    )
    require(sending.status == "failed" and sending.attempt_count == 1, "unknown sending outcome was made retryable")
    require(sending.error_code == "delivery_outcome_unknown" and sending.completed_at == NOW, "unknown sending audit mismatch")
    require(
        sending_successor.status == "pending",
        "stale sending cleanup changed its queued successor",
    )
    require(old_token.consumed_at is None, "unknown provider outcome invalidated the previous valid link")
    require(not delivery.calls, "maintenance called the email provider")
    require(
        session.commit_calls == 1 and len(session.statements) == 9,
        "maintenance transaction/target-lock contract mismatch",
    )

    compiled = [statement.compile(dialect=postgresql.dialect()) for statement in session.statements]
    sql = [str(item).upper() for item in compiled]
    params = [item.params for item in compiled]
    require(
        all("PG_ADVISORY_XACT_LOCK" in item for item in sql[1:4]),
        "maintenance did not serialize each stale pseudonymous target",
    )
    require("UPDATE AUTH_EMAIL_OUTBOX" in sql[4] and "EXISTS" in sql[4], "successor-aware suppression predicate missing")
    require("UPDATE AUTH_EMAIL_OUTBOX" in sql[5] and "NOT (EXISTS" in sql[5], "preparing recovery predicate missing")
    require("UPDATE AUTH_EMAIL_OUTBOX" in sql[6] and "ATTEMPTED_AT <" in sql[6], "sending timeout predicate missing")
    require("DELETE FROM AUTH_EMAIL_OUTBOX" in sql[7], "terminal retention cleanup missing")
    require("DELETE FROM AUTH_RATE_LIMIT_BUCKETS" in sql[8], "rate bucket retention cleanup missing")
    require("preparing" in params[5].values() and "pending" in params[5].values() and 0 in params[5].values(), "preparing recovery values changed")
    require("sending" in params[6].values() and "failed" in params[6].values() and 1 in params[6].values(), "unknown sending transition values changed")
    require("delivery_outcome_unknown" in params[6].values(), "unknown outcome error code missing")

    post_failure_store = ConcurrentClaimStore([sending, sending_successor])
    claimed_after_failure = await service._claim_next(  # noqa: SLF001
        post_failure_store.session()
    )
    require(
        claimed_after_failure == 8 and sending_successor.status == "preparing",
        "queued successor was not claimable after stale sending became terminal",
    )


async def main_async() -> None:
    await test_semantic_enqueue_persists_no_message_secrets()
    await test_two_workers_never_overlap_one_target()
    await test_successful_claim_prepare_send_finalize()
    await test_failed_attempt_is_never_automatically_retried()
    await test_decoy_is_suppressed_without_provider_or_token()
    await test_abandoned_state_maintenance()


def main() -> None:
    asyncio.run(main_async())
    print("OK: v377 semantic auth email outbox smoke passed")


if __name__ == "__main__":
    main()
