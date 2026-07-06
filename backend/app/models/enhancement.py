from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class EnhancementGroup(Base, IdMixin, TimestampMixin):
    __tablename__ = "enhancement_groups"

    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_level: Mapped[int] = mapped_column(Integer, default=0)
    rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class EnhancementLevel(Base, IdMixin, TimestampMixin):
    __tablename__ = "enhancement_levels"
    __table_args__ = (UniqueConstraint("group_code", "from_level", name="uq_enhancement_step"),)

    group_code: Mapped[str] = mapped_column(ForeignKey("enhancement_groups.code", ondelete="CASCADE"))
    from_level: Mapped[int] = mapped_column(Integer)
    to_level: Mapped[int] = mapped_column(Integer)
    success_rate: Mapped[float] = mapped_column(Numeric(10, 6), default=0)
    gold_cost: Mapped[float] = mapped_column(Numeric(40, 0), default=0)
    material_rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    result_stats_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    fail_rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
