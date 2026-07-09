from __future__ import annotations

from typing import Any

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


class AdminConfigService:
    """Static admin domain/config definitions used by split admin services."""

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

