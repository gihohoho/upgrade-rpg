const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.resolve(__dirname, '../../..');
const vue = path.join(root, 'frontend/vue-app');
const esbuild = require(path.join(vue, 'node_modules/esbuild'));
const compiled = esbuild.buildSync({
  stdin: { contents: `
    import { createPinia, setActivePinia } from 'pinia';
    import { useGameStore } from './src/stores/game';
    import { gameApi } from './src/api/gameApi';
    import { ApiRequestError } from './src/api/http';
    import { createDefaultServerState } from './src/game/domain';
    import { createSelectedCharacterSaveRequest } from './src/game/adapters/serverSave';
    import { createLocalRecovery, recoveryKey } from './src/game/save/localRecovery';
    globalThis.test = { createPinia, setActivePinia, useGameStore, gameApi, ApiRequestError, createDefaultServerState, createSelectedCharacterSaveRequest, createLocalRecovery, recoveryKey };
  `, resolveDir: vue, loader: 'ts' }, bundle: true, platform: 'node', format: 'iife', write: false,
  define: { 'process.env.NODE_ENV': '"test"', 'import.meta.env': '{}' },
}).outputFiles[0].text;

function fixture() {
  const entries = new Map();
  const storage = { getItem: (key) => entries.get(key) ?? null, setItem: (key, value) => entries.set(key, value) };
  const sandbox = { window: { localStorage: storage }, Buffer, AbortController, setTimeout, setInterval, clearInterval };
  vm.createContext(sandbox);
  vm.runInContext(compiled, sandbox);
  const m = sandbox.test;
  m.setActivePinia(m.createPinia());
  const game = m.useGameStore();
  const identity = { userId: 7, slotKey: 'character-1', accountCharacterId: 'a'.repeat(32), characterCode: 'weapon_master' };
  const character = { id: identity.accountCharacterId, slotIndex: 1, name: '복구 검사', characterCode: 'weapon_master', createdAt: '2026-09-06T00:00:00Z' };
  const slot = { ...identity, slotIndex: 1, occupied: true, accountCharacter: character, progress: null };
  const options = { token: 'synthetic-token-never-persist', userId: 7, slot, characterLabel: '검신' };
  const state = m.createDefaultServerState();
  state.player.gold = 100;
  state.player.level = 3;
  let server = m.createSelectedCharacterSaveRequest({ ...identity, serverState: state, saveVersion: 1 }, 'manual').snapshot;
  let posts = 0;
  const envelope = (status, snapshot, request = {}) => {
    const payload = { ...request, ...identity, accountCharacter: character, slotIndex: 1, status, exists: true, snapshot, saveVersion: 1, updatedAt: '2026-09-06T00:00:00Z', integrity: { ok: true, warnings: [] } };
    return { type: status === 'loaded' ? 'game.load' : 'game.save', payload, data: payload };
  };
  m.gameApi.loadSelectedCharacter = async () => envelope('loaded', server);
  m.gameApi.saveSelectedCharacter = async (_token, request) => { posts++; server = request.snapshot; return envelope('saved', server, request); };
  const local = m.createLocalRecovery(() => storage);
  const key = m.recoveryKey(identity);
  return { m, game, identity, slot, options, state, entries, storage, local, key, envelope, posts: () => posts,
    load: () => game.loadSelectedCharacterSnapshot(options),
    save: () => game.enqueueSelectedCharacterSave({ ...options, reason: 'manual' }),
    setServer: (value) => { server = value; },
    seedPending: (gold = 900) => { state.player.gold = gold; const request = m.createSelectedCharacterSaveRequest({ ...identity, serverState: state, saveVersion: 1 }, 'manual'); return local.capture(identity, request, local.read(identity)); },
  };
}

