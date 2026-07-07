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
    User,
    UserProfile,
    UserSaveSnapshot,
)


INLINE_ASSET_PREFIXES = (
    "data:image/svg+xml",
    "data:image/png",
    "data:image/jpeg",
    "data:image/webp",
)


def is_inline_asset_string(value: Any) -> bool:
    """Return True when a value is an inline image data URL.

    Seed JSON can contain image strings not only in top-level image_url/icon_url
    columns but also inside nested options JSON. The default master-data response
    should not include those long strings because some local antivirus tools flag
    large inline SVG payloads inside JSON responses.
    """
    if not isinstance(value, str):
        return False
    return value.startswith(INLINE_ASSET_PREFIXES)


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


def serialize_master_value(value: Any, *, include_assets: bool) -> Any:
    """Serialize DB values and optionally remove nested inline image assets.

    Top-level fields such as iconUrl/imageUrl are handled separately, but nested
    JSON fields like options/baseStats may also contain copied asset URLs. When
    include_assets is false, replace every inline image data URL with None while
    preserving the surrounding object shape.
    """
    serialized = serialize_value(value)

    if include_assets:
        return serialized

    if is_inline_asset_string(serialized):
        return None
    if isinstance(serialized, list):
        return [serialize_master_value(item, include_assets=include_assets) for item in serialized]
    if isinstance(serialized, dict):
        return {key: serialize_master_value(item, include_assets=include_assets) for key, item in serialized.items()}
    return serialized


