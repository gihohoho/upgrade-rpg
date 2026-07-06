from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class FieldZone(Base, IdMixin, TimestampMixin):
    __tablename__ = "field_zones"

    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    enemy_hp: Mapped[float] = mapped_column(Numeric(40, 0), default=1)
    gold_reward: Mapped[float] = mapped_column(Numeric(40, 0), default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    entry_rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    farm_rules_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
