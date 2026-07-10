(function () {
  "use strict";

  const VERSION = "v189.1.admin-create-lifecycle-split-hotfix";
  const LEGACY_SMOKE_VERSION_MARKERS = "v189.admin-create-lifecycle-split v188.admin-create-lifecycle-split-contract v187.admin-change-logs-split v183.admin-create-lifecycle-batch-check";

  let configured = false;
  let currentAdminCreateBlueprintPayload = null;

  let DEFAULT_MASTER_DOMAIN = "itemTemplates";
  let DEFAULT_TIMEOUT_MS = 3500;
  let ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  let ADMIN_CREATE_APPLY_CONFIRM_TEXT = "CREATE MASTER DATA ROW";
  let ADMIN_CREATE_DELETE_CONFIRM_TEXT = "DELETE CREATED MASTER DATA ROW";
  let ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = "RESTORE DELETED CREATED ROW";
  let ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT = "RUN CREATE DELETE RESTORE CHECK";
  let ADMIN_CHANGE_LOG_ACTION_FILTERS = ["update", "rollback", "create", "create_delete", "create_delete_restore"];
  let ADMIN_DRAFT_SELECT_FIELD_OPTIONS = {};
  let ADMIN_DRAFT_TEXTAREA_FIELDS = new Set();

  const ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT = {
    key: "create-lifecycle",
    label: "Create lifecycle",
    status: "extracted-v189",
    currentFile: "src/api/admin/admin-create-lifecycle.js",
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

  let $ = (selector) => document.querySelector(selector);
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let formatValue = (value) => (value === null || value === undefined || value === "" ? "-" : String(value));
  let formatValueWithFieldHint = (_key, value) => escapeHtml(formatValue(value));
  let renderFieldHelpBadge = () => "";
  let renderFieldHelpInline = () => "";
  let renderFieldValueHintInline = () => "";
  let renderAdminDraftTypeBadge = (type) => `<span class="pill">${escapeHtml(type || "text")}</span>`;
  let makeDraftOriginalValue = (value) => value === null || value === undefined ? "" : String(value);
  let parseDraftOriginalValue = (value) => value === null || value === undefined ? "" : String(value);
  let renderAdminDraftSelectOptionsHtml = (options, selectedValue) => {
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    const safeOptions = Array.isArray(options) ? options : [];
    return safeOptions.map((option) => {
      const optionValue = option && option.value !== undefined && option.value !== null ? String(option.value) : "";
      const optionLabel = option && option.label ? option.label : optionValue;
      return `<option value="${escapeHtml(optionValue)}" ${optionValue === selectedText ? "selected" : ""}>${escapeHtml(optionLabel)}</option>`;
    }).join("") || `<option value="${escapeHtml(selectedText)}" selected>${escapeHtml(selectedText || "선택지 없음")}</option>`;
  };
  let filterAdminDraftSelectOptions = (options, _query, selectedValue) => {
    const safeOptions = Array.isArray(options) ? options.slice() : [];
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    if (selectedText && !safeOptions.some((option) => String(option.value) === selectedText)) safeOptions.unshift({ value: selectedText, label: `${selectedText} · 현재 선택값` });
    return safeOptions;
  };
  let normalizeAdminDraftFieldKey = (key) => String(key || "").trim().toLowerCase();
  let normalizeAdminRelationSearchText = (value) => String(value === null || value === undefined ? "" : value).trim().toLowerCase();
  let getAdminEquipSlotDisplayName = (value) => String(value || "");
  let formatAdminRelationInfoText = (_relation, value) => formatValue(value);
  let renderAdminRelationOpenTargetButton = () => "";
  let ensureApi = () => {
    if (!window.RpgGameApi) throw new Error("RpgGameApi is not loaded");
    return window.RpgGameApi;
  };
  let setStatus = () => undefined;
  let requireAdminWriteDevKeyForUi = () => true;
  let refreshAdminChangeLogs = async () => ({ ok: true });
  let readChangeLogFiltersFromDom = () => ({});
  let refreshAdminReadOnlyPage = async () => ({ ok: true });
  let readSnapshotFiltersFromDom = () => ({});
  let readMasterCatalogFiltersFromDom = () => ({});
  let runPostWriteMasterApiVerification = async () => ({ ok: true });

  function readAdminCreateBlueprintFiltersFromDom() {
    const domainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    return {
      domain: domainEl && domainEl.value ? domainEl.value : (masterDomainEl && masterDomainEl.value ? masterDomainEl.value : DEFAULT_MASTER_DOMAIN),
    };
  }

  function syncAdminCreateDomainFromCatalog() {
    const createDomainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    if (createDomainEl && masterDomainEl && masterDomainEl.value) createDomainEl.value = masterDomainEl.value;
    return readAdminCreateBlueprintFiltersFromDom();
  }

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    if (typeof d.formatValueWithFieldHint === "function") formatValueWithFieldHint = d.formatValueWithFieldHint;
    if (typeof d.renderFieldHelpBadge === "function") renderFieldHelpBadge = d.renderFieldHelpBadge;
    if (typeof d.renderFieldHelpInline === "function") renderFieldHelpInline = d.renderFieldHelpInline;
    if (typeof d.renderFieldValueHintInline === "function") renderFieldValueHintInline = d.renderFieldValueHintInline;
    if (typeof d.renderAdminDraftTypeBadge === "function") renderAdminDraftTypeBadge = d.renderAdminDraftTypeBadge;
    if (typeof d.makeDraftOriginalValue === "function") makeDraftOriginalValue = d.makeDraftOriginalValue;
    if (typeof d.parseDraftOriginalValue === "function") parseDraftOriginalValue = d.parseDraftOriginalValue;
    if (typeof d.renderAdminDraftSelectOptionsHtml === "function") renderAdminDraftSelectOptionsHtml = d.renderAdminDraftSelectOptionsHtml;
    if (typeof d.filterAdminDraftSelectOptions === "function") filterAdminDraftSelectOptions = d.filterAdminDraftSelectOptions;
    if (typeof d.normalizeAdminDraftFieldKey === "function") normalizeAdminDraftFieldKey = d.normalizeAdminDraftFieldKey;
    if (typeof d.normalizeAdminRelationSearchText === "function") normalizeAdminRelationSearchText = d.normalizeAdminRelationSearchText;
    if (typeof d.getAdminEquipSlotDisplayName === "function") getAdminEquipSlotDisplayName = d.getAdminEquipSlotDisplayName;
    if (typeof d.formatAdminRelationInfoText === "function") formatAdminRelationInfoText = d.formatAdminRelationInfoText;
    if (typeof d.renderAdminRelationOpenTargetButton === "function") renderAdminRelationOpenTargetButton = d.renderAdminRelationOpenTargetButton;
    if (typeof d.ensureApi === "function") ensureApi = d.ensureApi;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.requireAdminWriteDevKeyForUi === "function") requireAdminWriteDevKeyForUi = d.requireAdminWriteDevKeyForUi;
    if (typeof d.refreshAdminChangeLogs === "function") refreshAdminChangeLogs = d.refreshAdminChangeLogs;
    if (typeof d.readChangeLogFiltersFromDom === "function") readChangeLogFiltersFromDom = d.readChangeLogFiltersFromDom;
    if (typeof d.refreshAdminReadOnlyPage === "function") refreshAdminReadOnlyPage = d.refreshAdminReadOnlyPage;
    if (typeof d.readSnapshotFiltersFromDom === "function") readSnapshotFiltersFromDom = d.readSnapshotFiltersFromDom;
    if (typeof d.readMasterCatalogFiltersFromDom === "function") readMasterCatalogFiltersFromDom = d.readMasterCatalogFiltersFromDom;
    if (typeof d.runPostWriteMasterApiVerification === "function") runPostWriteMasterApiVerification = d.runPostWriteMasterApiVerification;
    DEFAULT_MASTER_DOMAIN = d.DEFAULT_MASTER_DOMAIN || DEFAULT_MASTER_DOMAIN;
    DEFAULT_TIMEOUT_MS = Number(d.DEFAULT_TIMEOUT_MS || DEFAULT_TIMEOUT_MS);
    ADMIN_EDIT_APPLY_TIMEOUT_MS = Number(d.ADMIN_EDIT_APPLY_TIMEOUT_MS || ADMIN_EDIT_APPLY_TIMEOUT_MS);
    ADMIN_CREATE_APPLY_CONFIRM_TEXT = d.ADMIN_CREATE_APPLY_CONFIRM_TEXT || ADMIN_CREATE_APPLY_CONFIRM_TEXT;
    ADMIN_CREATE_DELETE_CONFIRM_TEXT = d.ADMIN_CREATE_DELETE_CONFIRM_TEXT || ADMIN_CREATE_DELETE_CONFIRM_TEXT;
    ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = d.ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT || ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT;
    ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT = d.ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT || ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT;
    ADMIN_CHANGE_LOG_ACTION_FILTERS = Array.isArray(d.ADMIN_CHANGE_LOG_ACTION_FILTERS) ? d.ADMIN_CHANGE_LOG_ACTION_FILTERS.slice() : ADMIN_CHANGE_LOG_ACTION_FILTERS;
    ADMIN_DRAFT_SELECT_FIELD_OPTIONS = d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS && typeof d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS === "object" ? d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS : ADMIN_DRAFT_SELECT_FIELD_OPTIONS;
    ADMIN_DRAFT_TEXTAREA_FIELDS = d.ADMIN_DRAFT_TEXTAREA_FIELDS instanceof Set ? d.ADMIN_DRAFT_TEXTAREA_FIELDS : ADMIN_DRAFT_TEXTAREA_FIELDS;
    configured = true;
    return getReadiness();
  }

  function getReadiness() {
    const requiredFunctions = {
      querySelector: typeof $ === "function",
      escapeHtml: typeof escapeHtml === "function",
      formatValue: typeof formatValue === "function",
      formatValueWithFieldHint: typeof formatValueWithFieldHint === "function",
      renderFieldHelpBadge: typeof renderFieldHelpBadge === "function",
      renderAdminDraftSelectOptionsHtml: typeof renderAdminDraftSelectOptionsHtml === "function",
      filterAdminDraftSelectOptions: typeof filterAdminDraftSelectOptions === "function",
      ensureApi: typeof ensureApi === "function",
      setStatus: typeof setStatus === "function",
      requireAdminWriteDevKeyForUi: typeof requireAdminWriteDevKeyForUi === "function",
      refreshAdminChangeLogs: typeof refreshAdminChangeLogs === "function",
      refreshAdminReadOnlyPage: typeof refreshAdminReadOnlyPage === "function",
      runPostWriteMasterApiVerification: typeof runPostWriteMasterApiVerification === "function",
    };
    const missingFunctions = Object.keys(requiredFunctions).filter((key) => !requiredFunctions[key]);
    const apiMethods = ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.requiredApiMethods.slice();
    const missingApiMethods = apiMethods.filter((key) => !(window.RpgGameApi && typeof window.RpgGameApi[key] === "function"));
    const exportedFunctions = [
      "readAdminCreateBlueprintFiltersFromDom",
      "syncAdminCreateDomainFromCatalog",
      "getAdminCreateBlueprintFieldInputKind",
      "getAdminCreateBlueprintRequiredKeys",
      "getAdminCreateBlueprintDefaultDraft",
      "renderAdminCreateBlueprint",
      "refreshAdminCreateBlueprint",
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
      "renderAdminOperationResultBanner",
      "renderAdminCreateDeleteBlockerSummary",
      "getAdminCreateLifecycleGuideReadiness",
      "getAdminCreateLifecycleSplitContractReadiness",
      "renderAdminCreateLifecycleSplitContractReadiness",
    ];
    return {
      version: VERSION,
      legacyMarkers: LEGACY_SMOKE_VERSION_MARKERS,
      configured,
      ok: configured && missingFunctions.length === 0,
      apiReady: missingApiMethods.length === 0,
      requiredFunctions,
      missingFunctions,
      missingApiMethods,
      exportedFunctions,
      exportedFunctionCount: exportedFunctions.length,
      sourceFile: "src/api/admin/admin-create-lifecycle.js",
      contractStatus: ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.status,
    };
  }

  function getAdminCreateBlueprintFieldInputKind(field) {
    return String((field && field.inputKind) || "text");
  }

  function getAdminCreateBlueprintRequiredKeys(domain, blueprint) {
    const payload = blueprint || currentAdminCreateBlueprintPayload || {};
    if (domain && payload.domain && payload.domain !== domain) return [];
    return Array.isArray(payload.requiredFields) ? payload.requiredFields.slice() : [];
  }

  function getAdminCreateBlueprintDefaultDraft(domain, blueprint) {
    const payload = blueprint || currentAdminCreateBlueprintPayload || {};
    if (domain && payload.domain && payload.domain !== domain) return {};
    return payload.defaultDraft && typeof payload.defaultDraft === "object" ? { ...payload.defaultDraft } : {};
  }

  function getAdminCreateBlueprintRelationOptionCount(field) {
    const relation = field && field.relation ? field.relation : null;
    if (!relation) return 0;
    if (relation.optionGroups && typeof relation.optionGroups === "object") {
      return Object.values(relation.optionGroups).reduce((sum, options) => sum + (Array.isArray(options) ? options.length : 0), 0);
    }
    return Array.isArray(relation.options) ? relation.options.length : 0;
  }


  function renderUnifiedPreviewDiff(payload) {
    const diff = payload && Array.isArray(payload.unifiedDiff) ? payload.unifiedDiff : [];
    const snapshot = payload && payload.rollbackSnapshot ? payload.rollbackSnapshot : null;
    if (!diff.length && !snapshot) return "";
    const rows = diff.length ? diff.map((item) => `<tr><td>${escapeHtml(item.path || "$")}</td><td>${escapeHtml(item.op || "replace")}</td><td>${escapeHtml(formatValue(item.before))}</td><td>${escapeHtml(formatValue(item.after))}</td></tr>`).join("") : `<tr><td colspan="4">변경 없음</td></tr>`;
    return `<details class="json-detail" open><summary>공통 Diff <span class="pill good">${escapeHtml(formatValue(diff.length))}</span></summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>경로</th><th>작업</th><th>이전</th><th>이후</th></tr></thead><tbody>${rows}</tbody></table></div>${snapshot ? `<div class="filter-help">rollback snapshot: schema v${escapeHtml(formatValue(snapshot.schemaVersion))} · fingerprint ${escapeHtml(String(snapshot.fingerprint || "").slice(0, 12))}…</div>` : ""}</details>`;
  }
  function renderAdminCreateBlueprintRelationCell(field) {
    const relation = field && field.relation ? field.relation : null;
    if (!relation) return "-";
    const target = relation.targetLabel || relation.targetDomain || field.targetDomain || "relation";
    const count = getAdminCreateBlueprintRelationOptionCount(field);
    const guard = Array.isArray(field.comboGuard) && field.comboGuard.length ? ` · 중복검사 ${field.comboGuard.join(" + ")}` : "";
    const depends = field.dependsOn ? ` · ${field.dependsOn} 연동` : "";
    return `${escapeHtml(target)} <span class="pill warn">후보 ${escapeHtml(formatValue(count))}</span>${escapeHtml(depends + guard)}`;
  }

  function getAdminCreateFieldDefinition(key) {
    const payload = currentAdminCreateBlueprintPayload || {};
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const normalized = normalizeAdminDraftFieldKey(key);
    return fields.find((field) => normalizeAdminDraftFieldKey(field && field.key) === normalized) || null;
  }

  function getAdminCreateRelationDefinition(key) {
    const field = getAdminCreateFieldDefinition(key);
    return field && field.relation ? { ...field.relation, field: field.key, dependsOn: field.dependsOn || (field.relation && field.relation.dependsOn) } : null;
  }

  function getAdminCreateRelationOptionsForValues(definition, values) {
    if (!definition) return null;
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyKey = String(definition.dependsOn || "");
      const groupKey = values && Object.prototype.hasOwnProperty.call(values, dependencyKey) ? String(values[dependencyKey] || "").trim() : "";
      const grouped = definition.optionGroups[groupKey];
      if (Array.isArray(grouped)) return grouped.slice();
    }
    return Array.isArray(definition.options) ? definition.options.slice() : null;
  }

  function getAdminCreateDraftCurrentValues() {
    const draft = $(`[data-admin-create-draft]`);
    const values = {};
    if (!draft) return values;
    Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")).forEach((field) => {
      const key = field.getAttribute("data-admin-create-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      values[key] = type === "boolean" ? field.value === "true" : field.value;
    });
    return values;
  }

  function getAdminCreateDraftSelectOptions(field, value, values) {
    const key = field ? field.key : "";
    const normalized = normalizeAdminDraftFieldKey(key);
    const definition = getAdminCreateRelationDefinition(normalized);
    const relationOptions = getAdminCreateRelationOptionsForValues(definition, values || getAdminCreateDraftCurrentValues());
    const baseOptions = relationOptions ? relationOptions.slice() : (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[normalized] || []).slice();
    const valueText = value === null || value === undefined ? "" : String(value);
    if (valueText && !baseOptions.some((option) => String(option.value) === valueText)) {
      const currentLabel = normalized === "equip_slot" ? `${valueText} · ${getAdminEquipSlotDisplayName(valueText)} · 현재 초안 값` : `${valueText} · 현재 초안 값`;
      baseOptions.unshift({ value: valueText, label: currentLabel, current: true });
    }
    return baseOptions;
  }

  function getAdminCreateRelationSelectMetaText(key, query) {
    const definition = getAdminCreateRelationDefinition(key);
    if (!definition) return "";
    const allOptions = getAdminCreateRelationOptionsForValues(definition, getAdminCreateDraftCurrentValues()) || [];
    const filtered = filterAdminDraftSelectOptions(allOptions, query, "");
    const target = definition.targetLabel || definition.targetDomain || "관계 대상";
    const queryText = normalizeAdminRelationSearchText(query);
    return queryText ? `${target} ${filtered.length}/${allOptions.length}개 표시` : `${target} ${allOptions.length}개 중 선택`;
  }

  function updateAdminCreateRelationOptionMeta(meta, key, query) {
    if (!meta) return;
    const text = getAdminCreateRelationSelectMetaText(key, query);
    meta.textContent = text;
    meta.classList.toggle("warn", !!query && text.includes("0/"));
  }

  function renderAdminCreateDraftControl(field, values) {
    const key = field ? field.key : "";
    const kind = getAdminCreateBlueprintFieldInputKind(field);
    const value = values && Object.prototype.hasOwnProperty.call(values, key) ? values[key] : field.defaultValue;
    const valueText = value === null || value === undefined ? "" : String(value);
    const original = makeDraftOriginalValue(value);
    const commonAttrs = `data-admin-create-draft-field="${escapeHtml(key)}" data-admin-create-draft-original="${escapeHtml(original)}"`;
    if (kind === "boolean-select") {
      const normalized = value === true || String(value).toLowerCase() === "true" ? "true" : "false";
      return `
        <select ${commonAttrs} data-admin-create-draft-value-type="boolean" aria-label="${escapeHtml(field.label || key)} true false 선택">
          <option value="true" ${normalized === "true" ? "selected" : ""}>true · 켜짐</option>
          <option value="false" ${normalized === "false" ? "selected" : ""}>false · 꺼짐</option>
        </select>
      `;
    }
    if (kind === "preset-select") {
      const options = getAdminCreateDraftSelectOptions(field, value, values);
      return `
        <select ${commonAttrs} data-admin-create-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
          ${renderAdminDraftSelectOptionsHtml(options, valueText)}
        </select>
      `;
    }
    if (kind === "relation-select") {
      const options = getAdminCreateDraftSelectOptions(field, value, values);
      const definition = getAdminCreateRelationDefinition(key) || {};
      const metaText = getAdminCreateRelationSelectMetaText(key, "");
      return `
        <div class="relation-select-tools" data-admin-create-relation-select-tools>
          <input class="relation-option-filter" data-admin-create-relation-option-filter data-admin-create-relation-option-filter-for="${escapeHtml(key)}" type="text" placeholder="코드/이름으로 후보 검색" autocomplete="off" aria-label="${escapeHtml(field.label || key)} 후보 검색" />
          <select ${commonAttrs} data-admin-create-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
            ${renderAdminDraftSelectOptionsHtml(options, valueText)}
          </select>
          <div class="relation-option-meta" data-admin-create-relation-option-meta>${escapeHtml(metaText || (definition.targetLabel ? `${definition.targetLabel} 후보` : "관계 후보"))}</div>
        </div>
      `;
    }
    if (kind === "number") {
      return `<input type="number" inputmode="decimal" step="any" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-create-draft-value-type="number" />`;
    }
    if (kind === "textarea") {
      const rows = ADMIN_DRAFT_TEXTAREA_FIELDS.has(normalizeAdminDraftFieldKey(key)) ? 4 : 3;
      return `<textarea rows="${rows}" ${commonAttrs} data-admin-create-draft-value-type="text">${escapeHtml(valueText)}</textarea>`;
    }
    return `<input type="text" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-create-draft-value-type="text" />`;
  }

  function applyAdminCreateRelationOptionFilter(input) {
    if (!input) return false;
    const draft = input.closest("[data-admin-create-draft]");
    const wrapper = input.closest("[data-admin-create-relation-select-tools]");
    if (!draft || !wrapper) return false;
    const key = input.getAttribute("data-admin-create-relation-option-filter-for") || "";
    const field = getAdminCreateFieldDefinition(key);
    const select = wrapper.querySelector(`[data-admin-create-draft-field="${key}"]`);
    if (!field || !select) return false;
    const selectedValue = select.value;
    const options = getAdminCreateDraftSelectOptions(field, selectedValue, getAdminCreateDraftCurrentValues());
    const filtered = filterAdminDraftSelectOptions(options, input.value, selectedValue);
    select.innerHTML = renderAdminDraftSelectOptionsHtml(filtered, selectedValue);
    select.value = selectedValue;
    updateAdminCreateRelationOptionMeta(wrapper.querySelector("[data-admin-create-relation-option-meta]"), key, input.value);
    return true;
  }

  function refreshDependentAdminCreateRelationSelects(changedKey) {
    const draft = document.querySelector("[data-admin-create-draft]");
    if (!draft) return false;
    const changed = normalizeAdminDraftFieldKey(changedKey);
    let touched = false;
    const fields = Array.isArray(currentAdminCreateBlueprintPayload && currentAdminCreateBlueprintPayload.fields) ? currentAdminCreateBlueprintPayload.fields : [];
    fields.forEach((field) => {
      const definition = field && field.relation ? { ...field.relation, field: field.key, dependsOn: field.dependsOn || field.relation.dependsOn } : null;
      if (!definition || normalizeAdminDraftFieldKey(definition.dependsOn) !== changed) return;
      const target = draft.querySelector(`[data-admin-create-draft-field="${field.key}"]`);
      if (!target) return;
      const previousValue = target.value;
      const options = getAdminCreateRelationOptionsForValues(definition, getAdminCreateDraftCurrentValues()) || [];
      let nextValue = "";
      if (options.some((option) => String(option.value) === previousValue)) nextValue = previousValue;
      else if (options.length) nextValue = String(options[0].value ?? "");
      const wrapper = target.closest("[data-admin-create-relation-select-tools]");
      const filter = wrapper ? wrapper.querySelector("[data-admin-create-relation-option-filter]") : null;
      if (filter) filter.value = "";
      target.innerHTML = renderAdminDraftSelectOptionsHtml(options, nextValue);
      target.value = nextValue;
      updateAdminCreateRelationOptionMeta(wrapper && wrapper.querySelector("[data-admin-create-relation-option-meta]"), field.key, "");
      touched = true;
    });
    return touched;
  }

  function renderAdminCreateDraft(blueprintPayload) {
    const payload = blueprintPayload || currentAdminCreateBlueprintPayload || {};
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const defaultDraft = payload.defaultDraft && typeof payload.defaultDraft === "object" ? payload.defaultDraft : {};
    const editableFields = fields.filter((field) => field && field.futureEditable !== false && getAdminCreateBlueprintFieldInputKind(field) !== "json-readonly");
    if (!editableFields.length) return `<div class="empty">이 도메인은 아직 생성 초안 입력 필드가 없습니다.</div>`;
    const rows = editableFields.map((field) => `
      <label class="draft-field draft-field-${escapeHtml(getAdminCreateBlueprintFieldInputKind(field))}">
        <span class="draft-field-heading">
          <span>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</span>
          <span class="draft-field-badges">${renderAdminDraftTypeBadge(getAdminCreateBlueprintFieldInputKind(field))}${field.required ? ` <span class="pill blocked">필수</span>` : ` <span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</span>
        </span>
        ${renderFieldHelpInline(field.key)}
        ${renderFieldValueHintInline(field.key, field.defaultValue)}
        ${renderAdminCreateDraftControl(field, defaultDraft)}
      </label>
    `).join("");
    return `
      <div class="detail-card edit-draft-card create-draft-card" data-admin-create-draft data-admin-create-draft-domain="${escapeHtml(payload.domain || DEFAULT_MASTER_DOMAIN)}">
        <div class="detail-title">신규 row 생성 초안 <span class="pill warn">preview first</span><span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "limited insert open" : "insert locked"}</span></div>
        <div class="filter-help">아래 입력칸은 새 row를 만들 때 필요한 값을 미리 넣어보는 화면입니다. 먼저 <strong>생성 초안 검증</strong>으로 unique/relation/combo 검사를 통과해야 합니다. 실제 생성은 characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills만 dev key와 확인 문구로 제한 적용됩니다.</div>
        <div class="edit-draft-grid">${rows}</div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-draft">생성 초안 검증</button>
          <button class="btn mini" type="button" data-admin-action="reset-admin-create-draft">기본값으로 되돌리기</button>
          <label class="apply-confirm-field"><span>생성 사유</span><input type="text" data-admin-create-reason placeholder="예: 신규 강화 그룹 준비" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>생성 확인 문구</span><input type="text" data-admin-create-confirm placeholder="${escapeHtml(payload.confirmTextRequired || ADMIN_CREATE_APPLY_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-draft" ${payload.createApplyUnlocked ? "" : "disabled"}>실제 생성 적용</button>
          <span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "제한 insert 가능" : "DB insert 잠금"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-draft-result><div class="empty">값을 입력한 뒤 <strong>생성 초안 검증</strong>을 누르세요. 생성 적용 전에도 백엔드가 같은 검증을 다시 실행합니다.</div></div>
      </div>
    `;
  }

  function formatAdminCreateLifecyclePill(value, trueText, falseText) {
    return `<span class="pill ${value ? "good" : "blocked"}">${escapeHtml(value ? trueText : falseText)}</span>`;
  }

  function renderAdminCreateLifecycleDependencyGuards(lifecycle) {
    const guards = Array.isArray(lifecycle && lifecycle.deleteDependencyGuards) ? lifecycle.deleteDependencyGuards : [];
    if (!guards.length) {
      return `<div class="filter-help">삭제 차단 기준이 아직 정의되지 않은 도메인입니다. 삭제 preview에서 최종 안전검사를 확인합니다.</div>`;
    }
    const rows = guards.map((guard) => `
      <li>
        <span class="pill ${guard.blocksDelete ? "blocked" : "good"}">${guard.blocksDelete ? "차단 가능" : "leaf"}</span>
        <strong>${escapeHtml(guard.label || guard.target || "dependency")}</strong>
        <code>${escapeHtml(guard.target || "-")}</code>
        <span>${escapeHtml(guard.note || "삭제 preview에서 현재 count를 확인합니다.")}</span>
      </li>
    `).join("");
    return `<ul class="create-lifecycle-guard-list">${rows}</ul>`;
  }

  function renderAdminCreateLifecycleActionShortcuts() {
    return `
      <div class="create-lifecycle-actions">
        <button class="btn mini" type="button" data-admin-action="set-change-log-action-filter" data-admin-change-log-action-shortcut="create">create 이력 보기</button>
        <button class="btn mini" type="button" data-admin-action="set-change-log-action-filter" data-admin-change-log-action-shortcut="create_delete">create_delete 이력 보기</button>
        <button class="btn mini" type="button" data-admin-action="set-change-log-action-filter" data-admin-change-log-action-shortcut="create_delete_restore">restore 이력 보기</button>
      </div>
    `;
  }

  function readAdminCreateLifecycleBatchControls() {
    const confirmEl = $(`[data-admin-create-lifecycle-batch-confirm]`);
    const reasonEl = $(`[data-admin-create-lifecycle-batch-reason]`);
    return {
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT,
    };
  }

  function renderAdminCreateLifecycleBatchResult(steps, options) {
    const target = $(`[data-admin-create-lifecycle-batch-result]`);
    if (!target) return;
    const safeSteps = Array.isArray(steps) ? steps : [];
    const opts = options || {};
    const doneCount = safeSteps.filter((step) => step && step.status !== "pending").length;
    const failCount = safeSteps.filter((step) => step && step.ok === false).length;
    const rows = safeSteps.length ? safeSteps.map((step, index) => {
      const tone = step.status === "pending" ? "warn" : (step.ok ? "good" : "blocked");
      const payload = step.payload && typeof step.payload === "object" ? step.payload : {};
      const logText = payload.changeLogId || payload.deleteChangeLogId || payload.restoreChangeLogId || "-";
      const idText = payload.id || (payload.createdRow && payload.createdRow.id) || payload.targetId || "-";
      return `<tr><td>${escapeHtml(formatValue(index + 1))}</td><td>${escapeHtml(step.label || step.key || "step")}</td><td><span class="pill ${tone}">${escapeHtml(step.status || (step.ok ? "ok" : "blocked"))}</span></td><td>${escapeHtml(formatValue(idText))}</td><td>${escapeHtml(formatValue(logText))}</td><td>${escapeHtml(formatValue(step.message || payload.status || "-"))}</td></tr>`;
    }).join("") : `<tr><td colspan="6">아직 일괄 점검을 실행하지 않았습니다.</td></tr>`;
    target.innerHTML = `
      ${renderAdminOperationResultBanner({
        tone: failCount ? "blocked" : (opts.finished ? "good" : "warn"),
        title: opts.finished ? "생성→삭제→복원 일괄 점검 완료" : "생성→삭제→복원 일괄 점검 진행 상태",
        subtitle: opts.note || "현재 생성 초안을 기준으로 preview/apply 안전검사를 순서대로 실행합니다.",
        metrics: [
          { label: "완료 단계", value: doneCount, tone: doneCount ? "good" : "warn" },
          { label: "실패 단계", value: failCount, tone: failCount ? "blocked" : "good" },
          { label: "전체 단계", value: safeSteps.length, tone: "warn" },
        ],
      })}
      <div class="table-wrap relation-table-wrap"><table><thead><tr><th>#</th><th>단계</th><th>상태</th><th>row</th><th>log</th><th>메시지</th></tr></thead><tbody>${rows}</tbody></table></div>
      <div class="filter-help">일괄 점검은 성공 시 마지막에 row를 다시 복원합니다. 테스트 row는 DB에 남으므로, 필요 없으면 create 이력에서 다시 삭제할 수 있습니다.</div>
    `;
  }

  async function runAdminCreateLifecycleBatchCheck() {
    ensureApi();
    requireAdminWriteDevKeyForUi("생성→삭제→복원 일괄 점검");
    const values = readAdminCreateDraftValues();
    if (!values.ok) throw new Error("일괄 점검할 생성 초안이 없습니다. 먼저 생성 설계를 불러와 주세요.");
    if (values.confirmText !== ADMIN_CREATE_APPLY_CONFIRM_TEXT) {
      throw new Error(`생성 확인 문구를 먼저 입력해야 합니다: ${ADMIN_CREATE_APPLY_CONFIRM_TEXT}`);
    }
    const controls = readAdminCreateLifecycleBatchControls();
    if (!controls.confirmMatches) {
      throw new Error(`일괄 점검 확인 문구를 정확히 입력해야 합니다: ${ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT}`);
    }
    const confirmed = window.confirm("현재 생성 초안으로 DB에 row를 생성한 뒤 삭제하고 다시 복원하는 일괄 점검을 실행할까요? 성공하면 최종 row는 복원되어 DB에 남습니다.");
    if (!confirmed) {
      setStatus("생성→삭제→복원 일괄 점검을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }

    const reason = controls.reason || values.reason || `v183 create lifecycle batch check: ${values.domain}`;
    const timeoutMs = ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const steps = [];
    const renderBatchProgress = (note, finished) => renderAdminCreateLifecycleBatchResult(steps, { note, finished });
    const pushPending = (key, label) => {
      steps.push({ key, label, status: "pending", ok: null, message: "실행 중" });
      renderBatchProgress(`${label} 실행 중`, false);
      return steps.length - 1;
    };
    const finishPending = (index, payload, ok, message) => {
      steps[index] = { ...steps[index], payload: payload || {}, ok: ok === true, status: ok === true ? "ok" : "blocked", message: message || (payload && payload.status) || "" };
      renderBatchProgress(`${steps[index].label} 완료`, false);
    };

    try {
      let stepIndex = pushPending("createPreview", "1. 생성 preview");
      let response = await window.RpgGameApi.previewAdminMasterDataCreate({ domain: values.domain, draft: values.draft, reason, dryRun: true, timeoutMs: DEFAULT_TIMEOUT_MS });
      let payload = response && response.payload ? response.payload : {};
      finishPending(stepIndex, payload, !!payload.createApplyReady, payload.status);
      if (!payload.createApplyReady) throw new Error(`생성 preview 차단: ${formatValue(payload.status)}`);

      stepIndex = pushPending("createApply", "2. 생성 apply");
      response = await window.RpgGameApi.applyAdminMasterDataCreate({ domain: values.domain, draft: values.draft, reason, confirmText: ADMIN_CREATE_APPLY_CONFIRM_TEXT, dryRun: false, timeoutMs });
      payload = response && response.payload ? response.payload : {};
      const createChangeLogId = Number(payload.changeLogId || 0);
      finishPending(stepIndex, payload, !!payload.created && createChangeLogId > 0, payload.status);
      if (!payload.created || !createChangeLogId) throw new Error(`생성 apply 실패: ${formatValue(payload.status)}`);

      stepIndex = pushPending("deletePreview", "3. 삭제 preview");
      response = await window.RpgGameApi.previewAdminCreateDeleteRollback({ id: createChangeLogId, reason, timeoutMs: DEFAULT_TIMEOUT_MS });
      payload = response && response.payload ? response.payload : {};
      finishPending(stepIndex, payload, !!payload.createDeleteReady, payload.status);
      if (!payload.createDeleteReady) throw new Error(`삭제 preview 차단: ${formatValue(payload.status)}`);

      stepIndex = pushPending("deleteApply", "4. 삭제 apply");
      response = await window.RpgGameApi.applyAdminCreateDeleteRollback({ id: createChangeLogId, reason, confirmText: ADMIN_CREATE_DELETE_CONFIRM_TEXT, timeoutMs });
      payload = response && response.payload ? response.payload : {};
      const deleteChangeLogId = Number(payload.deleteChangeLogId || 0);
      finishPending(stepIndex, payload, !!payload.deleted && deleteChangeLogId > 0, payload.status);
      if (!payload.deleted || !deleteChangeLogId) throw new Error(`삭제 apply 실패: ${formatValue(payload.status)}`);

      stepIndex = pushPending("restorePreview", "5. 복원 preview");
      response = await window.RpgGameApi.previewAdminCreateDeleteRestore({ id: deleteChangeLogId, reason, timeoutMs: DEFAULT_TIMEOUT_MS });
      payload = response && response.payload ? response.payload : {};
      finishPending(stepIndex, payload, !!payload.createDeleteRestoreReady, payload.status);
      if (!payload.createDeleteRestoreReady) throw new Error(`복원 preview 차단: ${formatValue(payload.status)}`);

      stepIndex = pushPending("restoreApply", "6. 복원 apply");
      response = await window.RpgGameApi.applyAdminCreateDeleteRestore({ id: deleteChangeLogId, reason, confirmText: ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT, timeoutMs });
      payload = response && response.payload ? response.payload : {};
      finishPending(stepIndex, payload, !!payload.restored, payload.status);
      if (!payload.restored) throw new Error(`복원 apply 실패: ${formatValue(payload.status)}`);

      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminReadOnlyPage({
        snapshotFilters: readSnapshotFiltersFromDom(),
        masterCatalogFilters: { ...readMasterCatalogFiltersFromDom(), domain: values.domain, page: 1 },
        changeLogFilters: readChangeLogFiltersFromDom(),
        createBlueprintFilters: { domain: values.domain },
      });
      renderAdminCreateLifecycleBatchResult(steps, { finished: true, note: `생성→삭제→복원 일괄 점검 완료 · restore log #${formatValue(payload.restoreChangeLogId)}` });
      if (payload.domain && payload.id) {
        await runPostWriteMasterApiVerification(payload.domain, payload.id, { label: "생성 lifecycle 일괄 점검", contextLabel: `restore log #${formatValue(payload.restoreChangeLogId)} 적용 후 자동 확인` });
      }
      setStatus(`생성→삭제→복원 일괄 점검 완료: ${formatValue(values.domain)} #${formatValue(payload.id)} · restore log #${formatValue(payload.restoreChangeLogId)}`, "ok");
      return { ok: true, steps };
    } catch (error) {
      renderAdminCreateLifecycleBatchResult(steps, { note: error && error.message ? error.message : "일괄 점검이 중단되었습니다." });
      setStatus(`생성→삭제→복원 일괄 점검 중단: ${error && error.message ? error.message : error}`, "error");
      throw error;
    }
  }

  function renderAdminCreateLifecycleMetric(label, value, tone) {
    return `
      <div class="create-result-metric ${escapeHtml(tone || "")}">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(formatValue(value))}</strong>
      </div>
    `;
  }

  function renderAdminOperationResultBanner(options) {
    const opts = options || {};
    const metrics = Array.isArray(opts.metrics) ? opts.metrics : [];
    const tone = opts.tone || "warn";
    const metricHtml = metrics.length ? `
      <div class="create-result-metric-grid">
        ${metrics.map((metric) => renderAdminCreateLifecycleMetric(metric.label, metric.value, metric.tone)).join("")}
      </div>
    ` : "";
    return `
      <div class="create-result-banner ${escapeHtml(tone)}">
        <div class="create-result-banner-title">${escapeHtml(opts.title || "검사 결과")}</div>
        ${opts.subtitle ? `<div class="create-result-banner-subtitle">${escapeHtml(opts.subtitle)}</div>` : ""}
        ${metricHtml}
      </div>
    `;
  }

  function renderAdminCreateDeleteBlockerSummary(dependencyChecks) {
    const checks = Array.isArray(dependencyChecks) ? dependencyChecks : [];
    const blockers = checks.filter((item) => item && item.blocksDelete);
    if (!blockers.length) {
      return `<div class="filter-help create-result-safe-note">연결 데이터 차단 없음: 현재값 안전 검사만 통과하면 삭제할 수 있습니다.</div>`;
    }
    return `
      <div class="create-result-blocker-list">
        <strong>삭제 차단 연결 ${escapeHtml(formatValue(blockers.length))}개</strong>
        <ul>
          ${blockers.map((item) => `<li>${escapeHtml(item.label || item.target || "dependency")} · ${escapeHtml(formatValue(item.count || 0))}건 · <code>${escapeHtml(item.target || "-")}</code></li>`).join("")}
        </ul>
      </div>
    `;
  }

  function renderAdminCreateLifecycleGuide(blueprintPayload) {
    const target = $("[data-admin-create-lifecycle-guide]");
    if (!target) return;
    const payload = blueprintPayload && blueprintPayload.domain ? blueprintPayload : {};
    if (!payload.domain) {
      target.innerHTML = `<div class="empty">생성 설계를 불러오면 현재 도메인의 생성→삭제→복원 점검 순서가 여기에 표시됩니다.</div>`;
      return;
    }
    const lifecycle = payload.createLifecycle && typeof payload.createLifecycle === "object" ? payload.createLifecycle : {};
    const order = Array.isArray(lifecycle.browserCheckOrder) ? lifecycle.browserCheckOrder : [];
    const lockedFields = Array.isArray(lifecycle.lockedFields) ? lifecycle.lockedFields : [];
    const comboGuards = Array.isArray(lifecycle.comboGuards) ? lifecycle.comboGuards : (Array.isArray(payload.comboGuards) ? payload.comboGuards : []);
    const confirmTexts = lifecycle.confirmTexts && typeof lifecycle.confirmTexts === "object" ? lifecycle.confirmTexts : {};
    const relationCount = Number(payload.relationFieldCount || 0);
    const actionFilters = ADMIN_CHANGE_LOG_ACTION_FILTERS.map((action) => `<code>${escapeHtml(action)}</code>`).join(" · ");
    const orderItems = order.length ? order.map((item) => `<li>${escapeHtml(item)}</li>`).join("") : `<li>생성 preview/apply 후 change log에서 create 이력을 열어 삭제/복원 미리보기를 확인합니다.</li>`;
    const lockedText = lockedFields.length ? lockedFields.map((field) => `<code>${escapeHtml(field)}</code>`).join(" · ") : "잠긴 JSON/asset 필드 없음";
    const comboText = comboGuards.length ? comboGuards.map((guard) => `<code>${escapeHtml(guard.join(" + "))}</code>`).join(" · ") : "combo 중복 검사 없음";
    const guardMode = lifecycle.deleteGuardMode || "preview-checked";
    target.innerHTML = `
      <div class="create-lifecycle-grid create-lifecycle-grid-wide">
        <div class="create-lifecycle-card">
          <strong>${escapeHtml(payload.domainLabel || payload.domain)} 흐름 상태</strong>
          <div class="draft-preview-summary">
            ${formatAdminCreateLifecyclePill(lifecycle.createApplyUnlocked !== false && payload.createApplyUnlocked !== false, "생성 가능", "생성 잠금")}
            ${formatAdminCreateLifecyclePill(lifecycle.createDeleteUnlocked !== false, "삭제 가능", "삭제 잠금")}
            ${formatAdminCreateLifecyclePill(lifecycle.createDeleteRestoreUnlocked !== false, "복원 가능", "복원 잠금")}
            <span class="pill warn">key: ${escapeHtml(lifecycle.deleteRestoreKey || lifecycle.identityMode || "id")}</span>
            <span class="pill ${guardMode === "dependency-blocking" ? "blocked" : "good"}">${escapeHtml(guardMode)}</span>
          </div>
          <ul>
            <li>relation 필드: ${escapeHtml(formatValue(relationCount))}개</li>
            <li>중복 검사: ${comboText}</li>
            <li>잠금 필드: ${lockedText}</li>
          </ul>
        </div>
        <div class="create-lifecycle-card">
          <strong>브라우저 점검 순서</strong>
          <ol>${orderItems}</ol>
        </div>
        <div class="create-lifecycle-card">
          <strong>확인 문구 / 이력 바로가기</strong>
          <ul>
            <li>생성: <code>${escapeHtml(confirmTexts.create || ADMIN_CREATE_APPLY_CONFIRM_TEXT)}</code></li>
            <li>생성 row 삭제: <code>${escapeHtml(confirmTexts.deleteCreatedRow || ADMIN_CREATE_DELETE_CONFIRM_TEXT)}</code></li>
            <li>삭제 row 복원: <code>${escapeHtml(confirmTexts.restoreDeletedCreatedRow || ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT)}</code></li>
            <li>변경 이력 action 필터: ${actionFilters}</li>
          </ul>
          ${renderAdminCreateLifecycleActionShortcuts()}
        </div>
        <div class="create-lifecycle-card create-lifecycle-card-wide">
          <strong>삭제 preview 차단 기준</strong>
          ${renderAdminCreateLifecycleDependencyGuards(lifecycle)}
        </div>
      </div>
      <div class="filter-help" style="padding:0 14px 12px;">이 점검 가이드는 DB를 수정하지 않습니다. 실제 적용은 기존처럼 dev key, 확인 문구, 백엔드 preview 안전검사를 모두 통과해야 합니다.</div>
    `;
  }

  function getAdminCreateLifecycleGuideReadiness() {
    const guide = currentAdminCreateBlueprintPayload && currentAdminCreateBlueprintPayload.createLifecycle ? currentAdminCreateBlueprintPayload.createLifecycle : {};
    const dependencyGuards = Array.isArray(guide.deleteDependencyGuards) ? guide.deleteDependencyGuards : [];
    return {
      ok: !!document.querySelector("[data-admin-create-lifecycle-guide]") && typeof renderAdminCreateLifecycleGuide === "function",
      hasGuideContainer: !!document.querySelector("[data-admin-create-lifecycle-guide]"),
      actionFilters: ADMIN_CHANGE_LOG_ACTION_FILTERS.slice(),
      dependencyGuardReady: typeof renderAdminCreateLifecycleDependencyGuards === "function",
      actionShortcutReady: typeof applyAdminChangeLogActionShortcut === "function",
      dependencyGuardCount: dependencyGuards.length,
      deleteGuardMode: guide.deleteGuardMode || null,
    };
  }

  function getAdminCreateLifecycleSplitContractReadiness() {
    const contract = ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT;
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
    const ok = (contract.status === "extracted-v189" || contract.status === "contract-frozen-v188") && missingApiMethods.length === 0 && missingWindowExports.length === 0 && missingDomTargets.length === 0 && missingConfirmTexts.length === 0;
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

  function renderAdminCreateLifecycleSplitContractReadiness(contractReadiness) {
    const readiness = contractReadiness || getAdminCreateLifecycleSplitContractReadiness();
    const apiHtml = readiness.requiredApiMethods.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${item.ok ? "ok" : "missing"}</span>`).join(" ");
    const exportRows = readiness.requiredWindowExports.map((item) => `<tr><td>${escapeHtml(item.key)}</td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const domRows = readiness.domTargets.map((item) => `<tr><td><code>${escapeHtml(item.selector)}</code></td><td><span class="pill ${item.ok ? "good" : "blocked"}">${item.ok ? "ok" : "missing"}</span></td></tr>`).join("");
    const confirmHtml = readiness.confirmTexts.map((item) => `<span class="pill ${item.ok ? "good" : "blocked"}">${escapeHtml(item.key)}: ${escapeHtml(item.value)}</span>`).join(" ");
    const boundaryHtml = readiness.splitBoundary.map((item) => `<span class="pill warn">${escapeHtml(item)}</span>`).join(" ");
    return `
      <div class="create-lifecycle-card create-lifecycle-card-wide">
        ${renderAdminOperationResultBanner({
          tone: readiness.ok ? "good" : "warn",
          title: readiness.ok ? "create lifecycle 분리 계약 고정 완료" : "create lifecycle 분리 계약 확인 필요",
          subtitle: `${readiness.currentFile} → ${readiness.nextFile} 이동 전, 생성 초안/일괄 점검 API·window·DOM 계약을 먼저 고정했습니다.`,
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
        <div class="filter-help">v189에서 실제 파일 분리를 완료했습니다. <code>admin-page-readonly.js</code>에는 호환 wrapper만 남겼습니다.</div>
        <div class="create-blueprint-summary" style="grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);">
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>window export</th><th>상태</th></tr></thead><tbody>${exportRows}</tbody></table></div>
          <div class="table-wrap relation-table-wrap"><table><thead><tr><th>DOM target</th><th>상태</th></tr></thead><tbody>${domRows}</tbody></table></div>
        </div>
      </div>
    `;
  }

  function renderAdminCreateBlueprint(blueprintPayload) {
    currentAdminCreateBlueprintPayload = blueprintPayload && blueprintPayload.status === "loaded" ? blueprintPayload : null;
    const target = $("[data-admin-create-blueprint]");
    if (!target) return;
    const payload = blueprintPayload || {};
    if (payload.status && payload.status !== "loaded") {
      target.innerHTML = `<div class="error">신규 row 생성 설계를 불러오지 못했습니다: ${escapeHtml(payload.status)}</div>`;
      renderAdminCreateLifecycleGuide({});
      return;
    }
    if (!payload.domain) {
      target.innerHTML = `<div class="empty">생성 설계를 불러오면 필수 필드, 기본값, relation 후보가 여기에 표시됩니다.</div>`;
      renderAdminCreateLifecycleGuide({});
      return;
    }
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const requiredFields = Array.isArray(payload.requiredFields) ? payload.requiredFields : [];
    const uniqueFields = Array.isArray(payload.uniqueFields) ? payload.uniqueFields : [];
    const comboGuards = Array.isArray(payload.comboGuards) ? payload.comboGuards : [];
    const defaultDraft = payload.defaultDraft && typeof payload.defaultDraft === "object" ? payload.defaultDraft : {};
    const rows = fields.length ? fields.map((field) => {
      const inputKind = getAdminCreateBlueprintFieldInputKind(field);
      const relationText = renderAdminCreateBlueprintRelationCell(field);
      return `
        <tr>
          <td>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</td>
          <td>${field.required ? `<span class="pill blocked">필수</span>` : `<span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</td>
          <td><span class="pill">${escapeHtml(inputKind)}</span></td>
          <td>${formatValueWithFieldHint(field.key, field.defaultValue)}</td>
          <td>${relationText}</td>
          <td><span class="create-blueprint-locked">${field.futureEditable === false ? "잠금" : "초안 가능"}</span><div class="filter-help" style="margin-top:4px;">${escapeHtml(field.futureEditable === false ? (field.lockedReason || "read-only") : "preview-only 입력 UI에서 검증 가능")}</div></td>
        </tr>
      `;
    }).join("") : `<tr><td colspan="6">필드 설계가 없습니다.</td></tr>`;
    target.innerHTML = `
      <div class="create-blueprint-summary">
        <div class="create-blueprint-card"><strong>${escapeHtml(payload.domainLabel || payload.domain)}</strong><span>${escapeHtml(payload.description || "설명 없음")}</span></div>
        <div class="create-blueprint-card"><strong>필수 필드</strong><span>${escapeHtml(requiredFields.join(", ") || "없음")}</span></div>
        <div class="create-blueprint-card"><strong>고유/중복 검사</strong><span>unique: ${escapeHtml(uniqueFields.join(", ") || "없음")}<br>combo: ${escapeHtml(comboGuards.map((guard) => guard.join(" + ")).join(", ") || "없음")}</span></div>
        <div class="create-blueprint-card"><strong>적용 상태</strong><span><span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "limited insert open" : "insert API locked"}</span><br>${payload.createApplyUnlocked ? "dev key + 확인 문구 필요" : "preview-only 검증 가능 · DB 수정 없음"}</span></div>
      </div>
      <div class="table-wrap relation-table-wrap">
        <table>
          <thead><tr><th>필드</th><th>필수</th><th>입력 타입</th><th>기본값</th><th>관계 후보</th><th>현재 상태</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <div class="create-blueprint-default">
        <pre>${escapeHtml(JSON.stringify(defaultDraft, null, 2))}</pre>
      </div>
      ${renderAdminCreateDraft(payload)}
      <div class="filter-help" style="padding:0 14px 12px;">relation 후보 반환=${escapeHtml(formatValue(payload.relationOptionsReturned))} · rawJsonReturned=${escapeHtml(formatValue(payload.rawJsonReturned))} · assetsReturned=${escapeHtml(formatValue(payload.assetsReturned))}</div>
    `;
    renderAdminCreateLifecycleGuide(payload);
  }

  async function refreshAdminCreateBlueprint(options) {
    ensureApi();
    const filters = options || readAdminCreateBlueprintFiltersFromDom();
    const response = await window.RpgGameApi.fetchAdminMasterCreateBlueprint({ timeoutMs: DEFAULT_TIMEOUT_MS, ...filters });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateBlueprint(payload);
    setStatus(`신규 row 생성 설계 로드: ${formatValue(payload.domainLabel || payload.domain)} · ${formatValue(payload.fieldCount)} fields · ${payload.createApplyUnlocked ? "limited insert open" : "preview-only"}`, "ok");
    return payload;
  }

  function readAdminCreateDraftValues() {
    const draft = $(`[data-admin-create-draft]`);
    if (!draft) return { ok: false, reason: "create_draft_missing", draft: {} };
    const fields = Array.from(draft.querySelectorAll("[data-admin-create-draft-field]"));
    const values = {};
    fields.forEach((field) => {
      const key = field.getAttribute("data-admin-create-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      values[key] = type === "boolean" ? field.value === "true" : field.value;
    });
    const reasonEl = $(`[data-admin-create-reason]`);
    const confirmEl = $(`[data-admin-create-confirm]`);
    return {
      ok: true,
      domain: draft.getAttribute("data-admin-create-draft-domain") || (currentAdminCreateBlueprintPayload && currentAdminCreateBlueprintPayload.domain) || DEFAULT_MASTER_DOMAIN,
      draft: values,
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      fieldCount: fields.length,
    };
  }

  function resetAdminCreateDraft() {
    const draft = $(`[data-admin-create-draft]`);
    if (!draft) return false;
    Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")).forEach((field) => {
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-create-draft-original"));
      if (type === "boolean") field.value = original ? "true" : "false";
      else field.value = original === null || original === undefined ? "" : String(original);
    });
    Array.from(draft.querySelectorAll("[data-admin-create-relation-option-filter]")).forEach((input) => { input.value = ""; applyAdminCreateRelationOptionFilter(input); });
    const confirmEl = $(`[data-admin-create-confirm]`);
    if (confirmEl) confirmEl.value = "";
    const result = $(`[data-admin-create-draft-result]`);
    if (result) result.innerHTML = `<div class="empty">기본값으로 되돌렸습니다. 값을 입력한 뒤 생성 초안 검증을 누르세요.</div>`;
    setStatus("생성 초안을 기본값으로 되돌렸습니다.", "ok");
    return true;
  }

  function renderAdminCreatePreviewValueCell(field) {
    const rawValue = field ? field.after : undefined;
    const relationText = formatAdminRelationInfoText(field && field.relation, rawValue);
    const text = relationText !== null ? relationText : formatValue(rawValue);
    const relation = field && field.relation ? field.relation : null;
    const target = relation && relation.targetDomain && !String(relation.targetDomain).includes("/") && relation.targetCode ? { domain: String(relation.targetDomain), code: String(relation.targetCode) } : null;
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${renderAdminRelationOpenTargetButton(target)}</div>`;
  }

  function renderAdminCreatePreviewResult(preview) {
    const target = $(`[data-admin-create-draft-result]`);
    if (!target) return;
    const payload = preview || {};
    const accepted = Array.isArray(payload.acceptedFields) ? payload.acceptedFields : [];
    const rejected = Array.isArray(payload.rejectedFields) ? payload.rejectedFields : [];
    const acceptedRows = accepted.length ? accepted.map((field) => `
      <tr><td>${escapeHtml(field.label || field.key)}${field.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminCreatePreviewValueCell(field)}</td><td>${escapeHtml(field.type || field.inputKind || "-")}</td><td>${field.required ? `<span class="pill blocked">필수</span>` : `<span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</td></tr>
    `).join("") : `<tr><td colspan="4">검증 통과 필드 없음</td></tr>`;
    const rejectedRows = rejected.length ? rejected.map((field) => `
      <tr><td>${escapeHtml(field.label || field.key)}</td><td>${escapeHtml(formatValue(field.after))}</td><td>${escapeHtml(field.reason || "rejected")}</td></tr>
    `).join("") : `<tr><td colspan="3">오류 없음</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${payload.wouldBeValid ? "good" : "blocked"}">valid: ${escapeHtml(formatValue(payload.wouldBeValid))}</span>
        <span class="pill ${payload.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(payload.dryRun))}</span>
        <span class="pill ${payload.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(payload.writeBlocked))}</span>
        <span class="pill ${payload.createApplyReady ? "warn" : "blocked"}">createApplyReady: ${escapeHtml(formatValue(payload.createApplyReady))}</span>
        ${payload.created ? `<span class="pill good">created #${escapeHtml(formatValue(payload.id))}</span>` : ""}
        ${payload.changeLogId ? `<span class="pill good">changeLog #${escapeHtml(formatValue(payload.changeLogId))}</span>` : ""}
        <span class="pill">fields ${escapeHtml(formatValue(payload.fieldCount || accepted.length))}</span>
        <span class="pill ${rejected.length ? "blocked" : "good"}">errors ${escapeHtml(formatValue(payload.errorCount || rejected.length))}</span>
        <span class="pill ${payload.relationFieldCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(payload.relationFieldCount || 0))}</span>
        <span class="pill ${payload.comboGuardCount ? "warn" : "good"}">combo ${escapeHtml(formatValue(payload.comboGuardCount || 0))}</span>
      </div>
      ${payload.comboGuardLabels && payload.comboGuardLabels.length ? `<div class="filter-help">중복 조합 검사: ${escapeHtml(payload.comboGuardLabels.join(", "))}</div>` : ""}
      ${payload.note ? `<div class="filter-help">${escapeHtml(payload.note)}</div>` : ""}
      ${renderUnifiedPreviewDiff(payload)}
      <details class="json-detail" open>
        <summary>검증 통과 필드 <span class="pill good">${escapeHtml(formatValue(accepted.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>타입</th><th>속성</th></tr></thead><tbody>${acceptedRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${rejected.length ? "open" : ""}>
        <summary>검증 오류 <span class="pill ${rejected.length ? "blocked" : "good"}">${escapeHtml(formatValue(rejected.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>사유</th></tr></thead><tbody>${rejectedRows}</tbody></table></div>
      </details>
      ${payload.createdRow ? `<div class="filter-help">생성됨: ${escapeHtml(payload.createdRow.domain)} #${escapeHtml(formatValue(payload.createdRow.id))} · ${escapeHtml(formatValue(payload.createdRow.code || payload.createdRow.title))}</div>` : ""}
      <div class="filter-help">${payload.created ? "DB insert와 create change log가 완료되었습니다. create rollback/delete는 아직 잠겨 있습니다." : "검증 통과 후 제한 도메인은 dev key와 생성 확인 문구로 실제 생성 적용할 수 있습니다."}</div>
    `;
  }

  async function previewAdminCreateDraft(options) {
    ensureApi();
    const values = readAdminCreateDraftValues();
    if (!values.ok) {
      const error = new Error("검증할 생성 초안이 없습니다. 먼저 생성 설계를 불러와 주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-create-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 초안을 검증하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminMasterDataCreate({
      domain: values.domain,
      draft: values.draft,
      reason: values.reason || undefined,
      dryRun: true,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreatePreviewResult(payload);
    setStatus(`생성 초안 검증 완료: fields ${formatValue(payload.fieldCount)} · errors ${formatValue(payload.errorCount)} · createApplyReady ${formatValue(payload.createApplyReady)}`, payload.errorCount ? "error" : "ok");
    return response;
  }

  async function applyAdminCreateDraft(options) {
    ensureApi();
    const values = readAdminCreateDraftValues();
    if (!values.ok) {
      const error = new Error("생성 적용할 초안이 없습니다. 먼저 생성 설계를 불러와 주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    if (!values.confirmText) {
      const error = new Error(`생성 확인 문구를 입력해야 합니다: ${ADMIN_CREATE_APPLY_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-create-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 초안을 재검증하고 실제 생성 적용 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminMasterDataCreate({
      domain: values.domain,
      draft: values.draft,
      reason: values.reason || undefined,
      confirmText: values.confirmText,
      dryRun: false,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreatePreviewResult(payload);
    if (payload.created) {
      setStatus(`신규 row 생성 완료: ${formatValue(payload.domain)} #${formatValue(payload.id)} · changeLog #${formatValue(payload.changeLogId)}`, "ok");
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminReadOnlyPage({
        snapshotFilters: readSnapshotFiltersFromDom(),
        masterCatalogFilters: { ...readMasterCatalogFiltersFromDom(), domain: values.domain, page: 1 },
        changeLogFilters: readChangeLogFiltersFromDom(),
        createBlueprintFilters: { domain: values.domain },
      });
    } else {
      setStatus(`신규 row 생성 차단: ${formatValue(payload.status)} · errors ${formatValue(payload.errorCount)}`, "error");
    }
    return response;
  }

  function getAdminCreateBlueprintReadiness() {
    const target = $("[data-admin-create-blueprint]");
    const draft = $(`[data-admin-create-draft]`);
    const filters = readAdminCreateBlueprintFiltersFromDom();
    const payload = currentAdminCreateBlueprintPayload || {};
    const fields = draft ? Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")) : [];
    return {
      ready: !!target,
      readOnly: !payload.createApplyUnlocked,
      createApplyReady: !!payload.createApplyReady,
      createApplyUnlocked: !!payload.createApplyUnlocked,
      insertLocked: payload.insertLocked !== false,
      confirmTextRequired: payload.confirmTextRequired || ADMIN_CREATE_APPLY_CONFIRM_TEXT,
      allowedCreateApplyDomains: Array.isArray(payload.allowedCreateApplyDomains) ? payload.allowedCreateApplyDomains.slice() : [],
      previewReady: typeof previewAdminCreateDraft === "function" && !!window.RpgGameApi && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function",
      applyReady: typeof applyAdminCreateDraft === "function" && !!window.RpgGameApi && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function",
      domain: filters.domain,
      loadedDomain: payload.domain || null,
      fieldCount: Number(payload.fieldCount || 0),
      draftFieldCount: fields.length,
      requiredFields: getAdminCreateBlueprintRequiredKeys(payload.domain, payload),
      defaultDraft: getAdminCreateBlueprintDefaultDraft(payload.domain, payload),
      relationOptionsReturned: !!payload.relationOptionsReturned,
    };
  }

  window.RpgAdminCreateLifecycle = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    readAdminCreateBlueprintFiltersFromDom,
    syncAdminCreateDomainFromCatalog,
    getAdminCreateBlueprintFieldInputKind,
    getAdminCreateBlueprintRequiredKeys,
    getAdminCreateBlueprintDefaultDraft,
    getAdminCreateBlueprintRelationOptionCount,
    renderAdminCreateBlueprintRelationCell,
    getAdminCreateFieldDefinition,
    getAdminCreateRelationDefinition,
    getAdminCreateRelationOptionsForValues,
    getAdminCreateDraftCurrentValues,
    getAdminCreateDraftSelectOptions,
    applyAdminCreateRelationOptionFilter,
    refreshDependentAdminCreateRelationSelects,
    renderAdminCreateLifecycleDependencyGuards,
    renderAdminCreateLifecycleBatchResult,
    runAdminCreateLifecycleBatchCheck,
    renderAdminOperationResultBanner,
    renderAdminCreateDeleteBlockerSummary,
    renderAdminCreateLifecycleGuide,
    getAdminCreateLifecycleGuideReadiness,
    getAdminCreateLifecycleSplitContractReadiness,
    renderAdminCreateLifecycleSplitContractReadiness,
    renderAdminCreateBlueprint,
    refreshAdminCreateBlueprint,
    readAdminCreateDraftValues,
    resetAdminCreateDraft,
    renderAdminCreatePreviewResult,
    previewAdminCreateDraft,
    applyAdminCreateDraft,
    getAdminCreateBlueprintReadiness,
  };
})();
