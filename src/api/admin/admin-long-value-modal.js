(function () {
  "use strict";

  const VERSION = "v266.admin-long-value-modal-compact";
  let bound = false;

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function decodeAttr(value) {
    const textarea = document.createElement("textarea");
    textarea.innerHTML = String(value || "");
    return textarea.value;
  }

  function truncateText(value, maxLength) {
    const text = String(value ?? "");
    const limit = Number(maxLength) || 44;
    if (text.length <= limit) return text;
    return `${text.slice(0, Math.max(0, limit - 1))}…`;
  }

  function renderLongValueTrigger(title, body, options) {
    const opts = options || {};
    const text = String(body ?? "");
    const preview = truncateText(text.replace(/\s+/g, " ").trim(), opts.previewLength || 28);
    const label = opts.buttonLabel || "전체";
    const safeTitle = escapeHtml(title || "값 전체 보기");
    const safeBody = escapeHtml(text);
    const safePreview = escapeHtml(preview || "-");
    return `
      <span class="catalog-cell-compact">
        <span class="catalog-cell-preview" title="${safeBody}">${safePreview}</span>
        <button class="btn mini compact-value-open" type="button" data-admin-long-value-open data-admin-long-value-title="${safeTitle}" data-admin-long-value-body="${safeBody}">${escapeHtml(label)}</button>
      </span>
    `;
  }

  function getModal() {
    return document.querySelector("[data-admin-long-value-modal]");
  }

  function openLongValueModal(title, body) {
    const modal = getModal();
    if (!modal) return false;
    const titleTarget = modal.querySelector("[data-admin-long-value-title]");
    const subtitleTarget = modal.querySelector("[data-admin-long-value-subtitle]");
    const bodyTarget = modal.querySelector("[data-admin-long-value-body]");
    if (titleTarget) titleTarget.textContent = title || "값 전체 보기";
    if (subtitleTarget) subtitleTarget.textContent = `${String(body ?? "").length}자 · 표에서는 줄임 표시`;
    if (bodyTarget) bodyTarget.textContent = String(body ?? "");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    const close = modal.querySelector("[data-admin-long-value-action='close']");
    if (close && close.focus) close.focus();
    return true;
  }

  function closeLongValueModal() {
    const modal = getModal();
    if (!modal) return false;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    return true;
  }

  function handleClick(event) {
    const openButton = event.target && event.target.closest ? event.target.closest("[data-admin-long-value-open]") : null;
    if (openButton) {
      event.preventDefault();
      openLongValueModal(decodeAttr(openButton.getAttribute("data-admin-long-value-title")), decodeAttr(openButton.getAttribute("data-admin-long-value-body")));
      return;
    }
    const closeButton = event.target && event.target.closest ? event.target.closest("[data-admin-long-value-action='close']") : null;
    if (closeButton) {
      event.preventDefault();
      closeLongValueModal();
      return;
    }
    const modal = getModal();
    if (modal && event.target === modal) closeLongValueModal();
  }

  function handleKeydown(event) {
    if (event.key === "Escape") closeLongValueModal();
  }

  function initializeAdminLongValueModal() {
    if (!bound) {
      bound = true;
      document.addEventListener("click", handleClick);
      document.addEventListener("keydown", handleKeydown);
    }
    return getAdminLongValueModalReadiness();
  }

  function getAdminLongValueModalReadiness() {
    const modalReady = !!getModal();
    return {
      ok: modalReady && bound,
      version: VERSION,
      modalReady,
      bound,
      routeChanges: 0,
      apiBodyChanges: 0,
      writeOperations: 0,
    };
  }

  window.RpgAdminLongValueModal = {
    VERSION,
    escapeHtml,
    truncateText,
    renderLongValueTrigger,
    openLongValueModal,
    closeLongValueModal,
    initializeAdminLongValueModal,
    getAdminLongValueModalReadiness,
  };
  window.initializeAdminLongValueModal = initializeAdminLongValueModal;
  window.getAdminLongValueModalReadiness = getAdminLongValueModalReadiness;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAdminLongValueModal, { once: true });
  } else {
    initializeAdminLongValueModal();
  }
})();
