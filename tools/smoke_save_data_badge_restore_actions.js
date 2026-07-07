const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}
function assertIncludes(file, text) {
  const content = read(file);
  if (!content.includes(text)) {
    console.error(`${file}에 필요한 문자열이 없습니다: ${text}`);
    process.exit(1);
  }
}
function assertOrder(file, first, second) {
  const content = read(file);
  const a = content.indexOf(first);
  const b = content.indexOf(second);
  if (a < 0 || b < 0 || a > b) {
    console.error(`${file} 로딩 순서가 올바르지 않습니다: ${first} -> ${second}`);
    process.exit(1);
  }
}

assertIncludes("src/api/save-data-dev-badge.js", "v110.backend-save-data-dev-badge-integrity");
assertIncludes("src/api/save-data-dev-badge.js", 'data-sd-action="preview"');
assertIncludes("src/api/save-data-dev-badge.js", 'data-sd-action="backup"');
assertIncludes("src/api/save-data-dev-badge.js", 'data-sd-action="slots"');
assertIncludes("src/api/save-data-dev-badge.js", "openBackendSaveSlotsModal");
assertIncludes("src/api/save-data-dev-badge.js", "openBackendSaveRestorePreviewModal");
assertIncludes("src/api/save-data-dev-badge.js", "restoreBackendSaveBackupToLocal");
assertIncludes("src/api/save-data-dev-badge.js", "data-sd-restore");
assertIncludes("src/api/save-data-dev-badge.js", "upgrade-rpg:backend-save-restore");
assertIncludes("src/api/save-data-restore-guard.js", "v108.backend-save-data-restore-reload-lock");
assertIncludes("src/api/save-data-restore-guard.js", "최근 백업으로 되돌리기");
assertIncludes("src/api/save-data-restore-guard.js", "save-restore-modal-warning");
assertIncludes("src/api/save-data-restore-guard.js", "escapeHtml");
assertOrder("index.html", "src/api/save-data-restore-guard.js", "src/api/save-data-dev-badge.js");
assertIncludes("docs/SAVE_DATA_BADGE_RESTORE_ACTIONS.md", "Save Data Badge Restore Actions");

console.log("save data badge restore actions smoke test passed");
