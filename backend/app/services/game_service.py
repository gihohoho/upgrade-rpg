from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Boss,
    Character,
    CharacterSkill,
    DropTable,
    DropTableItem,
    EnhancementGroup,
    EnhancementLevel,
    FieldZone,
    ItemTemplate,
    Skill,
    SkillLevel,
)


def serialize_value(value: Any) -> Any:
    """Convert DB values into JSON-friendly values.

    PostgreSQL NUMERIC is returned as Decimal. Large integer-like game values such as
    boss HP should remain integers instead of becoming floating point values.
    """
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    return value


class GameService:
    """Read/write service for game APIs.

    This stage only reads master data. User save/load still remains a stub until the
    localStorage migration step starts.
    """

    async def get_master_data(self, session: AsyncSession) -> dict[str, Any]:
        characters = await self._fetch_characters(session)
        skills = await self._fetch_skills(session)
        character_skills = await self._fetch_character_skills(session)
        skill_levels = await self._fetch_skill_levels(session)
        item_templates = await self._fetch_item_templates(session)
        bosses = await self._fetch_bosses(session)
        field_zones = await self._fetch_field_zones(session)
        drop_tables = await self._fetch_drop_tables(session)
        drop_table_items = await self._fetch_drop_table_items(session)
        enhancement_groups = await self._fetch_enhancement_groups(session)
        enhancement_levels = await self._fetch_enhancement_levels(session)

        enhancement_rules = {
            "groups": enhancement_groups,
            "levels": enhancement_levels,
        }
        counts = {
            "characters": len(characters),
            "skills": len(skills),
            "characterSkills": len(character_skills),
            "skillLevels": len(skill_levels),
            "itemTemplates": len(item_templates),
            "bosses": len(bosses),
            "fieldZones": len(field_zones),
            "dropTables": len(drop_tables),
            "dropTableItems": len(drop_table_items),
            "enhancementGroups": len(enhancement_groups),
            "enhancementLevels": len(enhancement_levels),
        }

        return {
            "characters": characters,
            "skills": skills,
            "characterSkills": character_skills,
            "skillLevels": skill_levels,
            "itemTemplates": item_templates,
            "bosses": bosses,
            "fieldZones": field_zones,
            "dropTables": drop_tables,
            "dropTableItems": drop_table_items,
            "enhancementGroups": enhancement_groups,
            "enhancementLevels": enhancement_levels,
            "enhancementRules": enhancement_rules,
            "counts": counts,
        }

    async def load_game(self, user_id: int) -> dict[str, Any]:
        return {"userId": user_id, "status": "stub"}

    async def _fetch_characters(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(Character).order_by(Character.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "imageUrl": row.image_url,
                "isEnabled": row.is_enabled,
                "meta": serialize_value(row.meta_json),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_skills(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(Skill).order_by(Skill.slot_key, Skill.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "slotKey": row.slot_key,
                "description": row.description,
                "iconUrl": row.icon_url,
                "procRate": serialize_value(row.proc_rate),
                "cooldownSeconds": row.cooldown_seconds,
                "options": serialize_value(row.options_json),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_character_skills(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            select(CharacterSkill).order_by(CharacterSkill.character_code, CharacterSkill.sort_order, CharacterSkill.skill_code)
        )
        return [
            {
                "characterCode": row.character_code,
                "skillCode": row.skill_code,
                "sortOrder": row.sort_order,
                "isDefault": row.is_default,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_skill_levels(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(SkillLevel).order_by(SkillLevel.skill_code, SkillLevel.level))
        return [
            {
                "skillCode": row.skill_code,
                "level": row.level,
                "damageMultiplier": serialize_value(row.damage_multiplier),
                "procRateBonus": serialize_value(row.proc_rate_bonus),
                "options": serialize_value(row.options_json),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_item_templates(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(ItemTemplate).order_by(ItemTemplate.item_type, ItemTemplate.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "itemType": row.item_type,
                "grade": row.grade,
                "iconUrl": row.icon_url,
                "description": row.description,
                "stackable": row.stackable,
                "equipSlot": row.equip_slot,
                "enhanceGroupCode": row.enhance_group_code,
                "baseStats": serialize_value(row.base_stats_json),
                "options": serialize_value(row.options_json),
                "adminNote": row.admin_note,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_bosses(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(Boss).order_by(Boss.boss_type, Boss.tier, Boss.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "tier": row.tier,
                "bossType": row.boss_type,
                "hp": serialize_value(row.hp),
                "imageUrl": row.image_url,
                "description": row.description,
                "summonRules": serialize_value(row.summon_rules_json),
                "cooldownSeconds": row.cooldown_seconds,
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_field_zones(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(FieldZone).order_by(FieldZone.sort_order, FieldZone.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "sortOrder": row.sort_order,
                "enemyHp": serialize_value(row.enemy_hp),
                "goldReward": serialize_value(row.gold_reward),
                "description": row.description,
                "entryRules": serialize_value(row.entry_rules_json),
                "farmRules": serialize_value(row.farm_rules_json),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_drop_tables(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(DropTable).order_by(DropTable.owner_code, DropTable.code))
        return [
            {
                "code": row.code,
                "ownerType": row.owner_type,
                "ownerCode": row.owner_code,
                "description": row.description,
                "rules": serialize_value(row.rules_json),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_drop_table_items(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(DropTableItem).order_by(DropTableItem.drop_table_code, DropTableItem.id))
        return [
            {
                "id": row.id,
                "dropTableCode": row.drop_table_code,
                "itemTemplateCode": row.item_template_code,
                "rate": serialize_value(row.rate),
                "minQuantity": row.min_quantity,
                "maxQuantity": row.max_quantity,
                "conditions": serialize_value(row.conditions_json),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_enhancement_groups(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(EnhancementGroup).order_by(EnhancementGroup.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "maxLevel": row.max_level,
                "rules": serialize_value(row.rules_json),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_enhancement_levels(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            select(EnhancementLevel).order_by(EnhancementLevel.group_code, EnhancementLevel.from_level)
        )
        return [
            {
                "groupCode": row.group_code,
                "fromLevel": row.from_level,
                "toLevel": row.to_level,
                "successRate": serialize_value(row.success_rate),
                "goldCost": serialize_value(row.gold_cost),
                "materialRules": serialize_value(row.material_rules_json),
                "resultStats": serialize_value(row.result_stats_json),
                "failRules": serialize_value(row.fail_rules_json),
            }
            for row in result.scalars().all()
        ]
