const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("admin.html", [
  "v174 admin collapsed panel style fix",
  "data-admin-layout-shell",
  "data-admin-sidebar",
  "data-admin-main-content",
  "data-admin-collapsible",
  "data-admin-footer",
  "admin-section-collapsed",
  "filter-panel.admin-section-collapsed",
  "field-help-panel.admin-section-collapsed",
  "--admin-sticky-top",
  "--admin-scroll-margin-top",
  "data-admin-sticky-header",
  "빠른 이동",
  "접기/펼치기",
  "legacy smoke marker: v165 admin create apply limited · v171 admin create delete restore",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v174.admin-collapsed-panel-style-fix",
  "v173.admin-layout-collapse-polish",
  "v172.admin-layout-navigation-shell",
  "v171.admin-create-delete-restore",
  "updateAdminStickyLayoutOffsets",
  "initializeAdminLayoutShell",
  "getAdminLayoutShellReadiness",
  "setAdminSectionCollapsed",
  "setAdminActiveSidebarLink",
  "getAdminDefaultCollapsedSectionKeys",
  "layoutShellReady",
]);


assertContains("src/api/admin-layout-shell.js", [
  "v185.admin-layout-shell-split",
  "ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY",
  "ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS",
  "upgradeRpgAdminCollapsedSectionsV2",
  "field-help",
  "create-blueprint",
  "change-logs",
  "updateAdminStickyLayoutOffsets",
  "initializeAdminLayoutShell",
  "getAdminLayoutShellReadiness",
  "setAdminSectionCollapsed",
  "setAdminActiveSidebarLink",
  "window.RpgAdminLayoutShell",
  "collapsedPanelStyleReady",
]);

assertContains("docs/archive/stage-notes/ADMIN_LAYOUT_NAVIGATION_SHELL.md", [
  "Admin Layout Navigation Shell",
  "sidebar",
  "sticky",
  "header",
  "기본 접기",
  "접기/펼치기",
  "DB reset / seed",
]);

console.log("admin layout navigation shell smoke test passed");
