const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

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

assertContains("admin.html", [
  "section-admin-js-split-readiness",
  "data-admin-js-split-readiness",
  "관리자 JS 분리 준비",
  "v184 split readiness",
  "JS 분리 준비",
  "v185 admin layout shell split",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v185.admin-layout-shell-split",
  "v183.admin-create-lifecycle-batch-check",
  "ADMIN_JS_SPLIT_PHASES",
  "ADMIN_JS_SPLIT_REQUIRED_GLOBALS",
  "RpgAdminLayoutShell",
  "layoutShellExternalReady",
  "getAdminJsSplitReadiness",
  "renderAdminJsSplitReadiness",
  "adminJsSplitReadinessReady",
  "data-admin-js-split-readiness",
  "layout shell 분리 안정 확인",
  "window.getAdminJsSplitReadiness",
  "window.renderAdminJsSplitReadiness",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_js_split_readiness.js",
]);

assertContains("docs/ADMIN_JS_SPLIT_READINESS.md", [
  "Admin JS Split Readiness",
  "v184",
  "layout shell",
  "src/api/admin-layout-shell.js",
  "layout shell",
  "DB reset / seed",
]);

console.log("admin js split readiness smoke test passed");
