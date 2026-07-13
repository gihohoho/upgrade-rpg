const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");
const sharedPath = path.join(root, "src/api/admin/admin-preview-diff.js");
const sharedSource = fs.readFileSync(sharedPath, "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const pattern of [
  "function renderResultBanner",
  "function renderPreviewResultSummary",
  "preview-result-warning",
  "preview-result-note",
  "resultSummaryReady",
]) {
  assert(sharedSource.includes(pattern), `shared preview result summary missing: ${pattern}`);
}

const context = { window: {} };
vm.createContext(context);
vm.runInContext(sharedSource, context, { filename: sharedPath });
const renderer = context.window.RpgAdminPreviewDiff;
const readiness = renderer.getReadiness();
assert(readiness.resultBannerReady, "shared result banner readiness must be true");
assert(readiness.resultSummaryReady, "shared result summary readiness must be true");

const html = renderer.renderPreviewResultSummary({ note: "안내" }, {
  banner: { tone: "blocked", title: "Preview 차단", subtitle: "사유 확인", metrics: [{ label: "오류", value: 2, tone: "blocked" }] },
  badges: [
    { label: "ready", value: false, tone: "blocked" },
    { label: "hidden", value: 1, hidden: true },
  ],
  warnings: ["stale", "mismatch"],
});
assert(html.includes("Preview 차단"), "summary must render status banner");
assert(html.includes("ready: false"), "summary must render badges");
assert(!html.includes("hidden: 1"), "summary must hide optional badges");
assert(html.includes("stale, mismatch"), "summary must render warnings");
assert(html.includes("안내"), "summary must render note");

for (const relativePath of [
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-change-logs.js",
]) {
  const source = fs.readFileSync(path.join(root, relativePath), "utf8");
  assert(source.includes("function renderPreviewResultSummary"), `${relativePath} must delegate result summaries`);
  assert(source.includes("renderPreviewResultSummary("), `${relativePath} must use shared result summary`);
}

const changeLogSource = fs.readFileSync(path.join(root, "src/api/admin/admin-change-logs.js"), "utf8");
assert((changeLogSource.match(/renderPreviewResultSummary\(result,/g) || []).length >= 3, "rollback/delete/restore must use shared result summary");

console.log("admin shared preview result summary smoke test passed");
