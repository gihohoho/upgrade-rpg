"""Durable online gameplay and committed command receipts."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class GameSession(Base, IdMixin, TimestampMixin):
    __tablename__ = "game_sessions"

    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("user_save_snapshots.id", ondelete="CASCADE"), unique=True
    )
    session_key: Mapped[str] = mapped_column(String(64), unique=True)
    auth_version: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    connection_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lease_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    settled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revision: Mapped[int] = mapped_column(BigInteger, default=0)
    rng_seed: Mapped[str] = mapped_column(String(64))
    rng_cursor: Mapped[int] = mapped_column(BigInteger, default=0)
    runtime_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class GameActionReceipt(Base, IdMixin, TimestampMixin):
    __tablename__ = "game_action_receipts"
    __table_args__ = (UniqueConstraint("snapshot_id", "request_id", name="uq_game_action_request"),)

    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("user_save_snapshots.id", ondelete="CASCADE"), index=True
    )
    request_id: Mapped[str] = mapped_column(String(64))
    request_hash: Mapped[str] = mapped_column(String(64))
    session_key: Mapped[str] = mapped_column(String(64))
    result_json: Mapped[dict] = mapped_column(JSONB)
