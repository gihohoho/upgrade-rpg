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

assertIncludes("src/api/save-data-sync-policy.js", "upgradeRpgBackendSaveSyncModeInitializedV102");
assertIncludes("src/api/save-data-sync-policy.js", "normalizeStoredBackendSaveSyncMode");
assertIncludes("src/api/save-data-sync-policy.js", "ready_manual_dual");
assertIncludes("src/api/save-data-sync-policy.js", "local_only_mode");
assertIncludes("src/api/save-data-sync-policy.js", "recordBackendSaveManualSaveCooldown");
assertIncludes("src/app/main.js", "recordBackendSaveManualSaveCooldown");
assertIncludes("src/api/save-data-dev-badge.js", "sync DB");
assertIncludes("src/api/save-data-dev-badge.js", "load DB");
assertIncludes("src/api/save-data-dev-badge.js", "skipped_manual_save_cooldown");
assertIncludes("docs/archive/stage-notes/SAVE_DATA_DEV_BADGE.md", "v102");
assertIncludes("docs/archive/stage-notes/SAVE_DATA_DUAL_WRITE.md", "skipped_local_only_mode");

console.log("save data default dual mode smoke test passed");
