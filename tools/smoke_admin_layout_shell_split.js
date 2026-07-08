const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    assert(text.includes(pattern), `${file}: missing pattern ${pattern}`);
  }
}

const adminHtml = read("admin.html");
const gameApiIndex = adminHtml.indexOf('src/api/game-api-client.js');
const layoutIndex = adminHtml.indexOf('src/api/admin-layout-shell.js');
const adminPageIndex = adminHtml.indexOf('src/api/admin-page-readonly.js');
assert(gameApiIndex >= 0, "admin.html: missing game-api-client.js script");
assert(layoutIndex >= 0, "admin.html: missing admin-layout-shell.js script");
assert(adminPageIndex >= 0, "admin.html: missing admin-page-readonly.js script");
assert(gameApiIndex < layoutIndex && layoutIndex < adminPageIndex, "admin.html: script order must be game-api -> layout-shell -> admin-page");

assertContains("src/api/admin-layout-shell.js", [
  "v185.admin-layout-shell-split",
  "window.RpgAdminLayoutShell",
  "ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY",
  "ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS",
  "initializeAdminLayoutShell",
  "getAdminLayoutShellReadiness",
  "setAdminSectionCollapsed",
  "setAdminActiveSidebarLink",
  "updateAdminStickyLayoutOffsets",
  "getAdminDefaultCollapsedSectionKeys",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v185.admin-layout-shell-split",
  "v184.admin-js-split-readiness",
  "getAdminLayoutShellApi",
  "RpgAdminLayoutShell is not loaded",
  "layoutShellExternalReady",
  "layoutShellReady",
  "window.getAdminDefaultCollapsedSectionKeys = getAdminDefaultCollapsedSectionKeys",
]);

assertContains("docs/ADMIN_LAYOUT_SHELL_SPLIT.md", [
  "Admin Layout Shell Split",
  "v185",
  "src/api/admin-layout-shell.js",
  "DB reset / seed",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_layout_shell_split.js",
]);

console.log("admin layout shell split smoke test passed");
