from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import logging
import secrets
from typing import Any, Callable

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import aliased

from app.core.config import (
    LOCAL_AUTH_ABUSE_SECRET,
    LOCAL_EMAIL_TOKEN_SECRET,
    Settings,
    settings,
)
from app.models import (
    AdminChangeLog,
    AuthEmailOutbox,
    AuthRateLimitBucket,
    User,
    UserEmailActionToken,
)
from app.services.auth_email_delivery import (
    BrevoEmailDelivery,
    EmailDeliveryError,
    RenderedAuthEmail,
    build_auth_action_url,
    render_account_deletion,
    render_email_verification,
    render_password_reset,
    render_username_recovery,
)


logger = logging.getLogger(__name__)

EMAIL_PURPOSE_VERIFY = "verify_email"
EMAIL_PURPOSE_USERNAME_RECOVERY = "username_recovery"
EMAIL_PURPOSE_PASSWORD_RESET = "password_reset"
EMAIL_PURPOSE_ACCOUNT_DELETION = "account_deletion"
EMAIL_OUTBOX_PURPOSES = frozenset(
    {
        EMAIL_PURPOSE_VERIFY,
        EMAIL_PURPOSE_USERNAME_RECOVERY,
        EMAIL_PURPOSE_PASSWORD_RESET,
        EMAIL_PURPOSE_ACCOUNT_DELETION,
    }
)
EMAIL_TOKEN_PURPOSES = frozenset(
    {
        EMAIL_PURPOSE_VERIFY,
        EMAIL_PURPOSE_PASSWORD_RESET,
        EMAIL_PURPOSE_ACCOUNT_DELETION,
    }
)
EMAIL_OUTBOX_INFLIGHT_STATUSES = ("preparing", "sending")
EMAIL_OUTBOX_LOCK_DOMAIN = "auth-email-outbox-delivery:v1"


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


@dataclass(frozen=True)
class PreparedOutboxEmail:
    outbox_id: int
    action_token_id: int | None
    recipient: str
    rendered: RenderedAuthEmail


