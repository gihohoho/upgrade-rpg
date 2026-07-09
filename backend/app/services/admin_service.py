from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, Numeric, String, Text, func, inspect as sa_inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AdminChangeLog,
    Boss,
    Character,
    CharacterSkill,
    DropTable,
    DropTableItem,
    ItemInstance,
    EnhancementGroup,
    EnhancementLevel,
    FieldZone,
    ItemTemplate,
    Skill,
    SkillLevel,
    User,
    UserCharacterSkill,
    UserEquipmentSlot,
    UserProfile,
    UserSaveSnapshot,
)
from app.services.game_service import serialize_value
from app.services.admin.admin_overview_snapshots_service import AdminOverviewSnapshotsService


class AdminService(AdminOverviewSnapshotsService):
    """Read-only admin preparation helpers.

    The real admin page will eventually edit DB values, but this stage deliberately
    exposes only safe diagnostics. It lets the browser/admin UI verify that master
    data and save snapshots are visible from FastAPI without adding any write path.
    """

    MASTER_DATA_MODELS: tuple[tuple[str, Any], ...] = (
        ("characters", Character),
        ("skills", Skill),
        ("characterSkills", CharacterSkill),
        ("skillLevels", SkillLevel),
        ("itemTemplates", ItemTemplate),
        ("bosses", Boss),
        ("dropTables", DropTable),
        ("dropTableItems", DropTableItem),
        ("fieldZones", FieldZone),
        ("enhancementGroups", EnhancementGroup),
        ("enhancementLevels", EnhancementLevel),
    )

    MASTER_EDIT_APPLY_CONFIRM_TEXT = "APPLY MASTER DATA EDIT"
    MASTER_EDIT_ROLLBACK_CONFIRM_TEXT = "ROLLBACK MASTER DATA EDIT"
    MASTER_CREATE_APPLY_CONFIRM_TEXT = "CREATE MASTER DATA ROW"
    MASTER_CREATE_DELETE_CONFIRM_TEXT = "DELETE CREATED MASTER DATA ROW"
    MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT = "RESTORE DELETED CREATED ROW"
    MASTER_CREATE_APPLY_ALLOWED_DOMAINS: set[str] = {"characters", "enhancementGroups", "fieldZones", "bosses", "skills", "dropTables", "itemTemplates", "dropTableItems", "skillLevels", "enhancementLevels", "characterSkills"}
    MASTER_CREATE_DELETE_ALLOWED_DOMAINS: set[str] = {"characters", "enhancementGroups", "fieldZones", "bosses", "skills", "dropTables", "itemTemplates", "dropTableItems", "skillLevels", "enhancementLevels", "characterSkills"}
    ADMIN_CHANGE_LOG_ACTION_FILTERS: set[str] = {"update", "rollback", "create", "create_delete", "create_delete_restore"}

    MASTER_EDIT_ALLOWED_FIELDS: dict[str, set[str]] = {
        "itemTemplates": {"name", "item_type", "description", "grade", "stackable", "equip_slot", "enhance_group_code", "admin_note"},
        "skills": {"slot_key", "name", "description", "proc_rate", "cooldown_seconds"},
        "skillLevels": {"skill_code", "level", "damage_multiplier", "proc_rate_bonus"},
        "bosses": {"name", "tier", "boss_type", "hp", "description", "cooldown_seconds", "is_enabled"},
        "fieldZones": {"name", "sort_order", "enemy_hp", "gold_reward", "description", "is_enabled"},
        "characters": {"name", "description", "is_enabled"},
        "dropTables": {"owner_type", "owner_code", "description", "is_enabled"},
        "dropTableItems": {"drop_table_code", "item_template_code", "rate", "min_quantity", "max_quantity"},
        "enhancementGroups": {"name", "description", "max_level", "is_enabled"},
        "enhancementLevels": {"group_code", "from_level", "to_level", "success_rate", "gold_cost"},
        "characterSkills": {"character_code", "skill_code", "sort_order", "is_default"},
    }

    MASTER_RELATION_EDIT_FIELDS: dict[str, set[str]] = {
        "itemTemplates": {"enhance_group_code"},
        "dropTables": {"owner_type", "owner_code"},
        "dropTableItems": {"drop_table_code", "item_template_code"},
        "skillLevels": {"skill_code"},
        "enhancementLevels": {"group_code"},
        "characterSkills": {"character_code", "skill_code"},
    }

    MASTER_COMBO_GUARDED_FIELDS: dict[str, set[str]] = {
        "skillLevels": {"skill_code", "level"},
        "enhancementLevels": {"group_code", "from_level"},
        "characterSkills": {"character_code", "skill_code"},
    }

    MASTER_CATALOG_DOMAINS: dict[str, dict[str, Any]] = {
        "itemTemplates": {
            "label": "아이템 템플릿",
            "model": ItemTemplate,
            "search": ("code", "name", "item_type", "grade", "equip_slot", "enhance_group_code", "admin_note"),
            "defaultSort": "code_asc",
            "description": "장비/재료/강화권 등 아이템 기준 데이터",
        },
        "skills": {
            "label": "스킬",
            "model": Skill,
            "search": ("code", "name", "slot_key", "description"),
            "defaultSort": "code_asc",
            "description": "Q/W 스킬과 발동 확률/쿨타임 기준 데이터",
        },
        "skillLevels": {
            "label": "스킬 레벨",
            "model": SkillLevel,
            "search": ("skill_code",),
            "defaultSort": "id_asc",
            "description": "스킬 강화 단계별 배율/발동 보너스",
        },
        "bosses": {
            "label": "보스",
            "model": Boss,
            "search": ("code", "name", "boss_type", "description"),
            "defaultSort": "code_asc",
            "description": "일반/특수 보스 기준 데이터",
        },
        "fieldZones": {
            "label": "필드",
            "model": FieldZone,
            "search": ("code", "name", "description"),
            "defaultSort": "sort_asc",
            "description": "사냥 필드와 보상 기준 데이터",
        },
        "characters": {
            "label": "캐릭터",
            "model": Character,
            "search": ("code", "name", "description"),
            "defaultSort": "code_asc",
            "description": "캐릭터 기준 데이터",
        },
        "dropTables": {
            "label": "드랍 테이블",
            "model": DropTable,
            "search": ("code", "owner_type", "owner_code", "description"),
            "defaultSort": "code_asc",
            "description": "보스/필드별 드랍 묶음",
        },
        "dropTableItems": {
            "label": "드랍 아이템",
            "model": DropTableItem,
            "search": ("drop_table_code", "item_template_code"),
            "defaultSort": "id_asc",
            "description": "드랍 테이블 안의 아이템과 확률",
        },
        "enhancementGroups": {
            "label": "강화 그룹",
            "model": EnhancementGroup,
            "search": ("code", "name", "description"),
            "defaultSort": "code_asc",
            "description": "강화 방식 묶음",
        },
        "enhancementLevels": {
            "label": "강화 단계",
            "model": EnhancementLevel,
            "search": ("group_code",),
            "defaultSort": "id_asc",
            "description": "강화 단계별 확률/비용/결과",
        },
        "characterSkills": {
            "label": "캐릭터 스킬 연결",
            "model": CharacterSkill,
            "search": ("character_code", "skill_code"),
            "defaultSort": "id_asc",
            "description": "캐릭터별 기본 스킬 연결",
        },
    }



    MASTER_CREATE_BLUEPRINT_FIELDS: dict[str, list[dict[str, Any]]] = {
        "itemTemplates": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": "", "note": "아이템을 식별하는 고유 코드입니다. 생성 기능을 열기 전까지는 read-only 설계만 보여줍니다."},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "item_type", "required": True, "inputKind": "preset-select", "defaultValue": "normal"},
            {"key": "grade", "required": False, "inputKind": "number", "defaultValue": None},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "stackable", "required": False, "inputKind": "boolean-select", "defaultValue": False},
            {"key": "equip_slot", "required": False, "inputKind": "preset-select", "defaultValue": ""},
            {"key": "enhance_group_code", "required": False, "inputKind": "relation-select", "defaultValue": "", "targetDomain": "enhancementGroups", "nullable": True},
            {"key": "base_stats_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "options_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "admin_note", "required": False, "inputKind": "textarea", "defaultValue": ""},
        ],
        "skills": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "slot_key", "required": True, "inputKind": "preset-select", "defaultValue": "Q"},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "proc_rate", "required": False, "inputKind": "number", "defaultValue": None},
            {"key": "cooldown_seconds", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "options_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
        ],
        "skillLevels": [
            {"key": "skill_code", "required": True, "inputKind": "relation-select", "targetDomain": "skills", "defaultValue": "", "comboGuard": ["skill_code", "level"]},
            {"key": "level", "required": True, "inputKind": "number", "defaultValue": 1, "comboGuard": ["skill_code", "level"]},
            {"key": "damage_multiplier", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "proc_rate_bonus", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "options_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
        ],
        "bosses": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "tier", "required": False, "inputKind": "number", "defaultValue": None},
            {"key": "boss_type", "required": False, "inputKind": "preset-select", "defaultValue": "normal"},
            {"key": "hp", "required": False, "inputKind": "number", "defaultValue": 1},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "summon_rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "cooldown_seconds", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "is_enabled", "required": False, "inputKind": "boolean-select", "defaultValue": True},
        ],
        "fieldZones": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "sort_order", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "enemy_hp", "required": False, "inputKind": "number", "defaultValue": 1},
            {"key": "gold_reward", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "entry_rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "farm_rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "is_enabled", "required": False, "inputKind": "boolean-select", "defaultValue": True},
        ],
        "characters": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "is_enabled", "required": False, "inputKind": "boolean-select", "defaultValue": True},
            {"key": "meta_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
        ],
        "dropTables": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "owner_type", "required": True, "inputKind": "preset-select", "defaultValue": "boss"},
            {"key": "owner_code", "required": True, "inputKind": "relation-select", "targetDomain": "bosses", "defaultValue": "", "dependsOn": "owner_type", "optionGroups": ["boss", "field"]},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "is_enabled", "required": False, "inputKind": "boolean-select", "defaultValue": True},
        ],
        "dropTableItems": [
            {"key": "drop_table_code", "required": True, "inputKind": "relation-select", "targetDomain": "dropTables", "defaultValue": ""},
            {"key": "item_template_code", "required": True, "inputKind": "relation-select", "targetDomain": "itemTemplates", "defaultValue": ""},
            {"key": "rate", "required": True, "inputKind": "number", "defaultValue": 0},
            {"key": "min_quantity", "required": False, "inputKind": "number", "defaultValue": 1},
            {"key": "max_quantity", "required": False, "inputKind": "number", "defaultValue": 1},
            {"key": "conditions_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
        ],
        "enhancementGroups": [
            {"key": "code", "required": True, "unique": True, "inputKind": "text", "defaultValue": ""},
            {"key": "name", "required": True, "inputKind": "text", "defaultValue": ""},
            {"key": "description", "required": False, "inputKind": "textarea", "defaultValue": ""},
            {"key": "max_level", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "is_enabled", "required": False, "inputKind": "boolean-select", "defaultValue": True},
        ],
        "enhancementLevels": [
            {"key": "group_code", "required": True, "inputKind": "relation-select", "targetDomain": "enhancementGroups", "defaultValue": "", "comboGuard": ["group_code", "from_level"]},
            {"key": "from_level", "required": True, "inputKind": "number", "defaultValue": 0, "comboGuard": ["group_code", "from_level"]},
            {"key": "to_level", "required": True, "inputKind": "number", "defaultValue": 1},
            {"key": "success_rate", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "gold_cost", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "material_rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "result_stats_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
            {"key": "fail_rules_json", "required": False, "inputKind": "json-readonly", "defaultValue": {}, "lockedReason": "JSON 필드는 생성 적용 단계 전까지 잠금"},
        ],
        "characterSkills": [
            {"key": "character_code", "required": True, "inputKind": "relation-select", "targetDomain": "characters", "defaultValue": "", "comboGuard": ["character_code", "skill_code"]},
            {"key": "skill_code", "required": True, "inputKind": "relation-select", "targetDomain": "skills", "defaultValue": "", "comboGuard": ["character_code", "skill_code"]},
            {"key": "sort_order", "required": False, "inputKind": "number", "defaultValue": 0},
            {"key": "is_default", "required": False, "inputKind": "boolean-select", "defaultValue": True},
        ],
    }

    def _master_create_lifecycle_dependency_guards(self, domain: str) -> list[dict[str, Any]]:
        guard_map: dict[str, list[dict[str, Any]]] = {
            "characters": [
                {"label": "캐릭터 스킬 연결", "target": "character_skills.character_code", "blocksDelete": True, "note": "기본 스킬 연결이 있으면 캐릭터 삭제를 막습니다."},
                {"label": "유저 캐릭터 스킬", "target": "user_character_skills.character_code", "blocksDelete": True, "note": "유저 진행 데이터에서 사용 중이면 삭제를 막습니다."},
                {"label": "유저 장비 슬롯", "target": "user_equipment_slots.character_code", "blocksDelete": True, "note": "장비 슬롯 데이터에서 사용 중이면 삭제를 막습니다."},
                {"label": "유저 현재 캐릭터", "target": "user_profiles.current_character_id", "blocksDelete": True, "note": "현재 선택 캐릭터로 사용 중이면 삭제를 막습니다."},
            ],
            "enhancementGroups": [
                {"label": "강화 단계", "target": "enhancement_levels.group_code", "blocksDelete": True, "note": "강화 단계가 있으면 그룹 삭제를 막습니다."},
                {"label": "아이템 강화 그룹", "target": "item_templates.enhance_group_code", "blocksDelete": True, "note": "아이템 템플릿에서 사용 중이면 삭제를 막습니다."},
            ],
            "fieldZones": [
                {"label": "필드 드랍 테이블", "target": "drop_tables.owner_type=field + owner_code", "blocksDelete": True, "note": "필드에 연결된 드랍 테이블이 있으면 삭제를 막습니다."},
            ],
            "bosses": [
                {"label": "보스 드랍 테이블", "target": "drop_tables.owner_type=boss + owner_code", "blocksDelete": True, "note": "보스에 연결된 드랍 테이블이 있으면 삭제를 막습니다."},
            ],
            "skills": [
                {"label": "스킬 레벨", "target": "skill_levels.skill_code", "blocksDelete": True, "note": "스킬 레벨이 있으면 삭제를 막습니다."},
                {"label": "캐릭터 스킬 연결", "target": "character_skills.skill_code", "blocksDelete": True, "note": "캐릭터 기본 스킬로 쓰이면 삭제를 막습니다."},
                {"label": "유저 캐릭터 스킬", "target": "user_character_skills.skill_code", "blocksDelete": True, "note": "유저 진행 데이터에서 사용 중이면 삭제를 막습니다."},
            ],
            "dropTables": [
                {"label": "드랍 아이템", "target": "drop_table_items.drop_table_code", "blocksDelete": True, "note": "드랍 아이템 row가 있으면 드랍 테이블 삭제를 막습니다."},
            ],
            "itemTemplates": [
                {"label": "드랍 아이템", "target": "drop_table_items.item_template_code", "blocksDelete": True, "note": "드랍 테이블에서 사용 중이면 아이템 템플릿 삭제를 막습니다."},
                {"label": "유저 아이템 인스턴스", "target": "item_instances.template_code", "blocksDelete": True, "note": "유저 인벤토리/창고에 생성된 아이템이면 삭제를 막습니다."},
            ],
            "dropTableItems": [
                {"label": "id 기반 leaf row", "target": "drop_table_items.id", "blocksDelete": False, "note": "하위 연결이 없는 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "skillLevels": [
                {"label": "id 기반 leaf row", "target": "skill_levels.id", "blocksDelete": False, "note": "스킬을 참조하는 레벨 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "enhancementLevels": [
                {"label": "id 기반 leaf row", "target": "enhancement_levels.id", "blocksDelete": False, "note": "강화 그룹을 참조하는 단계 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "characterSkills": [
                {"label": "id 기반 leaf row", "target": "character_skills.id", "blocksDelete": False, "note": "캐릭터와 스킬을 연결하는 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
        }
        return guard_map.get(domain, [])

    def _master_create_lifecycle_payload(self, domain: str) -> dict[str, Any]:
        create_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        delete_unlocked = domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS
        field_defs = self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain) or []
        has_code_field = any(str(field.get("key") or "") == "code" for field in field_defs)
        locked_fields = [str(field.get("key")) for field in field_defs if str(field.get("inputKind") or "") == "json-readonly" or str(field.get("key") or "").endswith("_json") or self._is_asset_field(str(field.get("key") or ""))]
        combo_guards: list[list[str]] = []
        for field in field_defs:
            combo_guard = field.get("comboGuard") if isinstance(field.get("comboGuard"), list) else None
            if combo_guard and combo_guard not in combo_guards:
                combo_guards.append(combo_guard)
        dependency_guards = self._master_create_lifecycle_dependency_guards(domain)
        dependency_blocker_count = sum(1 for guard in dependency_guards if guard.get("blocksDelete"))
        return {
            "createApplyUnlocked": create_unlocked,
            "createDeleteUnlocked": delete_unlocked,
            "createDeleteRestoreUnlocked": delete_unlocked,
            "identityMode": "code+id" if has_code_field else "id",
            "deleteRestoreKey": "code/id" if has_code_field else "id",
            "confirmTexts": {
                "create": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
                "deleteCreatedRow": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
                "restoreDeletedCreatedRow": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            },
            "comboGuards": combo_guards,
            "lockedFieldCount": len(locked_fields),
            "lockedFields": locked_fields[:30],
            "jsonAssetLocked": bool(locked_fields),
            "deleteDependencyGuards": dependency_guards,
            "deleteDependencyGuardCount": len(dependency_guards),
            "deleteDependencyBlockerGuardCount": dependency_blocker_count,
            "deleteGuardMode": "dependency-blocking" if dependency_blocker_count else "leaf-id-current-match",
            "manualCheckRequired": True,
            "browserCheckOrder": [
                "생성 설계 불러오기",
                "relation 후보/검색 확인",
                "생성 초안 검증",
                "실제 생성 적용",
                "change log에서 create 이력 열기",
                "생성 row 삭제 미리보기/apply",
                "change log에서 create_delete 이력 열기",
                "삭제 row 복원 미리보기/apply",
            ],
        }

    async def preview_change(self, target_type: str, before: dict, after: dict) -> dict:
        return {
            "targetType": target_type,
            "before": before,
            "after": after,
            "warnings": [],
            "allowed": True,
            "readOnly": True,
            "note": "현재 단계에서는 관리자 변경 적용 없이 미리보기/검증 구조만 준비합니다.",
        }


    async def preview_master_data_edit(
        self,
        session: AsyncSession,
        *,
        domain: str,
        row_id: int,
        draft: dict[str, Any],
        base_values: dict[str, Any] | None = None,
        reason: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Validate an admin edit draft without mutating the database.

        The static admin page can now behave like a real edit screen, but this
        endpoint is still preview-only. It loads the current row from PostgreSQL,
        normalizes proposed scalar values, builds a diff, and returns validation
        errors/warnings. It never assigns attributes, flushes, commits, or returns
        raw JSON/assets.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_edit_preview(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                row_id=row_id,
                warnings=["domain_invalid"],
            )

        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return self._empty_edit_preview(
                status="invalid_id",
                domain=domain,
                domain_label=config["label"],
                row_id=row_id,
                warnings=["id_invalid"],
            )

        model = config["model"]
        result = await session.execute(select(model).where(model.id == safe_row_id))
        row = result.scalar_one_or_none()
        if row is None:
            return self._empty_edit_preview(
                status="not_found",
                domain=domain,
                domain_label=config["label"],
                row_id=safe_row_id,
                warnings=["row_not_found"],
            )

        safe_draft = draft if isinstance(draft, dict) else {}
        if len(safe_draft) > 80:
            # The UI only sends visible fields, but this keeps manual API calls bounded.
            safe_draft = dict(list(safe_draft.items())[:80])

        safe_base_values = base_values if isinstance(base_values, dict) else None

        column_map = self._master_edit_column_map(row)
        accepted_changes: list[dict[str, Any]] = []
        unchanged: list[dict[str, Any]] = []
        rejected_changes: list[dict[str, Any]] = []
        stale_changes: list[dict[str, Any]] = []
        warnings: list[str] = []

        for raw_key, raw_after in safe_draft.items():
            key = str(raw_key or "").strip()
            if not key:
                rejected_changes.append({"key": raw_key, "reason": "empty_field_key"})
                continue

            column = column_map.get(key)
            if column is None:
                rejected_changes.append({"key": key, "reason": "unknown_field"})
                continue

            if self._master_edit_field_is_readonly(domain, key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "read_only_field"})
                continue
            if not self._master_edit_field_is_allowed(domain, key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "field_not_open_for_apply_yet"})
                continue
            if key.endswith("_json"):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "json_edit_not_enabled_yet"})
                continue
            if self._is_asset_field(key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "asset_edit_not_enabled_yet"})
                continue

            before_value = serialize_value(getattr(row, key, None))

            if safe_base_values is not None:
                if key not in safe_base_values:
                    stale_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "base": None,
                        "current": before_value,
                        "after": raw_after,
                        "reason": "base_value_missing",
                    })
                    rejected_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "before": before_value,
                        "after": raw_after,
                        "reason": "base_value_missing",
                    })
                    continue

                normalized_base, base_issue = self._normalize_master_edit_value(column, safe_base_values.get(key))
                base_value = serialize_value(safe_base_values.get(key) if base_issue else normalized_base)
                if base_value != before_value:
                    stale_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "base": base_value,
                        "current": before_value,
                        "after": raw_after,
                        "reason": "current_value_changed_since_form_loaded",
                    })
                    rejected_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "before": before_value,
                        "after": raw_after,
                        "reason": "current_value_changed_since_form_loaded",
                    })
                    continue

            normalized_after, issue = self._normalize_master_edit_value(column, raw_after)
            if issue:
                rejected_changes.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "before": before_value,
                    "after": raw_after,
                    "reason": issue,
                })
                continue

            relation_issue = await self._validate_master_relation_edit_value(session, domain, key, normalized_after, row, safe_draft, column_map)
            if relation_issue:
                rejected_changes.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "before": before_value,
                    "after": raw_after,
                    "reason": relation_issue,
                })
                continue

            relation_info = await self._describe_master_relation_edit_value(session, domain, key, normalized_after, row, safe_draft, column_map)
            normalized_after = serialize_value(normalized_after)
            change = {
                "key": key,
                "label": self._humanize_field_name(key),
                "before": before_value,
                "after": normalized_after,
                "rawAfter": raw_after,
                "type": self._master_edit_column_type(column),
            }
            if relation_info:
                change["relation"] = relation_info
            if before_value == normalized_after:
                unchanged.append(change)
            else:
                accepted_changes.append(change)

        if not safe_draft:
            warnings.append("draft_empty")
        if reason and len(str(reason)) > 300:
            warnings.append("reason_truncated_in_preview")
        if safe_base_values is None:
            warnings.append("base_values_missing_stale_guard_disabled")
        if stale_changes:
            warnings.append("current_value_changed_since_form_loaded")

        error_count = len(rejected_changes)
        diff_count = len(accepted_changes)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        return {
            "status": "preview_ready",
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "applyReady": error_count == 0 and diff_count > 0,
            "confirmTextRequired": self.MASTER_EDIT_APPLY_CONFIRM_TEXT,
            "allowedFields": sorted(self.MASTER_EDIT_ALLOWED_FIELDS.get(domain, set())),
            "wouldBeValid": error_count == 0,
            "domain": domain,
            "domainLabel": config["label"],
            "id": safe_row_id,
            "title": title,
            "reason": str(reason or "")[:300] if reason else None,
            "diffCount": diff_count,
            "errorCount": error_count,
            "unchangedCount": len(unchanged),
            "staleCount": len(stale_changes),
            "staleChanges": stale_changes[:30],
            "staleGuardEnabled": safe_base_values is not None,
            "acceptedChanges": accepted_changes,
            "rejectedChanges": rejected_changes,
            "unchangedChanges": unchanged[:30],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
            "note": "편집 초안을 검증만 했습니다. 이 응답은 DB를 수정하지 않는 dry-run 결과입니다.",
        }

    async def apply_master_data_edit(
        self,
        session: AsyncSession,
        *,
        domain: str,
        row_id: int,
        draft: dict[str, Any],
        base_values: dict[str, Any] | None,
        reason: str | None,
        confirm_text: str,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded scalar master-data edit and write an audit log.

        This is the first real admin write path, so it intentionally supports only
        a small allow-list of scalar fields. It always validates through the same
        preview path first, requires an exact confirmation phrase, and stores before
        and after values in admin_change_logs so the next step can add rollback.
        """
        preview = await self.preview_master_data_edit(
            session,
            domain=domain,
            row_id=row_id,
            draft=draft,
            base_values=base_values,
            reason=reason,
            dry_run=True,
        )

        if str(confirm_text or "").strip() != self.MASTER_EDIT_APPLY_CONFIRM_TEXT:
            preview.update({
                "status": "confirmation_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "confirm_text_mismatch"],
                "note": "정확한 확인 문구를 입력해야 DB 적용이 가능합니다.",
            })
            return preview

        if not isinstance(base_values, dict) or not base_values:
            preview.update({
                "status": "stale_guard_base_values_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "wouldBeValid": False,
                "staleGuardEnabled": False,
                "warnings": [*(preview.get("warnings") or []), "base_values_required_for_apply"],
                "note": "DB 적용에는 편집 화면을 열었을 때의 기준값(baseValues)이 필요합니다. 상세를 다시 열고 초안을 다시 적용하세요.",
            })
            return preview

        if preview.get("status") != "preview_ready" or preview.get("errorCount") or not preview.get("acceptedChanges"):
            preview.update({
                "status": "apply_rejected",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "preview_not_valid_for_apply"],
                "note": "검증 오류가 있거나 변경된 값이 없어 DB에 적용하지 않았습니다.",
            })
            return preview

        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            preview.update({"status": "invalid_domain", "applied": False, "writeBlocked": True})
            return preview

        model = config["model"]
        result = await session.execute(select(model).where(model.id == int(row_id)))
        row = result.scalar_one_or_none()
        if row is None:
            preview.update({"status": "not_found", "applied": False, "writeBlocked": True})
            return preview

        column_map = self._master_edit_column_map(row)
        before_values: dict[str, Any] = {}
        after_values: dict[str, Any] = {}
        applied_changes: list[dict[str, Any]] = []

        for change in preview.get("acceptedChanges") or []:
            key = str(change.get("key") or "").strip()
            column = column_map.get(key)
            if not key or column is None or not self._master_edit_field_is_allowed(domain, key):
                continue
            before_values[key] = serialize_value(getattr(row, key, None))
            normalized_after, issue = self._normalize_master_edit_value(column, (draft or {}).get(key))
            if issue:
                continue
            setattr(row, key, normalized_after)
            after_values[key] = serialize_value(normalized_after)
            applied_changes.append({**change, "after": serialize_value(normalized_after)})

        if not applied_changes:
            await session.rollback()
            preview.update({
                "status": "nothing_to_apply",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "warnings": [*(preview.get("warnings") or []), "no_applyable_changes"],
            })
            return preview

        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{row_id}"
        change_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="update",
            reason=str(reason or "")[:500] or None,
            before_json=before_values,
            after_json=after_values,
            rollback_json={"domain": domain, "id": int(row_id), "draft": before_values},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(change_log)

        return {
            **preview,
            "status": "applied",
            "readOnly": False,
            "dryRun": False,
            "writeBlocked": False,
            "applied": True,
            "applyReady": False,
            "wouldBeValid": True,
            "title": title,
            "diffCount": len(applied_changes),
            "acceptedChanges": applied_changes,
            "changeLogId": change_log.id,
            "appliedByAdminUserId": int(admin_user_id),
            "note": "관리자 마스터 데이터 변경을 DB에 적용했고, admin_change_logs에 이력을 저장했습니다. 게임 런타임은 새로고침 후 최신 master-data를 다시 읽습니다.",
            "warnings": [*(preview.get("warnings") or []), "game_runtime_requires_reload"],
        }

    async def list_admin_change_logs(
        self,
        session: AsyncSession,
        *,
        limit: int = 20,
        target_type: str | None = None,
        target_id: str | None = None,
        action: str | None = None,
        changed_key: str | None = None,
        applied: bool | None = None,
        sort: str | None = "created_desc",
    ) -> dict[str, Any]:
        safe_limit = max(1, min(int(limit or 20), 100))
        filters = self._clean_admin_change_log_filters(
            target_type=target_type,
            target_id=target_id,
            action=action,
            changed_key=changed_key,
            applied=applied,
            sort=sort,
        )
        clauses = self._build_admin_change_log_where_clauses(filters)

        total = await self._count_admin_change_logs(session, clauses)
        stmt = select(AdminChangeLog)
        if clauses:
            stmt = stmt.where(*clauses)
        stmt = stmt.order_by(*self._admin_change_log_order_by(filters.get("sort") or "created_desc")).limit(safe_limit)
        result = await session.execute(stmt)
        rows = [self._serialize_admin_change_log(row) for row in result.scalars().all()]
        return {
            "status": "loaded",
            "readOnly": True,
            "count": len(rows),
            "total": total,
            "limit": safe_limit,
            "filters": filters,
            "rows": rows,
            "rawBeforeAfterReturned": False,
        }


    async def get_admin_change_log_detail(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
    ) -> dict[str, Any]:
        """Return one admin change log with safe scalar before/after rows.

        The list endpoint intentionally hides before/after values. This detail endpoint
        is still bounded and sanitized, but it gives enough information for an admin to
        understand exactly what changed before using the guarded rollback flow.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_change_log_detail(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])
        detail = await self._serialize_admin_change_log_detail(session, row)
        domain, row_id = self._extract_master_change_target(row)
        rollback_available = bool(row.applied and row.action == "update" and domain and row_id and isinstance(serialize_value(row.rollback_json), dict))
        create_delete_available = bool(row.applied and row.action == "create" and domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS and row_id and isinstance(serialize_value(row.rollback_json), dict))
        create_delete_restore_available = bool(row.applied and row.action == "create_delete" and domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS and row_id and isinstance(serialize_value(row.before_json), dict) and isinstance(serialize_value(row.rollback_json), dict))
        detail["rollback"] = {
            "available": rollback_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "note": "변경 직후 현재 DB 값이 이 변경 이력의 after 값과 일치할 때만 안전 되돌리기가 가능합니다.",
        }
        detail["createDelete"] = {
            "available": create_delete_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "note": "create 이력으로 만든 제한 도메인 row만, 현재값이 생성 당시 값과 같고 연결 데이터가 없을 때 삭제 되돌리기가 가능합니다.",
        }
        detail["createDeleteRestore"] = {
            "available": create_delete_restore_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "note": "create_delete 이력으로 삭제된 제한 도메인 row만, 같은 id/code 충돌이 없을 때 복원할 수 있습니다. fieldZones/bosses는 dropTables(owner_type=field/boss) 연결 검사까지 거칩니다.",
        }
        return detail

    async def preview_admin_change_log_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview rollback of one guarded master-data change log.

        Rollback is deliberately stricter than normal editing: it only proceeds when
        the current DB row still matches the change log's after_json. If another edit
        already changed the row, rollback is blocked to avoid overwriting newer work.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_rollback_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "update" or not domain or not row_id or not isinstance(before_json, dict) or not isinstance(after_json, dict):
            return self._empty_rollback_preview(
                status="rollback_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_master_update"],
                target_type=row.target_type,
                target_id=row.target_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id):
            return self._empty_rollback_preview(
                status="rollback_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
            )

        master_row = await self._get_master_row(session, domain, int(row_id))
        if master_row is None:
            return self._empty_rollback_preview(
                status="target_not_found",
                change_log_id=change_log_id,
                warnings=["target_row_not_found"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=int(row_id),
            )

        keys = sorted(set(before_json.keys()) | set(after_json.keys()))
        current_values = self._current_master_values(master_row, keys)
        after_mismatches = []
        before_matches = []
        for key in keys:
            current = current_values.get(key)
            expected_after = serialize_value(after_json.get(key))
            expected_before = serialize_value(before_json.get(key))
            if current != expected_after:
                after_mismatches.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "current": current,
                    "expectedAfter": expected_after,
                    "rollbackTo": expected_before,
                })
            if current == expected_before:
                before_matches.append(key)

        changes = await self._build_change_log_changes_with_relations(session, domain, before_json, after_json)
        after_mismatches = await self._enrich_rollback_mismatches_with_relations(session, domain, after_mismatches, current_values, after_json, before_json)
        base = {
            "status": "rollback_preview_ready",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "rollbackReady": False,
            "wouldRollback": False,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "relationLabelsReturned": any(change.get("relation") for change in changes),
            "currentMatchesAfter": len(after_mismatches) == 0,
            "currentMismatches": after_mismatches[:30],
            "currentMismatchCount": len(after_mismatches),
            "alreadyRolledBackFieldCount": len(before_matches),
            "rawBeforeAfterReturned": False,
            "warnings": [],
            "note": "현재 DB 값이 변경 이력의 after 값과 일치하면, before 값으로 되돌릴 수 있습니다.",
        }

        if len(before_matches) == len(keys) and keys:
            base.update({
                "status": "already_rolled_back",
                "rollbackReady": False,
                "wouldRollback": False,
                "writeBlocked": True,
                "warnings": ["target_already_matches_before_values"],
                "note": "현재 DB 값이 이미 이 변경 이력의 이전 값과 같습니다. 되돌릴 변경이 없습니다.",
            })
            return base

        if after_mismatches:
            base.update({
                "status": "rollback_blocked_current_changed",
                "rollbackReady": False,
                "wouldRollback": False,
                "writeBlocked": True,
                "warnings": ["current_db_values_do_not_match_change_log_after_values"],
                "note": "이 변경 이후 같은 행이 다시 수정된 것으로 보입니다. 최신 변경을 덮어쓰지 않기 위해 되돌리기를 차단했습니다.",
            })
            return base

        edit_preview = await self.preview_master_data_edit(
            session,
            domain=domain,
            row_id=int(row_id),
            draft=before_json,
            reason=reason,
            dry_run=True,
        )
        error_count = int(edit_preview.get("errorCount") or 0)
        accepted_changes = edit_preview.get("acceptedChanges") or []
        base.update({
            "rollbackReady": error_count == 0 and len(accepted_changes) > 0,
            "wouldRollback": error_count == 0 and len(accepted_changes) > 0,
            "errorCount": error_count,
            "acceptedChanges": accepted_changes,
            "rejectedChanges": edit_preview.get("rejectedChanges") or [],
            "unchangedChanges": edit_preview.get("unchangedChanges") or [],
            "warnings": edit_preview.get("warnings") or [],
            "note": "되돌리기 미리보기입니다. 아직 DB를 수정하지 않았습니다.",
        })
        if not base["rollbackReady"]:
            base.update({
                "status": "rollback_preview_not_valid",
                "writeBlocked": True,
                "wouldRollback": False,
            })
        return base

    async def apply_admin_change_log_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded rollback for one master-data change log."""
        preview = await self.preview_admin_change_log_rollback(
            session,
            change_log_id=change_log_id,
            reason=reason,
        )
        if str(confirm_text or "").strip() != self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT:
            preview.update({
                "status": "rollback_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "rollbackReady": False,
                "wouldRollback": False,
                "warnings": [*(preview.get("warnings") or []), "rollback_confirm_text_mismatch"],
                "note": "정확한 되돌리기 확인 문구를 입력해야 DB에 적용됩니다.",
            })
            return preview
        if not preview.get("rollbackReady") or not preview.get("currentMatchesAfter"):
            preview.update({
                "status": "rollback_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "rollbackReady": False,
                "wouldRollback": False,
                "warnings": [*(preview.get("warnings") or []), "rollback_preview_not_safe_to_apply"],
            })
            return preview

        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            preview.update({"status": "not_found", "rolledBack": False, "writeBlocked": True})
            return preview
        domain, row_id = self._extract_master_change_target(row)
        master_row = await self._get_master_row(session, str(domain), int(row_id or 0))
        if master_row is None:
            preview.update({"status": "target_not_found", "rolledBack": False, "writeBlocked": True})
            return preview

        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        keys = sorted(set(before_json.keys()) | set(after_json.keys()))
        current_values = self._current_master_values(master_row, keys)
        column_map = self._master_edit_column_map(master_row)
        applied_changes: list[dict[str, Any]] = []
        rollback_values: dict[str, Any] = {}
        for key, rollback_to in before_json.items():
            column = column_map.get(key)
            if column is None or not self._master_edit_field_is_allowed(str(domain), key):
                continue
            normalized_value, issue = self._normalize_master_edit_value(column, rollback_to)
            if issue:
                continue
            setattr(master_row, key, normalized_value)
            rollback_values[key] = serialize_value(normalized_value)
            applied_changes.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "before": current_values.get(key),
                "after": serialize_value(normalized_value),
                "type": self._master_edit_column_type(column),
            })

        if not applied_changes:
            await session.rollback()
            preview.update({
                "status": "rollback_nothing_to_apply",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "warnings": [*(preview.get("warnings") or []), "no_rollback_changes_applied"],
            })
            return preview

        rollback_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=row.target_type,
            target_id=row.target_id,
            action="rollback",
            reason=(str(reason or "")[:500] or f"Rollback change log #{change_log_id}"),
            before_json=current_values,
            after_json=rollback_values,
            rollback_json={"domain": domain, "id": int(row_id), "draft": current_values, "sourceChangeLogId": int(change_log_id)},
            applied=True,
        )
        session.add(rollback_log)
        await session.commit()
        await session.refresh(rollback_log)
        applied_changes_with_relations = await self._build_change_log_changes_with_relations(session, str(domain), current_values, rollback_values)

        preview.update({
            "status": "rolled_back",
            "dryRun": False,
            "writeBlocked": False,
            "rolledBack": True,
            "rollbackReady": False,
            "wouldRollback": False,
            "rollbackChangeLogId": rollback_log.id,
            "appliedChanges": applied_changes_with_relations,
            "acceptedChanges": applied_changes_with_relations,
            "relationChangedKeys": [change["key"] for change in applied_changes_with_relations if change.get("relation")],
            "relationChangeCount": sum(1 for change in applied_changes_with_relations if change.get("relation")),
            "relationLabelsReturned": any(change.get("relation") for change in applied_changes_with_relations),
            "diffCount": len(applied_changes_with_relations),
            "warnings": [*(preview.get("warnings") or []), "game_runtime_requires_reload"],
            "note": "관리자 변경 이력을 기준으로 DB 값을 이전 값으로 되돌렸습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다.",
        })


    async def preview_admin_create_delete_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview safe deletion rollback for a row created through create-apply.

        This is intentionally narrower than update rollback. It only supports the
        limited create allow-list, blocks rows that changed after creation, and
        blocks rows with dependent data so no cascade/delete surprise can happen.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_create_delete_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        after_json = serialize_value(row.after_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "create" or not domain or not row_id or not isinstance(after_json, dict):
            return self._empty_create_delete_preview(
                status="create_delete_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_master_create"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if domain not in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS:
            return self._empty_create_delete_preview(
                status="create_delete_domain_locked",
                change_log_id=change_log_id,
                warnings=["create_delete_domain_locked"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id) or rollback_json.get("delete") is not True:
            return self._empty_create_delete_preview(
                status="create_delete_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["create_delete_rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )

        master_row = await self._get_master_row(session, domain, int(row_id))
        if master_row is None:
            return self._empty_create_delete_preview(
                status="target_already_deleted",
                change_log_id=change_log_id,
                warnings=["target_row_not_found"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=int(row_id),
            )

        keys = sorted(after_json.keys())
        current_values = self._current_master_values(master_row, keys)
        current_mismatches: list[dict[str, Any]] = []
        for key in keys:
            current = current_values.get(key)
            expected_after = serialize_value(after_json.get(key))
            if current != expected_after:
                current_mismatches.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "current": current,
                    "expectedAfter": expected_after,
                    "deleteEffect": "blocked_current_changed",
                })

        created_code = getattr(master_row, "code", None)
        dependency_checks = await self._build_create_delete_dependency_checks(session, domain, created_code, int(row_id))
        blocker_guard_count = sum(1 for check in dependency_checks if check.get("blocksDelete"))
        blocker_count = sum(int(check.get("count") or 0) for check in dependency_checks if check.get("blocksDelete"))
        changes = await self._build_change_log_changes_with_relations(session, domain, {}, after_json)
        create_delete_ready = len(current_mismatches) == 0 and blocker_count == 0
        return {
            "status": "create_delete_preview_ready" if create_delete_ready else "create_delete_blocked",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteReady": create_delete_ready,
            "wouldDelete": create_delete_ready,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "code": serialize_value(created_code),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "currentMatchesCreateValues": len(current_mismatches) == 0,
            "currentMismatches": current_mismatches[:30],
            "currentMismatchCount": len(current_mismatches),
            "dependencyChecks": dependency_checks,
            "dependencyCheckCount": len(dependency_checks),
            "dependencyBlockerGuardCount": blocker_guard_count,
            "dependencyBlockerCount": blocker_count,
            "rawBeforeAfterReturned": False,
            "warnings": [] if create_delete_ready else ["create_delete_has_blockers"],
            "note": "생성 row 삭제 되돌리기 미리보기입니다. 현재값이 생성 당시 값과 같고 연결 데이터가 없을 때만 삭제 적용할 수 있습니다.",
        }

    async def apply_admin_create_delete_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Delete a created row only when the create-delete preview is safe."""
        preview = await self.preview_admin_create_delete_rollback(session, change_log_id=change_log_id, reason=reason)
        if str(confirm_text or "").strip() != self.MASTER_CREATE_DELETE_CONFIRM_TEXT:
            preview.update({
                "status": "create_delete_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "deleted": False,
                "createDeleteReady": False,
                "wouldDelete": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_confirm_text_mismatch"],
                "note": "정확한 생성 row 삭제 확인 문구를 입력해야 DB에서 삭제할 수 있습니다.",
            })
            return preview
        if not preview.get("createDeleteReady"):
            preview.update({
                "status": "create_delete_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "deleted": False,
                "createDeleteReady": False,
                "wouldDelete": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_preview_not_safe_to_apply"],
            })
            return preview

        domain = str(preview.get("domain") or "")
        row_id = int(preview.get("id") or 0)
        master_row = await self._get_master_row(session, domain, row_id)
        if master_row is None:
            preview.update({"status": "target_already_deleted", "deleted": False, "writeBlocked": True})
            return preview

        before_values = {key: serialize_value(getattr(master_row, key, None)) for key in (preview.get("changedKeys") or [])}
        delete_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="create_delete",
            reason=(str(reason or "")[:500] or f"Delete created row from change log #{change_log_id}"),
            before_json=before_values,
            after_json={},
            rollback_json={"domain": domain, "id": row_id, "restoreLocked": True, "sourceChangeLogId": int(change_log_id)},
            applied=True,
        )
        await session.delete(master_row)
        session.add(delete_log)
        await session.commit()
        await session.refresh(delete_log)

        preview.update({
            "status": "created_row_deleted",
            "dryRun": False,
            "writeBlocked": False,
            "deleted": True,
            "createDeleteReady": False,
            "wouldDelete": False,
            "deleteChangeLogId": int(delete_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_enabled", "game_runtime_requires_reload"],
            "note": "create 이력으로 생성한 master-data row를 안전 검사 후 삭제했고 create_delete 이력을 저장했습니다. 삭제 복원은 별도 preview/apply 안전 검사를 통과해야 가능합니다.",
        })
        return preview

    async def preview_admin_create_delete_restore(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview restoring a row that was removed by create-delete apply.

        Restore is intentionally limited to create_delete logs produced by this admin
        flow. It only restores the exact deleted id when the row is still missing and
        the original code has not been reused.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_create_delete_restore_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        before_json = serialize_value(row.before_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "create_delete" or not domain or not row_id or not isinstance(before_json, dict):
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_create_delete"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if domain not in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS:
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_domain_locked",
                change_log_id=change_log_id,
                warnings=["create_delete_restore_domain_locked"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id) or rollback_json.get("sourceChangeLogId") is None:
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["create_delete_restore_rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )

        existing_row = await self._get_master_row(session, domain, int(row_id))
        id_conflict = existing_row is not None
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        model = config.get("model")
        code = str(before_json.get("code") or "").strip()
        code_conflict = False
        if model is not None and code:
            result = await session.execute(select(model).where(model.code == code))
            code_row = result.scalar_one_or_none()
            code_conflict = code_row is not None and int(getattr(code_row, "id", 0) or 0) != int(row_id)

        validation_errors: list[dict[str, Any]] = []
        normalized_restore: dict[str, Any] = {}
        if model is None:
            validation_errors.append({"key": "domain", "label": "도메인", "reason": "invalid_restore_domain"})
        else:
            column_map = self._master_create_column_map(model)
            field_defs = {str(field["key"]): field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")}
            for key, value in before_json.items():
                if key not in field_defs or key not in column_map:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "unknown_or_locked_restore_field"})
                    continue
                field_def = field_defs[key]
                if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "json_or_asset_restore_field_locked"})
                    continue
                normalized, issue = self._normalize_master_edit_value(column_map[key], value)
                if issue:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": issue})
                    continue
                normalized_restore[key] = normalized
            for field_def in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) or []:
                key = str(field_def.get("key") or "")
                if field_def.get("required") and key not in normalized_restore:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "reason": "required_restore_field_missing"})
            relation_errors = await self._validate_master_create_relations(session, domain, normalized_restore)
            validation_errors.extend(relation_errors)

        changes = await self._build_change_log_changes_with_relations(session, domain, {}, before_json)
        restore_conflict_count = int(bool(id_conflict)) + int(bool(code_conflict)) + len(validation_errors)
        restore_ready = not id_conflict and not code_conflict and len(validation_errors) == 0 and len(normalized_restore) > 0
        warnings: list[str] = []
        if id_conflict:
            warnings.append("create_delete_restore_id_conflict")
        if code_conflict:
            warnings.append("create_delete_restore_code_conflict")
        if validation_errors:
            warnings.append("create_delete_restore_validation_errors")
        return {
            "status": "create_delete_restore_preview_ready" if restore_ready else "create_delete_restore_blocked",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteRestoreReady": restore_ready,
            "wouldRestore": restore_ready,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "code": serialize_value(code),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "sourceCreateChangeLogId": int(rollback_json.get("sourceChangeLogId") or 0),
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "targetRowMissing": not id_conflict,
            "idConflict": id_conflict,
            "codeConflict": code_conflict,
            "validationErrors": validation_errors[:30],
            "validationErrorCount": len(validation_errors),
            "restoreConflictCount": restore_conflict_count,
            "normalizedRestoreDraft": {key: serialize_value(value) for key, value in normalized_restore.items()},
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
            "note": "create_delete 이력으로 삭제된 row 복원 미리보기입니다. 같은 id/code 충돌이 없고 생성 검증을 다시 통과해야만 복원 적용할 수 있습니다.",
        }

    async def apply_admin_create_delete_restore(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Restore a row deleted through create-delete apply after preview guards."""
        preview = await self.preview_admin_create_delete_restore(session, change_log_id=change_log_id, reason=reason)
        if str(confirm_text or "").strip() != self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT:
            preview.update({
                "status": "create_delete_restore_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "restored": False,
                "createDeleteRestoreReady": False,
                "wouldRestore": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_restore_confirm_text_mismatch"],
                "note": "정확한 생성 row 복원 확인 문구를 입력해야 DB에 다시 생성할 수 있습니다.",
            })
            return preview
        if not preview.get("createDeleteRestoreReady"):
            preview.update({
                "status": "create_delete_restore_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "restored": False,
                "createDeleteRestoreReady": False,
                "wouldRestore": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_not_safe_to_apply"],
            })
            return preview

        domain = str(preview.get("domain") or "")
        row_id = int(preview.get("id") or 0)
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        model = config.get("model")
        if model is None or row_id <= 0:
            preview.update({"status": "invalid_restore_target", "restored": False, "writeBlocked": True})
            return preview

        restore_values = dict(preview.get("normalizedRestoreDraft") or {})
        row = model(id=row_id, **restore_values)
        session.add(row)
        await session.flush()

        restore_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="create_delete_restore",
            reason=(str(reason or "")[:500] or f"Restore deleted created row from change log #{change_log_id}"),
            before_json={},
            after_json={key: serialize_value(value) for key, value in restore_values.items()},
            rollback_json={"domain": domain, "id": row_id, "deleteLocked": True, "sourceDeleteChangeLogId": int(change_log_id)},
            applied=True,
        )
        session.add(restore_log)
        await session.commit()
        await session.refresh(row)
        await session.refresh(restore_log)

        preview.update({
            "status": "created_row_restored",
            "dryRun": False,
            "writeBlocked": False,
            "restored": True,
            "createDeleteRestoreReady": False,
            "wouldRestore": False,
            "restoreChangeLogId": int(restore_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_redelete_not_enabled", "game_runtime_requires_reload"],
            "note": "create_delete 이력으로 삭제했던 master-data row를 같은 id로 복원했고 create_delete_restore 이력을 저장했습니다.",
        })
        return preview

    def _empty_create_delete_restore_preview(
        self,
        *,
        status: str,
        change_log_id: int,
        warnings: list[str],
        target_type: str | None = None,
        target_id: str | None = None,
        domain: str | None = None,
        row_id: int | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteRestoreReady": False,
            "wouldRestore": False,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "relationChangedKeys": [],
            "relationChangeCount": 0,
            "targetRowMissing": False,
            "idConflict": False,
            "codeConflict": False,
            "validationErrors": [],
            "validationErrorCount": 0,
            "restoreConflictCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    def _empty_create_delete_preview(
        self,
        *,
        status: str,
        change_log_id: int,
        warnings: list[str],
        target_type: str | None = None,
        target_id: str | None = None,
        domain: str | None = None,
        row_id: int | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteReady": False,
            "wouldDelete": False,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "currentMatchesCreateValues": False,
            "currentMismatches": [],
            "currentMismatchCount": 0,
            "dependencyChecks": [],
            "dependencyCheckCount": 0,
            "dependencyBlockerGuardCount": 0,
            "dependencyBlockerCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    async def _build_create_delete_dependency_checks(self, session: AsyncSession, domain: str, code: Any, row_id: int | None = None) -> list[dict[str, Any]]:
        code_text = "" if code is None else str(code).strip()

        async def check(label: str, model: Any, column_name: str, note: str) -> dict[str, Any]:
            column = getattr(model, column_name)
            count = await self._count_where(session, model, column == code_text)
            return {"label": label, "target": f"{model.__tablename__}.{column_name}", "count": count, "blocksDelete": count > 0, "note": note}

        if domain == "dropTableItems":
            return [
                {
                    "label": "id 기반 드랍 아이템",
                    "target": "drop_table_items.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "dropTableItems는 하위 연결이 없는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "skillLevels":
            return [
                {
                    "label": "id 기반 스킬 레벨",
                    "target": "skill_levels.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "skillLevels는 skills를 참조하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "enhancementLevels":
            return [
                {
                    "label": "id 기반 강화 단계",
                    "target": "enhancement_levels.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "enhancementLevels는 enhancementGroups를 참조하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "characterSkills":
            return [
                {
                    "label": "id 기반 캐릭터 스킬 연결",
                    "target": "character_skills.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "characterSkills는 캐릭터와 스킬을 연결하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]

        if not code_text:
            return [{"label": "code", "count": 1, "blocksDelete": True, "note": "삭제 대상 code를 찾을 수 없어 삭제를 막았습니다."}]

        if domain == "characters":
            return [
                await check("캐릭터 스킬 연결", CharacterSkill, "character_code", "characterSkills에서 사용 중이면 캐릭터 삭제를 막습니다."),
                await check("유저 캐릭터 스킬", UserCharacterSkill, "character_code", "유저 스킬 데이터에서 사용 중이면 삭제를 막습니다."),
                await check("유저 장비 슬롯", UserEquipmentSlot, "character_code", "유저 장비 슬롯에서 사용 중이면 삭제를 막습니다."),
                await check("유저 현재 캐릭터", UserProfile, "current_character_id", "유저 프로필의 현재 캐릭터로 사용 중이면 삭제를 막습니다."),
            ]
        if domain == "enhancementGroups":
            return [
                await check("강화 단계", EnhancementLevel, "group_code", "enhancementLevels에서 사용 중이면 강화 그룹 삭제를 막습니다."),
                await check("아이템 강화 그룹", ItemTemplate, "enhance_group_code", "itemTemplates에서 사용 중이면 강화 그룹 삭제를 막습니다."),
            ]
        if domain == "fieldZones":
            drop_table_count = await self._count_where(session, DropTable, DropTable.owner_type == "field", DropTable.owner_code == code_text)
            return [
                {
                    "label": "필드 드랍 테이블",
                    "target": "drop_tables.owner_type=field + owner_code",
                    "count": drop_table_count,
                    "blocksDelete": drop_table_count > 0,
                    "note": "dropTables에서 owner_type=field와 owner_code로 사용 중이면 필드 삭제를 막습니다.",
                },
            ]
        if domain == "bosses":
            drop_table_count = await self._count_where(session, DropTable, DropTable.owner_type == "boss", DropTable.owner_code == code_text)
            return [
                {
                    "label": "보스 드랍 테이블",
                    "target": "drop_tables.owner_type=boss + owner_code",
                    "count": drop_table_count,
                    "blocksDelete": drop_table_count > 0,
                    "note": "dropTables에서 owner_type=boss와 owner_code로 사용 중이면 보스 삭제를 막습니다.",
                },
            ]
        if domain == "skills":
            return [
                await check("스킬 레벨", SkillLevel, "skill_code", "skillLevels에서 사용 중이면 스킬 삭제를 막습니다."),
                await check("캐릭터 스킬 연결", CharacterSkill, "skill_code", "characterSkills에서 사용 중이면 스킬 삭제를 막습니다."),
                await check("유저 캐릭터 스킬", UserCharacterSkill, "skill_code", "유저 스킬 데이터에서 사용 중이면 삭제를 막습니다."),
            ]
        if domain == "dropTables":
            return [
                await check("드랍 아이템", DropTableItem, "drop_table_code", "dropTableItems에서 사용 중이면 드랍 테이블 삭제를 막습니다."),
            ]
        if domain == "itemTemplates":
            return [
                await check("드랍 아이템", DropTableItem, "item_template_code", "dropTableItems에서 사용 중이면 아이템 템플릿 삭제를 막습니다."),
                await check("유저 아이템 인스턴스", ItemInstance, "template_code", "유저 인벤토리에 생성된 아이템 인스턴스가 있으면 삭제를 막습니다."),
            ]
        return [{"label": "도메인 잠금", "count": 1, "blocksDelete": True, "note": "이 도메인은 생성 row 삭제 되돌리기 allow-list에 없습니다."}]

    def _empty_edit_preview(
        self,
        *,
        status: str,
        domain: str,
        domain_label: str,
        row_id: int,
        warnings: list[str],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "applyReady": False,
            "confirmTextRequired": self.MASTER_EDIT_APPLY_CONFIRM_TEXT,
            "allowedFields": [],
            "wouldBeValid": False,
            "domain": domain,
            "domainLabel": domain_label,
            "id": row_id,
            "title": "-",
            "reason": None,
            "diffCount": 0,
            "errorCount": 1,
            "unchangedCount": 0,
            "acceptedChanges": [],
            "rejectedChanges": [],
            "unchangedChanges": [],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
        }

    def _master_edit_column_map(self, row: Any) -> dict[str, Any]:
        mapper = sa_inspect(row.__class__)
        return {column_attr.key: column_attr.columns[0] for column_attr in mapper.mapper.column_attrs}

    def _master_edit_field_is_readonly(self, domain: str, key: str) -> bool:
        normalized = str(key or "").lower()
        if self._master_relation_edit_field_is_open(domain, normalized):
            return False
        return (
            normalized in {"id", "created_at", "updated_at", "code"}
            or normalized.endswith("_id")
            or normalized.endswith("_code")
            or normalized.endswith("_json")
        )

    def _master_edit_field_is_allowed(self, domain: str, key: str) -> bool:
        allowed = self.MASTER_EDIT_ALLOWED_FIELDS.get(domain) or set()
        return str(key or "") in allowed

    def _master_relation_edit_field_is_open(self, domain: str, key: str) -> bool:
        relation_fields = self.MASTER_RELATION_EDIT_FIELDS.get(str(domain or "")) or set()
        return str(key or "") in relation_fields

    async def _validate_master_relation_edit_value(
        self,
        session: AsyncSession,
        domain: str,
        key: str,
        value: Any,
        row: Any,
        draft: dict[str, Any] | None = None,
        column_map: dict[str, Any] | None = None,
    ) -> str | None:
        if not self._master_relation_edit_field_is_open(domain, key) and key not in (self.MASTER_COMBO_GUARDED_FIELDS.get(domain) or set()):
            return None
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return None
            exists = await self._exists_by_code(session, EnhancementGroup, value_text)
            return None if exists else "relation_target_not_found_enhancement_group"
        if domain == "dropTableItems" and key == "drop_table_code":
            if not value_text:
                return "relation_target_required_drop_table"
            exists = await self._exists_by_code(session, DropTable, value_text)
            return None if exists else "relation_target_not_found_drop_table"
        if domain == "dropTableItems" and key == "item_template_code":
            if not value_text:
                return "relation_target_required_item_template"
            exists = await self._exists_by_code(session, ItemTemplate, value_text)
            return None if exists else "relation_target_not_found_item_template"
        if domain == "dropTables" and key in {"owner_type", "owner_code"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["owner_type", "owner_code"])
            if proposed.get("issue"):
                return proposed["issue"]
            owner_type = str(proposed.get("owner_type") or "").strip()
            owner_code = str(proposed.get("owner_code") or "").strip()
            if owner_type not in {"boss", "field"}:
                return "invalid_owner_type"
            if not owner_code:
                return "owner_code_missing"
            model = Boss if owner_type == "boss" else FieldZone
            exists = await self._exists_by_code(session, model, owner_code)
            return None if exists else "owner_code_not_found_for_owner_type"
        if domain == "skillLevels" and key in {"skill_code", "level"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["skill_code", "level"])
            if proposed.get("issue"):
                return proposed["issue"]
            skill_code = str(proposed.get("skill_code") or "").strip()
            level = proposed.get("level")
            if not skill_code:
                return "relation_target_required_skill"
            if not await self._exists_by_code(session, Skill, skill_code):
                return "relation_target_not_found_skill"
            if level is None or int(level) < 0:
                return "invalid_skill_level"
            duplicate = await self._exists_duplicate_combo(session, SkillLevel, int(getattr(row, "id", 0) or 0), SkillLevel.skill_code == skill_code, SkillLevel.level == int(level))
            return "duplicate_skill_code_level" if duplicate else None
        if domain == "enhancementLevels" and key in {"group_code", "from_level"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["group_code", "from_level"])
            if proposed.get("issue"):
                return proposed["issue"]
            group_code = str(proposed.get("group_code") or "").strip()
            from_level = proposed.get("from_level")
            if not group_code:
                return "relation_target_required_enhancement_group"
            if not await self._exists_by_code(session, EnhancementGroup, group_code):
                return "relation_target_not_found_enhancement_group"
            if from_level is None or int(from_level) < 0:
                return "invalid_enhancement_from_level"
            duplicate = await self._exists_duplicate_combo(session, EnhancementLevel, int(getattr(row, "id", 0) or 0), EnhancementLevel.group_code == group_code, EnhancementLevel.from_level == int(from_level))
            return "duplicate_enhancement_group_from_level" if duplicate else None
        if domain == "characterSkills" and key in {"character_code", "skill_code"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["character_code", "skill_code"])
            if proposed.get("issue"):
                return proposed["issue"]
            character_code = str(proposed.get("character_code") or "").strip()
            skill_code = str(proposed.get("skill_code") or "").strip()
            if not character_code:
                return "relation_target_required_character"
            if not skill_code:
                return "relation_target_required_skill"
            if not await self._exists_by_code(session, Character, character_code):
                return "relation_target_not_found_character"
            if not await self._exists_by_code(session, Skill, skill_code):
                return "relation_target_not_found_skill"
            duplicate = await self._exists_duplicate_combo(session, CharacterSkill, int(getattr(row, "id", 0) or 0), CharacterSkill.character_code == character_code, CharacterSkill.skill_code == skill_code)
            return "duplicate_character_skill_pair" if duplicate else None
        return None

    async def _describe_master_relation_edit_value(
        self,
        session: AsyncSession,
        domain: str,
        key: str,
        value: Any,
        row: Any | None = None,
        draft: dict[str, Any] | None = None,
        column_map: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self._master_relation_edit_field_is_open(domain, key):
            return None
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return {"field": key, "targetDomain": "enhancementGroups", "targetCode": None, "targetLabel": "강화 그룹 없음"}
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTableItems" and key == "drop_table_code":
            target = await self._fetch_code_name(session, DropTable, value_text)
            return {"field": key, "targetDomain": "dropTables", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTableItems" and key == "item_template_code":
            target = await self._fetch_code_name(session, ItemTemplate, value_text)
            return {"field": key, "targetDomain": "itemTemplates", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTables" and key == "owner_type":
            return {"field": key, "targetDomain": "bosses" if value_text == "boss" else "fieldZones", "targetCode": value_text, "targetLabel": "보스" if value_text == "boss" else "필드"}
        if domain == "dropTables" and key == "owner_code":
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["owner_type", "owner_code"]) if row is not None else {"owner_type": "boss", "owner_code": value_text}
            owner_type = str(proposed.get("owner_type") or "").strip()
            target_domain = "bosses" if owner_type == "boss" else "fieldZones"
            target_model = Boss if owner_type == "boss" else FieldZone
            target = await self._fetch_code_name(session, target_model, value_text)
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "skillLevels" and key == "skill_code":
            target = await self._fetch_code_name(session, Skill, value_text)
            return {"field": key, "targetDomain": "skills", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "enhancementLevels" and key == "group_code":
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "characterSkills" and key == "character_code":
            target = await self._fetch_code_name(session, Character, value_text)
            return {"field": key, "targetDomain": "characters", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "characterSkills" and key == "skill_code":
            target = await self._fetch_code_name(session, Skill, value_text)
            return {"field": key, "targetDomain": "skills", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        return None

    def _build_proposed_combo_values(self, row: Any, column_map: dict[str, Any], draft: dict[str, Any], keys: list[str]) -> dict[str, Any]:
        proposed: dict[str, Any] = {}
        for key in keys:
            if key in draft:
                column = column_map.get(key)
                if column is None:
                    return {"issue": f"combo_field_unknown_{key}"}
                normalized, issue = self._normalize_master_edit_value(column, draft.get(key))
                if issue:
                    return {"issue": f"combo_field_invalid_{key}"}
                proposed[key] = normalized
            else:
                proposed[key] = getattr(row, key, None)
        return proposed

    async def _exists_by_code(self, session: AsyncSession, model: Any, code: str) -> bool:
        if not code:
            return False
        result = await session.execute(select(func.count()).select_from(model).where(model.code == code))
        return int(result.scalar_one() or 0) > 0

    async def _fetch_code_name(self, session: AsyncSession, model: Any, code: str) -> dict[str, Any] | None:
        if not code:
            return None
        result = await session.execute(select(model).where(model.code == code))
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {"code": getattr(row, "code", None), "name": getattr(row, "name", None) or getattr(row, "description", None)}

    async def _exists_duplicate_combo(self, session: AsyncSession, model: Any, current_id: int, *where_clauses: Any) -> bool:
        stmt = select(func.count()).select_from(model).where(*where_clauses)
        if current_id > 0:
            stmt = stmt.where(model.id != current_id)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0) > 0

    def _normalize_master_edit_value(self, column: Any, raw_value: Any) -> tuple[Any, str | None]:
        column_type = column.type
        nullable = bool(getattr(column, "nullable", False))
        if raw_value == "" or raw_value is None:
            if nullable:
                return None, None
            if isinstance(column_type, (String, Text)):
                return "", None
            return None, "empty_value_not_allowed"

        if isinstance(column_type, Boolean):
            if isinstance(raw_value, bool):
                return raw_value, None
            text = str(raw_value).strip().lower()
            if text in {"true", "1", "yes", "y", "on", "활성", "예"}:
                return True, None
            if text in {"false", "0", "no", "n", "off", "비활성", "아니오"}:
                return False, None
            return None, "invalid_boolean"

        if isinstance(column_type, Integer):
            try:
                text = str(raw_value).strip()
                if not text or any(ch in text for ch in [".", "e", "E"]):
                    return None, "invalid_integer"
                return int(text), None
            except (TypeError, ValueError):
                return None, "invalid_integer"

        if isinstance(column_type, Numeric):
            try:
                text = str(raw_value).strip().replace(",", "")
                if not text:
                    return None, "invalid_number"
                return float(text), None
            except (TypeError, ValueError):
                return None, "invalid_number"

        # For this dry-run stage, normal scalar fields are treated as text.
        text = str(raw_value)
        if text.startswith("data:"):
            return None, "asset_like_value_blocked"
        max_length = getattr(column_type, "length", None)
        if max_length and len(text) > int(max_length):
            return None, f"text_too_long_max_{max_length}"
        if len(text) > 2000:
            return None, "text_too_long_max_2000"
        return text, None

    @staticmethod
    def _master_edit_column_type(column: Any) -> str:
        column_type = column.type
        if isinstance(column_type, Boolean):
            return "boolean"
        if isinstance(column_type, Integer):
            return "integer"
        if isinstance(column_type, Numeric):
            return "number"
        if isinstance(column_type, Text):
            return "text"
        if isinstance(column_type, String):
            return "string"
        return column_type.__class__.__name__






    async def preview_master_data_create(
        self,
        session: AsyncSession,
        *,
        domain: str,
        draft: dict[str, Any],
        reason: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_create_preview(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                warnings=["domain_invalid"],
            )

        model = config["model"]
        column_map = self._master_create_column_map(model)
        blueprint_defs = [field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")]
        allowed_keys = {str(field["key"]) for field in blueprint_defs}
        safe_draft = draft if isinstance(draft, dict) else {}
        if len(safe_draft) > 100:
            safe_draft = dict(list(safe_draft.items())[:100])

        accepted_fields: list[dict[str, Any]] = []
        rejected_fields: list[dict[str, Any]] = []
        normalized_values: dict[str, Any] = {}
        warnings: list[str] = []
        field_defs = {str(field["key"]): field for field in blueprint_defs}

        for key, field_def in field_defs.items():
            column = column_map.get(key)
            if column is None:
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "reason": "column_not_found"})
                continue
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            raw_value = safe_draft.get(key, field_def.get("defaultValue"))
            normalized, issue = self._normalize_master_edit_value(column, raw_value)
            if issue:
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(raw_value), "reason": issue})
                continue
            normalized_values[key] = normalized

        for key, field_def in field_defs.items():
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            value = normalized_values.get(key)
            if field_def.get("required") and (value is None or (isinstance(value, str) and value.strip() == "")):
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "required_field_missing"})
            if field_def.get("unique") and value is not None and str(value).strip():
                duplicate = await self._exists_duplicate_unique_value(session, model, key, value)
                if duplicate:
                    rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": f"duplicate_unique_{key}"})

        for raw_key in safe_draft.keys():
            key = str(raw_key or "").strip()
            if not key or key in allowed_keys:
                continue
            rejected_fields.append({"key": key or raw_key, "label": self._humanize_field_name(key), "after": serialize_value(safe_draft.get(raw_key)), "reason": "unknown_or_locked_create_field"})

        relation_errors = await self._validate_master_create_relations(session, domain, normalized_values)
        rejected_fields.extend(relation_errors)

        rejected_key_reasons = {(str(item.get("key")), str(item.get("reason"))) for item in rejected_fields}
        for key, value in normalized_values.items():
            if any(item_key == key for item_key, _reason in rejected_key_reasons):
                continue
            field_def = field_defs.get(key) or {}
            relation = await self._describe_master_create_relation_value(session, domain, key, value, normalized_values)
            accepted_fields.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "after": serialize_value(value),
                "type": self._master_edit_column_type(column_map[key]),
                "required": bool(field_def.get("required")),
                "unique": bool(field_def.get("unique")),
                "relation": relation,
                "inputKind": field_def.get("inputKind") or "text",
            })

        error_count = len(rejected_fields)
        relation_count = sum(1 for field in accepted_fields if field.get("relation"))
        combo_labels = self._create_combo_guard_labels(domain)
        create_apply_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        create_apply_ready = create_apply_unlocked and error_count == 0 and len(accepted_fields) > 0
        return {
            "status": "previewed",
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "createApplyReady": create_apply_ready,
            "createApplyUnlocked": create_apply_unlocked,
            "insertLocked": not create_apply_unlocked,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "wouldBeValid": error_count == 0,
            "domain": domain,
            "domainLabel": config["label"],
            "reason": reason,
            "fieldCount": len(accepted_fields),
            "errorCount": error_count,
            "acceptedFields": accepted_fields,
            "rejectedFields": rejected_fields,
            "normalizedDraft": {key: serialize_value(value) for key, value in normalized_values.items()},
            "relationFieldCount": relation_count,
            "relationLabelsReturned": relation_count > 0,
            "comboGuardLabels": combo_labels,
            "comboGuardCount": len(combo_labels),
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": warnings,
            "note": "신규 row 생성 초안을 검증했습니다. characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills는 dev key와 확인 문구를 통과하면 실제 생성 적용이 가능합니다." if create_apply_unlocked else "신규 row 생성 초안을 검증했습니다. 이 도메인의 실제 insert는 아직 잠겨 있습니다.",
        }

    async def apply_master_data_create(
        self,
        session: AsyncSession,
        *,
        domain: str,
        draft: dict[str, Any],
        reason: str | None,
        confirm_text: str,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded new-row insert for a very small safe domain allow-list.

        The create path is deliberately narrower than edit apply. It only opens
        relation-light domains first, validates through the same preview function,
        requires the admin dev key at the route layer, requires an exact
        confirmation phrase, and records a create change log. Create rollback/delete
        is intentionally not opened in this step.
        """
        preview = await self.preview_master_data_create(
            session,
            domain=domain,
            draft=draft,
            reason=reason,
            dry_run=True,
        )

        if domain not in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS:
            preview.update({
                "status": "create_domain_locked",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "warnings": [*(preview.get("warnings") or []), "create_apply_domain_locked"],
                "note": "이 도메인의 실제 신규 row 생성은 아직 열지 않았습니다. 현재는 characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills만 제한적으로 생성 가능합니다.",
            })
            return preview

        if str(confirm_text or "").strip() != self.MASTER_CREATE_APPLY_CONFIRM_TEXT:
            preview.update({
                "status": "create_confirmation_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "warnings": [*(preview.get("warnings") or []), "create_confirm_text_mismatch"],
                "note": "정확한 생성 확인 문구를 입력해야 DB insert가 가능합니다.",
            })
            return preview

        if preview.get("status") != "previewed" or preview.get("errorCount") or not preview.get("acceptedFields"):
            preview.update({
                "status": "create_rejected",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "create_preview_not_valid_for_apply"],
                "note": "검증 오류가 있거나 생성 가능한 필드가 없어 DB에 insert하지 않았습니다.",
            })
            return preview

        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            preview.update({"status": "invalid_domain", "created": False, "writeBlocked": True})
            return preview

        model = config["model"]
        column_map = self._master_create_column_map(model)
        field_defs = {str(field["key"]): field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")}
        row_values: dict[str, Any] = {}
        after_values: dict[str, Any] = {}
        for field in preview.get("acceptedFields") or []:
            key = str(field.get("key") or "").strip()
            if not key or key not in field_defs or key not in column_map:
                continue
            field_def = field_defs[key]
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            raw_value = (draft or {}).get(key, field_def.get("defaultValue"))
            normalized, issue = self._normalize_master_edit_value(column_map[key], raw_value)
            if issue:
                continue
            row_values[key] = normalized
            after_values[key] = serialize_value(normalized)

        if not row_values:
            await session.rollback()
            preview.update({
                "status": "nothing_to_create",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "warnings": [*(preview.get("warnings") or []), "no_insertable_values"],
            })
            return preview

        row = model(**row_values)
        session.add(row)
        await session.flush()

        created_id = int(getattr(row, "id", 0) or 0)
        created_code = getattr(row, "code", None)
        created_title = getattr(row, "name", None) or created_code or f"#{created_id}"
        change_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(created_id),
            action="create",
            reason=str(reason or "")[:500] or None,
            before_json={},
            after_json=after_values,
            rollback_json={"domain": domain, "id": created_id, "delete": True},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(row)
        await session.refresh(change_log)

        return {
            **preview,
            "status": "created",
            "readOnly": False,
            "dryRun": False,
            "writeBlocked": False,
            "created": True,
            "createApplyReady": False,
            "wouldBeValid": True,
            "id": created_id,
            "code": serialize_value(created_code),
            "title": serialize_value(created_title),
            "createdRow": {"domain": domain, "id": created_id, "code": serialize_value(created_code), "title": serialize_value(created_title)},
            "changeLogId": int(change_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "note": "신규 master-data row를 DB에 생성했고 admin_change_logs에 create 이력을 저장했습니다. 제한 도메인 생성 row 삭제/복원은 별도 preview/apply 안전 검사를 통과해야 가능합니다.",
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_enabled", "game_runtime_requires_reload"],
        }

    def _empty_create_preview(self, *, status: str, domain: str, domain_label: str, warnings: list[str]) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "createApplyReady": False,
            "createApplyUnlocked": False,
            "insertLocked": True,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "wouldBeValid": False,
            "domain": domain,
            "domainLabel": domain_label,
            "fieldCount": 0,
            "errorCount": 1,
            "acceptedFields": [],
            "rejectedFields": [],
            "normalizedDraft": {},
            "relationFieldCount": 0,
            "relationLabelsReturned": False,
            "comboGuardLabels": [],
            "comboGuardCount": 0,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": warnings,
        }

    @staticmethod
    def _master_create_column_map(model: Any) -> dict[str, Any]:
        mapper = sa_inspect(model)
        return {column_attr.key: column_attr.columns[0] for column_attr in mapper.mapper.column_attrs}

    async def _exists_duplicate_unique_value(self, session: AsyncSession, model: Any, key: str, value: Any) -> bool:
        column = getattr(model, key, None)
        if column is None:
            return False
        result = await session.execute(select(func.count()).select_from(model).where(column == value))
        return int(result.scalar_one() or 0) > 0

    def _create_combo_guard_labels(self, domain: str) -> list[str]:
        labels: list[str] = []
        for field_def in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) or []:
            combo = field_def.get("comboGuard")
            if isinstance(combo, list) and combo:
                label = " + ".join(str(item) for item in combo)
                if label not in labels:
                    labels.append(label)
        return labels

    async def _validate_master_create_relations(self, session: AsyncSession, domain: str, values: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []

        def add(key: str, reason: str, value: Any = None) -> None:
            errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value if value is not None else values.get(key)), "reason": reason})

        if domain == "itemTemplates":
            code = str(values.get("enhance_group_code") or "").strip()
            if code and not await self._exists_by_code(session, EnhancementGroup, code):
                add("enhance_group_code", "relation_target_not_found_enhancement_group", code)
        elif domain == "dropTables":
            owner_type = str(values.get("owner_type") or "").strip()
            owner_code = str(values.get("owner_code") or "").strip()
            if owner_type not in {"boss", "field"}:
                add("owner_type", "invalid_owner_type", owner_type)
            if not owner_code:
                add("owner_code", "owner_code_missing", owner_code)
            elif owner_type in {"boss", "field"}:
                model = Boss if owner_type == "boss" else FieldZone
                if not await self._exists_by_code(session, model, owner_code):
                    add("owner_code", "owner_code_not_found_for_owner_type", owner_code)
        elif domain == "dropTableItems":
            drop_table_code = str(values.get("drop_table_code") or "").strip()
            item_template_code = str(values.get("item_template_code") or "").strip()
            rate = values.get("rate")
            min_quantity = values.get("min_quantity")
            max_quantity = values.get("max_quantity")
            if not drop_table_code or not await self._exists_by_code(session, DropTable, drop_table_code):
                add("drop_table_code", "relation_target_not_found_drop_table", drop_table_code)
            if not item_template_code or not await self._exists_by_code(session, ItemTemplate, item_template_code):
                add("item_template_code", "relation_target_not_found_item_template", item_template_code)
            if rate is None or float(rate) < 0:
                add("rate", "invalid_drop_rate", rate)
            if min_quantity is None or int(min_quantity) < 1:
                add("min_quantity", "invalid_min_quantity", min_quantity)
            if max_quantity is None or int(max_quantity) < 1:
                add("max_quantity", "invalid_max_quantity", max_quantity)
            if min_quantity is not None and max_quantity is not None and int(max_quantity) < int(min_quantity):
                add("max_quantity", "max_quantity_less_than_min_quantity", max_quantity)
        elif domain == "skillLevels":
            skill_code = str(values.get("skill_code") or "").strip()
            level = values.get("level")
            if not skill_code or not await self._exists_by_code(session, Skill, skill_code):
                add("skill_code", "relation_target_not_found_skill", skill_code)
            if level is None or int(level) < 0:
                add("level", "invalid_skill_level", level)
            elif skill_code and await self._exists_by_code(session, Skill, skill_code):
                duplicate = await self._exists_duplicate_combo(session, SkillLevel, 0, SkillLevel.skill_code == skill_code, SkillLevel.level == int(level))
                if duplicate:
                    add("level", "duplicate_skill_code_level", level)
        elif domain == "enhancementLevels":
            group_code = str(values.get("group_code") or "").strip()
            from_level = values.get("from_level")
            to_level = values.get("to_level")
            success_rate = values.get("success_rate")
            gold_cost = values.get("gold_cost")
            if not group_code or not await self._exists_by_code(session, EnhancementGroup, group_code):
                add("group_code", "relation_target_not_found_enhancement_group", group_code)
            if from_level is None or int(from_level) < 0:
                add("from_level", "invalid_enhancement_from_level", from_level)
            elif group_code and await self._exists_by_code(session, EnhancementGroup, group_code):
                duplicate = await self._exists_duplicate_combo(session, EnhancementLevel, 0, EnhancementLevel.group_code == group_code, EnhancementLevel.from_level == int(from_level))
                if duplicate:
                    add("from_level", "duplicate_enhancement_group_from_level", from_level)
            if to_level is None or int(to_level) <= int(from_level or 0):
                add("to_level", "invalid_enhancement_to_level", to_level)
            if success_rate is not None and float(success_rate) < 0:
                add("success_rate", "invalid_enhancement_success_rate", success_rate)
            if gold_cost is not None and float(gold_cost) < 0:
                add("gold_cost", "invalid_enhancement_gold_cost", gold_cost)
        elif domain == "characterSkills":
            character_code = str(values.get("character_code") or "").strip()
            skill_code = str(values.get("skill_code") or "").strip()
            sort_order = values.get("sort_order")
            if not character_code or not await self._exists_by_code(session, Character, character_code):
                add("character_code", "relation_target_not_found_character", character_code)
            if not skill_code or not await self._exists_by_code(session, Skill, skill_code):
                add("skill_code", "relation_target_not_found_skill", skill_code)
            if character_code and skill_code and await self._exists_by_code(session, Character, character_code) and await self._exists_by_code(session, Skill, skill_code):
                duplicate = await self._exists_duplicate_combo(session, CharacterSkill, 0, CharacterSkill.character_code == character_code, CharacterSkill.skill_code == skill_code)
                if duplicate:
                    add("skill_code", "duplicate_character_skill_pair", skill_code)
            if sort_order is not None and int(sort_order) < 0:
                add("sort_order", "invalid_character_skill_sort_order", sort_order)
        return errors

    async def _describe_master_create_relation_value(self, session: AsyncSession, domain: str, key: str, value: Any, values: dict[str, Any]) -> dict[str, Any] | None:
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return {"field": key, "targetDomain": "enhancementGroups", "targetCode": None, "targetLabel": "강화 그룹 없음", "displayText": "강화 그룹 없음"}
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        if domain == "dropTables" and key == "owner_type":
            label = "보스" if value_text == "boss" else "필드"
            target_domain = "bosses" if value_text == "boss" else "fieldZones"
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}"}
        if domain == "dropTables" and key == "owner_code":
            owner_type = str(values.get("owner_type") or "boss").strip()
            target_domain = "fieldZones" if owner_type == "field" else "bosses"
            target_model = FieldZone if owner_type == "field" else Boss
            target = await self._fetch_code_name(session, target_model, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        relation_targets = {
            ("dropTableItems", "drop_table_code"): (DropTable, "dropTables"),
            ("dropTableItems", "item_template_code"): (ItemTemplate, "itemTemplates"),
            ("skillLevels", "skill_code"): (Skill, "skills"),
            ("enhancementLevels", "group_code"): (EnhancementGroup, "enhancementGroups"),
            ("characterSkills", "character_code"): (Character, "characters"),
            ("characterSkills", "skill_code"): (Skill, "skills"),
        }
        target_def = relation_targets.get((domain, key))
        if target_def:
            model, target_domain = target_def
            target = await self._fetch_code_name(session, model, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        return None

    async def get_master_create_blueprint(self, session: AsyncSession, *, domain: str = "itemTemplates") -> dict[str, Any]:
        """Return a read-only create blueprint for a master-data domain.

        This prepares the future new-row UI without opening a DB insert path. It
        exposes required fields, safe defaults, relation candidates, and duplicate
        guard hints only. No database mutation is performed.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "createApplyReady": False,
                "createApplyUnlocked": False,
                "insertLocked": True,
                "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
                "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
                "createLifecycle": self._master_create_lifecycle_payload(domain),
                "domain": domain,
                "domainLabel": domain,
                "description": None,
                "fields": [],
                "requiredFields": [],
                "uniqueFields": [],
                "comboGuards": [],
                "defaultDraft": {},
                "relationOptionsReturned": False,
                "rawJsonReturned": False,
                "assetsReturned": False,
                "warnings": ["domain_invalid"],
                "note": "알 수 없는 도메인이라 신규 row 생성 설계를 만들 수 없습니다.",
            }

        blueprint_defs = list(self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain) or [])
        relation_options = await self._build_master_create_relation_options(session, domain)
        fields: list[dict[str, Any]] = []
        default_draft: dict[str, Any] = {}
        combo_guards: list[list[str]] = []
        relation_count = 0
        for field_def in blueprint_defs:
            key = str(field_def.get("key") or "")
            if not key:
                continue
            default_value = field_def.get("defaultValue")
            input_kind = str(field_def.get("inputKind") or "text")
            is_json_locked = input_kind == "json-readonly" or key.endswith("_json")
            if not is_json_locked:
                default_draft[key] = default_value
            combo_guard = field_def.get("comboGuard") if isinstance(field_def.get("comboGuard"), list) else None
            if combo_guard and combo_guard not in combo_guards:
                combo_guards.append(combo_guard)
            relation_payload = relation_options.get(key)
            if relation_payload:
                relation_count += 1
            fields.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "inputKind": input_kind,
                "required": bool(field_def.get("required")),
                "unique": bool(field_def.get("unique")),
                "nullable": bool(field_def.get("nullable")) if "nullable" in field_def else not bool(field_def.get("required")),
                "defaultValue": serialize_value(default_value),
                "targetDomain": field_def.get("targetDomain"),
                "dependsOn": field_def.get("dependsOn"),
                "comboGuard": combo_guard or [],
                "relation": relation_payload,
                "locked": True,
                "futureEditable": not is_json_locked,
                "lockedReason": field_def.get("lockedReason") or "현재 단계는 생성 설계 read-only입니다. 실제 insert API는 아직 열지 않았습니다.",
                "note": field_def.get("note"),
            })

        create_apply_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        return {
            "status": "loaded",
            "readOnly": True,
            "createApplyReady": False,
            "createApplyUnlocked": create_apply_unlocked,
            "insertLocked": not create_apply_unlocked,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "createLifecycle": self._master_create_lifecycle_payload(domain),
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "fieldCount": len(fields),
            "requiredFields": [field["key"] for field in fields if field.get("required")],
            "uniqueFields": [field["key"] for field in fields if field.get("unique")],
            "comboGuards": combo_guards,
            "defaultDraft": default_draft,
            "fields": fields,
            "relationOptionsReturned": relation_count > 0,
            "relationFieldCount": relation_count,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": [],
            "note": "신규 row 생성 설계 응답입니다. characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills는 dev key와 확인 문구를 통과하면 실제 생성 적용이 가능합니다." if create_apply_unlocked else "신규 row 생성 설계 응답입니다. 이 도메인의 실제 insert는 아직 잠겨 있습니다.",
        }

    async def _build_master_create_relation_options(self, session: AsyncSession, domain: str) -> dict[str, Any]:
        if domain == "itemTemplates":
            options = [{"value": "", "label": "없음 · 강화 그룹 연결 안 함", "current": True}]
            options.extend(await self._fetch_relation_code_options(session, EnhancementGroup, limit=300))
            return {"enhance_group_code": {"targetDomain": "enhancementGroups", "targetLabel": "강화 그룹", "nullable": True, "options": options}}
        if domain == "skillLevels":
            return {"skill_code": {"targetDomain": "skills", "targetLabel": "스킬", "nullable": False, "comboGuard": ["skill_code", "level"], "options": await self._fetch_relation_code_options(session, Skill, limit=300)}}
        if domain == "dropTables":
            return {
                "owner_code": {
                    "targetDomain": "bosses/fieldZones",
                    "targetLabel": "드랍 테이블 소유자 코드",
                    "nullable": False,
                    "dependsOn": "owner_type",
                    "optionGroups": {
                        "boss": await self._fetch_relation_code_options(session, Boss, limit=300),
                        "field": await self._fetch_relation_code_options(session, FieldZone, limit=300),
                    },
                    "options": await self._fetch_relation_code_options(session, Boss, limit=300),
                }
            }
        if domain == "dropTableItems":
            return {
                "drop_table_code": {"targetDomain": "dropTables", "targetLabel": "드랍 테이블", "nullable": False, "options": await self._fetch_relation_code_options(session, DropTable, limit=300)},
                "item_template_code": {"targetDomain": "itemTemplates", "targetLabel": "아이템 템플릿", "nullable": False, "options": await self._fetch_relation_code_options(session, ItemTemplate, limit=300)},
            }
        if domain == "enhancementLevels":
            return {"group_code": {"targetDomain": "enhancementGroups", "targetLabel": "강화 그룹", "nullable": False, "comboGuard": ["group_code", "from_level"], "options": await self._fetch_relation_code_options(session, EnhancementGroup, limit=300)}}
        if domain == "characterSkills":
            return {
                "character_code": {"targetDomain": "characters", "targetLabel": "캐릭터", "nullable": False, "comboGuard": ["character_code", "skill_code"], "options": await self._fetch_relation_code_options(session, Character, limit=200)},
                "skill_code": {"targetDomain": "skills", "targetLabel": "스킬", "nullable": False, "comboGuard": ["character_code", "skill_code"], "options": await self._fetch_relation_code_options(session, Skill, limit=300)},
            }
        return {}

    async def list_master_catalog_domains(self, session: AsyncSession) -> dict[str, Any]:
        """Return editable master-data domains for the admin page without row payloads."""
        domains: list[dict[str, Any]] = []
        for key, config in self.MASTER_CATALOG_DOMAINS.items():
            model = config["model"]
            total = await self._count(session, model)
            item: dict[str, Any] = {
                "key": key,
                "label": config["label"],
                "description": config.get("description"),
                "total": total,
                "searchableFields": list(config.get("search") or ()),
                "defaultSort": config.get("defaultSort") or "id_asc",
                "supportsEnabledFilter": hasattr(model, "is_enabled"),
                "rawJsonReturned": False,
                "assetsReturned": False,
            }
            if hasattr(model, "is_enabled"):
                enabled = await self._count(session, model, where_clause=(model.is_enabled.is_(True)))
                item["enabled"] = enabled
                item["disabled"] = max(0, int(total or 0) - int(enabled or 0))
            domains.append(item)
        return {
            "status": "loaded",
            "readOnly": True,
            "count": len(domains),
            "domains": domains,
            "defaultDomain": "itemTemplates",
            "rawJsonReturned": False,
            "assetsReturned": False,
            "note": "관리자 편집 화면 준비용 마스터 데이터 도메인 목록입니다. 아직 조회 전용입니다.",
        }

    async def list_master_catalog_rows(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        limit: int = 20,
        page: int = 1,
        query: str | None = None,
        enabled: str = "all",
        sort: str | None = None,
    ) -> dict[str, Any]:
        """List safe master-data rows for the admin page.

        This intentionally returns compact row cells instead of raw model JSON or
        inline assets. It is a bolder admin-page step, but still read-only.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "domain": domain,
                "domainLabel": domain,
                "count": 0,
                "total": 0,
                "limit": 0,
                "page": 1,
                "offset": 0,
                "totalPages": 1,
                "hasPrevPage": False,
                "hasNextPage": False,
                "filters": {"domain": domain, "page": 1, "limit": 0, "warnings": ["domain_invalid"]},
                "columns": [],
                "rows": [],
                "rawJsonReturned": False,
                "assetsReturned": False,
            }

        model = config["model"]
        warnings: list[str] = []
        safe_limit = max(1, min(int(limit or 20), 200))
        safe_page = max(1, int(page or 1))
        safe_offset = (safe_page - 1) * safe_limit
        safe_query = self._clean_filter_text(query)
        if safe_query and len(safe_query) > 80:
            safe_query = safe_query[:80]
            warnings.append("query_truncated_80")
        safe_enabled = enabled if enabled in {"all", "enabled", "disabled"} else "all"
        if safe_enabled != enabled:
            warnings.append("enabled_filter_fallback_all")
        safe_sort = sort or config.get("defaultSort") or "id_asc"
        if safe_sort not in {"code_asc", "name_asc", "updated_desc", "id_asc", "sort_asc"}:
            warnings.append("sort_fallback_default")
            safe_sort = config.get("defaultSort") or "id_asc"

        where_clauses = self._build_master_catalog_where_clauses(model, config, safe_query, safe_enabled, warnings)
        total_all = await self._count(session, model)
        total_filtered = await self._count_master_catalog_rows(session, model, where_clauses)

        stmt = select(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        stmt = stmt.order_by(*self._master_catalog_order_by(model, safe_sort)).offset(safe_offset).limit(safe_limit)
        result = await session.execute(stmt)
        rows = [self._serialize_master_catalog_row(domain, row) for row in result.scalars().all()]
        total_pages = max(1, (total_filtered + safe_limit - 1) // safe_limit)

        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "limit": safe_limit,
            "page": safe_page,
            "offset": safe_offset,
            "count": len(rows),
            "total": total_filtered,
            "totalPages": total_pages,
            "hasPrevPage": safe_page > 1,
            "hasNextPage": safe_page < total_pages,
            "totalAll": total_all,
            "filters": {
                "domain": domain,
                "query": safe_query,
                "enabled": safe_enabled,
                "sort": safe_sort,
                "page": safe_page,
                "limit": safe_limit,
                "warnings": warnings,
                "hasActiveFilters": bool(safe_query or safe_enabled != "all" or safe_page > 1),
            },
            "columns": self._master_catalog_columns(domain),
            "rows": rows,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "note": "관리자 마스터 데이터 카탈로그 조회 전용 목록입니다. 원본 JSON과 이미지 data URL은 내려주지 않습니다.",
        }


    async def get_master_catalog_detail(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        row_id: int,
    ) -> dict[str, Any]:
        """Return one sanitized master-data row for the read-only admin detail panel.

        This is intentionally not an edit endpoint. It returns normal scalar fields
        and sanitized JSON previews, but it hides inline image/data URL assets and
        still marks the response as read-only.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "domain": domain,
                "domainLabel": domain,
                "id": row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["domain_invalid"],
            }

        model = config["model"]
        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return {
                "status": "invalid_id",
                "readOnly": True,
                "domain": domain,
                "domainLabel": config["label"],
                "id": row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["id_invalid"],
            }

        result = await session.execute(select(model).where(model.id == safe_row_id))
        row = result.scalar_one_or_none()
        if row is None:
            return {
                "status": "not_found",
                "readOnly": True,
                "domain": domain,
                "domainLabel": config["label"],
                "id": safe_row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["row_not_found"],
            }

        scalar_fields, asset_fields = self._serialize_master_detail_scalar_fields(row)
        json_fields = self._serialize_master_detail_json_fields(row)
        relation_hints = await self._build_master_detail_relation_hints(session, domain, row)
        relation_edit_options = await self._build_master_relation_edit_options(session, domain, row)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        asset_hidden_count = sum(int(field.get("hiddenAssetCount") or 0) for field in json_fields)
        asset_hidden_count += sum(1 for field in asset_fields if field.get("hidden"))
        warnings: list[str] = []
        if asset_hidden_count:
            warnings.append("assets_hidden")
        if any(field.get("truncatedCount") for field in json_fields):
            warnings.append("json_preview_truncated")

        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "id": safe_row_id,
            "title": title,
            "fields": scalar_fields,
            "jsonFields": json_fields,
            "assetFields": asset_fields,
            "relationHints": relation_hints,
            "relationEditOptions": relation_edit_options,
            "rawJsonReturned": False,
            "sanitizedJsonReturned": True,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
            "note": "관리자 상세 보기 준비용 조회 전용 응답입니다. JSON은 안전하게 축약/마스킹되며 이미지 data URL은 내려주지 않습니다.",
        }

    async def get_master_catalog_relations(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        row_id: int,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Return compact related rows for one master-data record.

        This keeps the admin page read-only while making the catalog more useful:
        an admin can click one row and immediately see the connected drop tables,
        skills, enhancement rules, or item templates without exposing raw JSON or
        image assets.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_relation_response(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                row_id=row_id,
                warnings=["domain_invalid"],
            )

        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return self._empty_relation_response(
                status="invalid_id",
                domain=domain,
                domain_label=config["label"],
                row_id=row_id,
                warnings=["id_invalid"],
            )

        model = config["model"]
        result = await session.execute(select(model).where(model.id == safe_row_id))
        row = result.scalar_one_or_none()
        if row is None:
            return self._empty_relation_response(
                status="not_found",
                domain=domain,
                domain_label=config["label"],
                row_id=safe_row_id,
                warnings=["row_not_found"],
            )

        safe_limit = max(1, min(int(limit or 20), 80))
        groups = await self._build_master_relation_groups(session, domain, row, limit=safe_limit)
        total_related_rows = sum(int(group.get("count") or 0) for group in groups)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "id": safe_row_id,
            "title": title,
            "limitPerGroup": safe_limit,
            "groupCount": len(groups),
            "totalRelatedRows": total_related_rows,
            "groups": groups,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": [],
            "note": "관리자 상세 보기의 연결 항목 조회 전용 응답입니다. 관련 행은 축약된 목록으로만 내려갑니다.",
        }

    def _empty_relation_response(
        self,
        *,
        status: str,
        domain: str,
        domain_label: str,
        row_id: int,
        warnings: list[str],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "domain": domain,
            "domainLabel": domain_label,
            "id": row_id,
            "title": "-",
            "limitPerGroup": 0,
            "groupCount": 0,
            "totalRelatedRows": 0,
            "groups": [],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
        }

    async def _build_master_relation_groups(self, session: AsyncSession, domain: str, row: Any, *, limit: int) -> list[dict[str, Any]]:
        groups: list[dict[str, Any]] = []
        code = getattr(row, "code", None)

        if domain == "itemTemplates" and code:
            groups.append(await self._fetch_master_relation_group(session, "드랍 아이템", "dropTableItems", DropTableItem, limit, DropTableItem.item_template_code == code))
            group_code = getattr(row, "enhance_group_code", None)
            if group_code:
                groups.append(await self._fetch_master_relation_group(session, "강화 그룹", "enhancementGroups", EnhancementGroup, limit, EnhancementGroup.code == group_code))
                groups.append(await self._fetch_master_relation_group(session, "강화 단계", "enhancementLevels", EnhancementLevel, limit, EnhancementLevel.group_code == group_code))
        elif domain == "skills" and code:
            groups.append(await self._fetch_master_relation_group(session, "스킬 레벨", "skillLevels", SkillLevel, limit, SkillLevel.skill_code == code))
            groups.append(await self._fetch_master_relation_group(session, "캐릭터 스킬 연결", "characterSkills", CharacterSkill, limit, CharacterSkill.skill_code == code))
        elif domain == "skillLevels":
            skill_code = getattr(row, "skill_code", None)
            if skill_code:
                groups.append(await self._fetch_master_relation_group(session, "상위 스킬", "skills", Skill, limit, Skill.code == skill_code))
        elif domain == "characters" and code:
            groups.append(await self._fetch_master_relation_group(session, "캐릭터 스킬 연결", "characterSkills", CharacterSkill, limit, CharacterSkill.character_code == code))
        elif domain == "characterSkills":
            character_code = getattr(row, "character_code", None)
            skill_code = getattr(row, "skill_code", None)
            if character_code:
                groups.append(await self._fetch_master_relation_group(session, "캐릭터", "characters", Character, limit, Character.code == character_code))
            if skill_code:
                groups.append(await self._fetch_master_relation_group(session, "스킬", "skills", Skill, limit, Skill.code == skill_code))
        elif domain == "bosses" and code:
            groups.append(await self._fetch_master_relation_group(session, "보스 드랍 테이블", "dropTables", DropTable, limit, DropTable.owner_type == "boss", DropTable.owner_code == code))
        elif domain == "fieldZones" and code:
            groups.append(await self._fetch_master_relation_group(session, "필드 드랍 테이블", "dropTables", DropTable, limit, DropTable.owner_type == "field", DropTable.owner_code == code))
        elif domain == "dropTables" and code:
            owner_type = getattr(row, "owner_type", None)
            owner_code = getattr(row, "owner_code", None)
            if owner_type == "boss" and owner_code:
                groups.append(await self._fetch_master_relation_group(session, "대상 보스", "bosses", Boss, limit, Boss.code == owner_code))
            if owner_type == "field" and owner_code:
                groups.append(await self._fetch_master_relation_group(session, "대상 필드", "fieldZones", FieldZone, limit, FieldZone.code == owner_code))
            groups.append(await self._fetch_master_relation_group(session, "드랍 아이템", "dropTableItems", DropTableItem, limit, DropTableItem.drop_table_code == code))
        elif domain == "dropTableItems":
            drop_table_code = getattr(row, "drop_table_code", None)
            item_template_code = getattr(row, "item_template_code", None)
            if drop_table_code:
                groups.append(await self._fetch_master_relation_group(session, "드랍 테이블", "dropTables", DropTable, limit, DropTable.code == drop_table_code))
            if item_template_code:
                groups.append(await self._fetch_master_relation_group(session, "아이템 템플릿", "itemTemplates", ItemTemplate, limit, ItemTemplate.code == item_template_code))
        elif domain == "enhancementGroups" and code:
            groups.append(await self._fetch_master_relation_group(session, "강화 단계", "enhancementLevels", EnhancementLevel, limit, EnhancementLevel.group_code == code))
            groups.append(await self._fetch_master_relation_group(session, "연결 아이템", "itemTemplates", ItemTemplate, limit, ItemTemplate.enhance_group_code == code))
        elif domain == "enhancementLevels":
            group_code = getattr(row, "group_code", None)
            if group_code:
                groups.append(await self._fetch_master_relation_group(session, "강화 그룹", "enhancementGroups", EnhancementGroup, limit, EnhancementGroup.code == group_code))
                groups.append(await self._fetch_master_relation_group(session, "연결 아이템", "itemTemplates", ItemTemplate, limit, ItemTemplate.enhance_group_code == group_code))

        return [group for group in groups if group.get("count") or group.get("rows")]

    async def _fetch_master_relation_group(
        self,
        session: AsyncSession,
        label: str,
        domain: str,
        model: Any,
        limit: int,
        *where_clauses: Any,
    ) -> dict[str, Any]:
        where_list = [clause for clause in where_clauses if clause is not None]
        total = await self._count_master_catalog_rows(session, model, where_list)
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        sort = config.get("defaultSort") or "id_asc"
        stmt = select(model)
        if where_list:
            stmt = stmt.where(*where_list)
        stmt = stmt.order_by(*self._master_catalog_order_by(model, sort)).limit(limit)
        result = await session.execute(stmt)
        rows = [self._serialize_master_relation_row(domain, row) for row in result.scalars().all()]
        return {
            "label": label,
            "domain": domain,
            "domainLabel": config.get("label") or domain,
            "count": total,
            "shown": len(rows),
            "limited": total > len(rows),
            "columns": self._master_catalog_columns(domain),
            "rows": rows,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }

    def _serialize_master_relation_row(self, domain: str, row: Any) -> dict[str, Any]:
        catalog_row = self._serialize_master_catalog_row(domain, row)
        cells = catalog_row.get("cells") or {}
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{getattr(row, 'id', '-') }"
        return {
            "id": getattr(row, "id", None),
            "domain": domain,
            "title": title,
            "cells": cells,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }









    def _clean_admin_change_log_filters(
        self,
        *,
        target_type: Any = None,
        target_id: Any = None,
        action: Any = None,
        changed_key: Any = None,
        applied: Any = None,
        sort: Any = "created_desc",
    ) -> dict[str, Any]:
        safe_sort = str(sort or "created_desc").strip()
        if safe_sort not in {"created_desc", "created_asc", "target_asc", "action_asc"}:
            safe_sort = "created_desc"
        safe_changed_key = self._clean_filter_text(changed_key)
        if safe_changed_key and not self._is_safe_admin_change_key(safe_changed_key):
            safe_changed_key = None

        clean_applied: bool | None
        if applied is None or applied == "":
            clean_applied = None
        elif isinstance(applied, bool):
            clean_applied = applied
        else:
            clean_applied = str(applied).strip().lower() in {"true", "1", "yes", "applied"}

        safe_action = self._clean_filter_text(action)
        if safe_action and safe_action not in self.ADMIN_CHANGE_LOG_ACTION_FILTERS:
            safe_action = None

        active = {
            "targetType": self._clean_filter_text(target_type),
            "targetId": self._clean_filter_text(target_id),
            "action": safe_action,
            "changedKey": safe_changed_key,
            "applied": clean_applied,
            "sort": safe_sort,
            "allowedActions": sorted(self.ADMIN_CHANGE_LOG_ACTION_FILTERS),
        }
        active["hasActiveFilters"] = any(
            active.get(key) not in (None, "") for key in ("targetType", "targetId", "action", "changedKey", "applied")
        )
        return active

    def _build_admin_change_log_where_clauses(self, filters: dict[str, Any]) -> list[Any]:
        clauses: list[Any] = []
        if filters.get("targetType"):
            clauses.append(AdminChangeLog.target_type == filters["targetType"])
        if filters.get("targetId"):
            clauses.append(AdminChangeLog.target_id == filters["targetId"])
        if filters.get("action"):
            clauses.append(AdminChangeLog.action == filters["action"])
        if filters.get("applied") is not None:
            clauses.append(AdminChangeLog.applied.is_(bool(filters["applied"])))
        if filters.get("changedKey"):
            key = str(filters["changedKey"])
            clauses.append(or_(AdminChangeLog.before_json.op("?")(key), AdminChangeLog.after_json.op("?")(key)))
        return clauses

    def _admin_change_log_order_by(self, sort: str) -> tuple[Any, ...]:
        if sort == "created_asc":
            return (AdminChangeLog.created_at.asc(), AdminChangeLog.id.asc())
        if sort == "target_asc":
            return (AdminChangeLog.target_type.asc(), AdminChangeLog.target_id.asc(), AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())
        if sort == "action_asc":
            return (AdminChangeLog.action.asc(), AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())
        return (AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())

    @staticmethod
    def _is_safe_admin_change_key(value: str) -> bool:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        return bool(value) and all(ch in allowed for ch in value)

    async def _get_admin_change_log(self, session: AsyncSession, change_log_id: int) -> AdminChangeLog | None:
        safe_id = int(change_log_id or 0)
        if safe_id <= 0:
            return None
        result = await session.execute(select(AdminChangeLog).where(AdminChangeLog.id == safe_id))
        return result.scalar_one_or_none()

    def _empty_change_log_detail(self, *, status: str, change_log_id: int, warnings: list[str]) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "id": int(change_log_id or 0),
            "changes": [],
            "changedKeys": [],
            "changedKeyCount": 0,
            "rollback": {"available": False, "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT},
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    def _empty_rollback_preview(
        self,
        *,
        status: str,
        change_log_id: int,
        warnings: list[str],
        target_type: str | None = None,
        target_id: str | None = None,
        domain: str | None = None,
        row_id: int | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "rollbackReady": False,
            "wouldRollback": False,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "errorCount": 1,
            "currentMatchesAfter": False,
            "currentMismatches": [],
            "currentMismatchCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    async def _serialize_admin_change_log_detail(self, session: AsyncSession, row: AdminChangeLog) -> dict[str, Any]:
        base = self._serialize_admin_change_log(row)
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        domain, _ = self._extract_master_change_target(row)
        changes = await self._build_change_log_changes_with_relations(session, domain, before_json, after_json)
        relation_count = sum(1 for change in changes if change.get("relation"))
        base.update({
            "status": "loaded",
            "readOnly": True,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "changedKeyCount": len(changes),
            "relationChangeCount": relation_count,
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationLabelsReturned": relation_count > 0,
            "rawBeforeAfterReturned": False,
            "scalarChangesReturned": True,
            "rollbackRawJsonReturned": False,
            "warnings": [],
        })
        return base

    def _build_change_log_changes(self, before_json: Any, after_json: Any) -> list[dict[str, Any]]:
        before_dict = before_json if isinstance(before_json, dict) else {}
        after_dict = after_json if isinstance(after_json, dict) else {}
        keys = sorted(set(before_dict.keys()) | set(after_dict.keys()))
        return [
            {
                "key": key,
                "label": self._humanize_field_name(key),
                "before": serialize_value(before_dict.get(key)),
                "after": serialize_value(after_dict.get(key)),
            }
            for key in keys
        ]

    async def _build_change_log_changes_with_relations(self, session: AsyncSession, domain: str | None, before_json: Any, after_json: Any) -> list[dict[str, Any]]:
        changes = self._build_change_log_changes(before_json, after_json)
        if not domain:
            return changes
        before_dict = before_json if isinstance(before_json, dict) else {}
        after_dict = after_json if isinstance(after_json, dict) else {}
        for change in changes:
            key = str(change.get("key") or "")
            if not self._master_relation_edit_field_is_open(domain, key):
                continue
            before_info = await self._describe_change_log_relation_value(session, domain, key, change.get("before"), before_dict)
            after_info = await self._describe_change_log_relation_value(session, domain, key, change.get("after"), after_dict)
            change["relation"] = {
                "field": key,
                "before": before_info,
                "after": after_info,
                "targetDomain": (after_info or before_info or {}).get("targetDomain"),
                "targetCode": (after_info or before_info or {}).get("targetCode"),
                "targetLabel": (after_info or before_info or {}).get("targetLabel"),
            }
        return changes

    async def _enrich_rollback_mismatches_with_relations(
        self,
        session: AsyncSession,
        domain: str | None,
        mismatches: list[dict[str, Any]],
        current_values: dict[str, Any],
        after_json: Any,
        before_json: Any,
    ) -> list[dict[str, Any]]:
        if not domain or not mismatches:
            return mismatches
        after_context = after_json if isinstance(after_json, dict) else {}
        before_context = before_json if isinstance(before_json, dict) else {}
        current_context = {**after_context, **current_values}
        enriched: list[dict[str, Any]] = []
        for item in mismatches:
            key = str(item.get("key") or "")
            if self._master_relation_edit_field_is_open(domain, key):
                item = dict(item)
                item["relation"] = {
                    "field": key,
                    "current": await self._describe_change_log_relation_value(session, domain, key, item.get("current"), current_context),
                    "expectedAfter": await self._describe_change_log_relation_value(session, domain, key, item.get("expectedAfter"), after_context),
                    "rollbackTo": await self._describe_change_log_relation_value(session, domain, key, item.get("rollbackTo"), before_context),
                }
            enriched.append(item)
        return enriched

    async def _describe_change_log_relation_value(self, session: AsyncSession, domain: str, key: str, value: Any, context: dict[str, Any]) -> dict[str, Any] | None:
        if not self._master_relation_edit_field_is_open(domain, key):
            return None
        value_text = "" if value is None else str(value).strip()

        async def build(target_domain: str, model: Any | None, label_when_empty: str | None = None) -> dict[str, Any]:
            if not value_text:
                label = label_when_empty or "값 없음"
                return {"field": key, "targetDomain": target_domain, "targetCode": None, "targetLabel": label, "displayText": label}
            target = await self._fetch_code_name(session, model, value_text) if model is not None else None
            label = target.get("name") if target else None
            display = f"{value_text} · {label}" if label and label != value_text else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label or value_text, "displayText": display}

        if domain == "itemTemplates" and key == "enhance_group_code":
            return await build("enhancementGroups", EnhancementGroup, "강화 그룹 없음")
        if domain == "dropTableItems" and key == "drop_table_code":
            return await build("dropTables", DropTable)
        if domain == "dropTableItems" and key == "item_template_code":
            return await build("itemTemplates", ItemTemplate)
        if domain == "dropTables" and key == "owner_type":
            label = "보스" if value_text == "boss" else ("필드" if value_text == "field" else value_text or "값 없음")
            target_domain = "bosses" if value_text == "boss" else ("fieldZones" if value_text == "field" else "bosses/fieldZones")
            display = f"{value_text} · {label}" if value_text and label != value_text else label
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text or None, "targetLabel": label, "displayText": display}
        if domain == "dropTables" and key == "owner_code":
            owner_type = str((context or {}).get("owner_type") or "boss").strip()
            if owner_type == "field":
                return await build("fieldZones", FieldZone)
            return await build("bosses", Boss)
        if domain == "skillLevels" and key == "skill_code":
            return await build("skills", Skill)
        if domain == "enhancementLevels" and key == "group_code":
            return await build("enhancementGroups", EnhancementGroup)
        if domain == "characterSkills" and key == "character_code":
            return await build("characters", Character)
        if domain == "characterSkills" and key == "skill_code":
            return await build("skills", Skill)
        return None

    def _extract_master_change_target(self, row: AdminChangeLog) -> tuple[str | None, int | None]:
        target_type = str(getattr(row, "target_type", "") or "")
        if not target_type.startswith("master_data."):
            return None, None
        domain = target_type.split(".", 1)[1]
        if domain not in self.MASTER_CATALOG_DOMAINS:
            return None, None
        try:
            row_id = int(getattr(row, "target_id", 0) or 0)
        except (TypeError, ValueError):
            row_id = 0
        return domain, row_id if row_id > 0 else None

    async def _get_master_row(self, session: AsyncSession, domain: str, row_id: int) -> Any | None:
        config = self.MASTER_CATALOG_DOMAINS.get(str(domain or ""))
        safe_row_id = int(row_id or 0)
        if not config or safe_row_id <= 0:
            return None
        result = await session.execute(select(config["model"]).where(config["model"].id == safe_row_id))
        return result.scalar_one_or_none()

    def _current_master_values(self, row: Any, keys: list[str]) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for key in keys:
            values[key] = serialize_value(getattr(row, key, None))
        return values

    async def _count_admin_change_logs(self, session: AsyncSession, where_clauses: list[Any]) -> int:
        stmt = select(func.count()).select_from(AdminChangeLog)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    def _serialize_admin_change_log(self, row: AdminChangeLog) -> dict[str, Any]:
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        changed_keys = sorted(set(before_json.keys()) | set(after_json.keys())) if isinstance(before_json, dict) and isinstance(after_json, dict) else []
        domain, _ = self._extract_master_change_target(row)
        relation_changed_keys = [key for key in changed_keys if domain and self._master_relation_edit_field_is_open(domain, key)]
        return {
            "id": row.id,
            "adminUserId": row.admin_user_id,
            "targetType": row.target_type,
            "targetId": row.target_id,
            "action": row.action,
            "reason": row.reason,
            "applied": row.applied,
            "changedKeys": changed_keys,
            "changedKeyCount": len(changed_keys),
            "relationChangedKeys": relation_changed_keys,
            "relationChangeCount": len(relation_changed_keys),
            "createdAt": serialize_value(row.created_at),
            "updatedAt": serialize_value(row.updated_at),
            "rawBeforeAfterReturned": False,
        }


    @staticmethod
    def _clean_filter_text(value: Any) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _is_safe_slot_key(value: str) -> bool:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        return all(ch in allowed for ch in value)


    def _build_master_catalog_where_clauses(
        self,
        model: Any,
        config: dict[str, Any],
        query: str | None,
        enabled: str,
        warnings: list[str],
    ) -> list[Any]:
        clauses: list[Any] = []
        if query:
            search_clauses = []
            for field in config.get("search") or ():
                column = getattr(model, field, None)
                if column is not None:
                    search_clauses.append(column.ilike(f"%{query}%"))
            if search_clauses:
                clauses.append(or_(*search_clauses))
            else:
                warnings.append("query_ignored_no_searchable_fields")
        if enabled != "all":
            if hasattr(model, "is_enabled"):
                clauses.append(model.is_enabled.is_(enabled == "enabled"))
            else:
                warnings.append("enabled_filter_ignored_for_domain")
        return clauses

    def _master_catalog_order_by(self, model: Any, sort: str) -> tuple[Any, ...]:
        if sort == "code_asc" and hasattr(model, "code"):
            return (model.code.asc(), model.id.asc())
        if sort == "name_asc" and hasattr(model, "name"):
            return (model.name.asc(), model.id.asc())
        if sort == "updated_desc" and hasattr(model, "updated_at"):
            return (model.updated_at.desc(), model.id.asc())
        if sort == "sort_asc" and hasattr(model, "sort_order"):
            return (model.sort_order.asc(), model.id.asc())
        return (model.id.asc(),)

    async def _count_master_catalog_rows(self, session: AsyncSession, model: Any, where_clauses: list[Any]) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    def _master_catalog_columns(self, domain: str) -> list[dict[str, str]]:
        column_map: dict[str, list[tuple[str, str]]] = {
            "itemTemplates": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("itemType", "타입"), ("grade", "등급"), ("equipSlot", "장착칸"), ("stackable", "중첩"), ("enhanceGroupCode", "강화그룹"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "skills": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("slotKey", "슬롯"), ("procRate", "발동"), ("cooldownSeconds", "쿨타임"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "skillLevels": [("id", "ID"), ("skillCode", "스킬"), ("level", "레벨"), ("damageMultiplier", "배율"), ("procRateBonus", "발동+"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "bosses": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("tier", "티어"), ("bossType", "타입"), ("hp", "HP"), ("cooldownSeconds", "쿨타임"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "fieldZones": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("sortOrder", "순서"), ("enemyHp", "HP"), ("goldReward", "골드"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "characters": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "dropTables": [("id", "ID"), ("code", "코드"), ("ownerType", "대상"), ("ownerCode", "대상코드"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "dropTableItems": [("id", "ID"), ("dropTableCode", "테이블"), ("itemTemplateCode", "아이템"), ("rate", "확률"), ("minQuantity", "최소"), ("maxQuantity", "최대"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "enhancementGroups": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("maxLevel", "최대"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "enhancementLevels": [("id", "ID"), ("groupCode", "그룹"), ("fromLevel", "시작"), ("toLevel", "도착"), ("successRate", "확률"), ("goldCost", "비용"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "characterSkills": [("id", "ID"), ("characterCode", "캐릭터"), ("skillCode", "스킬"), ("sortOrder", "순서"), ("isDefault", "기본"), ("updatedAt", "수정")],
        }
        return [{"key": key, "label": label} for key, label in column_map.get(domain, [("id", "ID"), ("updatedAt", "수정")])]

    def _serialize_master_catalog_row(self, domain: str, row: Any) -> dict[str, Any]:
        cells: dict[str, Any]
        if domain == "itemTemplates":
            cells = {
                "id": row.id,
                "code": row.code,
                "name": row.name,
                "itemType": row.item_type,
                "grade": row.grade,
                "equipSlot": row.equip_slot,
                "stackable": row.stackable,
                "enhanceGroupCode": row.enhance_group_code,
                "jsonKeys": self._join_json_keys({"baseStats": row.base_stats_json, "options": row.options_json}),
                "updatedAt": serialize_value(row.updated_at),
            }
        elif domain == "skills":
            cells = {"id": row.id, "code": row.code, "name": row.name, "slotKey": row.slot_key, "procRate": serialize_value(row.proc_rate), "cooldownSeconds": row.cooldown_seconds, "jsonKeys": self._join_json_keys({"options": row.options_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "skillLevels":
            cells = {"id": row.id, "skillCode": row.skill_code, "level": row.level, "damageMultiplier": serialize_value(row.damage_multiplier), "procRateBonus": serialize_value(row.proc_rate_bonus), "jsonKeys": self._join_json_keys({"options": row.options_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "bosses":
            cells = {"id": row.id, "code": row.code, "name": row.name, "tier": row.tier, "bossType": row.boss_type, "hp": serialize_value(row.hp), "cooldownSeconds": row.cooldown_seconds, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"summonRules": row.summon_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "fieldZones":
            cells = {"id": row.id, "code": row.code, "name": row.name, "sortOrder": row.sort_order, "enemyHp": serialize_value(row.enemy_hp), "goldReward": serialize_value(row.gold_reward), "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"entryRules": row.entry_rules_json, "farmRules": row.farm_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "characters":
            cells = {"id": row.id, "code": row.code, "name": row.name, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"meta": row.meta_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "dropTables":
            cells = {"id": row.id, "code": row.code, "ownerType": row.owner_type, "ownerCode": row.owner_code, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"rules": row.rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "dropTableItems":
            cells = {"id": row.id, "dropTableCode": row.drop_table_code, "itemTemplateCode": row.item_template_code, "rate": serialize_value(row.rate), "minQuantity": row.min_quantity, "maxQuantity": row.max_quantity, "jsonKeys": self._join_json_keys({"conditions": row.conditions_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "enhancementGroups":
            cells = {"id": row.id, "code": row.code, "name": row.name, "maxLevel": row.max_level, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"rules": row.rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "enhancementLevels":
            cells = {"id": row.id, "groupCode": row.group_code, "fromLevel": row.from_level, "toLevel": row.to_level, "successRate": serialize_value(row.success_rate), "goldCost": serialize_value(row.gold_cost), "jsonKeys": self._join_json_keys({"materialRules": row.material_rules_json, "resultStats": row.result_stats_json, "failRules": row.fail_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "characterSkills":
            cells = {"id": row.id, "characterCode": row.character_code, "skillCode": row.skill_code, "sortOrder": row.sort_order, "isDefault": row.is_default, "updatedAt": serialize_value(row.updated_at)}
        else:
            cells = {"id": getattr(row, "id", None), "updatedAt": serialize_value(getattr(row, "updated_at", None))}

        return {
            "id": getattr(row, "id", None),
            "domain": domain,
            "cells": cells,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }

    @staticmethod
    def _join_json_keys(named_json_values: dict[str, Any]) -> str:
        parts: list[str] = []
        for label, value in named_json_values.items():
            if isinstance(value, dict) and value:
                parts.append(f"{label}:" + ",".join(sorted(map(str, value.keys()))[:8]))
        return " | ".join(parts) if parts else "-"


    def _serialize_master_detail_scalar_fields(self, row: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        fields: list[dict[str, Any]] = []
        asset_fields: list[dict[str, Any]] = []
        mapper = sa_inspect(row.__class__)
        for column_attr in mapper.mapper.column_attrs:
            key = column_attr.key
            value = getattr(row, key, None)
            if key.endswith("_json"):
                continue
            if self._is_asset_field(key):
                asset_fields.append(self._serialize_asset_field(key, value))
                continue
            fields.append({"key": key, "label": self._humanize_field_name(key), "value": self._safe_detail_scalar_value(value)})
        return fields, asset_fields

    def _serialize_master_detail_json_fields(self, row: Any) -> list[dict[str, Any]]:
        json_fields: list[dict[str, Any]] = []
        mapper = sa_inspect(row.__class__)
        for column_attr in mapper.mapper.column_attrs:
            key = column_attr.key
            if not key.endswith("_json"):
                continue
            raw_value = serialize_value(getattr(row, key, None)) or {}
            preview, stats = self._sanitize_json_preview(raw_value)
            json_fields.append(
                {
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "keys": sorted(map(str, raw_value.keys()))[:30] if isinstance(raw_value, dict) else [],
                    "preview": preview,
                    "hiddenAssetCount": stats["hiddenAssetCount"],
                    "truncatedCount": stats["truncatedCount"],
                    "maxDepthHit": stats["maxDepthHit"],
                    "rawJsonReturned": False,
                    "sanitizedPreview": True,
                }
            )
        return json_fields

    async def _build_master_detail_relation_hints(self, session: AsyncSession, domain: str, row: Any) -> list[dict[str, Any]]:
        hints: list[dict[str, Any]] = []
        code = getattr(row, "code", None)
        if domain == "itemTemplates" and code:
            hints.append({"label": "드랍 아이템 연결", "value": await self._count_where(session, DropTableItem, DropTableItem.item_template_code == code)})
            group_code = getattr(row, "enhance_group_code", None)
            if group_code:
                hints.append({"label": "강화 그룹", "value": group_code})
                hints.append({"label": "강화 단계 수", "value": await self._count_where(session, EnhancementLevel, EnhancementLevel.group_code == group_code)})
        elif domain == "skills" and code:
            hints.append({"label": "스킬 레벨 수", "value": await self._count_where(session, SkillLevel, SkillLevel.skill_code == code)})
            hints.append({"label": "캐릭터 연결 수", "value": await self._count_where(session, CharacterSkill, CharacterSkill.skill_code == code)})
        elif domain == "skillLevels":
            hints.append({"label": "스킬 코드", "value": getattr(row, "skill_code", None)})
        elif domain == "characters" and code:
            hints.append({"label": "스킬 연결 수", "value": await self._count_where(session, CharacterSkill, CharacterSkill.character_code == code)})
        elif domain == "bosses" and code:
            hints.append({"label": "보스 드랍 테이블 수", "value": await self._count_where(session, DropTable, DropTable.owner_type == "boss", DropTable.owner_code == code)})
        elif domain == "fieldZones" and code:
            hints.append({"label": "필드 드랍 테이블 수", "value": await self._count_where(session, DropTable, DropTable.owner_type == "field", DropTable.owner_code == code)})
        elif domain == "dropTables" and code:
            hints.append({"label": "드랍 아이템 수", "value": await self._count_where(session, DropTableItem, DropTableItem.drop_table_code == code)})
            hints.append({"label": "대상", "value": f"{getattr(row, 'owner_type', '-')}/{getattr(row, 'owner_code', '-')}"})
        elif domain == "dropTableItems":
            hints.append({"label": "드랍 테이블", "value": getattr(row, "drop_table_code", None)})
            hints.append({"label": "아이템 코드", "value": getattr(row, "item_template_code", None)})
        elif domain == "enhancementGroups" and code:
            hints.append({"label": "강화 단계 수", "value": await self._count_where(session, EnhancementLevel, EnhancementLevel.group_code == code)})
            hints.append({"label": "아이템 연결 수", "value": await self._count_where(session, ItemTemplate, ItemTemplate.enhance_group_code == code)})
        elif domain == "enhancementLevels":
            hints.append({"label": "강화 그룹", "value": getattr(row, "group_code", None)})
        elif domain == "characterSkills":
            hints.append({"label": "캐릭터", "value": getattr(row, "character_code", None)})
            hints.append({"label": "스킬", "value": getattr(row, "skill_code", None)})
        return hints

    async def _build_master_relation_edit_options(self, session: AsyncSession, domain: str, row: Any) -> list[dict[str, Any]]:
        if domain == "itemTemplates":
            current = getattr(row, "enhance_group_code", None)
            options = [{"value": "", "label": "없음 · 강화 그룹 연결 안 함", "current": not bool(current)}]
            options.extend(await self._fetch_relation_code_options(session, EnhancementGroup, current_code=current, limit=200))
            return [{
                "field": "enhance_group_code",
                "kind": "relation-select",
                "targetDomain": "enhancementGroups",
                "targetLabel": "강화 그룹",
                "nullable": True,
                "allowApply": True,
                "options": options,
                "note": "선택한 강화 그룹 code가 실제 enhancementGroups에 있을 때만 적용됩니다.",
            }]
        if domain == "dropTableItems":
            current_item = getattr(row, "item_template_code", None)
            current_table = getattr(row, "drop_table_code", None)
            return [
                {
                    "field": "drop_table_code",
                    "kind": "relation-select",
                    "targetDomain": "dropTables",
                    "targetLabel": "드랍 테이블",
                    "nullable": False,
                    "allowApply": True,
                    "options": await self._fetch_relation_code_options(session, DropTable, current_code=current_table, limit=300),
                    "note": "선택한 dropTables.code가 실제 존재할 때만 드랍 묶음을 변경합니다.",
                },
                {
                    "field": "item_template_code",
                    "kind": "relation-select",
                    "targetDomain": "itemTemplates",
                    "targetLabel": "아이템 템플릿",
                    "nullable": False,
                    "allowApply": True,
                    "options": await self._fetch_relation_code_options(session, ItemTemplate, current_code=current_item, limit=300),
                    "note": "선택한 itemTemplates.code가 실제 존재할 때만 드랍 아이템 연결을 변경합니다.",
                },
            ]
        if domain == "dropTables":
            current_owner_type = str(getattr(row, "owner_type", None) or "boss")
            current_owner_code = getattr(row, "owner_code", None)
            boss_options = await self._fetch_relation_code_options(session, Boss, current_code=current_owner_code if current_owner_type == "boss" else None, limit=300)
            field_options = await self._fetch_relation_code_options(session, FieldZone, current_code=current_owner_code if current_owner_type == "field" else None, limit=300)
            owner_code_options = boss_options if current_owner_type == "boss" else field_options
            return [
                {
                    "field": "owner_type",
                    "kind": "relation-select",
                    "targetDomain": "bosses/fieldZones",
                    "targetLabel": "드랍 테이블 소유자 종류",
                    "nullable": False,
                    "allowApply": True,
                    "linkedField": "owner_code",
                    "options": [
                        {"value": "boss", "label": "boss · 보스 드랍 테이블", "current": current_owner_type == "boss"},
                        {"value": "field", "label": "field · 필드 드랍 테이블", "current": current_owner_type == "field"},
                    ],
                    "note": "owner_type을 바꾸면 owner_code 후보도 보스/필드 목록으로 자동 전환됩니다.",
                },
                {
                    "field": "owner_code",
                    "kind": "relation-select",
                    "targetDomain": "bosses" if current_owner_type == "boss" else "fieldZones",
                    "targetLabel": "드랍 테이블 소유자 코드",
                    "nullable": False,
                    "allowApply": True,
                    "dependsOn": "owner_type",
                    "optionGroups": {
                        "boss": boss_options,
                        "field": field_options,
                    },
                    "options": owner_code_options,
                    "note": "owner_type이 boss이면 bosses.code, field이면 fieldZones.code 중에서만 선택합니다. 백엔드가 적용 직전에 다시 존재 여부를 검사합니다.",
                },
            ]
        if domain == "skillLevels":
            current = getattr(row, "skill_code", None)
            return [{
                "field": "skill_code",
                "kind": "relation-select",
                "targetDomain": "skills",
                "targetLabel": "스킬",
                "nullable": False,
                "allowApply": True,
                "comboGuard": ["skill_code", "level"],
                "options": await self._fetch_relation_code_options(session, Skill, current_code=current, limit=300),
                "note": "스킬 코드 + 레벨 조합이 이미 존재하면 적용이 차단됩니다.",
            }]
        if domain == "enhancementLevels":
            current = getattr(row, "group_code", None)
            return [{
                "field": "group_code",
                "kind": "relation-select",
                "targetDomain": "enhancementGroups",
                "targetLabel": "강화 그룹",
                "nullable": False,
                "allowApply": True,
                "comboGuard": ["group_code", "from_level"],
                "options": await self._fetch_relation_code_options(session, EnhancementGroup, current_code=current, limit=300),
                "note": "강화 그룹 + 시작 강화 단계 조합이 이미 존재하면 적용이 차단됩니다.",
            }]
        if domain == "characterSkills":
            current_character = getattr(row, "character_code", None)
            current_skill = getattr(row, "skill_code", None)
            return [
                {
                    "field": "character_code",
                    "kind": "relation-select",
                    "targetDomain": "characters",
                    "targetLabel": "캐릭터",
                    "nullable": False,
                    "allowApply": True,
                    "comboGuard": ["character_code", "skill_code"],
                    "options": await self._fetch_relation_code_options(session, Character, current_code=current_character, limit=200),
                    "note": "캐릭터 + 스킬 조합이 이미 존재하면 적용이 차단됩니다.",
                },
                {
                    "field": "skill_code",
                    "kind": "relation-select",
                    "targetDomain": "skills",
                    "targetLabel": "스킬",
                    "nullable": False,
                    "allowApply": True,
                    "comboGuard": ["character_code", "skill_code"],
                    "options": await self._fetch_relation_code_options(session, Skill, current_code=current_skill, limit=300),
                    "note": "캐릭터 + 스킬 조합이 이미 존재하면 적용이 차단됩니다.",
                },
            ]
        return []

    async def _fetch_relation_code_options(self, session: AsyncSession, model: Any, *, current_code: Any = None, limit: int = 200) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit or 200), 500))
        current_text = "" if current_code is None else str(current_code)
        result = await session.execute(select(model).order_by(model.code.asc()).limit(safe_limit))
        rows = result.scalars().all()
        options = [self._serialize_relation_option(row, current_text) for row in rows]
        if current_text and not any(str(option.get("value")) == current_text for option in options):
            current = await self._fetch_code_name(session, model, current_text)
            options.insert(0, {
                "value": current_text,
                "label": f"{current_text} · {(current or {}).get('name') or '현재 DB 값'}",
                "current": True,
            })
        return options

    @staticmethod
    def _serialize_relation_option(row: Any, current_code: str) -> dict[str, Any]:
        code = str(getattr(row, "code", "") or "")
        name = getattr(row, "name", None)
        return {
            "value": code,
            "label": f"{code} · {name}" if name else code,
            "current": bool(current_code and code == current_code),
        }

    async def _count_where(self, session: AsyncSession, model: Any, *where_clauses: Any) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    @staticmethod
    def _is_asset_field(key: str) -> bool:
        return key in {"image_url", "icon_url"} or key.endswith("_image_url") or key.endswith("_icon_url")

    def _serialize_asset_field(self, key: str, value: Any) -> dict[str, Any]:
        value_text = "" if value is None else str(value)
        hidden = bool(value_text)
        kind = "data-url" if value_text.startswith("data:") else ("url" if value_text else "empty")
        return {
            "key": key,
            "label": self._humanize_field_name(key),
            "kind": kind,
            "hidden": hidden,
            "length": len(value_text),
            "value": "[asset hidden]" if hidden else None,
        }

    def _safe_detail_scalar_value(self, value: Any) -> Any:
        serialized = serialize_value(value)
        if isinstance(serialized, str):
            if serialized.startswith("data:"):
                return "[asset hidden:data-url]"
            if len(serialized) > 1000:
                return serialized[:1000] + "…[truncated]"
        return serialized

    def _sanitize_json_preview(self, value: Any) -> tuple[Any, dict[str, int]]:
        stats = {"hiddenAssetCount": 0, "truncatedCount": 0, "maxDepthHit": 0}
        return self._sanitize_json_value(value, stats, depth=0), stats

    def _sanitize_json_value(self, value: Any, stats: dict[str, int], *, depth: int) -> Any:
        serialized = serialize_value(value)
        if depth > 5:
            stats["maxDepthHit"] += 1
            return "[max depth hidden]"
        if isinstance(serialized, str):
            if serialized.startswith("data:"):
                stats["hiddenAssetCount"] += 1
                return "[asset hidden:data-url]"
            if len(serialized) > 600:
                stats["truncatedCount"] += 1
                return serialized[:600] + "…[truncated]"
            return serialized
        if isinstance(serialized, list):
            max_items = 60
            values = [self._sanitize_json_value(item, stats, depth=depth + 1) for item in serialized[:max_items]]
            if len(serialized) > max_items:
                stats["truncatedCount"] += 1
                values.append(f"…[{len(serialized) - max_items} more hidden]")
            return values
        if isinstance(serialized, dict):
            max_items = 80
            result: dict[str, Any] = {}
            for index, key in enumerate(sorted(serialized.keys(), key=lambda item: str(item))):
                if index >= max_items:
                    stats["truncatedCount"] += 1
                    result["…"] = f"[{len(serialized) - max_items} more keys hidden]"
                    break
                result[str(key)] = self._sanitize_json_value(serialized[key], stats, depth=depth + 1)
            return result
        return serialized

    @staticmethod
    def _humanize_field_name(key: str) -> str:
        return key.replace("_", " ")

    def _build_readiness(self, master_counts: dict[str, Any], save_snapshot_summary: dict[str, Any]) -> dict[str, Any]:
        warnings: list[str] = []
        if int(master_counts.get("itemTemplates", {}).get("total") or 0) <= 0:
            warnings.append("master_item_templates_empty")
        if int(master_counts.get("skills", {}).get("total") or 0) <= 0:
            warnings.append("master_skills_empty")
        if int(save_snapshot_summary.get("totalSlots") or 0) <= 0:
            warnings.append("save_snapshots_empty")
        return {
            "ok": len(warnings) == 0,
            "warnings": warnings,
            "safeForAdminReadOnlyUi": True,
            "safeForAdminWriteUi": False,
            "guardedMasterEditApplyReady": True,
            "guardedRollbackReady": True,
            "writeUiBlockedReason": "일반 지급/삭제/관계 변경은 계속 막혀 있습니다. 단, allow-list 마스터 데이터 필드는 확인 문구와 변경 이력을 거쳐 guarded apply/rollback이 가능합니다.",
        }

    async def _count(self, session: AsyncSession, model: Any, *, where_clause: Any | None = None) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)
