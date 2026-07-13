(function () {
  "use strict";

  const VERSION = "v266.admin-detail-shortcuts";
  let bound = false;

  function escapeCssIdent(value) {
    const text = String(value || "");
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(text);
    return text.replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  function getTargetByKey(key) {
    if (!key) return null;
    return document.querySelector(`[data-admin-detail-target="${escapeCssIdent(key)}"]`) || document.getElementById(key);
  }

  function expandSectionForElement(element) {
    const section = element && element.closest ? element.closest("[data-admin-collapsible]") : null;
    if (!section) return false;
    if (typeof window.setAdminSectionCollapsed === "function") {
      window.setAdminSectionCollapsed(section, false);
    } else {
      section.classList.remove("admin-section-collapsed");
    }
    return true;
  }

  function scrollToElement(element) {
    if (!element) return false;
    expandSectionForElement(element);
    try {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (_) {
      if (element.id) window.location.hash = `#${element.id}`;
    }
    element.classList.add("admin-detail-scroll-highlight");
    window.setTimeout(() => element.classList.remove("admin-detail-scroll-highlight"), 1400);
    return true;
  }

  function handleClick(event) {
    const scrollTrigger = event.target && event.target.closest ? event.target.closest("[data-admin-detail-scroll-target]") : null;
    if (scrollTrigger) {
      const target = getTargetByKey(scrollTrigger.getAttribute("data-admin-detail-scroll-target"));
      if (target) {
        event.preventDefault();
        scrollToElement(target);
      }
      return;
    }

    const jumpTrigger = event.target && event.target.closest ? event.target.closest("[data-admin-detail-jump-target]") : null;
    if (jumpTrigger) {
      const target = getTargetByKey(jumpTrigger.getAttribute("data-admin-detail-jump-target"));
      if (target) {
        window.setTimeout(() => scrollToElement(target), 80);
      }
    }
  }

  function initializeAdminDetailShortcuts() {
    if (!bound) {
      bound = true;
      document.addEventListener("click", handleClick);
    }
    return getAdminDetailShortcutsReadiness();
  }

  function getAdminDetailShortcutsReadiness() {
    return {
      ok: bound,
      version: VERSION,
      bound,
      routeChanges: 0,
      apiBodyChanges: 0,
      writeOperations: 0,
    };
  }

  window.RpgAdminDetailShortcuts = {
    VERSION,
    initializeAdminDetailShortcuts,
    getAdminDetailShortcutsReadiness,
    scrollToElement,
  };
  window.initializeAdminDetailShortcuts = initializeAdminDetailShortcuts;
  window.getAdminDetailShortcutsReadiness = getAdminDetailShortcutsReadiness;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAdminDetailShortcuts, { once: true });
  } else {
    initializeAdminDetailShortcuts();
  }
})();
