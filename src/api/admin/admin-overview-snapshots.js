(function () {
  "use strict";

  const VERSION = "v193.admin-overview-snapshots-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v192.admin-master-catalog-detail-split v191.admin-edit-draft-split v189.1.admin-create-lifecycle-split-hotfix v187.admin-change-logs-split v185.admin-layout-shell-split";

  let configured = false;
  let DEFAULT_SNAPSHOT_LIMIT = 30;
  let DEFAULT_SNAPSHOT_SORT = "updated_desc";
  let $ = (selector) => document.querySelector(selector);
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let formatValue = (value) => (value === null || value === undefined || value === "" ? "-" : String(value));
  let formatClock = (value) => formatValue(value);
  let setStatus = () => undefined;
  let hasAdminWriteDevKey = () => false;

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    if (typeof d.formatClock === "function") formatClock = d.formatClock;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.hasAdminWriteDevKey === "function") hasAdminWriteDevKey = d.hasAdminWriteDevKey;
    DEFAULT_SNAPSHOT_LIMIT = Number(d.DEFAULT_SNAPSHOT_LIMIT || DEFAULT_SNAPSHOT_LIMIT);
    DEFAULT_SNAPSHOT_SORT = d.DEFAULT_SNAPSHOT_SORT || DEFAULT_SNAPSHOT_SORT;
    configured = true;
    return getReadiness({ log: false });
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

  function renderAdminOverviewCards(overviewPayload) {
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

function renderAdminSnapshotTable(snapshotPayload) {
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

function renderAdminReadiness(readiness) {
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

  function getReadiness(options) {
    const requiredExports = [
      "readSnapshotFiltersFromDom",
      "resetSnapshotFilters",
      "describeSnapshotFilters",
      "renderAdminOverviewCards",
      "renderAdminSnapshotTable",
      "renderAdminReadiness",
    ];
    const missingExports = requiredExports.filter((name) => typeof window.RpgAdminOverviewSnapshots[name] !== "function");
    const domTargets = [
      "[data-admin-cards]",
      "[data-admin-snapshot-table]",
      "[data-admin-snapshot-meta]",
      "[data-admin-readiness]",
      "[data-admin-filter-slot-key]",
    ];
    const missingDomTargets = domTargets.filter((selector) => !document.querySelector(selector));
    const result = {
      ok: configured && !missingExports.length && !missingDomTargets.length,
      version: VERSION,
      configured,
      status: "extracted-v193",
      currentFile: "src/api/admin/admin-overview-snapshots.js",
      requiredExports,
      missingExports,
      missingDomTargets,
      domTargets,
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin overview/snapshots readiness", result);
    return result;
  }

  window.RpgAdminOverviewSnapshots = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    readSnapshotFiltersFromDom,
    resetSnapshotFilters,
    describeSnapshotFilters,
    renderAdminOverviewCards,
    renderAdminSnapshotTable,
    renderAdminReadiness,
  };
})();
