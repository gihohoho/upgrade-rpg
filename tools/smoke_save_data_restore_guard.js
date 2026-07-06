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

assertIncludes("src/api/save-data-restore-guard.js", "v108.backend-save-data-restore-reload-lock");
assertIncludes("src/api/save-data-restore-guard.js", "restoreBackendSaveSnapshotToLocal");
assertIncludes("src/api/save-data-restore-guard.js", "openBackendSaveRestorePreviewModal");
assertIncludes("src/api/save-data-restore-guard.js", "createLocalSaveBackupBeforeRestore");
assertIncludes("src/api/save-data-restore-guard.js", "restoreBackendSaveBackupToLocal");
assertIncludes("src/api/save-data-restore-guard.js", "restored_needs_reload");
assertIncludes("src/api/save-data-restore-guard.js", "DB 세이브로 복구");
assertIncludes("src/api/save-data-restore-guard.js", "최근 백업으로 되돌리기");
assertIncludes("src/api/save-data-restore-guard.js", "save-restore-modal-warning");
assertIncludes("src/api/save-data-restore-guard.js", "escapeHtml");
assertIncludes("src/api/save-data-restore-guard.js", "upgrade-rpg:backend-save-restore");
assertIncludes("src/api/save-data-restore-guard.js", "RESTORE_PENDING_KEY");
assertIncludes("src/api/save-data-restore-guard.js", "markBackendSaveRestorePendingReload");
assertIncludes("src/api/save-data-restore-guard.js", "shouldSkipSaveGameForBackendRestore");
assertIncludes("src/api/save-data-restore-guard.js", "completeBackendSaveRestoreReloadApply");
assertIncludes("src/app/main.js", "shouldSkipSaveGameForBackendRestore");
assertIncludes("src/app/main.js", "completeBackendSaveRestoreReloadApply");
assertIncludes("index.html", "src/api/save-data-restore-guard.js");
assertOrder("index.html", "src/api/save-data-preview.js", "src/api/save-data-restore-guard.js");
assertOrder("index.html", "src/api/save-data-restore-guard.js", "src/api/save-data-dev-badge.js");
assertIncludes("docs/SAVE_DATA_RESTORE_GUARD.md", "Save Data Restore Guard");

console.log("save data restore guard smoke test passed");