class AuthEmailOutboxService:
    """Persist semantic mail work and execute one non-retried provider attempt.

    PostgreSQL never stores a recipient, rendered body, or raw action token in
    this queue.  Token generation happens after a row is claimed and the digest
    transaction commits before the provider call.  A row in ``sending`` is never
    automatically retried because a timeout or process exit can be ambiguous.
    """

    def __init__(
        self,
        *,
        current_settings: Settings | None = None,
        email_delivery: Any | None = None,
        token_secret: str | None = None,
        abuse_secret: str | None = None,
        token_factory: Callable[[], str] | None = None,
        now_factory: Callable[[], datetime] | None = None,
        public_frontend_origin: str | None = None,
        provider_ready: bool | None = None,
    ) -> None:
        self.settings = current_settings or settings
        self.email_delivery = email_delivery or BrevoEmailDelivery(
            current_settings=self.settings
        )
        self.token_secret = (
            str(token_secret).strip()
            if token_secret is not None
            else self.settings.email_token_secret.get_secret_value().strip()
        )
        self.abuse_secret = (
            str(abuse_secret).strip()
            if abuse_secret is not None
            else self.settings.auth_abuse_secret.get_secret_value().strip()
        )
        self.token_factory = token_factory or (lambda: secrets.token_urlsafe(32))
        self.now_factory = now_factory or (lambda: datetime.now(UTC))
        self.public_frontend_origin = str(
            public_frontend_origin or self.settings.public_frontend_origin
        ).rstrip("/")
        self.provider_ready = (
            self.settings.brevo_ready if provider_ready is None else bool(provider_ready)
        )

    def require_ready(self) -> None:
        self._require_token_secret()
        self._require_abuse_secret()
        if not self.provider_ready:
            raise RuntimeError("email_delivery_unavailable")

    async def enqueue(
        self,
        session: AsyncSession,
        *,
        purpose: str,
        canonical_email: str,
        user_id: int | None,
    ) -> None:
        """Add one durable request without committing the caller's transaction."""
        self.require_ready()
        if purpose not in EMAIL_OUTBOX_PURPOSES:
            raise ValueError("unsupported_email_outbox_purpose")
        target_digest = self.digest_target(canonical_email)
        now = self._now()
        # The advisory transaction lock closes the update-then-insert race
        # between concurrent requests.  It contains only a purpose and an HMAC
        # digest; the partial unique index remains the final database invariant.
        await session.execute(
            self.build_target_lock_statement(
                purpose=purpose,
                target_digest=target_digest,
            )
        )
        await session.execute(
            update(AuthEmailOutbox)
            .where(
                AuthEmailOutbox.purpose == purpose,
                AuthEmailOutbox.target_digest == target_digest,
                AuthEmailOutbox.status == "pending",
            )
            .values(
                status="suppressed",
                completed_at=now,
                error_code="superseded",
            )
        )
        session.add(
            AuthEmailOutbox(
                user_id=int(user_id) if user_id is not None else None,
                purpose=purpose,
                target_digest=target_digest,
                status="pending",
                available_at=now,
                attempt_count=0,
            )
        )

    async def process_one(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> bool:
        """Process at most one job and never retry an attempted provider call."""
        async with session_factory() as session:
            outbox_id = await self._claim_next(session)
        if outbox_id is None:
            return False

        async with session_factory() as session:
            prepared = await self._prepare_claimed(session, outbox_id=outbox_id)
        if prepared is None:
            return True

        error_code: str | None = None
        result = None
        try:
            result = await self.email_delivery.send(
                recipient=prepared.recipient,
                rendered=prepared.rendered,
            )
        except EmailDeliveryError as exc:
            error_code = exc.code
        except Exception:
            error_code = "email_delivery_unexpected"

        async with session_factory() as session:
            await self._finalize_attempt(
                session,
                prepared=prepared,
                provider_message_id=(str(result.message_id) if result is not None else None),
                error_code=error_code,
            )
        return True

    async def maintain(self, session: AsyncSession) -> None:
        """Recover pre-provider claims and close ambiguous attempted work."""
        now = self._now()
        preparing_cutoff = now - timedelta(
            seconds=int(self.settings.email_outbox_preparing_timeout_seconds)
        )
        sending_cutoff = now - timedelta(
            seconds=int(self.settings.email_outbox_sending_timeout_seconds)
        )
        retention_cutoff = now - timedelta(days=int(self.settings.email_outbox_retention_days))
        rate_limit_cutoff = now - timedelta(
            days=int(self.settings.auth_rate_limit_retention_days)
        )
        stale_target_rows = (
            await session.execute(
                select(AuthEmailOutbox.purpose, AuthEmailOutbox.target_digest)
                .where(
                    or_(
                        and_(
                            AuthEmailOutbox.status == "preparing",
                            AuthEmailOutbox.attempt_count == 0,
                            AuthEmailOutbox.claimed_at < preparing_cutoff,
                        ),
                        and_(
                            AuthEmailOutbox.status == "sending",
                            AuthEmailOutbox.attempt_count == 1,
                            AuthEmailOutbox.attempted_at < sending_cutoff,
                        ),
                    )
                )
                .distinct()
                .order_by(AuthEmailOutbox.purpose, AuthEmailOutbox.target_digest)
            )
        ).all()
        # Acquire locks in one deterministic order so maintenance and enqueue
        # cannot race a recovered claim into a second queued successor.
        for purpose, target_digest in stale_target_rows:
            await session.execute(
                self.build_target_lock_statement(
                    purpose=str(purpose),
                    target_digest=str(target_digest),
                )
            )

        pending_successor = aliased(AuthEmailOutbox)
        has_pending_successor = (
            select(pending_successor.id)
            .where(
                pending_successor.purpose == AuthEmailOutbox.purpose,
                pending_successor.target_digest == AuthEmailOutbox.target_digest,
                pending_successor.status == "pending",
            )
            .exists()
        )
        await session.execute(
            update(AuthEmailOutbox)
            .where(
                AuthEmailOutbox.status == "preparing",
                AuthEmailOutbox.attempt_count == 0,
                AuthEmailOutbox.claimed_at < preparing_cutoff,
                has_pending_successor,
            )
            .values(
                status="suppressed",
                completed_at=now,
                error_code="superseded_after_abandoned_claim",
            )
            .execution_options(synchronize_session=False)
        )
        await session.execute(
            update(AuthEmailOutbox)
            .where(
                AuthEmailOutbox.status == "preparing",
                AuthEmailOutbox.attempt_count == 0,
                AuthEmailOutbox.claimed_at < preparing_cutoff,
                ~has_pending_successor,
            )
            .values(
                status="pending",
                claimed_at=None,
                error_code=None,
                available_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        await session.execute(
            update(AuthEmailOutbox)
            .where(
                AuthEmailOutbox.status == "sending",
                AuthEmailOutbox.attempt_count == 1,
                AuthEmailOutbox.attempted_at < sending_cutoff,
            )
            .values(
                status="failed",
                completed_at=now,
                error_code="delivery_outcome_unknown",
            )
        )
        await session.execute(
            delete(AuthEmailOutbox).where(
                AuthEmailOutbox.status.in_(("sent", "failed", "suppressed")),
                AuthEmailOutbox.completed_at < retention_cutoff,
            )
        )
        await session.execute(
            delete(AuthRateLimitBucket).where(
                AuthRateLimitBucket.updated_at < rate_limit_cutoff
            )
        )
        await session.commit()

    async def _claim_next(self, session: AsyncSession) -> int | None:
        now = self._now()
        inflight = aliased(AuthEmailOutbox)
        has_inflight_delivery = (
            select(inflight.id)
            .where(
                inflight.target_digest == AuthEmailOutbox.target_digest,
                inflight.purpose == AuthEmailOutbox.purpose,
                inflight.status.in_(EMAIL_OUTBOX_INFLIGHT_STATUSES),
            )
            .exists()
        )
        row = (
            await session.execute(
                select(AuthEmailOutbox)
                .where(
                    AuthEmailOutbox.status == "pending",
                    AuthEmailOutbox.available_at <= now,
                    ~has_inflight_delivery,
                )
                .order_by(AuthEmailOutbox.id)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
        ).scalar_one_or_none()
        if row is None:
            await session.rollback()
            return None
        row.status = "preparing"
        row.claimed_at = now
        row.error_code = None
        await session.commit()
        return int(row.id)

    def build_target_lock_statement(
        self,
        *,
        purpose: str,
        target_digest: str,
    ) -> Any:
        """Build the PostgreSQL transaction lock for one pseudonymous mail target."""
        normalized_purpose = str(purpose)
        normalized_digest = str(target_digest)
        if normalized_purpose not in EMAIL_OUTBOX_PURPOSES:
            raise ValueError("unsupported_email_outbox_purpose")
        if len(normalized_digest) != 64 or any(
            character not in "0123456789abcdef" for character in normalized_digest
        ):
            raise ValueError("invalid_email_outbox_target_digest")
        lock_subject = (
            f"{EMAIL_OUTBOX_LOCK_DOMAIN}\0{normalized_purpose}\0{normalized_digest}"
        )
        lock_key = int.from_bytes(
            hashlib.sha256(lock_subject.encode("ascii")).digest()[:8],
            byteorder="big",
            signed=True,
        )
        return select(func.pg_advisory_xact_lock(lock_key))

    async def _prepare_claimed(
        self,
        session: AsyncSession,
        *,
        outbox_id: int,
    ) -> PreparedOutboxEmail | None:
        row = (
            await session.execute(
                select(AuthEmailOutbox)
                .where(AuthEmailOutbox.id == int(outbox_id))
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if row is None or row.status != "preparing" or int(row.attempt_count or 0) != 0:
            await session.rollback()
            return None

        user = None
        if row.user_id is not None:
            user = (
                await session.execute(
                    select(User)
                    .where(User.id == int(row.user_id))
                    .execution_options(populate_existing=True)
                    .with_for_update()
                )
            ).scalar_one_or_none()
        if user is None or not await self._eligible(session, user=user, purpose=row.purpose):
            row.status = "suppressed"
            row.completed_at = self._now()
            row.error_code = "recipient_not_eligible"
            await session.commit()
            return None

        recipient = str(user.email_canonical or "").strip()
        username = str(user.username)
        action_token_id: int | None = None
        raw_token: str | None = None
        if row.purpose in EMAIL_TOKEN_PURPOSES:
            now = self._now()
            raw_token, token_row = self.new_token_row(
                user_id=int(user.id),
                purpose=row.purpose,
                now=now,
            )
            session.add(token_row)
            await session.flush()
            action_token_id = int(token_row.id)
            row.action_token_id = action_token_id

        rendered = self._render(
            purpose=row.purpose,
            username=username,
            raw_token=raw_token,
        )
        row.status = "sending"
        row.attempt_count = 1
        row.attempted_at = self._now()
        row.error_code = None
        await session.commit()
        return PreparedOutboxEmail(
            outbox_id=int(row.id),
            action_token_id=action_token_id,
            recipient=recipient,
            rendered=rendered,
        )

    async def _eligible(
        self,
        session: AsyncSession,
        *,
        user: User,
        purpose: str,
    ) -> bool:
        has_identity = bool(
            user.is_active
            and user.password_hash
            and user.email_canonical
        )
        if not has_identity:
            return False
        if purpose == EMAIL_PURPOSE_VERIFY:
            return user.email_verified_at is None
        if purpose in {EMAIL_PURPOSE_USERNAME_RECOVERY, EMAIL_PURPOSE_PASSWORD_RESET}:
            return user.email_verified_at is not None
        if purpose != EMAIL_PURPOSE_ACCOUNT_DELETION or user.email_verified_at is None:
            return False
        if user.is_admin:
            return False
        audit_id = (
            await session.execute(
                select(AdminChangeLog.id)
                .where(
                    (AdminChangeLog.admin_user_id == int(user.id))
                    | (
                        (AdminChangeLog.target_type == "user")
                        & (AdminChangeLog.target_id == str(int(user.id)))
                    )
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        return audit_id is None

    async def _finalize_attempt(
        self,
        session: AsyncSession,
        *,
        prepared: PreparedOutboxEmail,
        provider_message_id: str | None,
        error_code: str | None,
    ) -> None:
        row = (
            await session.execute(
                select(AuthEmailOutbox)
                .where(AuthEmailOutbox.id == prepared.outbox_id)
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if row is None or row.status != "sending" or int(row.attempt_count or 0) != 1:
            await session.rollback()
            return
        token_row = None
        if prepared.action_token_id is not None:
            token_row = (
                await session.execute(
                    select(UserEmailActionToken)
                    .where(UserEmailActionToken.id == prepared.action_token_id)
                    .execution_options(populate_existing=True)
                    .with_for_update()
                )
            ).scalar_one_or_none()

        completed_at = self._now()
        safe_message_id = str(provider_message_id or "").strip()[:160]
        if error_code is None and safe_message_id:
            row.status = "sent"
            row.provider_message_id = safe_message_id
            row.error_code = None
            if token_row is not None:
                await session.execute(
                    update(UserEmailActionToken)
                    .where(
                        UserEmailActionToken.user_id == int(token_row.user_id),
                        UserEmailActionToken.purpose == row.purpose,
                        UserEmailActionToken.id != int(token_row.id),
                        UserEmailActionToken.consumed_at.is_(None),
                    )
                    .values(consumed_at=completed_at)
                )
                token_row.delivery_status = "sent"
                token_row.delivery_attempted_at = row.attempted_at
                token_row.delivered_at = completed_at
                token_row.provider_message_id = safe_message_id
                token_row.delivery_error_code = None
        else:
            safe_error = str(error_code or "email_delivery_failed")[:80]
            row.status = "failed"
            row.provider_message_id = None
            row.error_code = safe_error
            if token_row is not None:
                token_row.delivery_status = "failed"
                token_row.delivery_attempted_at = row.attempted_at
                token_row.delivered_at = None
                token_row.provider_message_id = None
                token_row.delivery_error_code = safe_error
        row.completed_at = completed_at
        await session.commit()

    def new_token_row(
        self,
        *,
        user_id: int,
        purpose: str,
        now: datetime | None = None,
    ) -> tuple[str, UserEmailActionToken]:
        self._require_token_secret()
        if purpose not in EMAIL_TOKEN_PURPOSES:
            raise ValueError("unsupported_email_token_purpose")
        raw_token = str(self.token_factory()).strip()
        if (
            len(raw_token) < 32
            or len(raw_token) > 256
            or not raw_token.isascii()
            or any(not (character.isalnum() or character in "_-") for character in raw_token)
        ):
            raise RuntimeError("unsafe_email_token_factory_output")
        issued_at = _as_utc(now or self._now())
        expiry_minutes = {
            EMAIL_PURPOSE_VERIFY: int(self.settings.email_verification_expire_minutes),
            EMAIL_PURPOSE_PASSWORD_RESET: int(self.settings.password_reset_expire_minutes),
            EMAIL_PURPOSE_ACCOUNT_DELETION: int(self.settings.account_deletion_expire_minutes),
        }[purpose]
        return raw_token, UserEmailActionToken(
            user_id=int(user_id),
            purpose=purpose,
            token_digest=self.digest_email_token(raw_token),
            expires_at=issued_at + timedelta(minutes=max(5, expiry_minutes)),
            delivery_status="pending",
        )

    def digest_email_token(self, raw_token: str) -> str:
        self._require_token_secret()
        return hmac.new(
            self.token_secret.encode("utf-8"),
            str(raw_token).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def digest_target(self, canonical_email: str) -> str:
        self._require_abuse_secret()
        normalized = str(canonical_email or "").strip().casefold()
        if not normalized:
            raise ValueError("empty_email_outbox_target")
        return hmac.new(
            self.abuse_secret.encode("utf-8"),
            f"auth-email-outbox\0{normalized}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _render(
        self,
        *,
        purpose: str,
        username: str,
        raw_token: str | None,
    ) -> RenderedAuthEmail:
        if purpose == EMAIL_PURPOSE_USERNAME_RECOVERY:
            return render_username_recovery(username=username)
        if raw_token is None:
            raise RuntimeError("email_action_token_missing")
        actions = {
            EMAIL_PURPOSE_VERIFY: ("verify-email", render_email_verification),
            EMAIL_PURPOSE_PASSWORD_RESET: ("reset-password", render_password_reset),
            EMAIL_PURPOSE_ACCOUNT_DELETION: ("delete-account", render_account_deletion),
        }
        action, renderer = actions[purpose]
        action_url = build_auth_action_url(
            action,
            raw_token,
            origin=self.public_frontend_origin,
        )
        return renderer(username=username, action_url=action_url)

    def _require_token_secret(self) -> None:
        if (
            len(self.token_secret) < 32
            or hmac.compare_digest(self.token_secret, LOCAL_EMAIL_TOKEN_SECRET)
            or hmac.compare_digest(self.token_secret, self.settings.jwt_secret_key.strip())
        ):
            raise RuntimeError("email_token_secret_unavailable")

    def _require_abuse_secret(self) -> None:
        if (
            len(self.abuse_secret) < 32
            or hmac.compare_digest(self.abuse_secret, LOCAL_AUTH_ABUSE_SECRET)
            or hmac.compare_digest(self.abuse_secret, self.settings.jwt_secret_key.strip())
            or hmac.compare_digest(self.abuse_secret, self.token_secret)
        ):
            raise RuntimeError("auth_abuse_secret_unavailable")

    def _now(self) -> datetime:
        return _as_utc(self.now_factory())


async def run_auth_email_outbox_worker(
    *,
    stop_event: asyncio.Event,
    session_factory: async_sessionmaker[AsyncSession],
    service: AuthEmailOutboxService | None = None,
) -> None:
    """Run the durable single-attempt queue inside the one-worker web service."""
    worker = service or AuthEmailOutboxService()
    poll_seconds = float(worker.settings.email_outbox_poll_seconds)
    maintenance_interval = float(worker.settings.email_outbox_maintenance_interval_seconds)
    last_maintenance = 0.0
    loop = asyncio.get_running_loop()
    while not stop_event.is_set():
        try:
            now_monotonic = loop.time()
            if now_monotonic - last_maintenance >= maintenance_interval:
                async with session_factory() as session:
                    await worker.maintain(session)
                last_maintenance = now_monotonic
            processed = await worker.process_one(session_factory)
            if processed:
                continue
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "auth email outbox iteration failed (%s); no provider retry was scheduled",
                type(exc).__name__,
            )
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=poll_seconds)
        except TimeoutError:
            pass
