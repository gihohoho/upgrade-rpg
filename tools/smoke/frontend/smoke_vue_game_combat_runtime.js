const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");

function read(relativePath) {
  return fs.readFileSync(path.join(VUE_ROOT, relativePath), "utf8");
}

function requireMarker(source, marker, label) {
  assert.ok(source.includes(marker), `${label} missing: ${marker}`);
}

function loadRuntime() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: [
        "import * as runtime from './src/game/runtime/combatRuntime.ts';",
        "import * as domain from './src/game/domain/index.ts';",
        "globalThis.__combat = { runtime, domain };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "combat-runtime-smoke-harness.ts",
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
  return context.__combat;
}

function assertStaticBoundary() {
  const runtime = read("src/game/runtime/combatRuntime.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
  ]) assert.ok(!forbidden.test(runtime), `combat runtime contains forbidden dependency: ${forbidden}`);
  for (const marker of [
    "createCombatRuntimeController",
    "scheduler.schedule(tick, state.intervalMs)",
    "const currentHp = Math.max",
    "serverStateConnected: false",
    "rewardsConnected: false",
    "randomConnected: false",
    "function pause(",
    "function resume(",
    "function restart(",
    "function destroy(",
  ]) requireMarker(runtime, marker, "typed combat runtime");

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now"]) {
    assert.ok(!store.includes(forbidden), `game store must delegate scheduling and persistence: ${forbidden}`);
  }
  for (const marker of [
    "createCombatRuntimeController",
    "getBasicAttackIntervalMs",
    "engageFieldRuntime",
    "engageBossRuntime",
    "combatController.pause('utility')",
    "combatRuntime,",
  ]) requireMarker(store, marker, "game runtime integration");

  const playShell = read("src/components/game/GamePlayShell.vue");
  assert.ok(!playShell.includes('v-if="game.model"'), "game frame must mount GameTownShell before the model initializer runs");
  for (const marker of [
    "handleVisibilityChange",
    "game.pauseCombatRuntime('visibility')",
    "game.resumeCombatRuntime('visibility')",
    "game.resetShell()",
  ]) requireMarker(playShell, marker, "combat timer lifecycle");

  for (const relativePath of [
    "src/components/game/GameFieldCombatShell.vue",
    "src/components/game/GameBossCombatShell.vue",
  ]) {
    const component = read(relativePath);
    for (const marker of [
      'aria-label="클라이언트 전투 실행 상태"',
      "runtime.value.currentHp",
      "game.pauseCombatRuntime('manual')",
      "game.resumeCombatRuntime('manual')",
      "game.restartCombatRuntime()",
      "snapshot 저장",
    ]) requireMarker(component, marker, relativePath);
  }

  const styles = read("src/styles/base.css");
  for (const marker of [
    "/* v393: client-only combat runtime controls shared by field and boss screens. */",
    ".combat-runtime-panel",
    '.combat-runtime-panel[data-tone="boss"]',
    '.combat-runtime-panel__status[data-state="paused"]',
    "@media (max-width: 760px)",
  ]) requireMarker(styles, marker, "combat runtime responsive CSS");
}

function assertRuntimeBehavior() {
  const { runtime, domain } = loadRuntime();
  let clock = 1_000;
  let nextHandle = 1;
  const callbacks = new Map();
  const snapshots = [];
  const scheduler = {
    now: () => clock,
    schedule(callback, delayMs) {
      const handle = nextHandle++;
      callbacks.set(handle, { callback, delayMs });
      return handle;
    },
    cancel(handle) {
      callbacks.delete(handle);
    },
  };
  const fire = () => {
    const active = [...callbacks.values()];
    assert.strictEqual(active.length, 1, "exactly one combat timer must be active");
    clock += active[0].delayMs;
    active[0].callback();
  };
  const controller = runtime.createCombatRuntimeController((snapshot) => snapshots.push(snapshot), scheduler);

  assert.strictEqual(controller.engage({
    type: "field",
    key: "field_1",
    name: "첫 몬스터",
    maxHp: 100,
    attackDamage: 30,
    intervalMs: 200,
  }), true);
  assert.strictEqual(callbacks.size, 1);
  assert.strictEqual(controller.getSnapshot().status, "running");
  assert.strictEqual(controller.getSnapshot().currentHp, 100);

  fire();
  assert.strictEqual(controller.getSnapshot().currentHp, 70);
  assert.strictEqual(controller.getSnapshot().attackCount, 1);
  assert.strictEqual(controller.pause("manual"), true);
  assert.strictEqual(callbacks.size, 0);
  assert.strictEqual(controller.getSnapshot().pauseReason, "manual");
  assert.strictEqual(controller.resume("visibility"), false, "a different lifecycle owner must not resume a manual pause");
  assert.strictEqual(controller.resume("manual"), true);
  assert.strictEqual(callbacks.size, 1);

  fire();
  fire();
  fire();
  const defeated = controller.getSnapshot();
  assert.strictEqual(defeated.currentHp, 0);
  assert.strictEqual(defeated.status, "defeated");
  assert.strictEqual(defeated.attackCount, 4);
  assert.strictEqual(defeated.lastDamage, 10);
  assert.strictEqual(callbacks.size, 0, "defeated targets must clear their timer");
  assert.strictEqual(defeated.serverStateConnected, false);
  assert.strictEqual(defeated.rewardsConnected, false);
  assert.strictEqual(defeated.randomConnected, false);
  for (const forbiddenKey of ["gold", "reward", "rewards", "drop", "drops", "save"]) {
    assert.ok(!(forbiddenKey in defeated), `runtime snapshot must not expose mutation field: ${forbiddenKey}`);
  }

  assert.strictEqual(controller.restart(), true);
  assert.strictEqual(controller.getSnapshot().currentHp, 100);
  assert.strictEqual(controller.getSnapshot().attackCount, 0);
  assert.strictEqual(callbacks.size, 1);
  assert.strictEqual(controller.engage({
    type: "boss",
    key: "boss_1",
    name: "첫 보스",
    maxHp: 500,
    attackDamage: 80,
    intervalMs: 90,
  }), true);
  assert.strictEqual(callbacks.size, 1, "switching targets must replace the previous timer");
  assert.strictEqual(controller.getSnapshot().targetType, "boss");
  assert.strictEqual(controller.getSnapshot().intervalMs, 100, "runtime interval has a 100ms safety floor");
  controller.stop();
  assert.strictEqual(callbacks.size, 0);
  assert.strictEqual(controller.getSnapshot().status, "idle");
  controller.destroy();
  assert.strictEqual(controller.engage({ type: "field", key: "x", name: "x", maxHp: 1, attackDamage: 1, intervalMs: 100 }), false);
  assert.ok(snapshots.length >= 10, "runtime state changes must publish immutable snapshots");

  assert.strictEqual(domain.getBasicAttackIntervalMs(150), 224);
  assert.strictEqual(domain.getBasicAttackIntervalMs(400), 112);
  assert.strictEqual(domain.getBasicAttackIntervalMs(999), 112, "attack speed must retain the legacy 400 cap");
}

function main() {
  assertStaticBoundary();
  assertRuntimeBehavior();
  console.log("PASS: Vue combat runtime owns one deterministic client timer with pause/resume/restart/cleanup and no server, save, reward, Gold, drop, or random mutation");
}

main();
