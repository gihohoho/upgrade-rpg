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

function loadModules() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: [
        "import * as save from './src/game/adapters/serverSave.ts';",
        "import * as queue from './src/game/save/serializedSaveQueue.ts';",
        "import * as state from './src/game/domain/state.ts';",
        "import { createPinia, setActivePinia } from 'pinia';",
        "import { useGameStore } from './src/stores/game.ts';",
        "import { gameApi } from './src/api/gameApi.ts';",
        "import { ApiRequestError } from './src/api/http.ts';",
        "globalThis.__saveQueue = { save, queue, state, createPinia, setActivePinia, useGameStore, gameApi, ApiRequestError };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "serialized-save-queue-smoke-harness.ts",
      loader: "ts",
    },
    bundle: true,
    platform: "node",
    format: "iife",
    target: "node20",
    define: { "process.env.NODE_ENV": '"test"', "import.meta.env": "{}" },
    write: false,
  });
  const context = { Buffer, setTimeout, setInterval, clearInterval };
  vm.createContext(context);
  vm.runInContext(output.outputFiles[0].text, context);
  return context.__saveQueue;
}

function assertStaticBoundary() {
  const api = read("src/api/gameApi.ts");
  for (const marker of [
    "saveSelectedCharacter",
    "requestApi<GameSavePayload, GameSaveData>('/game/save'",
    "method: 'POST'",
    "token",
    "body: request",
  ]) requireMarker(api, marker, "typed game save API");

  const adapter = read("src/game/adapters/serverSave.ts");
  for (const marker of [
    "createServerSavePayload",
    "accountCharacterId: source.accountCharacterId",
    "slotKey: source.slotKey",
    "snapshot.player.currentCharacterId !== source.characterCode",
    "inventoryItems: countFilled",
    "payload.status !== 'saved'",
  ]) requireMarker(adapter, marker, "server save adapter");
  for (const forbidden of ["localStorage", "sessionStorage", "Math.random", "expectedRevision"]) {
    assert.ok(!adapter.includes(forbidden), `save adapter invented an unsupported dependency or CAS field: ${forbidden}`);
  }

  const queue = read("src/game/save/serializedSaveQueue.ts");
  for (const marker of ["createSerializedSaveQueue", "const frozenRequest", ".catch(() => undefined)", "drain: () => tail"]) {
    requireMarker(queue, marker, "serialized queue");
  }
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "Math.random"]) {
    assert.ok(!queue.includes(forbidden), `serialized queue crossed its pure orchestration boundary: ${forbidden}`);
  }

  const store = read("src/stores/game.ts");
  for (const marker of [
    "enqueueSelectedCharacterSave",
    "serializedSaveQueue.enqueue",
    "executeQueuedSave",
    "flushSelectedCharacterSave",
    "combatController.pause('transition')",
    "error.status === 409",
    "자동으로 덮어쓰지 않았습니다",
  ]) requireMarker(store, marker, "save queue store lifecycle");
  for (const forbidden of ["localStorage", "sessionStorage", "Math.random"]) {
    assert.ok(!store.includes(forbidden), `store crossed the v395 save boundary: ${forbidden}`);
  }

  const play = read("src/components/game/GamePlayShell.vue");
  for (const marker of ["60_000", "runAutosave", "stopAutosaveTimer", "reason: 'auto'", "game.saveTransitioning", "game.saveQueue.errorKind === 'conflict'"]) {
    requireMarker(play, marker, "autosave lifecycle");
  }

  const town = read("src/components/game/GameTownShell.vue");
  for (const marker of [
    "지금 서버에 저장",
    "reason: 'manual'",
    "transitionFromGame('character-switch')",
    "transitionFromGame('logout')",
    "game.flushSelectedCharacterSave",
    "409 감시",
  ]) requireMarker(town, marker, "manual and transition save UI");
}

function createSource(modules) {
  const serverState = modules.state.createDefaultServerState({ defaultCharacterId: "weapon_master" });
  serverState.player.gold = 98765;
  serverState.player.level = 23;
  serverState.player.inventory = [null, { id: "item-1" }, undefined, { id: "item-2" }];
  serverState.progress.currentZoneIndex = 4;
  serverState.progress.currentZoneType = "field";
  return {
    userId: 7,
    slotKey: "character-2",
    accountCharacterId: "a".repeat(32),
    characterCode: "weapon_master",
    saveVersion: 7,
    serverState,
  };
}

