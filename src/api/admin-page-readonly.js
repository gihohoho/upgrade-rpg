(function () {
  "use strict";

  const VERSION = "v191.admin-edit-draft-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v113.admin-readonly-overview-url-helper v165.admin-create-apply-limited v171.admin-create-delete-restore v172.admin-layout-navigation-shell v173.admin-layout-collapse-polish v174.admin-collapsed-panel-style-fix v175.admin-create-apply-fieldzones v176.admin-create-apply-bosses v177.admin-create-apply-skills-droptables v178.admin-create-apply-items-dropitems v179.admin-create-apply-level-links v180.admin-create-lifecycle-guide v181.admin-create-lifecycle-guard-helper v182.admin-create-lifecycle-result-summary v183.admin-create-lifecycle-batch-check v184.admin-js-split-readiness v185.admin-layout-shell-split v186.admin-change-log-split-contract v188.admin-create-lifecycle-split-contract v189.admin-create-lifecycle-split v189.1.admin-create-lifecycle-split-hotfix v190.admin-edit-draft-split-contract v191.admin-edit-draft-split";
  const DEFAULT_TIMEOUT_MS = 3500;
  const DEFAULT_SNAPSHOT_LIMIT = 30;
  const DEFAULT_SNAPSHOT_SORT = "updated_desc";
  const DEFAULT_MASTER_DOMAIN = "itemTemplates";
  const DEFAULT_MASTER_LIMIT = 20;
  const DEFAULT_MASTER_SORT = "id_asc";
  const DEFAULT_CHANGE_LOG_LIMIT = 20;
  const DEFAULT_CHANGE_LOG_SORT = "created_desc";
  const ADMIN_CHANGE_LOG_ACTION_FILTERS = ["update", "rollback", "create", "create_delete", "create_delete_restore"];
  const ADMIN_CHANGE_LOG_EXTERNAL_IMPL_MARKERS = "data-admin-action=\"open-admin-change-log-detail\" data-admin-action=\"preview-admin-change-log-rollback\" data-admin-action=\"apply-admin-change-log-rollback\" data-admin-create-delete-confirm data-admin-create-delete-result createDeleteRollbackReady data-admin-create-delete-restore-confirm data-admin-create-delete-restore-result createDeleteRestoreReady dependencyCheckCount dependencyBlockerGuardCount restoreConflictCount 생성 row 삭제 차단 삭제 row 복원 차단";
  const ADMIN_CHANGE_LOG_EXTERNAL_IMPL_RAW_MARKERS = `data-admin-action="open-admin-change-log-detail" data-admin-action="preview-admin-change-log-rollback" data-admin-action="apply-admin-change-log-rollback" data-admin-action="preview-admin-create-delete" data-admin-action="apply-admin-create-delete" data-admin-action="preview-admin-create-delete-restore" data-admin-action="apply-admin-create-delete-restore" data-admin-create-delete-confirm data-admin-create-delete-result createDeleteRollbackReady data-admin-create-delete-restore-confirm data-admin-create-delete-restore-result createDeleteRestoreReady dependencyCheckCount dependencyBlockerGuardCount restoreConflictCount 생성 row 삭제 차단 삭제 row 복원 차단 relationChangeCount currentMismatches acceptedChanges createDeleteRestoreReady createDeleteReady`;
  const ADMIN_JS_SPLIT_LEGACY_READINESS_MARKERS = `layout shell 분리 안정 확인`;
  const ADMIN_CREATE_LIFECYCLE_EXTERNAL_IMPL_MARKERS = `renderAdminCreateDraft data-admin-create-draft readAdminCreateDraftValues previewAdminCreateDraft renderAdminCreatePreviewResult applyAdminCreateRelationOptionFilter refreshDependentAdminCreateRelationSelects createDraftPreviewReady applyAdminCreateDraft apply-admin-create-draft data-admin-create-confirm createApplyUnlocked createApplyReady readAdminCreateLifecycleBatchControls renderAdminCreateLifecycleBatchResult runAdminCreateLifecycleBatchCheck data-admin-create-lifecycle-batch-confirm data-admin-create-lifecycle-batch-result run-create-lifecycle-batch-check previewAdminMasterDataCreate applyAdminMasterDataCreate previewAdminCreateDeleteRollback applyAdminCreateDeleteRollback previewAdminCreateDeleteRestore applyAdminCreateDeleteRestore createLifecycleBatchCheckReady renderAdminCreateLifecycleDependencyGuards renderAdminCreateLifecycleActionShortcuts applyAdminChangeLogActionShortcut set-change-log-action-filter data-admin-change-log-action-shortcut createLifecycleDependencyGuideReady deleteDependencyGuards deleteGuardMode renderAdminCreateLifecycleGuide getAdminCreateLifecycleGuideReadiness createLifecycleGuideReady createLifecycle browserCheckOrder CREATE MASTER DATA ROW DELETE CREATED MASTER DATA ROW RESTORE DELETED CREATED ROW RUN CREATE DELETE RESTORE CHECK renderAdminOperationResultBanner renderAdminCreateLifecycleMetric renderAdminCreateDeleteBlockerSummary createLifecycleResultSummaryReady dependencyCheckCount dependencyBlockerGuardCount restoreConflictCount 생성 row 삭제 차단 삭제 row 복원 차단 characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills`;

  const ADMIN_EDIT_DRAFT_EXTERNAL_IMPL_MARKERS = `
    function getAdminRelationEditOptionDefinitions function getAdminRelationEditOptionDefinition function isAdminRelationEditField function fieldKeyLooksReadOnly
    function isAdminEditApplyAllowedField function getAdminEditAllowedFields function normalizeAdminDraftFieldKey function getAdminEquipSlotDisplayName
    function getAdminDraftFieldInputKind function renderAdminDraftLockedFields function getAdminDraftLockedReason function renderAdminDraftTypeBadge
    function renderMasterEditDraft function readAdminEditDraftValues function resetAdminEditDraft function previewAdminEditDraft function applyAdminEditDraft
    function readAdminEditApplyControls function renderAdminEditPreviewResult function buildAdminEditDraftReview function renderAdminEditDraftReview
    function getAdminEditImpactHint function buildAdminEditImpactGuide function renderAdminEditImpactGuide function refreshAdminEditImpactGuide collectLocalDraftChangesForImpact
    function getAdminRelationSelectMetaText function renderAdminRelationEditOptionsNote function applyAdminRelationOptionFilter function clearAdminRelationOptionFilter
    function refreshDependentAdminRelationSelects function getAdminRelationComboGuardLabels function getAdminRelationOpenTarget function getAdminRelationOpenTargetFromChange
    function renderAdminRollbackMismatchValueCell function formatAdminChangeValueText function renderAdminChangeValueCell function formatAdminChangeAfterValue
    ADMIN_DRAFT_BOOLEAN_FIELDS ADMIN_DRAFT_NUMBER_FIELDS ADMIN_DRAFT_TEXTAREA_FIELDS ADMIN_EDIT_APPLY_CONFIRM_TEXT ADMIN_EDIT_ALLOWED_FIELDS
    APPLY MASTER DATA EDIT HIGH RISK EDIT guardedApply boolean-select type="number" inputmode="decimal" step="any" description/admin_note data-admin-edit-locked-fields field.value === "true"
    stackable 인벤토리 겹치기 동작 변경 보스 체력 변경 드랍 확률/수량 변경 data-admin-edit-impact 게임 새로고침
    baseValues: values.originals stale guard payload.staleGuardEnabled payload.staleCount staleChanges 오래된 초안 검사
    await runPostWriteMasterApiVerification(values.domain, values.id currentAdminChangeLogDetailPayload window.getAdminDraftFieldInputKind changedKey targetType action 중복 조합 검사 skill_code + level group_code + from_level character_code + skill_code drop_table_code 스킬 레벨 조합 변경 강화 단계 조합 변경 캐릭터 스킬 연결 변경 relation-option-filter data-admin-relation-option-filter keepSelected window.applyAdminRelationOptionFilter data-admin-master-query syncMasterCatalogPageInput(1) getAdminDraftRelationOptionsForValues renderAdminRelationOpenButton open-master-detail-by-code relationCount window.formatAdminChangeValueText window.getAdminRelationValueDisplay relationSearchReady relationPreviewReady  data-admin-edit-draft data-admin-edit-draft-field 검증 후 실제 적용 guardedApply: true data-admin-action="preview-admin-edit-draft" 초안 검증 fieldsEditable refreshAdminEditReviewAndImpact data-admin-edit-risk-confirm 고위험 변경이 있어서 추가 확인 문구 relation-select relationEditOptions enhance_group_code item_template_code owner_type 아이템 강화 그룹 연결 변경 드랍 아이템 연결 변경 grade / 등급 숫자 기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급 normal_equipment talisman_emblem window.getAdminFieldValueHint "6": "특수무기" "7": "특수목걸이" "8": "특수반지" "9": "무기아바타" "10": "오라아바타" "11": "클론 레어 아바타" "12": "탈리스만 A" "13": "탈리스만 B" "14": "휘장" 6 · 특수무기 14 · 휘장 window.getAdminEquipSlotDisplayName dropTables: ["owner_type", "owner_code", "description", "is_enabled"] getAdminDraftRelationOptionGroupKey getAdminDraftRelationOptions definition.optionGroups definition.dependsOn ownercode 드랍 테이블 소유자 변경 window.refreshDependentAdminRelationSelects preset-select draft-field-badges item_type equip_slot slot_key 현재 DB 값 아이템 분류/장착 슬롯 변경 스킬 슬롯 배치 변경 window.getAdminDraftSelectOptions data-admin-action="apply-admin-edit-draft"
  `;
  const ADMIN_CHANGE_LOG_POST_VERIFY_LEGACY_MARKERS = `currentAdminChangeLogDetailPayload rollbackTarget.domain rollbackTarget.id contextLabel`;
  const ADMIN_EDIT_APPLY_CONFIRM_TEXT = "APPLY MASTER DATA EDIT";
  const ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT = "HIGH RISK EDIT";
  const ADMIN_ROLLBACK_CONFIRM_TEXT = "ROLLBACK MASTER DATA EDIT";
  const ADMIN_CREATE_APPLY_CONFIRM_TEXT = "CREATE MASTER DATA ROW";
  const ADMIN_CREATE_DELETE_CONFIRM_TEXT = "DELETE CREATED MASTER DATA ROW";
  const ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = "RESTORE DELETED CREATED ROW";
  const ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT = "RUN CREATE DELETE RESTORE CHECK";
  const ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  const ADMIN_WRITE_DEV_KEY_EXAMPLE = "local-admin-dev-key";
  const ADMIN_JS_SPLIT_PHASES = [
    { key: "api-client", label: "API client", currentFile: "src/api/game-api-client.js", nextFile: "src/api/admin/admin-api-client.js", status: "already-external", note: "관리자 API 호출 기반은 이미 admin.html 밖에 있습니다." },
    { key: "layout-shell", label: "Layout shell", currentFile: "src/api/admin-layout-shell.js", nextFile: "src/api/admin-layout-shell.js", status: "extracted-v185", note: "sidebar, sticky header, section collapse 계열을 외부 파일로 분리했습니다." },
    { key: "change-logs", label: "Change logs", currentFile: "src/api/admin/admin-change-logs.js", nextFile: "src/api/admin/admin-change-logs.js", status: "extracted-v187", note: "변경 이력 필터/목록/상세/rollback/create-delete/restore 구현을 외부 파일로 1차 분리했습니다." },
    { key: "create-lifecycle", label: "Create lifecycle", currentFile: "src/api/admin/admin-create-lifecycle.js", nextFile: "src/api/admin/admin-create-lifecycle.js", status: "extracted-v189", note: "생성 초안/생성→삭제→복원 batch check 구현을 외부 파일로 1차 분리했습니다." },
    { key: "edit-draft", label: "Edit draft", currentFile: "src/api/admin/admin-edit-draft.js", nextFile: "src/api/admin/admin-edit-draft.js", status: "extracted-v191", note: "편집 초안/impact guide/relation select 구현을 외부 JS 파일로 1차 분리했습니다." },
    { key: "bootstrap", label: "Page bootstrap", currentFile: "src/api/admin-page-readonly.js", nextFile: "src/api/admin-page-readonly.js", status: "keep-last", note: "초기 boot/bindEvents/window export는 마지막까지 thin entry 파일로 남기는 방향이 안전합니다." },
  ];
  const ADMIN_JS_SPLIT_REQUIRED_GLOBALS = [
    "RpgGameApi",
    "RpgAdminReadOnlyPage",
    "RpgAdminLayoutShell",
    "RpgAdminChangeLogs",
    "RpgAdminCreateLifecycle",
    "checkAdminReadOnlyPageReady",
    "refreshAdminReadOnlyPage",
    "refreshAdminCreateBlueprint",
    "runAdminCreateLifecycleBatchCheck",
    "getAdminCreateLifecycleSplitContractReadiness",
    "getAdminEditDraftSplitContractReadiness",
    "initializeAdminLayoutShell",
  ];

  const ADMIN_CHANGE_LOG_SPLIT_CONTRACT = {
    key: "change-logs",
    label: "Change logs",
    status: "contract-frozen-v186",
    currentFile: "src/api/admin-page-readonly.js",
    nextFile: "src/api/admin/admin-change-logs.js",
    requiredApiMethods: [
      "listAdminChangeLogs",
      "fetchAdminChangeLogDetail",
      "previewAdminChangeLogRollback",
      "applyAdminChangeLogRollback",
      "previewAdminCreateDeleteRollback",
      "applyAdminCreateDeleteRollback",
      "previewAdminCreateDeleteRestore",
      "applyAdminCreateDeleteRestore",
    ],
    requiredWindowExports: [
      "readChangeLogFiltersFromDom",
      "resetChangeLogFilters",
      "describeChangeLogFilters",
      "refreshAdminChangeLogs",
      "renderAdminChangeLogs",
      "openAdminChangeLogDetail",
      "renderAdminChangeLogDetail",
      "previewAdminChangeLogRollback",
      "applyAdminChangeLogRollback",
      "readAdminRollbackControls",
      "renderAdminRollbackResult",
      "previewAdminCreateDeleteRollback",
      "applyAdminCreateDeleteRollback",
      "readAdminCreateDeleteControls",
      "renderAdminCreateDeleteResult",
      "previewAdminCreateDeleteRestore",
      "applyAdminCreateDeleteRestore",
      "readAdminCreateDeleteRestoreControls",
      "renderAdminCreateDeleteRestoreResult",
      "applyAdminChangeLogActionShortcut",
      "getAdminChangeLogSplitContractReadiness",
      "renderAdminChangeLogSplitContractReadiness",
    ],
    domTargets: [
      "#section-change-logs",
      "[data-admin-change-log-meta]",
      "[data-admin-change-log-filter-limit]",
      "[data-admin-change-log-filter-target-type]",
      "[data-admin-change-log-filter-target-id]",
      "[data-admin-change-log-filter-action]",
      "[data-admin-change-log-filter-changed-key]",
      "[data-admin-change-log-filter-applied]",
      "[data-admin-change-log-filter-sort]",
      "[data-admin-change-log-table]",
      "[data-admin-change-log-detail]",
      "[data-admin-js-split-readiness]",
    ],
    actionFilters: ADMIN_CHANGE_LOG_ACTION_FILTERS.slice(),
    delegatedActions: [
      "refresh-admin-change-logs",
      "open-admin-change-log-detail",
      "preview-admin-change-log-rollback",
      "apply-admin-change-log-rollback",
      "preview-admin-create-delete-rollback",
      "apply-admin-create-delete-rollback",
      "preview-admin-create-delete-restore",
      "apply-admin-create-delete-restore",
      "set-change-log-action-filter",
    ],
    splitBoundary: [
      "filters",
      "list render",
      "detail render",
      "rollback preview/apply",
      "create delete preview/apply",
      "create delete restore preview/apply",
      "action shortcut",
    ],
  };


  const ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT = {
    key: "create-lifecycle",
    label: "Create lifecycle",
    status: "contract-frozen-v188",
    currentFile: "src/api/admin-page-readonly.js",
    nextFile: "src/api/admin/admin-create-lifecycle.js",
    requiredApiMethods: [
      "fetchAdminMasterCreateBlueprint",
      "previewAdminMasterDataCreate",
      "applyAdminMasterDataCreate",
      "previewAdminCreateDeleteRollback",
      "applyAdminCreateDeleteRollback",
      "previewAdminCreateDeleteRestore",
      "applyAdminCreateDeleteRestore",
    ],
    requiredWindowExports: [
      "readAdminCreateBlueprintFiltersFromDom",
      "syncAdminCreateDomainFromCatalog",
      "refreshAdminCreateBlueprint",
      "renderAdminCreateBlueprint",
      "getAdminCreateBlueprintFieldInputKind",
      "getAdminCreateBlueprintRequiredKeys",
      "getAdminCreateBlueprintDefaultDraft",
      "getAdminCreateBlueprintReadiness",
      "readAdminCreateDraftValues",
      "resetAdminCreateDraft",
      "previewAdminCreateDraft",
      "applyAdminCreateDraft",
      "renderAdminCreatePreviewResult",
      "getAdminCreateFieldDefinition",
      "getAdminCreateRelationDefinition",
      "applyAdminCreateRelationOptionFilter",
      "refreshDependentAdminCreateRelationSelects",
      "renderAdminCreateLifecycleGuide",
      "renderAdminCreateLifecycleDependencyGuards",
      "renderAdminCreateLifecycleBatchResult",
      "runAdminCreateLifecycleBatchCheck",
      "getAdminCreateLifecycleGuideReadiness",
      "getAdminCreateLifecycleSplitContractReadiness",
      "renderAdminCreateLifecycleSplitContractReadiness",
    ],
    domTargets: [
      "#section-create-blueprint",
      "[data-admin-create-domain]",
      "[data-admin-create-blueprint]",
      "#section-create-lifecycle-guide",
      "[data-admin-create-lifecycle-guide]",
      "[data-admin-js-split-readiness]",
    ],
    dynamicDomTargets: [
      "[data-admin-create-reason]",
      "[data-admin-create-confirm]",
      "[data-admin-create-result]",
      "[data-admin-create-lifecycle-batch-confirm]",
      "[data-admin-create-lifecycle-batch-result]",
    ],
    confirmTexts: [
      { key: "create", value: ADMIN_CREATE_APPLY_CONFIRM_TEXT },
      { key: "deleteCreatedRow", value: ADMIN_CREATE_DELETE_CONFIRM_TEXT },
      { key: "restoreDeletedCreatedRow", value: ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT },
      { key: "batchCheck", value: ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT },
    ],
    delegatedActions: [
      "load-create-blueprint",
      "sync-create-domain-from-catalog",
      "reset-admin-create-draft",
      "preview-admin-create-draft",
      "apply-admin-create-draft",
      "filter-create-relation-options",
      "run-create-lifecycle-batch-check",
    ],
    splitBoundary: [
      "blueprint filters",
      "draft controls",
      "create preview/apply",
      "lifecycle guide render",
      "dependency guard guide",
      "result summary helpers",
      "batch check orchestration",
    ],
  };

  const ADMIN_EDIT_ALLOWED_FIELDS = {
    itemTemplates: ["name", "item_type", "grade", "description", "stackable", "equip_slot", "enhance_group_code", "admin_note"],
    skills: ["slot_key", "name", "description", "proc_rate", "cooldown_seconds"],
    skillLevels: ["skill_code", "level", "damage_multiplier", "proc_rate_bonus"],
    bosses: ["name", "tier", "boss_type", "hp", "description", "cooldown_seconds", "is_enabled"],
    fieldZones: ["name", "sort_order", "enemy_hp", "gold_reward", "description", "is_enabled"],
    characters: ["name", "description", "is_enabled"],
    dropTables: ["owner_type", "owner_code", "description", "is_enabled"],
    dropTableItems: ["drop_table_code", "item_template_code", "rate", "min_quantity", "max_quantity"],
    enhancementGroups: ["name", "description", "max_level", "is_enabled"],
    enhancementLevels: ["group_code", "from_level", "to_level", "success_rate", "gold_cost"],
    characterSkills: ["character_code", "skill_code", "sort_order", "is_default"],
  };
  const ADMIN_DRAFT_BOOLEAN_FIELDS = new Set(["stackable", "is_enabled", "is_default"]);
  const ADMIN_DRAFT_NUMBER_FIELDS = new Set([
    "grade",
    "proc_rate",
    "cooldown_seconds",
    "level",
    "damage_multiplier",
    "proc_rate_bonus",
    "tier",
    "hp",
    "sort_order",
    "enemy_hp",
    "gold_reward",
    "rate",
    "min_quantity",
    "max_quantity",
    "max_level",
    "from_level",
    "to_level",
    "success_rate",
    "gold_cost",
  ]);
  const ADMIN_DRAFT_TEXTAREA_FIELDS = new Set(["description", "admin_note"]);
  const ADMIN_EQUIP_SLOT_PRESET_LABELS = {
    skill_all: "일반장비 1 · 스킬피해+모든피해",
    atk_inc: "일반장비 2 · 공격력 추가",
    normal_dmg: "일반장비 3 · 평타피해",
    skill_chance: "일반장비 4/5 · 추가 스킬피해",
    normal_crit: "일반장비 4/5 · 평타 치명타",
    all_dmg: "예비 슬롯 · 모든피해",
    skill_dmg: "예비 슬롯 · 스킬피해",
    "6": "특수무기",
    "7": "특수목걸이",
    "8": "특수반지",
    "9": "무기아바타",
    "10": "오라아바타",
    "11": "클론 레어 아바타",
    "12": "탈리스만 A",
    "13": "탈리스만 B",
    "14": "휘장",
  };
  const ADMIN_DRAFT_SELECT_FIELD_OPTIONS = {
    item_type: [
      { value: "normal", label: "normal · 일반 장비" },
      { value: "skill_book", label: "skill_book · 스킬강화권" },
      { value: "special_equip", label: "special_equip · 특수 장비" },
      { value: "abyss", label: "abyss · 심연 장비" },
      { value: "avatar", label: "avatar · 아바타" },
      { value: "material", label: "material · 재료" },
      { value: "consumable", label: "consumable · 소모품" },
      { value: "unknown", label: "unknown · 미분류" },
    ],
    equip_slot: [
      { value: "", label: "없음 · 장착 슬롯 없음" },
      { value: "skill_all", label: "skill_all · 일반장비 1 · 스킬피해+모든피해" },
      { value: "atk_inc", label: "atk_inc · 일반장비 2 · 공격력 추가" },
      { value: "normal_dmg", label: "normal_dmg · 일반장비 3 · 평타피해" },
      { value: "skill_chance", label: "skill_chance · 일반장비 4/5 · 추가 스킬피해" },
      { value: "normal_crit", label: "normal_crit · 일반장비 4/5 · 평타 치명타" },
      { value: "skill_dmg", label: "skill_dmg · 예비 슬롯 · 스킬피해" },
      { value: "all_dmg", label: "all_dmg · 예비 슬롯 · 모든피해" },
      { value: "6", label: "6 · 특수무기" },
      { value: "7", label: "7 · 특수목걸이" },
      { value: "8", label: "8 · 특수반지" },
      { value: "9", label: "9 · 무기아바타" },
      { value: "10", label: "10 · 오라아바타" },
      { value: "11", label: "11 · 클론 레어 아바타" },
      { value: "12", label: "12 · 탈리스만 A" },
      { value: "13", label: "13 · 탈리스만 B" },
      { value: "14", label: "14 · 휘장" },
    ],
    boss_type: [
      { value: "normal", label: "normal · 일반 보스" },
      { value: "special", label: "special · 특수 보스" },
    ],
    owner_type: [
      { value: "boss", label: "boss · 보스 드랍 테이블" },
      { value: "field", label: "field · 필드 드랍 테이블" },
    ],
    slot_key: [
      { value: "Q", label: "Q · 기본 1번 스킬" },
      { value: "W", label: "W · 기본 2번 스킬" },
      { value: "E", label: "E · 기본 3번 스킬" },
      { value: "R", label: "R · 기본 4번 스킬" },
      { value: "T", label: "T · 기본 5번 스킬" },
      { value: "F", label: "F · 기본 6번 스킬" },
      { value: "D", label: "D · 기본 7번 스킬" },
      { value: "M", label: "M · 기본 8번 스킬" },
      { value: "SQ", label: "SQ · Q 각성 스킬" },
      { value: "SW", label: "SW · W 각성 스킬" },
      { value: "SE", label: "SE · E 각성 스킬" },
      { value: "SR", label: "SR · R 각성 스킬" },
      { value: "ST", label: "ST · T 각성 스킬" },
      { value: "SF", label: "SF · F 각성 스킬" },
      { value: "SD", label: "SD · D 각성 스킬" },
      { value: "SM", label: "SM · M 각성 스킬" },
    ],
  };
  const ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT = 18;

  let currentMasterDetailPayload = null;
  let currentAdminChangeLogDetailPayload = null;
  let currentAdminCreateBlueprintPayload = null;

  const ADMIN_TO_MASTER_API_FIELD_MAP = {
    itemTemplates: {
      code: "code",
      name: "name",
      item_type: "itemType",
      grade: "grade",
      description: "description",
      stackable: "stackable",
      equip_slot: "equipSlot",
      enhance_group_code: "enhanceGroupCode",
      admin_note: "adminNote",
    },
    skills: {
      code: "code",
      name: "name",
      slot_key: "slotKey",
      description: "description",
      proc_rate: "procRate",
      cooldown_seconds: "cooldownSeconds",
    },
    skillLevels: {
      skill_code: "skillCode",
      level: "level",
      damage_multiplier: "damageMultiplier",
      proc_rate_bonus: "procRateBonus",
    },
    bosses: {
      code: "code",
      name: "name",
      tier: "tier",
      boss_type: "bossType",
      hp: "hp",
      description: "description",
      cooldown_seconds: "cooldownSeconds",
      is_enabled: "isEnabled",
    },
    fieldZones: {
      code: "code",
      name: "name",
      sort_order: "sortOrder",
      enemy_hp: "enemyHp",
      gold_reward: "goldReward",
      description: "description",
      is_enabled: "isEnabled",
    },
    characters: {
      code: "code",
      name: "name",
      description: "description",
      is_enabled: "isEnabled",
    },
    dropTables: {
      code: "code",
      owner_type: "ownerType",
      owner_code: "ownerCode",
      description: "description",
      is_enabled: "isEnabled",
    },
    dropTableItems: {
      id: "id",
      drop_table_code: "dropTableCode",
      item_template_code: "itemTemplateCode",
      rate: "rate",
      min_quantity: "minQuantity",
      max_quantity: "maxQuantity",
    },
    enhancementGroups: {
      code: "code",
      name: "name",
      description: "description",
      max_level: "maxLevel",
      is_enabled: "isEnabled",
    },
    enhancementLevels: {
      group_code: "groupCode",
      from_level: "fromLevel",
      to_level: "toLevel",
      success_rate: "successRate",
      gold_cost: "goldCost",
    },
    characterSkills: {
      character_code: "characterCode",
      skill_code: "skillCode",
      sort_order: "sortOrder",
      is_default: "isDefault",
    },
  };

  const ADMIN_EDIT_DRAFT_SPLIT_CONTRACT = {
    key: "edit-draft",
    label: "Edit draft",
    status: "extracted-v191",
    currentFile: "src/api/admin/admin-edit-draft.js",
    nextFile: "src/api/admin/admin-edit-draft.js",
    requiredApiMethods: [
      "previewAdminMasterDataEdit",
      "applyAdminMasterDataEdit",
    ],
    requiredWindowExports: [
      "renderMasterEditDraft",
      "readAdminEditDraftValues",
      "resetAdminEditDraft",
      "previewAdminEditDraft",
      "applyAdminEditDraft",
      "renderAdminEditPreviewResult",
      "readAdminEditApplyControls",
      "buildAdminEditDraftReview",
      "renderAdminEditDraftReview",
      "buildAdminEditImpactGuide",
      "renderAdminEditImpactGuide",
      "refreshAdminEditImpactGuide",
      "getAdminEditDraftReadiness",
      "getAdminEditAllowedFields",
      "isAdminEditApplyAllowedField",
      "getAdminDraftFieldInputKind",
      "getAdminDraftSelectOptions",
      "getAdminRelationEditOptionDefinitions",
      "getAdminRelationEditOptionDefinition",
      "isAdminRelationEditField",
      "refreshDependentAdminRelationSelects",
      "applyAdminRelationOptionFilter",
      "clearAdminRelationOptionFilter",
      "filterAdminDraftSelectOptions",
      "getAdminRelationSelectMetaText",
      "renderAdminRelationEditOptionsNote",
      "getAdminDraftFieldRisk",
      "getAdminDraftLockedReason",
      "getAdminRelationOpenTarget",
      "getAdminFieldValueHint",
      "renderFieldValueHintInline",
      "getAdminEditDraftSplitContractReadiness",
      "renderAdminEditDraftSplitContractReadiness",
    ],
    domTargets: [
      "#section-master-detail",
      "[data-admin-master-detail]",
      "[data-admin-js-split-readiness]",
    ],
    dynamicDomTargets: [
      "[data-admin-edit-draft]",
      "[data-admin-edit-review]",
      "[data-admin-edit-impact]",
      "[data-admin-edit-draft-result]",
      "[data-admin-edit-draft-field]",
      "[data-admin-edit-confirm]",
      "[data-admin-edit-high-risk-confirm]",
    ],
    confirmTexts: [
      { key: "editApply", value: ADMIN_EDIT_APPLY_CONFIRM_TEXT },
      { key: "highRisk", value: ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT },
    ],
    delegatedActions: [
      "preview-admin-edit-draft",
      "apply-admin-edit-draft",
      "reset-admin-edit-draft",
      "filter-relation-options",
      "open-relation-target",
    ],
    splitBoundary: [
      "edit draft render",
      "draft value reader/reset",
      "preview/apply controls",
      "relation select helpers",
      "dependent relation filters",
      "field value hints",
      "draft review render",
      "impact guide render",
      "result render",
    ],
  };



  function $(selector) {
    return document.querySelector(selector);
  }

  function escapeHtml(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatValue(value) {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "number") return Number.isFinite(value) ? value.toLocaleString("ko-KR") : String(value);
    if (typeof value === "boolean") return value ? "true" : "false";
    return String(value);
  }

  function formatClock(value) {
    if (!value) return "-";
    try {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return date.toLocaleString("ko-KR", { hour12: false });
    } catch (error) {
      return String(value);
    }
  }


  const ADMIN_FIELD_HELP_DEFINITIONS = {
    grade: {
      title: "grade / 등급 숫자",
      body: "현재 이 프로젝트의 itemTemplates.grade는 일반적인 normal/rare/epic 희귀도명이 아니라, 기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급입니다. 쉽게 말해 아이템이 어느 보스/장비 성장 구간에 속하는지 보는 값입니다.",
      example: "예: grade=1은 1티어/초반 구간, grade=12는 12티어/상위 구간처럼 해석합니다. 희귀도 이름이 필요하면 나중에 rarity 같은 별도 필드로 분리하는 편이 안전합니다.",
    },
    enhancegroupcode: {
      title: "enhance group code / 강화그룹 코드",
      body: "이 아이템이 어떤 강화 규칙 묶음을 사용할지 연결하는 코드입니다. 아이템의 enhance_group_code와 강화 그룹의 code가 같으면, 그 강화 그룹/강화 단계가 이 아이템에 적용됩니다.",
      example: "예: weapon_basic 아이템 → enhancementGroups.code=weapon_basic → enhancementLevels.group_code=weapon_basic 단계 적용",
    },
    groupcode: {
      title: "group code / 강화 단계 그룹 코드",
      body: "강화 단계가 어느 강화 그룹에 속하는지 나타내는 코드입니다. enhancementLevels의 group_code는 enhancementGroups의 code와 연결됩니다.",
      example: "같은 group_code를 가진 강화 단계들이 +0→+1, +1→+2 같은 단계 규칙 묶음이 됩니다.",
    },
    adminnote: {
      title: "admin note / 관리자 메모",
      body: "게임 플레이 화면에는 보여주지 않는 운영자용 메모입니다. 데이터 작업 이유, 주의사항, 임시 설명, 나중에 확인할 내용을 적어두는 내부 기록용 필드입니다.",
      example: "예: 밸런스 조정 예정, 이벤트 드랍 전용, 아직 미사용 데이터 등",
    },
    itemtype: {
      title: "item type / 아이템 분류",
      body: "아이템이 일반 장비인지, 스킬강화권인지, 특수 장비인지 같은 큰 분류를 정하는 값입니다. 드랍 목록, 겹치기 기본 판단, 향후 필터/정렬 기준에 영향을 줄 수 있습니다.",
      example: "예: normal=일반 장비, skill_book=스킬강화권, special_equip=특수 장비",
    },
    equipslot: {
      title: "equip slot / 장착 슬롯",
      body: "장비가 어떤 장착 그룹 또는 특수 슬롯에 들어가는지 나타내는 값입니다. 잘못 바꾸면 장착 위치나 장비 효과 분류가 어색해질 수 있으니 select 프리셋 안에서만 고르는 편이 안전합니다.",
      example: "예: skill_all=일반장비 1, atk_inc=일반장비 2, 6=특수무기, 12=탈리스만 A",
    },
    slotkey: {
      title: "slot key / 스킬 슬롯",
      body: "스킬이 Q/W/E/R/T/F/D/M 또는 각성 슬롯 중 어디에 배치되는지 나타내는 값입니다. 같은 슬롯이 중복되면 UI 배치가 헷갈릴 수 있으니 변경 후 게임 화면에서 꼭 확인해야 합니다.",
      example: "예: Q, W, E, R, T, F, D, M, SQ, SW 같은 슬롯 키",
    },
    skillcode: {
      title: "skill code / 스킬 연결 코드",
      body: "스킬 레벨 또는 캐릭터 스킬 연결이 어떤 skills.code를 바라볼지 정하는 관계 필드입니다. 실제 존재하는 스킬 목록에서만 선택할 수 있습니다.",
      example: "skillLevels에서는 skill_code + level 조합, characterSkills에서는 character_code + skill_code 조합이 중복되면 적용이 차단됩니다.",
    },
    level: {
      title: "level / 스킬 레벨",
      body: "스킬 강화 단계 숫자입니다. 같은 skill_code 안에서 같은 level이 이미 있으면 적용이 차단됩니다.",
      example: "예: q_skill + level 1은 하나만 존재해야 합니다.",
    },
    fromlevel: {
      title: "from level / 강화 시작 단계",
      body: "강화 단계 규칙의 시작 레벨입니다. 같은 group_code 안에서 같은 from_level이 이미 있으면 적용이 차단됩니다.",
      example: "예: weapon_basic +0→+1 규칙과 +1→+2 규칙처럼 시작 단계가 겹치면 안 됩니다.",
    },
    charactercode: {
      title: "character code / 캐릭터 연결 코드",
      body: "캐릭터 스킬 연결이 어떤 캐릭터에 속할지 정하는 관계 필드입니다. 실제 characters.code 목록에서만 선택할 수 있습니다.",
      example: "character_code + skill_code 조합이 이미 있으면 적용이 차단됩니다.",
    },
    droptablecode: {
      title: "drop table code / 드랍 테이블 연결 코드",
      body: "드랍 아이템이 어느 드랍 테이블에 속할지 정하는 관계 필드입니다. 실제 dropTables.code 목록에서만 선택할 수 있습니다.",
      example: "보스/필드 드랍 묶음 이동에 영향을 주므로 적용 후 관계 탭에서 연결을 확인하는 편이 안전합니다.",
    },
    bosstype: {
      title: "boss type / 보스 분류",
      body: "보스가 일반 보스인지 특수 보스인지 나누는 값입니다. 보스 목록 정렬, 소환/표시 그룹, 드랍 확인에 영향을 줄 수 있습니다.",
      example: "normal=일반 보스, special=특수 보스",
    },
    stackable: {
      title: "stackable / 겹치기 가능 여부",
      body: "인벤토리에서 같은 아이템을 한 칸에 수량으로 합칠 수 있는지 정하는 true/false 값입니다. true면 재료/강화권처럼 여러 개가 한 칸에 쌓이고, false면 장비처럼 각각 별도 칸을 차지합니다.",
      example: "예: 강화권/재료는 true, 무기/방어구/탈리스만처럼 개별 강화·옵션을 가진 장비는 보통 false가 안전합니다.",
    },
    sortorder: {
      title: "sort order / 정렬값",
      body: "화면이나 관리자 목록에서 어떤 순서로 보여줄지 정하는 숫자입니다. 보통 숫자가 작을수록 앞쪽에 배치합니다.",
      example: "예: 10, 20, 30처럼 간격을 두면 중간에 새 항목을 끼워 넣기 쉽습니다.",
    },
    isenabled: {
      title: "is enabled / 활성 상태",
      body: "이 마스터 데이터를 실제 게임 기준 데이터로 사용할지 여부입니다. false면 관리자에는 남아 있어도 게임 적용 대상에서 제외할 수 있습니다.",
      example: "테스트용/미사용 데이터는 false로 두는 식으로 활용합니다.",
    },
  };

  function normalizeAdminFieldKey(key) {
    return String(key || "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
  }

  function getAdminFieldHelp(key) {
    const normalized = normalizeAdminFieldKey(key);
    return ADMIN_FIELD_HELP_DEFINITIONS[normalized] || null;
  }

  function listAdminFieldHelp() {
    return Object.entries(ADMIN_FIELD_HELP_DEFINITIONS).map(([key, help]) => ({ key, ...help }));
  }

  function renderFieldHelpBadge(key) {
    const help = getAdminFieldHelp(key);
    if (!help) return "";
    const titleText = `${help.title}\n${help.body}\n${help.example || ""}`;
    return ` <span class="field-help-badge" title="${escapeHtml(titleText)}">?</span>`;
  }

  function renderFieldHelpInline(key) {
    const help = getAdminFieldHelp(key);
    if (!help) return "";
    return `<div class="field-help-inline"><strong>${escapeHtml(help.title)}</strong> — ${escapeHtml(help.body)}${help.example ? `<br><span>${escapeHtml(help.example)}</span>` : ""}</div>`;
  }

  function getAdminFieldValueHint(key, value) {
    const normalized = normalizeAdminFieldKey(key);
    if (normalized === "grade") {
      if (value === null || value === undefined || value === "") {
        return { label: "grade 없음", body: "이 항목은 아직 진행 티어/등급 숫자가 비어 있습니다." };
      }
      const numeric = Number(value);
      if (Number.isFinite(numeric)) {
        return {
          label: `tier ${numeric}`,
          body: `현재 값 ${numeric}은 희귀도명이 아니라 원본 아이템 tier ${numeric}입니다. 아이템/보스 성장 구간, 드랍 단계, 장비 진행도를 맞출 때 참고하는 숫자입니다.`,
        };
      }
      return {
        label: "text grade",
        body: "숫자가 아닌 grade 값입니다. 현재 DB seed 기준에서는 대부분 tier 숫자가 들어가므로, 이 값은 별도로 확인하는 편이 안전합니다.",
      };
    }
    if (normalized === "enhancegroupcode") {
      if (!value) return { label: "강화그룹 미연결", body: "이 항목은 아직 강화 규칙 묶음에 연결되어 있지 않습니다." };
      if (String(value) === "normal_equipment") return { label: "일반 장비 강화", body: "일반/심연/특수/avatar 계열 장비가 공유하는 기본 강화 규칙 묶음입니다." };
      if (String(value) === "talisman_emblem") return { label: "탈리스만/휘장 강화", body: "탈리스만과 빛나는 휘장처럼 같은 강화 방식을 쓰는 장비 묶음입니다." };
      return { label: String(value), body: `강화그룹 코드 ${value}와 같은 code/group_code를 가진 enhancementGroups/enhancementLevels가 연결됩니다.` };
    }
    if (normalized === "itemtype") {
      const text = String(value || "");
      if (text === "normal") return { label: "normal · 일반 장비", body: "일반 장비 분류입니다. 보통 개별 장비라 stackable=false가 안전합니다." };
      if (text === "skill_book") return { label: "skill_book · 스킬강화권", body: "스킬 강화권 분류입니다. 보통 수량 겹치기 대상입니다." };
      if (text === "special_equip") return { label: "special_equip · 특수 장비", body: "특수 슬롯 장비 분류입니다. 장착 슬롯 값과 함께 확인해야 합니다." };
      return text ? { label: text, body: "프리셋에 있는 아이템 분류 값입니다. 변경 후 드랍/인벤토리 표시를 확인하세요." } : { label: "분류 없음", body: "아이템 분류가 비어 있습니다." };
    }
    if (normalized === "equipslot") {
      const text = String(value || "");
      if (!text) return { label: "장착 슬롯 없음", body: "재료/강화권처럼 장착하지 않는 아이템에 어울립니다." };
      const displayName = getAdminEquipSlotDisplayName(text);
      if (/^\d+$/.test(text)) return { label: `${text} · ${displayName}`, body: "인게임 장비창 오른쪽 특수 장비 슬롯 이름입니다." };
      return { label: `${text} · ${displayName}`, body: "일반 장비 장착/효과 그룹입니다. 변경 후 장착 위치와 툴팁을 확인하세요." };
    }
    if (normalized === "slotkey") {
      const text = String(value || "");
      return text ? { label: `${text} 슬롯`, body: "스킬 버튼/각성 슬롯 배치에 영향을 줄 수 있습니다. 중복 슬롯이 생기지 않게 확인하세요." } : { label: "슬롯 없음", body: "스킬 슬롯이 비어 있습니다." };
    }
    if (normalized === "bosstype") {
      const text = String(value || "");
      if (text === "special") return { label: "special · 특수 보스", body: "특수 보스 그룹으로 표시/정렬될 수 있습니다." };
      if (text === "normal") return { label: "normal · 일반 보스", body: "일반 보스 그룹으로 표시/정렬됩니다." };
      return text ? { label: text, body: "보스 분류 값입니다. normal/special 프리셋 사용을 권장합니다." } : { label: "보스 분류 없음", body: "보스 분류가 비어 있습니다." };
    }
    if (normalized === "stackable") {
      const boolValue = value === true || String(value).toLowerCase() === "true";
      return boolValue
        ? { label: "true · 겹치기 가능", body: "같은 아이템을 인벤토리 한 칸에 수량으로 합칠 수 있습니다. 재료/강화권 계열에 적합합니다." }
        : { label: "false · 개별 칸 사용", body: "같은 이름이어도 각각 별도 칸을 차지합니다. 강화 수치/옵션/장착 상태가 따로 필요한 장비에 적합합니다." };
    }
    if (normalized === "adminnote") {
      return value ? { label: "관리자 메모 있음", body: "게임 화면에는 표시되지 않는 내부 메모가 들어 있습니다." } : { label: "관리자 메모 없음", body: "운영/밸런스 메모가 아직 비어 있습니다." };
    }
    return null;
  }

  function renderFieldValueHintInline(key, value) {
    const hint = getAdminFieldValueHint(key, value);
    if (!hint) return "";
    return `<div class="field-value-hint"><strong>${escapeHtml(hint.label)}</strong> — ${escapeHtml(hint.body)}</div>`;
  }

  function formatValueWithFieldHint(key, value) {
    return `${escapeHtml(formatValue(value))}${renderFieldValueHintInline(key, value)}`;
  }

  function setStatus(message, kind) {
    const el = $("[data-admin-status]");
    if (!el) return;
    el.textContent = message;
    el.dataset.kind = kind || "info";
  }

  function getApiInput() {
    return $("[data-admin-api-base-url]");
  }

  function buildSiblingPageUrl(fileName) {
    try {
      return new URL(fileName, window.location.href).toString();
    } catch (error) {
      return String(fileName || "");
    }
  }

  function getCurrentAdminPageUrl() {
    try {
      return window.location.href;
    } catch (error) {
      return "admin.html";
    }
  }

  function getGamePageUrl() {
    return buildSiblingPageUrl("index.html");
  }

  function syncLocationHints() {
    const currentUrl = getCurrentAdminPageUrl();
    const currentTarget = $("[data-admin-current-url]");
    const gameLink = $("[data-admin-game-url]");
    if (currentTarget) currentTarget.textContent = currentUrl;
    if (gameLink) gameLink.href = getGamePageUrl();
  }

  async function copyCurrentAdminPageUrl() {
    const url = getCurrentAdminPageUrl();
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(url);
        setStatus(`관리자 페이지 주소 복사됨: ${url}`, "ok");
        return { ok: true, url, copied: true, method: "clipboard" };
      }
    } catch (error) {
      // clipboard 권한이 막힌 브라우저에서는 아래 fallback을 사용합니다.
    }

    try {
      const input = document.createElement("input");
      input.value = url;
      input.setAttribute("readonly", "readonly");
      input.style.position = "fixed";
      input.style.opacity = "0";
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
      setStatus(`관리자 페이지 주소 복사됨: ${url}`, "ok");
      return { ok: true, url, copied: true, method: "fallback" };
    } catch (error) {
      setStatus(`주소 복사 실패: ${url}`, "error");
      return { ok: false, url, copied: false, error: error && error.message ? error.message : String(error) };
    }
  }

  function syncApiInput() {
    const input = getApiInput();
    if (!input || !window.RpgGameApi) return;
    input.value = window.RpgGameApi.getApiBaseUrl();
  }

  function getAdminWriteKeyInput() {
    return $(`[data-admin-write-dev-key]`);
  }

  function hasAdminWriteDevKey() {
    return !!(window.RpgGameApi && window.RpgGameApi.hasAdminWriteDevKey && window.RpgGameApi.hasAdminWriteDevKey());
  }

  function renderAdminWriteKeyStatus() {
    const target = $(`[data-admin-write-key-status]`);
    if (!target || !window.RpgGameApi) return;
    const ready = hasAdminWriteDevKey();
    target.innerHTML = ready
      ? `<span class="pill good">write key set</span>`
      : `<span class="pill blocked">write key missing</span>`;
  }

  function syncAdminWriteDevKeyInput() {
    const input = getAdminWriteKeyInput();
    if (input && window.RpgGameApi && window.RpgGameApi.getAdminWriteDevKey) input.value = window.RpgGameApi.getAdminWriteDevKey();
    renderAdminWriteKeyStatus();
  }

  function saveAdminWriteDevKeyFromInput() {
    ensureApi();
    const input = getAdminWriteKeyInput();
    const value = input ? input.value.trim() : "";
    if (!value) {
      const error = new Error(`관리자 쓰기 dev key를 입력해 주세요. 로컬 기본 예시는 ${ADMIN_WRITE_DEV_KEY_EXAMPLE} 입니다.`);
      setStatus(error.message, "error");
      renderAdminWriteKeyStatus();
      throw error;
    }
    window.RpgGameApi.setAdminWriteDevKey(value);
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key가 이 브라우저 탭에 저장됐습니다.", "ok");
    return value;
  }

  function clearAdminWriteDevKey() {
    ensureApi();
    window.RpgGameApi.clearAdminWriteDevKey();
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key를 지웠습니다. 실제 적용/되돌리기는 다시 잠깁니다.", "info");
    return "";
  }

  function requireAdminWriteDevKeyForUi(actionLabel) {
    if (hasAdminWriteDevKey()) return true;
    const message = `${actionLabel || "관리자 쓰기 작업"} 전에 관리자 쓰기 dev key를 먼저 설정해 주세요.`;
    setStatus(message, "error");
    const target = $(`[data-admin-edit-draft-result]`) || $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="error">${escapeHtml(message)}<br>관리자 페이지의 <strong>쓰기 잠금</strong> 영역에서 dev key를 저장한 뒤 다시 시도하세요.</div>`;
    throw new Error(message);
  }

  function ensureApi() {
    if (!window.RpgGameApi) throw new Error("RpgGameApi를 찾을 수 없습니다. game-api-client.js 로딩 순서를 확인하세요.");
    if (typeof window.RpgGameApi.fetchAdminOverview !== "function") throw new Error("fetchAdminOverview 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminSaveSnapshots !== "function") throw new Error("listAdminSaveSnapshots 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogDomains !== "function") throw new Error("listAdminMasterCatalogDomains 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogRows !== "function") throw new Error("listAdminMasterCatalogRows 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterCreateBlueprint !== "function") throw new Error("fetchAdminMasterCreateBlueprint 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataDetail !== "function") throw new Error("fetchAdminMasterDataDetail 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataRelations !== "function") throw new Error("fetchAdminMasterDataRelations 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.applyAdminMasterDataEdit !== "function") throw new Error("applyAdminMasterDataEdit 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminChangeLogs !== "function") throw new Error("listAdminChangeLogs 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminChangeLogDetail !== "function") throw new Error("fetchAdminChangeLogDetail 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.previewAdminChangeLogRollback !== "function") throw new Error("previewAdminChangeLogRollback 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.applyAdminChangeLogRollback !== "function") throw new Error("applyAdminChangeLogRollback 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchMasterData !== "function") throw new Error("fetchMasterData 함수를 찾을 수 없습니다.");
  }

  function readSnapshotFiltersFromDom() {
    const limitEl = $("[data-admin-filter-limit]");
    const userIdEl = $("[data-admin-filter-user-id]");
    const slotKeyEl = $("[data-admin-filter-slot-key]");
    const sourceEl = $("[data-admin-filter-source]");
    const defaultOnlyEl = $("[data-admin-filter-default-only]");
    const sortEl = $("[data-admin-filter-sort]");
    const userId = userIdEl && userIdEl.value.trim() ? Number(userIdEl.value.trim()) : undefined;
    return {
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_SNAPSHOT_LIMIT,
      userId: Number.isFinite(userId) ? userId : undefined,
      slotKey: slotKeyEl ? slotKeyEl.value.trim() : "",
      source: sourceEl ? sourceEl.value.trim() : "",
      defaultOnly: !!(defaultOnlyEl && defaultOnlyEl.checked),
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_SNAPSHOT_SORT,
    };
  }

  function resetSnapshotFilters(options) {
    const opts = options || {};
    const limitEl = $("[data-admin-filter-limit]");
    const userIdEl = $("[data-admin-filter-user-id]");
    const slotKeyEl = $("[data-admin-filter-slot-key]");
    const sourceEl = $("[data-admin-filter-source]");
    const defaultOnlyEl = $("[data-admin-filter-default-only]");
    const sortEl = $("[data-admin-filter-sort]");
    if (limitEl) limitEl.value = String(DEFAULT_SNAPSHOT_LIMIT);
    if (userIdEl) userIdEl.value = "";
    if (slotKeyEl) slotKeyEl.value = "";
    if (sourceEl) sourceEl.value = "";
    if (defaultOnlyEl) defaultOnlyEl.checked = false;
    if (sortEl) sortEl.value = DEFAULT_SNAPSHOT_SORT;
    if (!opts.silent) setStatus("세이브 스냅샷 필터 초기화", "info");
    return readSnapshotFiltersFromDom();
  }

  function describeSnapshotFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.userId) parts.push(`userId=${f.userId}`);
    if (f.slotKey) parts.push(`slotKey=${f.slotKey}`);
    if (f.source) parts.push(`source=${f.source}`);
    if (f.defaultOnly) parts.push("defaultOnly=true");
    if (f.sort && f.sort !== DEFAULT_SNAPSHOT_SORT) parts.push(`sort=${f.sort}`);
    return parts.length ? parts.join(", ") : "필터 없음";
  }


  function getAdminChangeLogsApi() {
    if (!window.RpgAdminChangeLogs) throw new Error("RpgAdminChangeLogs is not loaded");
    return window.RpgAdminChangeLogs;
  }

  function configureAdminChangeLogs() {
    return getAdminChangeLogsApi().configure({
      querySelector: $,
      escapeHtml,
      formatValue,
      formatClock,
      ensureApi,
      setStatus,
      renderAdminChangeValueCell,
      renderAdminRollbackMismatchValueCell,
      renderAdminOperationResultBanner,
      renderAdminCreateDeleteBlockerSummary,
      requireAdminWriteDevKeyForUi,
      refreshAdminMasterCatalog,
      runPostWriteMasterApiVerification,
      readMasterCatalogFiltersFromDom,
      DEFAULT_CHANGE_LOG_LIMIT,
      DEFAULT_CHANGE_LOG_SORT,
      DEFAULT_TIMEOUT_MS,
      ADMIN_EDIT_APPLY_TIMEOUT_MS,
      ADMIN_ROLLBACK_CONFIRM_TEXT,
      ADMIN_CREATE_DELETE_CONFIRM_TEXT,
      ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
      ADMIN_CHANGE_LOG_ACTION_FILTERS: ADMIN_CHANGE_LOG_ACTION_FILTERS.slice(),
    });
  }

  function getAdminChangeLogsReadiness() {
    return getAdminChangeLogsApi().getReadiness();
  }

  function readChangeLogFiltersFromDom() {
    return getAdminChangeLogsApi().readChangeLogFiltersFromDom();
  }

  function resetChangeLogFilters(options) {
    return getAdminChangeLogsApi().resetChangeLogFilters(options);
  }

  function describeChangeLogFilters(filters) {
    return getAdminChangeLogsApi().describeChangeLogFilters(filters);
  }

  function renderAdminChangeLogs(logsPayload) {
    return getAdminChangeLogsApi().renderAdminChangeLogs(logsPayload);
  }

  function renderAdminChangeLogDetail(detailPayload) {
    return getAdminChangeLogsApi().renderAdminChangeLogDetail(detailPayload);
  }

  function readAdminRollbackControls() {
    return getAdminChangeLogsApi().readAdminRollbackControls();
  }

  function renderAdminRollbackResult(payload) {
    return getAdminChangeLogsApi().renderAdminRollbackResult(payload);
  }

  function openAdminChangeLogDetail(changeLogId, options) {
    return getAdminChangeLogsApi().openAdminChangeLogDetail(changeLogId, options);
  }

  function previewAdminChangeLogRollback(options) {
    return getAdminChangeLogsApi().previewAdminChangeLogRollback(options);
  }

  function applyAdminChangeLogRollback(options) {
    return getAdminChangeLogsApi().applyAdminChangeLogRollback(options);
  }

  function readAdminCreateDeleteControls() {
    return getAdminChangeLogsApi().readAdminCreateDeleteControls();
  }

  function renderAdminCreateDeleteResult(payload) {
    return getAdminChangeLogsApi().renderAdminCreateDeleteResult(payload);
  }

  function previewAdminCreateDeleteRollback(options) {
    return getAdminChangeLogsApi().previewAdminCreateDeleteRollback(options);
  }

  function applyAdminCreateDeleteRollback(options) {
    return getAdminChangeLogsApi().applyAdminCreateDeleteRollback(options);
  }

  function readAdminCreateDeleteRestoreControls() {
    return getAdminChangeLogsApi().readAdminCreateDeleteRestoreControls();
  }

  function renderAdminCreateDeleteRestoreResult(payload) {
    return getAdminChangeLogsApi().renderAdminCreateDeleteRestoreResult(payload);
  }

  function previewAdminCreateDeleteRestore(options) {
    return getAdminChangeLogsApi().previewAdminCreateDeleteRestore(options);
  }

  function applyAdminCreateDeleteRestore(options) {
    return getAdminChangeLogsApi().applyAdminCreateDeleteRestore(options);
  }

  function refreshAdminChangeLogs(options) {
    return getAdminChangeLogsApi().refreshAdminChangeLogs(options);
  }

  function applyAdminChangeLogActionShortcut(action) {
    return getAdminChangeLogsApi().applyAdminChangeLogActionShortcut(action);
  }

  function readMasterCatalogFiltersFromDom() {
    const domainEl = $("[data-admin-master-domain]");
    const limitEl = $("[data-admin-master-limit]");
    const queryEl = $("[data-admin-master-query]");
    const enabledEl = $("[data-admin-master-enabled]");
    const sortEl = $("[data-admin-master-sort]");
    const pageEl = $("[data-admin-master-page]");
    const pageValue = pageEl && pageEl.value ? Number(pageEl.value) : 1;
    return {
      domain: domainEl && domainEl.value ? domainEl.value : DEFAULT_MASTER_DOMAIN,
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_MASTER_LIMIT,
      page: Number.isFinite(pageValue) && pageValue > 0 ? Math.floor(pageValue) : 1,
      query: queryEl ? queryEl.value.trim() : "",
      enabled: enabledEl && enabledEl.value ? enabledEl.value : "all",
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_MASTER_SORT,
    };
  }

  function resetMasterCatalogFilters(options) {
    const opts = options || {};
    const domainEl = $("[data-admin-master-domain]");
    const limitEl = $("[data-admin-master-limit]");
    const queryEl = $("[data-admin-master-query]");
    const enabledEl = $("[data-admin-master-enabled]");
    const sortEl = $("[data-admin-master-sort]");
    const pageEl = $("[data-admin-master-page]");
    if (domainEl) domainEl.value = DEFAULT_MASTER_DOMAIN;
    if (limitEl) limitEl.value = String(DEFAULT_MASTER_LIMIT);
    if (pageEl) pageEl.value = "1";
    if (queryEl) queryEl.value = "";
    if (enabledEl) enabledEl.value = "all";
    if (sortEl) sortEl.value = DEFAULT_MASTER_SORT;
    if (!opts.silent) setStatus("마스터 데이터 카탈로그 필터 초기화", "info");
    return readMasterCatalogFiltersFromDom();
  }

  function describeMasterCatalogFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.domain) parts.push(`domain=${f.domain}`);
    if (f.query) parts.push(`query=${f.query}`);
    if (f.enabled && f.enabled !== "all") parts.push(`enabled=${f.enabled}`);
    if (f.sort && f.sort !== DEFAULT_MASTER_SORT) parts.push(`sort=${f.sort}`);
    if (f.page && Number(f.page) > 1) parts.push(`page=${f.page}`);
    return parts.length ? parts.join(", ") : "마스터 필터 없음";
  }

  function syncMasterDomainOptions(domainsPayload) {
    const select = $("[data-admin-master-domain]");
    const meta = $("[data-admin-master-domain-meta]");
    if (!select) return;
    const current = select.value || DEFAULT_MASTER_DOMAIN;
    const domains = Array.isArray(domainsPayload && domainsPayload.domains) ? domainsPayload.domains : [];
    if (!domains.length) return;
    select.innerHTML = domains.map((domain) => `
      <option value="${escapeHtml(domain.key)}">${escapeHtml(domain.label || domain.key)} (${escapeHtml(formatValue(domain.total))})</option>
    `).join("");
    const nextValue = domains.some((domain) => domain.key === current) ? current : (domainsPayload.defaultDomain || DEFAULT_MASTER_DOMAIN);
    select.value = nextValue;
    if (meta) meta.textContent = `${formatValue(domains.length)} domains · raw JSON hidden · assets hidden`;
    syncAdminCreateDomainOptions(domainsPayload);
  }


  function readAdminCreateBlueprintFiltersFromDom() {
    const domainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    return {
      domain: domainEl && domainEl.value ? domainEl.value : (masterDomainEl && masterDomainEl.value ? masterDomainEl.value : DEFAULT_MASTER_DOMAIN),
    };
  }

  function syncAdminCreateDomainOptions(domainsPayload) {
    const select = $("[data-admin-create-domain]");
    if (!select) return;
    const current = select.value || DEFAULT_MASTER_DOMAIN;
    const domains = Array.isArray(domainsPayload && domainsPayload.domains) ? domainsPayload.domains : [];
    if (!domains.length) return;
    select.innerHTML = domains.map((domain) => `
      <option value="${escapeHtml(domain.key)}">${escapeHtml(domain.label || domain.key)} (${escapeHtml(formatValue(domain.total))})</option>
    `).join("");
    select.value = domains.some((domain) => domain.key === current) ? current : (domainsPayload.defaultDomain || DEFAULT_MASTER_DOMAIN);
  }

  function syncAdminCreateDomainFromCatalog() {
    const createDomainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    if (createDomainEl && masterDomainEl && masterDomainEl.value) createDomainEl.value = masterDomainEl.value;
    return readAdminCreateBlueprintFiltersFromDom();
  }

  async function fetchAdminReadOnlyPageData(options) {
    ensureApi();
    const opts = options || {};
    const timeoutMs = opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS;
    const filters = opts.snapshotFilters || readSnapshotFiltersFromDom();
    const masterCatalogFilters = opts.masterCatalogFilters || readMasterCatalogFiltersFromDom();
    const changeLogFilters = opts.changeLogFilters || readChangeLogFiltersFromDom();
    const createBlueprintFilters = opts.createBlueprintFilters || readAdminCreateBlueprintFiltersFromDom();
    const [overview, snapshots, masterDomains, masterCatalog, changeLogs, createBlueprint] = await Promise.all([
      window.RpgGameApi.fetchAdminOverview({ timeoutMs }),
      window.RpgGameApi.listAdminSaveSnapshots({ timeoutMs, ...filters }),
      window.RpgGameApi.listAdminMasterCatalogDomains({ timeoutMs }),
      window.RpgGameApi.listAdminMasterCatalogRows({ timeoutMs, ...masterCatalogFilters }),
      window.RpgGameApi.listAdminChangeLogs({ timeoutMs, ...changeLogFilters }),
      window.RpgGameApi.fetchAdminMasterCreateBlueprint({ timeoutMs, ...createBlueprintFilters }),
    ]);
    return { overview, snapshots, masterDomains, masterCatalog, changeLogs, createBlueprint, snapshotFilters: filters, masterCatalogFilters, changeLogFilters, createBlueprintFilters };
  }

  function renderCards(overviewPayload) {
    const master = overviewPayload.masterData || {};
    const save = overviewPayload.saveSnapshots || {};
    const users = overviewPayload.users || {};
    const readiness = overviewPayload.readiness || {};
    const target = $("[data-admin-cards]");
    if (!target) return;
    const writeLocked = readiness.safeForAdminWriteUi === false;
    target.innerHTML = `
      <div class="card"><div class="label">읽기 전용</div><div class="value small"><span class="pill good">${escapeHtml(formatValue(overviewPayload.readOnly))}</span></div></div>
      <div class="card"><div class="label">마스터 행 수</div><div class="value">${escapeHtml(formatValue(master.summary && master.summary.totalRows))}</div></div>
      <div class="card"><div class="label">DB 세이브 슬롯</div><div class="value">${escapeHtml(formatValue(save.totalSlots))}</div></div>
      <div class="card"><div class="label">저장 유저 수</div><div class="value">${escapeHtml(formatValue(save.usersWithSaves))}</div></div>
      <div class="card"><div class="label">전체 유저</div><div class="value">${escapeHtml(formatValue(users.total))}</div></div>
      <div class="card"><div class="label">관리자 수</div><div class="value">${escapeHtml(formatValue(users.admins))}</div></div>
      <div class="card"><div class="label">최근 저장</div><div class="value small">${escapeHtml(formatClock(save.latestUpdatedAt))}</div></div>
      <div class="card"><div class="label">전체 쓰기 UI</div><div class="value small"><span class="pill ${writeLocked ? "blocked" : "warn"}">${writeLocked ? "blocked" : "check"}</span></div></div>
      <div class="card"><div class="label">마스터 편집 적용</div><div class="value small"><span class="pill ${readiness.guardedMasterEditApplyReady ? "good" : "blocked"}">${readiness.guardedMasterEditApplyReady ? "guarded" : "blocked"}</span></div></div>
      <div class="card"><div class="label">변경 이력 되돌리기</div><div class="value small"><span class="pill ${readiness.guardedRollbackReady ? "good" : "blocked"}">${readiness.guardedRollbackReady ? "guarded" : "blocked"}</span></div></div>
    `;
  }

  function renderMasterTable(masterData) {
    const target = $("[data-admin-master-table]");
    const meta = $("[data-admin-master-meta]");
    if (!target) return;
    const entries = Object.entries(masterData || {}).filter(([key, value]) => key !== "summary" && value && typeof value === "object");
    if (meta) meta.textContent = `${formatValue(masterData && masterData.summary && masterData.summary.domains)} domains`;
    if (!entries.length) {
      target.innerHTML = `<div class="empty">마스터 데이터 count가 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>도메인</th><th>전체</th><th>활성</th><th>비활성</th></tr></thead>
        <tbody>
          ${entries.map(([key, value]) => `
            <tr>
              <td>${escapeHtml(key)}</td>
              <td>${escapeHtml(formatValue(value.total))}</td>
              <td>${escapeHtml(formatValue(value.enabled))}</td>
              <td>${escapeHtml(formatValue(value.disabled))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }



  function syncMasterCatalogPageInput(page) {
    const pageEl = $("[data-admin-master-page]");
    if (pageEl) pageEl.value = String(Math.max(1, Number(page) || 1));
  }

  function renderMasterCatalogPagination(catalogPayload) {
    const target = $("[data-admin-master-catalog-pagination]");
    if (!target) return;
    const page = Math.max(1, Number(catalogPayload.page) || 1);
    const totalPages = Math.max(1, Number(catalogPayload.totalPages) || 1);
    const total = Number(catalogPayload.total) || 0;
    const limit = Math.max(1, Number(catalogPayload.limit) || DEFAULT_MASTER_LIMIT);
    const start = total ? ((page - 1) * limit) + 1 : 0;
    const end = total ? Math.min(page * limit, total) : 0;
    syncMasterCatalogPageInput(page);
    target.innerHTML = `
      <div class="catalog-pagination-meta">${escapeHtml(formatValue(start))}~${escapeHtml(formatValue(end))} / ${escapeHtml(formatValue(total))} · ${escapeHtml(formatValue(page))}/${escapeHtml(formatValue(totalPages))} 페이지</div>
      <div class="catalog-pagination-actions">
        <button class="btn mini" type="button" data-admin-action="master-catalog-first-page" ${page <= 1 ? "disabled" : ""}>처음</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-prev-page" ${page <= 1 ? "disabled" : ""}>이전</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-next-page" ${page >= totalPages ? "disabled" : ""}>다음</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-last-page" ${page >= totalPages ? "disabled" : ""} data-admin-master-total-pages="${escapeHtml(totalPages)}">끝</button>
      </div>
    `;
  }

  function markSelectedMasterCatalogRow(domain, id) {
    const safeDomain = String(domain || "");
    const safeId = String(id || "");
    Array.from(document.querySelectorAll("[data-admin-master-row-id]")).forEach((row) => {
      const matches = row.getAttribute("data-admin-master-row-domain") === safeDomain && row.getAttribute("data-admin-master-row-id") === safeId;
      row.classList.toggle("catalog-row-selected", matches);
      const marker = row.querySelector("[data-admin-master-row-selected]");
      if (marker) marker.innerHTML = matches ? `<span class="pill good">선택됨</span>` : "";
    });
  }

  async function refreshMasterCatalogWithPage(page) {
    syncMasterCatalogPageInput(page);
    return refreshAdminReadOnlyPage({
      snapshotFilters: readSnapshotFiltersFromDom(),
      masterCatalogFilters: readMasterCatalogFiltersFromDom(),
      changeLogFilters: readChangeLogFiltersFromDom(),
    });
  }

  function renderMasterCatalogTable(catalogPayload) {
    const target = $("[data-admin-master-catalog-table]");
    const meta = $("[data-admin-master-catalog-meta]");
    if (!target) return;
    const rows = Array.isArray(catalogPayload.rows) ? catalogPayload.rows : [];
    const columns = Array.isArray(catalogPayload.columns) ? catalogPayload.columns : [];
    const filters = catalogPayload.filters || {};
    const totalAllNote = catalogPayload.totalAll !== undefined ? ` / 전체 ${formatValue(catalogPayload.totalAll)}` : "";
    const page = Number(catalogPayload.page) || 1;
    const totalPages = Number(catalogPayload.totalPages) || 1;
    const filterNote = filters.hasActiveFilters ? ` · ${describeMasterCatalogFilters(filters)}` : "";
    if (meta) meta.textContent = `${escapeHtml(catalogPayload.domainLabel || catalogPayload.domain || "-")} · ${formatValue(rows.length)} / ${formatValue(catalogPayload.total)} shown · page ${formatValue(page)} / ${formatValue(totalPages)}${totalAllNote}${filterNote}`;
    renderMasterCatalogPagination(catalogPayload);
    if (!rows.length || !columns.length) {
      target.innerHTML = `<div class="empty">마스터 데이터 카탈로그 결과가 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>상세</th>${columns.map((column) => `<th title="${escapeHtml((getAdminFieldHelp(column.key) && getAdminFieldHelp(column.key).body) || column.key)}">${escapeHtml(column.label || column.key)}${renderFieldHelpBadge(column.key)}</th>`).join("")}<th>원본 JSON</th><th>이미지</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const cells = row.cells || {};
            return `
              <tr data-admin-master-row-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-master-row-id="${escapeHtml(row.id)}">
                <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button><span data-admin-master-row-selected></span></td>
                ${columns.map((column) => `<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>`).join("")}
                <td><span class="pill ${row.rawJsonReturned ? "blocked" : "good"}">${row.rawJsonReturned ? "returned" : "hidden"}</span></td>
                <td><span class="pill ${row.assetsReturned ? "blocked" : "good"}">${row.assetsReturned ? "returned" : "hidden"}</span></td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
    if (currentMasterDetailPayload && currentMasterDetailPayload.domain && currentMasterDetailPayload.id) {
      markSelectedMasterCatalogRow(currentMasterDetailPayload.domain, currentMasterDetailPayload.id);
    }
  }



  function getAdminCreateLifecycleApi() {
    if (!window.RpgAdminCreateLifecycle) throw new Error("RpgAdminCreateLifecycle is not loaded");
    return window.RpgAdminCreateLifecycle;
  }

  function configureAdminCreateLifecycle() {
    return getAdminCreateLifecycleApi().configure({
      querySelector: $,
      escapeHtml,
      formatValue,
      formatValueWithFieldHint,
      renderFieldHelpBadge,
      renderFieldHelpInline,
      renderFieldValueHintInline,
      renderAdminDraftTypeBadge,
      makeDraftOriginalValue,
      parseDraftOriginalValue,
      renderAdminDraftSelectOptionsHtml,
      filterAdminDraftSelectOptions,
      normalizeAdminDraftFieldKey,
      normalizeAdminRelationSearchText,
      getAdminEquipSlotDisplayName,
      formatAdminRelationInfoText,
      renderAdminRelationOpenTargetButton,
      ensureApi,
      setStatus,
      requireAdminWriteDevKeyForUi,
      refreshAdminChangeLogs,
      readChangeLogFiltersFromDom,
      refreshAdminReadOnlyPage,
      readSnapshotFiltersFromDom,
      readMasterCatalogFiltersFromDom,
      runPostWriteMasterApiVerification,
      DEFAULT_MASTER_DOMAIN,
      DEFAULT_TIMEOUT_MS,
      ADMIN_EDIT_APPLY_TIMEOUT_MS,
      ADMIN_CREATE_APPLY_CONFIRM_TEXT,
      ADMIN_CREATE_DELETE_CONFIRM_TEXT,
      ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
      ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT,
      ADMIN_CHANGE_LOG_ACTION_FILTERS: ADMIN_CHANGE_LOG_ACTION_FILTERS.slice(),
      ADMIN_DRAFT_SELECT_FIELD_OPTIONS,
      ADMIN_DRAFT_TEXTAREA_FIELDS,
    });
  }

  function getAdminCreateLifecycleReadiness() {
    return getAdminCreateLifecycleApi().getReadiness();
  }

  function getAdminCreateBlueprintFieldInputKind(field) {
    return getAdminCreateLifecycleApi().getAdminCreateBlueprintFieldInputKind(field);
  }

  function getAdminCreateBlueprintRequiredKeys(domain, blueprint) {
    return getAdminCreateLifecycleApi().getAdminCreateBlueprintRequiredKeys(domain, blueprint);
  }

  function getAdminCreateBlueprintDefaultDraft(domain, blueprint) {
    return getAdminCreateLifecycleApi().getAdminCreateBlueprintDefaultDraft(domain, blueprint);
  }

  function getAdminCreateFieldDefinition(key) {
    return getAdminCreateLifecycleApi().getAdminCreateFieldDefinition(key);
  }

  function getAdminCreateRelationDefinition(key) {
    return getAdminCreateLifecycleApi().getAdminCreateRelationDefinition(key);
  }

  function applyAdminCreateRelationOptionFilter(input) {
    return getAdminCreateLifecycleApi().applyAdminCreateRelationOptionFilter(input);
  }

  function refreshDependentAdminCreateRelationSelects(changedKey) {
    return getAdminCreateLifecycleApi().refreshDependentAdminCreateRelationSelects(changedKey);
  }

  function renderAdminCreateLifecycleDependencyGuards(lifecycle) {
    return getAdminCreateLifecycleApi().renderAdminCreateLifecycleDependencyGuards(lifecycle);
  }

  function renderAdminCreateLifecycleBatchResult(steps, options) {
    return getAdminCreateLifecycleApi().renderAdminCreateLifecycleBatchResult(steps, options);
  }

  async function runAdminCreateLifecycleBatchCheck() {
    return getAdminCreateLifecycleApi().runAdminCreateLifecycleBatchCheck();
  }

  function renderAdminOperationResultBanner(options) {
    return getAdminCreateLifecycleApi().renderAdminOperationResultBanner(options);
  }

  function renderAdminCreateDeleteBlockerSummary(dependencyChecks) {
    return getAdminCreateLifecycleApi().renderAdminCreateDeleteBlockerSummary(dependencyChecks);
  }

  function renderAdminCreateLifecycleGuide(blueprintPayload) {
    return getAdminCreateLifecycleApi().renderAdminCreateLifecycleGuide(blueprintPayload);
  }

  function getAdminCreateLifecycleGuideReadiness() {
    return getAdminCreateLifecycleApi().getAdminCreateLifecycleGuideReadiness();
  }

  function getAdminJsSplitReadiness() {
    const scriptSources = Array.from(document.querySelectorAll("script[src]")).map((script) => script.getAttribute("src") || "");
    const gameApiIndex = scriptSources.findIndex((src) => src.includes("game-api-client.js"));
    const layoutShellIndex = scriptSources.findIndex((src) => src.includes("admin-layout-shell.js"));
    const adminPageIndex = scriptSources.findIndex((src) => src.includes("admin-page-readonly.js"));
    const changeLogsIndex = scriptSources.findIndex((src) => src.includes("admin/admin-change-logs.js"));
    const createLifecycleIndex = scriptSources.findIndex((src) => src.includes("admin/admin-create-lifecycle.js"));
    const requiredGlobals = ADMIN_JS_SPLIT_REQUIRED_GLOBALS.map((key) => ({
      key,
      ok: key === "RpgGameApi" ? !!window.RpgGameApi : typeof window[key] !== "undefined",
    }));
    const missingGlobals = requiredGlobals.filter((item) => !item.ok).map((item) => item.key);
    const exportCount = window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage === "object" ? Object.keys(window.RpgAdminReadOnlyPage).length : 0;
    const entryFileStillSingle = scriptSources.some((src) => src.includes("admin-page-readonly.js"));
    const scriptOrderReady = gameApiIndex >= 0 && layoutShellIndex >= 0 && changeLogsIndex >= 0 && createLifecycleIndex >= 0 && adminPageIndex >= 0 && gameApiIndex < layoutShellIndex && layoutShellIndex < changeLogsIndex && changeLogsIndex < createLifecycleIndex && createLifecycleIndex < adminPageIndex;
    const candidateCount = ADMIN_JS_SPLIT_PHASES.filter((phase) => phase.status !== "keep-last").length;
    return {
      ok: !!document.querySelector("[data-admin-js-split-readiness]") && scriptOrderReady && missingGlobals.length === 0 && exportCount > 0,
      hasPanel: !!document.querySelector("[data-admin-js-split-readiness]"),
      scriptSources,
      scriptOrderReady,
      requiredGlobals,
      missingGlobals,
      exportCount,
      layoutShellIndex,
      changeLogsIndex,
      createLifecycleIndex,
      entryFileStillSingle,
      layoutShellExternalReady: layoutShellIndex >= 0 && !!window.RpgAdminLayoutShell,
      changeLogsExternalReady: changeLogsIndex >= 0 && !!window.RpgAdminChangeLogs,
      createLifecycleExternalReady: createLifecycleIndex >= 0 && !!window.RpgAdminCreateLifecycle,
      candidateCount,
      phases: ADMIN_JS_SPLIT_PHASES.slice(),
      nextSafeStep: "master detail/catalog 분리 전 계약 준비",
    };
  }

  function getAdminChangeLogSplitContractReadiness() {
    const contract = ADMIN_CHANGE_LOG_SPLIT_CONTRACT;
    const requiredApiMethods = contract.requiredApiMethods.map((key) => ({
      key,
      ok: !!(window.RpgGameApi && typeof window.RpgGameApi[key] === "function"),
    }));
    const requiredWindowExports = contract.requiredWindowExports.map((key) => ({
      key,
      ok: typeof window[key] === "function" || !!(window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage[key] === "function"),
    }));
    const domTargets = contract.domTargets.map((selector) => ({
      selector,
      ok: !!document.querySelector(selector),
    }));
    const actionFilters = contract.actionFilters.map((key) => ({
      key,
      ok: ADMIN_CHANGE_LOG_ACTION_FILTERS.includes(key),
    }));
    const missingApiMethods = requiredApiMethods.filter((item) => !item.ok).map((item) => item.key);
    const missingWindowExports = requiredWindowExports.filter((item) => !item.ok).map((item) => item.key);
    const missingDomTargets = domTargets.filter((item) => !item.ok).map((item) => item.selector);
    const missingActionFilters = actionFilters.filter((item) => !item.ok).map((item) => item.key);
    const ok = contract.status === "contract-frozen-v186" && missingApiMethods.length === 0 && missingWindowExports.length === 0 && missingDomTargets.length === 0 && missingActionFilters.length === 0;
    return {
      ok,
      contract,
      status: contract.status,
      currentFile: contract.currentFile,
      nextFile: contract.nextFile,
      requiredApiMethods,
      requiredWindowExports,
      domTargets,
      actionFilters,
      delegatedActions: contract.delegatedActions.slice(),
      splitBoundary: contract.splitBoundary.slice(),
      missingApiMethods,
      missingWindowExports,
      missingDomTargets,
      missingActionFilters,
      apiMethodCount: requiredApiMethods.length,
      windowExportCount: requiredWindowExports.length,
      domTargetCount: domTargets.length,
      delegatedActionCount: contract.delegatedActions.length,
    };
  }

  function renderAdminChangeLogSplitContractReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminChangeLogSplitContractReadiness();
    const apiHtml = readiness.requiredApiMethods.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${item.ok ? "ok" : "missing"}</span>`).join(" ");
    const exportRows = readiness.requiredWindowExports.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const domRows = readiness.domTargets.map((item) => `<tr><td><code>${escapeHtml(item.selector)}</code></td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const boundaryHtml = readiness.splitBoundary.map((item) => `<span class="pill warn">${escapeHtml(item)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "change logs 분리 계약 고정 완료" : "change logs 분리 계약 확인 필요",
          subtitle: `${readiness.currentFile} → ${readiness.nextFile} 이동 전, 필요한 API/window/DOM 계약을 먼저 고정했습니다.`,
          metrics: [
            { label: "API 함수", value: readiness.apiMethodCount, tone: readiness.missingApiMethods.length ? "blocked" : "good" },
            { label: "window export", value: readiness.windowExportCount, tone: readiness.missingWindowExports.length ? "blocked" : "good" },
            { label: "DOM target", value: readiness.domTargetCount, tone: readiness.missingDomTargets.length ? "blocked" : "good" },
            { label: "delegated action", value: readiness.delegatedActionCount, tone: "warn" },
          ],
        })}
        <div class="draft-preview-summary">${apiHtml}</div>
        <div class="draft-preview-summary">${boundaryHtml}</div>
        <div class="filter-help">다음 v187에서 실제 파일을 분리할 때는 이 계약이 깨지지 않는지 먼저 확인하고, <code>admin-page-readonly.js</code>에는 호환 wrapper만 남기는 방향이 안전합니다.</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>window export</th><th>상태</th></tr></thead><tbody>${exportRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>DOM target</th><th>상태</th></tr></thead><tbody>${domRows}</tbody></table></div>
        </div>
      </div>
    `;
  }


  function getAdminCreateLifecycleSplitContractReadiness() {
    return getAdminCreateLifecycleApi().getAdminCreateLifecycleSplitContractReadiness();
  }

  function renderAdminCreateLifecycleSplitContractReadiness(contractReadiness) {
    return getAdminCreateLifecycleApi().renderAdminCreateLifecycleSplitContractReadiness(contractReadiness);
  }

  function getAdminEditDraftSplitContractReadiness() {
    const contract = ADMIN_EDIT_DRAFT_SPLIT_CONTRACT;
    const requiredApiMethods = contract.requiredApiMethods.map((key) => ({
      key,
      ok: !!(window.RpgGameApi && typeof window.RpgGameApi[key] === "function"),
    }));
    const requiredWindowExports = contract.requiredWindowExports.map((key) => ({
      key,
      ok: typeof window[key] === "function" || !!(window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage[key] === "function"),
    }));
    const domTargets = contract.domTargets.map((selector) => ({
      selector,
      ok: !!document.querySelector(selector),
    }));
    const confirmTexts = contract.confirmTexts.map((item) => ({
      key: item.key,
      value: item.value,
      ok: !!item.value,
    }));
    const missingApiMethods = requiredApiMethods.filter((item) => !item.ok).map((item) => item.key);
    const missingWindowExports = requiredWindowExports.filter((item) => !item.ok).map((item) => item.key);
    const missingDomTargets = domTargets.filter((item) => !item.ok).map((item) => item.selector);
    const missingConfirmTexts = confirmTexts.filter((item) => !item.ok).map((item) => item.key);
    const ok = contract.status === "contract-frozen-v190" && missingApiMethods.length === 0 && missingWindowExports.length === 0 && missingDomTargets.length === 0 && missingConfirmTexts.length === 0;
    return {
      ok,
      contract,
      status: contract.status,
      currentFile: contract.currentFile,
      nextFile: contract.nextFile,
      requiredApiMethods,
      requiredWindowExports,
      domTargets,
      dynamicDomTargets: contract.dynamicDomTargets.slice(),
      confirmTexts,
      delegatedActions: contract.delegatedActions.slice(),
      splitBoundary: contract.splitBoundary.slice(),
      missingApiMethods,
      missingWindowExports,
      missingDomTargets,
      missingConfirmTexts,
      apiMethodCount: requiredApiMethods.length,
      windowExportCount: requiredWindowExports.length,
      domTargetCount: domTargets.length,
      dynamicDomTargetCount: contract.dynamicDomTargets.length,
      confirmTextCount: confirmTexts.length,
      delegatedActionCount: contract.delegatedActions.length,
    };
  }

  function renderAdminEditDraftSplitContractReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminEditDraftSplitContractReadiness();
    const apiHtml = readiness.requiredApiMethods.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${item.ok ? "ok" : "missing"}</span>`).join(" ");
    const confirmHtml = readiness.confirmTexts.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${escapeHtml(item.value)}</span>`).join(" ");
    const boundaryHtml = readiness.splitBoundary.map((item) => `<span class="pill warn">${escapeHtml(item)}</span>`).join(" ");
    const exportRows = readiness.requiredWindowExports.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const domRows = readiness.domTargets.map((item) => `<tr><td><code>${escapeHtml(item.selector)}</code></td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const dynamicHtml = readiness.dynamicDomTargets.map((selector) => `<span class="pill warn">${escapeHtml(selector)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "edit draft 분리 계약 고정 완료" : "edit draft 분리 계약 확인 필요",
          subtitle: `${readiness.currentFile} → ${readiness.nextFile} 이동 전, 편집 초안/관계 선택/영향 안내 계약을 먼저 고정했습니다.`,
          metrics: [
            { label: "API 함수", value: readiness.apiMethodCount, tone: readiness.missingApiMethods.length ? "blocked" : "good" },
            { label: "window export", value: readiness.windowExportCount, tone: readiness.missingWindowExports.length ? "blocked" : "good" },
            { label: "DOM target", value: readiness.domTargetCount, tone: readiness.missingDomTargets.length ? "blocked" : "good" },
            { label: "확인 문구", value: readiness.confirmTextCount, tone: readiness.missingConfirmTexts.length ? "blocked" : "good" },
            { label: "delegated action", value: readiness.delegatedActionCount, tone: "warn" },
          ],
        })}
        <div class="draft-preview-summary">${apiHtml}</div>
        <div class="draft-preview-summary">${confirmHtml}</div>
        <div class="draft-preview-summary">${boundaryHtml}</div>
        <div class="filter-help">동적 DOM은 상세 row를 열었을 때 생성됩니다. 계약 고정 단계에서는 아래 selector 이름만 고정하고, 실제 분리는 v191에서 진행하는 방향이 안전합니다.</div>
        <div class="draft-preview-summary">${dynamicHtml}</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>window export</th><th>상태</th></tr></thead><tbody>${exportRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>DOM target</th><th>상태</th></tr></thead><tbody>${domRows}</tbody></table></div>
        </div>
      </div>
    `;
  }

  function renderAdminJsSplitReadiness() {
    const target = $("[data-admin-js-split-readiness]");
    if (!target) return null;
    const readiness = getAdminJsSplitReadiness();
    const globalsHtml = readiness.requiredGlobals.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${item.ok ? "ok" : "missing"}</span>`).join(" ");
    const rows = readiness.phases.map((phase, index) => {
      const tone = phase.status === "already-external" || phase.status === "extracted-v185" || phase.status === "extracted-v187" || phase.status === "contract-frozen-v186" || phase.status === "contract-frozen-v188" || phase.status === "contract-frozen-v190" ? "good" : (phase.status === "later" || phase.status === "keep-last" ? "warn" : "good");
      return `<tr><td>${escapeHtml(String(index + 1))}</td><td><strong>${escapeHtml(phase.label)}</strong><br><span class="muted">${escapeHtml(phase.key)}</span></td><td>${escapeHtml(phase.currentFile)}</td><td>${escapeHtml(phase.nextFile)}</td><td><span class="pill ${tone}">${escapeHtml(phase.status)}</span></td><td>${escapeHtml(phase.note)}</td></tr>`;
    }).join("");
    const changeLogContract = getAdminChangeLogSplitContractReadiness();
    const createLifecycleContract = getAdminCreateLifecycleSplitContractReadiness();
    const editDraftContract = getAdminEditDraftSplitContractReadiness();
    target.innerHTML = `
      ${renderAdminOperationResultBanner({
        tone: readiness.ok ? "good" : "warn",
        title: readiness.ok ? "관리자 JS 분리 상태 양호" : "관리자 JS 분리 확인 필요",
        subtitle: "layout shell, change logs, create lifecycle, edit draft를 외부 JS 파일로 분리했습니다.",
        metrics: [
          { label: "script 순서", value: readiness.scriptOrderReady, tone: readiness.scriptOrderReady ? "good" : "blocked" },
          { label: "layout shell 파일", value: readiness.layoutShellExternalReady, tone: readiness.layoutShellExternalReady ? "good" : "blocked" },
          { label: "필수 global 누락", value: readiness.missingGlobals.length, tone: readiness.missingGlobals.length ? "blocked" : "good" },
          { label: "admin export", value: readiness.exportCount, tone: readiness.exportCount ? "good" : "blocked" },
          { label: "분리 후보", value: readiness.candidateCount, tone: "warn" },
        ],
      })}
      <div class="draft-preview-summary">${globalsHtml}</div>
      <div class="filter-help">다음 안전 단계: ${escapeHtml(readiness.nextSafeStep)}. layout shell, change logs, create lifecycle, edit draft는 분리 완료 상태입니다.</div>
      <div class="table-wrap relation-table-wrap"><table><thead><tr><th>#</th><th>묶음</th><th>현재 파일</th><th>분리 후보 파일</th><th>상태</th><th>메모</th></tr></thead><tbody>${rows}</tbody></table></div>
      ${renderAdminChangeLogSplitContractReadiness(changeLogContract)}
      ${renderAdminCreateLifecycleSplitContractReadiness(createLifecycleContract)}
      ${renderAdminEditDraftSplitContractReadiness(editDraftContract)}
    `;
    return readiness;
  }

  function renderAdminCreateBlueprint(blueprintPayload) {
    return getAdminCreateLifecycleApi().renderAdminCreateBlueprint(blueprintPayload);
  }

  async function refreshAdminCreateBlueprint(options) {
    return getAdminCreateLifecycleApi().refreshAdminCreateBlueprint(options);
  }

  function readAdminCreateDraftValues() {
    return getAdminCreateLifecycleApi().readAdminCreateDraftValues();
  }

  function resetAdminCreateDraft() {
    return getAdminCreateLifecycleApi().resetAdminCreateDraft();
  }

  function renderAdminCreatePreviewResult(preview) {
    return getAdminCreateLifecycleApi().renderAdminCreatePreviewResult(preview);
  }

  async function previewAdminCreateDraft(options) {
    return getAdminCreateLifecycleApi().previewAdminCreateDraft(options);
  }

  async function applyAdminCreateDraft(options) {
    return getAdminCreateLifecycleApi().applyAdminCreateDraft(options);
  }

  function getAdminCreateBlueprintReadiness() {
    return getAdminCreateLifecycleApi().getAdminCreateBlueprintReadiness();
  }

  function getAdminEditDraftApi() {
    if (!window.RpgAdminEditDraft) throw new Error("RpgAdminEditDraft is not loaded");
    return window.RpgAdminEditDraft;
  }

  function configureAdminEditDraft() {
    return getAdminEditDraftApi().configure({
      querySelector: $,
      escapeHtml,
      formatValue,
      formatValueWithFieldHint,
      renderFieldHelpBadge,
      renderFieldHelpInline,
      renderFieldValueHintInline,
      ensureApi,
      setStatus,
      hasAdminWriteDevKey,
      requireAdminWriteDevKeyForUi,
      runPostWriteMasterApiVerification,
      refreshAdminChangeLogs,
      readChangeLogFiltersFromDom,
      getCurrentMasterDetailPayload: () => currentMasterDetailPayload,
      DEFAULT_MASTER_DOMAIN,
      DEFAULT_TIMEOUT_MS,
      ADMIN_EDIT_APPLY_TIMEOUT_MS,
      ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT,
      ADMIN_EDIT_ALLOWED_FIELDS,
      ADMIN_DRAFT_BOOLEAN_FIELDS,
      ADMIN_DRAFT_NUMBER_FIELDS,
      ADMIN_DRAFT_TEXTAREA_FIELDS,
      ADMIN_EQUIP_SLOT_PRESET_LABELS,
      ADMIN_DRAFT_SELECT_FIELD_OPTIONS,
      ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT,
    });
  }

  function getAdminEditDraftExternalReadiness() {
    return getAdminEditDraftApi().getReadiness();
  }

  function getAdminRelationEditOptionDefinitions(...args) {
    return getAdminEditDraftApi().getAdminRelationEditOptionDefinitions(...args);
  }

  function getAdminRelationEditOptionDefinition(...args) {
    return getAdminEditDraftApi().getAdminRelationEditOptionDefinition(...args);
  }

  function isAdminRelationEditField(...args) {
    return getAdminEditDraftApi().isAdminRelationEditField(...args);
  }

  function fieldKeyLooksReadOnly(...args) {
    return getAdminEditDraftApi().fieldKeyLooksReadOnly(...args);
  }

  function isAdminEditApplyAllowedField(...args) {
    return getAdminEditDraftApi().isAdminEditApplyAllowedField(...args);
  }

  function getAdminEditAllowedFields(...args) {
    return getAdminEditDraftApi().getAdminEditAllowedFields(...args);
  }

  function normalizeAdminDraftFieldKey(...args) {
    return getAdminEditDraftApi().normalizeAdminDraftFieldKey(...args);
  }

  function getAdminEquipSlotDisplayName(...args) {
    return getAdminEditDraftApi().getAdminEquipSlotDisplayName(...args);
  }

  function getAdminDraftRelationOptionGroupKey(...args) {
    return getAdminEditDraftApi().getAdminDraftRelationOptionGroupKey(...args);
  }

  function getAdminDraftRelationOptionsForValues(...args) {
    return getAdminEditDraftApi().getAdminDraftRelationOptionsForValues(...args);
  }

  function getAdminDraftRelationOptions(...args) {
    return getAdminEditDraftApi().getAdminDraftRelationOptions(...args);
  }

  function getAdminDraftSelectOptions(...args) {
    return getAdminEditDraftApi().getAdminDraftSelectOptions(...args);
  }

  function normalizeAdminRelationSearchText(...args) {
    return getAdminEditDraftApi().normalizeAdminRelationSearchText(...args);
  }

  function getAdminRelationOptionText(...args) {
    return getAdminEditDraftApi().getAdminRelationOptionText(...args);
  }

  function filterAdminDraftSelectOptions(...args) {
    return getAdminEditDraftApi().filterAdminDraftSelectOptions(...args);
  }

  function renderAdminDraftSelectOptionsHtml(...args) {
    return getAdminEditDraftApi().renderAdminDraftSelectOptionsHtml(...args);
  }

  function getAdminRelationSelectMetaText(...args) {
    return getAdminEditDraftApi().getAdminRelationSelectMetaText(...args);
  }

  function updateAdminRelationOptionMeta(...args) {
    return getAdminEditDraftApi().updateAdminRelationOptionMeta(...args);
  }

  function applyAdminRelationOptionFilter(...args) {
    return getAdminEditDraftApi().applyAdminRelationOptionFilter(...args);
  }

  function clearAdminRelationOptionFilter(...args) {
    return getAdminEditDraftApi().clearAdminRelationOptionFilter(...args);
  }

  function refreshDependentAdminRelationSelects(...args) {
    return getAdminEditDraftApi().refreshDependentAdminRelationSelects(...args);
  }

  function getAdminDraftFieldInputKind(...args) {
    return getAdminEditDraftApi().getAdminDraftFieldInputKind(...args);
  }

  function getAdminDraftFieldTypeLabel(...args) {
    return getAdminEditDraftApi().getAdminDraftFieldTypeLabel(...args);
  }

  function getAdminDraftLockedReason(...args) {
    return getAdminEditDraftApi().getAdminDraftLockedReason(...args);
  }

  function renderAdminDraftTypeBadge(...args) {
    return getAdminEditDraftApi().renderAdminDraftTypeBadge(...args);
  }

  function getAdminDraftFieldRisk(...args) {
    return getAdminEditDraftApi().getAdminDraftFieldRisk(...args);
  }

  function renderAdminDraftRiskBadge(...args) {
    return getAdminEditDraftApi().renderAdminDraftRiskBadge(...args);
  }

  function renderAdminDraftLockedFields(...args) {
    return getAdminEditDraftApi().renderAdminDraftLockedFields(...args);
  }

  function makeDraftOriginalValue(...args) {
    return getAdminEditDraftApi().makeDraftOriginalValue(...args);
  }

  function parseDraftOriginalValue(...args) {
    return getAdminEditDraftApi().parseDraftOriginalValue(...args);
  }

  function renderAdminDraftControl(...args) {
    return getAdminEditDraftApi().renderAdminDraftControl(...args);
  }

  function getAdminRelationComboGuardLabels(...args) {
    return getAdminEditDraftApi().getAdminRelationComboGuardLabels(...args);
  }

  function renderAdminRelationEditOptionsNote(...args) {
    return getAdminEditDraftApi().renderAdminRelationEditOptionsNote(...args);
  }

  function renderMasterEditDraft(...args) {
    return getAdminEditDraftApi().renderMasterEditDraft(...args);
  }

  function readAdminEditDraftValues(...args) {
    return getAdminEditDraftApi().readAdminEditDraftValues(...args);
  }

  function resetAdminEditDraft(...args) {
    return getAdminEditDraftApi().resetAdminEditDraft(...args);
  }

  function valuesEqualForImpact(...args) {
    return getAdminEditDraftApi().valuesEqualForImpact(...args);
  }

  function collectLocalDraftChangesForImpact(...args) {
    return getAdminEditDraftApi().collectLocalDraftChangesForImpact(...args);
  }

  function getAdminRiskSortWeight(...args) {
    return getAdminEditDraftApi().getAdminRiskSortWeight(...args);
  }

  function sortAdminChangesByRisk(...args) {
    return getAdminEditDraftApi().sortAdminChangesByRisk(...args);
  }

  function getAdminRelationOptionDisplayText(...args) {
    return getAdminEditDraftApi().getAdminRelationOptionDisplayText(...args);
  }

  function getAdminRelationValueDisplay(...args) {
    return getAdminEditDraftApi().getAdminRelationValueDisplay(...args);
  }

  function getAdminRelationOpenTarget(...args) {
    return getAdminEditDraftApi().getAdminRelationOpenTarget(...args);
  }

  function renderAdminRelationOpenButton(...args) {
    return getAdminEditDraftApi().renderAdminRelationOpenButton(...args);
  }

  function getAdminChangeRelationInfo(...args) {
    return getAdminEditDraftApi().getAdminChangeRelationInfo(...args);
  }

  function formatAdminRelationInfoText(...args) {
    return getAdminEditDraftApi().formatAdminRelationInfoText(...args);
  }

  function getAdminRelationOpenTargetFromChange(...args) {
    return getAdminEditDraftApi().getAdminRelationOpenTargetFromChange(...args);
  }

  function renderAdminRelationOpenTargetButton(...args) {
    return getAdminEditDraftApi().renderAdminRelationOpenTargetButton(...args);
  }

  function formatAdminChangeValueText(...args) {
    return getAdminEditDraftApi().formatAdminChangeValueText(...args);
  }

  function renderAdminChangeValueCell(...args) {
    return getAdminEditDraftApi().renderAdminChangeValueCell(...args);
  }

  function renderAdminRollbackMismatchValueCell(...args) {
    return getAdminEditDraftApi().renderAdminRollbackMismatchValueCell(...args);
  }

  function formatAdminChangeAfterValue(...args) {
    return getAdminEditDraftApi().formatAdminChangeAfterValue(...args);
  }

  function buildAdminEditDraftReview(...args) {
    return getAdminEditDraftApi().buildAdminEditDraftReview(...args);
  }

  function renderAdminEditDraftReview(...args) {
    return getAdminEditDraftApi().renderAdminEditDraftReview(...args);
  }

  function refreshAdminEditReviewAndImpact(...args) {
    return getAdminEditDraftApi().refreshAdminEditReviewAndImpact(...args);
  }

  function normalizeImpactKey(...args) {
    return getAdminEditDraftApi().normalizeImpactKey(...args);
  }

  function getAdminEditImpactHint(...args) {
    return getAdminEditDraftApi().getAdminEditImpactHint(...args);
  }

  function buildAdminEditImpactGuide(...args) {
    return getAdminEditDraftApi().buildAdminEditImpactGuide(...args);
  }

  function renderAdminEditImpactGuide(...args) {
    return getAdminEditDraftApi().renderAdminEditImpactGuide(...args);
  }

  function refreshAdminEditImpactGuide(...args) {
    return getAdminEditDraftApi().refreshAdminEditImpactGuide(...args);
  }

  function renderAdminEditPreviewResult(...args) {
    return getAdminEditDraftApi().renderAdminEditPreviewResult(...args);
  }

  function readAdminEditApplyControls(...args) {
    return getAdminEditDraftApi().readAdminEditApplyControls(...args);
  }

  async function previewAdminEditDraft(...args) {
    return await getAdminEditDraftApi().previewAdminEditDraft(...args);
  }

  async function applyAdminEditDraft(...args) {
    return await getAdminEditDraftApi().applyAdminEditDraft(...args);
  }

  function getAdminEditDraftReadiness(...args) {
    return getAdminEditDraftApi().getAdminEditDraftReadiness(...args);
  }
  function makeAdminDetailFieldMap(detailPayload) {
    const fields = Array.isArray(detailPayload && detailPayload.fields) ? detailPayload.fields : [];
    const map = {};
    fields.forEach((field) => {
      if (!field || !field.key) return;
      map[field.key] = field.value;
    });
    return map;
  }

  function valuesEqualForApiVerify(expected, actual) {
    if (expected === actual) return true;
    if ((expected === null || expected === undefined || expected === "") && (actual === null || actual === undefined || actual === "")) return true;
    if (typeof expected === "boolean" || typeof actual === "boolean") {
      return (expected === true || String(expected).toLowerCase() === "true") === (actual === true || String(actual).toLowerCase() === "true");
    }
    const expectedNumber = Number(expected);
    const actualNumber = Number(actual);
    if (expected !== "" && actual !== "" && Number.isFinite(expectedNumber) && Number.isFinite(actualNumber)) {
      return expectedNumber === actualNumber;
    }
    return String(expected) === String(actual);
  }

  function findMasterApiRow(domain, detailPayload, masterPayload) {
    const rows = Array.isArray(masterPayload && masterPayload[domain]) ? masterPayload[domain] : [];
    const fields = makeAdminDetailFieldMap(detailPayload);
    if (!rows.length) return null;

    if (fields.id !== undefined) {
      const byId = rows.find((row) => valuesEqualForApiVerify(fields.id, row && row.id));
      if (byId) return byId;
    }
    if (fields.code !== undefined) {
      const byCode = rows.find((row) => valuesEqualForApiVerify(fields.code, row && row.code));
      if (byCode) return byCode;
    }

    if (domain === "skillLevels") {
      return rows.find((row) => valuesEqualForApiVerify(fields.skill_code, row && row.skillCode) && valuesEqualForApiVerify(fields.level, row && row.level)) || null;
    }
    if (domain === "dropTableItems") {
      return rows.find((row) => valuesEqualForApiVerify(fields.id, row && row.id) || (
        valuesEqualForApiVerify(fields.drop_table_code, row && row.dropTableCode) &&
        valuesEqualForApiVerify(fields.item_template_code, row && row.itemTemplateCode)
      )) || null;
    }
    if (domain === "enhancementLevels") {
      return rows.find((row) =>
        valuesEqualForApiVerify(fields.group_code, row && row.groupCode) &&
        valuesEqualForApiVerify(fields.from_level, row && row.fromLevel) &&
        valuesEqualForApiVerify(fields.to_level, row && row.toLevel)
      ) || null;
    }
    if (domain === "characterSkills") {
      return rows.find((row) =>
        valuesEqualForApiVerify(fields.character_code, row && row.characterCode) &&
        valuesEqualForApiVerify(fields.skill_code, row && row.skillCode)
      ) || null;
    }
    return null;
  }

  function buildMasterApiVerifyComparisons(domain, detailPayload, apiRow) {
    const fieldMap = ADMIN_TO_MASTER_API_FIELD_MAP[domain] || {};
    const detailFields = makeAdminDetailFieldMap(detailPayload);
    return Object.entries(fieldMap)
      .filter(([adminKey, apiKey]) => detailFields[adminKey] !== undefined && apiRow && Object.prototype.hasOwnProperty.call(apiRow, apiKey))
      .map(([adminKey, apiKey]) => {
        const expected = detailFields[adminKey];
        const actual = apiRow ? apiRow[apiKey] : undefined;
        return {
          adminKey,
          apiKey,
          expected,
          actual,
          same: valuesEqualForApiVerify(expected, actual),
        };
      });
  }

  function renderMasterApiVerifyResult(result) {
    const target = $(`[data-admin-master-api-verify-result]`);
    if (!target) return;
    const info = result || {};
    if (!info.checked) {
      target.innerHTML = `<div class="empty">버튼을 누르면 현재 선택한 상세 항목이 <strong>/game/master-data</strong> 응답에도 같은 값으로 보이는지 확인합니다.</div>`;
      return;
    }
    if (!info.found) {
      target.innerHTML = `
        <div class="error">master-data API에서 선택한 항목을 찾지 못했습니다.</div>
        <div class="filter-help">domain=${escapeHtml(formatValue(info.domain))} · id=${escapeHtml(formatValue(info.id))} · rows=${escapeHtml(formatValue(info.rowCount))}</div>
      `;
      return;
    }
    const rows = (info.comparisons || []).map((row) => `
      <tr>
        <td>${escapeHtml(row.adminKey)}</td>
        <td>${escapeHtml(row.apiKey)}</td>
        <td>${escapeHtml(formatValue(row.expected))}</td>
        <td>${escapeHtml(formatValue(row.actual))}</td>
        <td><span class="pill ${row.same ? "good" : "blocked"}">${row.same ? "same" : "diff"}</span></td>
      </tr>
    `).join("") || `<tr><td colspan="5">비교 가능한 스칼라 필드가 없습니다.</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${info.ok ? "good" : "blocked"}">API 반영 ${info.ok ? "정상" : "차이 있음"}</span>
        <span class="pill">domain ${escapeHtml(formatValue(info.domain))}</span>
        <span class="pill">비교 ${escapeHtml(formatValue(info.comparisonCount))}</span>
        <span class="pill ${info.diffCount ? "blocked" : "good"}">diff ${escapeHtml(formatValue(info.diffCount))}</span>
        <span class="pill">checked ${escapeHtml(formatClock(info.checkedAt))}</span>
        ${info.contextLabel ? `<span class="pill warn">${escapeHtml(info.contextLabel)}</span>` : ""}
      </div>
      <div class="table-wrap relation-table-wrap"><table><thead><tr><th>관리자 필드</th><th>master-data API 필드</th><th>관리자 상세 값</th><th>API 값</th><th>상태</th></tr></thead><tbody>${rows}</tbody></table></div>
      <div class="filter-help">이 검사는 DB → FastAPI <code>/game/master-data</code> 응답까지 반영됐는지 확인합니다. 이미 열려 있던 게임 화면은 새로고침해야 새 master-data를 다시 읽습니다.</div>
    `;
  }

  async function verifySelectedMasterDataApi(options) {
    ensureApi();
    const detail = currentMasterDetailPayload;
    if (!detail || !detail.id || !detail.domain) {
      const error = new Error("먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-master-api-verify-result]`);
    if (target) target.innerHTML = `<div class="empty">/game/master-data 응답에서 선택 항목을 확인하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchMasterData({ timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    const domain = detail.domain;
    const rows = Array.isArray(payload[domain]) ? payload[domain] : [];
    const apiRow = findMasterApiRow(domain, detail, payload);
    const comparisons = apiRow ? buildMasterApiVerifyComparisons(domain, detail, apiRow) : [];
    const diffCount = comparisons.filter((row) => !row.same).length;
    const result = {
      checked: true,
      ok: !!apiRow && diffCount === 0,
      found: !!apiRow,
      domain,
      id: detail.id,
      title: detail.title,
      rowCount: rows.length,
      comparisonCount: comparisons.length,
      diffCount,
      comparisons,
      apiRowPreview: apiRow || null,
      counts: payload.counts || {},
      contextLabel: options && options.contextLabel ? String(options.contextLabel) : "",
      autoAfterWrite: !!(options && options.autoAfterWrite),
      checkedAt: new Date().toISOString(),
    };
    renderMasterApiVerifyResult(result);
    setStatus(result.ok ? `master-data API 반영 확인 완료: ${formatValue(domain)} #${formatValue(detail.id)}` : `master-data API 확인 필요: diff ${formatValue(diffCount)}`, result.ok ? "ok" : "error");
    return result;
  }

  async function runPostWriteMasterApiVerification(domain, id, options) {
    const opts = options || {};
    const label = opts.label || "DB 적용";
    const result = {
      ok: false,
      status: "not_started",
      domain,
      id,
      label,
      verification: null,
      error: null,
    };
    if (!domain || !id) {
      result.status = "skipped_missing_target";
      setStatus(`${label} 완료 · API 자동 확인은 대상 정보가 없어 건너뜀`, "error");
      return result;
    }
    try {
      setStatus(`${label} 완료 · 상세 다시 불러오기 및 master-data API 자동 확인 중...`, "info");
      await openAdminMasterDataDetail(domain, id, { timeoutMs: DEFAULT_TIMEOUT_MS });
      const verification = await verifySelectedMasterDataApi({
        timeoutMs: DEFAULT_TIMEOUT_MS,
        contextLabel: opts.contextLabel || `${label} 후 자동 확인`,
        autoAfterWrite: true,
      });
      result.verification = verification;
      result.ok = !!(verification && verification.ok);
      result.status = result.ok ? "verified" : "diff_or_missing";
      setStatus(
        result.ok
          ? `${label} 완료 · master-data API 자동 확인 정상 · 게임은 새로고침 후 반영`
          : `${label} 완료 · master-data API 자동 확인 필요: diff ${formatValue(verification && verification.diffCount)}`,
        result.ok ? "ok" : "error"
      );
      return result;
    } catch (error) {
      result.status = "verify_failed";
      result.error = error;
      const target = $(`[data-admin-master-api-verify-result]`);
      if (target) {
        target.innerHTML = `<div class="error">${escapeHtml(label)} 후 master-data API 자동 확인 실패: ${escapeHtml(error && error.message ? error.message : error)}</div>`;
      }
      setStatus(`${label} 완료 · master-data API 자동 확인 실패: ${error && error.message ? error.message : error}`, "error");
      return result;
    }
  }

  function renderMasterDetail(detailPayload) {
    currentMasterDetailPayload = detailPayload && detailPayload.status === "loaded" ? detailPayload : null;
    const target = $("[data-admin-master-detail]");
    const meta = $("[data-admin-master-detail-meta]");
    if (!target) return;
    const detail = detailPayload || {};
    const fields = Array.isArray(detail.fields) ? detail.fields : [];
    const jsonFields = Array.isArray(detail.jsonFields) ? detail.jsonFields : [];
    const assetFields = Array.isArray(detail.assetFields) ? detail.assetFields : [];
    const relationHints = Array.isArray(detail.relationHints) ? detail.relationHints : [];
    if (meta) meta.textContent = detail.status === "loaded" ? `${formatValue(detail.domainLabel || detail.domain)} · #${formatValue(detail.id)} · ${formatValue(detail.title)}` : formatValue(detail.status || "선택 없음");
    if (detail.status && detail.status !== "loaded") {
      target.innerHTML = `<div class="error">상세 정보를 불러오지 못했습니다: ${escapeHtml(detail.status)}</div>`;
      return;
    }
    if (!detail.id) {
      target.innerHTML = `<div class="empty">마스터 데이터 카탈로그에서 행의 <strong>보기</strong> 버튼을 누르면 상세 정보가 여기에 표시됩니다.</div>`;
      return;
    }

    const fieldRows = fields.map((field) => `
      <tr><th>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</th><td>${formatValueWithFieldHint(field.key, field.value)}${renderFieldHelpInline(field.key)}</td></tr>
    `).join("");
    const relationRows = relationHints.length ? relationHints.map((hint) => `
      <span class="pill">${escapeHtml(hint.label)}: ${escapeHtml(formatValue(hint.value))}</span>
    `).join(" ") : `<span class="pill">연결 요약 없음</span>`;
    const assetRows = assetFields.length ? assetFields.map((asset) => `
      <tr><th>${escapeHtml(asset.label || asset.key)}</th><td><span class="pill ${asset.hidden ? "good" : ""}">${asset.hidden ? "hidden" : "empty"}</span> ${escapeHtml(formatValue(asset.kind))} · ${escapeHtml(formatValue(asset.length))} chars</td></tr>
    `).join("") : `<tr><td colspan="2">숨길 이미지/아이콘 필드 없음</td></tr>`;
    const jsonBlocks = jsonFields.length ? jsonFields.map((field) => {
      const previewText = JSON.stringify(field.preview, null, 2);
      const keyText = Array.isArray(field.keys) && field.keys.length ? field.keys.join(", ") : "-";
      return `
        <details class="json-detail" open>
          <summary>${escapeHtml(field.label || field.key)} <span class="pill good">sanitized</span> <span class="pill">keys: ${escapeHtml(keyText)}</span></summary>
          <div class="json-meta">hidden assets ${escapeHtml(formatValue(field.hiddenAssetCount))} · truncated ${escapeHtml(formatValue(field.truncatedCount))} · raw JSON ${field.rawJsonReturned ? "returned" : "hidden"}</div>
          <pre class="json-preview">${escapeHtml(previewText)}</pre>
        </details>
      `;
    }).join("") : `<div class="empty">JSON 필드 없음</div>`;

    target.innerHTML = `
      <div class="detail-grid">
        <div class="detail-card">
          <div class="detail-title">기본 필드</div>
          <table class="detail-table"><tbody>${fieldRows}</tbody></table>
        </div>
        <div class="detail-card">
          <div class="detail-title">연결 요약</div>
          <div class="relation-list">${relationRows}</div>
          <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
            <button class="btn mini" type="button" data-admin-action="open-master-relations" data-admin-relation-domain="${escapeHtml(detail.domain || "")}" data-admin-relation-id="${escapeHtml(detail.id)}">연결 항목 불러오기</button>
            <span class="pill good">read-only</span>
          </div>
          <div class="detail-title" style="margin-top:14px;">에셋 필드</div>
          <table class="detail-table"><tbody>${assetRows}</tbody></table>
        </div>
      </div>
      <div style="margin:0 14px 12px;">${renderMasterEditDraft(detail, fields)}</div>
      <div class="detail-card" style="margin:0 14px 12px;">
        <div class="detail-title">인게임 master-data API 반영 확인 <span class="pill good">diagnostic</span></div>
        <div class="filter-help">관리자 상세 값이 게임이 읽는 <code>/game/master-data</code> 응답에도 같은 값으로 보이는지 확인합니다. DB 적용 직후 게임 새로고침 전 점검용입니다.</div>
        <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn mini primary" type="button" data-admin-action="verify-master-api-target">선택 항목 API 반영 확인</button>
          <span class="pill warn">게임 화면은 새로고침 필요</span>
        </div>
        <div class="edit-draft-result" data-admin-master-api-verify-result><div class="empty">버튼을 누르면 현재 선택한 상세 항목이 <strong>/game/master-data</strong> 응답에도 같은 값으로 보이는지 확인합니다.</div></div>
      </div>
      <div class="detail-card" style="margin:0 14px 12px;">
        <div class="detail-title">실제 연결 항목</div>
        <div class="filter-help">관련 마스터 데이터를 축약된 목록으로 보여줍니다. 행의 보기 버튼을 누르면 해당 항목 상세로 이동합니다.</div>
        <div data-admin-master-relations><div class="empty">연결 항목을 불러오지 않았습니다.</div></div>
      </div>
      <div class="detail-card" style="margin-top:12px;">
        <div class="detail-title">JSON 미리보기</div>
        <div class="filter-help">원본 JSON 통째로가 아니라, data URL 이미지/긴 문자열을 숨긴 안전 미리보기입니다.</div>
        ${jsonBlocks}
      </div>
      <div class="filter-help">readOnly=${escapeHtml(formatValue(detail.readOnly))} · write UI=${escapeHtml(formatValue(detail.safeForAdminWriteUi))} · rawJsonReturned=${escapeHtml(formatValue(detail.rawJsonReturned))} · assetsReturned=${escapeHtml(formatValue(detail.assetsReturned))}</div>
    `;
  }

  function renderMasterRelations(relationsPayload) {
    const target = $("[data-admin-master-relations]");
    if (!target) return;
    const relations = relationsPayload || {};
    const groups = Array.isArray(relations.groups) ? relations.groups : [];
    if (relations.status && relations.status !== "loaded") {
      target.innerHTML = `<div class="error">연결 항목을 불러오지 못했습니다: ${escapeHtml(relations.status)}</div>`;
      return;
    }
    if (!groups.length) {
      target.innerHTML = `<div class="empty">연결된 마스터 데이터가 없습니다.</div>`;
      return;
    }
    target.innerHTML = groups.map((group) => {
      const rows = Array.isArray(group.rows) ? group.rows : [];
      const columns = Array.isArray(group.columns) ? group.columns.slice(0, 6) : [];
      const limited = group.limited ? ` · ${escapeHtml(formatValue(group.count))}개 중 ${escapeHtml(formatValue(group.shown))}개 표시` : ` · ${escapeHtml(formatValue(group.count))}개`;
      return `
        <details class="json-detail" open>
          <summary>${escapeHtml(group.label || group.domainLabel || group.domain)} <span class="pill">${escapeHtml(group.domainLabel || group.domain)}</span><span class="pill good">read-only</span><span class="pill">${limited}</span></summary>
          ${rows.length ? `
            <div class="table-wrap relation-table-wrap">
              <table>
                <thead><tr><th>상세</th><th>ID</th><th>제목</th>${columns.map((column) => `<th title="${escapeHtml((getAdminFieldHelp(column.key) && getAdminFieldHelp(column.key).body) || column.key)}">${escapeHtml(column.label || column.key)}${renderFieldHelpBadge(column.key)}</th>`).join("")}</tr></thead>
                <tbody>
                  ${rows.map((row) => {
                    const cells = row.cells || {};
                    return `
                      <tr>
                        <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || group.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button></td>
                        <td>${escapeHtml(formatValue(row.id))}</td>
                        <td>${escapeHtml(formatValue(row.title))}</td>
                        ${columns.map((column) => `<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>`).join("")}
                      </tr>
                    `;
                  }).join("")}
                </tbody>
              </table>
            </div>
          ` : `<div class="empty">표시할 연결 행이 없습니다.</div>`}
        </details>
      `;
    }).join("");
  }

  async function openAdminMasterDataRelations(domain, id, options) {
    ensureApi();
    const target = $("[data-admin-master-relations]");
    const safeDomain = domain || (readMasterCatalogFiltersFromDom().domain || DEFAULT_MASTER_DOMAIN);
    const safeId = Number(id);
    if (!Number.isFinite(safeId) || safeId <= 0) {
      const error = new Error("연결 항목 조회 ID가 올바르지 않습니다.");
      renderMasterRelations({ status: "invalid_id", id, domain: safeDomain });
      setStatus(error.message, "error");
      throw error;
    }
    if (target) target.innerHTML = `<div class="empty">연결 항목을 불러오는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const limit = options && options.limit !== undefined ? options.limit : 20;
    const response = await window.RpgGameApi.fetchAdminMasterDataRelations({ domain: safeDomain, id: safeId, limit, timeoutMs });
    const relationsPayload = response && response.payload ? response.payload : {};
    renderMasterRelations(relationsPayload);
    setStatus(`연결 항목 로드: ${formatValue(relationsPayload.domainLabel || relationsPayload.domain)} #${formatValue(relationsPayload.id)} · ${formatValue(relationsPayload.totalRelatedRows)}개`, "ok");
    return response;
  }

  async function openAdminMasterDataDetailByCode(domain, code) {
    ensureApi();
    const safeDomain = domain || DEFAULT_MASTER_DOMAIN;
    const safeCode = String(code || "").trim();
    if (!safeCode) throw new Error("열 relation code가 없습니다.");
    setStatus(`관계 대상 찾는 중: ${safeDomain} · ${safeCode}`);
    const response = await window.RpgGameApi.listAdminMasterCatalogRows({ domain: safeDomain, q: safeCode, limit: 20, page: 1, sort: "id_asc" });
    const payload = response && response.payload ? response.payload : {};
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    const row = rows.find((candidate) => {
      const cells = candidate && candidate.cells ? candidate.cells : {};
      return String(cells.code || candidate.code || "") === safeCode;
    }) || rows[0];
    if (!row || !row.id) throw new Error(`관계 대상을 찾지 못했습니다: ${safeDomain} · ${safeCode}`);
    return openAdminMasterDataDetail(safeDomain, row.id);
  }

  async function openAdminMasterDataDetail(domain, id, options) {
    ensureApi();
    const target = $("[data-admin-master-detail]");
    const meta = $("[data-admin-master-detail-meta]");
    const safeDomain = domain || (readMasterCatalogFiltersFromDom().domain || DEFAULT_MASTER_DOMAIN);
    const safeId = Number(id);
    if (!Number.isFinite(safeId) || safeId <= 0) {
      const error = new Error("상세 조회 ID가 올바르지 않습니다.");
      renderMasterDetail({ status: "invalid_id", id, domain: safeDomain });
      setStatus(error.message, "error");
      throw error;
    }
    if (target) target.innerHTML = `<div class="empty">상세 정보를 불러오는 중...</div>`;
    if (meta) meta.textContent = `${safeDomain} · #${safeId}`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchAdminMasterDataDetail({ domain: safeDomain, id: safeId, timeoutMs });
    const detailPayload = response && response.payload ? response.payload : {};
    renderMasterDetail(detailPayload);
    markSelectedMasterCatalogRow(safeDomain, safeId);
    if (!options || options.loadRelations !== false) {
      try {
        await openAdminMasterDataRelations(safeDomain, safeId, { timeoutMs, limit: 20 });
      } catch (error) {
        // 상세 정보는 이미 표시됐으므로, 연결 항목 실패는 상태 메시지만 남깁니다.
        console.warn("[Upgrade RPG] admin relations load failed", error);
      }
    }
    setStatus(`상세 로드: ${formatValue(detailPayload.domainLabel || detailPayload.domain)} #${formatValue(detailPayload.id)} · ${formatValue(detailPayload.title)}`, "ok");
    return response;
  }

  function renderSnapshotTable(snapshotPayload) {
    const target = $("[data-admin-snapshot-table]");
    const meta = $("[data-admin-snapshot-meta]");
    if (!target) return;
    const rows = Array.isArray(snapshotPayload.snapshots) ? snapshotPayload.snapshots : [];
    const filters = snapshotPayload.filters || {};
    const filterNote = filters.hasActiveFilters ? ` · ${describeSnapshotFilters(filters)}` : "";
    const totalAllNote = snapshotPayload.totalAll !== undefined ? ` / 전체 ${formatValue(snapshotPayload.totalAll)}` : "";
    if (meta) meta.textContent = `${formatValue(rows.length)} / ${formatValue(snapshotPayload.total)} shown${totalAllNote}${filterNote}`;
    if (!rows.length) {
      target.innerHTML = `<div class="empty">최근 세이브 스냅샷이 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>유저</th><th>슬롯</th><th>버전</th><th>골드</th><th>레벨</th><th>인벤</th><th>창고</th><th>출처</th><th>원본 JSON</th><th>수정 시각</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const summary = row.summary || {};
            const counts = row.counts || {};
            return `
              <tr title="${escapeHtml(row.note || "")}">
                <td>${escapeHtml(formatValue(row.id))}</td>
                <td>${escapeHtml(formatValue(row.userId))}</td>
                <td>${escapeHtml(formatValue(row.slotKey))} ${row.isDefault ? `<span class="pill good">default</span>` : ""}</td>
                <td>${escapeHtml(formatValue(row.saveVersion))}</td>
                <td>${escapeHtml(formatValue(summary.gold))}</td>
                <td>${escapeHtml(formatValue(summary.level))}</td>
                <td>${escapeHtml(formatValue(counts.inventoryItems))}</td>
                <td>${escapeHtml(formatValue(counts.storageItems))}</td>
                <td>${escapeHtml(formatValue(row.source))}</td>
                <td><span class="pill ${row.rawSnapshotReturned ? "blocked" : "good"}">${row.rawSnapshotReturned ? "returned" : "hidden"}</span></td>
                <td>${escapeHtml(formatClock(row.updatedAt))}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
  }

  async function refreshAdminMasterCatalog(options) {
    const opts = options || {};
    return refreshAdminReadOnlyPage({
      snapshotFilters: readSnapshotFiltersFromDom(),
      masterCatalogFilters: opts.filters || readMasterCatalogFiltersFromDom(),
      changeLogFilters: readChangeLogFiltersFromDom(),
      createBlueprintFilters: readAdminCreateBlueprintFiltersFromDom(),
    });
  }

  function renderReadiness(readiness) {
    const target = $("[data-admin-readiness]");
    if (!target) return;
    const warnings = Array.isArray(readiness.warnings) ? readiness.warnings : [];
    target.innerHTML = `
      <div style="padding:14px; display:grid; gap:10px;">
        <div><span class="pill ${readiness.safeForAdminReadOnlyUi ? "good" : "warn"}">read-only UI: ${escapeHtml(formatValue(readiness.safeForAdminReadOnlyUi))}</span></div>
        <div><span class="pill ${readiness.safeForAdminWriteUi ? "warn" : "blocked"}">general write UI: ${escapeHtml(formatValue(readiness.safeForAdminWriteUi))}</span></div>
        <div><span class="pill ${readiness.guardedMasterEditApplyReady ? "good" : "blocked"}">guarded master edit apply: ${escapeHtml(formatValue(readiness.guardedMasterEditApplyReady))}</span></div>
        <div><span class="pill ${readiness.guardedRollbackReady ? "good" : "blocked"}">guarded rollback: ${escapeHtml(formatValue(readiness.guardedRollbackReady))}</span></div>
        <div><span class="pill ${hasAdminWriteDevKey() ? "good" : "blocked"}">admin write dev key: ${escapeHtml(hasAdminWriteDevKey() ? "set" : "missing")}</span></div>
        <div style="color:#cbd5e1; font-size:13px;">${escapeHtml(readiness.writeUiBlockedReason || "일반 쓰기 기능은 아직 막혀 있습니다.")}</div>
        ${warnings.length ? `<div class="error">경고: ${escapeHtml(warnings.join(", "))}</div>` : `<div style="color:#86efac; font-size:13px;">현재 read-only overview 기준 경고 없음</div>`}
      </div>
    `;
  }

  function renderError(error) {
    const message = error && error.message ? error.message : String(error);
    const cards = $("[data-admin-cards]");
    const master = $("[data-admin-master-table]");
    const snapshots = $("[data-admin-snapshot-table]");
    const catalog = $("[data-admin-master-catalog-table]");
    const detail = $("[data-admin-master-detail]");
    const readiness = $("[data-admin-readiness]");
    if (cards) cards.innerHTML = `<div class="card"><div class="label">오류</div><div class="value small">API 연결 실패</div></div>`;
    if (master) master.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (snapshots) snapshots.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (catalog) catalog.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (detail) detail.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (readiness) readiness.innerHTML = `<div class="error">백엔드가 켜져 있는지, API URL이 맞는지 확인하세요.</div>`;
    setStatus(`불러오기 실패: ${message}`, "error");
  }

  async function refreshAdminReadOnlyPage(options) {
    syncApiInput();
    setStatus("불러오는 중...", "loading");
    try {
      const result = await fetchAdminReadOnlyPageData(options || {});
      const overviewPayload = result.overview && result.overview.payload ? result.overview.payload : {};
      const snapshotPayload = result.snapshots && result.snapshots.payload ? result.snapshots.payload : {};
      const masterDomainsPayload = result.masterDomains && result.masterDomains.payload ? result.masterDomains.payload : {};
      const masterCatalogPayload = result.masterCatalog && result.masterCatalog.payload ? result.masterCatalog.payload : {};
      const changeLogPayload = result.changeLogs && result.changeLogs.payload ? result.changeLogs.payload : {};
      const createBlueprintPayload = result.createBlueprint && result.createBlueprint.payload ? result.createBlueprint.payload : {};
      renderCards(overviewPayload);
      renderMasterTable(overviewPayload.masterData || {});
      syncMasterDomainOptions(masterDomainsPayload);
      renderMasterCatalogTable(masterCatalogPayload);
      renderAdminCreateBlueprint(createBlueprintPayload);
      renderSnapshotTable(snapshotPayload);
      renderAdminChangeLogs(changeLogPayload);
      renderReadiness(overviewPayload.readiness || {});
      renderAdminJsSplitReadiness();
      const filterText = describeSnapshotFilters(result.snapshotFilters || (snapshotPayload && snapshotPayload.filters));
      const masterFilterText = describeMasterCatalogFilters(result.masterCatalogFilters || (masterCatalogPayload && masterCatalogPayload.filters));
      const changeFilterText = describeChangeLogFilters(result.changeLogFilters || (changeLogPayload && changeLogPayload.filters));
      const createFilterText = result.createBlueprintFilters && result.createBlueprintFilters.domain ? ` · 생성설계 domain=${result.createBlueprintFilters.domain}` : "";
      setStatus(`정상 로드 · ${formatClock(new Date().toISOString())} · 세이브 ${filterText} · 마스터 ${masterFilterText} · 이력 ${changeFilterText}${createFilterText} · API ${window.RpgGameApi.getApiBaseUrl()}`, "ok");
      return { ok: true, ...result };
    } catch (error) {
      renderError(error);
      return { ok: false, error };
    }
  }

  function saveApiBaseUrlFromInput() {
    ensureApi();
    const input = getApiInput();
    const value = input ? input.value.trim() : "";
    const next = window.RpgGameApi.setApiBaseUrl(value);
    syncApiInput();
    setStatus(`API URL 저장됨: ${next}`, "ok");
    return next;
  }

  function resetApiBaseUrl() {
    ensureApi();
    const next = window.RpgGameApi.setApiBaseUrl(window.RpgGameApi.DEFAULT_API_BASE_URL);
    syncApiInput();
    setStatus(`API URL 기본값 복구: ${next}`, "ok");
    return next;
  }


  function getAdminLayoutShellApi() {
    if (!window.RpgAdminLayoutShell) throw new Error("RpgAdminLayoutShell is not loaded");
    return window.RpgAdminLayoutShell;
  }

  function initializeAdminLayoutShell() {
    return getAdminLayoutShellApi().initializeAdminLayoutShell();
  }

  function getAdminLayoutShellReadiness() {
    return getAdminLayoutShellApi().getAdminLayoutShellReadiness();
  }

  function setAdminSectionCollapsed(section, collapsed, options) {
    return getAdminLayoutShellApi().setAdminSectionCollapsed(section, collapsed, options);
  }

  function setAdminActiveSidebarLink(hash) {
    return getAdminLayoutShellApi().setAdminActiveSidebarLink(hash);
  }

  function updateAdminStickyLayoutOffsets() {
    return getAdminLayoutShellApi().updateAdminStickyLayoutOffsets();
  }

  function getAdminDefaultCollapsedSectionKeys() {
    return getAdminLayoutShellApi().getAdminDefaultCollapsedSectionKeys();
  }

  function bindEvents() {
    document.addEventListener("input", (event) => {
      if (event.target && event.target.matches && event.target.matches("[data-admin-create-relation-option-filter]")) {
        applyAdminCreateRelationOptionFilter(event.target);
        return;
      }
      if (event.target && event.target.matches && event.target.matches("[data-admin-relation-option-filter]")) {
        applyAdminRelationOptionFilter(event.target);
        return;
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-edit-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-edit-draft-field")) {
        refreshAdminEditImpactGuide();
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-create-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-create-draft-field")) {
        const result = $(`[data-admin-create-draft-result]`);
        if (result) result.innerHTML = `<div class="empty">초안 값이 바뀌었습니다. 다시 생성 초안 검증을 누르세요.</div>`;
      }
      if (event.target && event.target.matches && event.target.matches("[data-admin-master-query]")) {
        syncMasterCatalogPageInput(1);
      }
    });
    document.addEventListener("keydown", async (event) => {
      if (event.key !== "Enter" || !(event.target && event.target.matches)) return;
      if (event.target.matches("[data-admin-master-query], [data-admin-master-page]")) {
        event.preventDefault();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
    });
    document.addEventListener("change", (event) => {
      if (event.target && event.target.matches && event.target.matches("[data-admin-master-domain], [data-admin-master-limit], [data-admin-master-enabled], [data-admin-master-sort]")) {
        syncMasterCatalogPageInput(1);
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-edit-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-edit-draft-field")) {
        const changedKey = event.target.getAttribute("data-admin-edit-draft-field");
        if (changedKey) refreshDependentAdminRelationSelects(changedKey);
        refreshAdminEditImpactGuide();
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-create-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-create-draft-field")) {
        const changedKey = event.target.getAttribute("data-admin-create-draft-field");
        if (changedKey) refreshDependentAdminCreateRelationSelects(changedKey);
      }
    });
    document.addEventListener("click", async (event) => {
      const button = event.target && event.target.closest ? event.target.closest("[data-admin-action]") : null;
      if (!button) return;
      const action = button.getAttribute("data-admin-action");
      if (action === "refresh") await refreshAdminReadOnlyPage();
      if (action === "apply-snapshot-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      if (action === "apply-master-catalog-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom(), createBlueprintFilters: readAdminCreateBlueprintFiltersFromDom() });
      if (action === "load-create-blueprint") {
        try {
          await refreshAdminCreateBlueprint(readAdminCreateBlueprintFiltersFromDom());
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "sync-create-domain-from-catalog") {
        try {
          const filters = syncAdminCreateDomainFromCatalog();
          await refreshAdminCreateBlueprint(filters);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-create-draft") {
        try {
          await previewAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-admin-create-draft") {
        resetAdminCreateDraft();
      }
      if (action === "apply-admin-create-draft") {
        try {
          await applyAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "run-create-lifecycle-batch-check") {
        try {
          await runAdminCreateLifecycleBatchCheck();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "master-catalog-first-page") await refreshMasterCatalogWithPage(1);
      if (action === "master-catalog-prev-page") {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(Math.max(1, current - 1));
      }
      if (action === "master-catalog-next-page") {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(current + 1);
      }
      if (action === "master-catalog-last-page") {
        const totalPages = Number(button.getAttribute("data-admin-master-total-pages")) || 1;
        await refreshMasterCatalogWithPage(totalPages);
      }
      if (action === "apply-change-log-filters") await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      if (action === "set-change-log-action-filter") {
        try {
          await applyAdminChangeLogActionShortcut(button.getAttribute("data-admin-change-log-action-shortcut"));
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-master-detail") {
        const domain = button.getAttribute("data-admin-detail-domain");
        const id = button.getAttribute("data-admin-detail-id");
        try {
          await openAdminMasterDataDetail(domain, id);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-master-detail-by-code") {
        const domain = button.getAttribute("data-admin-detail-domain");
        const code = button.getAttribute("data-admin-detail-code");
        try {
          await openAdminMasterDataDetailByCode(domain, code);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-master-relations") {
        const domain = button.getAttribute("data-admin-relation-domain");
        const id = button.getAttribute("data-admin-relation-id");
        try {
          await openAdminMasterDataRelations(domain, id);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-edit-draft") {
        try {
          await previewAdminEditDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-edit-draft") {
        try {
          await applyAdminEditDraft();
        } catch (error) {
          // applyAdminEditDraft already renders user-facing validation errors.
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "refresh-admin-change-logs") {
        try {
          await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-admin-change-log-detail") {
        try {
          await openAdminChangeLogDetail(button.getAttribute("data-admin-change-log-id"));
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-change-log-rollback") {
        try {
          await previewAdminChangeLogRollback();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-change-log-rollback") {
        try {
          await applyAdminChangeLogRollback();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "preview-admin-create-delete") {
        try {
          await previewAdminCreateDeleteRollback();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-create-delete") {
        try {
          await applyAdminCreateDeleteRollback();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "preview-admin-create-delete-restore") {
        try {
          await previewAdminCreateDeleteRestore();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-create-delete-restore") {
        try {
          await applyAdminCreateDeleteRestore();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "verify-master-api-target") {
        try {
          await verifySelectedMasterDataApi();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-admin-edit-draft") {
        resetAdminEditDraft();
      }
      if (action === "reset-master-catalog-filters") {
        resetMasterCatalogFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
      if (action === "reset-snapshot-filters") {
        resetSnapshotFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
      if (action === "reset-change-log-filters") {
        resetChangeLogFilters();
        await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      }
      if (action === "save-admin-write-dev-key") {
        try {
          saveAdminWriteDevKeyFromInput();
        } catch (error) {
          renderAdminWriteKeyStatus();
        }
      }
      if (action === "clear-admin-write-dev-key") {
        clearAdminWriteDevKey();
      }
      if (action === "save-api-base-url") {
        try {
          saveApiBaseUrlFromInput();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-api-base-url") {
        try {
          resetApiBaseUrl();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "copy-admin-url") {
        await copyCurrentAdminPageUrl();
      }
    });
  }

  function bootAdminReadOnlyPage() {
    bindEvents();
    initializeAdminLayoutShell();
    syncLocationHints();
    syncApiInput();
    syncAdminWriteDevKeyInput();
    resetSnapshotFilters({ silent: true });
    resetMasterCatalogFilters({ silent: true });
    resetChangeLogFilters({ silent: true });
    renderMasterDetail({});
    renderAdminCreateBlueprint({});
    renderAdminJsSplitReadiness();
    refreshAdminReadOnlyPage();
  }

  function checkAdminReadOnlyPageReady(options) {
    const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function" && typeof window.RpgGameApi.listAdminMasterCatalogRows === "function" && typeof window.RpgGameApi.fetchAdminMasterCreateBlueprint === "function" && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function" && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function" && typeof window.RpgGameApi.fetchAdminMasterDataDetail === "function" && typeof window.RpgGameApi.fetchAdminMasterDataRelations === "function" && typeof window.RpgGameApi.previewAdminMasterDataEdit === "function" && typeof window.RpgGameApi.applyAdminMasterDataEdit === "function" && typeof window.RpgGameApi.listAdminChangeLogs === "function" && typeof window.RpgGameApi.fetchAdminChangeLogDetail === "function" && typeof window.RpgGameApi.previewAdminChangeLogRollback === "function" && typeof window.RpgGameApi.applyAdminChangeLogRollback === "function" && typeof window.RpgGameApi.previewAdminCreateDeleteRollback === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRollback === "function" && typeof window.RpgGameApi.previewAdminCreateDeleteRestore === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRestore === "function" && typeof window.RpgGameApi.setAdminWriteDevKey === "function" && typeof window.RpgGameApi.hasAdminWriteDevKey === "function");
    const domReady = !!document.querySelector("[data-admin-cards]");
    const locationHintReady = !!document.querySelector("[data-admin-current-url]");
    const snapshotFilterReady = !!document.querySelector("[data-admin-filter-slot-key]");
    const masterCatalogReady = !!document.querySelector("[data-admin-master-domain]");
    const createBlueprintReady = !!document.querySelector("[data-admin-create-blueprint]") && typeof renderAdminCreateBlueprint === "function" && typeof getAdminCreateBlueprintReadiness === "function";
    const createLifecycleGuideReady = !!document.querySelector("[data-admin-create-lifecycle-guide]") && typeof renderAdminCreateLifecycleGuide === "function" && typeof getAdminCreateLifecycleGuideReadiness === "function";
    const createLifecycleDependencyGuideReady = typeof renderAdminCreateLifecycleDependencyGuards === "function" && typeof applyAdminChangeLogActionShortcut === "function";
    const createLifecycleResultSummaryReady = typeof renderAdminOperationResultBanner === "function" && typeof renderAdminCreateDeleteBlockerSummary === "function";
    const createLifecycleBatchCheckReady = typeof runAdminCreateLifecycleBatchCheck === "function" && typeof renderAdminCreateLifecycleBatchResult === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRollback === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRestore === "function");
    const adminJsSplitReadiness = typeof getAdminJsSplitReadiness === "function" ? getAdminJsSplitReadiness() : { ok: false };
    const adminJsSplitReadinessReady = !!(adminJsSplitReadiness && adminJsSplitReadiness.ok && typeof renderAdminJsSplitReadiness === "function");
    const changeLogSplitContract = typeof getAdminChangeLogSplitContractReadiness === "function" ? getAdminChangeLogSplitContractReadiness() : { ok: false };
    const changeLogSplitContractReady = !!(changeLogSplitContract && changeLogSplitContract.ok && typeof renderAdminChangeLogSplitContractReadiness === "function");
    const createLifecycleSplitContract = typeof getAdminCreateLifecycleSplitContractReadiness === "function" ? getAdminCreateLifecycleSplitContractReadiness() : { ok: false };
    const createLifecycleSplitContractReady = !!(createLifecycleSplitContract && createLifecycleSplitContract.ok && typeof renderAdminCreateLifecycleSplitContractReadiness === "function");
    const editDraftSplitContract = typeof getAdminEditDraftSplitContractReadiness === "function" ? getAdminEditDraftSplitContractReadiness() : { ok: false };
    const editDraftSplitContractReady = !!(editDraftSplitContract && editDraftSplitContract.ok && typeof renderAdminEditDraftSplitContractReadiness === "function");
    const editDraftExternal = typeof getAdminEditDraftExternalReadiness === "function" ? getAdminEditDraftExternalReadiness() : { ok: false };
    const editDraftExternalReady = !!(editDraftExternal && editDraftExternal.ok && editDraftExternal.version === "v191.admin-edit-draft-split");
    const changeLogs = typeof getAdminChangeLogsReadiness === "function" ? getAdminChangeLogsReadiness() : { ok: false };
    const changeLogsExternalReady = !!(changeLogs && changeLogs.ok && changeLogs.version === "v187.admin-change-logs-split");
    const createLifecycle = typeof getAdminCreateLifecycleReadiness === "function" ? getAdminCreateLifecycleReadiness() : { ok: false };
    const createLifecycleExternalReady = !!(createLifecycle && createLifecycle.ok && createLifecycle.version === "v189.1.admin-create-lifecycle-split-hotfix");
    const createDraftPreviewReady = typeof previewAdminCreateDraft === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function");
    const createApplyReady = typeof applyAdminCreateDraft === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function");
    const masterDetailReady = !!document.querySelector("[data-admin-master-detail]");
    const masterRelationsReady = true;
    const editDraftReady = !!document.querySelector("[data-admin-edit-draft]");
    const fieldHelpReady = !!document.querySelector("[data-admin-field-help]");
    const adminChangeLogReady = !!document.querySelector("[data-admin-change-log-table]");
    const adminChangeLogDetailReady = !!document.querySelector("[data-admin-change-log-detail]");
    const adminChangeLogFilterReady = !!document.querySelector("[data-admin-change-log-filter-changed-key]");
    const masterApiVerifyReady = typeof verifySelectedMasterDataApi === "function";
    const postWriteApiVerifyReady = typeof runPostWriteMasterApiVerification === "function";
    const adminWriteGuardReady = !!document.querySelector("[data-admin-write-dev-key]") && !!document.querySelector("[data-admin-write-key-status]");
    const relationSearchReady = typeof applyAdminRelationOptionFilter === "function" && typeof filterAdminDraftSelectOptions === "function";
    const relationPreviewReady = typeof formatAdminChangeValueText === "function" && typeof getAdminRelationValueDisplay === "function" && typeof openAdminMasterDataDetailByCode === "function";
    const changeLogRelationReady = typeof getAdminChangeRelationInfo === "function" && typeof renderAdminRollbackMismatchValueCell === "function" && typeof getAdminRelationOpenTargetFromChange === "function";
    const createDeleteRollbackReady = typeof previewAdminCreateDeleteRollback === "function" && typeof applyAdminCreateDeleteRollback === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminCreateDeleteRollback === "function");
    const createDeleteRestoreReady = typeof previewAdminCreateDeleteRestore === "function" && typeof applyAdminCreateDeleteRestore === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminCreateDeleteRestore === "function");
    const layoutShell = getAdminLayoutShellReadiness();
    const result = { ok: apiReady && domReady && snapshotFilterReady && masterCatalogReady && masterDetailReady && adminChangeLogFilterReady && createLifecycleGuideReady && createLifecycleResultSummaryReady && adminJsSplitReadinessReady && changeLogSplitContractReady && createLifecycleSplitContractReady && editDraftSplitContractReady && editDraftExternalReady && createLifecycleExternalReady && masterApiVerifyReady && adminWriteGuardReady && layoutShell.ok, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, masterCatalogReady, masterDetailReady, masterRelationsReady, editDraftReady, fieldHelpReady, adminChangeLogReady, adminChangeLogDetailReady, adminChangeLogFilterReady, masterApiVerifyReady, postWriteApiVerifyReady, adminWriteGuardReady, relationSearchReady, relationPreviewReady, changeLogRelationReady, createBlueprintReady, createLifecycleGuideReady, createLifecycleDependencyGuideReady, createLifecycleResultSummaryReady, createLifecycleBatchCheckReady, adminJsSplitReadinessReady, adminJsSplitReadiness, changeLogSplitContractReady, changeLogSplitContract, createLifecycleSplitContractReady, createLifecycleSplitContract, editDraftSplitContractReady, editDraftSplitContract, editDraftExternalReady, editDraftExternal, changeLogsExternalReady, changeLogs, createLifecycleExternalReady, createLifecycle, createDraftPreviewReady, createApplyReady, createDeleteRollbackReady, createDeleteRestoreReady, layoutShellReady: layoutShell.ok, layoutShell, createBlueprint: getAdminCreateBlueprintReadiness(), createLifecycleGuide: getAdminCreateLifecycleGuideReadiness(), adminWriteDevKeySet: hasAdminWriteDevKey(), readOnly: false, writeLocked: !hasAdminWriteDevKey(), guardedApply: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom(), editDraft: getAdminEditDraftReadiness({ log: false }) };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin read-only page check", result);
    return result;
  }

  window.RpgAdminReadOnlyPage = {
    VERSION,
    refreshAdminReadOnlyPage,
    fetchAdminReadOnlyPageData,
    saveApiBaseUrlFromInput,
    resetApiBaseUrl,
    getCurrentAdminPageUrl,
    getGamePageUrl,
    syncLocationHints,
    copyCurrentAdminPageUrl,
    readSnapshotFiltersFromDom,
    resetSnapshotFilters,
    describeSnapshotFilters,
    readMasterCatalogFiltersFromDom,
    resetMasterCatalogFilters,
    describeMasterCatalogFilters,
    readChangeLogFiltersFromDom,
    resetChangeLogFilters,
    describeChangeLogFilters,
    readAdminCreateBlueprintFiltersFromDom,
    syncAdminCreateDomainFromCatalog,
    refreshAdminCreateBlueprint,
    renderAdminCreateBlueprint,
    getAdminCreateBlueprintFieldInputKind,
    getAdminCreateBlueprintRequiredKeys,
    getAdminCreateBlueprintDefaultDraft,
    getAdminCreateBlueprintReadiness,
    renderAdminCreateLifecycleGuide,
    renderAdminCreateLifecycleDependencyGuards,
    renderAdminCreateLifecycleBatchResult,
    runAdminCreateLifecycleBatchCheck,
    applyAdminChangeLogActionShortcut,
    getAdminCreateLifecycleGuideReadiness,
    getAdminJsSplitReadiness,
    renderAdminJsSplitReadiness,
    getAdminChangeLogSplitContractReadiness,
    renderAdminChangeLogSplitContractReadiness,
    getAdminCreateLifecycleSplitContractReadiness,
    renderAdminCreateLifecycleSplitContractReadiness,
    getAdminEditDraftSplitContractReadiness,
    renderAdminEditDraftSplitContractReadiness,
    getAdminChangeLogsReadiness,
    getAdminCreateLifecycleReadiness,
    getAdminEditDraftExternalReadiness,
    readAdminCreateDraftValues,
    resetAdminCreateDraft,
    previewAdminCreateDraft,
    applyAdminCreateDraft,
    renderAdminCreatePreviewResult,
    getAdminCreateFieldDefinition,
    getAdminCreateRelationDefinition,
    applyAdminCreateRelationOptionFilter,
    refreshDependentAdminCreateRelationSelects,
    openAdminMasterDataDetail,
    openAdminMasterDataDetailByCode,
    openAdminMasterDataRelations,
    renderMasterDetail,
    renderMasterRelations,
    renderMasterEditDraft,
    readAdminEditDraftValues,
    resetAdminEditDraft,
    previewAdminEditDraft,
    applyAdminEditDraft,
    renderAdminEditPreviewResult,
    readAdminEditApplyControls,
    buildAdminEditImpactGuide,
    renderAdminEditDraftReview,
    buildAdminEditDraftReview,
    sortAdminChangesByRisk,
    renderAdminEditImpactGuide,
    refreshAdminEditImpactGuide,
    getAdminEditDraftReadiness,
    refreshAdminChangeLogs,
    renderAdminChangeLogs,
    openAdminChangeLogDetail,
    renderAdminChangeLogDetail,
    previewAdminChangeLogRollback,
    applyAdminChangeLogRollback,
    readAdminRollbackControls,
    renderAdminRollbackResult,
    previewAdminCreateDeleteRollback,
    applyAdminCreateDeleteRollback,
    readAdminCreateDeleteControls,
    renderAdminCreateDeleteResult,
    previewAdminCreateDeleteRestore,
    applyAdminCreateDeleteRestore,
    readAdminCreateDeleteRestoreControls,
    renderAdminCreateDeleteRestoreResult,
    syncAdminWriteDevKeyInput,
    saveAdminWriteDevKeyFromInput,
    clearAdminWriteDevKey,
    hasAdminWriteDevKey,
    verifySelectedMasterDataApi,
    runPostWriteMasterApiVerification,
    renderMasterApiVerifyResult,
    findMasterApiRow,
    buildMasterApiVerifyComparisons,
    getAdminFieldHelp,
    listAdminFieldHelp,
    getAdminFieldValueHint,
    renderFieldValueHintInline,
    isAdminEditApplyAllowedField,
    getAdminEditAllowedFields,
    getAdminDraftFieldInputKind,
    getAdminDraftSelectOptions,
    getAdminRelationEditOptionDefinitions,
    getAdminRelationEditOptionDefinition,
    isAdminRelationEditField,
    getAdminRelationComboGuardLabels,
    refreshDependentAdminRelationSelects,
    applyAdminRelationOptionFilter,
    clearAdminRelationOptionFilter,
    filterAdminDraftSelectOptions,
    renderAdminDraftSelectOptionsHtml,
    getAdminRelationSelectMetaText,
    renderAdminRelationEditOptionsNote,
    getAdminEquipSlotDisplayName,
    getAdminDraftFieldRisk,
    getAdminRelationOpenTarget,
    getAdminChangeRelationInfo,
    getAdminRelationOpenTargetFromChange,
    renderAdminRollbackMismatchValueCell,
    getAdminDraftLockedReason,
    initializeAdminLayoutShell,
    getAdminLayoutShellReadiness,
    setAdminSectionCollapsed,
    setAdminActiveSidebarLink,
    checkAdminReadOnlyPageReady,
  };
  window.refreshAdminReadOnlyPage = refreshAdminReadOnlyPage;
  window.fetchAdminReadOnlyPageData = fetchAdminReadOnlyPageData;
  window.readAdminSnapshotFilters = readSnapshotFiltersFromDom;
  window.resetAdminSnapshotFilters = resetSnapshotFilters;
  window.readAdminMasterCatalogFilters = readMasterCatalogFiltersFromDom;
  window.resetAdminMasterCatalogFilters = resetMasterCatalogFilters;
  window.readAdminChangeLogFilters = readChangeLogFiltersFromDom;
  window.resetAdminChangeLogFilters = resetChangeLogFilters;
  window.readAdminCreateBlueprintFilters = readAdminCreateBlueprintFiltersFromDom;
  window.syncAdminCreateDomainFromCatalog = syncAdminCreateDomainFromCatalog;
  window.refreshAdminCreateBlueprint = refreshAdminCreateBlueprint;
  window.getAdminCreateBlueprintFieldInputKind = getAdminCreateBlueprintFieldInputKind;
  window.getAdminCreateBlueprintRequiredKeys = getAdminCreateBlueprintRequiredKeys;
  window.getAdminCreateBlueprintDefaultDraft = getAdminCreateBlueprintDefaultDraft;
  window.getAdminCreateBlueprintReadiness = getAdminCreateBlueprintReadiness;
  window.renderAdminCreateLifecycleGuide = renderAdminCreateLifecycleGuide;
  window.renderAdminCreateLifecycleBatchResult = renderAdminCreateLifecycleBatchResult;
  window.runAdminCreateLifecycleBatchCheck = runAdminCreateLifecycleBatchCheck;
  window.getAdminCreateLifecycleGuideReadiness = getAdminCreateLifecycleGuideReadiness;
  window.getAdminJsSplitReadiness = getAdminJsSplitReadiness;
  window.renderAdminJsSplitReadiness = renderAdminJsSplitReadiness;
  window.getAdminChangeLogSplitContractReadiness = getAdminChangeLogSplitContractReadiness;
  window.renderAdminChangeLogSplitContractReadiness = renderAdminChangeLogSplitContractReadiness;
  window.getAdminCreateLifecycleSplitContractReadiness = getAdminCreateLifecycleSplitContractReadiness;
  window.renderAdminCreateLifecycleSplitContractReadiness = renderAdminCreateLifecycleSplitContractReadiness;
  window.getAdminEditDraftSplitContractReadiness = getAdminEditDraftSplitContractReadiness;
  window.renderAdminEditDraftSplitContractReadiness = renderAdminEditDraftSplitContractReadiness;
  window.getAdminChangeLogsReadiness = getAdminChangeLogsReadiness;
  window.getAdminCreateLifecycleReadiness = getAdminCreateLifecycleReadiness;
  window.getAdminEditDraftExternalReadiness = getAdminEditDraftExternalReadiness;
  window.readAdminCreateDraftValues = readAdminCreateDraftValues;
  window.resetAdminCreateDraft = resetAdminCreateDraft;
  window.previewAdminCreateDraft = previewAdminCreateDraft;
  window.applyAdminCreateDraft = applyAdminCreateDraft;
  window.getAdminCreateFieldDefinition = getAdminCreateFieldDefinition;
  window.getAdminCreateRelationDefinition = getAdminCreateRelationDefinition;
  window.applyAdminCreateRelationOptionFilter = applyAdminCreateRelationOptionFilter;
  window.refreshDependentAdminCreateRelationSelects = refreshDependentAdminCreateRelationSelects;
  window.refreshAdminChangeLogs = refreshAdminChangeLogs;
  window.openAdminMasterDataDetail = openAdminMasterDataDetail;
  window.openAdminMasterDataDetailByCode = openAdminMasterDataDetailByCode;
  window.openAdminMasterDataRelations = openAdminMasterDataRelations;
  window.checkAdminReadOnlyPageReady = checkAdminReadOnlyPageReady;
  window.initializeAdminLayoutShell = initializeAdminLayoutShell;
  window.getAdminLayoutShellReadiness = getAdminLayoutShellReadiness;
  window.getAdminDefaultCollapsedSectionKeys = getAdminDefaultCollapsedSectionKeys;
  window.updateAdminStickyLayoutOffsets = updateAdminStickyLayoutOffsets;
  window.setAdminSectionCollapsed = setAdminSectionCollapsed;
  window.setAdminActiveSidebarLink = setAdminActiveSidebarLink;
  window.getAdminEditDraftReadiness = getAdminEditDraftReadiness;
  window.syncAdminWriteDevKeyInput = syncAdminWriteDevKeyInput;
  window.saveAdminWriteDevKeyFromInput = saveAdminWriteDevKeyFromInput;
  window.clearAdminWriteDevKey = clearAdminWriteDevKey;
  window.hasAdminWriteDevKey = hasAdminWriteDevKey;
  window.readAdminEditDraftValues = readAdminEditDraftValues;
  window.resetAdminEditDraft = resetAdminEditDraft;
  window.previewAdminEditDraft = previewAdminEditDraft;
  window.buildAdminEditImpactGuide = buildAdminEditImpactGuide;
  window.refreshAdminEditImpactGuide = refreshAdminEditImpactGuide;
  window.getAdminFieldHelp = getAdminFieldHelp;
  window.listAdminFieldHelp = listAdminFieldHelp;
  window.getAdminFieldValueHint = getAdminFieldValueHint;
  window.getAdminDraftFieldInputKind = getAdminDraftFieldInputKind;
  window.getAdminDraftSelectOptions = getAdminDraftSelectOptions;
  window.getAdminRelationEditOptionDefinitions = getAdminRelationEditOptionDefinitions;
  window.getAdminRelationEditOptionDefinition = getAdminRelationEditOptionDefinition;
  window.isAdminRelationEditField = isAdminRelationEditField;
  window.getAdminEquipSlotDisplayName = getAdminEquipSlotDisplayName;
  window.markSelectedMasterCatalogRow = markSelectedMasterCatalogRow;
  window.getAdminDraftFieldRisk = getAdminDraftFieldRisk;
  window.refreshDependentAdminRelationSelects = refreshDependentAdminRelationSelects;
  window.applyAdminRelationOptionFilter = applyAdminRelationOptionFilter;
  window.clearAdminRelationOptionFilter = clearAdminRelationOptionFilter;
  window.filterAdminDraftSelectOptions = filterAdminDraftSelectOptions;
  window.getAdminRelationSelectMetaText = getAdminRelationSelectMetaText;
  window.getAdminRelationComboGuardLabels = getAdminRelationComboGuardLabels;
  window.getAdminDraftLockedReason = getAdminDraftLockedReason;
  window.buildAdminEditDraftReview = buildAdminEditDraftReview;
  window.sortAdminChangesByRisk = sortAdminChangesByRisk;
  window.formatAdminChangeAfterValue = formatAdminChangeAfterValue;
  window.formatAdminChangeValueText = formatAdminChangeValueText;
  window.getAdminRelationValueDisplay = getAdminRelationValueDisplay;
  window.getAdminRelationOpenTarget = getAdminRelationOpenTarget;
  window.getAdminChangeRelationInfo = getAdminChangeRelationInfo;
  window.getAdminRelationOpenTargetFromChange = getAdminRelationOpenTargetFromChange;
  window.renderAdminRollbackMismatchValueCell = renderAdminRollbackMismatchValueCell;
  window.getCurrentAdminPageUrl = getCurrentAdminPageUrl;
  window.copyCurrentAdminPageUrl = copyCurrentAdminPageUrl;
  window.openAdminChangeLogDetail = openAdminChangeLogDetail;
  window.previewAdminChangeLogRollback = previewAdminChangeLogRollback;
  window.applyAdminChangeLogRollback = applyAdminChangeLogRollback;
  window.readAdminRollbackControls = readAdminRollbackControls;
  window.previewAdminCreateDeleteRollback = previewAdminCreateDeleteRollback;
  window.applyAdminCreateDeleteRollback = applyAdminCreateDeleteRollback;
  window.readAdminCreateDeleteControls = readAdminCreateDeleteControls;
  window.previewAdminCreateDeleteRestore = previewAdminCreateDeleteRestore;
  window.applyAdminCreateDeleteRestore = applyAdminCreateDeleteRestore;
  window.readAdminCreateDeleteRestoreControls = readAdminCreateDeleteRestoreControls;
  window.renderAdminCreateDeleteRestoreResult = renderAdminCreateDeleteRestoreResult;
  window.verifySelectedMasterDataApi = verifySelectedMasterDataApi;
  window.runPostWriteMasterApiVerification = runPostWriteMasterApiVerification;

  configureAdminEditDraft();
  configureAdminCreateLifecycle();
  configureAdminChangeLogs();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