async function assertOwnedTransfers() {
  function ownedFixture() {
    const f = fixture();
    f.state.player.inventory = [{ id: 'same', name: '첫 묶음', count: 5, level: 0, extra: { rune: 3 } }, null, { id: 'same', name: '두 번째', count: 2, level: 7 }];
    f.state.player.storage = [null, { id: 'kept', name: '보관중', count: 4 }];
    f.setServer(f.m.createSelectedCharacterSaveRequest({ ...f.identity, serverState: f.state, saveVersion: 1 }, 'manual').snapshot);
    f.move = (container = 'inventory', selectionKey = 'inventory:2') => f.game.mutateOwnedItems({ ...f.options, action: { type: 'move', container, selectionKey } });
    f.sort = (container) => f.game.mutateOwnedItems({ ...f.options, action: { type: 'sort', container } });
    f.ready = async () => { await f.load(); f.game.enterInventoryPreview([]); f.game.selectInventoryPreview('inventory:2'); };
    return f;
  }
  let f = ownedFixture(); await f.ready();
  const original = JSON.stringify(f.game.model.serverState.player);
  f.game.toggleInventoryCompactPreview();
  assert.strictEqual(await f.move(), 'saved', 'preview selection uses original slot, not display index');
  let player = f.game.model.serverState.player;
  assert.strictEqual(player.inventory[2], null);
  assert.strictEqual(player.inventory.length, 3);
  assert.strictEqual(player.inventory[0].count, 5);
  assert.strictEqual(player.storage[0].name, '두 번째');
  assert.strictEqual(player.storage[0].count, 2);
  assert.strictEqual(player.storage[1].id, 'kept');
  assert.strictEqual(f.posts(), 1);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, false);
  f.game.enterStorageTrashPreview(); f.game.selectStorageTrashPreview('storage', 'storage:0');
  assert.strictEqual(await f.move('storage', 'storage:0'), 'saved');
  assert.strictEqual(f.game.model.serverState.player.inventory[1].name, '두 번째');
  assert.strictEqual(f.game.model.serverState.player.storage[0], null);
  assert.strictEqual(JSON.stringify(f.state.player), original, 'source fixture immutable');
  assert.strictEqual(await f.sort('inventory'), 'cancelled', 'already sorted does not POST');
  assert.strictEqual(await f.sort('storage'), 'saved');
  assert.strictEqual(f.game.model.serverState.player.storage[0].id, 'kept');
  const sortedPosts = f.posts();
  assert.strictEqual(await f.sort('storage'), 'cancelled');
  assert.strictEqual(f.posts(), sortedPosts);
  assert.strictEqual(await f.sort('trash'), 'cancelled', 'trash mutations out of scope');

  for (const status of [0, 401, 403, 409, 503]) {
    f = ownedFixture(); await f.ready();
    f.m.gameApi.saveSelectedCharacter = async () => { throw new f.m.ApiRequestError('synthetic failure', { status }); };
    await f.move();
    assert.strictEqual(f.game.model.serverState.player.inventory[2], null);
    const local = f.local.read(f.identity);
    assert.strictEqual(local.entry.current.pending, true);
    assert.strictEqual(local.entry.current.snapshot.player.storage[0].count, 2);
    assert.strictEqual(f.game.canMutateItems, false);
    assert.strictEqual(await f.move(), 'cancelled');
    f.game.resetShell(); await f.load();
    assert.strictEqual(f.game.snapshotLoad.status, 'recovery');
  }
  f = ownedFixture(); await f.ready();
  const beforeQuota = JSON.stringify(f.game.model.serverState);
  assert.strictEqual(await f.game.mutateOwnedItems({ ...f.options, userId: 99, action: { type: 'move', container: 'inventory', selectionKey: 'inventory:2' } }), 'cancelled');
  f.storage.setItem = () => { throw new Error('quota'); };
  assert.strictEqual(await f.move(), 'error');
  assert.strictEqual(JSON.stringify(f.game.model.serverState), beforeQuota);
  assert.strictEqual(f.posts(), 0, 'quota blocks mutation and POST');

  f = ownedFixture(); await f.ready();
  f.m.gameApi.saveSelectedCharacter = async () => { throw new f.m.ApiRequestError('offline', { status: 503 }); };
  await f.move();
  assert.ok(f.game.model.snapshotStatusLabel.startsWith('이 기기 복구본'));
  const moved = JSON.stringify(f.game.model.serverState);
  f.m.gameApi.saveSelectedCharacter = async (_token, request) => f.envelope('saved', request.snapshot, request);
  assert.strictEqual(await f.save(), 'saved');
  assert.strictEqual(JSON.stringify(f.game.model.serverState), moved, 'retry saves without repeating the move');
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, false);
  assert.strictEqual(f.game.canMutateItems, true);

  f = ownedFixture(); await f.ready();
  const beforeStale = JSON.stringify(f.game.model.serverState);
  f.entries.set(f.key, 'changed-by-another-tab');
  assert.strictEqual(await f.move(), 'conflict');
  assert.strictEqual(JSON.stringify(f.game.model.serverState), beforeStale);
  assert.strictEqual(f.entries.get(f.key), 'changed-by-another-tab');

  f = ownedFixture();
  f.state.player.storage = Array.from({ length: 60 }, (_, id) => ({ id, name: '가득 참' }));
  f.setServer(f.m.createSelectedCharacterSaveRequest({ ...f.identity, serverState: f.state, saveVersion: 1 }, 'manual').snapshot);
  await f.ready(); const full = JSON.stringify(f.game.model.serverState);
  assert.strictEqual(await f.move(), 'cancelled');
  assert.strictEqual(JSON.stringify(f.game.model.serverState), full);
  assert.strictEqual(f.posts(), 0);

  f = ownedFixture(); await f.ready();
  let resolveSave;
  f.m.gameApi.saveSelectedCharacter = (_token, request) => new Promise((resolve) => { resolveSave = () => resolve(f.envelope('saved', request.snapshot, request)); });
  const pendingMove = f.move();
  await Promise.resolve(); await Promise.resolve();
  assert.strictEqual(f.game.itemAction.busy, true);
  assert.strictEqual(await f.move(), 'cancelled', 'double click blocked');
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, true);
  f.game.resetShell(); resolveSave();
  assert.strictEqual(await pendingMove, 'cancelled');
  assert.strictEqual(f.game.model, null);
  assert.strictEqual(f.game.itemAction.message, '');
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, true, 'stale response cannot acknowledge');
}

