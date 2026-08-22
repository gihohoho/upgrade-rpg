from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class AuthEmailOutbox(Base, IdMixin, TimestampMixin):
    """Durable semantic email request with no recipient or raw action token.

    The worker resolves the current user email and creates a fresh one-time token
    only after it has exclusively claimed this row.  A crash can therefore never
    leave a reusable raw token or rendered email body in PostgreSQL.
    """

    __tablename__ = "auth_email_outbox"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('verify_email', 'username_recovery', "
            "'password_reset', 'account_deletion')",
            name="ck_auth_email_outbox_purpose",
        ),
        CheckConstraint(
            "status IN ('pending', 'preparing', 'sending', 'sent', 'failed', 'suppressed')",
            name="ck_auth_email_outbox_status",
        ),
        CheckConstraint(
            "attempt_count >= 0 AND attempt_count <= 1",
            name="ck_auth_email_outbox_single_attempt",
        ),
        CheckConstraint(
            "char_length(target_digest) = 64",
            name="ck_auth_email_outbox_target_digest_length",
        ),
        CheckConstraint(
            "(status = 'pending' AND attempt_count = 0 AND claimed_at IS NULL "
            "AND attempted_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'preparing' AND attempt_count = 0 AND claimed_at IS NOT NULL "
            "AND attempted_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'sending' AND attempt_count = 1 AND claimed_at IS NOT NULL "
            "AND attempted_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status = 'sent' AND attempt_count = 1 AND attempted_at IS NOT NULL "
            "AND completed_at IS NOT NULL AND provider_message_id IS NOT NULL "
            "AND error_code IS NULL) OR "
            "(status = 'failed' AND attempt_count = 1 AND attempted_at IS NOT NULL "
            "AND completed_at IS NOT NULL AND error_code IS NOT NULL) OR "
            "(status = 'suppressed' AND attempt_count = 0 AND attempted_at IS NULL "
            "AND completed_at IS NOT NULL AND error_code IS NOT NULL)",
            name="ck_auth_email_outbox_state_shape",
        ),
        Index(
            "ix_auth_email_outbox_pending",
            "status",
            "available_at",
            "id",
        ),
        Index(
            "ix_auth_email_outbox_user_purpose",
            "user_id",
            "purpose",
            "created_at",
        ),
        Index(
            "ix_auth_email_outbox_target_purpose",
            "target_digest",
            "purpose",
            "created_at",
        ),
        Index(
            "uq_auth_email_outbox_pending_target_purpose",
            "target_digest",
            "purpose",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
        Index(
            "uq_auth_email_outbox_inflight_target_purpose",
            "target_digest",
            "purpose",
            unique=True,
            postgresql_where=text("status IN ('preparing', 'sending')"),
        ),
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    purpose: Mapped[str] = mapped_column(String(40), nullable=False)
    target_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default="pending"
    )
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    action_token_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_email_action_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    provider_message_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
