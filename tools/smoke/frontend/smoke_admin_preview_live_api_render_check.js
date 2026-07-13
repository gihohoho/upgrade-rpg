const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");
const sourcePath = path.join(root, "src/api/admin/admin-preview-live-verification.js");
const source = fs.readFileSync(sourcePath, "utf8");
const html = fs.readFileSync(path.join(root, "admin.html"), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const marker of [
  "v256.admin-preview-live-api-render-check",
  "ALLOWED_PREVIEW_METHODS",
  "previewAdminMasterDataCreate",
  "previewAdminMasterDataEdit",
  "previewAdminChangeLogRollback",
  "previewAdminCreateDeleteRollback",
  "previewAdminCreateDeleteRestore",
  "dryRunOnly: true",
  "writeOperations: 0",
  "applyMethodsBlocked: true",
  "data-admin-live-preview-actions",
  "data-admin-live-preview-result",
]) assert(source.includes(marker) || html.includes(marker), `live preview marker missing: ${marker}`);

assert(!/RpgGameApi\.applyAdmin/.test(source), "live preview module must not call apply admin APIs");
assert(!/getAdminWriteHeaders\s*\(/.test(source), "live preview module must not request write headers");
assert(!/confirmText\s*:/.test(source), "live preview module must not send confirmText");
assert(html.includes('data-admin-live-preview-actions'), "live preview action target missing");
assert(html.includes('data-admin-live-preview-result'), "live preview result target missing");
assert(html.includes('admin-preview-live-verification.js'), "live preview script missing");
assert(html.indexOf('admin-preview-diff.js') < html.indexOf('admin-preview-live-verification.js'), "shared renderer must load before live preview script");
assert(html.indexOf('admin-change-logs.js') < html.indexOf('admin-preview-live-verification.js'), "change log module must load before live preview script");
assert(html.indexOf('admin-create-lifecycle.js') < html.indexOf('admin-preview-live-verification.js'), "create module must load before live preview script");
assert(html.indexOf('admin-edit-draft.js') < html.indexOf('admin-preview-live-verification.js'), "edit module must load before live preview script");

let resultTarget = { innerHTML: "" };
let actionsTarget = { innerHTML: "" };
const fakeDocument = {
  readyState: "loading",
  addEventListener: () => {},
  querySelector: (selector) => {
    if (selector === "[data-admin-live-preview-result]") return resultTarget;
    if (selector === "[data-admin-live-preview-actions]") return actionsTarget;
    return null;
  },
  querySelectorAll: () => [],
};

const calls = [];
const context = {
  window: {
    RpgGameApi: {
      previewAdminMasterDataCreate: async (args) => {
        calls.push(["previewAdminMasterDataCreate", args]);
        return { ok: true, payload: { createApplyReady: true, dryRun: true, writeBlocked: true, previewSchemaVersion: 1, unifiedDiff: [{ path: "$.name", op: "add", before: null, after: args.draft.name }] } };
      },
      previewAdminMasterDataEdit: async (args) => {
        calls.push(["previewAdminMasterDataEdit", args]);
        return { ok: true, payload: { editApplyReady: true, dryRun: true, writeBlocked: true, previewSchemaVersion: 1, unifiedDiff: [{ path: "$.attack", op: "replace", before: args.baseValues.attack, after: args.draft.attack }] } };
      },
      previewAdminChangeLogRollback: async (args) => {
        calls.push(["previewAdminChangeLogRollback", args]);
        return { ok: true, payload: { rollbackReady: true, dryRun: true, writeBlocked: true, previewSchemaVersion: 1, unifiedDiff: [{ path: "$.hp", op: "replace", before: 1200, after: 1000 }] } };
      },
      previewAdminCreateDeleteRollback: async (args) => {
        calls.push(["previewAdminCreateDeleteRollback", args]);
        return { ok: true, payload: { createDeleteReady: true, dryRun: true, writeBlocked: true, previewSchemaVersion: 1, unifiedDiff: [] } };
      },
      previewAdminCreateDeleteRestore: async (args) => {
        calls.push(["previewAdminCreateDeleteRestore", args]);
        return { ok: true, payload: { createDeleteRestoreReady: true, dryRun: true, writeBlocked: true, previewSchemaVersion: 1, unifiedDiff: [] } };
      },
    },
    RpgAdminPreviewDiff: {
      renderPreviewResultSummary: (payload, options) => `<summary>${options.banner.title}:${payload.previewSchemaVersion}:${options.note}</summary>`,
      renderUnifiedPreviewDiff: (payload) => `<diff>${Array.isArray(payload.unifiedDiff) ? payload.unifiedDiff.length : 0}</diff>`,
    },
    RpgAdminCreateLifecycle: {
      readAdminCreateDraftValues: () => ({ ok: true, domain: "itemTemplates", draft: { name: "Live API 테스트" }, reason: "smoke", fieldCount: 1 }),
    },
    RpgAdminEditDraft: {
      readAdminEditDraftValues: () => ({ ok: true, domain: "itemTemplates", id: 1, draft: { attack: 12 }, originals: { attack: 10 }, fieldCount: 1 }),
      readAdminEditApplyControls: () => ({ reason: "smoke" }),
    },
    RpgAdminChangeLogs: {
      readAdminRollbackControls: () => ({ changeLogId: 7, reason: "smoke" }),
      readAdminCreateDeleteControls: () => ({ changeLogId: 8, reason: "smoke" }),
      readAdminCreateDeleteRestoreControls: () => ({ changeLogId: 9, reason: "smoke" }),
    },
  },
  document: fakeDocument,
  console,
  setTimeout,
  clearTimeout,
};

vm.createContext(context);
vm.runInContext(source, context, { filename: sourcePath });
const moduleApi = context.window.RpgAdminPreviewLiveVerification;
assert(moduleApi, "live preview global missing");
assert(moduleApi.LIVE_PREVIEW_KINDS.length === 5, "live preview must expose five API checks");
assert(moduleApi.ALLOWED_PREVIEW_METHODS.length === 5, "allowed preview API list must expose five methods");
assert(moduleApi.isAllowedPreviewMethod("previewAdminMasterDataCreate") === true, "create preview must be allowed");
assert(moduleApi.isAllowedPreviewMethod("applyAdminMasterDataCreate") === false, "apply API must not be allowed");
const readiness = moduleApi.getReadiness();
assert(readiness.ok === true, "live preview readiness must be true");
assert(readiness.dryRunOnly === true, "live preview must be dryRun only");
assert(readiness.writeOperations === 0, "live preview write count must be zero");
assert(readiness.applyMethodsBlocked === true, "live preview must block apply methods");
assert(readiness.apiMethodsReady === true, "mocked preview API methods must be ready");

(async () => {
  await moduleApi.runLivePreview("create");
  await moduleApi.runLivePreview("edit");
  await moduleApi.runLivePreview("rollback");
  await moduleApi.runLivePreview("create-delete");
  await moduleApi.runLivePreview("restore");
  assert(calls.length === 5, "each live preview kind must call exactly one preview API");
  assert(calls.every(([name]) => name.startsWith("previewAdmin")), "only preview APIs may be called");
  assert(calls.every(([, args]) => args.dryRun === true), "all live preview calls must be dryRun=true");
  assert(calls.every(([, args]) => !Object.prototype.hasOwnProperty.call(args, "confirmText")), "live preview calls must not send confirmText");
  assert(resultTarget.innerHTML.includes("실제 Preview 응답 body 확인"), "live preview must render raw response detail");
  assert(resultTarget.innerHTML.includes("apply API"), "live preview safety note must mention apply API is not used");
  console.log("admin preview live API render check smoke test passed");
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
