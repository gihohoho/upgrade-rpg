from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Skill(Base, IdMixin, TimestampMixin):
    __tablename__ = "skills"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    slot_key: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    proc_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=0)
    options_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class CharacterSkill(Base, IdMixin, TimestampMixin):
    __tablename__ = "character_skills"
    __table_args__ = (UniqueConstraint("character_code", "skill_code", name="uq_character_skill"),)

    character_code: Mapped[str] = mapped_column(ForeignKey("characters.code", ondelete="CASCADE"))
    skill_code: Mapped[str] = mapped_column(ForeignKey("skills.code", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)


class SkillLevel(Base, IdMixin, TimestampMixin):
    __tablename__ = "skill_levels"
    __table_args__ = (UniqueConstraint("skill_code", "level", name="uq_skill_level"),)

    skill_code: Mapped[str] = mapped_column(ForeignKey("skills.code", ondelete="CASCADE"))
    level: Mapped[int] = mapped_column(Integer)
    damage_multiplier: Mapped[float] = mapped_column(Numeric(14, 6), default=0)
    proc_rate_bonus: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    options_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class UserCharacterSkill(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_character_skills"
    __table_args__ = (UniqueConstraint("user_id", "character_code", "skill_code", name="uq_user_character_skill"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    character_code: Mapped[str] = mapped_column(ForeignKey("characters.code", ondelete="CASCADE"))
    skill_code: Mapped[str] = mapped_column(ForeignKey("skills.code", ondelete="CASCADE"))
    level: Mapped[int] = mapped_column(Integer, default=0)
    is_awakened: Mapped[bool] = mapped_column(Boolean, default=False)
    state_json: Mapped[dict] = mapped_column(JSONB, default=dict)