function assertAdapterBehavior(modules) {
  const source = createSource(modules);
  const before = JSON.stringify(source.serverState);
  const request = modules.save.createSelectedCharacterSaveRequest(source, "manual", "2026-09-05T00:00:00Z");
  assert.strictEqual(request.accountCharacterId, source.accountCharacterId);
  assert.strictEqual(request.slotKey, source.slotKey);
  assert.strictEqual(request.saveVersion, 7);
  assert.strictEqual(request.snapshot.saveVersion, 7);
  assert.strictEqual(request.snapshot.player.gold, 98765);
  assert.strictEqual(request.summary.inventoryItems, 2);
  assert.strictEqual(request.summary.currentZoneIndex, 4);
  assert.strictEqual(request.source, "vue-manual-save");
  assert.strictEqual(Object.prototype.hasOwnProperty.call(request, "expectedRevision"), false);
  assert.strictEqual(JSON.stringify(source.serverState), before, "save adapter mutated the live typed state");

  request.snapshot.player.gold = 1;
  assert.strictEqual(source.serverState.player.gold, 98765, "save request must be a detached capture");

  const accepted = modules.save.acceptSelectedCharacterSave({
    ...request,
    userId: 7,
    slotIndex: 2,
    status: "saved",
    exists: true,
    accountCharacter: {
      id: source.accountCharacterId,
      slotIndex: 2,
      name: "기호검신",
      characterCode: source.characterCode,
      createdAt: "2026-09-01T00:00:00Z",
    },
    integrity: { ok: true, warnings: [] },
    updatedAt: "2026-09-05T00:00:01Z",
  }, source);
  assert.strictEqual(accepted.saveVersion, 7);
  assert.strictEqual(accepted.integrityOk, true);
  assert.throws(() => modules.save.acceptSelectedCharacterSave({
    status: "saved",
    exists: true,
    slotKey: "character-3",
    accountCharacterId: source.accountCharacterId,
  }, source), /식별 정보/);
}

async function assertQueueBehavior(modules) {
  const events = [];
  let active = 0;
  let maxActive = 0;
  const completed = [];
  const queue = modules.queue.createSerializedSaveQueue({
    clone: (request) => JSON.parse(JSON.stringify(request)),
    onChange: (snapshot) => events.push({ ...snapshot }),
  });
  const first = { sequence: 1, nested: { captured: "first" } };
  const firstWrite = queue.enqueue({
    request: first,
    execute: async (request) => {
      active += 1;
      maxActive = Math.max(maxActive, active);
      await new Promise((resolve) => setTimeout(resolve, 10));
      completed.push(`${request.sequence}:${request.nested.captured}`);
      active -= 1;
    },
  });
  first.nested.captured = "mutated-after-enqueue";
  const secondWrite = queue.enqueue({
    request: { sequence: 2, nested: { captured: "second" } },
    execute: async (request) => {
      active += 1;
      maxActive = Math.max(maxActive, active);
      completed.push(`${request.sequence}:${request.nested.captured}`);
      active -= 1;
    },
  });
  await queue.drain();
  await Promise.all([firstWrite, secondWrite]);
  assert.deepStrictEqual(completed, ["1:first", "2:second"]);
  assert.strictEqual(maxActive, 1, "save writes were not serialized");
  assert.strictEqual(queue.getSnapshot().queuedWrites, 0);
  assert.strictEqual(queue.getSnapshot().active, false);
  assert.ok(events.some((event) => event.queuedWrites === 2), "queue never exposed both queued writes");

  await assert.rejects(queue.enqueue({
    request: { sequence: 3, nested: { captured: "failure" } },
    execute: async () => { throw new Error("temporary outage"); },
  }), /temporary outage/);
  await queue.enqueue({
    request: { sequence: 4, nested: { captured: "recovery" } },
    execute: async (request) => { completed.push(`${request.sequence}:${request.nested.captured}`); },
  });
  assert.strictEqual(completed.at(-1), "4:recovery", "a failed write poisoned later queue work");
}

