(function () {
  "use strict";

  const VERSION = "v256.admin-preview-live-api-render-check";
  const DEFAULT_TIMEOUT_MS = 3500;
  const ALLOWED_PREVIEW_METHODS = [
    "previewAdminMasterDataCreate",
    "previewAdminMasterDataEdit",
    "previewAdminChangeLogRollback",
    "previewAdminCreateDeleteRollback",
    "previewAdminCreateDeleteRestore",
  ];

  const LIVE_PREVIEW_KINDS = [
    {
      id: "create",
      label: "현재 Create Preview API",
      description: "현재 신규 row 생성 초안 값을 실제 create-preview API로 검증하고 공통 렌더러로 표시합니다.",
      method: "previewAdminMasterDataCreate",
      reader: readCreatePreviewArgs,
      readyKey: "createApplyReady",
    },
    {
      id: "edit",
      label: "현재 Edit Preview API",
      description: "현재 편집 초안 값을 실제 edit-preview API로 검증하고 공통 렌더러로 표시합니다.",
      method: "previewAdminMasterDataEdit",
      reader: readEditPreviewArgs,
      readyKey: "editApplyReady",
    },
    {
      id: "rollback",
      label: "Rollback Preview API",
      description: "현재 열린 변경 이력의 rollback-preview API 응답을 공통 렌더러로 표시합니다.",
      method: "previewAdminChangeLogRollback",
      reader: readRollbackPreviewArgs,
      readyKey: "rollbackReady",
    },
    {
      id: "create-delete",
      label: "생성 row 삭제 Preview API",
      description: "현재 열린 create 이력의 create-delete-preview API 응답을 공통 렌더러로 표시합니다.",
      method: "previewAdminCreateDeleteRollback",
      reader: readCreateDeletePreviewArgs,
      readyKey: "createDeleteReady",
    },
    {
      id: "restore",
      label: "삭제 row 복원 Preview API",
      description: "현재 열린 create_delete 이력의 create-delete-restore-preview API 응답을 공통 렌더러로 표시합니다.",
      method: "previewAdminCreateDeleteRestore",
      reader: readCreateDeleteRestorePreviewArgs,
      readyKey: "createDeleteRestoreReady",
    },
  ];

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
    if (typeof value === "object") {
      try { return JSON.stringify(value); }
      catch (_error) { return String(value); }
    }
    return String(value);
  }

  function getRenderer() {
    return window.RpgAdminPreviewDiff || null;
  }

  function getTarget() {
    return document.querySelector("[data-admin-live-preview-result]");
  }

  function isAllowedPreviewMethod(methodName) {
    return ALLOWED_PREVIEW_METHODS.includes(methodName);
  }

  function getPreviewMethod(methodName) {
    if (!isAllowedPreviewMethod(methodName)) throw new Error(`허용되지 않은 Preview API입니다: ${methodName}`);
    if (!window.RpgGameApi || typeof window.RpgGameApi[methodName] !== "function") {
      throw new Error(`RpgGameApi.${methodName} 함수를 찾을 수 없습니다.`);
    }
    return window.RpgGameApi[methodName].bind(window.RpgGameApi);
  }

  function readCreatePreviewArgs() {
    const moduleApi = window.RpgAdminCreateLifecycle;
    if (!moduleApi || typeof moduleApi.readAdminCreateDraftValues !== "function") {
      return { ok: false, reason: "신규 row 생성 모듈을 불러오지 못했습니다." };
    }
    const values = moduleApi.readAdminCreateDraftValues();
    if (!values || !values.ok) return { ok: false, reason: values && values.reason ? values.reason : "생성 설계를 먼저 불러와 주세요." };
    return {
      ok: true,
      args: {
        domain: values.domain,
        draft: values.draft || {},
        reason: values.reason || undefined,
        dryRun: true,
        timeoutMs: DEFAULT_TIMEOUT_MS,
      },
      summary: `domain=${values.domain || "-"} · fields=${values.fieldCount || 0}`,
    };
  }

  function readEditPreviewArgs() {
    const moduleApi = window.RpgAdminEditDraft;
    if (!moduleApi || typeof moduleApi.readAdminEditDraftValues !== "function") {
      return { ok: false, reason: "편집 초안 모듈을 불러오지 못했습니다." };
    }
    const values = moduleApi.readAdminEditDraftValues();
    if (!values || !values.ok || !values.id) return { ok: false, reason: "마스터 데이터 상세를 먼저 열고 편집 초안을 준비해 주세요." };
    const controls = typeof moduleApi.readAdminEditApplyControls === "function" ? moduleApi.readAdminEditApplyControls() : {};
    return {
      ok: true,
      args: {
        domain: values.domain,
        id: values.id,
        draft: values.draft || {},
        baseValues: values.originals || undefined,
        reason: controls.reason || undefined,
        dryRun: true,
        timeoutMs: DEFAULT_TIMEOUT_MS,
      },
      summary: `domain=${values.domain || "-"} · id=${values.id} · fields=${values.fieldCount || 0}`,
    };
  }

  function readRollbackPreviewArgs() {
    const moduleApi = window.RpgAdminChangeLogs;
    if (!moduleApi || typeof moduleApi.readAdminRollbackControls !== "function") {
      return { ok: false, reason: "변경 이력 모듈을 불러오지 못했습니다." };
    }
    const controls = moduleApi.readAdminRollbackControls();
    if (!controls || !controls.changeLogId) return { ok: false, reason: "되돌릴 변경 이력 상세를 먼저 열어 주세요." };
    return {
      ok: true,
      args: {
        id: controls.changeLogId,
        reason: controls.reason || undefined,
        dryRun: true,
        timeoutMs: DEFAULT_TIMEOUT_MS,
      },
      summary: `changeLogId=${controls.changeLogId}`,
    };
  }

  function readCreateDeletePreviewArgs() {
    const moduleApi = window.RpgAdminChangeLogs;
    if (!moduleApi || typeof moduleApi.readAdminCreateDeleteControls !== "function") {
      return { ok: false, reason: "생성 row 삭제 모듈을 불러오지 못했습니다." };
    }
    const controls = moduleApi.readAdminCreateDeleteControls();
    if (!controls || !controls.changeLogId) return { ok: false, reason: "삭제 Preview를 확인할 create 변경 이력 상세를 먼저 열어 주세요." };
    return {
      ok: true,
      args: {
        id: controls.changeLogId,
        reason: controls.reason || undefined,
        dryRun: true,
        timeoutMs: DEFAULT_TIMEOUT_MS,
      },
      summary: `changeLogId=${controls.changeLogId}`,
    };
  }

  function readCreateDeleteRestorePreviewArgs() {
    const moduleApi = window.RpgAdminChangeLogs;
    if (!moduleApi || typeof moduleApi.readAdminCreateDeleteRestoreControls !== "function") {
      return { ok: false, reason: "삭제 row 복원 모듈을 불러오지 못했습니다." };
    }
    const controls = moduleApi.readAdminCreateDeleteRestoreControls();
    if (!controls || !controls.changeLogId) return { ok: false, reason: "복원 Preview를 확인할 create_delete 변경 이력 상세를 먼저 열어 주세요." };
    return {
      ok: true,
      args: {
        id: controls.changeLogId,
        reason: controls.reason || undefined,
        dryRun: true,
        timeoutMs: DEFAULT_TIMEOUT_MS,
      },
      summary: `changeLogId=${controls.changeLogId}`,
    };
  }

  function getReadyValue(payload, kind) {
    if (!payload || !kind || !kind.readyKey) return undefined;
    return payload[kind.readyKey];
  }

  function collectWarnings(payload) {
    const data = payload || {};
    const warnings = [];
    if (Array.isArray(data.warnings)) warnings.push(...data.warnings);
    if (Array.isArray(data.validationErrors)) {
      data.validationErrors.forEach((item) => warnings.push(item.reason || item.message || item.key || "validation error"));
    }
    if (Array.isArray(data.rejectedFields)) {
      data.rejectedFields.forEach((item) => warnings.push(item.reason || item.key || "rejected field"));
    }
    if (Array.isArray(data.currentMismatches) && data.currentMismatches.length) warnings.push(`현재값 불일치 ${data.currentMismatches.length}건`);
    return warnings.filter((item) => item !== null && item !== undefined && String(item).trim());
  }

  function buildLiveSummaryOptions(kind, payload, response, readResult) {
    const data = payload || {};
    const readyValue = getReadyValue(data, kind);
    const blocked = readyValue === false || Number(data.errorCount || 0) > 0 || Number(data.rejectedCount || 0) > 0;
    const tone = blocked ? "blocked" : (readyValue === true ? "good" : "warn");
    const title = `${kind.label} ${blocked ? "차단/확인 필요" : "응답 수신"}`;
    const subtitle = `실제 Preview API 응답을 공통 렌더러로 표시했습니다. ${readResult && readResult.summary ? readResult.summary : ""}`.trim();
    const diffCount = Number(data.unifiedDiffCount !== undefined ? data.unifiedDiffCount : (Array.isArray(data.unifiedDiff) ? data.unifiedDiff.length : 0));
    return {
      banner: {
        tone,
        title,
        subtitle,
        metrics: [
          { label: "ok", value: response && response.ok !== undefined ? response.ok : true, tone: response && response.ok === false ? "blocked" : "good" },
          { label: "diff", value: diffCount, tone: diffCount ? "warn" : "good" },
          { label: "errors", value: data.errorCount || data.rejectedCount || 0, tone: (data.errorCount || data.rejectedCount) ? "blocked" : "good" },
        ],
      },
      badges: [
        { label: kind.readyKey || "ready", value: readyValue, tone: readyValue === false ? "blocked" : (readyValue === true ? "good" : "warn"), hidden: readyValue === undefined },
        { label: "dryRun", value: data.dryRun, tone: data.dryRun === false ? "blocked" : "warn", hidden: data.dryRun === undefined },
        { label: "writeBlocked", value: data.writeBlocked, tone: data.writeBlocked === false ? "blocked" : "good", hidden: data.writeBlocked === undefined },
        { label: "status", value: data.status, tone: tone, hidden: !data.status },
        { label: "schema", value: data.previewSchemaVersion, tone: "good", hidden: data.previewSchemaVersion === undefined },
      ],
      warnings: collectWarnings(data),
      note: "이 영역은 실제 Preview API 응답 표시만 수행합니다. apply API, confirmText, write header는 사용하지 않습니다.",
    };
  }

  function stringifyForDetail(value) {
    try { return JSON.stringify(value, null, 2); }
    catch (_error) { return String(value); }
  }

  function renderLivePreviewResult(kind, response, readResult) {
    const target = getTarget();
    if (!target) return false;
    const renderer = getRenderer();
    const payload = response && response.payload ? response.payload : {};
    if (!renderer || typeof renderer.renderPreviewResultSummary !== "function" || typeof renderer.renderUnifiedPreviewDiff !== "function") {
      target.innerHTML = '<div class="empty">공통 Preview 렌더러를 불러오지 못했습니다.</div>';
      return false;
    }
    target.innerHTML = `
      <div class="filter-help preview-verification-safety">실제 Preview API 응답 · dryRun 전용 · apply/write 호출 없음</div>
      ${renderer.renderPreviewResultSummary(payload, buildLiveSummaryOptions(kind, payload, response, readResult))}
      ${renderer.renderUnifiedPreviewDiff(payload)}
      <details class="json-detail"><summary>실제 Preview 응답 body 확인</summary><pre>${escapeHtml(stringifyForDetail(response))}</pre></details>
    `;
    return true;
  }

  function renderLivePreviewError(kind, error) {
    const target = getTarget();
    if (!target) return false;
    target.innerHTML = `
      <div class="create-result-banner blocked">
        <div class="create-result-banner-title">${escapeHtml(kind ? kind.label : "Preview API")} 실행 불가</div>
        <div class="create-result-banner-subtitle">${escapeHtml(error && error.message ? error.message : error)}</div>
      </div>
      <div class="filter-help preview-result-note">실제 write 작업은 실행하지 않았습니다.</div>
    `;
    return true;
  }

  function setActiveKind(kindId) {
    document.querySelectorAll("[data-admin-live-preview-kind]").forEach((button) => {
      button.classList.toggle("primary", button.getAttribute("data-admin-live-preview-kind") === kindId);
    });
  }

  async function runLivePreview(kindId, options) {
    const kind = LIVE_PREVIEW_KINDS.find((item) => item.id === kindId) || LIVE_PREVIEW_KINDS[0];
    setActiveKind(kind.id);
    const target = getTarget();
    if (target) target.innerHTML = `<div class="empty">${escapeHtml(kind.label)} 응답을 불러오는 중...</div>`;
    try {
      const readResult = kind.reader(options || {});
      if (!readResult || !readResult.ok) throw new Error(readResult && readResult.reason ? readResult.reason : "Preview 입력값을 읽지 못했습니다.");
      const method = getPreviewMethod(kind.method);
      const response = await method(readResult.args || {});
      renderLivePreviewResult(kind, response, readResult);
      return response;
    } catch (error) {
      renderLivePreviewError(kind, error);
      return { ok: false, error: error && error.message ? error.message : String(error) };
    }
  }

  function renderLivePreviewButtons() {
    const target = document.querySelector("[data-admin-live-preview-actions]");
    if (!target) return false;
    target.innerHTML = LIVE_PREVIEW_KINDS.map((kind) => `
      <button class="btn mini" type="button" data-admin-live-preview-kind="${escapeHtml(kind.id)}" title="${escapeHtml(kind.description)}">${escapeHtml(kind.label)}</button>
    `).join("");
    return true;
  }

  function bindEvents() {
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-admin-live-preview-kind]");
      if (!button) return;
      runLivePreview(button.getAttribute("data-admin-live-preview-kind"));
    });
  }

  function init() {
    renderLivePreviewButtons();
    bindEvents();
  }

  function getReadiness() {
    const api = window.RpgGameApi || {};
    const apiMethodsReady = ALLOWED_PREVIEW_METHODS.every((methodName) => typeof api[methodName] === "function");
    return {
      version: VERSION,
      ok: true,
      dryRunOnly: true,
      writeOperations: 0,
      applyMethodsBlocked: true,
      allowedPreviewMethods: ALLOWED_PREVIEW_METHODS.slice(),
      livePreviewKindCount: LIVE_PREVIEW_KINDS.length,
      rendererReady: !!getRenderer(),
      apiMethodsReady,
      sourceFile: "src/api/admin/admin-preview-live-verification.js",
    };
  }

  window.RpgAdminPreviewLiveVerification = {
    VERSION,
    ALLOWED_PREVIEW_METHODS,
    LIVE_PREVIEW_KINDS,
    isAllowedPreviewMethod,
    renderLivePreviewButtons,
    runLivePreview,
    renderLivePreviewResult,
    getReadiness,
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
