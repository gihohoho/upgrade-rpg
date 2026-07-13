(function () {
  "use strict";

  const VERSION = "v254.admin-preview-result-summary-shared-renderer";

  function defaultEscapeHtml(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function defaultFormatValue(value) {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "object") {
      try {
        return JSON.stringify(value);
      } catch (_error) {
        return String(value);
      }
    }
    return String(value);
  }

  function valuesEqual(left, right) {
    if (left === right) return true;
    try {
      return JSON.stringify(left) === JSON.stringify(right);
    } catch (_error) {
      return false;
    }
  }

  function buildSnapshotDiff(before, after, path) {
    const currentPath = path || "$";
    if (valuesEqual(before, after)) return [];

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

    return [{ path: currentPath, op: "replace", before, after }];
  }

  function isRollbackSnapshotConsistent(snapshot, diff) {
    if (!snapshot || Number(snapshot.schemaVersion) !== 1) return false;
    if (typeof snapshot.fingerprint !== "string" || snapshot.fingerprint.length !== 64) return false;
    return valuesEqual(buildSnapshotDiff(snapshot.before, snapshot.after, "$"), Array.isArray(diff) ? diff : []);
  }


  function renderResultBanner(options) {
    const opts = options || {};
    const escapeHtml = typeof opts.escapeHtml === "function" ? opts.escapeHtml : defaultEscapeHtml;
    const formatValue = typeof opts.formatValue === "function" ? opts.formatValue : defaultFormatValue;
    const metrics = Array.isArray(opts.metrics) ? opts.metrics : [];
    const tone = opts.tone || "warn";
    const metricHtml = metrics.length ? `
      <div class="create-result-metric-grid">
        ${metrics.map((metric) => `
          <div class="create-result-metric ${escapeHtml(metric.tone || "")}">
            <span>${escapeHtml(metric.label || "항목")}</span>
            <strong>${escapeHtml(formatValue(metric.value))}</strong>
          </div>
        `).join("")}
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

  function renderPreviewResultSummary(payload, options) {
    const data = payload || {};
    const opts = options || {};
    const escapeHtml = typeof opts.escapeHtml === "function" ? opts.escapeHtml : defaultEscapeHtml;
    const formatValue = typeof opts.formatValue === "function" ? opts.formatValue : defaultFormatValue;
    const badges = Array.isArray(opts.badges) ? opts.badges : [];
    const warnings = Array.isArray(opts.warnings) ? opts.warnings.filter((item) => item !== null && item !== undefined && String(item).trim()) : [];
    const visibleBadges = badges.filter((badge) => badge && badge.hidden !== true);
    const banner = opts.banner ? renderResultBanner({ ...opts.banner, escapeHtml, formatValue }) : "";
    const badgeHtml = visibleBadges.length ? `
      <div class="draft-preview-summary">
        ${visibleBadges.map((badge) => `<span class="pill ${escapeHtml(badge.tone || "")}">${escapeHtml(badge.label || "status")}: ${escapeHtml(formatValue(badge.value))}</span>`).join("")}
      </div>
    ` : "";
    const warningHtml = warnings.length ? `<div class="filter-help preview-result-warning">warnings: ${escapeHtml(warnings.join(", "))}</div>` : "";
    const note = opts.note !== undefined ? opts.note : data.note;
    const noteHtml = note ? `<div class="filter-help preview-result-note">${escapeHtml(note)}</div>` : "";
    return `${banner}${badgeHtml}${warningHtml}${noteHtml}`;
  }

  function renderUnifiedPreviewDiff(payload, options) {
    const settings = options || {};
    const escapeHtml = typeof settings.escapeHtml === "function" ? settings.escapeHtml : defaultEscapeHtml;
    const formatValue = typeof settings.formatValue === "function" ? settings.formatValue : defaultFormatValue;
    const diff = payload && Array.isArray(payload.unifiedDiff) ? payload.unifiedDiff : [];
    const snapshot = payload && payload.rollbackSnapshot ? payload.rollbackSnapshot : null;
    if (!diff.length && !snapshot) return "";

    const rows = diff.length
      ? diff.map((item) => `<tr><td>${escapeHtml(item.path || "$")}</td><td>${escapeHtml(item.op || "replace")}</td><td>${escapeHtml(formatValue(item.before))}</td><td>${escapeHtml(formatValue(item.after))}</td></tr>`).join("")
      : `<tr><td colspan="4">변경 없음</td></tr>`;

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

  function getReadiness() {
    return {
      version: VERSION,
      ok: true,
      buildSnapshotDiffReady: typeof buildSnapshotDiff === "function",
      snapshotConsistencyReady: typeof isRollbackSnapshotConsistent === "function",
      resultBannerReady: typeof renderResultBanner === "function",
      resultSummaryReady: typeof renderPreviewResultSummary === "function",
      rendererReady: typeof renderUnifiedPreviewDiff === "function",
      sourceFile: "src/api/admin/admin-preview-diff.js",
    };
  }

  window.RpgAdminPreviewDiff = {
    VERSION,
    buildSnapshotDiff,
    isRollbackSnapshotConsistent,
    renderResultBanner,
    renderPreviewResultSummary,
    renderUnifiedPreviewDiff,
    getReadiness,
  };
})();
