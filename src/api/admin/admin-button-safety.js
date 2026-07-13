(function () {
  "use strict";

  const VERSION = "v266.admin-button-safety-color-only";
  let observer = null;
  let bound = false;

  const RISK_LABELS = {
    safe: "조회",
    preview: "Preview",
    write: "적용주의",
    danger: "고위험",
  };

  function classifyButton(button) {
    const action = String(button.getAttribute("data-admin-action") || "").toLowerCase();
    const text = String(button.textContent || "").toLowerCase();
    const source = `${action} ${text}`;
    if (/apply.*rollback|delete|restore|rollback|삭제|복원|되돌리기/.test(source)) return "danger";
    if (/apply|save|confirm|적용|저장|dev key 저장/.test(source)) return "write";
    if (/preview|점검|검증|확인/.test(source)) return "preview";
    if (/open|load|refresh|reset|copy|filter|조회|보기|불러오기|새로고침|초기화|복사/.test(source)) return "safe";
    return "safe";
  }

  function renderRiskChip(risk) {
    const label = RISK_LABELS[risk] || RISK_LABELS.safe;
    return `<span class="button-risk-chip ${risk}" data-admin-button-risk-chip aria-hidden="true">${label}</span>`;
  }

  function applyButtonRiskLabels(root) {
    const scope = root && root.querySelectorAll ? root : document;
    const buttons = Array.from(scope.querySelectorAll("button.btn, a.btn"));
    let changed = 0;
    buttons.forEach((button) => {
      if (button.hasAttribute("data-admin-skip-risk-label")) return;
      const risk = classifyButton(button);
      button.setAttribute("data-admin-button-risk", risk);
      button.setAttribute("title", button.getAttribute("title") || `${RISK_LABELS[risk]} 버튼`);
      const existingChip = button.querySelector("[data-admin-button-risk-chip]");
      if (existingChip) existingChip.remove();
      changed += 1;
    });
    return changed;
  }

  function initializeAdminButtonSafety() {
    applyButtonRiskLabels(document);
    if (!bound) {
      bound = true;
      observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node && node.nodeType === 1) applyButtonRiskLabels(node);
          });
        });
      });
      observer.observe(document.body, { childList: true, subtree: true });
    }
    return getAdminButtonSafetyReadiness();
  }

  function getAdminButtonSafetyReadiness() {
    const labeledCount = document.querySelectorAll("[data-admin-button-risk]").length;
    const legendReady = !!document.querySelector(".admin-safety-legend");
    return {
      ok: bound && legendReady,
      version: VERSION,
      labeledCount,
      legendReady,
      routeChanges: 0,
      apiBodyChanges: 0,
      writeOperations: 0,
    };
  }

  window.RpgAdminButtonSafety = {
    VERSION,
    classifyButton,
    applyButtonRiskLabels,
    initializeAdminButtonSafety,
    getAdminButtonSafetyReadiness,
  };
  window.initializeAdminButtonSafety = initializeAdminButtonSafety;
  window.getAdminButtonSafetyReadiness = getAdminButtonSafetyReadiness;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAdminButtonSafety, { once: true });
  } else {
    initializeAdminButtonSafety();
  }
})();
