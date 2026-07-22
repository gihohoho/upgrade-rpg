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

assertIncludes("src/api/save-data-preview.js", "previewBackendSaveSnapshot");
assertIncludes("src/api/save-data-preview.js", "compareSaveSnapshots");
assertIncludes("src/api/save-data-preview.js", "sameRawSnapshot");
assertIncludes("src/api/save-data-preview.js", "different_review_before_restore");
assertIncludes("src/api/save-data-preview.js", "assertBackendSaveSnapshotPreview");
assertIncludes("index.html", "src/api/save-data-preview.js");
assertOrder("index.html", "src/api/save-data-sync-policy.js", "src/api/save-data-preview.js");
assertOrder("index.html", "src/api/save-data-preview.js", "src/api/save-data-dev-badge.js");
assertIncludes("docs/archive/stage-notes/SAVE_DATA_PREVIEW_COMPARE.md", "Save Data Preview");

console.log("save data preview compare smoke test passed");
