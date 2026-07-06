const fs = require("fs");
const path = require("path");
const vm = require("vm");

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
    console.error(`${file} 순서가 올바르지 않습니다: ${first} -> ${second}`);
    process.exit(1);
  }
}

assertIncludes("src/api/save-data-restore-guard.js", "v108.backend-save-data-restore-reload-lock");
assertIncludes("src/api/save-data-restore-guard.js", "upgradeRpgBackendSaveRestorePendingReload");
assertIncludes("src/api/save-data-restore-guard.js", "markBackendSaveRestorePendingReload");
assertIncludes("src/api/save-data-restore-guard.js", "shouldSkipSaveGameForBackendRestore");
assertIncludes("src/api/save-data-restore-guard.js", "completeBackendSaveRestoreReloadApply");
assertIncludes("src/api/save-data-restore-guard.js", "applied_after_reload");
assertIncludes("src/app/main.js", "window.shouldSkipSaveGameForBackendRestore");
assertIncludes("src/app/main.js", "window.completeBackendSaveRestoreReloadApply");
assertIncludes("src/app/main.js", "세이브 복구가 새로고침 대기 중이라 수동 저장");
assertOrder("index.html", "src/api/save-data-restore-guard.js", "src/app/main.js");
assertIncludes("docs/SAVE_DATA_RESTORE_RELOAD_LOCK.md", "Save Data Restore Reload Lock");

async function assertDynamicRestoreLockBehavior() {
  const code = read("src/api/save-data-restore-guard.js");
  const store = new Map();
  const windowStub = {
    localStorage: {
      getItem: (key) => (store.has(key) ? store.get(key) : null),
      setItem: (key, value) => store.set(key, String(value)),
      removeItem: (key) => store.delete(key),
    },
    dispatchEvent: () => {},
    CustomEvent: function CustomEvent(name, options) {
      this.name = name;
      this.detail = options.detail;
    },
    console,
  };

  const localSnapshot = { saveVersion: 5, player: { level: 1, gold: 100, inventory: [] } };
  const backendSnapshot = { saveVersion: 5, player: { level: 9, gold: 999, inventory: [{ name: "테스트" }] } };
  store.set("idleRpgSaveV22", JSON.stringify(localSnapshot));

  windowStub.readLocalSaveSnapshot = (key) => ({
    key,
    exists: true,
    raw: store.get(key),
    snapshot: JSON.parse(store.get(key)),
    error: null,
  });
  windowStub.summarizeSaveSnapshotForPreview = (snapshot) => ({
    level: snapshot.player.level,
    gold: snapshot.player.gold,
    inventoryItems: snapshot.player.inventory.length,
  });
  windowStub.previewBackendSaveSnapshot = async () => ({
    backend: { exists: true },
    recommendation: "different_review_before_restore",
    comparison: { diffCount: 2, sameRawSnapshot: false },
    backendResponse: { payload: { snapshot: backendSnapshot } },
  });

  vm.runInNewContext(code, { window: windowStub, console });
  const result = await windowStub.restoreBackendSaveSnapshotToLocal({ skipConfirm: true, log: false });
  if (!result.ok) throw new Error("restoreBackendSaveSnapshotToLocal did not succeed");

  const restored = JSON.parse(store.get("idleRpgSaveV22"));
  if (restored.player.gold !== 999) throw new Error("backend snapshot was not written to idleRpgSaveV22");
  if (!windowStub.shouldSkipSaveGameForBackendRestore("idleRpgSaveV22")) {
    throw new Error("pending reload lock did not block saveGame");
  }

  const applied = windowStub.completeBackendSaveRestoreReloadApply({ loaded: true, saveKey: "idleRpgSaveV22" });
  if (!applied.applied) throw new Error("reload apply completion failed");
  if (windowStub.shouldSkipSaveGameForBackendRestore("idleRpgSaveV22")) {
    throw new Error("pending reload lock was not cleared after load");
  }
}

assertDynamicRestoreLockBehavior()
  .then(() => console.log("save data restore reload lock smoke test passed"))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
