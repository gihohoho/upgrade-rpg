const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/townHud.ts",
  "src/stores/game.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameTownShell.vue",
];

function read(relativePath) {
  return fs.readFileSync(path.join(VUE_ROOT, relativePath), "utf8");
}

function requireMarker(source, marker, label) {
  assert.ok(source.includes(marker), `${label} missing: ${marker}`);
}

function loadTownAdapter() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: "import * as adapter from './src/game/adapters/townHud.ts'; globalThis.__townAdapter = adapter;",
      resolveDir: VUE_ROOT,
      sourcefile: "town-hud-smoke-harness.ts",
      loader: "ts",
    },
    bundle: true,
    platform: "node",
    format: "iife",
    target: "node20",
    write: false,
  });
  const context = {};
  vm.createContext(context);
  vm.runInContext(output.outputFiles[0].text, context);
  return context.__townAdapter;
}

function assertStaticBoundary() {
  for (const relative of REQUIRED_FILES) {
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue town HUD file: ${relative}`);
  }

  const adapter = read("src/game/adapters/townHud.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) {
    assert.ok(!forbidden.test(adapter), `town HUD adapter contains forbidden dependency: ${forbidden}`);
  }

  const store = read("src/stores/game.ts");
  for (const forbidden of ["accountApi", "authApi", "fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now"] ) {
    assert.ok(!store.includes(forbidden), `game store must remain UI-only before runtime/save stage: ${forbidden}`);
  }
  for (const marker of ["createTownHudViewModel", "shallowRef<TownHudViewModel", "slot.accountCharacterId", "activeFeatureKey"] ) {
    requireMarker(store, marker, "typed game store");
  }

  const component = read("src/components/game/GameTownShell.vue");
  for (const marker of [
    'data-zone="town"',
    'v-if="game.isTown"',
    "접속 캐릭터",
    "마을 시설",
    'aria-label="캐릭터 HUD"',
    'aria-current="location"',
    'aria-haspopup="dialog"',
    'role="dialog"',
    'aria-modal="true"',
    "event.key === 'Escape'",
    "snapshot load/save와 전투 timer는 아직 시작하지 않습니다",
    "account.changeCharacter()",
    "account.logout()",
  ]) {
    requireMarker(component, marker, "town HUD component");
  }
  assert.ok(!component.includes("confirm(") && !component.includes("alert("), "town HUD must not use browser alert/confirm");

  const gate = read("src/components/account/AccountGate.vue");
  requireMarker(gate, "<GamePlayShell v-else />", "account ready gate");
  requireMarker(gate, "import GamePlayShell", "account ready gate");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".town-session-bar",
    ".town-scene",
    ".town-hub__grid",
    ".town-hud",
    ".town-hud__skill-grid",
    ".town-feature-modal-backdrop",
    "@media (max-width: 560px)",
    "@media (prefers-reduced-motion: reduce)",
  ]) {
    requireMarker(styles, selector, "town HUD responsive CSS");
  }

  const app = read("src/App.vue");
  requireMarker(app, 'aria-label="메뉴 닫기"', "mobile sidebar close control");
  requireMarker(app, 'aria-label="메뉴 밖 영역 닫기"', "mobile sidebar scrim control");
  requireMarker(styles, ".app-sidebar__close", "mobile sidebar close control CSS");
}

function assertAdapterBehavior() {
  const adapter = loadTownAdapter();
  const source = {
    accountCharacterId: "a".repeat(32),
    slotKey: "character-2",
    characterName: "기호검신",
    characterCode: "weapon_master",
    characterLabel: "검신",
    progress: {
      gold: "12500",
      level: 7,
      currentZoneIndex: 2,
      currentZoneType: "field",
      updatedAt: "2026-08-31T00:00:00Z",
    },
  };
  const before = JSON.stringify(source);
  const model = adapter.createTownHudViewModel(source);

  assert.strictEqual(model.zoneType, "town");
  assert.strictEqual(model.serverState.progress.currentZoneType, "town");
  assert.strictEqual(model.serverState.player.gold, 12500);
  assert.strictEqual(model.goldLabel, "1.25B");
  assert.strictEqual(model.levelLabel, "Lv.7");
  assert.strictEqual(model.recentSaveZoneLabel, "최근 저장 · 필드 3");
  assert.strictEqual(model.recentSaveZoneIndex, 2);
  assert.strictEqual(model.recentSaveZoneType, "field");
  assert.strictEqual(model.stats.find((item) => item.key === "attack").value, "1250A");
  assert.strictEqual(model.skills.find((item) => item.slotKey === "Q").level, 1);
  assert.strictEqual(model.skills.find((item) => item.slotKey === "W").level, 0);
  assert.strictEqual(model.snapshotConnected, false);
  assert.ok(adapter.TOWN_FEATURES.save.nextStep.includes("snapshot load"));
  assert.strictEqual(JSON.stringify(source), before, "town adapter mutated account summary input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue town/HUD uses the typed domain without starting save or combat runtime");
}

main();
