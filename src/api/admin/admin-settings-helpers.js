(function () {
  "use strict";

  const VERSION = "v197.admin-settings-helpers-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v196.admin-field-help-split v195.admin-thin-entry-cleanup v194.admin-bootstrap-bindings-readiness v113.admin-readonly-overview-url-helper";

  let configured = false;
  let ADMIN_WRITE_DEV_KEY_EXAMPLE = "local-admin-dev-key";
  let $ = (selector) => document.querySelector(selector);
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let setStatus = () => undefined;
  let ensureApi = () => {
    if (!window.RpgGameApi) throw new Error("RpgGameApi를 찾을 수 없습니다. game-api-client.js 로딩 순서를 확인하세요.");
    return window.RpgGameApi;
  };

  function configure(deps) {
    const d = deps || {};
    if (typeof d.querySelector === "function") $ = d.querySelector;
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.setStatus === "function") setStatus = d.setStatus;
    if (typeof d.ensureApi === "function") ensureApi = d.ensureApi;
    if (d.ADMIN_WRITE_DEV_KEY_EXAMPLE) ADMIN_WRITE_DEV_KEY_EXAMPLE = String(d.ADMIN_WRITE_DEV_KEY_EXAMPLE);
    configured = true;
    return getReadiness({ log: false });
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
    return { currentUrl, gameUrl: getGamePageUrl(), hasCurrentTarget: !!currentTarget, hasGameLink: !!gameLink };
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
    if (!input || !window.RpgGameApi) return undefined;
    input.value = window.RpgGameApi.getApiBaseUrl();
    return input.value;
  }

  function getAdminWriteKeyInput() {
    return $("[data-admin-write-dev-key]");
  }

  function hasAdminWriteDevKey() {
    return !!(window.RpgGameApi && window.RpgGameApi.hasAdminWriteDevKey && window.RpgGameApi.hasAdminWriteDevKey());
  }

  function renderAdminWriteKeyStatus() {
    const target = $("[data-admin-write-key-status]");
    if (!target || !window.RpgGameApi) return false;
    const ready = hasAdminWriteDevKey();
    target.innerHTML = ready
      ? `<span class="pill good">write key set</span>`
      : `<span class="pill blocked">write key missing</span>`;
    return ready;
  }

  function syncAdminWriteDevKeyInput() {
    const input = getAdminWriteKeyInput();
    if (input && window.RpgGameApi && window.RpgGameApi.getAdminWriteDevKey) input.value = window.RpgGameApi.getAdminWriteDevKey();
    renderAdminWriteKeyStatus();
    return input ? input.value : "";
  }

  function saveAdminWriteDevKeyFromInput() {
    ensureApi();
    const input = getAdminWriteKeyInput();
    const value = input ? input.value.trim() : "";
    if (!value) {
      const error = new Error(`관리자 쓰기 dev key를 입력해 주세요. 로컬 기본 예시는 ${ADMIN_WRITE_DEV_KEY_EXAMPLE} 입니다.`);
      setStatus(error.message, "error");
      renderAdminWriteKeyStatus();
      throw error;
    }
    window.RpgGameApi.setAdminWriteDevKey(value);
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key가 이 브라우저 탭에 저장됐습니다.", "ok");
    return value;
  }

  function clearAdminWriteDevKey() {
    ensureApi();
    window.RpgGameApi.clearAdminWriteDevKey();
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key를 지웠습니다. 실제 적용/되돌리기는 다시 잠깁니다.", "info");
    return "";
  }

  function requireAdminWriteDevKeyForUi(actionLabel) {
    if (hasAdminWriteDevKey()) return true;
    const message = `${actionLabel || "관리자 쓰기 작업"} 전에 관리자 쓰기 dev key를 먼저 설정해 주세요.`;
    setStatus(message, "error");
    const target = $("[data-admin-edit-draft-result]") || $("[data-admin-rollback-result]");
    if (target) target.innerHTML = `<div class="error">${escapeHtml(message)}<br>관리자 페이지의 <strong>쓰기 잠금</strong> 영역에서 dev key를 저장한 뒤 다시 시도하세요.</div>`;
    throw new Error(message);
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
    const defaultApiBaseUrl = typeof window.RpgGameApi.getEnvironmentDefaultApiBaseUrl === "function"
      ? window.RpgGameApi.getEnvironmentDefaultApiBaseUrl()
      : window.RpgGameApi.DEFAULT_API_BASE_URL;
    const next = window.RpgGameApi.setApiBaseUrl(defaultApiBaseUrl);
    syncApiInput();
    setStatus(`API URL 기본값 복구: ${next}`, "ok");
    return next;
  }

  function getReadiness(options) {
    const opts = options || {};
    const requiredApiMethods = [
      "getApiBaseUrl",
      "setApiBaseUrl",
      "getAdminWriteDevKey",
      "setAdminWriteDevKey",
      "clearAdminWriteDevKey",
      "hasAdminWriteDevKey",
    ].map((key) => ({ key, ok: !!(window.RpgGameApi && typeof window.RpgGameApi[key] === "function") }));
    const domTargets = [
      "[data-admin-current-url]",
      "[data-admin-game-url]",
      "[data-admin-api-base-url]",
      "[data-admin-write-dev-key]",
      "[data-admin-write-key-status]",
      "[data-admin-status]",
    ].map((selector) => ({ selector, ok: !!$(selector) }));
    const missingApiMethods = requiredApiMethods.filter((item) => !item.ok).map((item) => item.key);
    const missingDomTargets = domTargets.filter((item) => !item.ok).map((item) => item.selector);
    const ok = configured && missingApiMethods.length === 0 && missingDomTargets.length === 0;
    const readiness = {
      ok,
      version: VERSION,
      configured,
      requiredApiMethods,
      domTargets,
      missingApiMethods,
      missingDomTargets,
      hasRpgGameApi: !!window.RpgGameApi,
      hasClipboardApi: !!(typeof navigator !== "undefined" && navigator.clipboard && typeof navigator.clipboard.writeText === "function"),
      currentUrl: getCurrentAdminPageUrl(),
      gameUrl: getGamePageUrl(),
      apiBaseUrl: window.RpgGameApi && window.RpgGameApi.getApiBaseUrl ? window.RpgGameApi.getApiBaseUrl() : "",
      hasAdminWriteDevKey: hasAdminWriteDevKey(),
    };
    if (opts.log) console.log("[admin-settings-helpers] readiness", readiness);
    return readiness;
  }

  window.RpgAdminSettingsHelpers = {
    VERSION,
    LEGACY_SMOKE_VERSION_MARKERS,
    configure,
    getReadiness,
    getApiInput,
    buildSiblingPageUrl,
    getCurrentAdminPageUrl,
    getGamePageUrl,
    syncLocationHints,
    copyCurrentAdminPageUrl,
    syncApiInput,
    getAdminWriteKeyInput,
    hasAdminWriteDevKey,
    renderAdminWriteKeyStatus,
    syncAdminWriteDevKeyInput,
    saveAdminWriteDevKeyFromInput,
    clearAdminWriteDevKey,
    requireAdminWriteDevKeyForUi,
    saveApiBaseUrlFromInput,
    resetApiBaseUrl,
  };
})();