function savedEnvelope(request, source) {
  return {
    ok: true,
    responseVersion: "1",
    type: "game.save",
    requestId: "smoke",
    payload: {
      userId: source.userId,
      slotKey: source.slotKey,
      slotIndex: 2,
      accountCharacterId: source.accountCharacterId,
      accountCharacter: {
        id: source.accountCharacterId,
        slotIndex: 2,
        name: "기호검신",
        characterCode: source.characterCode,
        createdAt: "2026-09-01T00:00:00Z",
      },
      status: "saved",
      exists: true,
      clientSaveKey: request.clientSaveKey,
      saveVersion: request.saveVersion,
      snapshot: request.snapshot,
      summary: request.summary,
      source: request.source,
      note: request.note,
      integrity: { ok: true, warnings: [] },
      createdAt: "2026-09-01T00:00:00Z",
      updatedAt: "2026-09-05T00:00:01Z",
    },
    data: {
      status: "saved",
      userId: source.userId,
      slotKey: source.slotKey,
      accountCharacterId: source.accountCharacterId,
      saveVersion: request.saveVersion,
      integrity: { ok: true, warnings: [] },
    },
    meta: {},
    error: null,
  };
}

async function assertStoreBehavior(modules) {
  modules.setActivePinia(modules.createPinia());
  const game = modules.useGameStore();
  const source = createSource(modules);
  const slot = {
    slotIndex: 2,
    slotKey: source.slotKey,
    occupied: true,
    accountCharacterId: source.accountCharacterId,
    accountCharacter: {
      id: source.accountCharacterId,
      slotIndex: 2,
      name: "기호검신",
      characterCode: source.characterCode,
      createdAt: "2026-09-01T00:00:00Z",
    },
    progress: null,
  };
  game.enterTown(slot, "검신", {
    slotKey: source.slotKey,
    accountCharacterId: source.accountCharacterId,
    saveVersion: source.saveVersion,
    serverState: source.serverState,
    isEmpty: false,
    source: "smoke",
    updatedAt: "2026-09-04T00:00:00Z",
    integrity: { ok: true, warnings: [] },
  });
  game.snapshotLoad = {
    status: "ready", errorKind: null, message: "ready",
    slotKey: source.slotKey, accountCharacterId: source.accountCharacterId,
  };

  let active = 0;
  let maxActive = 0;
  const requests = [];
  modules.gameApi.saveSelectedCharacter = async (token, request) => {
    assert.strictEqual(token, "save-token");
    active += 1;
    maxActive = Math.max(maxActive, active);
    requests.push(JSON.parse(JSON.stringify(request)));
    await new Promise((resolve) => setTimeout(resolve, 5));
    active -= 1;
    return savedEnvelope(request, source);
  };
  const results = await Promise.all([
    game.enqueueSelectedCharacterSave({ token: "save-token", userId: 7, slot, reason: "manual" }),
    game.enqueueSelectedCharacterSave({ token: "save-token", userId: 7, slot, reason: "auto" }),
  ]);
  assert.deepStrictEqual(Array.from(results), ["saved", "saved"]);
  assert.strictEqual(maxActive, 1, "Pinia store bypassed the serializer queue");
  assert.deepStrictEqual(requests.map((request) => request.source), ["vue-manual-save", "vue-auto-save"]);
  assert.strictEqual(game.saveQueue.status, "saved");
  assert.strictEqual(game.saveQueue.queuedWrites, 0);

  modules.gameApi.saveSelectedCharacter = async () => {
    throw new modules.ApiRequestError("conflict", { status: 409 });
  };
  const conflict = await game.enqueueSelectedCharacterSave({ token: "save-token", userId: 7, slot, reason: "manual" });
  assert.strictEqual(conflict, "conflict");
  assert.strictEqual(game.saveQueue.errorKind, "conflict");
  assert.match(game.saveQueue.message, /덮어쓰지 않았습니다/);

  modules.gameApi.saveSelectedCharacter = async (_token, request) => savedEnvelope(request, source);
  const transition = await game.flushSelectedCharacterSave({
    token: "save-token", userId: 7, slot, reason: "character-switch",
  });
  assert.strictEqual(transition, "saved");
  assert.strictEqual(game.saveTransitioning, true, "transition must stay locked until account context is cleared");
  game.resetShell();
  assert.strictEqual(game.saveTransitioning, false);
}

async function main() {
  assertStaticBoundary();
  const modules = loadModules();
  assertAdapterBehavior(modules);
  await assertQueueBehavior(modules);
  await assertStoreBehavior(modules);
  console.log("PASS: Vue selected-character saves use one frozen, failure-tolerant serialized queue with manual, auto, and transition gates");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
