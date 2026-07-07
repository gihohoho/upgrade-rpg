(function () {
  "use strict";

  const VERSION = "v117.admin-master-data-relations";
  const DEFAULT_TIMEOUT_MS = 3500;
  const DEFAULT_SNAPSHOT_LIMIT = 30;
  const DEFAULT_SNAPSHOT_SORT = "updated_desc";
  const DEFAULT_MASTER_DOMAIN = "itemTemplates";
  const DEFAULT_MASTER_LIMIT = 50;
  const DEFAULT_MASTER_SORT = "code_asc";

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
      <div class="card"><div class="label">쓰기 UI</div><div class="value small"><span class="pill ${writeLocked ? "blocked" : "warn"}">${writeLocked ? "blocked" : "check"}</span></div></div>
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
        <thead><tr><th>상세</th>${columns.map((column) => `<th>${escapeHtml(column.label || column.key)}</th>`).join("")}<th>원본 JSON</th><th>이미지</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const cells = row.cells || {};
            return `
              <tr>
                <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button></td>
                ${columns.map((column) => `<td>${escapeHtml(formatValue(cells[column.key]))}</td>`).join("")}
                <td><span class="pill ${row.rawJsonReturned ? "blocked" : "good"}">${row.rawJsonReturned ? "returned" : "hidden"}</span></td>
                <td><span class="pill ${row.assetsReturned ? "blocked" : "good"}">${row.assetsReturned ? "returned" : "hidden"}</span></td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
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
      <tr><th>${escapeHtml(field.label || field.key)}</th><td>${escapeHtml(formatValue(field.value))}</td></tr>
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
                <thead><tr><th>상세</th><th>ID</th><th>제목</th>${columns.map((column) => `<th>${escapeHtml(column.label || column.key)}</th>`).join("")}</tr></thead>
                <tbody>
                  ${rows.map((row) => {
                    const cells = row.cells || {};
                    return `
                      <tr>
                        <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || group.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button></td>
                        <td>${escapeHtml(formatValue(row.id))}</td>
                        <td>${escapeHtml(formatValue(row.title))}</td>
                        ${columns.map((column) => `<td>${escapeHtml(formatValue(cells[column.key]))}</td>`).join("")}
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

  function renderReadiness(readiness) {
    const target = $("[data-admin-readiness]");
    if (!target) return;
    const warnings = Array.isArray(readiness.warnings) ? readiness.warnings : [];
    target.innerHTML = `
      <div style="padding:14px; display:grid; gap:10px;">
        <div><span class="pill ${readiness.safeForAdminReadOnlyUi ? "good" : "warn"}">read-only UI: ${escapeHtml(formatValue(readiness.safeForAdminReadOnlyUi))}</span></div>
        <div><span class="pill ${readiness.safeForAdminWriteUi ? "warn" : "blocked"}">write UI: ${escapeHtml(formatValue(readiness.safeForAdminWriteUi))}</span></div>
        <div style="color:#cbd5e1; font-size:13px;">${escapeHtml(readiness.writeUiBlockedReason || "쓰기 기능은 아직 막혀 있습니다.")}</div>
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
    const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function" && typeof window.RpgGameApi.listAdminMasterCatalogRows === "function" && typeof window.RpgGameApi.fetchAdminMasterDataDetail === "function" && typeof window.RpgGameApi.fetchAdminMasterDataRelations === "function");
    const domReady = !!document.querySelector("[data-admin-cards]");
    const locationHintReady = !!document.querySelector("[data-admin-current-url]");
    const snapshotFilterReady = !!document.querySelector("[data-admin-filter-slot-key]");
    const masterCatalogReady = !!document.querySelector("[data-admin-master-domain]");
    const masterDetailReady = !!document.querySelector("[data-admin-master-detail]");
    const masterRelationsReady = true;
    const result = { ok: apiReady && domReady && snapshotFilterReady && masterCatalogReady && masterDetailReady, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, masterCatalogReady, masterDetailReady, masterRelationsReady, readOnly: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom() };
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
  window.getCurrentAdminPageUrl = getCurrentAdminPageUrl;
  window.copyCurrentAdminPageUrl = copyCurrentAdminPageUrl;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