class GameService:
    """Read/write service for game APIs.

    This stage only reads master data. User save/load still remains a stub until the
    localStorage migration step starts.
    """

    async def get_master_data(self, session: AsyncSession, *, include_assets: bool = False) -> dict[str, Any]:
        characters = await self._fetch_characters(session, include_assets=include_assets)
        skills = await self._fetch_skills(session, include_assets=include_assets)
        character_skills = await self._fetch_character_skills(session)
        skill_levels = await self._fetch_skill_levels(session, include_assets=include_assets)
        item_templates = await self._fetch_item_templates(session, include_assets=include_assets)
        bosses = await self._fetch_bosses(session, include_assets=include_assets)
        field_zones = await self._fetch_field_zones(session, include_assets=include_assets)
        drop_tables = await self._fetch_drop_tables(session, include_assets=include_assets)
        drop_table_items = await self._fetch_drop_table_items(session, include_assets=include_assets)
        enhancement_groups = await self._fetch_enhancement_groups(session, include_assets=include_assets)
        enhancement_levels = await self._fetch_enhancement_levels(session, include_assets=include_assets)

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
            "assetPolicy": self._build_asset_policy(include_assets=include_assets),
            "counts": counts,
        }

    def _build_asset_policy(self, *, include_assets: bool) -> dict[str, Any]:
        return {
            "includeAssets": include_assets,
            "mode": "inline-data-url" if include_assets else "metadata-only",
            "excludedByDefault": [
                "characters.imageUrl",
                "skills.iconUrl",
                "itemTemplates.iconUrl",
                "bosses.imageUrl",
                "*.options.* inline data:image URLs",
                "*.rules.* inline data:image URLs",
                "dropTableItems.conditions.* inline data:image URLs",
            ],
            "includeAssetsQuery": "?includeAssets=true",
            "note": (
                "기본 응답은 백신 오탐과 응답 크기 증가를 줄이기 위해 최상위 asset 필드와 중첩 JSON 안의 긴 SVG/data URL을 null로 내려줍니다."
                if not include_assets
                else "includeAssets=true 요청이므로 최상위 asset 필드와 중첩 JSON 안의 긴 SVG/data URL을 함께 내려줍니다."
            ),
        }

    @staticmethod
    def _asset_value(value: str | None, *, include_assets: bool) -> str | None:
        if include_assets:
            return value
        return None

    async def load_game(self, session: AsyncSession, user_id: int, *, slot_key: str = "default") -> dict[str, Any]:
        """Load the latest raw save snapshot for a user/slot.

        This is a migration bridge. It returns the raw snapshot exactly as stored so
        later browser-side migration can still use the existing saveVersion rules.
        """
        result = await session.execute(
            select(UserSaveSnapshot).where(
                UserSaveSnapshot.user_id == user_id,
                UserSaveSnapshot.slot_key == slot_key,
            )
        )
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            return {
                "userId": user_id,
                "slotKey": slot_key,
                "status": "empty",
                "exists": False,
                "clientSaveKey": None,
                "saveVersion": None,
                "snapshot": None,
                "summary": {},
                "source": None,
                "updatedAt": None,
            }

        return self._serialize_save_snapshot(snapshot, status="loaded")


    async def list_save_slots(self, session: AsyncSession, user_id: int) -> dict[str, Any]:
        """List save snapshot slots for a user without returning full snapshots.

        Returning only metadata/summary keeps the API light and safe while preparing
        the project for multiple save slots and a future admin page.
        """
        result = await session.execute(
            select(UserSaveSnapshot)
            .where(UserSaveSnapshot.user_id == user_id)
            .order_by(UserSaveSnapshot.updated_at.desc(), UserSaveSnapshot.slot_key)
        )
        slots = [self._serialize_save_slot(row) for row in result.scalars().all()]
        return {
            "userId": user_id,
            "status": "loaded",
            "exists": bool(slots),
            "count": len(slots),
            "slots": slots,
        }

    async def save_game_snapshot(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        username: str,
        payload: Any,
    ) -> dict[str, Any]:
        """Store the browser localStorage save payload as one raw DB snapshot.

        The local dev auth placeholder uses user id 1. Since local schema resets wipe
        users too, this method also ensures the placeholder user/profile exists before
        inserting the save snapshot.
        """
        await self._ensure_local_user(session, user_id=user_id, username=username)

        snapshot_data = payload.snapshot or {}
        save_version = payload.save_version
        if save_version is None and isinstance(snapshot_data, dict):
            raw_version = snapshot_data.get("saveVersion")
            if raw_version is not None:
                try:
                    save_version = int(raw_version)
                except (TypeError, ValueError):
                    save_version = 0
        if save_version is None:
            save_version = 0

        result = await session.execute(
            select(UserSaveSnapshot).where(
                UserSaveSnapshot.user_id == user_id,
                UserSaveSnapshot.slot_key == payload.slot_key,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = UserSaveSnapshot(
                user_id=user_id,
                slot_key=payload.slot_key,
                client_save_key=payload.client_save_key,
                save_version=save_version,
                snapshot_json=snapshot_data,
                summary_json=payload.summary or {},
                source=payload.source or "localStorage",
                note=payload.note,
            )
            session.add(row)
        else:
            row.client_save_key = payload.client_save_key
            row.save_version = save_version
            row.snapshot_json = snapshot_data
            row.summary_json = payload.summary or {}
            row.source = payload.source or "localStorage"
            row.note = payload.note

        await session.commit()
        await session.refresh(row)
        return self._serialize_save_snapshot(row, status="saved")

    async def _ensure_local_user(self, session: AsyncSession, *, user_id: int, username: str) -> None:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id, username=username or f"local-dev-{user_id}", is_active=True, is_admin=True)
            session.add(user)
            await session.flush()

        result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        if profile is None:
            session.add(UserProfile(user_id=user_id))
            await session.flush()


    def _serialize_save_slot(self, snapshot: UserSaveSnapshot) -> dict[str, Any]:
        return {
            "userId": snapshot.user_id,
            "slotKey": snapshot.slot_key,
            "exists": True,
            "isDefault": snapshot.slot_key == "default",
            "clientSaveKey": snapshot.client_save_key,
            "saveVersion": snapshot.save_version,
            "summary": serialize_value(snapshot.summary_json),
            "source": snapshot.source,
            "note": snapshot.note,
            "createdAt": serialize_value(snapshot.created_at),
            "updatedAt": serialize_value(snapshot.updated_at),
        }

    def _serialize_save_snapshot(self, snapshot: UserSaveSnapshot, *, status: str) -> dict[str, Any]:
        return {
            "userId": snapshot.user_id,
            "slotKey": snapshot.slot_key,
            "status": status,
            "exists": True,
            "clientSaveKey": snapshot.client_save_key,
            "saveVersion": snapshot.save_version,
            "snapshot": serialize_value(snapshot.snapshot_json),
            "summary": serialize_value(snapshot.summary_json),
            "source": snapshot.source,
            "note": snapshot.note,
            "createdAt": serialize_value(snapshot.created_at),
            "updatedAt": serialize_value(snapshot.updated_at),
        }

    async def _fetch_characters(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(Character).order_by(Character.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "imageUrl": self._asset_value(row.image_url, include_assets=include_assets),
                "hasImage": bool(row.image_url),
                "isEnabled": row.is_enabled,
                "meta": serialize_master_value(row.meta_json, include_assets=include_assets),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_skills(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(Skill).order_by(Skill.slot_key, Skill.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "slotKey": row.slot_key,
                "description": row.description,
                "iconUrl": self._asset_value(row.icon_url, include_assets=include_assets),
                "hasIcon": bool(row.icon_url),
                "procRate": serialize_value(row.proc_rate),
                "cooldownSeconds": row.cooldown_seconds,
                "options": serialize_master_value(row.options_json, include_assets=include_assets),
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

    async def _fetch_skill_levels(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(SkillLevel).order_by(SkillLevel.skill_code, SkillLevel.level))
        return [
            {
                "skillCode": row.skill_code,
                "level": row.level,
                "damageMultiplier": serialize_value(row.damage_multiplier),
                "procRateBonus": serialize_value(row.proc_rate_bonus),
                "options": serialize_master_value(row.options_json, include_assets=include_assets),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_item_templates(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(ItemTemplate).order_by(ItemTemplate.item_type, ItemTemplate.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "itemType": row.item_type,
                "grade": row.grade,
                "iconUrl": self._asset_value(row.icon_url, include_assets=include_assets),
                "hasIcon": bool(row.icon_url),
                "description": row.description,
                "stackable": row.stackable,
                "equipSlot": row.equip_slot,
                "enhanceGroupCode": row.enhance_group_code,
                "baseStats": serialize_master_value(row.base_stats_json, include_assets=include_assets),
                "options": serialize_master_value(row.options_json, include_assets=include_assets),
                "adminNote": row.admin_note,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_bosses(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(Boss).order_by(Boss.boss_type, Boss.tier, Boss.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "tier": row.tier,
                "bossType": row.boss_type,
                "hp": serialize_value(row.hp),
                "imageUrl": self._asset_value(row.image_url, include_assets=include_assets),
                "hasImage": bool(row.image_url),
                "description": row.description,
                "summonRules": serialize_master_value(row.summon_rules_json, include_assets=include_assets),
                "cooldownSeconds": row.cooldown_seconds,
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_field_zones(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(FieldZone).order_by(FieldZone.sort_order, FieldZone.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "sortOrder": row.sort_order,
                "enemyHp": serialize_value(row.enemy_hp),
                "goldReward": serialize_value(row.gold_reward),
                "description": row.description,
                "entryRules": serialize_master_value(row.entry_rules_json, include_assets=include_assets),
                "farmRules": serialize_master_value(row.farm_rules_json, include_assets=include_assets),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_drop_tables(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(DropTable).order_by(DropTable.owner_code, DropTable.code))
        return [
            {
                "code": row.code,
                "ownerType": row.owner_type,
                "ownerCode": row.owner_code,
                "description": row.description,
                "rules": serialize_master_value(row.rules_json, include_assets=include_assets),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_drop_table_items(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(DropTableItem).order_by(DropTableItem.drop_table_code, DropTableItem.id))
        return [
            {
                "id": row.id,
                "dropTableCode": row.drop_table_code,
                "itemTemplateCode": row.item_template_code,
                "rate": serialize_value(row.rate),
                "minQuantity": row.min_quantity,
                "maxQuantity": row.max_quantity,
                "conditions": serialize_master_value(row.conditions_json, include_assets=include_assets),
            }
            for row in result.scalars().all()
        ]

    async def _fetch_enhancement_groups(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
        result = await session.execute(select(EnhancementGroup).order_by(EnhancementGroup.code))
        return [
            {
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "maxLevel": row.max_level,
                "rules": serialize_master_value(row.rules_json, include_assets=include_assets),
                "isEnabled": row.is_enabled,
            }
            for row in result.scalars().all()
        ]

    async def _fetch_enhancement_levels(self, session: AsyncSession, *, include_assets: bool) -> list[dict[str, Any]]:
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
                "materialRules": serialize_master_value(row.material_rules_json, include_assets=include_assets),
                "resultStats": serialize_master_value(row.result_stats_json, include_assets=include_assets),
                "failRules": serialize_master_value(row.fail_rules_json, include_assets=include_assets),
            }
            for row in result.scalars().all()
        ]
