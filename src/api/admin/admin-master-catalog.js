(function () {
  "use strict";

  const VERSION = "v192.admin-master-catalog-detail-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v191.admin-edit-draft-split v189.1.admin-create-lifecycle-split-hotfix v187.admin-change-logs-split v185.admin-layout-shell-split";
  const CATALOG_VIEW_MODES = ["detail"];
  const CATALOG_COLUMN_PRESETS = {
    itemTemplates: {
      basic: ["id", "code", "name", "itemType", "item_type", "grade", "equipSlot", "equip_slot", "stackable", "updatedAt", "updated_at", "updated"],
      json: ["id", "code", "name", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    skills: {
      basic: ["id", "code", "name", "slotKey", "slot_key", "cooldownSeconds", "cooldown_seconds", "procRate", "proc_rate", "updatedAt", "updated_at", "updated"],
      json: ["id", "code", "name", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    bosses: {
      basic: ["id", "code", "name", "bossType", "boss_type", "enemyHp", "enemy_hp", "goldReward", "gold_reward", "updatedAt", "updated_at", "updated"],
      json: ["id", "code", "name", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    fieldZones: {
      basic: ["id", "code", "name", "enemyHp", "enemy_hp", "goldReward", "gold_reward", "sortOrder", "sort_order", "updatedAt", "updated_at", "updated"],
      json: ["id", "code", "name", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    dropTableItems: {
      basic: ["id", "dropTableCode", "drop_table_code", "itemTemplateCode", "item_template_code", "rate", "minQuantity", "min_quantity", "maxQuantity", "max_quantity", "updatedAt", "updated_at", "updated"],
      json: ["id", "dropTableCode", "drop_table_code", "itemTemplateCode", "item_template_code", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    skillLevels: {
      basic: ["id", "skillCode", "skill_code", "level", "damageMultiplier", "damage_multiplier", "cooldownSeconds", "cooldown_seconds", "updatedAt", "updated_at", "updated"],
      json: ["id", "skillCode", "skill_code", "level", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
    enhancementLevels: {
      basic: ["id", "groupCode", "group_code", "fromLevel", "from_level", "toLevel", "to_level", "successRate", "success_rate", "goldCost", "gold_cost", "updatedAt", "updated_at", "updated"],
      json: ["id", "groupCode", "group_code", "fromLevel", "from_level", "toLevel", "to_level", "jsonKeys", "json_keys", "updatedAt", "updated_at", "updated"],
    },
  };

  let configured = false;
  let DEFAULT_MASTER_DOMAIN = "itemTemplates";
  let DEFAULT_MASTER_LIMIT = 10;
  let DEFAULT_MASTER_SORT = "id_asc";
  let DEFAULT_TIMEOUT_MS = 3500;
  let ADMIN_TO_MASTER_API_FIELD_MAP = {};

  let $ = (selector) => document.querySelector(selector);
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let formatValue = (value) => (value === null || value === undefined || value === "" ? "-" : String(value));
  let formatClock = (value) => formatValue(value);
  let formatValueWithFieldHint = (_key, value) => escapeHtml(formatValue(value));
  let renderFieldHelpBadge = () => "";
  let renderFieldHelpInline = () => "";
  let getAdminFieldHelp = () => null;
  let getAdminFieldValueHint = () => null;
  let renderMasterEditDraft = () => "";
  let ensureApi = () => {
    if (!window.RpgGameApi) throw new Error("RpgGameApi is not loaded");
    return window.RpgGameApi;
  };
  let setStatus = () => undefined;
  let readSnapshotFiltersFromDom = () => ({});
  let readChangeLogFiltersFromDom = () => ({});
  let readAdminCreateBlueprintFiltersFromDom = () => ({ domain: DEFAULT_MASTER_DOMAIN });
  let syncAdminCreateDomainOptions = () => undefined;
  let refreshAdminReadOnlyPage = async () => ({ ok: true });
  let getCurrentMasterDetailPayload = () => null;
  let setCurrentMasterDetailPayload = () => undefined;

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    if (typeof d.formatClock === "function") formatClock = d.formatClock;
    if (typeof d.formatValueWithFieldHint === "function") formatValueWithFieldHint = d.formatValueWithFieldHint;
    if (typeof d.renderFieldHelpBadge === "function") renderFieldHelpBadge = d.renderFieldHelpBadge;
    if (typeof d.renderFieldHelpInline === "function") renderFieldHelpInline = d.renderFieldHelpInline;
    if (typeof d.getAdminFieldHelp === "function") getAdminFieldHelp = d.getAdminFieldHelp;
    if (typeof d.getAdminFieldValueHint === "function") getAdminFieldValueHint = d.getAdminFieldValueHint;
    if (typeof d.renderMasterEditDraft === "function") renderMasterEditDraft = d.renderMasterEditDraft;
    if (typeof d.ensureApi === "function") ensureApi = d.ensureApi;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.readSnapshotFiltersFromDom === "function") readSnapshotFiltersFromDom = d.readSnapshotFiltersFromDom;
    if (typeof d.readChangeLogFiltersFromDom === "function") readChangeLogFiltersFromDom = d.readChangeLogFiltersFromDom;
    if (typeof d.readAdminCreateBlueprintFiltersFromDom === "function") readAdminCreateBlueprintFiltersFromDom = d.readAdminCreateBlueprintFiltersFromDom;
    if (typeof d.syncAdminCreateDomainOptions === "function") syncAdminCreateDomainOptions = d.syncAdminCreateDomainOptions;
    if (typeof d.refreshAdminReadOnlyPage === "function") refreshAdminReadOnlyPage = d.refreshAdminReadOnlyPage;
    if (typeof d.getCurrentMasterDetailPayload === "function") getCurrentMasterDetailPayload = d.getCurrentMasterDetailPayload;
    if (typeof d.setCurrentMasterDetailPayload === "function") setCurrentMasterDetailPayload = d.setCurrentMasterDetailPayload;
    DEFAULT_MASTER_DOMAIN = d.DEFAULT_MASTER_DOMAIN || DEFAULT_MASTER_DOMAIN;
    DEFAULT_MASTER_LIMIT = Number(d.DEFAULT_MASTER_LIMIT || DEFAULT_MASTER_LIMIT);
    DEFAULT_MASTER_SORT = d.DEFAULT_MASTER_SORT || DEFAULT_MASTER_SORT;
    DEFAULT_TIMEOUT_MS = Number(d.DEFAULT_TIMEOUT_MS || DEFAULT_TIMEOUT_MS);
    ADMIN_TO_MASTER_API_FIELD_MAP = d.ADMIN_TO_MASTER_API_FIELD_MAP && typeof d.ADMIN_TO_MASTER_API_FIELD_MAP === "object" ? d.ADMIN_TO_MASTER_API_FIELD_MAP : ADMIN_TO_MASTER_API_FIELD_MAP;
    configured = true;
    return getReadiness({ log: false });
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


function normalizeCatalogFieldKey(key) {
    return String(key || "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
  }

function readMasterCatalogViewModeFromDom() {
    return "detail";
  }

function getCatalogPresetForDomain(domain) {
    return CATALOG_COLUMN_PRESETS[String(domain || "")] || null;
  }

function columnMatchesAny(column, keys) {
    const normalized = normalizeCatalogFieldKey(column && column.key);
    const normalizedKeys = (keys || []).map(normalizeCatalogFieldKey);
    return normalizedKeys.includes(normalized);
  }

function filterCatalogColumnsForView(_domain, columns, _viewMode) {
    return Array.isArray(columns) ? columns : [];
  }

function getCatalogViewModeLabel(_viewMode) {
    return "전체 컬럼";
  }

function isCatalogUpdatedAtField(key) {
    const normalized = normalizeCatalogFieldKey(key);
    return normalized === "updatedat" || normalized === "modifiedat" || normalized === "updated";
  }

function isCatalogJsonKeysField(key) {
    const normalized = normalizeCatalogFieldKey(key);
    return normalized === "jsonkeys" || normalized.endsWith("jsonkeys");
  }

function formatCatalogTimestampDetail(value) {
    if (value === null || value === undefined || value === "") return { dateOnly: "-", fullText: "상세 수정 시각 없음" };
    const raw = String(value);
    const dateMatch = raw.match(/^(\d{4}-\d{2}-\d{2})/);
    const dateOnly = dateMatch ? dateMatch[1] : formatValue(value);
    let fullText = raw.replace("T", " ").replace(/\.\d+/, "");
    fullText = fullText.replace(/Z$/, " UTC");
    const timeMatch = fullText.match(/^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})(?!:)/);
    if (timeMatch) fullText = fullText.replace(timeMatch[0], `${timeMatch[1]} ${timeMatch[2]}:00`);
    return { dateOnly, fullText };
  }

function formatCatalogUpdatedAtCell(value) {
    const time = formatCatalogTimestampDetail(value);
    if (time.dateOnly === "-") return escapeHtml(time.dateOnly);
    return `<span class="catalog-date-compact"><strong>${escapeHtml(time.dateOnly)}</strong><span class="field-help-badge catalog-time-badge" title="${escapeHtml(`상세 수정 시각\n${time.fullText}`)}">?</span></span>`;
  }

function extractCatalogJsonKeys(value) {
    if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean);
    if (value === null || value === undefined || value === "") return [];
    return String(value)
      .replace(/^\[|\]$/g, "")
      .split(/[\n,|]/)
      .map((item) => item.replace(/^['"\s]+|['"\s]+$/g, "").trim())
      .filter(Boolean);
  }

function formatCatalogJsonKeysCell(value) {
    const keys = Array.from(new Set(extractCatalogJsonKeys(value)));
    if (!keys.length) return `<span class="pill good">JSON 키 없음</span>`;
    const visible = keys.slice(0, 3);
    const hiddenCount = Math.max(0, keys.length - visible.length);
    const fullText = `전체 JSON 키 ${keys.length}개\n${keys.join(", ")}`;
    return `<span class="json-keys-compact" title="${escapeHtml(fullText)}">${visible.map((key) => `<span class="json-key-chip">${escapeHtml(key)}</span>`).join("")}${hiddenCount ? `<span class="json-key-more">외 ${escapeHtml(hiddenCount)}개</span>` : ""}<span class="field-help-badge catalog-json-keys-badge" title="${escapeHtml(fullText)}">?</span></span>`;
  }

function renderCatalogLongValueCell(key, value) {
    const text = formatValue(value);
    if (text === "-" || text.length <= 44) return escapeHtml(text);
    if (window.RpgAdminLongValueModal && typeof window.RpgAdminLongValueModal.renderLongValueTrigger === "function") {
      return window.RpgAdminLongValueModal.renderLongValueTrigger(`${key} 전체 보기`, text, { previewLength: 28, buttonLabel: "전체" });
    }
    return `<span class="catalog-cell-compact"><span class="catalog-cell-preview" title="${escapeHtml(text)}">${escapeHtml(text.slice(0, 27))}…</span></span>`;
  }

function formatCatalogCellValue(key, value) {
    if (isCatalogUpdatedAtField(key)) return formatCatalogUpdatedAtCell(value);
    if (isCatalogJsonKeysField(key)) return formatCatalogJsonKeysCell(value);
    const hint = getAdminFieldValueHint(key, value);
    if (!hint) return renderCatalogLongValueCell(key, value);
    const titleText = `${hint.label}
${hint.body || ""}`;
    return `<span class="field-value-compact" title="${escapeHtml(titleText)}"><strong>${escapeHtml(hint.label)}</strong>${renderFieldHelpBadge(key)}</span>`;
  }

function renderMasterCatalogTable(catalogPayload) {
    const target = $("[data-admin-master-catalog-table]");
    const meta = $("[data-admin-master-catalog-meta]");
    if (!target) return;
    const rows = Array.isArray(catalogPayload.rows) ? catalogPayload.rows : [];
    const rawColumns = Array.isArray(catalogPayload.columns) ? catalogPayload.columns : [];
    const viewMode = readMasterCatalogViewModeFromDom();
    const columns = filterCatalogColumnsForView(catalogPayload.domain, rawColumns, viewMode);
    const filters = catalogPayload.filters || {};
    const totalAllNote = catalogPayload.totalAll !== undefined ? ` / 전체 ${formatValue(catalogPayload.totalAll)}` : "";
    const page = Number(catalogPayload.page) || 1;
    const totalPages = Number(catalogPayload.totalPages) || 1;
    const filterNote = filters.hasActiveFilters ? ` · ${describeMasterCatalogFilters(filters)}` : "";
    if (meta) meta.textContent = `${escapeHtml(catalogPayload.domainLabel || catalogPayload.domain || "-")} · ${getCatalogViewModeLabel(viewMode)} · ${formatValue(rows.length)} / ${formatValue(catalogPayload.total)} shown · page ${formatValue(page)} / ${formatValue(totalPages)}${totalAllNote}${filterNote}`;
    renderMasterCatalogPagination(catalogPayload);
    if (!rows.length || !columns.length) {
      target.innerHTML = `<div class="empty">마스터 데이터 카탈로그 결과가 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table data-admin-master-catalog-view-mode="${escapeHtml(viewMode)}">
        <thead><tr><th>상세</th>${columns.map((column) => `<th title="${escapeHtml((getAdminFieldHelp(column.key) && getAdminFieldHelp(column.key).body) || column.key)}">${escapeHtml(column.label || column.key)}${renderFieldHelpBadge(column.key)}</th>`).join("")}<th>원본 JSON</th><th>이미지</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const cells = row.cells || {};
            return `
              <tr data-admin-master-row-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-master-row-id="${escapeHtml(row.id)}">
                <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button><span data-admin-master-row-selected></span></td>
                ${columns.map((column) => `<td>${formatCatalogCellValue(column.key, cells[column.key])}</td>`).join("")}
                <td><span class="pill ${row.rawJsonReturned ? "blocked" : "good"}">${row.rawJsonReturned ? "returned" : "hidden"}</span></td>
                <td><span class="pill ${row.assetsReturned ? "blocked" : "good"}">${row.assetsReturned ? "returned" : "hidden"}</span></td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
    const selectedDetail = getCurrentMasterDetailPayload();
    if (selectedDetail && selectedDetail.domain && selectedDetail.id) {
      markSelectedMasterCatalogRow(selectedDetail.domain, selectedDetail.id);
    }
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
    const detail = getCurrentMasterDetailPayload();
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
    setCurrentMasterDetailPayload(detailPayload && detailPayload.status === "loaded" ? detailPayload : null);
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
    const detailSummaryHtml = `
      <div class="detail-quick-summary">
        <div>
          <h3>${escapeHtml(detail.title || detail.name || detail.code || `#${detail.id}`)}</h3>
          <p>${escapeHtml(formatValue(detail.domainLabel || detail.domain))} · #${escapeHtml(formatValue(detail.id))} · 아래 순서로 기본 필드 → 편집 Preview → 연결 항목 → JSON 미리보기를 확인하세요.</p>
        </div>
        <div class="detail-next-actions">
          <button class="btn mini" type="button" data-admin-action="verify-master-api-target" data-admin-detail-jump-target="admin-master-api-verify-card" title="아래 API 반영 확인 카드로 이동한 뒤 현재 항목을 점검합니다.">API 반영 확인</button>
          <button class="btn mini" type="button" data-admin-action="open-master-relations" data-admin-detail-jump-target="admin-master-relations-card" data-admin-relation-domain="${escapeHtml(detail.domain || "")}" data-admin-relation-id="${escapeHtml(detail.id)}" title="아래 실제 연결 항목 카드로 이동하고 관계 데이터를 불러옵니다.">연결 항목</button>
          <a class="btn mini" href="#section-field-help" data-admin-detail-scroll-target="section-field-help" title="필드 용어 도움말 섹션을 펼치고 이동합니다.">필드 도움말</a>
        </div>
      </div>
      <div class="detail-section-guide">
        <div class="guide-mini-card"><strong>1. 기본 필드</strong>짧은 값과 ? 도움말로 현재 상태를 먼저 읽습니다.</div>
        <div class="guide-mini-card"><strong>2. Preview</strong>변경 전/후 Diff와 stale 여부를 확인합니다.</div>
        <div class="guide-mini-card"><strong>3. JSON/연결</strong>긴 값과 연결 항목은 접힌 영역에서 필요할 때만 봅니다.</div>
      </div>
    `;
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
      ${detailSummaryHtml}
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
      <div class="detail-card" style="margin:0 14px 12px;" data-admin-detail-target="admin-master-api-verify-card">
        <div class="detail-title">인게임 master-data API 반영 확인 <span class="pill good">diagnostic</span></div>
        <div class="filter-help">관리자 상세 값이 게임이 읽는 <code>/game/master-data</code> 응답에도 같은 값으로 보이는지 확인합니다. DB 적용 직후 게임 새로고침 전 점검용입니다.</div>
        <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn mini primary" type="button" data-admin-action="verify-master-api-target">선택 항목 API 반영 확인</button>
          <span class="pill warn">게임 화면은 새로고침 필요</span>
        </div>
        <div class="edit-draft-result" data-admin-master-api-verify-result><div class="empty">버튼을 누르면 현재 선택한 상세 항목이 <strong>/game/master-data</strong> 응답에도 같은 값으로 보이는지 확인합니다.</div></div>
      </div>
      <div class="detail-card" style="margin:0 14px 12px;" data-admin-detail-target="admin-master-relations-card">
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
                        ${columns.map((column) => `<td>${formatCatalogCellValue(column.key, cells[column.key])}</td>`).join("")}
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

async function refreshAdminMasterCatalog(options) {
    const opts = options || {};
    return refreshAdminReadOnlyPage({
      snapshotFilters: readSnapshotFiltersFromDom(),
      masterCatalogFilters: opts.filters || readMasterCatalogFiltersFromDom(),
      changeLogFilters: readChangeLogFiltersFromDom(),
      createBlueprintFilters: readAdminCreateBlueprintFiltersFromDom(),
    });
  }

  function getReadiness(options) {
    const requiredExports = [
      "readMasterCatalogFiltersFromDom",
      "resetMasterCatalogFilters",
      "describeMasterCatalogFilters",
      "syncMasterDomainOptions",
      "renderMasterTable",
      "renderMasterCatalogTable",
      "formatCatalogCellValue",
      "filterCatalogColumnsForView",
      "readMasterCatalogViewModeFromDom",
      "openAdminMasterDataDetail",
      "openAdminMasterDataDetailByCode",
      "openAdminMasterDataRelations",
      "verifySelectedMasterDataApi",
      "runPostWriteMasterApiVerification",
    ];
    const missingExports = requiredExports.filter((name) => typeof window.RpgAdminMasterCatalog[name] !== "function");
    const domTargets = [
      "[data-admin-master-domain]",
      "[data-admin-master-catalog-table]",
      "[data-admin-master-detail]",
    ];
    const missingDomTargets = domTargets.filter((selector) => !document.querySelector(selector));
    const result = {
      ok: configured && typeof window.RpgGameApi !== "undefined" && !missingExports.length && !missingDomTargets.length,
      version: VERSION,
      configured,
      status: "extracted-v192",
      currentFile: "src/api/admin/admin-master-catalog.js",
      requiredExports,
      missingExports,
      missingDomTargets,
      domTargets,
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin master catalog/detail readiness", result);
    return result;
  }

  window.RpgAdminMasterCatalog = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    readMasterCatalogFiltersFromDom,
    resetMasterCatalogFilters,
    describeMasterCatalogFilters,
    syncMasterDomainOptions,
    renderMasterTable,
    syncMasterCatalogPageInput,
    renderMasterCatalogPagination,
    markSelectedMasterCatalogRow,
    refreshMasterCatalogWithPage,
    renderMasterCatalogTable,
    formatCatalogCellValue,
    renderCatalogLongValueCell,
    readMasterCatalogViewModeFromDom,
    filterCatalogColumnsForView,
    getCatalogViewModeLabel,
    CATALOG_COLUMN_PRESETS,
    makeAdminDetailFieldMap,
    valuesEqualForApiVerify,
    findMasterApiRow,
    buildMasterApiVerifyComparisons,
    renderMasterApiVerifyResult,
    verifySelectedMasterDataApi,
    runPostWriteMasterApiVerification,
    renderMasterDetail,
    renderMasterRelations,
    openAdminMasterDataRelations,
    openAdminMasterDataDetailByCode,
    openAdminMasterDataDetail,
    refreshAdminMasterCatalog,
  };
})();
