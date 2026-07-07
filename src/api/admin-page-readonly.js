(function () {
  "use strict";

  const VERSION = "v122.admin-guarded-edit-apply";
  const DEFAULT_TIMEOUT_MS = 3500;
  const DEFAULT_SNAPSHOT_LIMIT = 30;
  const DEFAULT_SNAPSHOT_SORT = "updated_desc";
  const DEFAULT_MASTER_DOMAIN = "itemTemplates";
  const DEFAULT_MASTER_LIMIT = 50;
  const DEFAULT_MASTER_SORT = "code_asc";
  const ADMIN_EDIT_APPLY_CONFIRM_TEXT = "APPLY MASTER DATA EDIT";
  const ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  const ADMIN_EDIT_ALLOWED_FIELDS = {
    itemTemplates: ["name", "description", "grade", "stackable", "admin_note"],
    skills: ["name", "description", "proc_rate", "cooldown_seconds"],
    skillLevels: ["damage_multiplier", "proc_rate_bonus"],
    bosses: ["name", "tier", "boss_type", "hp", "description", "cooldown_seconds", "is_enabled"],
    fieldZones: ["name", "sort_order", "enemy_hp", "gold_reward", "description", "is_enabled"],
    characters: ["name", "description", "is_enabled"],
    dropTables: ["description", "is_enabled"],
    dropTableItems: ["rate", "min_quantity", "max_quantity"],
    enhancementGroups: ["name", "description", "max_level", "is_enabled"],
    enhancementLevels: ["to_level", "success_rate", "gold_cost"],
    characterSkills: ["sort_order", "is_default"],
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

  function ensureApi() {
    if (!window.RpgGameApi) throw new Error("RpgGameApi를 찾을 수 없습니다. game-api-client.js 로딩 순서를 확인하세요.");
    if (typeof window.RpgGameApi.fetchAdminOverview !== "function") throw new Error("fetchAdminOverview 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminSaveSnapshots !== "function") throw new Error("listAdminSaveSnapshots 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogDomains !== "function") throw new Error("listAdminMasterCatalogDomains 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogRows !== "function") throw new Error("listAdminMasterCatalogRows 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataDetail !== "function") throw new Error("fetchAdminMasterDataDetail 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataRelations !== "function") throw new Error("fetchAdminMasterDataRelations 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.applyAdminMasterDataEdit !== "function") throw new Error("applyAdminMasterDataEdit 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminChangeLogs !== "function") throw new Error("listAdminChangeLogs 함수를 찾을 수 없습니다.");
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


  function readMasterCatalogFiltersFromDom() {
    const domainEl = $("[data-admin-master-domain]");
    const limitEl = $("[data-admin-master-limit]");
    const queryEl = $("[data-admin-master-query]");
    const enabledEl = $("[data-admin-master-enabled]");
    const sortEl = $("[data-admin-master-sort]");
    return {
      domain: domainEl && domainEl.value ? domainEl.value : DEFAULT_MASTER_DOMAIN,
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_MASTER_LIMIT,
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
    if (domainEl) domainEl.value = DEFAULT_MASTER_DOMAIN;
    if (limitEl) limitEl.value = String(DEFAULT_MASTER_LIMIT);
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
  }

  async function fetchAdminReadOnlyPageData(options) {
    ensureApi();
    const opts = options || {};
    const timeoutMs = opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS;
    const filters = opts.snapshotFilters || readSnapshotFiltersFromDom();
    const masterCatalogFilters = opts.masterCatalogFilters || readMasterCatalogFiltersFromDom();
    const [overview, snapshots, masterDomains, masterCatalog] = await Promise.all([
      window.RpgGameApi.fetchAdminOverview({ timeoutMs }),
      window.RpgGameApi.listAdminSaveSnapshots({ timeoutMs, ...filters }),
      window.RpgGameApi.listAdminMasterCatalogDomains({ timeoutMs }),
      window.RpgGameApi.listAdminMasterCatalogRows({ timeoutMs, ...masterCatalogFilters }),
    ]);
    return { overview, snapshots, masterDomains, masterCatalog, snapshotFilters: filters, masterCatalogFilters };
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



  function renderMasterCatalogTable(catalogPayload) {
    const target = $("[data-admin-master-catalog-table]");
    const meta = $("[data-admin-master-catalog-meta]");
    if (!target) return;
    const rows = Array.isArray(catalogPayload.rows) ? catalogPayload.rows : [];
    const columns = Array.isArray(catalogPayload.columns) ? catalogPayload.columns : [];
    const filters = catalogPayload.filters || {};
    const totalAllNote = catalogPayload.totalAll !== undefined ? ` / 전체 ${formatValue(catalogPayload.totalAll)}` : "";
    const filterNote = filters.hasActiveFilters ? ` · ${describeMasterCatalogFilters(filters)}` : "";
    if (meta) meta.textContent = `${escapeHtml(catalogPayload.domainLabel || catalogPayload.domain || "-")} · ${formatValue(rows.length)} / ${formatValue(catalogPayload.total)} shown${totalAllNote}${filterNote}`;
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
              <tr>
                <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button></td>
                ${columns.map((column) => `<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>`).join("")}
                <td><span class="pill ${row.rawJsonReturned ? "blocked" : "good"}">${row.rawJsonReturned ? "returned" : "hidden"}</span></td>
                <td><span class="pill ${row.assetsReturned ? "blocked" : "good"}">${row.assetsReturned ? "returned" : "hidden"}</span></td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
  }



  function fieldKeyLooksReadOnly(key) {
    const normalized = String(key || "").toLowerCase();
    return normalized === "id" || normalized === "code" || normalized.endsWith("_id") || normalized.endsWith("_code") || normalized.endsWith("_json") || normalized === "created_at" || normalized === "updated_at" || normalized === "createdat" || normalized === "updatedat";
  }

  function isAdminEditApplyAllowedField(domain, key) {
    const allowed = ADMIN_EDIT_ALLOWED_FIELDS[domain] || [];
    return allowed.includes(String(key || ""));
  }

  function getAdminEditAllowedFields(domain) {
    return (ADMIN_EDIT_ALLOWED_FIELDS[domain] || []).slice();
  }

  function inputTypeForDraftField(field) {
    const value = field ? field.value : null;
    if (typeof value === "number") return "number";
    if (typeof value === "boolean") return "checkbox";
    return "text";
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

  function renderMasterEditDraft(detail, fields) {
    const safeFields = Array.isArray(fields) ? fields : [];
    const domain = detail && detail.domain ? detail.domain : DEFAULT_MASTER_DOMAIN;
    const candidateFields = safeFields.filter((field) => !fieldKeyLooksReadOnly(field.key));
    const editableFields = candidateFields.filter((field) => isAdminEditApplyAllowedField(domain, field.key)).slice(0, 14);
    const lockedFields = candidateFields.filter((field) => !isAdminEditApplyAllowedField(domain, field.key)).map((field) => field.key);
    const hiddenCount = Math.max(0, candidateFields.length - editableFields.length);
    const rows = editableFields.length ? editableFields.map((field) => {
      const value = field.value;
      const valueText = value === null || value === undefined ? "" : String(value);
      const isLong = String(valueText).length > 90 || String(valueText).includes("\n");
      const type = inputTypeForDraftField(field);
      const label = field.label || field.key;
      const original = makeDraftOriginalValue(value);
      if (type === "checkbox") {
        return `
          <label class="draft-field draft-field-check">
            <span>${escapeHtml(label)}${renderFieldHelpBadge(field.key)}</span>
            ${renderFieldHelpInline(field.key)}
            ${renderFieldValueHintInline(field.key, value)}
            <label class="check-field" style="margin:0; padding:9px 10px; border-radius:10px; border:1px solid rgba(148, 163, 184, 0.22); background:rgba(2, 6, 23, 0.56);">
              <input type="checkbox" ${value ? "checked" : ""} data-admin-edit-draft-field="${escapeHtml(field.key)}" data-admin-edit-draft-original="${escapeHtml(original)}" data-admin-edit-draft-value-type="boolean" />
              true / false
            </label>
          </label>
        `;
      }
      return `
        <label class="draft-field">
          <span>${escapeHtml(label)}${renderFieldHelpBadge(field.key)}</span>
          ${renderFieldHelpInline(field.key)}
          ${renderFieldValueHintInline(field.key, value)}
          ${isLong
            ? `<textarea rows="3" data-admin-edit-draft-field="${escapeHtml(field.key)}" data-admin-edit-draft-original="${escapeHtml(original)}" data-admin-edit-draft-value-type="text">${escapeHtml(valueText)}</textarea>`
            : `<input type="${type === "number" ? "number" : "text"}" value="${escapeHtml(valueText)}" data-admin-edit-draft-field="${escapeHtml(field.key)}" data-admin-edit-draft-original="${escapeHtml(original)}" data-admin-edit-draft-value-type="${escapeHtml(type)}" />`}
        </label>
      `;
    }).join("") : `<div class="empty">이 도메인에서 실제 적용까지 열어둔 일반 필드가 없습니다.</div>`;

    return `
      <div class="detail-card edit-draft-card" data-admin-edit-draft data-admin-edit-draft-domain="${escapeHtml(domain || "")}" data-admin-edit-draft-id="${escapeHtml(detail.id || "")}">
        <div class="detail-title">관리자 편집 초안 <span class="pill warn">guarded apply</span><span class="pill good">change log</span></div>
        <div class="filter-help">이제 allow-list 필드는 실제 DB 적용까지 가능합니다. 먼저 <strong>초안 검증</strong>으로 오류가 없는지 확인한 뒤, 확인 문구 <code>${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}</code>를 정확히 입력해야 적용됩니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다.</div>
        <div class="filter-help">실제 적용 가능 필드: ${escapeHtml(getAdminEditAllowedFields(domain).join(", ") || "없음")}</div>
        ${lockedFields.length ? `<div class="filter-help">연결/식별자라 잠근 필드: ${escapeHtml(lockedFields.slice(0, 12).join(", "))}${lockedFields.length > 12 ? " ..." : ""}</div>` : ""}
        <div class="edit-draft-grid">${rows}</div>
        ${hiddenCount ? `<div class="filter-help">표시 제한/잠금으로 ${escapeHtml(formatValue(hiddenCount))}개 필드는 편집 초안에서 제외했습니다.</div>` : ""}
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-edit-draft">초안 검증</button>
          <button class="btn mini" type="button" data-admin-action="reset-admin-edit-draft">원래 값으로 되돌리기</button>
          <label class="apply-confirm-field"><span>확인 문구</span><input type="text" data-admin-edit-apply-confirm placeholder="${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>변경 사유</span><input type="text" data-admin-edit-apply-reason placeholder="예: 보스 HP 밸런스 조정" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-edit-draft">검증 후 실제 적용</button>
          <span class="pill warn">DB write: guarded</span>
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
      if (type === "boolean") values[key] = !!field.checked;
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
      if (type === "boolean") field.checked = !!original;
      else field.value = original === null || original === undefined ? "" : String(original);
    });
    const result = $(`[data-admin-edit-draft-result]`);
    if (result) result.innerHTML = `<div class="empty">원래 값으로 되돌렸습니다. 값을 바꾼 뒤 초안 검증을 누르세요.</div>`;
    setStatus("편집 초안을 원래 값으로 되돌렸습니다.", "ok");
    return true;
  }

  function renderAdminEditPreviewResult(preview) {
    const target = $(`[data-admin-edit-draft-result]`);
    if (!target) return;
    const payload = preview || {};
    const accepted = Array.isArray(payload.acceptedChanges) ? payload.acceptedChanges : [];
    const rejected = Array.isArray(payload.rejectedChanges) ? payload.rejectedChanges : [];
    const unchanged = Array.isArray(payload.unchangedChanges) ? payload.unchangedChanges : [];
    const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
    const acceptedRows = accepted.length ? accepted.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.before))}</td><td>${escapeHtml(formatValue(change.after))}</td><td>${escapeHtml(change.type || "-")}</td></tr>
    `).join("") : `<tr><td colspan="4">변경된 값 없음</td></tr>`;
    const rejectedRows = rejected.length ? rejected.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.after))}</td><td>${escapeHtml(change.reason || "rejected")}</td></tr>
    `).join("") : `<tr><td colspan="3">오류 없음</td></tr>`;
    const applied = payload.applied === true;
    const modeLabel = applied ? "applied" : (payload.dryRun ? "preview only" : "apply result");
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${payload.wouldBeValid ? "good" : "blocked"}">valid: ${escapeHtml(formatValue(payload.wouldBeValid))}</span>
        <span class="pill ${payload.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(payload.dryRun))}</span>
        <span class="pill ${payload.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(payload.writeBlocked))}</span>
        <span class="pill ${applied ? "good" : "warn"}">applied: ${escapeHtml(formatValue(applied))}</span>
        <span class="pill">diff ${escapeHtml(formatValue(payload.diffCount))}</span>
        <span class="pill">errors ${escapeHtml(formatValue(payload.errorCount))}</span>
        <span class="pill">unchanged ${escapeHtml(formatValue(payload.unchangedCount || unchanged.length))}</span>
        ${payload.changeLogId ? `<span class="pill good">change log #${escapeHtml(formatValue(payload.changeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${payload.note ? `<div class="filter-help">${escapeHtml(payload.note)}</div>` : ""}
      <details class="json-detail" open>
        <summary>변경 값 <span class="pill good">${escapeHtml(modeLabel)}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>이전 DB 값</th><th>적용/초안 값</th><th>타입</th></tr></thead><tbody>${acceptedRows}</tbody></table></div>
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
    const reasonEl = $(`[data-admin-edit-apply-reason]`);
    return {
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_EDIT_APPLY_CONFIRM_TEXT,
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
    if (!controls.confirmMatches) {
      const error = new Error(`확인 문구를 정확히 입력해야 합니다: ${ADMIN_EDIT_APPLY_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-edit-draft-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 DB 마스터 데이터를 수정할까요? 적용 후 게임은 새로고침해야 최신 master-data를 읽습니다.");
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
      reason: controls.reason || undefined,
      confirmText: controls.confirmText,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminEditPreviewResult(payload);
    if (payload.applied) {
      setStatus(`DB 적용 완료 · change log #${formatValue(payload.changeLogId)} · 상세 다시 불러오기`, "ok");
      await openAdminMasterDataDetail(values.domain, values.id, { timeoutMs: DEFAULT_TIMEOUT_MS });
      await refreshAdminChangeLogs({ targetType: `master_data.${values.domain}`, targetId: String(values.id), limit: 10 });
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
      writeLocked: false,
      guardedApply: true,
      confirmTextRequired: ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      confirmMatches: controls.confirmMatches,
      fieldsEditable: fields.every((field) => field.disabled === false),
      hasDraft: !!draft,
      fieldCount: fields.length,
      validateButtonEnabled: !!validateButton && validateButton.disabled === false,
      applyButtonReady: !!applyButton,
      currentDraft: readAdminEditDraftValues(),
      applyControls: controls,
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin edit draft readiness", result);
    return result;
  }

  function renderMasterDetail(detailPayload) {
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

  function renderAdminChangeLogs(logsPayload) {
    const target = $(`[data-admin-change-log-table]`);
    const meta = $(`[data-admin-change-log-meta]`);
    if (!target) return;
    const payload = logsPayload || {};
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    if (meta) meta.textContent = `${formatValue(rows.length)} / ${formatValue(payload.total)} logs · before/after raw JSON hidden`;
    if (!rows.length) {
      target.innerHTML = `<div class="empty">아직 관리자 변경 이력이 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>대상</th><th>행</th><th>액션</th><th>변경 필드</th><th>사유</th><th>적용</th><th>시각</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td>${escapeHtml(formatValue(row.id))}</td>
              <td>${escapeHtml(formatValue(row.targetType))}</td>
              <td>${escapeHtml(formatValue(row.targetId))}</td>
              <td>${escapeHtml(formatValue(row.action))}</td>
              <td>${escapeHtml((row.changedKeys || []).join(", ") || "-")}</td>
              <td>${escapeHtml(formatValue(row.reason))}</td>
              <td><span class="pill ${row.applied ? "good" : "blocked"}">${escapeHtml(formatValue(row.applied))}</span></td>
              <td>${escapeHtml(formatClock(row.createdAt))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  async function refreshAdminChangeLogs(options) {
    ensureApi();
    const opts = options || {};
    const target = $(`[data-admin-change-log-table]`);
    if (target) target.innerHTML = `<div class="empty">변경 이력 불러오는 중...</div>`;
    const response = await window.RpgGameApi.listAdminChangeLogs({
      limit: opts.limit || 20,
      targetType: opts.targetType || undefined,
      targetId: opts.targetId || undefined,
      timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminChangeLogs(payload);
    return response;
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
      renderCards(overviewPayload);
      renderMasterTable(overviewPayload.masterData || {});
      syncMasterDomainOptions(masterDomainsPayload);
      renderMasterCatalogTable(masterCatalogPayload);
      renderSnapshotTable(snapshotPayload);
      renderReadiness(overviewPayload.readiness || {});
      await refreshAdminChangeLogs({ limit: 20 });
      const filterText = describeSnapshotFilters(result.snapshotFilters || (snapshotPayload && snapshotPayload.filters));
      const masterFilterText = describeMasterCatalogFilters(result.masterCatalogFilters || (masterCatalogPayload && masterCatalogPayload.filters));
      setStatus(`정상 로드 · ${formatClock(new Date().toISOString())} · ${filterText} · ${masterFilterText} · API ${window.RpgGameApi.getApiBaseUrl()}`, "ok");
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

  function bindEvents() {
    document.addEventListener("click", async (event) => {
      const button = event.target && event.target.closest ? event.target.closest("[data-admin-action]") : null;
      if (!button) return;
      const action = button.getAttribute("data-admin-action");
      if (action === "refresh") await refreshAdminReadOnlyPage();
      if (action === "apply-snapshot-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom() });
      if (action === "apply-master-catalog-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom() });
      if (action === "open-master-detail") {
        const domain = button.getAttribute("data-admin-detail-domain");
        const id = button.getAttribute("data-admin-detail-id");
        try {
          await openAdminMasterDataDetail(domain, id);
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
          if (!(error && String(error.message || "").includes("확인 문구"))) renderError(error);
        }
      }
      if (action === "refresh-admin-change-logs") {
        try {
          await refreshAdminChangeLogs();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-admin-edit-draft") {
        resetAdminEditDraft();
      }
      if (action === "reset-master-catalog-filters") {
        resetMasterCatalogFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom() });
      }
      if (action === "reset-snapshot-filters") {
        resetSnapshotFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom() });
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
    syncLocationHints();
    syncApiInput();
    resetSnapshotFilters({ silent: true });
    resetMasterCatalogFilters({ silent: true });
    renderMasterDetail({});
    refreshAdminReadOnlyPage();
  }

  function checkAdminReadOnlyPageReady(options) {
    const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function" && typeof window.RpgGameApi.listAdminMasterCatalogRows === "function" && typeof window.RpgGameApi.fetchAdminMasterDataDetail === "function" && typeof window.RpgGameApi.fetchAdminMasterDataRelations === "function" && typeof window.RpgGameApi.previewAdminMasterDataEdit === "function" && typeof window.RpgGameApi.applyAdminMasterDataEdit === "function" && typeof window.RpgGameApi.listAdminChangeLogs === "function");
    const domReady = !!document.querySelector("[data-admin-cards]");
    const locationHintReady = !!document.querySelector("[data-admin-current-url]");
    const snapshotFilterReady = !!document.querySelector("[data-admin-filter-slot-key]");
    const masterCatalogReady = !!document.querySelector("[data-admin-master-domain]");
    const masterDetailReady = !!document.querySelector("[data-admin-master-detail]");
    const masterRelationsReady = true;
    const editDraftReady = !!document.querySelector("[data-admin-edit-draft]");
    const fieldHelpReady = !!document.querySelector("[data-admin-field-help]");
    const adminChangeLogReady = !!document.querySelector("[data-admin-change-log-table]");
    const result = { ok: apiReady && domReady && snapshotFilterReady && masterCatalogReady && masterDetailReady, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, masterCatalogReady, masterDetailReady, masterRelationsReady, editDraftReady, fieldHelpReady, adminChangeLogReady, readOnly: false, writeLocked: false, guardedApply: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), editDraft: getAdminEditDraftReadiness({ log: false }) };
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
    openAdminMasterDataDetail,
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
    getAdminEditDraftReadiness,
    refreshAdminChangeLogs,
    renderAdminChangeLogs,
    getAdminFieldHelp,
    listAdminFieldHelp,
    getAdminFieldValueHint,
    renderFieldValueHintInline,
    isAdminEditApplyAllowedField,
    getAdminEditAllowedFields,
    checkAdminReadOnlyPageReady,
  };
  window.refreshAdminReadOnlyPage = refreshAdminReadOnlyPage;
  window.fetchAdminReadOnlyPageData = fetchAdminReadOnlyPageData;
  window.readAdminSnapshotFilters = readSnapshotFiltersFromDom;
  window.resetAdminSnapshotFilters = resetSnapshotFilters;
  window.readAdminMasterCatalogFilters = readMasterCatalogFiltersFromDom;
  window.resetAdminMasterCatalogFilters = resetMasterCatalogFilters;
  window.openAdminMasterDataDetail = openAdminMasterDataDetail;
  window.openAdminMasterDataRelations = openAdminMasterDataRelations;
  window.checkAdminReadOnlyPageReady = checkAdminReadOnlyPageReady;
  window.getAdminEditDraftReadiness = getAdminEditDraftReadiness;
  window.readAdminEditDraftValues = readAdminEditDraftValues;
  window.resetAdminEditDraft = resetAdminEditDraft;
  window.previewAdminEditDraft = previewAdminEditDraft;
  window.getAdminFieldHelp = getAdminFieldHelp;
  window.listAdminFieldHelp = listAdminFieldHelp;
  window.getAdminFieldValueHint = getAdminFieldValueHint;
  window.getCurrentAdminPageUrl = getCurrentAdminPageUrl;
  window.copyCurrentAdminPageUrl = copyCurrentAdminPageUrl;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
