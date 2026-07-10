const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

function assertContains(file, patterns) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  const text = fs.readFileSync(fullPath, "utf8");
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/api/save-data-integrity.js", [
  "v110.backend-save-data-integrity-verify",
  "verifyBackendSaveSnapshotIntegrity",
  "pushLocalSaveToBackendAndVerify",
  "checkBackendSaveIntegrityReady",
  "compareSaveSnapshots",
  "sameRawSnapshot",
]);

assertContains("src/api/save-data-sync-policy.js", [
  "pushLocalSaveToBackendAndVerify",
  "synced_verified",
  "saved_verify_failed",
  "verified",
  "diffCount",
]);

assertContains("src/api/save-data-dev-badge.js", [
  "synced_verified",
  "v111.backend-save-data-dev-badge-admin-overview",
]);

assertContains("index.html", [
  'src/api/save-data-preview.js',
  'src/api/save-data-integrity.js',
  'src/api/save-data-restore-guard.js',
]);

console.log("save data integrity verify smoke test passed");
