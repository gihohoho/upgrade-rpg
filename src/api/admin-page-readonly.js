(function () {
  "use strict";

  const VERSION = "v114.admin-save-snapshot-filters";
  const DEFAULT_TIMEOUT_MS = 3500;
  const DEFAULT_SNAPSHOT_LIMIT = 30;
  const DEFAULT_SNAPSHOT_SORT = "updated_desc";

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

  async function fetchAdminReadOnlyPageData(options) {
    ensureApi();
    const opts = options || {};
    const timeoutMs = opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS;
    const filters = opts.snapshotFilters || readSnapshotFiltersFromDom();
    const [overview, snapshots] = await Promise.all([
      window.RpgGameApi.fetchAdminOverview({ timeoutMs }),
      window.RpgGameApi.listAdminSaveSnapshots({ timeoutMs, ...filters }),
    ]);
    return { overview, snapshots, snapshotFilters: filters };
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
    const readiness = $("[data-admin-readiness]");
    if (cards) cards.innerHTML = `<div class="card"><div class="label">오류</div><div class="value small">API 연결 실패</div></div>`;
    if (master) master.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (snapshots) snapshots.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
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
      renderCards(overviewPayload);
      renderMasterTable(overviewPayload.masterData || {});
      renderSnapshotTable(snapshotPayload);
      renderReadiness(overviewPayload.readiness || {});
      const filterText = describeSnapshotFilters(result.snapshotFilters || (snapshotPayload && snapshotPayload.filters));
      setStatus(`정상 로드 · ${formatClock(new Date().toISOString())} · ${filterText} · API ${window.RpgGameApi.getApiBaseUrl()}`, "ok");
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
      if (action === "apply-snapshot-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom() });
      if (action === "reset-snapshot-filters") {
        resetSnapshotFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom() });
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
    refreshAdminReadOnlyPage();
  }

  function checkAdminReadOnlyPageReady(options) {
    const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function");
    const domReady = !!document.querySelector("[data-admin-cards]");
    const locationHintReady = !!document.querySelector("[data-admin-current-url]");
    const snapshotFilterReady = !!document.querySelector("[data-admin-filter-slot-key]");
    const result = { ok: apiReady && domReady && snapshotFilterReady, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, readOnly: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom() };
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
    checkAdminReadOnlyPageReady,
  };
  window.refreshAdminReadOnlyPage = refreshAdminReadOnlyPage;
  window.fetchAdminReadOnlyPageData = fetchAdminReadOnlyPageData;
  window.readAdminSnapshotFilters = readSnapshotFiltersFromDom;
  window.resetAdminSnapshotFilters = resetSnapshotFilters;
  window.checkAdminReadOnlyPageReady = checkAdminReadOnlyPageReady;
  window.getCurrentAdminPageUrl = getCurrentAdminPageUrl;
  window.copyCurrentAdminPageUrl = copyCurrentAdminPageUrl;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
