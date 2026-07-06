from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Boss(Base, IdMixin, TimestampMixin):
    __tablename__ = "bosses"

    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    boss_type: Mapped[str] = mapped_column(String(30), default="normal")
    hp: Mapped[float] = mapped_column(Numeric(40, 0), default=1)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    summon_rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class DropTable(Base, IdMixin, TimestampMixin):
    __tablename__ = "drop_tables"

    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    owner_type: Mapped[str] = mapped_column(String(40))
    owner_code: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class DropTableItem(Base, IdMixin, TimestampMixin):
    __tablename__ = "drop_table_items"

    drop_table_code: Mapped[str] = mapped_column(ForeignKey("drop_tables.code", ondelete="CASCADE"))
    item_template_code: Mapped[str] = mapped_column(ForeignKey("item_templates.code", ondelete="RESTRICT"))
    rate: Mapped[float] = mapped_column(Numeric(10, 6), default=0)
    min_quantity: Mapped[int] = mapped_column(Integer, default=1)
    max_quantity: Mapped[int] = mapped_column(Integer, default=1)
    conditions_json: Mapped[dict] = mapped_column(JSONB, default=dict)
