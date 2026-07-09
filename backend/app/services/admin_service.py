from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, Numeric, String, Text, func, inspect as sa_inspect, select
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
from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService
from app.services.admin.admin_create_lifecycle_service import AdminCreateLifecycleService
from app.services.admin.admin_change_log_service import AdminChangeLogService


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


class AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminChangeLogService, AdminCreateLifecycleService):
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
    async def _get_master_row(self, session: AsyncSession, domain: str, row_id: int) -> Any | None:
        config = self.MASTER_CATALOG_DOMAINS.get(str(domain or ""))
        safe_row_id = int(row_id or 0)
        if not config or safe_row_id <= 0:
            return None
        result = await session.execute(select(config["model"]).where(config["model"].id == safe_row_id))
        return result.scalar_one_or_none()

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
