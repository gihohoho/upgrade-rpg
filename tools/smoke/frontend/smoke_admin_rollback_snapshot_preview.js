const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");
const sharedPath = path.join(root, "src/api/admin/admin-preview-diff.js");
const sharedSource = fs.readFileSync(sharedPath, "utf8");
const consumerFiles = [
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const pattern of [
  "function buildSnapshotDiff",
  "function isRollbackSnapshotConsistent",
  "function renderUnifiedPreviewDiff",
  "snapshot/diff",
  "Snapshot 기준값 확인",
  "fingerprint: <code>",
  "현재/적용 기준",
  "되돌릴 기준",
]) {
  assert(sharedSource.includes(pattern), `shared rollback preview renderer missing: ${pattern}`);
}

assert(sharedSource.includes('Number(snapshot.schemaVersion) !== 1'), "snapshot schema version must be checked");
assert(sharedSource.includes('snapshot.fingerprint.length !== 64'), "snapshot fingerprint length must be checked");
assert(sharedSource.includes('buildSnapshotDiff(snapshot.before, snapshot.after, "$")'), "snapshot must be compared with unified diff");

for (const relativePath of consumerFiles) {
  const source = fs.readFileSync(path.join(root, relativePath), "utf8");
  assert(source.includes("window.RpgAdminPreviewDiff"), `${relativePath} must delegate to shared preview renderer`);
  assert(!source.includes("Snapshot 기준값 확인"), `${relativePath} must not duplicate snapshot preview markup`);
}

const context = { window: {} };
vm.createContext(context);
vm.runInContext(sharedSource, context, { filename: sharedPath });
const renderer = context.window.RpgAdminPreviewDiff;
assert(renderer && renderer.getReadiness().ok, "shared preview renderer readiness must be ok");

const snapshot = {
  schemaVersion: 1,
  fingerprint: "a".repeat(64),
  domain: "itemTemplates",
  targetId: 1,
  before: { name: "after" },
  after: { name: "before" },
};
const diff = [{ path: "$.name", op: "replace", before: "after", after: "before" }];
assert(renderer.isRollbackSnapshotConsistent(snapshot, diff), "shared renderer must accept matching snapshot/diff");
const html = renderer.renderUnifiedPreviewDiff({ unifiedDiff: diff, rollbackSnapshot: snapshot });
assert(html.includes("snapshot/diff 일치"), "rendered preview must show snapshot/diff consistency");
assert(html.includes("Snapshot 기준값 확인"), "rendered preview must show snapshot values");

const adminHtml = fs.readFileSync(path.join(root, "admin.html"), "utf8");
const sharedIndex = adminHtml.indexOf('src/api/admin/admin-preview-diff.js');
for (const consumer of ["admin-change-logs.js", "admin-create-lifecycle.js", "admin-edit-draft.js"]) {
  assert(sharedIndex >= 0 && sharedIndex < adminHtml.indexOf(consumer), `shared renderer must load before ${consumer}`);
}

console.log("admin shared rollback snapshot preview smoke test passed");