async function main() {
  await assertOwnedTransfers();
  let f = fixture();
  f.state.player.inventory = [{ id: 'owned-a', name: '소유 A' }, null, { id: 'owned-b', name: '소유 B' }];
  f.state.player.storage = [null, { id: 'stored', name: '보관 A' }];
  f.setServer(f.m.createSelectedCharacterSaveRequest({ ...f.identity, serverState: f.state, saveVersion: 1 }, 'manual').snapshot);
  await f.load();
  const ownedBefore = JSON.stringify(f.game.model.serverState);
  assert.strictEqual(f.game.enterInventoryPreview([]), true, 'owned UI works without master-data');
  f.game.selectInventoryPreview('inventory:2');
  assert.strictEqual(f.game.inventoryModel.selectedItem.instanceId, 'owned-b');
  f.game.toggleInventoryCompactPreview();
  assert.strictEqual(f.game.inventoryModel.selectedSlotNumber, 2);
  assert.strictEqual(f.game.enterStorageTrashPreview(), true);
  assert.strictEqual(f.game.storageTrashModel.storage.slots[1].item.instanceId, 'stored');
  f.game.toggleStorageTrashCompactPreview('storage');
  assert.strictEqual(f.game.storageTrashModel.storage.slots[0].item.instanceId, 'stored');
  assert.strictEqual(JSON.stringify(f.game.model.serverState), ownedBefore);
  assert.strictEqual(f.posts(), 0, 'owned display and sorting must never POST');
  f.game.resetShell();
  assert.strictEqual(f.game.inventoryModel, null);
  assert.strictEqual(f.game.storageTrashModel, null);

  f = fixture();
  f.seedPending();
  const pending = f.entries.get(f.key);
  assert.strictEqual(await f.load(), 'recovery');
  assert.strictEqual(f.game.model, null);
  assert.strictEqual(f.posts(), 0);
  assert.strictEqual(await f.save(), 'cancelled');
  assert.strictEqual(await f.game.resolveRecovery('local', 'wrong-token', 7), 'cancelled');
  assert.strictEqual(await f.game.resolveRecovery('local', f.options.token, 8), 'cancelled');
  f.game.resetShell(); // Cancel leaves both originals and the marker byte-for-byte intact.
  assert.strictEqual(f.entries.get(f.key), pending);
  assert.strictEqual(await f.load(), 'recovery');
  assert.strictEqual(await f.game.resolveRecovery('server', f.options.token, 7), 'ready');
  assert.strictEqual(f.posts(), 0);
  assert.strictEqual(f.game.model.serverState.player.gold, 100);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, false);
  assert.strictEqual(f.local.read(f.identity).entry.backups[0].snapshot.player.gold, 900);

  f = fixture(); f.seedPending(); await f.load();
  assert.strictEqual(await f.game.resolveRecovery('local', f.options.token, 7), 'saved');
  assert.strictEqual(f.posts(), 1);
  assert.strictEqual(f.game.model.serverState.player.gold, 900);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, false);
  assert.ok(!f.entries.get(f.key).includes(f.options.token));

  f = fixture(); f.seedPending(); await f.load();
  f.m.gameApi.saveSelectedCharacter = async () => { throw new f.m.ApiRequestError('offline', { status: 503 }); };
  assert.strictEqual(await f.game.resolveRecovery('local', f.options.token, 7), 'error');
  assert.match(f.game.model.snapshotStatusLabel, /이 기기 복구본/);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, true);

  f = fixture(); const unread = f.seedPending();
  f.m.gameApi.loadSelectedCharacter = async () => { throw new f.m.ApiRequestError('expired', { status: 401 }); };
  assert.strictEqual(await f.load(), 'session-invalid');
  assert.strictEqual(f.entries.get(f.key), unread.raw);
  f.m.gameApi.loadSelectedCharacter = async () => { const response = f.envelope('loaded', {}); response.data.userId = 8; return response; };
  assert.strictEqual(await f.load(), 'error');
  assert.strictEqual(f.game.model, null);

  for (const status of [0, 401, 403, 409, 503]) {
    f = fixture(); await f.load();
    f.game.model.serverState.player.gold = 555;
    f.m.gameApi.saveSelectedCharacter = async () => { throw new f.m.ApiRequestError('synthetic failure', { status }); };
    await f.save();
    assert.strictEqual(f.local.read(f.identity).entry.current.pending, true);
    assert.strictEqual(f.local.read(f.identity).entry.current.snapshot.player.gold, 555);
    f.game.resetShell();
    assert.strictEqual(await f.load(), 'recovery', `${status} must preserve a recovery choice after re-entry`);
  }

  f = fixture(); await f.load();
  const waiting = [];
  f.m.gameApi.saveSelectedCharacter = (_token, request) => new Promise(resolve => waiting.push(() => resolve(f.envelope('saved', request.snapshot, request))));
  f.game.model.serverState.player.gold = 200;
  const first = f.save();
  await new Promise(resolve => setTimeout(resolve, 0));
  f.game.model.serverState.player.gold = 300;
  const second = f.save();
  waiting.shift()(); await first;
  assert.strictEqual(f.local.read(f.identity).entry.current.snapshot.player.gold, 300);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, true, 'old ack cleared a newer pending copy');
  await new Promise(resolve => setTimeout(resolve, 0));
  waiting.shift()(); await second;
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, false);

  f = fixture(); await f.load();
  f.game.model.serverState.player.gold = 777;
  f.game.preserveLocalProgress();
  assert.strictEqual(f.posts(), 0, 'unload preservation must never call the network');
  assert.strictEqual(f.local.read(f.identity).entry.current.snapshot.player.gold, 777);
  assert.strictEqual(f.local.read(f.identity).entry.current.pending, true);

  f = fixture(); const original = f.seedPending(); await f.load();
  f.seedPending(999); // A second tab changes the record while the choice is open.
  assert.strictEqual(await f.game.resolveRecovery('server', f.options.token, 7), 'error');
  assert.strictEqual(f.local.read(f.identity).entry.current.snapshot.player.gold, 999);
  assert.strictEqual(f.posts(), 0);
  assert.throws(() => f.local.write(f.identity, original, original.entry.current), /변경/);

  f = fixture(); f.seedPending();
  assert.strictEqual(f.local.read({ ...f.identity, userId: 8 }).entry, null);
  assert.strictEqual(f.local.read({ ...f.identity, accountCharacterId: 'b'.repeat(32) }).entry, null);
  const invalid = JSON.parse(f.entries.get(f.key)); invalid.identity.userId = 8;
  f.entries.set(f.key, JSON.stringify(invalid));
  assert.strictEqual(await f.load(), 'error');
  assert.strictEqual(f.posts(), 0);
  f.entries.set(f.key, '{broken'); assert.strictEqual(await f.load(), 'error');
  assert.strictEqual(f.entries.get(f.key), '{broken');

  f = fixture(); const preserved = f.seedPending(); await f.load();
  f.storage.setItem = () => { throw new Error('quota'); };
  assert.strictEqual(await f.game.resolveRecovery('server', f.options.token, 7), 'error');
  assert.strictEqual(f.entries.get(f.key), preserved.raw);
  f = fixture(); await f.load(); f.storage.setItem = () => { throw new Error('quota'); };
  assert.strictEqual(await f.save(), 'saved', 'storage quota must not prevent an available server save');
  assert.match(f.game.recoveryWarning, /기록하지 못했습니다/);

  f = fixture(); const savedLocal = f.seedPending(444); f.local.acknowledge(f.identity, savedLocal); f.setServer({});
  assert.strictEqual(await f.load(), 'ready');
  assert.strictEqual(f.game.model.serverState.player.gold, 444);
  assert.strictEqual(f.posts(), 1, 'empty server fallback uses the serialized save queue');
  f = fixture(); const different = f.seedPending(222); f.local.acknowledge(f.identity, different);
  assert.strictEqual(await f.load(), 'ready');
  assert.strictEqual(f.game.model.serverState.player.gold, 100);
  assert.strictEqual(f.local.read(f.identity).entry.backups[0].snapshot.player.gold, 222);

  const play = fs.readFileSync(path.join(vue, 'src/components/game/GamePlayShell.vue'), 'utf8');
  for (const marker of ['이 기기 저장 사용', '서버 저장 사용', '취소 · 캐릭터 선택으로', 'beforeunload', 'game.preserveLocalProgress', 'game.resolveRecovery', 'initialFocus: recoveryCancel']) assert.ok(play.includes(marker), marker);
  assert.ok(!fs.readFileSync(path.join(vue, 'src/game/save/localRecovery.ts'), 'utf8').includes('removeItem('));
  console.log('PASS: Vue recovery and owned transfers preserve pending snapshots, quantities and identity; handle explicit recovery, full destinations, quota, stale responses, double clicks and save retries');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
