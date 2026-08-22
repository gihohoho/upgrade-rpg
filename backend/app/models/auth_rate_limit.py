from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class AuthRateLimitBucket(Base, TimestampMixin):
    """Persistent abuse-control state keyed only by an HMAC subject digest.

    ``scope`` is a source-controlled policy name such as ``login:ip``. The
    subject column never stores an IP address, email, username, bearer token, or
    action token. Callers must construct it through ``AuthRateLimiter``.
    """

    __tablename__ = "auth_rate_limit_buckets"
    __table_args__ = (
        CheckConstraint(
            "char_length(subject_digest) = 64",
            name="ck_auth_rate_limit_buckets_digest_length",
        ),
        CheckConstraint(
            "request_count >= 0",
            name="ck_auth_rate_limit_buckets_request_count",
        ),
        CheckConstraint(
            "failure_count >= 0",
            name="ck_auth_rate_limit_buckets_failure_count",
        ),
        Index("ix_auth_rate_limit_buckets_updated_at", "updated_at"),
        Index("ix_auth_rate_limit_buckets_blocked_until", "blocked_until"),
    )

    scope: Mapped[str] = mapped_column(String(80), primary_key=True)
    subject_digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    request_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    failure_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
