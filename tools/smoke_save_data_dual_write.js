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

assertIncludes("src/api/save-data-sync-policy.js", "requestBackendSaveAfterManualSave");
assertIncludes("src/api/save-data-sync-policy.js", "ready_manual_dual");
assertIncludes("src/api/save-data-sync-policy.js", "skipped_manual_save_cooldown");
assertIncludes("src/api/save-data-sync-policy.js", "manual_dual");
assertIncludes("src/api/save-data-sync-policy.js", "failed_fallback_to_local_storage");
assertIncludes("src/app/main.js", "requestBackendSaveAfterManualSave");
assertIncludes("index.html", "src/api/save-data-sync-policy.js");
assertOrder("index.html", "src/api/save-data-bridge.js", "src/api/save-data-sync-policy.js");
assertOrder("index.html", "src/api/save-data-sync-policy.js", "src/app/main.js");
assertIncludes("docs/SAVE_DATA_DUAL_WRITE.md", "manual_dual");
assertIncludes("docs/SAVE_DATA_DUAL_WRITE.md", "disableBackendSaveDualWrite");

console.log("save data dual-write smoke test passed");
