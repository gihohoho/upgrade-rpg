from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class ItemTemplate(Base, IdMixin, TimestampMixin):
    __tablename__ = "item_templates"

    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    item_type: Mapped[str] = mapped_column(String(60), index=True)
    grade: Mapped[str | None] = mapped_column(String(60), nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stackable: Mapped[bool] = mapped_column(Boolean, default=False)
    equip_slot: Mapped[str | None] = mapped_column(String(60), nullable=True)
    enhance_group_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    base_stats_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    options_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ItemInstance(Base, IdMixin, TimestampMixin):
    __tablename__ = "item_instances"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    template_code: Mapped[str] = mapped_column(ForeignKey("item_templates.code", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    enhance_level: Mapped[int] = mapped_column(Integer, default=0)
    bound_character_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    instance_stats_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    instance_options_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class UserInventorySlot(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_inventory_slots"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    bag_type: Mapped[str] = mapped_column(String(30), default="inventory")
    slot_index: Mapped[int] = mapped_column(Integer)
    item_instance_id: Mapped[int | None] = mapped_column(ForeignKey("item_instances.id", ondelete="SET NULL"), nullable=True)


class UserEquipmentSlot(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_equipment_slots"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    character_code: Mapped[str] = mapped_column(String(80), default="weapon_master")
    slot_key: Mapped[str] = mapped_column(String(60))
    item_instance_id: Mapped[int | None] = mapped_column(ForeignKey("item_instances.id", ondelete="SET NULL"), nullable=True)
