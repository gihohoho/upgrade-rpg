(function () {
  "use strict";

  const VERSION = "v185.admin-layout-shell-split";
  const ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY = "upgradeRpgAdminCollapsedSectionsV2";
  const ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS = ["field-help", "create-blueprint", "change-logs"];

  function getAdminDefaultCollapsedSectionSet() {
    return new Set(ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS.map(String));
  }

  function getAdminDefaultCollapsedSectionKeys() {
    return Array.from(getAdminDefaultCollapsedSectionSet());
  }

  function readAdminCollapsedSectionSet() {
    try {
      const raw = window.localStorage ? window.localStorage.getItem(ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY) : null;
      if (!raw) return getAdminDefaultCollapsedSectionSet();
      const values = JSON.parse(raw);
      return new Set(Array.isArray(values) ? values.map(String) : []);
    } catch (_) {
      return getAdminDefaultCollapsedSectionSet();
    }
  }

  function writeAdminCollapsedSectionSet(keys) {
    try {
      if (!window.localStorage) return false;
      window.localStorage.setItem(ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY, JSON.stringify(Array.from(keys || [])));
      return true;
    } catch (_) {
      return false;
    }
  }

  function getAdminCollapsibleSectionKey(section) {
    if (!section) return "";
    return section.getAttribute("data-admin-section-key") || section.id || "";
  }

  function setAdminSectionCollapsed(section, collapsed, options) {
    if (!section) return false;
    const key = getAdminCollapsibleSectionKey(section);
    const button = section.querySelector("[data-admin-layout-collapse-toggle]");
    section.classList.toggle("admin-section-collapsed", !!collapsed);
    section.setAttribute("data-admin-section-collapsed", collapsed ? "true" : "false");
    if (button) {
      button.textContent = collapsed ? "펼치기" : "접기";
      button.setAttribute("aria-expanded", collapsed ? "false" : "true");
      button.setAttribute("aria-label", `${key || "section"} ${collapsed ? "펼치기" : "접기"}`);
    }
    if (!options || !options.silent) {
      const collapsedSet = readAdminCollapsedSectionSet();
      if (collapsed) collapsedSet.add(key);
      else collapsedSet.delete(key);
      writeAdminCollapsedSectionSet(collapsedSet);
    }
    return true;
  }

  function ensureAdminSectionCollapseControl(section, collapsedSet) {
    if (!section || section.querySelector("[data-admin-layout-collapse-toggle]")) return false;
    const key = getAdminCollapsibleSectionKey(section);
    const header = section.querySelector(":scope > .section-header") || section.querySelector(":scope > .filter-title");
    if (!header) return false;
    header.classList.add("admin-collapse-header");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn mini admin-collapse-toggle";
    button.setAttribute("data-admin-layout-collapse-toggle", key);
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      setAdminSectionCollapsed(section, !section.classList.contains("admin-section-collapsed"));
    });
    header.appendChild(button);
    setAdminSectionCollapsed(section, collapsedSet && collapsedSet.has(key), { silent: true });
    return true;
  }

  function setAdminActiveSidebarLink(hash) {
    const links = Array.from(document.querySelectorAll(".admin-jump-nav a[href^='#']"));
    const nextHash = hash || window.location.hash || "#section-overview";
    links.forEach((link) => {
      const active = link.getAttribute("href") === nextHash;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    return nextHash;
  }

  function updateAdminStickyLayoutOffsets() {
    const header = document.querySelector("[data-admin-sticky-header]") || document.querySelector(".topbar");
    const height = header && header.getBoundingClientRect ? Math.ceil(header.getBoundingClientRect().height) : 112;
    const stickyTop = Math.max(96, height + 18);
    const scrollMargin = stickyTop + 18;
    document.documentElement.style.setProperty("--admin-sticky-top", `${stickyTop}px`);
    document.documentElement.style.setProperty("--admin-scroll-margin-top", `${scrollMargin}px`);
    return { height, stickyTop, scrollMargin };
  }

  function initializeAdminLayoutShell() {
    const stickyOffsets = updateAdminStickyLayoutOffsets();
    const collapsedSet = readAdminCollapsedSectionSet();
    const sections = Array.from(document.querySelectorAll("[data-admin-collapsible]"));
    sections.forEach((section) => ensureAdminSectionCollapseControl(section, collapsedSet));
    setAdminActiveSidebarLink(window.location.hash || "#section-overview");
    if (!window.__upgradeRpgAdminLayoutHashBound) {
      window.__upgradeRpgAdminLayoutHashBound = true;
      window.addEventListener("hashchange", () => setAdminActiveSidebarLink(window.location.hash || "#section-overview"));
      window.addEventListener("resize", () => updateAdminStickyLayoutOffsets());
      document.addEventListener("click", (event) => {
        const link = event.target && event.target.closest ? event.target.closest(".admin-jump-nav a[href^='#']") : null;
        if (!link) return;
        setTimeout(() => setAdminActiveSidebarLink(link.getAttribute("href")), 0);
      });
    }
    const readiness = getAdminLayoutShellReadiness();
    readiness.stickyOffsets = stickyOffsets;
    return readiness;
  }

  function getAdminLayoutShellReadiness() {
    const collapsibleCount = document.querySelectorAll("[data-admin-collapsible]").length;
    const collapseToggleCount = document.querySelectorAll("[data-admin-layout-collapse-toggle]").length;
    const defaultCollapsedKeys = getAdminDefaultCollapsedSectionKeys();
    const defaultCollapsedReady = defaultCollapsedKeys.every((key) => {
      const section = document.querySelector(`[data-admin-section-key="${key}"]`);
      return !!section && section.classList.contains("admin-section-collapsed");
    });
    const stickyTop = getComputedStyle(document.documentElement).getPropertyValue("--admin-sticky-top").trim();
    const collapsedPanelHeaderCount = document.querySelectorAll(".filter-panel[data-admin-collapsible] > .filter-title.admin-collapse-header, .field-help-panel[data-admin-collapsible] > .filter-title.admin-collapse-header").length;
    const collapsedPanelStyleReady = collapsedPanelHeaderCount >= document.querySelectorAll(".filter-panel[data-admin-collapsible], .field-help-panel[data-admin-collapsible]").length;
    const result = {
      layoutShellVersion: VERSION,
      layoutReady: !!document.querySelector("[data-admin-layout-shell]"),
      sidebarReady: !!document.querySelector("[data-admin-sidebar]"),
      mainContentReady: !!document.querySelector("[data-admin-main-content]"),
      footerReady: !!document.querySelector("[data-admin-footer]"),
      collapsibleCount,
      collapseToggleCount,
      collapseReady: collapsibleCount > 0 && collapseToggleCount >= collapsibleCount,
      collapsedPanelHeaderCount,
      collapsedPanelStyleReady,
      activeNavReady: !!document.querySelector(".admin-jump-nav a.active, .admin-jump-nav a[aria-current='location']"),
      defaultCollapsedKeys,
      defaultCollapsedReady,
      stickyTop,
      stickyOffsetReady: !!stickyTop && stickyTop !== "92px",
    };
    result.ok = result.layoutReady && result.sidebarReady && result.mainContentReady && result.footerReady && result.collapseReady && result.collapsedPanelStyleReady && result.stickyOffsetReady;
    return result;
  }

  window.RpgAdminLayoutShell = {
    VERSION,
    ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY,
    ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS: ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS.slice(),
    getAdminDefaultCollapsedSectionKeys,
    readAdminCollapsedSectionSet,
    writeAdminCollapsedSectionSet,
    getAdminCollapsibleSectionKey,
    setAdminSectionCollapsed,
    setAdminActiveSidebarLink,
    updateAdminStickyLayoutOffsets,
    initializeAdminLayoutShell,
    getAdminLayoutShellReadiness,
  };

  window.initializeAdminLayoutShell = initializeAdminLayoutShell;
  window.getAdminLayoutShellReadiness = getAdminLayoutShellReadiness;
  window.getAdminDefaultCollapsedSectionKeys = getAdminDefaultCollapsedSectionKeys;
  window.updateAdminStickyLayoutOffsets = updateAdminStickyLayoutOffsets;
  window.setAdminSectionCollapsed = setAdminSectionCollapsed;
  window.setAdminActiveSidebarLink = setAdminActiveSidebarLink;
})();
