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

function loadAdapters() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: [
        "import * as snapshot from './src/game/adapters/serverSnapshot.ts';",
        "import * as town from './src/game/adapters/townHud.ts';",
        "globalThis.__snapshotLoad = { snapshot, town };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "server-snapshot-load-smoke-harness.ts",
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
  return context.__snapshotLoad;
}

function assertStaticBoundary() {
  const api = read("src/api/gameApi.ts");
  for (const marker of [
    "loadSelectedCharacter",
    "slotKey: request.slotKey",
    "accountCharacterId: request.accountCharacterId",
    "requestApi<GameLoadPayload, GameLoadData>",
  ]) requireMarker(api, marker, "typed game load API");
  const loadApi = api.slice(api.indexOf("loadSelectedCharacter"), api.indexOf("saveSelectedCharacter"));
  for (const forbidden of ["method: 'POST'", "/game/save", "snapshot:"]) {
    assert.ok(!loadApi.includes(forbidden), `game load API must remain read-only: ${forbidden}`);
  }

  const adapter = read("src/game/adapters/serverSnapshot.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
  ]) assert.ok(!forbidden.test(adapter), `snapshot adapter contains forbidden dependency: ${forbidden}`);
  for (const marker of [
    "applyServerSavePayload",
    "payload.slotKey !== expected.slotKey",
    "payload.accountCharacterId !== expected.accountCharacterId",
    "serverState.player.currentCharacterId !== expected.characterCode",
    "Object.keys(snapshot).length === 0",
  ]) requireMarker(adapter, marker, "server snapshot adapter");

  const store = read("src/stores/game.ts");
  for (const marker of [
    "loadSelectedCharacterSnapshot",
    "gameApi.loadSelectedCharacter",
    "supersedeSnapshotRequest",
    "response.type !== 'game.load'",
    "error.status === 401 || error.status === 403",
    "status: 'loading'",
    "status: 'ready'",
    "status: 'error'",
  ]) requireMarker(store, marker, "snapshot load store lifecycle");
  for (const forbidden of ["method: 'POST'", "Math.random", "localStorage", "sessionStorage"]) {
    assert.ok(!store.includes(forbidden), `snapshot load store crossed mutation boundary: ${forbidden}`);
  }

  const playShell = read("src/components/game/GamePlayShell.vue");
  for (const marker of [
    "game-snapshot-gate",
    "게임 저장을 불러오는 중입니다",
    "서버 저장 다시 불러오기",
    "캐릭터 다시 선택",
    "game.loadSelectedCharacterSnapshot",
    "account.invalidateSession",
  ]) requireMarker(playShell, marker, "snapshot load UI gate");

  const townShell = read("src/components/game/GameTownShell.vue");
  assert.ok(!townShell.includes("watchEffect"), "town shell must not create a default model before snapshot load");
  requireMarker(townShell, "서버 저장을 읽어 typed 게임 상태에 적용했습니다", "town snapshot boundary");

  const styles = read("src/styles/base.css");
  for (const marker of ["/* v394 selected-character server snapshot", ".game-snapshot-gate", ".game-snapshot-gate__actions", "@keyframes game-snapshot-spin"]) {
    requireMarker(styles, marker, "snapshot load responsive CSS");
  }
}

function createPayload(overrides = {}) {
  return {
    userId: 7,
    slotKey: "character-2",
    slotIndex: 2,
    accountCharacterId: "a".repeat(32),
    accountCharacter: {
      id: "a".repeat(32),
      slotIndex: 2,
      name: "기호검신",
      characterCode: "weapon_master",
      createdAt: "2026-09-01T00:00:00Z",
    },
    status: "loaded",
    exists: true,
    clientSaveKey: "character-2",
    saveVersion: 7,
    snapshot: {
      saveVersion: 7,
      player: {
        gold: 98765,
        addAttackSpeed: 220,
        currentCharacterId: "weapon_master",
        skills: {
          lightsabre: { level: 3, isUpgraded: false },
          ironStrike: { level: 2, isUpgraded: false },
        },
      },
      currentZoneIndex: 4,
      currentZoneType: "field",
      fieldEnemyHp: { field_5: 123 },
      fieldRespawnEndAt: {},
    },
    summary: {},
    source: "localStorage",
    note: null,
    integrity: { ok: true, warnings: [] },
    createdAt: "2026-09-01T00:00:00Z",
    updatedAt: "2026-09-03T00:00:00Z",
    ...overrides,
  };
}

