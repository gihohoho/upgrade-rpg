const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
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

assertIncludes("src/api/save-data-dev-badge.js", "SAVE DATA");
assertIncludes("src/api/save-data-dev-badge.js", "hide SAVE");
assertIncludes("src/api/save-data-dev-badge.js", "show SAVE");
assertIncludes("src/api/save-data-dev-badge.js", "syncLatestLocalSaveToBackend");
assertIncludes("src/api/save-data-dev-badge.js", "sync DB");
assertIncludes("src/api/save-data-dev-badge.js", "load DB");
assertIncludes("src/api/save-data-dev-badge.js", "slots");
assertIncludes("src/api/save-data-dev-badge.js", "openBackendSaveSlotsModal");
assertIncludes("src/api/save-data-dev-badge.js", "preview");
assertIncludes("src/api/save-data-dev-badge.js", "backup");
assertIncludes("src/api/save-data-dev-badge.js", "openBackendSaveRestorePreviewModal");
assertIncludes("src/api/save-data-dev-badge.js", "restoreBackendSaveBackupToLocal");
assertIncludes("src/api/save-data-dev-badge.js", "upgrade-rpg:backend-save-restore");
assertIncludes("src/api/save-data-dev-badge.js", "loadBackendSaveSnapshot");
assertIncludes("src/api/save-data-dev-badge.js", "enableBackendSaveDualWrite");
assertIncludes("src/api/save-data-dev-badge.js", "disableBackendSaveDualWrite");
assertIncludes("src/api/save-data-dev-badge.js", "refreshBackendSaveDataDevBadge");
assertIncludes("src/api/save-data-dev-badge.js", "v378.backend-save-data-dev-badge-admin-visibility");
assertIncludes("src/api/save-data-dev-badge.js", "RpgGameDevUiAccess");
assertIncludes("src/api/save-data-dev-badge.js", "canUseGameDevUi");
assertIncludes("src/api/save-data-dev-badge.js", "removeControls");
assertIncludes("src/api/save-data-dev-badge.js", "bottom: calc(100% + 10px)");
assertIncludes("src/api/save-data-dev-badge.js", "right: 20px");
assertIncludes("src/api/save-data-dev-badge.js", "position: fixed");
assertIncludes("src/api/save-data-sync-policy.js", "upgrade-rpg:backend-save-sync-${name}");
assertIncludes("src/api/save-data-sync-policy.js", "dispatchBackendSaveSyncEvent(\"status\"");
assertIncludes("src/api/save-data-sync-policy.js", "dispatchBackendSaveSyncEvent(\"mode\"");
assertIncludes("index.html", "src/api/save-data-dev-badge.js");
assertOrder("index.html", "src/api/save-data-sync-policy.js", "src/api/save-data-dev-badge.js");
assertIncludes("docs/archive/history/SAVE_SYSTEM_HISTORY.md", "SAVE DATA");

console.log("save data dev badge smoke test passed");
