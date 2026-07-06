from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class AdminRole(Base, IdMixin, TimestampMixin):
    __tablename__ = "admin_roles"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    permissions_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AdminUserRole(Base, IdMixin, TimestampMixin):
    __tablename__ = "admin_user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_code: Mapped[str] = mapped_column(ForeignKey("admin_roles.code", ondelete="CASCADE"))


class AdminChangeLog(Base, IdMixin, TimestampMixin):
    __tablename__ = "admin_change_logs"

    admin_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    target_type: Mapped[str] = mapped_column(String(80), index=True)
    target_id: Mapped[str] = mapped_column(String(160), index=True)
    action: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    before_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    after_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    rollback_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    applied: Mapped[bool] = mapped_column(Boolean, default=True)
