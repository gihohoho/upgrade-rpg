(function () {
  "use strict";

  const VERSION = "v187.admin-change-logs-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v186.admin-change-log-split-contract v185.admin-layout-shell-split";

  let configured = false;
  let currentAdminChangeLogDetailPayload = null;

  let DEFAULT_CHANGE_LOG_LIMIT = 20;
  let DEFAULT_CHANGE_LOG_SORT = "created_desc";
  let DEFAULT_TIMEOUT_MS = 3500;
  let ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  let ADMIN_ROLLBACK_CONFIRM_TEXT = "ROLLBACK MASTER DATA EDIT";
  let ADMIN_CREATE_DELETE_CONFIRM_TEXT = "DELETE CREATED MASTER DATA ROW";
  let ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = "RESTORE DELETED CREATED ROW";
  let ADMIN_CHANGE_LOG_ACTION_FILTERS = ["update", "rollback", "create", "create_delete", "create_delete_restore"];

  let $ = (selector) => document.querySelector(selector);
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let formatValue = (value) => (value === null || value === undefined || value === "" ? "-" : String(value));
  let formatClock = (value) => formatValue(value);
  let ensureApi = () => {
    if (!window.RpgGameApi) throw new Error("RpgGameApi is not loaded");
    return window.RpgGameApi;
  };
  let setStatus = () => undefined;
  let renderAdminChangeValueCell = (_domain, change, side) => escapeHtml(formatValue(change && change[side]));
  let renderAdminRollbackMismatchValueCell = (_domain, item, key) => escapeHtml(formatValue(item && item[key]));
  let renderAdminOperationResultBanner = () => "";
  let renderAdminCreateDeleteBlockerSummary = () => "";
  let requireAdminWriteDevKeyForUi = () => true;
  let refreshAdminMasterCatalog = async () => ({ ok: true });
  let runPostWriteMasterApiVerification = async () => ({ ok: true });
  let readMasterCatalogFiltersFromDom = () => ({});

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    if (typeof d.formatClock === "function") formatClock = d.formatClock;
    if (typeof d.ensureApi === "function") ensureApi = d.ensureApi;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.renderAdminChangeValueCell === "function") renderAdminChangeValueCell = d.renderAdminChangeValueCell;
    if (typeof d.renderAdminRollbackMismatchValueCell === "function") renderAdminRollbackMismatchValueCell = d.renderAdminRollbackMismatchValueCell;
    if (typeof d.renderAdminOperationResultBanner === "function") renderAdminOperationResultBanner = d.renderAdminOperationResultBanner;
    if (typeof d.renderAdminCreateDeleteBlockerSummary === "function") renderAdminCreateDeleteBlockerSummary = d.renderAdminCreateDeleteBlockerSummary;
    if (typeof d.requireAdminWriteDevKeyForUi === "function") requireAdminWriteDevKeyForUi = d.requireAdminWriteDevKeyForUi;
    if (typeof d.refreshAdminMasterCatalog === "function") refreshAdminMasterCatalog = d.refreshAdminMasterCatalog;
    if (typeof d.runPostWriteMasterApiVerification === "function") runPostWriteMasterApiVerification = d.runPostWriteMasterApiVerification;
    if (typeof d.readMasterCatalogFiltersFromDom === "function") readMasterCatalogFiltersFromDom = d.readMasterCatalogFiltersFromDom;
    DEFAULT_CHANGE_LOG_LIMIT = Number(d.DEFAULT_CHANGE_LOG_LIMIT || DEFAULT_CHANGE_LOG_LIMIT);
    DEFAULT_CHANGE_LOG_SORT = d.DEFAULT_CHANGE_LOG_SORT || DEFAULT_CHANGE_LOG_SORT;
    DEFAULT_TIMEOUT_MS = Number(d.DEFAULT_TIMEOUT_MS || DEFAULT_TIMEOUT_MS);
    ADMIN_EDIT_APPLY_TIMEOUT_MS = Number(d.ADMIN_EDIT_APPLY_TIMEOUT_MS || ADMIN_EDIT_APPLY_TIMEOUT_MS);
    ADMIN_ROLLBACK_CONFIRM_TEXT = d.ADMIN_ROLLBACK_CONFIRM_TEXT || ADMIN_ROLLBACK_CONFIRM_TEXT;
    ADMIN_CREATE_DELETE_CONFIRM_TEXT = d.ADMIN_CREATE_DELETE_CONFIRM_TEXT || ADMIN_CREATE_DELETE_CONFIRM_TEXT;
    ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = d.ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT || ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT;
    ADMIN_CHANGE_LOG_ACTION_FILTERS = Array.isArray(d.ADMIN_CHANGE_LOG_ACTION_FILTERS) ? d.ADMIN_CHANGE_LOG_ACTION_FILTERS.slice() : ADMIN_CHANGE_LOG_ACTION_FILTERS;
    configured = true;
    return getReadiness();
  }

  function getReadiness() {
    const requiredFunctions = {
      querySelector: typeof $ === "function",
      escapeHtml: typeof escapeHtml === "function",
      formatValue: typeof formatValue === "function",
      formatClock: typeof formatClock === "function",
      ensureApi: typeof ensureApi === "function",
      setStatus: typeof setStatus === "function",
      renderAdminChangeValueCell: typeof renderAdminChangeValueCell === "function",
      renderAdminRollbackMismatchValueCell: typeof renderAdminRollbackMismatchValueCell === "function",
      renderAdminOperationResultBanner: typeof renderAdminOperationResultBanner === "function",
      renderAdminCreateDeleteBlockerSummary: typeof renderAdminCreateDeleteBlockerSummary === "function",
      requireAdminWriteDevKeyForUi: typeof requireAdminWriteDevKeyForUi === "function",
      refreshAdminMasterCatalog: typeof refreshAdminMasterCatalog === "function",
      runPostWriteMasterApiVerification: typeof runPostWriteMasterApiVerification === "function",
      readMasterCatalogFiltersFromDom: typeof readMasterCatalogFiltersFromDom === "function",
    };
    const missingFunctions = Object.keys(requiredFunctions).filter((key) => !requiredFunctions[key]);
    const apiMethods = [
      "listAdminChangeLogs",
      "fetchAdminChangeLogDetail",
      "previewAdminChangeLogRollback",
      "applyAdminChangeLogRollback",
      "previewAdminCreateDeleteRollback",
      "applyAdminCreateDeleteRollback",
      "previewAdminCreateDeleteRestore",
      "applyAdminCreateDeleteRestore",
    ];
    const missingApiMethods = apiMethods.filter((key) => !(window.RpgGameApi && typeof window.RpgGameApi[key] === "function"));
    const exportedFunctions = [
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
      actionFilters: ADMIN_CHANGE_LOG_ACTION_FILTERS.slice(),
      sourceFile: "src/api/admin/admin-change-logs.js",
    };
  }

  function readChangeLogFiltersFromDom() {
    const limitEl = $("[data-admin-change-log-filter-limit]");
    const targetTypeEl = $("[data-admin-change-log-filter-target-type]");
    const targetIdEl = $("[data-admin-change-log-filter-target-id]");
    const actionEl = $("[data-admin-change-log-filter-action]");
    const changedKeyEl = $("[data-admin-change-log-filter-changed-key]");
    const appliedEl = $("[data-admin-change-log-filter-applied]");
    const sortEl = $("[data-admin-change-log-filter-sort]");
    const appliedValue = appliedEl && appliedEl.value ? appliedEl.value : "all";
    return {
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_CHANGE_LOG_LIMIT,
      targetType: targetTypeEl ? targetTypeEl.value.trim() : "",
      targetId: targetIdEl ? targetIdEl.value.trim() : "",
      action: actionEl ? actionEl.value.trim() : "",
      changedKey: changedKeyEl ? changedKeyEl.value.trim() : "",
      applied: appliedValue === "all" ? undefined : appliedValue === "true",
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_CHANGE_LOG_SORT,
    };
  }

  function resetChangeLogFilters(options) {
    const opts = options || {};
    const limitEl = $("[data-admin-change-log-filter-limit]");
    const targetTypeEl = $("[data-admin-change-log-filter-target-type]");
    const targetIdEl = $("[data-admin-change-log-filter-target-id]");
    const actionEl = $("[data-admin-change-log-filter-action]");
    const changedKeyEl = $("[data-admin-change-log-filter-changed-key]");
    const appliedEl = $("[data-admin-change-log-filter-applied]");
    const sortEl = $("[data-admin-change-log-filter-sort]");
    if (limitEl) limitEl.value = String(DEFAULT_CHANGE_LOG_LIMIT);
    if (targetTypeEl) targetTypeEl.value = "";
    if (targetIdEl) targetIdEl.value = "";
    if (actionEl) actionEl.value = "";
    if (changedKeyEl) changedKeyEl.value = "";
    if (appliedEl) appliedEl.value = "all";
    if (sortEl) sortEl.value = DEFAULT_CHANGE_LOG_SORT;
    if (!opts.silent) setStatus("관리자 변경 이력 필터 초기화", "info");
    return readChangeLogFiltersFromDom();
  }

  function describeChangeLogFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.targetType) parts.push(`targetType=${f.targetType}`);
    if (f.targetId) parts.push(`targetId=${f.targetId}`);
    if (f.action) parts.push(`action=${f.action}`);
    if (f.changedKey) parts.push(`changedKey=${f.changedKey}`);
    if (f.applied !== undefined && f.applied !== null) parts.push(`applied=${f.applied}`);
    if (f.sort && f.sort !== DEFAULT_CHANGE_LOG_SORT) parts.push(`sort=${f.sort}`);
    return parts.length ? parts.join(", ") : "필터 없음";
  }




  function buildSnapshotDiff(before, after, path) {
    const currentPath = path || "$";
    const beforeIsObject = before && typeof before === "object" && !Array.isArray(before);
    const afterIsObject = after && typeof after === "object" && !Array.isArray(after);
    if (beforeIsObject && afterIsObject) {
      const keys = Array.from(new Set([...Object.keys(before), ...Object.keys(after)])).sort();
      return keys.flatMap((key) => {
        const hasBefore = Object.prototype.hasOwnProperty.call(before, key);
        const hasAfter = Object.prototype.hasOwnProperty.call(after, key);
        const childPath = `${currentPath}.${key}`;
        if (!hasBefore) return [{ path: childPath, op: "add", before: null, after: after[key] }];
        if (!hasAfter) return [{ path: childPath, op: "remove", before: before[key], after: null }];
        return buildSnapshotDiff(before[key], after[key], childPath);
      });
    }
    if (Array.isArray(before) && Array.isArray(after)) {
      const changes = [];
      const maxLength = Math.max(before.length, after.length);
      for (let index = 0; index < maxLength; index += 1) {
        const childPath = `${currentPath}[${index}]`;
        if (index >= before.length) changes.push({ path: childPath, op: "add", before: null, after: after[index] });
        else if (index >= after.length) changes.push({ path: childPath, op: "remove", before: before[index], after: null });
        else changes.push(...buildSnapshotDiff(before[index], after[index], childPath));
      }
      return changes;
    }
    if (before !== after || typeof before !== typeof after) {
      return [{ path: currentPath, op: "replace", before, after }];
    }
    return [];
  }

  function isRollbackSnapshotConsistent(snapshot, diff) {
    if (!snapshot || snapshot.schemaVersion !== 1 || typeof snapshot.fingerprint !== "string" || snapshot.fingerprint.length !== 64) return false;
    const snapshotDiff = buildSnapshotDiff(snapshot.before, snapshot.after, "$");
    return JSON.stringify(snapshotDiff) === JSON.stringify(Array.isArray(diff) ? diff : []);
  }

  function renderUnifiedPreviewDiff(payload) {
    const diff = payload && Array.isArray(payload.unifiedDiff) ? payload.unifiedDiff : [];
    const snapshot = payload && payload.rollbackSnapshot ? payload.rollbackSnapshot : null;
    if (!diff.length && !snapshot) return "";
    const rows = diff.length ? diff.map((item) => `<tr><td>${escapeHtml(item.path || "$")}</td><td>${escapeHtml(item.op || "replace")}</td><td>${escapeHtml(formatValue(item.before))}</td><td>${escapeHtml(formatValue(item.after))}</td></tr>`).join("") : `<tr><td colspan="4">변경 없음</td></tr>`;
    const snapshotConsistent = snapshot ? isRollbackSnapshotConsistent(snapshot, diff) : false;
    const snapshotDetail = snapshot ? `
      <div class="draft-preview-summary">
        <span class="pill ${snapshotConsistent ? "good" : "blocked"}">snapshot/diff ${snapshotConsistent ? "일치" : "불일치"}</span>
        <span class="pill good">schema v${escapeHtml(formatValue(snapshot.schemaVersion))}</span>
        <span class="pill warn">target ${escapeHtml(formatValue(snapshot.domain))} / ${escapeHtml(formatValue(snapshot.targetId))}</span>
      </div>
      <div class="filter-help">fingerprint: <code>${escapeHtml(String(snapshot.fingerprint || ""))}</code></div>
      <details class="json-detail"><summary>Snapshot 기준값 확인</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>구분</th><th>값</th></tr></thead><tbody><tr><td>현재/적용 기준</td><td>${escapeHtml(formatValue(snapshot.before))}</td></tr><tr><td>되돌릴 기준</td><td>${escapeHtml(formatValue(snapshot.after))}</td></tr></tbody></table></div></details>
    ` : "";
    return `<details class="json-detail" open><summary>공통 Diff <span class="pill good">${escapeHtml(formatValue(diff.length))}</span></summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>경로</th><th>작업</th><th>이전</th><th>이후</th></tr></thead><tbody>${rows}</tbody></table></div>${snapshotDetail}</details>`;
  }
  function renderAdminChangeLogs(logsPayload) {
    const target = $(`[data-admin-change-log-table]`);
    const meta = $(`[data-admin-change-log-meta]`);
    if (!target) return;
    const payload = logsPayload || {};
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    const warnings = Array.isArray(payload.warnings) ? payload.warnings : (Array.isArray((payload.filters || {}).warnings) ? payload.filters.warnings : []);
    if (meta) meta.textContent = `${formatValue(rows.length)} / ${formatValue(payload.total)} logs · ${describeChangeLogFilters(payload.filters || {})} · before/after raw JSON hidden${warnings.length ? ` · warnings=${warnings.join(",")}` : ""}`;
    if (!rows.length) {
      if (payload.status === "schema_unavailable") {
        target.innerHTML = `<div class="empty warn">admin_change_logs 테이블을 아직 읽을 수 없습니다. backend 폴더에서 <code>python scripts/setup_dev_db.py --create-schema --verify</code>를 한 번 실행하면 기존 데이터 삭제 없이 누락 테이블을 만들 수 있습니다.</div>`;
        return;
      }
      target.innerHTML = `<div class="empty">아직 관리자 변경 이력이 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>상세</th><th>ID</th><th>대상</th><th>행</th><th>액션</th><th>변경 필드</th><th>사유</th><th>적용</th><th>시각</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td><button class="btn mini" type="button" data-admin-action="open-admin-change-log-detail" data-admin-change-log-id="${escapeHtml(row.id)}">보기</button></td>
              <td>${escapeHtml(formatValue(row.id))}</td>
              <td>${escapeHtml(formatValue(row.targetType))}</td>
              <td>${escapeHtml(formatValue(row.targetId))}</td>
              <td>${escapeHtml(formatValue(row.action))}</td>
              <td>${escapeHtml((row.changedKeys || []).join(", ") || "-")}${row.relationChangeCount ? ` <span class="pill warn">relation ${escapeHtml(formatValue(row.relationChangeCount))}</span>` : ""}</td>
              <td>${escapeHtml(formatValue(row.reason))}</td>
              <td><span class="pill ${row.applied ? "good" : "blocked"}">${escapeHtml(formatValue(row.applied))}</span></td>
              <td>${escapeHtml(formatClock(row.createdAt))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }


  function renderAdminChangeLogDetail(detailPayload) {
    currentAdminChangeLogDetailPayload = detailPayload && detailPayload.status === "loaded" ? detailPayload : null;
    const target = $(`[data-admin-change-log-detail]`);
    if (!target) return;
    const payload = detailPayload || {};
    if (!payload.id || payload.status !== "loaded") {
      target.innerHTML = `<div class="empty">변경 이력의 <strong>보기</strong> 버튼을 누르면 상세/되돌리기 미리보기가 여기에 표시됩니다.</div>`;
      return;
    }
    const changes = Array.isArray(payload.changes) ? payload.changes : [];
    const rollback = payload.rollback || {};
    const createDelete = payload.createDelete || {};
    const createDeleteRestore = payload.createDeleteRestore || {};
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(payload.rollback && payload.rollback.domain, change, "before", {})}</td><td>${renderAdminChangeValueCell(payload.rollback && payload.rollback.domain, change, "after", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">변경 필드 없음</td></tr>`;
    const relationCount = payload.relationChangeCount || changes.filter((change) => change.relation).length;
    target.innerHTML = `
      <div class="detail-card" data-admin-change-log-detail-card data-admin-change-log-id="${escapeHtml(payload.id)}">
        <div class="detail-title">변경 이력 #${escapeHtml(formatValue(payload.id))} <span class="pill ${rollback.available ? "good" : "blocked"}">rollback ${rollback.available ? "ready" : "blocked"}</span> <span class="pill ${createDelete.available ? "warn" : "blocked"}">create delete ${createDelete.available ? "ready" : "blocked"}</span> <span class="pill ${createDeleteRestore.available ? "good" : "blocked"}">restore ${createDeleteRestore.available ? "ready" : "blocked"}</span>${relationCount ? ` <span class="pill warn">relation ${escapeHtml(formatValue(relationCount))}</span>` : ""}</div>
        <div class="filter-help">대상: ${escapeHtml(formatValue(payload.targetType))} / 행 ${escapeHtml(formatValue(payload.targetId))} · action=${escapeHtml(formatValue(payload.action))} · applied=${escapeHtml(formatValue(payload.applied))}</div>
        <div class="filter-help">사유: ${escapeHtml(formatValue(payload.reason))} · 시각: ${escapeHtml(formatClock(payload.createdAt))}</div>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>이전 값</th><th>적용 값</th></tr></thead><tbody>${rows}</tbody></table></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-change-log-rollback">되돌리기 미리보기</button>
          <label class="apply-confirm-field"><span>되돌리기 확인 문구</span><input type="text" data-admin-rollback-confirm placeholder="${escapeHtml(ADMIN_ROLLBACK_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>되돌리기 사유</span><input type="text" data-admin-rollback-reason placeholder="예: 보스 HP 변경 되돌림" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-change-log-rollback">검사 후 되돌리기</button>
          <span class="pill warn">DB rollback: dev-key guarded</span>
        </div>
        <div class="edit-draft-result" data-admin-rollback-result><div class="empty">먼저 <strong>되돌리기 미리보기</strong>를 눌러 현재 DB 값이 이 변경 이력의 적용 값과 일치하는지 확인하세요.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-delete" ${createDelete.available ? "" : "disabled"}>생성 row 삭제 미리보기</button>
          <label class="apply-confirm-field"><span>생성 row 삭제 확인 문구</span><input type="text" data-admin-create-delete-confirm placeholder="${escapeHtml(ADMIN_CREATE_DELETE_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>생성 row 삭제 사유</span><input type="text" data-admin-create-delete-reason placeholder="예: 테스트 생성 row 삭제" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-delete" ${createDelete.available ? "" : "disabled"}>검사 후 생성 row 삭제</button>
          <span class="pill ${createDelete.available ? "warn" : "blocked"}">${createDelete.available ? "create-delete guarded" : "create-delete locked"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-delete-result><div class="empty">create action으로 생성된 제한 도메인 row만 삭제 되돌리기를 미리보기할 수 있습니다.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-delete-restore" ${createDeleteRestore.available ? "" : "disabled"}>삭제 row 복원 미리보기</button>
          <label class="apply-confirm-field"><span>삭제 row 복원 확인 문구</span><input type="text" data-admin-create-delete-restore-confirm placeholder="${escapeHtml(ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>삭제 row 복원 사유</span><input type="text" data-admin-create-delete-restore-reason placeholder="예: 실수로 삭제한 생성 row 복원" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-delete-restore" ${createDeleteRestore.available ? "" : "disabled"}>검사 후 삭제 row 복원</button>
          <span class="pill ${createDeleteRestore.available ? "good" : "blocked"}">${createDeleteRestore.available ? "create-delete restore guarded" : "restore locked"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-delete-restore-result><div class="empty">create_delete action으로 삭제된 제한 도메인 row만 복원 미리보기를 할 수 있습니다.</div></div>
      </div>
    `;
  }

  function readAdminRollbackControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-rollback-confirm]`);
    const reasonEl = $(`[data-admin-rollback-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_ROLLBACK_CONFIRM_TEXT,
    };
  }

  function renderAdminRollbackResult(payload) {
    const target = $(`[data-admin-rollback-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.acceptedChanges) && result.acceptedChanges.length ? result.acceptedChanges : (Array.isArray(result.changes) ? result.changes : []);
    const mismatches = Array.isArray(result.currentMismatches) ? result.currentMismatches : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td><td>${renderAdminChangeValueCell(result.domain, change, "before", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">되돌릴 변경 없음</td></tr>`;
    const relationCount = result.relationChangeCount || changes.filter((change) => change.relation).length;
    const mismatchRows = mismatches.length ? mismatches.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}${item.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "current")}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "expectedAfter")}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "rollbackTo")}</td></tr>
    `).join("") : `<tr><td colspan="4">현재 DB 값 일치</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${result.rollbackReady ? "good" : "blocked"}">rollbackReady: ${escapeHtml(formatValue(result.rollbackReady))}</span>
        <span class="pill ${result.currentMatchesAfter ? "good" : "blocked"}">currentMatchesAfter: ${escapeHtml(formatValue(result.currentMatchesAfter))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.rolledBack ? "good" : "warn"}">rolledBack: ${escapeHtml(formatValue(result.rolledBack === true))}</span>
        <span class="pill ${relationCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(relationCount || 0))}</span>
        ${result.rollbackChangeLogId ? `<span class="pill good">rollback log #${escapeHtml(formatValue(result.rollbackChangeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      ${renderUnifiedPreviewDiff(result)}
      <details class="json-detail" open><summary>되돌릴 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재/적용 값</th><th>되돌릴 값</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${mismatches.length ? "open" : ""}><summary>현재값 안전 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재 DB 값</th><th>이력의 적용 값</th><th>되돌릴 값</th></tr></thead><tbody>${mismatchRows}</tbody></table></div></details>
    `;
  }

  async function openAdminChangeLogDetail(changeLogId, options) {
    ensureApi();
    const id = Number(changeLogId || 0);
    if (!id) throw new Error("변경 이력 ID가 올바르지 않습니다.");
    const target = $(`[data-admin-change-log-detail]`);
    if (target) target.innerHTML = `<div class="empty">변경 이력 상세 불러오는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchAdminChangeLogDetail({ id, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminChangeLogDetail(payload);
    setStatus(`변경 이력 #${formatValue(id)} 상세 로드`, "ok");
    return response;
  }

  async function previewAdminChangeLogRollback(options) {
    ensureApi();
    const controls = readAdminRollbackControls();
    if (!controls.changeLogId) throw new Error("되돌릴 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="empty">되돌리기 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminChangeLogRollback({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminRollbackResult(payload);
    setStatus(`되돌리기 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.rollbackReady)}`, payload.rollbackReady ? "ok" : "error");
    return response;
  }

  async function applyAdminChangeLogRollback(options) {
    ensureApi();
    const controls = readAdminRollbackControls();
    if (!controls.changeLogId) throw new Error("되돌릴 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("변경 이력 되돌리기 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`되돌리기 확인 문구를 정확히 입력해야 합니다: ${ADMIN_ROLLBACK_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-rollback-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 이 변경 이력을 기준으로 DB 값을 이전 값으로 되돌릴까요? 현재값 안전 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("관리자 되돌리기를 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 되돌리기를 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminChangeLogRollback({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminRollbackResult(payload);
    if (payload.rolledBack) {
      const rollbackTarget = currentAdminChangeLogDetailPayload && currentAdminChangeLogDetailPayload.rollback ? currentAdminChangeLogDetailPayload.rollback : {};
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await runPostWriteMasterApiVerification(rollbackTarget.domain, rollbackTarget.id, {
        label: "되돌리기",
        contextLabel: `rollback log #${formatValue(payload.rollbackChangeLogId)} 적용 후 자동 확인`,
      });
    } else {
      setStatus(`되돌리기 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }


  function readAdminCreateDeleteControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-create-delete-confirm]`);
    const reasonEl = $(`[data-admin-create-delete-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_CREATE_DELETE_CONFIRM_TEXT,
    };
  }

  function renderAdminCreateDeleteResult(payload) {
    const target = $(`[data-admin-create-delete-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.changes) ? result.changes : [];
    const mismatches = Array.isArray(result.currentMismatches) ? result.currentMismatches : [];
    const dependencyChecks = Array.isArray(result.dependencyChecks) ? result.dependencyChecks : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td><td><span class="pill blocked">삭제 후 없음</span></td></tr>
    `).join("") : `<tr><td colspan="3">삭제 대상 필드 없음</td></tr>`;
    const mismatchRows = mismatches.length ? mismatches.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}</td><td>${escapeHtml(formatValue(item.current))}</td><td>${escapeHtml(formatValue(item.expectedAfter))}</td><td>${escapeHtml(formatValue(item.deleteEffect || "blocked"))}</td></tr>
    `).join("") : `<tr><td colspan="4">현재 DB 값이 생성 당시 값과 일치</td></tr>`;
    const dependencyRows = dependencyChecks.length ? dependencyChecks.map((item) => `
      <tr><td>${escapeHtml(formatValue(item.label))}</td><td>${escapeHtml(formatValue(item.target))}</td><td>${escapeHtml(formatValue(item.count))}</td><td><span class="pill ${item.blocksDelete ? "blocked" : "good"}">${item.blocksDelete ? "차단" : "통과"}</span><div class="filter-help">${escapeHtml(formatValue(item.note))}</div></td></tr>
    `).join("") : `<tr><td colspan="4">연결 검사 없음</td></tr>`;
    const dependencyCheckCount = Number(result.dependencyCheckCount !== undefined ? result.dependencyCheckCount : dependencyChecks.length);
    const dependencyBlockerGuardCount = Number(result.dependencyBlockerGuardCount !== undefined ? result.dependencyBlockerGuardCount : dependencyChecks.filter((item) => item && item.blocksDelete).length);
    const dependencyBlockerRowCount = Number(result.dependencyBlockerCount || 0);
    const currentMismatchCount = Number(result.currentMismatchCount || mismatches.length || 0);
    target.innerHTML = `
      ${renderAdminOperationResultBanner({
        tone: result.createDeleteReady ? "good" : "blocked",
        title: result.createDeleteReady ? "생성 row 삭제 가능" : "생성 row 삭제 차단",
        subtitle: result.createDeleteReady ? "현재값과 연결 데이터 검사를 통과했습니다." : "아래 차단 개수/현재값 불일치를 먼저 확인해야 합니다.",
        metrics: [
          { label: "현재값 불일치", value: currentMismatchCount, tone: currentMismatchCount ? "blocked" : "good" },
          { label: "연결 검사", value: dependencyCheckCount, tone: dependencyCheckCount ? "warn" : "good" },
          { label: "차단 guard", value: dependencyBlockerGuardCount, tone: dependencyBlockerGuardCount ? "blocked" : "good" },
          { label: "차단 row", value: dependencyBlockerRowCount, tone: dependencyBlockerRowCount ? "blocked" : "good" },
          { label: "dryRun", value: result.dryRun, tone: result.dryRun ? "warn" : "good" },
        ],
      })}
      <div class="draft-preview-summary">
        <span class="pill ${result.createDeleteReady ? "good" : "blocked"}">createDeleteReady: ${escapeHtml(formatValue(result.createDeleteReady))}</span>
        <span class="pill ${result.currentMatchesCreateValues ? "good" : "blocked"}">currentMatchesCreateValues: ${escapeHtml(formatValue(result.currentMatchesCreateValues))}</span>
        <span class="pill ${dependencyBlockerRowCount ? "blocked" : "good"}">dependency blockers: ${escapeHtml(formatValue(dependencyBlockerRowCount))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.deleted ? "good" : "warn"}">deleted: ${escapeHtml(formatValue(result.deleted === true))}</span>
        ${result.deleteChangeLogId ? `<span class="pill good">delete log #${escapeHtml(formatValue(result.deleteChangeLogId))}</span>` : ""}
      </div>
      ${renderAdminCreateDeleteBlockerSummary(dependencyChecks)}
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      ${renderUnifiedPreviewDiff(result)}
      <details class="json-detail" open><summary>삭제될 생성 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>생성 값</th><th>삭제 후</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${mismatches.length ? "open" : ""}><summary>현재값 안전 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재 DB 값</th><th>생성 당시 값</th><th>판정</th></tr></thead><tbody>${mismatchRows}</tbody></table></div></details>
      <details class="json-detail" open><summary>연결 데이터 삭제 차단 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>검사</th><th>대상</th><th>개수</th><th>판정</th></tr></thead><tbody>${dependencyRows}</tbody></table></div></details>
    `;
  }

  async function previewAdminCreateDeleteRollback(options) {
    ensureApi();
    const controls = readAdminCreateDeleteControls();
    if (!controls.changeLogId) throw new Error("생성 row 삭제를 검사할 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-create-delete-result]`);
    if (target) target.innerHTML = `<div class="empty">생성 row 삭제 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminCreateDeleteRollback({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteResult(payload);
    setStatus(`생성 row 삭제 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.createDeleteReady)}`, payload.createDeleteReady ? "ok" : "error");
    return response;
  }

  async function applyAdminCreateDeleteRollback(options) {
    ensureApi();
    const controls = readAdminCreateDeleteControls();
    if (!controls.changeLogId) throw new Error("생성 row 삭제를 적용할 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("생성 row 삭제 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`생성 row 삭제 확인 문구를 정확히 입력해야 합니다: ${ADMIN_CREATE_DELETE_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-create-delete-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 create 이력으로 생성된 row를 DB에서 삭제할까요? 현재값/연결 데이터 안전 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("생성 row 삭제 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-create-delete-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 row 삭제를 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminCreateDeleteRollback({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteResult(payload);
    if (payload.deleted) {
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminMasterCatalog({ filters: readMasterCatalogFiltersFromDom() });
      setStatus(`생성 row 삭제 완료: delete log #${formatValue(payload.deleteChangeLogId)}`, "ok");
    } else {
      setStatus(`생성 row 삭제 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }


  function readAdminCreateDeleteRestoreControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-create-delete-restore-confirm]`);
    const reasonEl = $(`[data-admin-create-delete-restore-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
    };
  }

  function renderAdminCreateDeleteRestoreResult(payload) {
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.changes) ? result.changes : [];
    const validationErrors = Array.isArray(result.validationErrors) ? result.validationErrors : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td><span class="pill blocked">복원 전 없음</span></td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">복원 대상 필드 없음</td></tr>`;
    const errorRows = validationErrors.length ? validationErrors.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}</td><td>${escapeHtml(formatValue(item.after))}</td><td>${escapeHtml(formatValue(item.reason || "blocked"))}</td></tr>
    `).join("") : `<tr><td colspan="3">복원 검증 오류 없음</td></tr>`;
    const validationErrorCount = Number(result.validationErrorCount || validationErrors.length || 0);
    const restoreConflictCount = Number(result.restoreConflictCount !== undefined ? result.restoreConflictCount : ((result.idConflict ? 1 : 0) + (result.codeConflict ? 1 : 0) + validationErrorCount));
    const relationChangeCount = Number(result.relationChangeCount || 0);
    target.innerHTML = `
      ${renderAdminOperationResultBanner({
        tone: result.createDeleteRestoreReady ? "good" : "blocked",
        title: result.createDeleteRestoreReady ? "삭제 row 복원 가능" : "삭제 row 복원 차단",
        subtitle: result.createDeleteRestoreReady ? "id/code 충돌과 생성 검증을 통과했습니다." : "id/code 충돌 또는 복원 검증 오류를 먼저 확인해야 합니다.",
        metrics: [
          { label: "충돌/오류", value: restoreConflictCount, tone: restoreConflictCount ? "blocked" : "good" },
          { label: "검증 오류", value: validationErrorCount, tone: validationErrorCount ? "blocked" : "good" },
          { label: "relation 값", value: relationChangeCount, tone: relationChangeCount ? "warn" : "good" },
          { label: "id 충돌", value: result.idConflict === true, tone: result.idConflict ? "blocked" : "good" },
          { label: "code 충돌", value: result.codeConflict === true, tone: result.codeConflict ? "blocked" : "good" },
        ],
      })}
      <div class="draft-preview-summary">
        <span class="pill ${result.createDeleteRestoreReady ? "good" : "blocked"}">createDeleteRestoreReady: ${escapeHtml(formatValue(result.createDeleteRestoreReady))}</span>
        <span class="pill ${result.targetRowMissing ? "good" : "blocked"}">targetRowMissing: ${escapeHtml(formatValue(result.targetRowMissing))}</span>
        <span class="pill ${result.idConflict ? "blocked" : "good"}">idConflict: ${escapeHtml(formatValue(result.idConflict === true))}</span>
        <span class="pill ${result.codeConflict ? "blocked" : "good"}">codeConflict: ${escapeHtml(formatValue(result.codeConflict === true))}</span>
        <span class="pill ${validationErrorCount ? "blocked" : "good"}">validation errors: ${escapeHtml(formatValue(validationErrorCount))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.restored ? "good" : "warn"}">restored: ${escapeHtml(formatValue(result.restored === true))}</span>
        ${result.restoreChangeLogId ? `<span class="pill good">restore log #${escapeHtml(formatValue(result.restoreChangeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      ${renderUnifiedPreviewDiff(result)}
      <details class="json-detail" open><summary>복원될 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>복원 전</th><th>복원 후</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${validationErrors.length ? "open" : ""}><summary>복원 검증 오류</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>값</th><th>사유</th></tr></thead><tbody>${errorRows}</tbody></table></div></details>
    `;
  }

  async function previewAdminCreateDeleteRestore(options) {
    ensureApi();
    const controls = readAdminCreateDeleteRestoreControls();
    if (!controls.changeLogId) throw new Error("복원할 create_delete 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (target) target.innerHTML = `<div class="empty">삭제 row 복원 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminCreateDeleteRestore({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteRestoreResult(payload);
    setStatus(`삭제 row 복원 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.createDeleteRestoreReady)}`, payload.createDeleteRestoreReady ? "ok" : "error");
    return response;
  }

  async function applyAdminCreateDeleteRestore(options) {
    ensureApi();
    const controls = readAdminCreateDeleteRestoreControls();
    if (!controls.changeLogId) throw new Error("복원할 create_delete 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("삭제 row 복원 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`삭제 row 복원 확인 문구를 정확히 입력해야 합니다: ${ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-create-delete-restore-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 create_delete 이력으로 삭제된 row를 DB에 다시 복원할까요? id/code 충돌 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("삭제 row 복원 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 삭제 row 복원을 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminCreateDeleteRestore({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteRestoreResult(payload);
    if (payload.restored) {
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminMasterCatalog({ filters: readMasterCatalogFiltersFromDom() });
      await runPostWriteMasterApiVerification(payload.domain, payload.id, {
        label: "생성 row 복원",
        contextLabel: `restore log #${formatValue(payload.restoreChangeLogId)} 적용 후 자동 확인`,
      });
      setStatus(`삭제 row 복원 완료: restore log #${formatValue(payload.restoreChangeLogId)}`, "ok");
    } else {
      setStatus(`삭제 row 복원 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }

  async function refreshAdminChangeLogs(options) {
    ensureApi();
    const opts = options || {};
    const filters = opts.filters || readChangeLogFiltersFromDom();
    const target = $(`[data-admin-change-log-table]`);
    if (target) target.innerHTML = `<div class="empty">변경 이력 불러오는 중...</div>`;
    const response = await window.RpgGameApi.listAdminChangeLogs({
      ...filters,
      timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminChangeLogs(payload);
    setStatus(`변경 이력 로드 · ${describeChangeLogFilters(filters)}`, "ok");
    return response;
  }

  async function applyAdminChangeLogActionShortcut(action) {
    const actionText = String(action || "").trim();
    if (!ADMIN_CHANGE_LOG_ACTION_FILTERS.includes(actionText)) {
      setStatus(`지원하지 않는 변경 이력 action 필터입니다: ${formatValue(actionText)}`, "error");
      return null;
    }
    const actionEl = $("[data-admin-change-log-filter-action]");
    const limitEl = $("[data-admin-change-log-filter-limit]");
    const sortEl = $("[data-admin-change-log-filter-sort]");
    if (actionEl) actionEl.value = actionText;
    if (limitEl) limitEl.value = "20";
    if (sortEl) sortEl.value = "created_desc";
    const response = await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
    setStatus(`변경 이력 action=${actionText} 필터를 적용했습니다.`, "ok");
    return response;
  }



  window.RpgAdminChangeLogs = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    readChangeLogFiltersFromDom,
    resetChangeLogFilters,
    describeChangeLogFilters,
    refreshAdminChangeLogs,
    renderAdminChangeLogs,
    openAdminChangeLogDetail,
    renderAdminChangeLogDetail,
    previewAdminChangeLogRollback,
    applyAdminChangeLogRollback,
    readAdminRollbackControls,
    renderAdminRollbackResult,
    buildSnapshotDiff,
    isRollbackSnapshotConsistent,
    renderUnifiedPreviewDiff,
    previewAdminCreateDeleteRollback,
    applyAdminCreateDeleteRollback,
    readAdminCreateDeleteControls,
    renderAdminCreateDeleteResult,
    previewAdminCreateDeleteRestore,
    applyAdminCreateDeleteRestore,
    readAdminCreateDeleteRestoreControls,
    renderAdminCreateDeleteRestoreResult,
    applyAdminChangeLogActionShortcut,
  };
})();
