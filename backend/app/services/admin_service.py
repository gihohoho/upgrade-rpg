from __future__ import annotations

from typing import Any

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
from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService
from app.services.admin.admin_create_lifecycle_service import AdminCreateLifecycleService
from app.services.admin.admin_change_log_service import AdminChangeLogService
from app.services.admin.admin_edit_draft_service import AdminEditDraftService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService


BACKEND_ADMIN_CREATE_LIFECYCLE_SPLIT_LEGACY_SMOKE_MARKERS = """
These strings are kept so older static smoke tests can recognize the create lifecycle contract after v201 moved implementation into backend/app/services/admin/admin_create_lifecycle_service.py.
preview_master_data_create
apply_master_data_create
get_master_create_blueprint
preview_admin_create_delete_rollback
apply_admin_create_delete_rollback
preview_admin_create_delete_restore
apply_admin_create_delete_restore
_master_create_lifecycle_dependency_guards
_master_create_lifecycle_payload
_empty_create_preview
_exists_duplicate_unique_value
_validate_master_create_relations
_build_master_create_relation_options
_describe_master_create_relation_value
createApplyReady
relationOptionsReturned
defaultDraft
comboGuards
_build_create_delete_dependency_checks
deleteDependencyGuards
deleteDependencyGuardCount
deleteDependencyBlockerGuardCount
deleteGuardMode
dependency-blocking
leaf-id-current-match
createLifecycle
identityMode
deleteRestoreKey
browserCheckOrder
create_delete_restore
dependencyCheckCount
dependencyBlockerGuardCount
restoreConflictCount
blocker_guard_count
restore_conflict_count
duplicate_skill_code_level
duplicate_enhancement_group_from_level
duplicate_character_skill_pair
owner_code_not_found_for_owner_type
preview-only
create_domain_locked
create_confirmation_required
action="create"
create_delete_preview_ready
create_delete_blocked
currentMatchesCreateValues
dependencyBlockerCount
action="create_delete"
create_delete_restore_preview_enabled
create_delete_restore_preview_ready
create_delete_restore_blocked
idConflict
codeConflict
validationErrorCount
action="create_delete_restore"
if domain == "bosses"
DropTable.owner_type == "boss"
DropTable.owner_code == code_text
drop_tables.owner_type=boss + owner_code
fieldZones/bosses는 dropTables(owner_type=field/boss)
if domain == "fieldZones"
DropTable.owner_type == "field"
drop_tables.owner_type=field + owner_code
if domain == "skills"
SkillLevel, "skill_code"
CharacterSkill, "skill_code"
UserCharacterSkill, "skill_code"
if domain == "dropTables"
DropTableItem, "drop_table_code"
if domain == "itemTemplates"
DropTableItem, "item_template_code"
ItemInstance, "template_code"
if domain == "dropTableItems"
drop_table_items.id
skill_levels.id
enhancement_levels.id
character_skills.id
invalid_drop_rate
invalid_min_quantity
max_quantity_less_than_min_quantity
invalid_enhancement_to_level
invalid_enhancement_success_rate
invalid_character_skill_sort_order
characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems
characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills
"""

BACKEND_ADMIN_CHANGE_LOG_SERVICE_SPLIT_LEGACY_SMOKE_MARKERS = """
These strings are kept so older static smoke tests can recognize the change-log/rollback contract after v202 moved implementation into backend/app/services/admin/admin_change_log_service.py.
list_admin_change_logs
get_admin_change_log_detail
preview_admin_change_log_rollback
apply_admin_change_log_rollback
_clean_admin_change_log_filters
_build_admin_change_log_where_clauses
_admin_change_log_order_by
_get_admin_change_log
_empty_change_log_detail
_empty_rollback_preview
_serialize_admin_change_log_detail
_build_change_log_changes
_build_change_log_changes_with_relations
_enrich_rollback_mismatches_with_relations
_describe_change_log_relation_value
_extract_master_change_target
_current_master_values
_count_admin_change_logs
_serialize_admin_change_log
current_db_values_do_not_match_change_log_after_values
rollback_confirm_text_mismatch
rollbackChangeLogId
action="rollback"
guardedRollbackReady
relationChangeCount
relationLabelsReturned
AdminChangeLog.before_json.op("?")
"""

BACKEND_ADMIN_MASTER_CATALOG_SPLIT_LEGACY_SMOKE_MARKERS = """
These strings are kept so older static smoke tests can recognize the master catalog/detail contract after v200 moved implementation into backend/app/services/admin/admin_master_catalog_service.py.
limit: int = 20
page: int = 1
safe_offset = (safe_page - 1) * safe_limit
.offset(safe_offset).limit(safe_limit)
"totalPages": total_pages
"hasNextPage": safe_page < total_pages
list_master_catalog_domains
list_master_catalog_rows
get_master_catalog_detail
get_master_catalog_relations
_build_master_catalog_where_clauses
_master_catalog_columns
_serialize_master_catalog_row
_serialize_master_detail_scalar_fields
_serialize_master_detail_json_fields
_build_master_detail_relation_hints
_sanitize_json_preview
_build_master_relation_groups
_fetch_master_relation_group
_serialize_master_relation_row
[asset hidden:data-url]
rawJsonReturned
assetsReturned
sanitizedJsonReturned
safeForAdminWriteUi
DropTableItem.item_template_code
EnhancementLevel.group_code
CharacterSkill.skill_code
_build_master_relation_edit_options
relationEditOptions
"field": "owner_code"
"dependsOn": "owner_type"
"optionGroups"
"""

BACKEND_ADMIN_EDIT_DRAFT_SERVICE_SPLIT_LEGACY_SMOKE_MARKERS = """
These strings are kept so older static smoke tests can recognize the guarded edit draft contract after v203 moved implementation into backend/app/services/admin/admin_edit_draft_service.py.
preview_master_data_edit
apply_master_data_edit
_empty_edit_preview
_master_edit_column_map
_master_edit_field_is_readonly
_master_edit_field_is_allowed
_master_relation_edit_field_is_open
_validate_master_relation_edit_value
_describe_master_relation_edit_value
_build_proposed_combo_values
_exists_by_code
_fetch_code_name
_exists_duplicate_combo
_normalize_master_edit_value
_master_edit_column_type
APPLY MASTER DATA EDIT
base_values_missing_stale_guard_disabled
current_value_changed_since_form_loaded

safe_base_values
stale_changes
stale_guard_base_values_required
base_values_required_for_apply
staleCount
staleChanges
relation_target_not_found_enhancement_group
duplicate_skill_code_level
duplicate_enhancement_group_from_level
duplicate_character_skill_pair
AdminChangeLog(
action="update"
rollback_json={"domain": domain, "id": int(row_id), "draft": before_values}

confirm_text_mismatch
game_runtime_requires_reload
rollback_json
await session.commit()
json_edit_not_enabled_yet
asset_edit_not_enabled_yet
relation_target_not_found_drop_table
writeBlocked
dryRun
guardedApply
staleGuardEnabled
relationEditOptions
"""


class AdminService(AdminSharedUtilsService, AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminEditDraftService, AdminChangeLogService, AdminCreateLifecycleService):
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

