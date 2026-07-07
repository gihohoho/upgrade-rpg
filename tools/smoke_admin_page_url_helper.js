const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

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

assertContains("src/api/admin-readonly-overview.js", [
  "v113.admin-readonly-overview-url-helper",
  "function getAdminReadOnlyPageUrl()",
  "new URL(\"admin.html\", window.location.href).toString()",
  "function copyAdminReadOnlyPageUrl()",
  "window.getAdminReadOnlyPageUrl",
  "window.copyAdminReadOnlyPageUrl",
]);

assertContains("admin.html", [
  "현재 관리자 페이지 주소",
  "data-admin-current-url",
  "data-admin-game-url",
  "data-admin-action=\"copy-admin-url\"",
  "고정된 5500 주소가 아니라",
  "v119 admin edit draft validation",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v119.admin-edit-draft-validation",
  "function buildSiblingPageUrl(fileName)",
  "function getCurrentAdminPageUrl()",
  "function getGamePageUrl()",
  "function syncLocationHints()",
  "function copyCurrentAdminPageUrl()",
  "window.getCurrentAdminPageUrl",
  "window.copyCurrentAdminPageUrl",
]);

console.log("admin page URL helper smoke test passed");