function assertAdapterBehavior() {
  const { snapshot, town } = loadAdapters();
  const expected = {
    slotKey: "character-2",
    accountCharacterId: "a".repeat(32),
    characterCode: "weapon_master",
  };
  const payload = createPayload();
  const before = JSON.stringify(payload);
  const loaded = snapshot.applyLoadedGameSnapshot(payload, expected);
  assert.strictEqual(loaded.isEmpty, false);
  assert.strictEqual(loaded.saveVersion, 7);
  assert.strictEqual(loaded.serverState.player.gold, 98765);
  assert.strictEqual(loaded.serverState.player.skills.lightsabre.level, 3);
  assert.strictEqual(loaded.serverState.progress.currentZoneIndex, 4);
  assert.strictEqual(loaded.serverState.progress.fieldEnemyHp.field_5, 123);
  assert.strictEqual(JSON.stringify(payload), before, "snapshot adapter mutated the API payload");

  const model = town.createTownHudViewModel({
    accountCharacterId: expected.accountCharacterId,
    slotKey: expected.slotKey,
    characterName: "기호검신",
    characterCode: expected.characterCode,
    characterLabel: "검신",
    progress: { gold: 1, level: 1, currentZoneIndex: 0, currentZoneType: "town", updatedAt: null },
    serverState: loaded.serverState,
    snapshot: {
      connected: true,
      isEmpty: loaded.isEmpty,
      saveVersion: loaded.saveVersion,
      updatedAt: loaded.updatedAt,
      integrityOk: loaded.integrity.ok,
    },
  });
  assert.strictEqual(model.snapshotConnected, true);
  assert.strictEqual(model.snapshotEmpty, false);
  assert.strictEqual(model.serverState.player.gold, 98765, "server snapshot must win over slot summary");
  assert.strictEqual(model.skills.find((skill) => skill.slotKey === "Q").level, 3);
  assert.strictEqual(model.recentSaveZoneIndex, 4);

  const empty = snapshot.applyLoadedGameSnapshot(createPayload({ snapshot: {}, saveVersion: 0 }), expected);
  assert.strictEqual(empty.isEmpty, true);
  assert.strictEqual(empty.serverState.player.currentCharacterId, "weapon_master");
  assert.strictEqual(empty.serverState.player.skills.lightsabre.level, 1);
  assert.strictEqual(empty.serverState.player.skills.ironStrike.level, 0);
  const emptyModel = town.createTownHudViewModel({
    accountCharacterId: expected.accountCharacterId,
    slotKey: expected.slotKey,
    characterName: "신규검신",
    characterCode: expected.characterCode,
    characterLabel: "검신",
    progress: null,
    serverState: empty.serverState,
    snapshot: {
      connected: true,
      isEmpty: true,
      saveVersion: empty.saveVersion,
      updatedAt: empty.updatedAt,
      integrityOk: false,
    },
  });
  assert.strictEqual(emptyModel.snapshotConnected, true);
  assert.strictEqual(emptyModel.snapshotEmpty, true);
  assert.strictEqual(emptyModel.snapshotStatusLabel, "서버 연결 · 신규 기본 상태");
  assert.strictEqual(emptyModel.recentSaveZoneIndex, null);

  assert.throws(() => snapshot.applyLoadedGameSnapshot(undefined, expected), /완전하지 않습니다/);
  assert.throws(
    () => snapshot.applyLoadedGameSnapshot(createPayload({ accountCharacterId: "b".repeat(32) }), expected),
    /식별 정보/,
  );
  assert.throws(
    () => snapshot.applyLoadedGameSnapshot(createPayload({
      snapshot: { player: { currentCharacterId: "other_character" } },
    }), expected),
    /캐릭터 종류/,
  );
  assert.throws(
    () => snapshot.applyLoadedGameSnapshot(createPayload({ snapshot: [] }), expected),
    /snapshot 형식/,
  );
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue load path validates one selected-character server snapshot without write, reward, random, or storage mutation");
}

main();
