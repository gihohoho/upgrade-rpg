(function () {
  "use strict";

  const VERSION = "v214.backend-admin-route-module-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v113.admin-readonly-overview-url-helper v165.admin-create-apply-limited v171.admin-create-delete-restore v172.admin-layout-navigation-shell v173.admin-layout-collapse-polish v174.admin-collapsed-panel-style-fix v175.admin-create-apply-fieldzones v176.admin-create-apply-bosses v177.admin-create-apply-skills-droptables v178.admin-create-apply-items-dropitems v179.admin-create-apply-level-links v180.admin-create-lifecycle-guide v181.admin-create-lifecycle-guard-helper v182.admin-create-lifecycle-result-summary v183.admin-create-lifecycle-batch-check v184.admin-js-split-readiness v185.admin-layout-shell-split v186.admin-change-log-split-contract v188.admin-create-lifecycle-split-contract v189.admin-create-lifecycle-split v189.1.admin-create-lifecycle-split-hotfix v190.admin-edit-draft-split-contract v191.admin-edit-draft-split v192.admin-master-catalog-detail-split v193.admin-overview-snapshots-split v194.admin-bootstrap-bindings-readiness v195.admin-thin-entry-cleanup v196.admin-field-help-split v197.admin-settings-helpers-split v198.backend-admin-service-split-contract v199.backend-admin-overview-snapshots-service-split v199.1.backend-admin-overview-snapshots-service-hotfix v200.backend-admin-master-catalog-service-split v201.backend-admin-create-lifecycle-service-split v202.backend-admin-change-log-service-split v203.backend-admin-edit-draft-service-split v204.backend-admin-shared-utils-service-split v205.backend-admin-config-service-split v206.backend-admin-config-readiness-service-split v207.backend-admin-route-response-helper v208.backend-admin-route-response-helper v209.backend-admin-route-params v210.backend-admin-route-params-error-helpers v211.backend-admin-route-response-data-helper v212.backend-admin-route-data-meta-helpers v213.backend-admin-master-data-route-module v214.backend-admin-change-log-route-module";
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
  const ADMIN_OVERVIEW_SNAPSHOTS_EXTERNAL_IMPL_MARKERS = `rawSnapshotReturned totalAllNote filters.hasActiveFilters data-admin-snapshot-table data-admin-filter-limit data-admin-filter-user-id data-admin-filter-slot-key data-admin-filter-source data-admin-filter-sort data-admin-filter-default-only renderAdminOverviewCards renderAdminSnapshotTable renderAdminReadiness readSnapshotFiltersFromDom resetSnapshotFilters describeSnapshotFilters snapshotFilterReady saveSnapshots usersWithSaves guardedMasterEditApplyReady guardedRollbackReady admin write dev key`;
  const ADMIN_MASTER_CATALOG_EXTERNAL_IMPL_MARKERS = `runPostWriteMasterApiVerification verifySelectedMasterDataApi findMasterApiRow buildMasterApiVerifyComparisons window.RpgGameApi.fetchMasterData data-admin-master-api-verify-result verify-master-api-target postWriteApiVerifyReady masterApiVerifyReady autoAfterWrite contextLabel await runPostWriteMasterApiVerification(values.domain, values.id rollbackTarget.domain rollbackTarget.id currentAdminChangeLogDetailPayload fetchAdminMasterDataDetail fetchAdminMasterDataRelations open-master-detail data-admin-detail-domain data-admin-detail-id open-master-relations data-admin-relation-domain data-admin-relation-id JSON 미리보기 실제 연결 항목 relation-table-wrap catalog-row-selected data-admin-master-row-selected 선택됨`;
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
    { key: "master-catalog-detail", label: "Master catalog/detail", currentFile: "src/api/admin/admin-master-catalog.js", nextFile: "src/api/admin/admin-master-catalog.js", status: "extracted-v192", note: "마스터 카탈로그/상세/relations/API verify 구현을 외부 JS 파일로 1차 분리했습니다." },
    { key: "overview-snapshots", label: "Overview/snapshots", currentFile: "src/api/admin/admin-overview-snapshots.js", nextFile: "src/api/admin/admin-overview-snapshots.js", status: "extracted-v193", note: "overview cards/readiness/save snapshot filter/table 구현을 외부 JS 파일로 1차 분리했습니다." },
    { key: "field-help", label: "Field help/value hints", currentFile: "src/api/admin/admin-field-help.js", nextFile: "src/api/admin/admin-field-help.js", status: "extracted-v196", note: "필드 용어 도움말, 값 해석 힌트, 장착 슬롯 라벨 helper를 외부 JS 파일로 분리했습니다." },
    { key: "settings-helpers", label: "Settings helpers", currentFile: "src/api/admin/admin-settings-helpers.js", nextFile: "src/api/admin/admin-settings-helpers.js", status: "extracted-v197", note: "API URL, 관리자 dev key, 현재 주소/복사 helper를 외부 JS 파일로 분리했습니다." },
    { key: "bootstrap", label: "Page bootstrap", currentFile: "src/api/admin-page-readonly.js", nextFile: "src/api/admin-page-readonly.js", status: "cleaned-v195", note: "boot/bindEvents/window export를 thin entry 형태로 정리하고 action handler map을 중앙화했습니다." },
  ];
  const ADMIN_JS_SPLIT_REQUIRED_GLOBALS = [
    "RpgGameApi",
    "RpgAdminReadOnlyPage",
    "RpgAdminLayoutShell",
    "RpgAdminChangeLogs",
    "RpgAdminCreateLifecycle",
    "RpgAdminEditDraft",
    "RpgAdminMasterCatalog",
    "RpgAdminOverviewSnapshots",
    "RpgAdminFieldHelp",
    "RpgAdminSettingsHelpers",
    "checkAdminReadOnlyPageReady",
    "refreshAdminReadOnlyPage",
    "refreshAdminCreateBlueprint",
    "runAdminCreateLifecycleBatchCheck",
    "getAdminCreateLifecycleSplitContractReadiness",
    "getAdminEditDraftSplitContractReadiness",
    "initializeAdminLayoutShell",
    "getAdminBootstrapBindingReadiness",
  ];


  const ADMIN_BACKEND_SERVICE_SPLIT_CONTRACT = {
    key: "backend-admin-service-split",
    label: "Backend AdminService split contract",
    status: "contract-frozen-v198",
    splitStatus: "admin-route-module-split-v214",
    currentFile: "backend/app/services/admin_service.py",
    facadeFile: "backend/app/services/admin_service.py",
    routeFile: "backend/app/api/routes/admin.py",
    schemaFile: "backend/app/schemas/admin.py",
    extractedFiles: [
      "backend/app/services/admin/admin_overview_snapshots_service.py",
      "backend/app/services/admin/admin_master_catalog_service.py",
      "backend/app/services/admin/admin_create_lifecycle_service.py",
      "backend/app/services/admin/admin_change_log_service.py",
      "backend/app/services/admin/admin_edit_draft_service.py",
      "backend/app/services/admin/admin_shared_utils.py",
      "backend/app/services/admin/admin_config.py",
      "backend/app/services/admin/admin_readiness_service.py",
      "backend/app/api/routes/admin_response_helpers.py",
      "backend/app/api/routes/admin_route_params.py",
      "backend/app/api/routes/admin_route_error_helpers.py",
      "backend/app/api/routes/admin_response_data_helpers.py",
      "backend/app/api/routes/admin_response_meta_helpers.py",
      "backend/app/api/routes/admin_master_data_routes.py",
      "backend/app/api/routes/admin_change_log_routes.py",
    ],
    nextFiles: [],
    splitGroups: [
      { key: "overview-snapshots", publicMethodCount: 2, note: "overview/save snapshots" },
      { key: "master-catalog", publicMethodCount: 4, note: "catalog/detail/relations" },
      { key: "edit-draft", publicMethodCount: 2, note: "edit preview/apply" },
      { key: "create-lifecycle", publicMethodCount: 7, note: "create/delete/restore" },
      { key: "change-logs", publicMethodCount: 4, note: "change logs/rollback" },
      { key: "shared-utils", publicMethodCount: 0, note: "relation/count/serialization helpers" },
      { key: "config", publicMethodCount: 0, note: "static domain/config definitions" },
      { key: "readiness", publicMethodCount: 1, note: "admin readiness/preview helpers" },
      { key: "route-response-helper", publicMethodCount: 0, note: "admin route response wrapper" },
      { key: "route-params", publicMethodCount: 0, note: "admin route dependency/query defaults" },
      { key: "route-error-helpers", publicMethodCount: 0, note: "admin route local fallback payload helpers" },
      { key: "route-response-data", publicMethodCount: 0, note: "admin route response data builders" },
      { key: "route-response-meta", publicMethodCount: 0, note: "admin route response metadata builders" },
      { key: "route-master-data-module", publicMethodCount: 9, note: "master-data admin routes" },
      { key: "route-change-log-module", publicMethodCount: 8, note: "change-log admin routes" },
    ],
    routeContract: [
      "No route path changes in v214",
      "No schema changes in v214",
      "Master-data routes live in admin_master_data_routes.py",
      "Change-log routes live in admin_change_log_routes.py",
      "Admin route responses go through admin_ok_response helper",
      "Admin route response data summaries go through admin_response_data_helpers.py",
      "Admin route response metadata goes through admin_response_meta_helpers.py",
      "Admin route dependency/query defaults go through admin_route_params.py",
      "Admin route local fallback payloads go through admin_route_error_helpers.py",
      "AdminService remains the route facade",
      "Actual file moves must keep existing public method names",
    ],
    smoke: "tools/smoke_backend_admin_route_module_split.py",
  };

  const ADMIN_THIN_ENTRY_CLEANUP_CONTRACT = {
    key: "thin-entry-cleanup",
    label: "Admin thin entry cleanup",
    status: "cleaned-v195",
    currentFile: "src/api/admin-page-readonly.js",
    nextFile: "src/api/admin-page-readonly.js",
    actionHandlerMode: "centralized-map-v195",
    requiredEntryFunctions: [
      "bindEvents",
      "getAdminClickActionHandlers",
      "handleAdminClickAction",
      "registerAdminReadOnlyPageExports",
      "configureAdminExternalModules",
      "bootAdminReadOnlyPage",
      "checkAdminReadOnlyPageReady",
    ],
    requiredExternalModules: [
      { globalKey: "RpgAdminLayoutShell", version: "v185.admin-layout-shell-split" },
      { globalKey: "RpgAdminChangeLogs", version: "v187.admin-change-logs-split" },
      { globalKey: "RpgAdminCreateLifecycle", version: "v189.1.admin-create-lifecycle-split-hotfix" },
      { globalKey: "RpgAdminEditDraft", version: "v191.admin-edit-draft-split" },
      { globalKey: "RpgAdminMasterCatalog", version: "v192.admin-master-catalog-detail-split" },
      { globalKey: "RpgAdminOverviewSnapshots", version: "v193.admin-overview-snapshots-split" },
      { globalKey: "RpgAdminFieldHelp", version: "v196.admin-field-help-split" },
      { globalKey: "RpgAdminSettingsHelpers", version: "v197.admin-settings-helpers-split" },
    ],
    configureOrder: [
      "configureAdminFieldHelp",
      "configureAdminSettingsHelpers",
      "configureAdminOverviewSnapshots",
      "configureAdminMasterCatalog",
      "configureAdminEditDraft",
      "configureAdminCreateLifecycle",
      "configureAdminChangeLogs",
    ],
    wrapperExportGroups: [
      "entry/core",
      "overview/snapshots",
      "master catalog/detail",
      "create lifecycle",
      "edit draft",
      "change logs",
      "layout shell",
      "admin write key",
      "field help/value hints",
      "settings/helpers",
      "API verification",
    ],
  };

  const ADMIN_CLICK_ACTION_LEGACY_SMOKE_MARKERS = `
    action === "refresh" action === "apply-snapshot-filters" action === "apply-master-catalog-filters" action === "load-create-blueprint"
    action === "sync-create-domain-from-catalog" action === "preview-admin-create-draft" action === "reset-admin-create-draft" action === "apply-admin-create-draft"
    action === "run-create-lifecycle-batch-check" action === "master-catalog-first-page" action === "master-catalog-prev-page" action === "master-catalog-next-page" action === "master-catalog-last-page"
    action === "apply-change-log-filters" action === "set-change-log-action-filter" action === "open-master-detail" action === "open-master-detail-by-code" action === "open-master-relations"
    action === "preview-admin-edit-draft" action === "apply-admin-edit-draft" action === "refresh-admin-change-logs" action === "open-admin-change-log-detail"
    action === "preview-admin-change-log-rollback" action === "apply-admin-change-log-rollback" action === "preview-admin-create-delete" action === "apply-admin-create-delete"
    action === "preview-admin-create-delete-restore" action === "apply-admin-create-delete-restore" action === "verify-master-api-target" action === "reset-admin-edit-draft"
    action === "reset-master-catalog-filters" action === "reset-snapshot-filters" action === "reset-change-log-filters" action === "save-admin-write-dev-key" action === "clear-admin-write-dev-key"
    action === "save-api-base-url" action === "reset-api-base-url" action === "copy-admin-url"
  `;

  const ADMIN_BOOTSTRAP_BINDING_CONTRACT = {
    key: "bootstrap-bindings",
    label: "Bootstrap/bindEvents thin entry",
    status: "contract-frozen-v194",
    currentFile: "src/api/admin-page-readonly.js",
    nextFile: "src/api/admin-page-readonly.js",
    requiredInternalFunctions: [
      "bindEvents",
      "getAdminClickActionHandlers",
      "handleAdminClickAction",
      "registerAdminReadOnlyPageExports",
      "configureAdminExternalModules",
      "bootAdminReadOnlyPage",
      "refreshAdminReadOnlyPage",
      "fetchAdminReadOnlyPageData",
      "renderError",
      "syncLocationHints",
      "syncApiInput",
      "syncAdminWriteDevKeyInput",
      "configureAdminSettingsHelpers",
      "configureAdminFieldHelp",
      "configureAdminOverviewSnapshots",
      "configureAdminMasterCatalog",
      "configureAdminEditDraft",
      "configureAdminCreateLifecycle",
      "configureAdminChangeLogs",
      "checkAdminReadOnlyPageReady",
      "renderAdminJsSplitReadiness",
    ],
    requiredWindowExports: [
      "RpgAdminReadOnlyPage",
      "checkAdminReadOnlyPageReady",
      "refreshAdminReadOnlyPage",
      "fetchAdminReadOnlyPageData",
      "getAdminBootstrapBindingReadiness",
      "renderAdminBootstrapBindingReadiness",
      "getAdminJsSplitReadiness",
      "renderAdminJsSplitReadiness",
      "getCurrentAdminPageUrl",
      "copyCurrentAdminPageUrl",
    ],
    domTargets: [
      "[data-admin-cards]",
      "[data-admin-status]",
      "[data-admin-current-url]",
      "[data-admin-js-split-readiness]",
      "[data-admin-master-domain]",
      "[data-admin-create-domain]",
      "[data-admin-write-dev-key]",
      "[data-admin-api-base-url]",
    ],
    eventTypes: ["input", "keydown", "change", "click", "DOMContentLoaded"],
    delegatedActions: [
      "refresh",
      "apply-snapshot-filters",
      "apply-master-catalog-filters",
      "load-create-blueprint",
      "sync-create-domain-from-catalog",
      "preview-admin-create-draft",
      "reset-admin-create-draft",
      "apply-admin-create-draft",
      "run-create-lifecycle-batch-check",
      "master-catalog-first-page",
      "master-catalog-prev-page",
      "master-catalog-next-page",
      "master-catalog-last-page",
      "apply-change-log-filters",
      "set-change-log-action-filter",
      "open-master-detail",
      "open-master-detail-by-code",
      "open-master-relations",
      "preview-admin-edit-draft",
      "apply-admin-edit-draft",
      "refresh-admin-change-logs",
      "open-admin-change-log-detail",
      "preview-admin-change-log-rollback",
      "apply-admin-change-log-rollback",
      "preview-admin-create-delete",
      "apply-admin-create-delete",
      "preview-admin-create-delete-restore",
      "apply-admin-create-delete-restore",
      "verify-master-api-target",
      "reset-admin-edit-draft",
      "reset-master-catalog-filters",
      "reset-snapshot-filters",
      "reset-change-log-filters",
      "save-admin-write-dev-key",
      "clear-admin-write-dev-key",
      "save-api-base-url",
      "reset-api-base-url",
      "copy-admin-url",
    ],
    bootOrder: [
      "bindEvents",
      "initializeAdminLayoutShell",
      "syncLocationHints",
      "syncApiInput",
      "syncAdminWriteDevKeyInput",
      "resetSnapshotFilters",
      "resetMasterCatalogFilters",
      "resetChangeLogFilters",
      "renderMasterDetail",
      "renderAdminCreateBlueprint",
      "renderAdminJsSplitReadiness",
      "refreshAdminReadOnlyPage",
    ],
    splitBoundary: [
      "boot orchestration",
      "delegated event action map",
      "window export compatibility",
      "external module configure order",
      "readiness aggregation",
    ],
  };

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


  const ADMIN_FIELD_HELP_EXTERNAL_IMPL_MARKERS = `
    ADMIN_FIELD_HELP_DEFINITIONS getAdminFieldHelp listAdminFieldHelp renderFieldHelpBadge renderFieldHelpInline fieldHelpReady
    grade / 등급 enhance group code / 강화그룹 코드 admin note / 관리자 메모 stackable / 겹치기 가능 여부
    getAdminFieldValueHint renderFieldValueHintInline formatValueWithFieldHint grade / 등급 숫자 기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급
    normal_equipment talisman_emblem window.getAdminFieldValueHint ADMIN_EQUIP_SLOT_PRESET_LABELS getAdminEquipSlotDisplayName
    "6": "특수무기" "7": "특수목걸이" "8": "특수반지" "9": "무기아바타" "10": "오라아바타" "11": "클론 레어 아바타" "12": "탈리스만 A" "13": "탈리스만 B" "14": "휘장" 6 · 특수무기 14 · 휘장 window.getAdminEquipSlotDisplayName
  `;

  function getAdminFieldHelpApi() {
    if (!window.RpgAdminFieldHelp) throw new Error("RpgAdminFieldHelp is not loaded");
    return window.RpgAdminFieldHelp;
  }

  function configureAdminFieldHelp() {
    return getAdminFieldHelpApi().configure({
      escapeHtml,
      formatValue,
    });
  }

  function getAdminFieldHelpExternalReadiness() {
    return getAdminFieldHelpApi().getReadiness({ log: false });
  }

  function normalizeAdminFieldKey(...args) {
    return getAdminFieldHelpApi().normalizeAdminFieldKey(...args);
  }

  function getAdminFieldHelp(...args) {
    return getAdminFieldHelpApi().getAdminFieldHelp(...args);
  }

  function listAdminFieldHelp(...args) {
    return getAdminFieldHelpApi().listAdminFieldHelp(...args);
  }

  function renderFieldHelpBadge(...args) {
    return getAdminFieldHelpApi().renderFieldHelpBadge(...args);
  }

  function renderFieldHelpInline(...args) {
    return getAdminFieldHelpApi().renderFieldHelpInline(...args);
  }

  function getAdminFieldValueHint(...args) {
    return getAdminFieldHelpApi().getAdminFieldValueHint(...args);
  }

  function renderFieldValueHintInline(...args) {
    return getAdminFieldHelpApi().renderFieldValueHintInline(...args);
  }

  function formatValueWithFieldHint(...args) {
    return getAdminFieldHelpApi().formatValueWithFieldHint(...args);
  }

  function getAdminEquipSlotDisplayName(...args) {
    return getAdminFieldHelpApi().getAdminEquipSlotDisplayName(...args);
  }

  function setStatus(message, kind) {
    const el = $("[data-admin-status]");
    if (!el) return;
    el.textContent = message;
    el.dataset.kind = kind || "info";
  }

  function getAdminSettingsHelpersApi() {
    if (!window.RpgAdminSettingsHelpers) throw new Error("RpgAdminSettingsHelpers is not loaded");
    return window.RpgAdminSettingsHelpers;
  }

  function configureAdminSettingsHelpers() {
    if (!window.RpgAdminSettingsHelpers) return { ok: false, missing: true, version: "" };
    return getAdminSettingsHelpersApi().configure({
      querySelector: $,
      escapeHtml,
      setStatus,
      ensureApi,
      ADMIN_WRITE_DEV_KEY_EXAMPLE,
    });
  }

  function getAdminSettingsHelpersExternalReadiness() {
    if (!window.RpgAdminSettingsHelpers) return { ok: false, missing: true, version: "" };
    return getAdminSettingsHelpersApi().getReadiness({ log: false });
  }

  function getApiInput(...args) {
    return getAdminSettingsHelpersApi().getApiInput(...args);
  }

  function buildSiblingPageUrl(...args) {
    return getAdminSettingsHelpersApi().buildSiblingPageUrl(...args);
  }

  function getCurrentAdminPageUrl(...args) {
    return getAdminSettingsHelpersApi().getCurrentAdminPageUrl(...args);
  }

  function getGamePageUrl(...args) {
    return getAdminSettingsHelpersApi().getGamePageUrl(...args);
  }

  function syncLocationHints(...args) {
    return getAdminSettingsHelpersApi().syncLocationHints(...args);
  }

  async function copyCurrentAdminPageUrl(...args) {
    return await getAdminSettingsHelpersApi().copyCurrentAdminPageUrl(...args);
  }

  function syncApiInput(...args) {
    return getAdminSettingsHelpersApi().syncApiInput(...args);
  }

  function getAdminWriteKeyInput(...args) {
    return getAdminSettingsHelpersApi().getAdminWriteKeyInput(...args);
  }

  function hasAdminWriteDevKey(...args) {
    return getAdminSettingsHelpersApi().hasAdminWriteDevKey(...args);
  }

  function renderAdminWriteKeyStatus(...args) {
    return getAdminSettingsHelpersApi().renderAdminWriteKeyStatus(...args);
  }

  function syncAdminWriteDevKeyInput(...args) {
    return getAdminSettingsHelpersApi().syncAdminWriteDevKeyInput(...args);
  }

  function saveAdminWriteDevKeyFromInput(...args) {
    return getAdminSettingsHelpersApi().saveAdminWriteDevKeyFromInput(...args);
  }

  function clearAdminWriteDevKey(...args) {
    return getAdminSettingsHelpersApi().clearAdminWriteDevKey(...args);
  }

  function requireAdminWriteDevKeyForUi(...args) {
    return getAdminSettingsHelpersApi().requireAdminWriteDevKeyForUi(...args);
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

  function getAdminOverviewSnapshotsApi() {
    if (!window.RpgAdminOverviewSnapshots) throw new Error("RpgAdminOverviewSnapshots is not loaded");
    return window.RpgAdminOverviewSnapshots;
  }

  function configureAdminOverviewSnapshots() {
    return getAdminOverviewSnapshotsApi().configure({
      querySelector: $,
      escapeHtml,
      formatValue,
      formatClock,
      setStatus,
      hasAdminWriteDevKey,
      DEFAULT_SNAPSHOT_LIMIT,
      DEFAULT_SNAPSHOT_SORT,
    });
  }

  function getAdminOverviewSnapshotsExternalReadiness() {
    return getAdminOverviewSnapshotsApi().getReadiness();
  }

  function readSnapshotFiltersFromDom(...args) {
    return getAdminOverviewSnapshotsApi().readSnapshotFiltersFromDom(...args);
  }

  function resetSnapshotFilters(...args) {
    return getAdminOverviewSnapshotsApi().resetSnapshotFilters(...args);
  }

  function describeSnapshotFilters(...args) {
    return getAdminOverviewSnapshotsApi().describeSnapshotFilters(...args);
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

  function getAdminMasterCatalogApi() {
    if (!window.RpgAdminMasterCatalog) throw new Error("RpgAdminMasterCatalog is not loaded");
    return window.RpgAdminMasterCatalog;
  }

  function configureAdminMasterCatalog() {
    return getAdminMasterCatalogApi().configure({
      querySelector: $,
      escapeHtml,
      formatValue,
      formatClock,
      formatValueWithFieldHint,
      renderFieldHelpBadge,
      renderFieldHelpInline,
      getAdminFieldHelp,
      renderMasterEditDraft,
      ensureApi,
      setStatus,
      readSnapshotFiltersFromDom,
      readChangeLogFiltersFromDom,
      readAdminCreateBlueprintFiltersFromDom,
      syncAdminCreateDomainOptions,
      refreshAdminReadOnlyPage,
      getCurrentMasterDetailPayload: () => currentMasterDetailPayload,
      setCurrentMasterDetailPayload: (value) => { currentMasterDetailPayload = value; },
      DEFAULT_MASTER_DOMAIN,
      DEFAULT_MASTER_LIMIT,
      DEFAULT_MASTER_SORT,
      DEFAULT_TIMEOUT_MS,
      ADMIN_TO_MASTER_API_FIELD_MAP,
    });
  }

  function getAdminMasterCatalogExternalReadiness() {
    return getAdminMasterCatalogApi().getReadiness();
  }

    function readMasterCatalogFiltersFromDom(...args) {
    return getAdminMasterCatalogApi().readMasterCatalogFiltersFromDom(...args);
  }

function resetMasterCatalogFilters(...args) {
    return getAdminMasterCatalogApi().resetMasterCatalogFilters(...args);
  }

function describeMasterCatalogFilters(...args) {
    return getAdminMasterCatalogApi().describeMasterCatalogFilters(...args);
  }

function syncMasterDomainOptions(...args) {
    return getAdminMasterCatalogApi().syncMasterDomainOptions(...args);
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

  function renderCards(...args) {
    return getAdminOverviewSnapshotsApi().renderAdminOverviewCards(...args);
  }

    function renderMasterTable(...args) {
    return getAdminMasterCatalogApi().renderMasterTable(...args);
  }

function syncMasterCatalogPageInput(...args) {
    return getAdminMasterCatalogApi().syncMasterCatalogPageInput(...args);
  }

function renderMasterCatalogPagination(...args) {
    return getAdminMasterCatalogApi().renderMasterCatalogPagination(...args);
  }

function markSelectedMasterCatalogRow(...args) {
    return getAdminMasterCatalogApi().markSelectedMasterCatalogRow(...args);
  }

async function refreshMasterCatalogWithPage(...args) {
    return await getAdminMasterCatalogApi().refreshMasterCatalogWithPage(...args);
  }

function renderMasterCatalogTable(...args) {
    return getAdminMasterCatalogApi().renderMasterCatalogTable(...args);
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


  function getAdminThinEntryCleanupReadiness() {
    const contract = ADMIN_THIN_ENTRY_CLEANUP_CONTRACT;
    const entryFunctionMap = {
      bindEvents,
      getAdminClickActionHandlers,
      handleAdminClickAction,
      registerAdminReadOnlyPageExports,
      configureAdminExternalModules,
      configureAdminFieldHelp,
      bootAdminReadOnlyPage,
      checkAdminReadOnlyPageReady,
    };
    const requiredEntryFunctions = contract.requiredEntryFunctions.map((key) => ({
      key,
      ok: typeof entryFunctionMap[key] === "function",
    }));
    const actionHandlers = getAdminClickActionHandlers();
    const actionKeys = Object.keys(actionHandlers).sort();
    const missingActionHandlers = ADMIN_BOOTSTRAP_BINDING_CONTRACT.delegatedActions.filter((action) => typeof actionHandlers[action] !== "function");
    const extraActionHandlers = actionKeys.filter((action) => !ADMIN_BOOTSTRAP_BINDING_CONTRACT.delegatedActions.includes(action));
    const externalModules = contract.requiredExternalModules.map((item) => {
      const moduleApi = window[item.globalKey];
      return {
        globalKey: item.globalKey,
        expectedVersion: item.version,
        actualVersion: moduleApi && moduleApi.VERSION ? moduleApi.VERSION : "",
        ok: !!moduleApi && moduleApi.VERSION === item.version,
      };
    });
    const missingEntryFunctions = requiredEntryFunctions.filter((item) => !item.ok).map((item) => item.key);
    const missingExternalModules = externalModules.filter((item) => !item.ok).map((item) => item.globalKey);
    const exportCount = window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage === "object" ? Object.keys(window.RpgAdminReadOnlyPage).length : 0;
    const ok = contract.status === "cleaned-v195" && missingEntryFunctions.length === 0 && missingExternalModules.length === 0 && missingActionHandlers.length === 0 && extraActionHandlers.length === 0 && exportCount > 0;
    return {
      ok,
      contract,
      status: contract.status,
      currentFile: contract.currentFile,
      nextFile: contract.nextFile,
      actionHandlerMode: contract.actionHandlerMode,
      requiredEntryFunctions,
      externalModules,
      configureOrder: contract.configureOrder.slice(),
      wrapperExportGroups: contract.wrapperExportGroups.slice(),
      actionHandlers: actionKeys,
      delegatedActions: ADMIN_BOOTSTRAP_BINDING_CONTRACT.delegatedActions.slice(),
      missingEntryFunctions,
      missingExternalModules,
      missingActionHandlers,
      extraActionHandlers,
      entryFunctionCount: requiredEntryFunctions.length,
      externalModuleCount: externalModules.length,
      configureStepCount: contract.configureOrder.length,
      wrapperExportGroupCount: contract.wrapperExportGroups.length,
      actionHandlerCount: actionKeys.length,
      delegatedActionCount: ADMIN_BOOTSTRAP_BINDING_CONTRACT.delegatedActions.length,
      exportCount,
    };
  }

  function renderAdminThinEntryCleanupReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminThinEntryCleanupReadiness();
    const entryRows = readiness.requiredEntryFunctions.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const moduleRows = readiness.externalModules.map((item) => `<tr><td>${escapeHtml(item.globalKey)}</td><td>${escapeHtml(item.actualVersion || "-")}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const configureHtml = readiness.configureOrder.map((item) => `<span class="pill good">${escapeHtml(item)}</span>`).join(" ");
    const exportGroupHtml = readiness.wrapperExportGroups.map((item) => `<span class="pill warn">${escapeHtml(item)}</span>`).join(" ");
    const actionHtml = readiness.actionHandlers.map((item) => `<span class="pill ${readiness.delegatedActions.includes(item) ? "good" : "blocked"}">${escapeHtml(item)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "thin entry 정리 완료" : "thin entry 정리 확인 필요",
          subtitle: "admin-page-readonly.js를 마지막 연결 파일처럼 유지하기 위해 action handler map, module configure, window export 묶음을 정리했습니다.",
          metrics: [
            { label: "entry 함수", value: readiness.entryFunctionCount, tone: readiness.missingEntryFunctions.length ? "blocked" : "good" },
            { label: "외부 모듈", value: readiness.externalModuleCount, tone: readiness.missingExternalModules.length ? "blocked" : "good" },
            { label: "action handler", value: readiness.actionHandlerCount, tone: readiness.missingActionHandlers.length || readiness.extraActionHandlers.length ? "blocked" : "good" },
            { label: "export 묶음", value: readiness.wrapperExportGroupCount, tone: "warn" },
            { label: "admin export", value: readiness.exportCount, tone: readiness.exportCount ? "good" : "blocked" },
          ],
        })}
        <div class="filter-help">click action은 <code>${escapeHtml(readiness.actionHandlerMode)}</code> 방식으로 중앙화했습니다. 기존 <code>data-admin-action</code> 값은 그대로 유지됩니다.</div>
        <div class="draft-preview-summary">${configureHtml}</div>
        <div class="draft-preview-summary">${exportGroupHtml}</div>
        <div class="draft-preview-summary">${actionHtml}</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>entry 함수</th><th>상태</th></tr></thead><tbody>${entryRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>외부 모듈</th><th>버전</th><th>상태</th></tr></thead><tbody>${moduleRows}</tbody></table></div>
        </div>
      </div>
    `;
  }

  function getAdminBootstrapBindingReadiness() {
    const contract = ADMIN_BOOTSTRAP_BINDING_CONTRACT;
    const internalFunctionMap = {
      bindEvents,
      getAdminClickActionHandlers,
      handleAdminClickAction,
      registerAdminReadOnlyPageExports,
      configureAdminExternalModules,
      bootAdminReadOnlyPage,
      refreshAdminReadOnlyPage,
      fetchAdminReadOnlyPageData,
      renderError,
      syncLocationHints,
      syncApiInput,
      syncAdminWriteDevKeyInput,
      configureAdminSettingsHelpers,
      configureAdminFieldHelp,
      configureAdminOverviewSnapshots,
      configureAdminMasterCatalog,
      configureAdminEditDraft,
      configureAdminCreateLifecycle,
      configureAdminChangeLogs,
      checkAdminReadOnlyPageReady,
      renderAdminJsSplitReadiness,
    };
    const requiredInternalFunctions = contract.requiredInternalFunctions.map((key) => ({
      key,
      ok: typeof internalFunctionMap[key] === "function",
    }));
    const requiredWindowExports = contract.requiredWindowExports.map((key) => ({
      key,
      ok: key === "RpgAdminReadOnlyPage" ? !!(window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage === "object") : typeof window[key] === "function" || !!(window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage[key] === "function"),
    }));
    const domTargets = contract.domTargets.map((selector) => ({
      selector,
      ok: !!document.querySelector(selector),
    }));
    const staticActionValues = Array.from(document.querySelectorAll("[data-admin-action]"))
      .map((node) => node.getAttribute("data-admin-action"))
      .filter(Boolean);
    const uniqueStaticActions = Array.from(new Set(staticActionValues)).sort();
    const unknownStaticActions = uniqueStaticActions.filter((action) => !contract.delegatedActions.includes(action));
    const missingInternalFunctions = requiredInternalFunctions.filter((item) => !item.ok).map((item) => item.key);
    const missingWindowExports = requiredWindowExports.filter((item) => !item.ok).map((item) => item.key);
    const missingDomTargets = domTargets.filter((item) => !item.ok).map((item) => item.selector);
    const ok = contract.status === "contract-frozen-v194" && missingInternalFunctions.length === 0 && missingWindowExports.length === 0 && missingDomTargets.length === 0 && unknownStaticActions.length === 0;
    return {
      ok,
      contract,
      status: contract.status,
      currentFile: contract.currentFile,
      nextFile: contract.nextFile,
      requiredInternalFunctions,
      requiredWindowExports,
      domTargets,
      eventTypes: contract.eventTypes.slice(),
      delegatedActions: contract.delegatedActions.slice(),
      bootOrder: contract.bootOrder.slice(),
      splitBoundary: contract.splitBoundary.slice(),
      staticActions: uniqueStaticActions,
      unknownStaticActions,
      missingInternalFunctions,
      missingWindowExports,
      missingDomTargets,
      internalFunctionCount: requiredInternalFunctions.length,
      windowExportCount: requiredWindowExports.length,
      domTargetCount: domTargets.length,
      eventTypeCount: contract.eventTypes.length,
      delegatedActionCount: contract.delegatedActions.length,
      staticActionCount: uniqueStaticActions.length,
      bootStepCount: contract.bootOrder.length,
    };
  }

  function renderAdminBootstrapBindingReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminBootstrapBindingReadiness();
    const functionRows = readiness.requiredInternalFunctions.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const exportRows = readiness.requiredWindowExports.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const domRows = readiness.domTargets.map((item) => `<tr><td><code>${escapeHtml(item.selector)}</code></td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const eventHtml = readiness.eventTypes.map((eventType) => `<span class="pill warn">${escapeHtml(eventType)}</span>`).join(" ");
    const actionHtml = readiness.delegatedActions.map((action) => `<span class="pill ${readiness.staticActions.includes(action) ? "good" : "warn"}">${escapeHtml(action)}</span>`).join(" ");
    const bootHtml = readiness.bootOrder.map((step) => `<span class="pill warn">${escapeHtml(step)}</span>`).join(" ");
    const boundaryHtml = readiness.splitBoundary.map((item) => `<span class="pill warn">${escapeHtml(item)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "bootstrap/bindEvents 계약 고정 완료" : "bootstrap/bindEvents 계약 확인 필요",
          subtitle: `${readiness.currentFile}를 thin entry로 유지하면서 boot 순서와 delegated action map을 고정했습니다.`,
          metrics: [
            { label: "내부 함수", value: readiness.internalFunctionCount, tone: readiness.missingInternalFunctions.length ? "blocked" : "good" },
            { label: "window export", value: readiness.windowExportCount, tone: readiness.missingWindowExports.length ? "blocked" : "good" },
            { label: "DOM target", value: readiness.domTargetCount, tone: readiness.missingDomTargets.length ? "blocked" : "good" },
            { label: "event type", value: readiness.eventTypeCount, tone: "warn" },
            { label: "delegated action", value: readiness.delegatedActionCount, tone: readiness.unknownStaticActions.length ? "blocked" : "good" },
            { label: "boot step", value: readiness.bootStepCount, tone: "warn" },
          ],
        })}
        <div class="draft-preview-summary">${eventHtml}</div>
        <div class="draft-preview-summary">${bootHtml}</div>
        <div class="draft-preview-summary">${boundaryHtml}</div>
        <div class="filter-help">버튼 action은 아래 map에 등록된 값만 entry에서 처리합니다. 초록색은 현재 HTML에 정적 버튼으로 존재하는 action이고, 노란색은 상세/동적 렌더 후 생기는 action입니다.</div>
        <div class="draft-preview-summary">${actionHtml}</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>internal function</th><th>상태</th></tr></thead><tbody>${functionRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>window export</th><th>상태</th></tr></thead><tbody>${exportRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>DOM target</th><th>상태</th></tr></thead><tbody>${domRows}</tbody></table></div>
        </div>
      </div>
    `;
  }

  function getAdminBackendServiceSplitContractReadiness() {
    const contract = ADMIN_BACKEND_SERVICE_SPLIT_CONTRACT;
    const extractedFiles = (contract.extractedFiles || []).map((path) => ({ path, extracted: true }));
    const nextFiles = contract.nextFiles.map((path) => ({ path, planned: true }));
    const splitGroups = contract.splitGroups.map((group) => ({ ...group, ok: !!group.key }));
    const routeContract = contract.routeContract.map((item) => ({ value: item, ok: !!item }));
    const overviewSnapshotsExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_overview_snapshots_service.py");
    const masterCatalogExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_master_catalog_service.py");
    const createLifecycleExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_create_lifecycle_service.py");
    const changeLogsExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_change_log_service.py");
    const editDraftExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_edit_draft_service.py");
    const sharedUtilsExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_shared_utils.py");
    const configExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_config.py");
    const readinessExtractedReady = extractedFiles.some((item) => item.path === "backend/app/services/admin/admin_readiness_service.py");
    const routeResponseHelperReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_response_helpers.py");
    const routeParamsReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_route_params.py");
    const routeErrorHelperReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_route_error_helpers.py");
    const routeResponseDataHelperReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_response_data_helpers.py");
    const routeResponseMetaHelperReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_response_meta_helpers.py");
    const routeMasterDataModuleReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_master_data_routes.py");
    const routeChangeLogModuleReady = extractedFiles.some((item) => item.path === "backend/app/api/routes/admin_change_log_routes.py");
    const routeModuleSplitReady = routeMasterDataModuleReady && routeChangeLogModuleReady;
    const ok = contract.status === "contract-frozen-v198"
      && contract.splitStatus === "admin-route-module-split-v214"
      && overviewSnapshotsExtractedReady
      && masterCatalogExtractedReady
      && createLifecycleExtractedReady
      && changeLogsExtractedReady
      && editDraftExtractedReady
      && sharedUtilsExtractedReady
      && configExtractedReady
      && readinessExtractedReady
      && routeResponseHelperReady
      && routeParamsReady
      && routeErrorHelperReady
      && routeResponseDataHelperReady
      && routeResponseMetaHelperReady
      && routeMasterDataModuleReady
      && routeChangeLogModuleReady
      && nextFiles.length === 0
      && splitGroups.length >= 8
      && routeContract.every((item) => item.ok)
      && !!contract.smoke;
    return {
      ok,
      contract,
      status: contract.status,
      currentFile: contract.currentFile,
      facadeFile: contract.facadeFile,
      routeFile: contract.routeFile,
      schemaFile: contract.schemaFile,
      splitStatus: contract.splitStatus,
      extractedFiles,
      nextFiles,
      overviewSnapshotsExtractedReady,
      masterCatalogExtractedReady,
      createLifecycleExtractedReady,
      changeLogsExtractedReady,
      editDraftExtractedReady,
      sharedUtilsExtractedReady,
      configExtractedReady,
      readinessExtractedReady,
      routeResponseHelperReady,
      routeParamsReady,
      routeErrorHelperReady,
      routeResponseDataHelperReady,
      routeResponseMetaHelperReady,
      routeMasterDataModuleReady,
      routeChangeLogModuleReady,
      routeModuleSplitReady,
      splitGroups,
      routeContract,
      smoke: contract.smoke,
      extractedFileCount: extractedFiles.length,
      nextFileCount: nextFiles.length,
      splitGroupCount: splitGroups.length,
      publicMethodCount: splitGroups.reduce((sum, group) => sum + Number(group.publicMethodCount || 0), 0),
      routeContractCount: routeContract.length,
    };
  }

  function renderAdminBackendServiceSplitContractReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminBackendServiceSplitContractReadiness();
    const extractedRows = readiness.extractedFiles.map((item, index) => `<tr><td>${escapeHtml(String(index + 1))}</td><td><code>${escapeHtml(item.path)}</code></td><td><span class="pill good">extracted</span></td></tr>`).join("");
    const fileRows = readiness.nextFiles.map((item, index) => `<tr><td>${escapeHtml(String(index + 1))}</td><td><code>${escapeHtml(item.path)}</code></td><td><span class="pill warn">planned</span></td></tr>`).join("");
    const groupRows = readiness.splitGroups.map((group) => `<tr><td>${escapeHtml(group.key)}</td><td>${escapeHtml(group.note)}</td><td>${escapeHtml(String(group.publicMethodCount))}</td></tr>`).join("");
    const routeHtml = readiness.routeContract.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.value)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "백엔드 admin route helper 정리 완료" : "백엔드 admin route helper 확인 필요",
          subtitle: `${readiness.routeFile}의 응답/파라미터/예외 fallback helper를 분리했습니다.`,
          metrics: [
            { label: "분리 묶음", value: readiness.splitGroupCount, tone: readiness.splitGroupCount ? "good" : "blocked" },
            { label: "분리 완료 파일", value: readiness.extractedFileCount, tone: readiness.overviewSnapshotsExtractedReady ? "good" : "blocked" },
            { label: "남은 후보 파일", value: readiness.nextFileCount, tone: readiness.nextFileCount ? "warn" : "good" },
            { label: "public method", value: readiness.publicMethodCount, tone: readiness.publicMethodCount ? "good" : "blocked" },
            { label: "route 계약", value: readiness.routeContractCount, tone: readiness.routeContractCount ? "good" : "blocked" },
          ],
        })}
        <div class="draft-preview-summary">${routeHtml}</div>
        <div class="filter-help">검증 smoke: <code>${escapeHtml(readiness.smoke)}</code> + <code>tools/run_smoke_core.sh</code>. v214는 route/schema/path를 그대로 두고 master-data/change-log route 모듈만 분리합니다.</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>#</th><th>분리/후보 파일</th><th>상태</th></tr></thead><tbody>${extractedRows}${fileRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>묶음</th><th>역할</th><th>public method</th></tr></thead><tbody>${groupRows}</tbody></table></div>
        </div>
      </div>
    `;
  }

  function getAdminJsSplitReadiness() {
    const scriptSources = Array.from(document.querySelectorAll("script[src]")).map((script) => script.getAttribute("src") || "");
    const gameApiIndex = scriptSources.findIndex((src) => src.includes("game-api-client.js"));
    const layoutShellIndex = scriptSources.findIndex((src) => src.includes("admin-layout-shell.js"));
    const adminPageIndex = scriptSources.findIndex((src) => src.includes("admin-page-readonly.js"));
    const changeLogsIndex = scriptSources.findIndex((src) => src.includes("admin/admin-change-logs.js"));
    const createLifecycleIndex = scriptSources.findIndex((src) => src.includes("admin/admin-create-lifecycle.js"));
    const editDraftIndex = scriptSources.findIndex((src) => src.includes("admin/admin-edit-draft.js"));
    const masterCatalogIndex = scriptSources.findIndex((src) => src.includes("admin/admin-master-catalog.js"));
    const overviewSnapshotsIndex = scriptSources.findIndex((src) => src.includes("admin/admin-overview-snapshots.js"));
    const fieldHelpIndex = scriptSources.findIndex((src) => src.includes("admin/admin-field-help.js"));
    const settingsHelpersIndex = scriptSources.findIndex((src) => src.includes("admin/admin-settings-helpers.js"));
    const requiredGlobals = ADMIN_JS_SPLIT_REQUIRED_GLOBALS.map((key) => ({
      key,
      ok: key === "RpgGameApi" ? !!window.RpgGameApi : typeof window[key] !== "undefined",
    }));
    const missingGlobals = requiredGlobals.filter((item) => !item.ok).map((item) => item.key);
    const exportCount = window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage === "object" ? Object.keys(window.RpgAdminReadOnlyPage).length : 0;
    const entryFileStillSingle = scriptSources.some((src) => src.includes("admin-page-readonly.js"));
    const scriptOrderReady = gameApiIndex >= 0 && layoutShellIndex >= 0 && fieldHelpIndex >= 0 && settingsHelpersIndex >= 0 && changeLogsIndex >= 0 && createLifecycleIndex >= 0 && editDraftIndex >= 0 && masterCatalogIndex >= 0 && overviewSnapshotsIndex >= 0 && adminPageIndex >= 0 && gameApiIndex < layoutShellIndex && layoutShellIndex < fieldHelpIndex && fieldHelpIndex < settingsHelpersIndex && settingsHelpersIndex < changeLogsIndex && changeLogsIndex < createLifecycleIndex && createLifecycleIndex < editDraftIndex && editDraftIndex < masterCatalogIndex && masterCatalogIndex < overviewSnapshotsIndex && overviewSnapshotsIndex < adminPageIndex;
    const candidateCount = ADMIN_JS_SPLIT_PHASES.filter((phase) => phase.status !== "keep-last").length;
    const bootstrapBinding = getAdminBootstrapBindingReadiness();
    const thinEntryCleanup = getAdminThinEntryCleanupReadiness();
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
      editDraftIndex,
      masterCatalogIndex,
      overviewSnapshotsIndex,
      fieldHelpIndex,
      settingsHelpersIndex,
      entryFileStillSingle,
      layoutShellExternalReady: layoutShellIndex >= 0 && !!window.RpgAdminLayoutShell,
      changeLogsExternalReady: changeLogsIndex >= 0 && !!window.RpgAdminChangeLogs,
      createLifecycleExternalReady: createLifecycleIndex >= 0 && !!window.RpgAdminCreateLifecycle,
      editDraftExternalReady: editDraftIndex >= 0 && !!window.RpgAdminEditDraft,
      masterCatalogExternalReady: masterCatalogIndex >= 0 && !!window.RpgAdminMasterCatalog,
      overviewSnapshotsExternalReady: overviewSnapshotsIndex >= 0 && !!window.RpgAdminOverviewSnapshots,
      fieldHelpExternalReady: fieldHelpIndex >= 0 && !!window.RpgAdminFieldHelp,
      settingsHelpersExternalReady: settingsHelpersIndex >= 0 && !!window.RpgAdminSettingsHelpers,
      candidateCount,
      phases: ADMIN_JS_SPLIT_PHASES.slice(),
      bootstrapBindingReady: !!(bootstrapBinding && bootstrapBinding.ok),
      bootstrapBinding,
      thinEntryCleanupReady: !!(thinEntryCleanup && thinEntryCleanup.ok),
      thinEntryCleanup,
      nextSafeStep: "admin-page-readonly.js thin entry 유지 + 설정 helper 이후 backend admin service 분리 준비",
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
      const tone = phase.status === "already-external" || phase.status === "extracted-v185" || phase.status === "extracted-v187" || phase.status === "contract-frozen-v186" || phase.status === "contract-frozen-v188" || phase.status === "contract-frozen-v190" || phase.status === "extracted-v193" || phase.status === "contract-frozen-v194" || phase.status === "cleaned-v195" ? "good" : (phase.status === "later" || phase.status === "keep-last" ? "warn" : "good");
      return `<tr><td>${escapeHtml(String(index + 1))}</td><td><strong>${escapeHtml(phase.label)}</strong><br><span class="muted">${escapeHtml(phase.key)}</span></td><td>${escapeHtml(phase.currentFile)}</td><td>${escapeHtml(phase.nextFile)}</td><td><span class="pill ${tone}">${escapeHtml(phase.status)}</span></td><td>${escapeHtml(phase.note)}</td></tr>`;
    }).join("");
    const changeLogContract = getAdminChangeLogSplitContractReadiness();
    const createLifecycleContract = getAdminCreateLifecycleSplitContractReadiness();
    const editDraftContract = getAdminEditDraftSplitContractReadiness();
    const bootstrapBindingContract = getAdminBootstrapBindingReadiness();
    const thinEntryCleanupContract = getAdminThinEntryCleanupReadiness();
    const backendServiceSplitContract = getAdminBackendServiceSplitContractReadiness();
    target.innerHTML = `
      ${renderAdminOperationResultBanner({
        tone: readiness.ok ? "good" : "warn",
        title: readiness.ok ? "관리자 JS 분리 상태 양호" : "관리자 JS 분리 확인 필요",
        subtitle: "layout shell부터 overview/snapshots까지 관리자 기능을 외부 JS 파일로 분리했습니다.",
        metrics: [
          { label: "script 순서", value: readiness.scriptOrderReady, tone: readiness.scriptOrderReady ? "good" : "blocked" },
          { label: "layout shell 파일", value: readiness.layoutShellExternalReady, tone: readiness.layoutShellExternalReady ? "good" : "blocked" },
          { label: "overview 파일", value: readiness.overviewSnapshotsExternalReady, tone: readiness.overviewSnapshotsExternalReady ? "good" : "blocked" },
          { label: "필수 global 누락", value: readiness.missingGlobals.length, tone: readiness.missingGlobals.length ? "blocked" : "good" },
          { label: "admin export", value: readiness.exportCount, tone: readiness.exportCount ? "good" : "blocked" },
          { label: "분리 후보", value: readiness.candidateCount, tone: "warn" },
          { label: "entry 계약", value: readiness.bootstrapBindingReady, tone: readiness.bootstrapBindingReady ? "good" : "blocked" },
          { label: "thin entry", value: readiness.thinEntryCleanupReady, tone: readiness.thinEntryCleanupReady ? "good" : "blocked" },
          { label: "backend 계약", value: readiness.backendServiceSplitContractReady, tone: readiness.backendServiceSplitContractReady ? "good" : "blocked" },
        ],
      })}
      <div class="draft-preview-summary">${globalsHtml}</div>
      <div class="filter-help">다음 안전 단계: ${escapeHtml(readiness.nextSafeStep)}. layout shell, change logs, create lifecycle, edit draft, master catalog/detail, overview/snapshots는 분리 완료 상태입니다.</div>
      <div class="table-wrap relation-table-wrap"><table><thead><tr><th>#</th><th>묶음</th><th>현재 파일</th><th>분리 후보 파일</th><th>상태</th><th>메모</th></tr></thead><tbody>${rows}</tbody></table></div>
      ${renderAdminChangeLogSplitContractReadiness(changeLogContract)}
      ${renderAdminCreateLifecycleSplitContractReadiness(createLifecycleContract)}
      ${renderAdminEditDraftSplitContractReadiness(editDraftContract)}
      ${renderAdminBootstrapBindingReadiness(bootstrapBindingContract)}
      ${renderAdminThinEntryCleanupReadiness(thinEntryCleanupContract)}
      ${renderAdminBackendServiceSplitContractReadiness(backendServiceSplitContract)}
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
    function makeAdminDetailFieldMap(...args) {
    return getAdminMasterCatalogApi().makeAdminDetailFieldMap(...args);
  }

function valuesEqualForApiVerify(...args) {
    return getAdminMasterCatalogApi().valuesEqualForApiVerify(...args);
  }

function findMasterApiRow(...args) {
    return getAdminMasterCatalogApi().findMasterApiRow(...args);
  }

function buildMasterApiVerifyComparisons(...args) {
    return getAdminMasterCatalogApi().buildMasterApiVerifyComparisons(...args);
  }

function renderMasterApiVerifyResult(...args) {
    return getAdminMasterCatalogApi().renderMasterApiVerifyResult(...args);
  }

async function verifySelectedMasterDataApi(...args) {
    return await getAdminMasterCatalogApi().verifySelectedMasterDataApi(...args);
  }

async function runPostWriteMasterApiVerification(...args) {
    return await getAdminMasterCatalogApi().runPostWriteMasterApiVerification(...args);
  }

function renderMasterDetail(...args) {
    return getAdminMasterCatalogApi().renderMasterDetail(...args);
  }

function renderMasterRelations(...args) {
    return getAdminMasterCatalogApi().renderMasterRelations(...args);
  }

async function openAdminMasterDataRelations(...args) {
    return await getAdminMasterCatalogApi().openAdminMasterDataRelations(...args);
  }

async function openAdminMasterDataDetailByCode(...args) {
    return await getAdminMasterCatalogApi().openAdminMasterDataDetailByCode(...args);
  }

async function openAdminMasterDataDetail(...args) {
    return await getAdminMasterCatalogApi().openAdminMasterDataDetail(...args);
  }

  function renderSnapshotTable(...args) {
    return getAdminOverviewSnapshotsApi().renderAdminSnapshotTable(...args);
  }

    async function refreshAdminMasterCatalog(...args) {
    return await getAdminMasterCatalogApi().refreshAdminMasterCatalog(...args);
  }

  function renderReadiness(...args) {
    return getAdminOverviewSnapshotsApi().renderAdminReadiness(...args);
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

  function saveApiBaseUrlFromInput(...args) {
    return getAdminSettingsHelpersApi().saveApiBaseUrlFromInput(...args);
  }

  function resetApiBaseUrl(...args) {
    return getAdminSettingsHelpersApi().resetApiBaseUrl(...args);
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

  function isExpectedAdminWriteGuardError(error) {
    const message = String((error && error.message) || "");
    return message.includes("확인 문구") || message.includes("dev key");
  }

  function getSharedRefreshFilters(extra) {
    return Object.assign({
      snapshotFilters: readSnapshotFiltersFromDom(),
      masterCatalogFilters: readMasterCatalogFiltersFromDom(),
      changeLogFilters: readChangeLogFiltersFromDom(),
    }, extra || {});
  }

  function getAdminClickActionHandlers() {
    return {
      "refresh": async () => refreshAdminReadOnlyPage(),
      "apply-snapshot-filters": async () => refreshAdminReadOnlyPage(getSharedRefreshFilters()),
      "apply-master-catalog-filters": async () => refreshAdminReadOnlyPage(getSharedRefreshFilters({ createBlueprintFilters: readAdminCreateBlueprintFiltersFromDom() })),
      "load-create-blueprint": async () => {
        try {
          await refreshAdminCreateBlueprint(readAdminCreateBlueprintFiltersFromDom());
        } catch (error) {
          renderError(error);
        }
      },
      "sync-create-domain-from-catalog": async () => {
        try {
          const filters = syncAdminCreateDomainFromCatalog();
          await refreshAdminCreateBlueprint(filters);
        } catch (error) {
          renderError(error);
        }
      },
      "preview-admin-create-draft": async () => {
        try {
          await previewAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      },
      "reset-admin-create-draft": () => resetAdminCreateDraft(),
      "apply-admin-create-draft": async () => {
        try {
          await applyAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      },
      "run-create-lifecycle-batch-check": async () => {
        try {
          await runAdminCreateLifecycleBatchCheck();
        } catch (error) {
          if (!isExpectedAdminWriteGuardError(error)) renderError(error);
        }
      },
      "master-catalog-first-page": async () => refreshMasterCatalogWithPage(1),
      "master-catalog-prev-page": async () => {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(Math.max(1, current - 1));
      },
      "master-catalog-next-page": async () => {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(current + 1);
      },
      "master-catalog-last-page": async (button) => {
        const totalPages = Number(button.getAttribute("data-admin-master-total-pages")) || 1;
        await refreshMasterCatalogWithPage(totalPages);
      },
      "apply-change-log-filters": async () => refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() }),
      "set-change-log-action-filter": async (button) => {
        try {
          await applyAdminChangeLogActionShortcut(button.getAttribute("data-admin-change-log-action-shortcut"));
        } catch (error) {
          renderError(error);
        }
      },
      "open-master-detail": async (button) => {
        const domain = button.getAttribute("data-admin-detail-domain");
        const id = button.getAttribute("data-admin-detail-id");
        try {
          await openAdminMasterDataDetail(domain, id);
        } catch (error) {
          renderError(error);
        }
      },
      "open-master-detail-by-code": async (button) => {
        const domain = button.getAttribute("data-admin-detail-domain");
        const code = button.getAttribute("data-admin-detail-code");
        try {
          await openAdminMasterDataDetailByCode(domain, code);
        } catch (error) {
          renderError(error);
        }
      },
      "open-master-relations": async (button) => {
        const domain = button.getAttribute("data-admin-relation-domain");
        const id = button.getAttribute("data-admin-relation-id");
        try {
          await openAdminMasterDataRelations(domain, id);
        } catch (error) {
          renderError(error);
        }
      },
      "preview-admin-edit-draft": async () => {
        try {
          await previewAdminEditDraft();
        } catch (error) {
          renderError(error);
        }
      },
      "apply-admin-edit-draft": async () => {
        try {
          await applyAdminEditDraft();
        } catch (error) {
          if (!isExpectedAdminWriteGuardError(error)) renderError(error);
        }
      },
      "refresh-admin-change-logs": async () => {
        try {
          await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
        } catch (error) {
          renderError(error);
        }
      },
      "open-admin-change-log-detail": async (button) => {
        try {
          await openAdminChangeLogDetail(button.getAttribute("data-admin-change-log-id"));
        } catch (error) {
          renderError(error);
        }
      },
      "preview-admin-change-log-rollback": async () => {
        try {
          await previewAdminChangeLogRollback();
        } catch (error) {
          renderError(error);
        }
      },
      "apply-admin-change-log-rollback": async () => {
        try {
          await applyAdminChangeLogRollback();
        } catch (error) {
          if (!isExpectedAdminWriteGuardError(error)) renderError(error);
        }
      },
      "preview-admin-create-delete": async () => {
        try {
          await previewAdminCreateDeleteRollback();
        } catch (error) {
          renderError(error);
        }
      },
      "apply-admin-create-delete": async () => {
        try {
          await applyAdminCreateDeleteRollback();
        } catch (error) {
          if (!isExpectedAdminWriteGuardError(error)) renderError(error);
        }
      },
      "preview-admin-create-delete-restore": async () => {
        try {
          await previewAdminCreateDeleteRestore();
        } catch (error) {
          renderError(error);
        }
      },
      "apply-admin-create-delete-restore": async () => {
        try {
          await applyAdminCreateDeleteRestore();
        } catch (error) {
          if (!isExpectedAdminWriteGuardError(error)) renderError(error);
        }
      },
      "verify-master-api-target": async () => {
        try {
          await verifySelectedMasterDataApi();
        } catch (error) {
          renderError(error);
        }
      },
      "reset-admin-edit-draft": () => resetAdminEditDraft(),
      "reset-master-catalog-filters": async () => {
        resetMasterCatalogFilters();
        await refreshAdminReadOnlyPage(getSharedRefreshFilters());
      },
      "reset-snapshot-filters": async () => {
        resetSnapshotFilters();
        await refreshAdminReadOnlyPage(getSharedRefreshFilters());
      },
      "reset-change-log-filters": async () => {
        resetChangeLogFilters();
        await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      },
      "save-admin-write-dev-key": () => {
        try {
          saveAdminWriteDevKeyFromInput();
        } catch (error) {
          renderAdminWriteKeyStatus();
        }
      },
      "clear-admin-write-dev-key": () => clearAdminWriteDevKey(),
      "save-api-base-url": async () => {
        try {
          saveApiBaseUrlFromInput();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      },
      "reset-api-base-url": async () => {
        try {
          resetApiBaseUrl();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      },
      "copy-admin-url": async () => copyCurrentAdminPageUrl(),
    };
  }

  async function handleAdminClickAction(button, action) {
    const handlers = getAdminClickActionHandlers();
    const handler = handlers[action];
    if (typeof handler !== "function") return false;
    await handler(button);
    return true;
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
        await refreshAdminReadOnlyPage(getSharedRefreshFilters());
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
      await handleAdminClickAction(button, button.getAttribute("data-admin-action"));
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
    const masterCatalogExternal = typeof getAdminMasterCatalogExternalReadiness === "function" ? getAdminMasterCatalogExternalReadiness() : { ok: false };
    const masterCatalogExternalReady = !!(masterCatalogExternal && masterCatalogExternal.ok && masterCatalogExternal.version === "v192.admin-master-catalog-detail-split");
    const overviewSnapshotsExternal = typeof getAdminOverviewSnapshotsExternalReadiness === "function" ? getAdminOverviewSnapshotsExternalReadiness() : { ok: false };
    const overviewSnapshotsExternalReady = !!(overviewSnapshotsExternal && overviewSnapshotsExternal.ok && overviewSnapshotsExternal.version === "v193.admin-overview-snapshots-split");
    const fieldHelpExternal = typeof getAdminFieldHelpExternalReadiness === "function" ? getAdminFieldHelpExternalReadiness() : { ok: false };
    const fieldHelpExternalReady = !!(fieldHelpExternal && fieldHelpExternal.ok && fieldHelpExternal.version === "v196.admin-field-help-split");
    const settingsHelpersExternal = typeof getAdminSettingsHelpersExternalReadiness === "function" ? getAdminSettingsHelpersExternalReadiness() : { ok: false };
    const settingsHelpersExternalReady = !!(settingsHelpersExternal && settingsHelpersExternal.ok && settingsHelpersExternal.version === "v197.admin-settings-helpers-split");
    const bootstrapBinding = typeof getAdminBootstrapBindingReadiness === "function" ? getAdminBootstrapBindingReadiness() : { ok: false };
    const bootstrapBindingReady = !!(bootstrapBinding && bootstrapBinding.ok && bootstrapBinding.status === "contract-frozen-v194" && typeof renderAdminBootstrapBindingReadiness === "function");
    const thinEntryCleanup = typeof getAdminThinEntryCleanupReadiness === "function" ? getAdminThinEntryCleanupReadiness() : { ok: false };
    const thinEntryCleanupReady = !!(thinEntryCleanup && thinEntryCleanup.ok && thinEntryCleanup.status === "cleaned-v195" && typeof renderAdminThinEntryCleanupReadiness === "function");
    const backendServiceSplitContract = typeof getAdminBackendServiceSplitContractReadiness === "function" ? getAdminBackendServiceSplitContractReadiness() : { ok: false };
    const backendServiceSplitContractReady = !!(backendServiceSplitContract && backendServiceSplitContract.ok && backendServiceSplitContract.status === "contract-frozen-v198" && typeof renderAdminBackendServiceSplitContractReadiness === "function");
    const backendOverviewSnapshotsServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.overviewSnapshotsExtractedReady);
    const backendMasterCatalogServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.masterCatalogExtractedReady);
    const backendCreateLifecycleServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.createLifecycleExtractedReady);
    const backendChangeLogServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.changeLogsExtractedReady);
    const backendEditDraftServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.editDraftExtractedReady);
    const backendSharedUtilsServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.sharedUtilsExtractedReady);
    const backendConfigServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.configExtractedReady);
    const backendReadinessServiceSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.readinessExtractedReady);
    const backendRouteResponseHelperReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeResponseHelperReady);
    const backendRouteParamsReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeParamsReady);
    const backendRouteErrorHelperReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeErrorHelperReady);
    const backendRouteResponseDataHelperReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeResponseDataHelperReady);
    const backendRouteResponseMetaHelperReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeResponseMetaHelperReady);
    const backendRouteMasterDataModuleReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeMasterDataModuleReady);
    const backendRouteChangeLogModuleReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeChangeLogModuleReady);
    const backendRouteModuleSplitReady = !!(backendServiceSplitContractReady && backendServiceSplitContract.routeModuleSplitReady);
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
    const result = { ok: apiReady && domReady && snapshotFilterReady && masterCatalogReady && masterDetailReady && adminChangeLogFilterReady && createLifecycleGuideReady && createLifecycleResultSummaryReady && adminJsSplitReadinessReady && changeLogSplitContractReady && createLifecycleSplitContractReady && editDraftSplitContractReady && editDraftExternalReady && createLifecycleExternalReady && masterCatalogExternalReady && overviewSnapshotsExternalReady && fieldHelpExternalReady && settingsHelpersExternalReady && bootstrapBindingReady && thinEntryCleanupReady && backendServiceSplitContractReady && backendOverviewSnapshotsServiceSplitReady && backendMasterCatalogServiceSplitReady && backendCreateLifecycleServiceSplitReady && backendChangeLogServiceSplitReady && backendEditDraftServiceSplitReady && backendSharedUtilsServiceSplitReady && backendConfigServiceSplitReady && backendReadinessServiceSplitReady && backendRouteResponseHelperReady && backendRouteParamsReady && backendRouteErrorHelperReady && backendRouteResponseDataHelperReady && backendRouteResponseMetaHelperReady && backendRouteModuleSplitReady && masterApiVerifyReady && adminWriteGuardReady && layoutShell.ok, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, masterCatalogReady, masterDetailReady, masterRelationsReady, editDraftReady, fieldHelpReady, fieldHelpExternalReady, fieldHelpExternal, settingsHelpersExternalReady, settingsHelpersExternal, adminChangeLogReady, adminChangeLogDetailReady, adminChangeLogFilterReady, masterApiVerifyReady, postWriteApiVerifyReady, adminWriteGuardReady, relationSearchReady, relationPreviewReady, changeLogRelationReady, createBlueprintReady, createLifecycleGuideReady, createLifecycleDependencyGuideReady, createLifecycleResultSummaryReady, createLifecycleBatchCheckReady, adminJsSplitReadinessReady, adminJsSplitReadiness, changeLogSplitContractReady, changeLogSplitContract, createLifecycleSplitContractReady, createLifecycleSplitContract, editDraftSplitContractReady, editDraftSplitContract, editDraftExternalReady, editDraftExternal, masterCatalogExternalReady, masterCatalogExternal, overviewSnapshotsExternalReady, overviewSnapshotsExternal, bootstrapBindingReady, bootstrapBinding, thinEntryCleanupReady, thinEntryCleanup, backendServiceSplitContractReady, backendOverviewSnapshotsServiceSplitReady, backendMasterCatalogServiceSplitReady, backendCreateLifecycleServiceSplitReady, backendChangeLogServiceSplitReady, backendEditDraftServiceSplitReady, backendSharedUtilsServiceSplitReady, backendConfigServiceSplitReady, backendReadinessServiceSplitReady, backendRouteResponseHelperReady, backendRouteParamsReady, backendRouteErrorHelperReady, backendRouteResponseDataHelperReady, backendRouteResponseMetaHelperReady, backendRouteMasterDataModuleReady, backendRouteChangeLogModuleReady, backendRouteModuleSplitReady, backendServiceSplitContract, changeLogsExternalReady, changeLogs, createLifecycleExternalReady, createLifecycle, createDraftPreviewReady, createApplyReady, createDeleteRollbackReady, createDeleteRestoreReady, layoutShellReady: layoutShell.ok, layoutShell, createBlueprint: getAdminCreateBlueprintReadiness(), createLifecycleGuide: getAdminCreateLifecycleGuideReadiness(), adminWriteDevKeySet: hasAdminWriteDevKey(), readOnly: false, writeLocked: !hasAdminWriteDevKey(), guardedApply: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom(), editDraft: getAdminEditDraftReadiness({ log: false }) };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin read-only page check", result);
    return result;
  }

  function registerAdminReadOnlyPageExports() {
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
      getAdminOverviewSnapshotsExternalReadiness,
      getAdminFieldHelpExternalReadiness,
      getAdminSettingsHelpersExternalReadiness,
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
      getAdminBootstrapBindingReadiness,
      renderAdminBootstrapBindingReadiness,
      getAdminThinEntryCleanupReadiness,
      renderAdminThinEntryCleanupReadiness,
      getAdminBackendServiceSplitContractReadiness,
      renderAdminBackendServiceSplitContractReadiness,
      getAdminFieldHelpExternalReadiness,
      getAdminClickActionHandlers,
      handleAdminClickAction,
      registerAdminReadOnlyPageExports,
      configureAdminExternalModules,
      getAdminChangeLogsReadiness,
      getAdminCreateLifecycleReadiness,
      getAdminEditDraftExternalReadiness,
      getAdminMasterCatalogExternalReadiness,
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
      renderAdminWriteKeyStatus,
      getAdminSettingsHelpersExternalReadiness,
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
    window.getAdminOverviewSnapshotsExternalReadiness = getAdminOverviewSnapshotsExternalReadiness;
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
    window.getAdminBootstrapBindingReadiness = getAdminBootstrapBindingReadiness;
    window.renderAdminBootstrapBindingReadiness = renderAdminBootstrapBindingReadiness;
    window.getAdminThinEntryCleanupReadiness = getAdminThinEntryCleanupReadiness;
    window.renderAdminThinEntryCleanupReadiness = renderAdminThinEntryCleanupReadiness;
    window.getAdminBackendServiceSplitContractReadiness = getAdminBackendServiceSplitContractReadiness;
    window.renderAdminBackendServiceSplitContractReadiness = renderAdminBackendServiceSplitContractReadiness;
    window.getAdminClickActionHandlers = getAdminClickActionHandlers;
    window.handleAdminClickAction = handleAdminClickAction;
    window.registerAdminReadOnlyPageExports = registerAdminReadOnlyPageExports;
    window.configureAdminExternalModules = configureAdminExternalModules;
    window.getAdminChangeLogsReadiness = getAdminChangeLogsReadiness;
    window.getAdminCreateLifecycleReadiness = getAdminCreateLifecycleReadiness;
    window.getAdminEditDraftExternalReadiness = getAdminEditDraftExternalReadiness;
    window.getAdminMasterCatalogExternalReadiness = getAdminMasterCatalogExternalReadiness;
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
    window.renderAdminWriteKeyStatus = renderAdminWriteKeyStatus;
    window.getAdminSettingsHelpersExternalReadiness = getAdminSettingsHelpersExternalReadiness;
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

  }

  function configureAdminExternalModules() {
    configureAdminFieldHelp();
    configureAdminSettingsHelpers();
    configureAdminOverviewSnapshots();
    configureAdminMasterCatalog();
    configureAdminEditDraft();
    configureAdminCreateLifecycle();
    configureAdminChangeLogs();
  }

  registerAdminReadOnlyPageExports();
  configureAdminExternalModules();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
