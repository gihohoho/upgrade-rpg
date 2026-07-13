const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
const source = fs.readFileSync(path.join(root, "src/api/admin/admin-change-logs.js"), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const pattern of [
  "function buildSnapshotDiff",
  "function isRollbackSnapshotConsistent",
  "snapshot/diff",
  "Snapshot 기준값 확인",
  "fingerprint: <code>",
  "현재/적용 기준",
  "되돌릴 기준",
  "buildSnapshotDiff,",
  "isRollbackSnapshotConsistent,",
  "renderUnifiedPreviewDiff,",
]) {
  assert(source.includes(pattern), `admin rollback snapshot preview missing: ${pattern}`);
}

assert(source.includes('snapshot.schemaVersion !== 1'), "snapshot schema version must be checked");
assert(source.includes('snapshot.fingerprint.length !== 64'), "snapshot fingerprint length must be checked");
assert(source.includes('JSON.stringify(snapshotDiff) === JSON.stringify'), "snapshot must be compared with unified diff");

console.log("admin rollback snapshot preview smoke test passed");
