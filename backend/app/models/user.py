from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class UserProfile(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    gold: Mapped[float] = mapped_column(Numeric(40, 0), default=0)
    farm_atk_bonus: Mapped[float] = mapped_column(default=0)
    add_attack_speed: Mapped[float] = mapped_column(default=0)
    current_character_id: Mapped[str] = mapped_column(String(80), default="weapon_master")
    current_zone_index: Mapped[int] = mapped_column(Integer, default=0)
    current_zone_type: Mapped[str] = mapped_column(String(30), default="field")
    flags_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    records_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped[User] = relationship(back_populates="profile")



class UserSaveSnapshot(Base, IdMixin, TimestampMixin):
    """Raw localStorage save snapshot kept during the backend migration.

    This table is intentionally snapshot-based first. The next migration stages can
    split inventory, equipment, skills, mailbox, and records into normalized tables
    after the browser/localStorage bridge is proven safe.
    """

    __tablename__ = "user_save_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "slot_key", name="uq_user_save_snapshot_slot"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    slot_key: Mapped[str] = mapped_column(String(80), default="default")
    client_save_key: Mapped[str] = mapped_column(String(120), default="idleRpgSaveV22")
    save_version: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    summary_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    source: Mapped[str] = mapped_column(String(80), default="localStorage")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
