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

assertContains("src/api/admin-page-readonly.js", [
  "v156.admin-change-log-relation-tools",
  "getAdminChangeRelationInfo",
  "formatAdminRelationInfoText",
  "getAdminRelationOpenTargetFromChange",
  "renderAdminRollbackMismatchValueCell",
  "relationChangeCount",
  "changeLogRelationReady",
  "window.getAdminChangeRelationInfo",
]);

assertContains("backend/app/services/admin_service.py", [
  "_build_change_log_changes_with_relations",
  "_describe_change_log_relation_value",
  "_enrich_rollback_mismatches_with_relations",
  "relationChangeCount",
  "relationLabelsReturned",
]);

assertContains("admin.html", [
  "v156 admin change log relation tools",
  "relation-value-cell",
  "relation-jump-btn",
]);

assertContains("docs/ADMIN_CHANGE_LOG_RELATION_TOOLS.md", [
  "Admin Change Log Relation Tools",
  "rollback preview",
  "relation label",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v156 - Admin Change Log Relation Tools",
  "변경 이력 상세",
  "rollback preview",
]);

console.log("admin change log relation tools smoke test passed");
