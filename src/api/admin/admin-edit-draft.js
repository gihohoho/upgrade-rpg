(function () {
  "use strict";

  const VERSION = "v191.admin-edit-draft-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v190.admin-edit-draft-split-contract v189.1.admin-create-lifecycle-split-hotfix v187.admin-change-logs-split";

  let configured = false;
  let DEFAULT_MASTER_DOMAIN = "itemTemplates";
  let DEFAULT_TIMEOUT_MS = 3500;
  let ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  let ADMIN_EDIT_APPLY_CONFIRM_TEXT = "APPLY MASTER DATA EDIT";
  let ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT = "HIGH RISK EDIT";
  let ADMIN_EDIT_ALLOWED_FIELDS = {};
  let ADMIN_DRAFT_BOOLEAN_FIELDS = new Set();
  let ADMIN_DRAFT_NUMBER_FIELDS = new Set();
  let ADMIN_DRAFT_TEXTAREA_FIELDS = new Set();
  let ADMIN_EQUIP_SLOT_PRESET_LABELS = {};
  let ADMIN_DRAFT_SELECT_FIELD_OPTIONS = {};
  let ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT = 18;

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
  let ensureApi = () => {
    if (!window.RpgGameApi) throw new Error("RpgGameApi is not loaded");
    return window.RpgGameApi;
  };
  let setStatus = () => undefined;
  let hasAdminWriteDevKey = () => false;
  let requireAdminWriteDevKeyForUi = () => true;
  let runPostWriteMasterApiVerification = async () => ({ ok: true });
  let refreshAdminChangeLogs = async () => ({ ok: true });
  let readChangeLogFiltersFromDom = () => ({});
  let getCurrentMasterDetailPayload = () => null;

  const ADMIN_EDIT_DRAFT_SPLIT_CONTRACT = {
    key: "edit-draft",
    label: "Edit draft",
    status: "extracted-v191",
    currentFile: "src/api/admin/admin-edit-draft.js",
    nextFile: "src/api/admin/admin-edit-draft.js",
  };

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    if (typeof d.formatValueWithFieldHint === "function") formatValueWithFieldHint = d.formatValueWithFieldHint;
    if (typeof d.renderFieldHelpBadge === "function") renderFieldHelpBadge = d.renderFieldHelpBadge;
    if (typeof d.renderFieldHelpInline === "function") renderFieldHelpInline = d.renderFieldHelpInline;
    if (typeof d.renderFieldValueHintInline === "function") renderFieldValueHintInline = d.renderFieldValueHintInline;
    if (typeof d.ensureApi === "function") ensureApi = d.ensureApi;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.hasAdminWriteDevKey === "function") hasAdminWriteDevKey = d.hasAdminWriteDevKey;
    if (typeof d.requireAdminWriteDevKeyForUi === "function") requireAdminWriteDevKeyForUi = d.requireAdminWriteDevKeyForUi;
    if (typeof d.runPostWriteMasterApiVerification === "function") runPostWriteMasterApiVerification = d.runPostWriteMasterApiVerification;
    if (typeof d.refreshAdminChangeLogs === "function") refreshAdminChangeLogs = d.refreshAdminChangeLogs;
    if (typeof d.readChangeLogFiltersFromDom === "function") readChangeLogFiltersFromDom = d.readChangeLogFiltersFromDom;
    if (typeof d.getCurrentMasterDetailPayload === "function") getCurrentMasterDetailPayload = d.getCurrentMasterDetailPayload;
    DEFAULT_MASTER_DOMAIN = d.DEFAULT_MASTER_DOMAIN || DEFAULT_MASTER_DOMAIN;
    DEFAULT_TIMEOUT_MS = Number(d.DEFAULT_TIMEOUT_MS || DEFAULT_TIMEOUT_MS);
    ADMIN_EDIT_APPLY_TIMEOUT_MS = Number(d.ADMIN_EDIT_APPLY_TIMEOUT_MS || ADMIN_EDIT_APPLY_TIMEOUT_MS);
    ADMIN_EDIT_APPLY_CONFIRM_TEXT = d.ADMIN_EDIT_APPLY_CONFIRM_TEXT || ADMIN_EDIT_APPLY_CONFIRM_TEXT;
    ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT = d.ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT || ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT;
    ADMIN_EDIT_ALLOWED_FIELDS = d.ADMIN_EDIT_ALLOWED_FIELDS && typeof d.ADMIN_EDIT_ALLOWED_FIELDS === "object" ? d.ADMIN_EDIT_ALLOWED_FIELDS : ADMIN_EDIT_ALLOWED_FIELDS;
    ADMIN_DRAFT_BOOLEAN_FIELDS = d.ADMIN_DRAFT_BOOLEAN_FIELDS instanceof Set ? d.ADMIN_DRAFT_BOOLEAN_FIELDS : ADMIN_DRAFT_BOOLEAN_FIELDS;
    ADMIN_DRAFT_NUMBER_FIELDS = d.ADMIN_DRAFT_NUMBER_FIELDS instanceof Set ? d.ADMIN_DRAFT_NUMBER_FIELDS : ADMIN_DRAFT_NUMBER_FIELDS;
    ADMIN_DRAFT_TEXTAREA_FIELDS = d.ADMIN_DRAFT_TEXTAREA_FIELDS instanceof Set ? d.ADMIN_DRAFT_TEXTAREA_FIELDS : ADMIN_DRAFT_TEXTAREA_FIELDS;
    ADMIN_EQUIP_SLOT_PRESET_LABELS = d.ADMIN_EQUIP_SLOT_PRESET_LABELS && typeof d.ADMIN_EQUIP_SLOT_PRESET_LABELS === "object" ? d.ADMIN_EQUIP_SLOT_PRESET_LABELS : ADMIN_EQUIP_SLOT_PRESET_LABELS;
    ADMIN_DRAFT_SELECT_FIELD_OPTIONS = d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS && typeof d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS === "object" ? d.ADMIN_DRAFT_SELECT_FIELD_OPTIONS : ADMIN_DRAFT_SELECT_FIELD_OPTIONS;
    ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT = Number(d.ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT || ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT);
    configured = true;
    return getReadiness();
  }

  function getReadiness() {
    const requiredFunctions = {
      querySelector: typeof $ === "function",
      escapeHtml: typeof escapeHtml === "function",
      formatValue: typeof formatValue === "function",
      ensureApi: typeof ensureApi === "function",
      setStatus: typeof setStatus === "function",
      hasAdminWriteDevKey: typeof hasAdminWriteDevKey === "function",
      requireAdminWriteDevKeyForUi: typeof requireAdminWriteDevKeyForUi === "function",
      refreshAdminChangeLogs: typeof refreshAdminChangeLogs === "function",
      getCurrentMasterDetailPayload: typeof getCurrentMasterDetailPayload === "function",
    };
    const missing = Object.keys(requiredFunctions).filter((key) => !requiredFunctions[key]);
    return {
      ok: configured && !missing.length,
      version: VERSION,
      configured,
      missing,
      contract: ADMIN_EDIT_DRAFT_SPLIT_CONTRACT,
    };
  }

  function getAdminRelationEditOptionDefinitions(domain) {
    const currentMasterDetailPayload = getCurrentMasterDetailPayload();
    const detail = currentMasterDetailPayload && currentMasterDetailPayload.domain === domain ? currentMasterDetailPayload : {};
    return Array.isArray(detail.relationEditOptions) ? detail.relationEditOptions : [];
  }

  function getAdminRelationEditOptionDefinition(domain, key) {
    const normalized = normalizeAdminDraftFieldKey(key);
    return getAdminRelationEditOptionDefinitions(domain).find((definition) => normalizeAdminDraftFieldKey(definition && definition.field) === normalized) || null;
  }

  function isAdminRelationEditField(domain, key) {
    return !!getAdminRelationEditOptionDefinition(domain, key);
  }

  function fieldKeyLooksReadOnly(domain, key) {
    const normalized = String(key || "").toLowerCase();
    if (isAdminRelationEditField(domain, normalized)) return false;
    return normalized === "id" || normalized === "code" || normalized.endsWith("_id") || normalized.endsWith("_code") || normalized.endsWith("_json") || normalized === "created_at" || normalized === "updated_at" || normalized === "createdat" || normalized === "updatedat";
  }

  function isAdminEditApplyAllowedField(domain, key) {
    const allowed = ADMIN_EDIT_ALLOWED_FIELDS[domain] || [];
    return allowed.includes(String(key || ""));
  }

  function getAdminEditAllowedFields(domain) {
    return (ADMIN_EDIT_ALLOWED_FIELDS[domain] || []).slice();
  }

  function normalizeAdminDraftFieldKey(key) {
    return String(key || "").trim().toLowerCase();
  }

  function getAdminEquipSlotDisplayName(value) {
    const key = value === null || value === undefined ? "" : String(value);
    return ADMIN_EQUIP_SLOT_PRESET_LABELS[key] || key || "장착 슬롯 없음";
  }

  function getAdminDraftRelationOptionGroupKey(definition) {
    if (!definition || !definition.dependsOn) return "";
    const dependencyField = document.querySelector(`[data-admin-edit-draft-field="${definition.dependsOn}"]`);
    const dependencyValue = dependencyField ? dependencyField.value : "";
    return String(dependencyValue || "").trim();
  }

  function getAdminDraftRelationOptionsForValues(definition, values) {
    if (!definition) return null;
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyKey = String(definition.dependsOn || "");
      const groupKey = values && Object.prototype.hasOwnProperty.call(values, dependencyKey) ? String(values[dependencyKey] || "").trim() : getAdminDraftRelationOptionGroupKey(definition);
      const grouped = definition.optionGroups[groupKey];
      if (Array.isArray(grouped)) return grouped.slice();
    }
    return Array.isArray(definition.options) ? definition.options.slice() : null;
  }

  function getAdminDraftRelationOptions(definition) {
    return getAdminDraftRelationOptionsForValues(definition, null);
  }

  function getAdminDraftSelectOptions(key, value, domain) {
    const normalized = normalizeAdminDraftFieldKey(key);
    const relationDefinition = getAdminRelationEditOptionDefinition(domain, normalized);
    const relationOptions = getAdminDraftRelationOptions(relationDefinition);
    const baseOptions = relationOptions ? relationOptions.slice() : (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[normalized] || []).slice();
    const valueText = value === null || value === undefined ? "" : String(value);
    if (valueText && !baseOptions.some((option) => String(option.value) === valueText)) {
      const currentLabel = normalized === "equip_slot" ? `${valueText} · ${getAdminEquipSlotDisplayName(valueText)} · 현재 DB 값` : `${valueText} · 현재 DB 값`;
      baseOptions.unshift({ value: valueText, label: currentLabel, current: true });
    }
    return baseOptions;
  }

  function normalizeAdminRelationSearchText(value) {
    return String(value === null || value === undefined ? "" : value).trim().toLowerCase();
  }

  function getAdminRelationOptionText(option) {
    if (!option) return "";
    return [option.value, option.label, option.targetLabel, option.targetDomain].filter((value) => value !== null && value !== undefined).join(" ");
  }

  function filterAdminDraftSelectOptions(options, query, selectedValue) {
    const safeOptions = Array.isArray(options) ? options.slice() : [];
    const normalizedQuery = normalizeAdminRelationSearchText(query);
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    const filtered = normalizedQuery
      ? safeOptions.filter((option) => normalizeAdminRelationSearchText(getAdminRelationOptionText(option)).includes(normalizedQuery))
      : safeOptions;
    if (selectedText && !filtered.some((option) => String(option.value) === selectedText)) {
      const selectedOption = safeOptions.find((option) => String(option.value) === selectedText);
      if (selectedOption) filtered.unshift({ ...selectedOption, keepSelected: true });
    }
    return filtered;
  }


  function renderUnifiedPreviewDiff(payload) {
    const diff = payload && Array.isArray(payload.unifiedDiff) ? payload.unifiedDiff : [];
    const snapshot = payload && payload.rollbackSnapshot ? payload.rollbackSnapshot : null;
    if (!diff.length && !snapshot) return "";
    const rows = diff.length ? diff.map((item) => `<tr><td>${escapeHtml(item.path || "$")}</td><td>${escapeHtml(item.op || "replace")}</td><td>${escapeHtml(formatValue(item.before))}</td><td>${escapeHtml(formatValue(item.after))}</td></tr>`).join("") : `<tr><td colspan="4">변경 없음</td></tr>`;
    return `<details class="json-detail" open><summary>공통 Diff <span class="pill good">${escapeHtml(formatValue(diff.length))}</span></summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>경로</th><th>작업</th><th>이전</th><th>이후</th></tr></thead><tbody>${rows}</tbody></table></div>${snapshot ? `<div class="filter-help">rollback snapshot: schema v${escapeHtml(formatValue(snapshot.schemaVersion))} · fingerprint ${escapeHtml(String(snapshot.fingerprint || "").slice(0, 12))}…</div>` : ""}</details>`;
  }
  function renderAdminDraftSelectOptionsHtml(options, selectedValue) {
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    const safeOptions = Array.isArray(options) ? options : [];
    if (!safeOptions.length) {
      return `<option value="${escapeHtml(selectedText)}" selected>${escapeHtml(selectedText ? `${selectedText} · 검색 결과 없음` : "검색 결과 없음")}</option>`;
    }
    return safeOptions.map((option) => {
      const optionValue = option && option.value !== undefined && option.value !== null ? String(option.value) : "";
      const optionLabel = option && option.label ? option.label : optionValue;
      const suffix = option && option.keepSelected ? " · 현재 선택값" : "";
      return `<option value="${escapeHtml(optionValue)}" ${optionValue === selectedText ? "selected" : ""}>${escapeHtml(optionLabel + suffix)}</option>`;
    }).join("");
  }

  function getAdminRelationSelectMetaText(key, domain, query) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return "";
    const allOptions = getAdminDraftRelationOptions(definition) || [];
    const filtered = filterAdminDraftSelectOptions(allOptions, query, "");
    const target = definition.targetLabel || definition.targetDomain || "관계 대상";
    const queryText = normalizeAdminRelationSearchText(query);
    return queryText ? `${target} ${filtered.length}/${allOptions.length}개 표시` : `${target} ${allOptions.length}개 중 선택`;
  }

  function updateAdminRelationOptionMeta(meta, key, domain, query) {
    if (!meta) return;
    const text = getAdminRelationSelectMetaText(key, domain, query);
    meta.textContent = text;
    meta.classList.toggle("warn", !!query && text.includes("0/"));
  }

  function applyAdminRelationOptionFilter(input) {
    if (!input) return false;
    const draft = input.closest("[data-admin-edit-draft]");
    const wrapper = input.closest("[data-admin-relation-select-tools]");
    if (!draft || !wrapper) return false;
    const domain = draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN;
    const key = input.getAttribute("data-admin-relation-option-filter-for") || "";
    const select = wrapper.querySelector(`[data-admin-edit-draft-field="${key}"]`);
    if (!select) return false;
    const selectedValue = select.value;
    const original = parseDraftOriginalValue(select.getAttribute("data-admin-edit-draft-original"));
    const options = getAdminDraftSelectOptions(key, original, domain);
    const filtered = filterAdminDraftSelectOptions(options, input.value, selectedValue);
    select.innerHTML = renderAdminDraftSelectOptionsHtml(filtered, selectedValue);
    select.value = selectedValue;
    updateAdminRelationOptionMeta(wrapper.querySelector("[data-admin-relation-option-meta]"), key, domain, input.value);
    return true;
  }

  function clearAdminRelationOptionFilter(key) {
    const filter = document.querySelector(`[data-admin-relation-option-filter-for="${key}"]`);
    if (!filter) return false;
    filter.value = "";
    return applyAdminRelationOptionFilter(filter);
  }

  function refreshDependentAdminRelationSelects(changedKey) {
    const draft = document.querySelector("[data-admin-edit-draft]");
    if (!draft) return false;
    const domain = draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN;
    const changed = normalizeAdminDraftFieldKey(changedKey);
    let touched = false;
    getAdminRelationEditOptionDefinitions(domain).forEach((definition) => {
      if (!definition || normalizeAdminDraftFieldKey(definition.dependsOn) !== changed) return;
      const fieldName = definition.field;
      const field = draft.querySelector(`[data-admin-edit-draft-field="${fieldName}"]`);
      if (!field) return;
      const previousValue = field.value;
      const options = getAdminDraftRelationOptions(definition) || [];
      let nextValue = "";
      if (options.some((option) => String(option.value) === previousValue)) {
        nextValue = previousValue;
      } else if (options.length) {
        nextValue = String(options[0].value ?? "");
      }
      const wrapper = field.closest("[data-admin-relation-select-tools]");
      const filter = wrapper ? wrapper.querySelector("[data-admin-relation-option-filter]") : null;
      if (filter) filter.value = "";
      field.innerHTML = renderAdminDraftSelectOptionsHtml(options, nextValue);
      field.value = nextValue;
      updateAdminRelationOptionMeta(wrapper && wrapper.querySelector("[data-admin-relation-option-meta]"), fieldName, domain, "");
      touched = true;
    });
    return touched;
  }

  function getAdminDraftFieldInputKind(field, domain) {
    const key = normalizeAdminDraftFieldKey(field && field.key);
    const value = field ? field.value : null;
    const valueText = value === null || value === undefined ? "" : String(value);
    const isLongText = valueText.length > 90 || valueText.includes("\n");
    if (isAdminRelationEditField(domain, key)) return "relation-select";
    if (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[key]) return "preset-select";
    if (ADMIN_DRAFT_BOOLEAN_FIELDS.has(key) || typeof value === "boolean") return "boolean-select";
    if (ADMIN_DRAFT_NUMBER_FIELDS.has(key) || typeof value === "number") return "number";
    if (ADMIN_DRAFT_TEXTAREA_FIELDS.has(key) || isLongText) return "textarea";
    return "text";
  }

  function getAdminDraftFieldTypeLabel(kind) {
    if (kind === "boolean-select") return "true/false select";
    if (kind === "preset-select") return "preset select";
    if (kind === "relation-select") return "relation select";
    if (kind === "number") return "number input";
    if (kind === "textarea") return "textarea";
    return "text input";
  }

  function getAdminDraftLockedReason(key) {
    const normalized = normalizeAdminDraftFieldKey(key);
    if (normalized === "id" || normalized === "code") return "식별자 필드라 잠금";
    if (normalized.endsWith("_id") || normalized.endsWith("_code")) return "관계/연결 필드라 잠금";
    if (normalized.endsWith("_json")) return "JSON 원본 필드는 아직 편집 막음";
    if (normalized === "created_at" || normalized === "updated_at" || normalized === "createdat" || normalized === "updatedat") return "자동 시간 필드라 잠금";
    return "allow-list 밖이라 잠금";
  }

  function renderAdminDraftTypeBadge(kind) {
    const label = getAdminDraftFieldTypeLabel(kind);
    const tone = kind === "boolean-select" || kind === "preset-select" ? "good" : (kind === "relation-select" || kind === "number" ? "warn" : "");
    return `<span class="pill ${escapeHtml(tone)}">${escapeHtml(label)}</span>`;
  }

  function getAdminDraftFieldRisk(domain, key) {
    const rawDomain = String(domain || "");
    const normalized = normalizeAdminDraftFieldKey(key).replace(/_/g, "");
    if (rawDomain === "itemTemplates" && ["stackable", "itemtype", "equipslot", "enhancegroupcode"].includes(normalized)) return "high";
    if (rawDomain === "bosses" && ["hp", "isenabled"].includes(normalized)) return "high";
    if (rawDomain === "skills" && ["slotkey", "procrate", "cooldownseconds"].includes(normalized)) return "high";
    if (rawDomain === "skillLevels" && ["skillcode", "level", "damagemultiplier", "procratebonus"].includes(normalized)) return "high";
    if (rawDomain === "dropTables" && ["ownertype", "ownercode"].includes(normalized)) return "high";
    if (rawDomain === "dropTableItems" && ["droptablecode", "itemtemplatecode", "rate", "minquantity", "maxquantity"].includes(normalized)) return "high";
    if (rawDomain === "enhancementLevels" && ["groupcode", "fromlevel", "successrate", "goldcost"].includes(normalized)) return "high";
    if (rawDomain === "characterSkills" && ["charactercode", "skillcode"].includes(normalized)) return "high";
    if (["grade", "bosstype", "ownertype", "tier", "sortorder", "enemyhp", "goldreward", "maxlevel", "tolevel", "isdefault"].includes(normalized)) return "medium";
    if (["adminnote", "description"].includes(normalized)) return "low";
    return "medium";
  }

  function renderAdminDraftRiskBadge(domain, key) {
    const risk = getAdminDraftFieldRisk(domain, key);
    const tone = risk === "high" ? "blocked" : (risk === "medium" ? "warn" : "good");
    return `<span class="pill ${escapeHtml(tone)}">risk ${escapeHtml(risk)}</span>`;
  }

  function renderAdminDraftLockedFields(lockedFields) {
    const safeFields = Array.isArray(lockedFields) ? lockedFields : [];
    if (!safeFields.length) return "";
    const visibleFields = safeFields.slice(0, ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT);
    const hiddenCount = Math.max(0, safeFields.length - visibleFields.length);
    return `
      <div class="locked-field-panel" data-admin-edit-locked-fields>
        <div class="locked-field-title">
          <span>읽기 전용/잠금 필드</span>
          <span class="pill blocked">수정 불가 ${escapeHtml(formatValue(safeFields.length))}</span>
        </div>
        <div class="filter-help">아래 필드는 화면에 보이지만 실수 방지를 위해 입력칸을 만들지 않았습니다. 코드/연결값/JSON/시간값은 아직 관리자에서 직접 수정하지 않는 쪽이 안전합니다.</div>
        <div class="locked-field-grid">
          ${visibleFields.map((field) => {
            const reason = getAdminDraftLockedReason(field.key);
            return `
              <div class="locked-field-card">
                <strong>${escapeHtml(field.label || field.key)}</strong>
                <span>${escapeHtml(formatValue(field.value))}</span>
                <em>${escapeHtml(reason)}</em>
              </div>
            `;
          }).join("")}
        </div>
        ${hiddenCount ? `<div class="filter-help">잠금 필드 ${escapeHtml(formatValue(hiddenCount))}개는 너무 많아서 일부만 표시했습니다.</div>` : ""}
      </div>
    `;
  }

  function makeDraftOriginalValue(value) {
    try {
      return JSON.stringify(value);
    } catch (error) {
      return JSON.stringify(formatValue(value));
    }
  }

  function parseDraftOriginalValue(value) {
    try {
      return JSON.parse(value || "null");
    } catch (error) {
      return value;
    }
  }

  function renderAdminDraftControl(field, kind, domain) {
    const value = field ? field.value : null;
    const valueText = value === null || value === undefined ? "" : String(value);
    const original = makeDraftOriginalValue(value);
    const key = field ? field.key : "";
    const commonAttrs = `data-admin-edit-draft-field="${escapeHtml(key)}" data-admin-edit-draft-original="${escapeHtml(original)}"`;
    if (kind === "boolean-select") {
      const normalized = value === true || String(value).toLowerCase() === "true" ? "true" : "false";
      return `
        <select ${commonAttrs} data-admin-edit-draft-value-type="boolean" aria-label="${escapeHtml(field.label || key)} true false 선택">
          <option value="true" ${normalized === "true" ? "selected" : ""}>true · 켜짐</option>
          <option value="false" ${normalized === "false" ? "selected" : ""}>false · 꺼짐</option>
        </select>
      `;
    }
    if (kind === "preset-select") {
      const options = getAdminDraftSelectOptions(key, value, domain);
      return `
        <select ${commonAttrs} data-admin-edit-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
          ${renderAdminDraftSelectOptionsHtml(options, valueText)}
        </select>
      `;
    }
    if (kind === "relation-select") {
      const options = getAdminDraftSelectOptions(key, value, domain);
      const definition = getAdminRelationEditOptionDefinition(domain, key) || {};
      const metaText = getAdminRelationSelectMetaText(key, domain, "");
      return `
        <div class="relation-select-tools" data-admin-relation-select-tools>
          <input class="relation-option-filter" data-admin-relation-option-filter data-admin-relation-option-filter-for="${escapeHtml(key)}" type="text" placeholder="코드/이름으로 후보 검색" autocomplete="off" aria-label="${escapeHtml(field.label || key)} 후보 검색" />
          <select ${commonAttrs} data-admin-edit-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
            ${renderAdminDraftSelectOptionsHtml(options, valueText)}
          </select>
          <div class="relation-option-meta" data-admin-relation-option-meta>${escapeHtml(metaText || (definition.targetLabel ? `${definition.targetLabel} 후보` : "관계 후보"))}</div>
        </div>
      `;
    }
    if (kind === "number") {
      return `<input type="number" inputmode="decimal" step="any" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-edit-draft-value-type="number" />`;
    }
    if (kind === "textarea") {
      const rows = ADMIN_DRAFT_TEXTAREA_FIELDS.has(normalizeAdminDraftFieldKey(key)) ? 4 : 3;
      return `<textarea rows="${rows}" ${commonAttrs} data-admin-edit-draft-value-type="text">${escapeHtml(valueText)}</textarea>`;
    }
    return `<input type="text" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-edit-draft-value-type="text" />`;
  }

  function getAdminRelationComboGuardLabels(domain) {
    return getAdminRelationEditOptionDefinitions(domain)
      .filter((definition) => definition && definition.allowApply && Array.isArray(definition.comboGuard) && definition.comboGuard.length)
      .map((definition) => definition.comboGuard.join(" + "))
      .filter((value, index, list) => value && list.indexOf(value) === index);
  }

  function renderAdminRelationEditOptionsNote(domain) {
    const definitions = getAdminRelationEditOptionDefinitions(domain).filter((definition) => definition && definition.allowApply);
    if (!definitions.length) return "";
    const labels = definitions.map((definition) => `${definition.field} → ${definition.targetLabel || definition.targetDomain || "대상"}`).join(", ");
    const comboLabels = getAdminRelationComboGuardLabels(domain);
    const comboLine = comboLabels.length ? `<br><span><strong>중복 조합 검사:</strong> ${escapeHtml(comboLabels.join(", "))}</span>` : "";
    return `<div class="relation-edit-note"><span class="pill warn">relation select</span> ${escapeHtml(labels)}<br><span>${escapeHtml("관계 필드는 직접 텍스트 입력이 아니라 실제 존재하는 대상 목록에서 선택하고, 백엔드가 적용 직전에 대상 존재 여부를 다시 검사합니다.")}</span>${comboLine}</div>`;
  }

  function renderMasterEditDraft(detail, fields) {
    const safeFields = Array.isArray(fields) ? fields : [];
    const domain = detail && detail.domain ? detail.domain : DEFAULT_MASTER_DOMAIN;
    const candidateFields = safeFields.filter((field) => !fieldKeyLooksReadOnly(domain, field.key));
    const editableCandidateFields = candidateFields.filter((field) => isAdminEditApplyAllowedField(domain, field.key));
    const editableFields = editableCandidateFields.slice(0, 14);
    const lockedFields = candidateFields.filter((field) => !isAdminEditApplyAllowedField(domain, field.key));
    const editableOverflowCount = Math.max(0, editableCandidateFields.length - editableFields.length);
    const rows = editableFields.length ? editableFields.map((field) => {
      const value = field.value;
      const kind = getAdminDraftFieldInputKind(field, domain);
      const label = field.label || field.key;
      return `
        <label class="draft-field draft-field-${escapeHtml(kind)}">
          <span class="draft-field-heading">
            <span>${escapeHtml(label)}${renderFieldHelpBadge(field.key)}</span>
            <span class="draft-field-badges">${renderAdminDraftTypeBadge(kind)}${renderAdminDraftRiskBadge(domain, field.key)}</span>
          </span>
          ${renderFieldHelpInline(field.key)}
          ${renderFieldValueHintInline(field.key, value)}
          ${renderAdminDraftControl(field, kind, domain)}
        </label>
      `;
    }).join("") : `<div class="empty">이 도메인에서 실제 적용까지 열어둔 일반 필드가 없습니다.</div>`;

    return `
      <div class="detail-card edit-draft-card" data-admin-edit-draft data-admin-edit-draft-domain="${escapeHtml(domain || "")}" data-admin-edit-draft-id="${escapeHtml(detail.id || "")}">
        <div class="detail-title">관리자 편집 초안 <span class="pill warn">guarded apply</span><span class="pill good">typed inputs</span><span class="pill good">change log</span></div>
        <div class="filter-help">allow-list 필드는 실제 DB 적용까지 가능합니다. 입력 실수를 줄이기 위해 boolean은 <strong>true/false select</strong>, enum 성격 필드는 <strong>preset select</strong>, number는 <strong>number input</strong>, description/admin_note는 <strong>textarea</strong>로 표시합니다.</div>
        <div class="filter-help">먼저 <strong>초안 검증</strong>으로 오류가 없는지 확인한 뒤, dev key와 확인 문구 <code>${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}</code>를 정확히 입력해야 적용됩니다. 적용 직전에는 편집 화면을 열었을 때의 기준값과 현재 DB 값이 같은지도 한 번 더 검사합니다.</div>
        <div class="filter-help">실제 적용 가능 필드: ${escapeHtml(getAdminEditAllowedFields(domain).join(", ") || "없음")}</div>
        ${renderAdminRelationEditOptionsNote(domain)}
        <div class="edit-draft-grid">${rows}</div>
        ${editableOverflowCount ? `<div class="filter-help">표시 제한으로 실제 적용 가능 필드 ${escapeHtml(formatValue(editableOverflowCount))}개는 편집 초안에서 제외했습니다.</div>` : ""}
        ${renderAdminDraftLockedFields(lockedFields)}
        <div class="edit-draft-review" data-admin-edit-review>
          <div class="draft-review-banner draft-review-empty">
            <span class="pill good">변경 0</span>
            <span>값을 바꾸면 적용 직전 비교표가 여기에 표시됩니다.</span>
          </div>
        </div>
        <div class="edit-draft-impact" data-admin-edit-impact><div class="empty">값을 바꾸면 여기에 <strong>인게임 영향 안내</strong>가 표시됩니다.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-edit-draft">초안 검증</button>
          <button class="btn mini" type="button" data-admin-action="reset-admin-edit-draft">원래 값으로 되돌리기</button>
          <label class="apply-confirm-field"><span>확인 문구</span><input type="text" data-admin-edit-apply-confirm placeholder="${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>고위험 확인</span><input type="text" data-admin-edit-risk-confirm placeholder="${escapeHtml(ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>변경 사유</span><input type="text" data-admin-edit-apply-reason placeholder="예: 보스 HP 밸런스 조정" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-edit-draft">검증 후 실제 적용</button>
          <span class="pill warn">DB write: dev-key guarded</span>
          <span class="pill good">stale guard</span>
        </div>
        <div class="edit-draft-result" data-admin-edit-draft-result><div class="empty">값을 바꾼 뒤 <strong>초안 검증</strong>을 누르세요. 실제 적용은 확인 문구가 맞고 검증 오류가 없을 때만 됩니다.</div></div>
      </div>
    `;
  }

  function readAdminEditDraftValues() {
    const draft = $(`[data-admin-edit-draft]`);
    if (!draft) return { ok: false, reason: "draft_missing", draft: {} };
    const fields = Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]"));
    const values = {};
    const originals = {};
    fields.forEach((field) => {
      const key = field.getAttribute("data-admin-edit-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-edit-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-edit-draft-original"));
      originals[key] = original;
      if (type === "boolean") values[key] = field.value === "true";
      else values[key] = field.value;
    });
    return {
      ok: true,
      domain: draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN,
      id: Number(draft.getAttribute("data-admin-edit-draft-id") || 0),
      draft: values,
      originals,
      fieldCount: fields.length,
    };
  }

  function resetAdminEditDraft() {
    const draft = $(`[data-admin-edit-draft]`);
    if (!draft) return false;
    Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]")).forEach((field) => {
      const type = field.getAttribute("data-admin-edit-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-edit-draft-original"));
      if (type === "boolean") field.value = original ? "true" : "false";
      else field.value = original === null || original === undefined ? "" : String(original);
    });
    const riskConfirm = $(`[data-admin-edit-risk-confirm]`);
    if (riskConfirm) riskConfirm.value = "";
    const result = $(`[data-admin-edit-draft-result]`);
    if (result) result.innerHTML = `<div class="empty">원래 값으로 되돌렸습니다. 값을 바꾼 뒤 초안 검증을 누르세요.</div>`;
    refreshAdminEditReviewAndImpact();
    setStatus("편집 초안을 원래 값으로 되돌렸습니다.", "ok");
    return true;
  }

  function valuesEqualForImpact(before, after) {
    if (before === after) return true;
    if (before === null || before === undefined) return after === "" || after === null || after === undefined;
    if (typeof before === "number") return Number(after) === before;
    if (typeof before === "boolean") return after === before || String(after).toLowerCase() === String(before);
    return String(before) === String(after);
  }

  function collectLocalDraftChangesForImpact(values) {
    const result = values || readAdminEditDraftValues();
    if (!result || !result.ok) return [];
    return Object.keys(result.draft || {}).filter((key) => !valuesEqualForImpact(result.originals[key], result.draft[key])).map((key) => ({
      key,
      label: key,
      before: result.originals[key],
      after: result.draft[key],
      domain: result.domain,
    }));
  }

  function getAdminRiskSortWeight(risk) {
    if (risk === "high") return 0;
    if (risk === "medium") return 1;
    if (risk === "low") return 2;
    return 3;
  }

  function sortAdminChangesByRisk(domain, changes) {
    return (Array.isArray(changes) ? changes.slice() : []).sort((a, b) => {
      const riskA = getAdminDraftFieldRisk(domain || a.domain, a.key);
      const riskB = getAdminDraftFieldRisk(domain || b.domain, b.key);
      const riskDiff = getAdminRiskSortWeight(riskA) - getAdminRiskSortWeight(riskB);
      if (riskDiff) return riskDiff;
      return String(a.key || "").localeCompare(String(b.key || ""));
    });
  }

  function getAdminRelationOptionDisplayText(option, value) {
    const valueText = value === null || value === undefined ? "" : String(value);
    if (!option) return formatValue(value);
    const label = String(option.label || option.targetLabel || option.value || valueText || "");
    if (!valueText) return label || "-";
    if (label === valueText || label.startsWith(`${valueText} ·`)) return label;
    return `${valueText} · ${label}`;
  }

  function getAdminRelationValueDisplay(domain, key, value, contextValues) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return formatValue(value);
    const valueText = value === null || value === undefined ? "" : String(value);
    const options = getAdminDraftRelationOptionsForValues(definition, contextValues || {}) || [];
    const option = options.find((candidate) => String(candidate.value ?? "") === valueText);
    return getAdminRelationOptionDisplayText(option, value);
  }

  function getAdminRelationOpenTarget(domain, key, value, contextValues) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return null;
    const valueText = value === null || value === undefined ? "" : String(value).trim();
    if (!valueText) return null;
    if (domain === "dropTables" && key === "owner_type") return null;
    let targetDomain = definition.targetDomain || "";
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyValue = contextValues && Object.prototype.hasOwnProperty.call(contextValues, definition.dependsOn) ? String(contextValues[definition.dependsOn] || "") : getAdminDraftRelationOptionGroupKey(definition);
      if (domain === "dropTables" && key === "owner_code") targetDomain = dependencyValue === "field" ? "fieldZones" : "bosses";
    }
    if (!targetDomain || targetDomain.includes("/")) return null;
    return { domain: targetDomain, code: valueText };
  }

  function renderAdminRelationOpenButton(domain, key, value, contextValues) {
    const target = getAdminRelationOpenTarget(domain, key, value, contextValues);
    if (!target) return "";
    return `<button class="btn mini relation-jump-btn" type="button" data-admin-action="open-master-detail-by-code" data-admin-detail-domain="${escapeHtml(target.domain)}" data-admin-detail-code="${escapeHtml(target.code)}">대상 열기</button>`;
  }

  function getAdminChangeRelationInfo(change, side) {
    const relation = change && change.relation ? change.relation : null;
    if (!relation) return null;
    if (side && relation[side]) return relation[side];
    if (side === "after" && (relation.targetLabel || relation.targetDomain || relation.targetCode)) return relation;
    return null;
  }

  function formatAdminRelationInfoText(info, rawValue) {
    if (!info) return null;
    if (info.displayText !== undefined && info.displayText !== null && String(info.displayText) !== "") return String(info.displayText);
    const valueText = formatValue(rawValue);
    const label = info.targetLabel !== undefined && info.targetLabel !== null ? String(info.targetLabel) : "";
    if (!label || label === valueText) return valueText;
    return `${valueText} · ${label}`;
  }

  function getAdminRelationOpenTargetFromChange(domain, key, rawValue, contextValues, change, side) {
    if (domain === "dropTables" && key === "owner_type") return null;
    const info = getAdminChangeRelationInfo(change, side);
    if (info && info.targetDomain && !String(info.targetDomain).includes("/")) {
      const code = info.targetCode !== undefined && info.targetCode !== null ? String(info.targetCode).trim() : String(rawValue || "").trim();
      if (code) return { domain: String(info.targetDomain), code };
    }
    return isAdminRelationEditField(domain, key) ? getAdminRelationOpenTarget(domain, key, rawValue, contextValues) : null;
  }

  function renderAdminRelationOpenTargetButton(target) {
    if (!target) return "";
    return `<button class="btn mini relation-jump-btn" type="button" data-admin-action="open-master-detail-by-code" data-admin-detail-domain="${escapeHtml(target.domain)}" data-admin-detail-code="${escapeHtml(target.code)}">대상 열기</button>`;
  }

  function formatAdminChangeValueText(domain, change, side, contextValues) {
    const key = change && change.key;
    const rawValue = side === "before" ? change && change.before : change && change.after;
    const relationText = formatAdminRelationInfoText(getAdminChangeRelationInfo(change, side), rawValue);
    if (relationText !== null) return relationText;
    if (isAdminRelationEditField(domain, key)) return getAdminRelationValueDisplay(domain, key, rawValue, contextValues);
    return formatValue(rawValue);
  }

  function renderAdminChangeValueCell(domain, change, side, contextValues) {
    const text = formatAdminChangeValueText(domain, change, side, contextValues);
    const key = change && change.key;
    const rawValue = side === "before" ? change && change.before : change && change.after;
    const target = getAdminRelationOpenTargetFromChange(domain, key, rawValue, contextValues, change, side);
    const button = renderAdminRelationOpenTargetButton(target);
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${button}</div>`;
  }

  function renderAdminRollbackMismatchValueCell(domain, item, valueKey) {
    const relation = item && item.relation ? item.relation : null;
    const rawValue = item ? item[valueKey] : undefined;
    const info = relation && relation[valueKey] ? relation[valueKey] : null;
    const text = formatAdminRelationInfoText(info, rawValue) || formatValue(rawValue);
    const target = info && info.targetDomain && !String(info.targetDomain).includes("/") && info.targetCode ? { domain: String(info.targetDomain), code: String(info.targetCode) } : null;
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${renderAdminRelationOpenTargetButton(target)}</div>`;
  }

  function formatAdminChangeAfterValue(change) {
    return formatAdminChangeValueText(change && change.domain, change, "after", change || {});
  }


  function buildAdminEditDraftReview(values) {
    const result = values || readAdminEditDraftValues();
    if (!result || !result.ok) {
      return { ok: false, domain: DEFAULT_MASTER_DOMAIN, changes: [], changeCount: 0, highCount: 0, mediumCount: 0, lowCount: 0 };
    }
    const changes = sortAdminChangesByRisk(result.domain, collectLocalDraftChangesForImpact(result)).map((change) => {
      const risk = getAdminDraftFieldRisk(result.domain, change.key);
      const relation = isAdminRelationEditField(result.domain, change.key);
      return { ...change, risk, relation };
    });
    return {
      ok: true,
      version: VERSION,
      domain: result.domain,
      id: result.id,
      changes,
      changeCount: changes.length,
      relationCount: changes.filter((change) => change.relation).length,
      highCount: changes.filter((change) => change.risk === "high").length,
      mediumCount: changes.filter((change) => change.risk === "medium").length,
      lowCount: changes.filter((change) => change.risk === "low").length,
    };
  }

  function renderAdminEditDraftReview(review) {
    const target = $(`[data-admin-edit-review]`);
    if (!target) return;
    const info = review || buildAdminEditDraftReview();
    if (!info.changeCount) {
      target.innerHTML = `
        <div class="draft-review-banner draft-review-empty">
          <span class="pill good">변경 0</span>
          <span>값을 바꾸면 적용 직전 비교표가 여기에 표시됩니다.</span>
        </div>
      `;
      return;
    }
    const rows = info.changes.map((change) => {
      const beforeContext = { ...Object.fromEntries(info.changes.map((item) => [item.key, item.before])), [change.key]: change.before };
      const afterContext = { ...Object.fromEntries(info.changes.map((item) => [item.key, item.after])), [change.key]: change.after };
      return `
        <tr class="draft-review-row-${escapeHtml(change.risk)}">
          <td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td>
          <td><span class="pill ${change.risk === "high" ? "blocked" : (change.risk === "medium" ? "warn" : "good")}">${escapeHtml(change.risk)}</span></td>
          <td>${renderAdminChangeValueCell(info.domain, change, "before", beforeContext)}</td>
          <td>${renderAdminChangeValueCell(info.domain, change, "after", afterContext)}</td>
        </tr>
      `;
    }).join("");
    target.innerHTML = `
      <div class="draft-review-banner ${info.highCount ? "draft-review-danger" : ""}">
        <span class="pill ${info.highCount ? "blocked" : "good"}">변경 ${escapeHtml(formatValue(info.changeCount))}</span>
        <span class="pill ${info.highCount ? "blocked" : "good"}">high ${escapeHtml(formatValue(info.highCount))}</span>
        <span class="pill ${info.mediumCount ? "warn" : "good"}">medium ${escapeHtml(formatValue(info.mediumCount))}</span>
        <span class="pill good">low ${escapeHtml(formatValue(info.lowCount))}</span>
        <span class="pill ${info.relationCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(info.relationCount || 0))}</span>
        ${info.highCount ? `<span class="pill blocked">고위험 변경은 ${escapeHtml(ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT)} 추가 입력 필요</span>` : ""}
      </div>
      <div class="table-wrap relation-table-wrap draft-review-table-wrap">
        <table>
          <thead><tr><th>필드</th><th>위험도</th><th>현재 기준값</th><th>초안 값</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function refreshAdminEditReviewAndImpact() {
    const values = readAdminEditDraftValues();
    if (!values.ok) return null;
    const review = buildAdminEditDraftReview(values);
    renderAdminEditDraftReview(review);
    const guide = buildAdminEditImpactGuide(values.domain, review.changes);
    renderAdminEditImpactGuide(guide);
    return { review, guide };
  }

  function normalizeImpactKey(key) {
    return String(key || "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
  }

  function getAdminEditImpactHint(domain, change) {
    const key = normalizeImpactKey(change && change.key);
    const rawDomain = String(domain || (change && change.domain) || "");
    const before = change ? change.before : undefined;
    const after = change ? change.after : undefined;
    if (!key) return null;

    if (rawDomain === "itemTemplates" && key === "stackable") {
      return {
        severity: "high",
        title: "인벤토리 겹치기 동작 변경",
        body: `stackable ${formatValue(before)} → ${formatValue(after)} 변경은 새로 획득하는 같은 +0 아이템의 겹치기 여부에 영향을 줍니다. 기존 세이브에 이미 따로 들어간 아이템은 자동 병합하지 않습니다. 겹친 장비를 강화할 때는 1개 분리용 빈 칸이 필요합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && ["itemtype", "equipslot"].includes(key)) {
      return {
        severity: "high",
        title: "아이템 분류/장착 슬롯 변경",
        body: `${change.label || change.key} 변경은 인벤토리 분류, 장착 위치, 드랍 표시, 향후 강화/필터 규칙에 영향을 줄 수 있습니다. 변경 후 신규 획득/장착/툴팁을 꼭 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && key === "enhancegroupcode") {
      return {
        severity: "high",
        title: "아이템 강화 그룹 연결 변경",
        body: `enhance_group_code ${formatValue(before)} → ${formatValue(after)} 변경은 이 아이템이 사용하는 강화 확률/비용/결과 단계에 직접 영향을 줍니다. 적용 전 연결 항목에서 강화 그룹과 단계를 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && ["name", "description", "grade"].includes(key)) {
      return {
        severity: "medium",
        title: "아이템 표시/구간 정보 변경",
        body: `${change.label || change.key} 변경은 드랍 목록, 툴팁, 관리자 목록, 일부 정렬/구간 판단에 영향을 줄 수 있습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && key === "adminnote") {
      return {
        severity: "low",
        title: "관리자 메모만 변경",
        body: "admin_note는 게임 화면에는 표시되지 않는 내부 메모입니다. 인게임 밸런스에는 직접 영향이 없습니다.",
        reload: false,
      };
    }

    if (rawDomain === "bosses" && key === "hp") {
      return {
        severity: "high",
        title: "보스 체력 변경",
        body: `보스 HP ${formatValue(before)} → ${formatValue(after)} 변경은 보스 전투의 최대 체력에 직접 반영됩니다. 이미 떠 있는 게임 화면은 새로고침 후 최신 값을 읽습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "bosses" && ["name", "description", "boss_type", "tier", "cooldown_seconds"].includes(key)) {
      return {
        severity: "medium",
        title: "보스 표시/소환 규칙 변경",
        body: `${change.label || change.key} 변경은 보스 카드, 전투 표시, 쿨타임/구간 정보에 영향을 줄 수 있습니다. 적용 후 게임 새로고침을 권장합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "bosses" && key === "isenabled") {
      return {
        severity: "high",
        title: "보스 활성 상태 변경",
        body: "is_enabled 변경은 보스가 게임 기준 데이터에 포함되는지 여부에 영향을 줄 수 있습니다. 비활성화 전에는 드랍/퀘스트 연결 상태를 확인하는 편이 안전합니다.",
        reload: true,
      };
    }

    if (rawDomain === "fieldZones" && ["enemyhp", "goldreward"].includes(key)) {
      return {
        severity: "high",
        title: "필드 사냥 보상/난이도 변경",
        body: `${change.label || change.key} 변경은 필드 몬스터 체력 또는 골드 보상에 직접 영향을 줍니다. 게임 새로고침 후 적용됩니다.`,
        reload: true,
      };
    }
    if (rawDomain === "fieldZones" && ["name", "description", "sortorder", "isenabled"].includes(key)) {
      return {
        severity: "medium",
        title: "필드 표시/노출 변경",
        body: `${change.label || change.key} 변경은 필드 목록 표시와 진입 가능 상태에 영향을 줄 수 있습니다.`,
        reload: true,
      };
    }

    if (rawDomain === "skills" && key === "slotkey") {
      return {
        severity: "high",
        title: "스킬 슬롯 배치 변경",
        body: "slot_key 변경은 Q/W/E/R/T/F/D/M 또는 각성 슬롯 배치에 영향을 줍니다. 같은 슬롯이 중복되지 않는지, 게임 화면에서 스킬 버튼이 의도대로 보이는지 확인해야 합니다.",
        reload: true,
      };
    }
    if (rawDomain === "skills" && ["procrate", "cooldownseconds"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 발동/쿨타임 변경",
        body: `${change.label || change.key} 변경은 전투 스킬 발동 확률 또는 쿨타임에 영향을 줍니다. 게임 새로고침 후 최신 master-data가 적용됩니다.`,
        reload: true,
      };
    }
    if (rawDomain === "skillLevels" && ["skillcode", "level"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 레벨 조합 변경",
        body: `${change.label || change.key} 변경은 어떤 스킬의 몇 레벨 규칙인지 바꿉니다. 백엔드가 skill_code + level 중복을 차단하지만, 적용 후 스킬 강화 화면을 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "skillLevels" && ["damagemultiplier", "procratebonus"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 레벨 효과 변경",
        body: `${change.label || change.key} 변경은 스킬 레벨별 피해량/발동 보너스에 영향을 줍니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && key === "droptablecode") {
      return {
        severity: "high",
        title: "드랍 테이블 연결 변경",
        body: `drop_table_code ${formatValue(before)} → ${formatValue(after)} 변경은 이 드랍 아이템 행이 어느 보스/필드 드랍 묶음에 속하는지 바꿉니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && key === "itemtemplatecode") {
      return {
        severity: "high",
        title: "드랍 아이템 연결 변경",
        body: `item_template_code ${formatValue(before)} → ${formatValue(after)} 변경은 해당 드랍 테이블에서 실제로 떨어지는 아이템을 바꿉니다. 확률/수량과 함께 게임 드랍 결과를 꼭 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && ["rate", "minquantity", "maxquantity"].includes(key)) {
      return {
        severity: "high",
        title: "드랍 확률/수량 변경",
        body: `${change.label || change.key} 변경은 보스/필드 드랍 결과에 직접 영향을 줍니다. 너무 높은 rate나 수량은 밸런스가 크게 바뀔 수 있습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTables" && key === "ownertype") {
      return {
        severity: "high",
        title: "드랍 테이블 대상 종류 변경",
        body: "owner_type 변경은 같은 owner_code를 보스 코드로 볼지 필드 코드로 볼지 바꿉니다. owner_code 후보 목록이 타입에 맞게 자동 전환되고, 백엔드가 존재 여부를 다시 검사합니다.",
        reload: true,
      };
    }
    if (rawDomain === "dropTables" && key === "ownercode") {
      return {
        severity: "high",
        title: "드랍 테이블 소유자 변경",
        body: "owner_code를 바꾸면 이 드랍 테이블이 연결되는 보스/필드가 바뀝니다. 적용 후 관계 보기에서 대상 보스/필드를 확인하세요.",
        reload: true,
      };
    }
    if (rawDomain === "enhancementLevels" && ["groupcode", "fromlevel"].includes(key)) {
      return {
        severity: "high",
        title: "강화 단계 조합 변경",
        body: `${change.label || change.key} 변경은 어떤 강화 그룹의 어느 단계 규칙인지 바꿉니다. 백엔드가 group_code + from_level 중복을 차단하지만, 적용 후 강화 단계 관계를 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "enhancementLevels" && ["successrate", "goldcost"].includes(key)) {
      return {
        severity: "high",
        title: "강화 확률/비용 변경",
        body: `${change.label || change.key} 변경은 강화 난이도와 골드 소모량에 직접 영향을 줍니다.`,
        reload: true,
      };
    }
    if (rawDomain === "characterSkills" && ["charactercode", "skillcode"].includes(key)) {
      return {
        severity: "high",
        title: "캐릭터 스킬 연결 변경",
        body: `${change.label || change.key} 변경은 캐릭터가 어떤 스킬을 기본 연결로 갖는지 바꿉니다. 백엔드가 character_code + skill_code 중복을 차단합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "enhancementGroups" && ["name", "description", "maxlevel", "isenabled"].includes(key)) {
      return {
        severity: "medium",
        title: "강화 그룹 설정 변경",
        body: `${change.label || change.key} 변경은 해당 그룹을 쓰는 장비들의 강화 표시/최대 단계에 영향을 줄 수 있습니다.`,
        reload: true,
      };
    }
    if (["name", "description", "isenabled"].includes(key)) {
      return {
        severity: key === "isenabled" ? "medium" : "low",
        title: "표시/활성 상태 변경",
        body: `${change.label || change.key} 변경은 화면 표시 또는 데이터 활성 상태에 영향을 줄 수 있습니다.`,
        reload: key === "isenabled",
      };
    }
    return {
      severity: "low",
      title: "일반 마스터 데이터 변경",
      body: `${change.label || change.key} 값이 변경됩니다. 인게임 반영은 이 필드를 사용하는 화면/시스템에서 새로고침 후 확인하세요.`,
      reload: true,
    };
  }

  function buildAdminEditImpactGuide(domain, changes, options) {
    const safeChanges = Array.isArray(changes) ? changes : [];
    const hints = safeChanges.map((change) => getAdminEditImpactHint(domain, change)).filter(Boolean);
    const requiresGameReload = hints.some((hint) => hint.reload);
    const highCount = hints.filter((hint) => hint.severity === "high").length;
    const mediumCount = hints.filter((hint) => hint.severity === "medium").length;
    return {
      ok: true,
      version: VERSION,
      domain: domain || DEFAULT_MASTER_DOMAIN,
      changeCount: safeChanges.length,
      hintCount: hints.length,
      highCount,
      mediumCount,
      requiresGameReload,
      applied: !!(options && options.applied),
      hints,
    };
  }

  function renderAdminEditImpactGuide(guide) {
    const target = $(`[data-admin-edit-impact]`);
    if (!target) return;
    const info = guide || buildAdminEditImpactGuide(DEFAULT_MASTER_DOMAIN, []);
    if (!info.changeCount) {
      target.innerHTML = `<div class="empty">값을 바꾸면 여기에 <strong>인게임 영향 안내</strong>가 표시됩니다.</div>`;
      return;
    }
    const rows = info.hints.map((hint) => `
      <div class="impact-row impact-${escapeHtml(hint.severity)}">
        <span class="pill ${hint.severity === "high" ? "blocked" : (hint.severity === "medium" ? "warn" : "good")}">${escapeHtml(hint.severity)}</span>
        <div><strong>${escapeHtml(hint.title)}</strong><br><span>${escapeHtml(hint.body)}</span></div>
      </div>
    `).join("");
    target.innerHTML = `
      <div class="impact-summary">
        <span class="pill ${info.requiresGameReload ? "warn" : "good"}">게임 새로고침 ${info.requiresGameReload ? "필요" : "불필요"}</span>
        <span class="pill">변경 ${escapeHtml(formatValue(info.changeCount))}</span>
        <span class="pill ${info.highCount ? "blocked" : "good"}">high ${escapeHtml(formatValue(info.highCount))}</span>
        <span class="pill ${info.mediumCount ? "warn" : "good"}">medium ${escapeHtml(formatValue(info.mediumCount))}</span>
      </div>
      ${rows}
      <div class="filter-help">이 안내는 저장 전 이해를 돕는 가이드입니다. 실제 저장 여부는 백엔드 검증과 확인 문구로 한 번 더 막습니다.</div>
    `;
  }

  function refreshAdminEditImpactGuide() {
    const state = refreshAdminEditReviewAndImpact();
    return state ? state.guide : null;
  }

  function renderAdminEditPreviewResult(preview) {
    const target = $(`[data-admin-edit-draft-result]`);
    if (!target) return;
    const payload = preview || {};
    const accepted = Array.isArray(payload.acceptedChanges) ? payload.acceptedChanges : [];
    const rejected = Array.isArray(payload.rejectedChanges) ? payload.rejectedChanges : [];
    const unchanged = Array.isArray(payload.unchangedChanges) ? payload.unchangedChanges : [];
    const stale = Array.isArray(payload.staleChanges) ? payload.staleChanges : [];
    const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
    const draftValuesForImpact = readAdminEditDraftValues();
    const acceptedForDisplay = sortAdminChangesByRisk(draftValuesForImpact.domain, accepted);
    const acceptedRows = acceptedForDisplay.length ? acceptedForDisplay.map((change) => {
      const risk = getAdminDraftFieldRisk(draftValuesForImpact.domain, change.key);
      const beforeContext = { ...(draftValuesForImpact.originals || {}), [change.key]: change.before };
      const afterContext = { ...(draftValuesForImpact.draft || {}), [change.key]: change.after };
      const relationBadge = isAdminRelationEditField(draftValuesForImpact.domain, change.key) ? ` <span class="pill warn">relation</span>` : "";
      return `
        <tr class="draft-review-row-${escapeHtml(risk)}"><td>${escapeHtml(change.label || change.key)}${relationBadge}</td><td><span class="pill ${risk === "high" ? "blocked" : (risk === "medium" ? "warn" : "good")}">${escapeHtml(risk)}</span></td><td>${renderAdminChangeValueCell(draftValuesForImpact.domain, change, "before", beforeContext)}</td><td>${renderAdminChangeValueCell(draftValuesForImpact.domain, change, "after", afterContext)}</td><td>${escapeHtml(change.type || "-")}</td></tr>
      `;
    }).join("") : `<tr><td colspan="5">변경된 값 없음</td></tr>`;
    const rejectedRows = rejected.length ? rejected.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.after))}</td><td>${escapeHtml(change.reason || "rejected")}</td></tr>
    `).join("") : `<tr><td colspan="3">오류 없음</td></tr>`;
    const staleRows = stale.length ? stale.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.base))}</td><td>${escapeHtml(formatValue(change.current))}</td><td>${escapeHtml(formatValue(change.after))}</td></tr>
    `).join("") : `<tr><td colspan="4">오래된 초안 아님</td></tr>`;
    const applied = payload.applied === true;
    const modeLabel = applied ? "applied" : (payload.dryRun ? "preview only" : "apply result");
    const impactChanges = accepted.length ? accepted.map((change) => ({ ...change, domain: draftValuesForImpact.domain })) : collectLocalDraftChangesForImpact(draftValuesForImpact);
    renderAdminEditDraftReview(buildAdminEditDraftReview(draftValuesForImpact));
    renderAdminEditImpactGuide(buildAdminEditImpactGuide(draftValuesForImpact.domain, impactChanges, { applied }));
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${payload.wouldBeValid ? "good" : "blocked"}">valid: ${escapeHtml(formatValue(payload.wouldBeValid))}</span>
        <span class="pill ${payload.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(payload.dryRun))}</span>
        <span class="pill ${payload.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(payload.writeBlocked))}</span>
        <span class="pill ${applied ? "good" : "warn"}">applied: ${escapeHtml(formatValue(applied))}</span>
        <span class="pill">diff ${escapeHtml(formatValue(payload.diffCount))}</span>
        <span class="pill">errors ${escapeHtml(formatValue(payload.errorCount))}</span>
        <span class="pill">unchanged ${escapeHtml(formatValue(payload.unchangedCount || unchanged.length))}</span>
        <span class="pill ${payload.staleGuardEnabled === false ? "warn" : "good"}">stale guard: ${escapeHtml(payload.staleGuardEnabled === false ? "off" : "on")}</span>
        <span class="pill ${stale.length ? "blocked" : "good"}">stale ${escapeHtml(formatValue(payload.staleCount || stale.length))}</span>
        ${payload.changeLogId ? `<span class="pill good">change log #${escapeHtml(formatValue(payload.changeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${payload.note ? `<div class="filter-help">${escapeHtml(payload.note)}</div>` : ""}
      ${renderUnifiedPreviewDiff(payload)}
      <details class="json-detail" open>
        <summary>변경 값 <span class="pill good">${escapeHtml(modeLabel)}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>위험도</th><th>이전 DB 값</th><th>적용/초안 값</th><th>타입</th></tr></thead><tbody>${acceptedRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${stale.length ? "open" : ""}>
        <summary>오래된 초안 검사 <span class="pill ${stale.length ? "blocked" : "good"}">${escapeHtml(formatValue(stale.length))}</span></summary>
        <div class="filter-help">편집 화면을 연 뒤 다른 변경이 먼저 적용됐다면, 이 초안은 최신 DB 값을 덮어쓸 수 있어서 차단됩니다. 이 경우 상세를 다시 열고 새 기준값으로 수정하세요.</div>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>화면 열 때 값</th><th>현재 DB 값</th><th>내 초안 값</th></tr></thead><tbody>${staleRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${rejected.length ? "open" : ""}>
        <summary>검증 오류 <span class="pill ${rejected.length ? "blocked" : "good"}">${escapeHtml(formatValue(rejected.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>사유</th></tr></thead><tbody>${rejectedRows}</tbody></table></div>
      </details>
      <div class="filter-help">${applied ? "DB에 적용했습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다." : "검증 결과입니다. 실제 적용은 확인 문구가 맞고 오류가 없을 때만 됩니다."}</div>
    `;
  }

  function readAdminEditApplyControls() {
    const confirmEl = $(`[data-admin-edit-apply-confirm]`);
    const riskConfirmEl = $(`[data-admin-edit-risk-confirm]`);
    const reasonEl = $(`[data-admin-edit-apply-reason]`);
    return {
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      riskConfirmText: riskConfirmEl ? riskConfirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      highRiskConfirmRequired: buildAdminEditDraftReview().highCount > 0,
      highRiskConfirmMatches: !!riskConfirmEl && riskConfirmEl.value.trim() === ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT,
    };
  }

  async function previewAdminEditDraft(options) {
    ensureApi();
    const values = readAdminEditDraftValues();
    if (!values.ok || !values.id) {
      const error = new Error("검증할 편집 초안이 없습니다. 먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-edit-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 초안을 검증하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const applyControls = readAdminEditApplyControls();
    const response = await window.RpgGameApi.previewAdminMasterDataEdit({
      domain: values.domain,
      id: values.id,
      draft: values.draft,
      baseValues: values.originals,
      reason: applyControls.reason || undefined,
      dryRun: true,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminEditPreviewResult(payload);
    setStatus(`초안 검증 완료: diff ${formatValue(payload.diffCount)} · errors ${formatValue(payload.errorCount)} · DB 저장 없음`, payload.errorCount ? "error" : "ok");
    return response;
  }

  async function applyAdminEditDraft(options) {
    ensureApi();
    const values = readAdminEditDraftValues();
    const controls = readAdminEditApplyControls();
    if (!values.ok || !values.id) {
      const error = new Error("적용할 편집 초안이 없습니다. 먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    requireAdminWriteDevKeyForUi("마스터 데이터 실제 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`확인 문구를 정확히 입력해야 합니다: ${ADMIN_EDIT_APPLY_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-edit-draft-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const review = buildAdminEditDraftReview(values);
    if (review.highCount > 0 && !controls.highRiskConfirmMatches) {
      const error = new Error(`고위험 변경이 있어서 추가 확인 문구를 정확히 입력해야 합니다: ${ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-edit-draft-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm(`정말 DB 마스터 데이터를 수정할까요? 변경 ${review.changeCount}개, high ${review.highCount}개입니다. 적용 후 게임은 새로고침해야 최신 master-data를 읽습니다.`);
    if (!confirmed) {
      setStatus("관리자 변경 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-edit-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에 변경을 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminMasterDataEdit({
      domain: values.domain,
      id: values.id,
      draft: values.draft,
      baseValues: values.originals,
      reason: controls.reason || undefined,
      confirmText: controls.confirmText,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminEditPreviewResult(payload);
    if (payload.applied) {
      await runPostWriteMasterApiVerification(values.domain, values.id, {
        label: "DB 적용",
        contextLabel: `change log #${formatValue(payload.changeLogId)} 적용 후 자동 확인`,
      });
      await refreshAdminChangeLogs({ filters: { ...readChangeLogFiltersFromDom(), targetType: `master_data.${values.domain}`, targetId: String(values.id), limit: 10 } });
    } else {
      setStatus(`DB 적용 실패/차단: ${formatValue(payload.status)} · errors ${formatValue(payload.errorCount)}`, "error");
    }
    return response;
  }

  function getAdminEditDraftReadiness(options) {
    const draft = $(`[data-admin-edit-draft]`);
    const fields = draft ? Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]")) : [];
    const validateButton = draft ? draft.querySelector('[data-admin-action="preview-admin-edit-draft"]') : null;
    const applyButton = draft ? draft.querySelector('[data-admin-action="apply-admin-edit-draft"]') : null;
    const controls = readAdminEditApplyControls();
    const result = {
      ok: !!draft && fields.length >= 0 && !!validateButton && validateButton.disabled === false && !!applyButton,
      version: VERSION,
      readOnly: false,
      dryRun: false,
      writeLocked: !hasAdminWriteDevKey(),
      guardedApply: true,
      adminWriteDevKeySet: hasAdminWriteDevKey(),
      confirmTextRequired: ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      highRiskConfirmTextRequired: ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT,
      confirmMatches: controls.confirmMatches,
      highRiskConfirmRequired: controls.highRiskConfirmRequired,
      highRiskConfirmMatches: controls.highRiskConfirmMatches,
      fieldsEditable: fields.every((field) => field.disabled === false),
      hasDraft: !!draft,
      fieldCount: fields.length,
      validateButtonEnabled: !!validateButton && validateButton.disabled === false,
      applyButtonReady: !!applyButton,
      currentDraft: readAdminEditDraftValues(),
      applyControls: controls,
      draftReview: buildAdminEditDraftReview(),
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin edit draft readiness", result);
    return result;
  }



  window.RpgAdminEditDraft = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    getAdminRelationEditOptionDefinitions,
    getAdminRelationEditOptionDefinition,
    isAdminRelationEditField,
    fieldKeyLooksReadOnly,
    isAdminEditApplyAllowedField,
    getAdminEditAllowedFields,
    normalizeAdminDraftFieldKey,
    getAdminEquipSlotDisplayName,
    getAdminDraftRelationOptionGroupKey,
    getAdminDraftRelationOptionsForValues,
    getAdminDraftRelationOptions,
    getAdminDraftSelectOptions,
    normalizeAdminRelationSearchText,
    getAdminRelationOptionText,
    filterAdminDraftSelectOptions,
    renderAdminDraftSelectOptionsHtml,
    getAdminRelationSelectMetaText,
    updateAdminRelationOptionMeta,
    applyAdminRelationOptionFilter,
    clearAdminRelationOptionFilter,
    refreshDependentAdminRelationSelects,
    getAdminDraftFieldInputKind,
    getAdminDraftFieldTypeLabel,
    getAdminDraftLockedReason,
    renderAdminDraftTypeBadge,
    getAdminDraftFieldRisk,
    renderAdminDraftRiskBadge,
    renderAdminDraftLockedFields,
    makeDraftOriginalValue,
    parseDraftOriginalValue,
    renderAdminDraftControl,
    getAdminRelationComboGuardLabels,
    renderAdminRelationEditOptionsNote,
    renderMasterEditDraft,
    readAdminEditDraftValues,
    resetAdminEditDraft,
    valuesEqualForImpact,
    collectLocalDraftChangesForImpact,
    getAdminRiskSortWeight,
    sortAdminChangesByRisk,
    getAdminRelationOptionDisplayText,
    getAdminRelationValueDisplay,
    getAdminRelationOpenTarget,
    renderAdminRelationOpenButton,
    getAdminChangeRelationInfo,
    formatAdminRelationInfoText,
    getAdminRelationOpenTargetFromChange,
    renderAdminRelationOpenTargetButton,
    formatAdminChangeValueText,
    renderAdminChangeValueCell,
    renderAdminRollbackMismatchValueCell,
    formatAdminChangeAfterValue,
    buildAdminEditDraftReview,
    renderAdminEditDraftReview,
    refreshAdminEditReviewAndImpact,
    normalizeImpactKey,
    getAdminEditImpactHint,
    buildAdminEditImpactGuide,
    renderAdminEditImpactGuide,
    refreshAdminEditImpactGuide,
    renderAdminEditPreviewResult,
    readAdminEditApplyControls,
    previewAdminEditDraft,
    applyAdminEditDraft,
    getAdminEditDraftReadiness
  };
})();
