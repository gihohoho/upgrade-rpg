const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..", "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

function createStorage() {
	const values = new Map();
	return {
		getItem(key) { return values.has(String(key)) ? values.get(String(key)) : null; },
		setItem(key, value) { values.set(String(key), String(value)); },
		removeItem(key) { values.delete(String(key)); },
	};
}

async function run() {
	const html = read("index.html");
	const authSource = read("src/api/auth-session.js");
	const clientSource = read("src/api/game-api-client.js");
	const bridgeSource = read("src/api/save-data-bridge.js");
	const gateSource = read("src/ui/account-gate.js");
	const mainSource = read("src/app/main.js");
	const combatSource = read("src/systems/combat-system.js");
	const css = read("src/styles/account.css");

	assert.match(html, /<body class="account-gate-active">/);
	assert.match(html, /id="game-root"[^>]+aria-hidden="true"[^>]+inert/);
	assert.match(html, /src\/styles\/account\.css\?v=371/);
	assert(html.indexOf("auth-session.js?v=371") < html.indexOf("game-api-client.js?v=371"));
	assert(html.indexOf("account-gate.js?v=371") < html.indexOf("main.js?v=370"));
	assert.match(html, /src\/systems\/combat-system\.js\?v=370/);
	assert.match(html, /src\/api\/admin-readonly-overview\.js\?v=370/);

	const localStorage = createStorage();
	const sessionStorage = createStorage();
	const calls = [];
	const context = {
		console,
		URL,
		AbortController,
		localStorage,
		sessionStorage,
		setTimeout,
		clearTimeout,
		fetch: async (url, options) => {
			calls.push({ url: String(url), options });
			return { ok: true, status: 200, async json() { return { ok: true, payload: {} }; } };
		},
	};
	context.window = context;
	vm.runInNewContext(authSource, context, { filename: "auth-session.js" });

	const characterId = "0123456789abcdef0123456789abcdef";
	context.RpgAuthSession.setCurrentUser({ id: 17, username: "safe_user", isAdmin: false });
	const character = context.RpgAuthSession.storeSelectedCharacter({
		slotIndex: 6,
		accountCharacter: { id: characterId, slotIndex: 6, name: "검신_1", characterCode: "weapon_master" },
		progress: { level: 22, currentZoneIndex: 4 },
	});
	assert.equal(character.accountCharacterId, characterId);
	assert.equal(character.summary.level, 22);
	assert.equal(context.getCurrentAccountLocalSaveKey(), `idleRpgSaveV22.u17.c${characterId}`);
	assert.equal(context.getCurrentAccountBackendSlotKey(), "character-6");

	context.RpgAuthSession.storeAccessToken("session-token", false);
	assert.equal(sessionStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), "session-token");
	assert.equal(localStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), null);
	context.RpgAuthSession.storeAccessToken("local-token", true);
	assert.equal(localStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), "local-token");
	assert.equal(sessionStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), null);

	vm.runInNewContext(clientSource, context, { filename: "game-api-client.js" });
	await context.RpgGameApi.loginAccount({ identifier: "safe_user", password: "Password1" });
	assert.equal(calls.at(-1).options.headers.Authorization, undefined, "login must not send an existing bearer token");
	await context.RpgGameApi.listAccountCharacters();
	assert.equal(calls.at(-1).options.headers.Authorization, "Bearer local-token");
	await context.RpgGameApi.loadGameSnapshot({ slotKey: "character-6", accountCharacterId: characterId });
	const loadUrl = new URL(calls.at(-1).url);
	assert.equal(loadUrl.searchParams.get("slotKey"), "character-6");
	assert.equal(loadUrl.searchParams.get("accountCharacterId"), characterId);

	context.fetch = async () => { throw new Error("temporary network outage"); };
	const retryableRestore = await context.RpgAuthSession.restoreSession({ timeoutMs: 0 });
	assert.equal(retryableRestore.reason, "session-unavailable");
	assert.equal(retryableRestore.retryable, true);
	assert.equal(localStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), "local-token", "network failure must preserve persistent token");
	context.fetch = async () => ({ ok: false, status: 401, async json() { return { detail: "expired" }; } });
	const expiredRestore = await context.RpgAuthSession.restoreSession({ timeoutMs: 0 });
	assert.equal(expiredRestore.reason, "session-invalid");
	assert.equal(localStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), null, "401 must discard expired token");
	context.RpgAuthSession.storeAuthNotice("expired locally preserved");
	assert.equal(context.RpgAuthSession.consumeAuthNotice(), "expired locally preserved");
	assert.equal(context.RpgAuthSession.consumeAuthNotice(), "");
	context.RpgAuthSession.storeAccessToken("inactive-token", true);
	context.fetch = async () => ({ ok: false, status: 403, async json() { return { detail: "inactive" }; } });
	const inactiveRestore = await context.RpgAuthSession.restoreSession({ timeoutMs: 0 });
	assert.equal(inactiveRestore.reason, "session-invalid");
	assert.equal(localStorage.getItem(context.RpgAuthSession.ACCESS_TOKEN_KEY), null, "403 inactive account must discard its unusable token");

	context.RpgAuthSession.storeAccessToken("queue-token", false);
	context.RpgAuthSession.setCurrentUser({ id: 17, username: "safe_user", isAdmin: false });
	context.RpgAuthSession.storeSelectedCharacter(character);
	localStorage.setItem(context.getCurrentAccountLocalSaveKey(), JSON.stringify({ saveVersion: 5, player: { currentCharacterId: "weapon_master" } }));
	let activeWrites = 0;
	let maxActiveWrites = 0;
	let completedWrites = 0;
	context.RpgGameApi = {
		async saveGameSnapshot() {
			activeWrites += 1;
			maxActiveWrites = Math.max(maxActiveWrites, activeWrites);
			await new Promise((resolve) => setTimeout(resolve, 10));
			activeWrites -= 1;
			completedWrites += 1;
			return { ok: true, data: { status: "saved" }, payload: {} };
		},
		async loadGameSnapshot() { return { ok: true, payload: { snapshot: {} }, data: { exists: true } }; },
	};
	vm.runInNewContext(bridgeSource, context, { filename: "save-data-bridge.js" });
	await Promise.all([
		context.enqueueBackendSaveSnapshotWrite({ source: "smoke-one" }),
		context.enqueueBackendSaveSnapshotWrite({ source: "smoke-two" }),
	]);
	assert.equal(completedWrites, 2);
	assert.equal(maxActiveWrites, 1, "all backend save writes must share one serializer queue");
	const queueState = context.getBackendSaveWriteQueueState();
	assert.equal(queueState.queuedWrites, 0);
	assert.equal(queueState.idle, true);
	context.RpgGameApi.saveGameSnapshot = async () => {
		const error = new Error("temporary database outage");
		error.status = 503;
		throw error;
	};
	await assert.rejects(context.enqueueBackendSaveSnapshotWrite({ source: "smoke-failed-write" }), /temporary database outage/);
	const pendingMarker = context.RpgAuthSession.getPendingUnsyncedSave({ userId: 17, accountCharacterId: characterId });
	assert.equal(pendingMarker.accountCharacterId, characterId);
	assert.equal(pendingMarker.slotKey, "character-6");
	assert.equal(pendingMarker.status, 503);
	context.RpgGameApi.saveGameSnapshot = async () => ({ ok: true, data: { status: "saved" }, payload: {} });
	await context.enqueueBackendSaveSnapshotWrite({ source: "smoke-retry-success" });
	assert.equal(context.RpgAuthSession.getPendingUnsyncedSave({ userId: 17, accountCharacterId: characterId }), null, "successful serialized retry must clear pending marker");
	let resolveOlderWrite;
	context.RpgGameApi.saveGameSnapshot = () => new Promise((resolve) => { resolveOlderWrite = resolve; });
	const olderWrite = context.enqueueBackendSaveSnapshotWrite({ source: "smoke-older-inflight" });
	await new Promise((resolve) => setTimeout(resolve, 0));
	context.RpgAuthSession.markPendingUnsyncedSave({
		userId: 17,
		accountCharacterId: characterId,
		saveKey: context.getCurrentAccountLocalSaveKey(),
		slotKey: "character-6",
		reason: "beforeunload-local-only",
	});
	resolveOlderWrite({ ok: true, data: { status: "saved" }, payload: {} });
	await olderWrite;
	assert.equal(context.RpgAuthSession.getPendingUnsyncedSave({ userId: 17, accountCharacterId: characterId }).reason, "beforeunload-local-only", "older in-flight success must not clear a newer local-only marker");
	context.RpgAuthSession.clearPendingUnsyncedSave({ userId: 17, accountCharacterId: characterId });

	assert.match(bridgeSource, /accountCharacterId/);
	assert.match(bridgeSource, /getCurrentAccountBackendSlotKey/);
	assert.match(bridgeSource, /enqueueBackendSaveSnapshotWrite/);
	assert.match(bridgeSource, /backendSaveWriteQueue/);
	assert.match(mainSource, /hasReadyAccountGameContext\(\)/);
	assert.match(mainSource, /backend-authoritative/);
	assert.match(mainSource, /pre-backend-recovery/);
	assert(mainSource.indexOf("if (backendSnapshot) {") < mainSource.indexOf('source: "account-local-recovery-backend-empty"'));
	assert.match(mainSource, /pending-unsynced-local-retry/);
	assert.match(mainSource, /requestPendingUnsyncedDecision/);
	assert.doesNotMatch(mainSource, /accountBackendSaveQueue/);
	assert.match(mainSource, /enqueueBackendSaveSnapshotWrite/);
	assert.match(mainSource, /function pauseAccountGameRuntime\(\)/);
	assert.match(mainSource, /clearInterval\(accountAutosaveInterval\)/);
	assert.match(mainSource, /clearInterval\(accountMaintenanceInterval\)/);
	assert.match(mainSource, /clearInterval\(activeBuffInterval\)/);
	assert.match(mainSource, /clearInterval\(playTimeRecordInterval\)/);
	assert.match(mainSource, /function resumeAccountGameRuntime\(\)/);
	const beforeUnloadBlock = mainSource.slice(mainSource.indexOf('window.addEventListener("beforeunload"'));
	assert.match(beforeUnloadBlock, /isTransitionInProgress\(\)/);
	assert(beforeUnloadBlock.indexOf("const saved = saveGame()") < beforeUnloadBlock.indexOf("markPendingUnsyncedSave"), "beforeunload must mark pending only after a successful local save");
	assert.match(beforeUnloadBlock, /reason: "beforeunload-local-only"/);
	assert.match(mainSource, /window\.RpgAccountGate\.start\(\)/);
	assert.doesNotMatch(mainSource, /localStorage\.(?:getItem|setItem|removeItem)\("idleRpgSaveV22"/);
	assert.doesNotMatch(clientSource, /deleteAccountCharacterProgress/);

	assert.match(gateSource, /escapeHtml\(character\.name\)/);
	assert.match(gateSource, /characterTarget\.textContent/);
	assert.match(gateSource, /userTarget\.textContent/);
	assert.doesNotMatch(gateSource, />\$\{character\.name\}</);
	assert.match(gateSource, /data-account-action="confirm-delete-character" disabled/);
	assert.match(gateSource, /removeItem\(`\$\{localKey\}\.pre-backend-recovery`\)/);
	assert.match(gateSource, /clearPendingUnsyncedSave/);
	assert.match(gateSource, /pending-use-local/);
	assert.match(gateSource, /pending-use-server/);
	const transitionBlock = gateSource.slice(gateSource.indexOf("async function transitionFromGame"), gateSource.indexOf("async function logoutFromSlots"));
	assert(transitionBlock.indexOf("pauseAccountGameRuntime") < transitionBlock.indexOf("flushAccountGameSave"), "runtime must pause before final save capture");
	assert.match(transitionBlock, /handleGameSessionInvalid\(error\)/);
	const invalidSessionBlock = gateSource.slice(gateSource.indexOf("function handleGameSessionInvalid"), gateSource.indexOf("function getCharacterId"));
	assert.match(invalidSessionBlock, /pendingRuntimeResume = false;[\s\S]+returnToLoginAfterSessionExpiry/);
	assert.match(gateSource, /returnToLoginAfterSessionExpiry/);
	assert.match(gateSource, /retry-session/);
	assert.match(gateSource, /consumeAuthNotice/);
	assert.match(gateSource, /event\.key === "Escape"/);
	assert.match(gateSource, /button:not\(:disabled\).*input:not\(:disabled\)/s);
	const deleteFunctionBlock = gateSource.slice(gateSource.indexOf("async function confirmDeleteCharacter"), gateSource.indexOf("async function handleGateClick"));
	assert.equal((deleteFunctionBlock.match(/deleteAccountCharacter\(/g) || []).length, 1, "character delete must never auto-retry DELETE");
	assert.match(deleteFunctionBlock, /verifyCharacterDeletionAfterError/);
	assert.match(deleteFunctionBlock, /자동으로 다시 삭제하지 않았습니다/);
	const deletionHelperSource = gateSource.slice(gateSource.indexOf("async function verifyCharacterDeletionAfterError"), gateSource.indexOf("async function confirmDeleteCharacter"));
	let deletionVerificationGets = 0;
	const deletionContext = {
		window: {
			RpgGameApi: {
				async listAccountCharacters() {
					deletionVerificationGets += 1;
					return { payload: { slots: [{ accountCharacterId: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" }] } };
				},
			},
		},
		getPayload(response) { return response.payload || {}; },
		normalizeCharacters(payload) { return payload.slots || []; },
		normalizeCharacterOptions() { return [{ code: "weapon_master", name: "검신" }]; },
	};
	vm.runInNewContext(`${deletionHelperSource}\nwindow.verifyCharacterDeletionAfterError = verifyCharacterDeletionAfterError;`, deletionContext);
	const verifiedDeleted = await deletionContext.window.verifyCharacterDeletionAfterError(characterId);
	assert.equal(deletionVerificationGets, 1, "ambiguous DELETE must issue exactly one verification GET");
	assert.equal(verifiedDeleted.deleted, true, "missing UUID after ambiguous DELETE must be treated as deleted");
	const verifiedStillPresent = await deletionContext.window.verifyCharacterDeletionAfterError("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
	assert.equal(deletionVerificationGets, 2, "each ambiguous DELETE decision must issue one and only one verification GET");
	assert.equal(verifiedStillPresent.deleted, false, "existing UUID after ambiguous DELETE must remain a failure");

	const scheduledTimeouts = [];
	let combatPaused = true;
	let combatIntervalsStarted = 0;
	const combatContext = {
		console,
		Date,
		Math,
		window: null,
		fieldEnemyHp: {},
		fieldRespawnEndAt: {},
		zones: [{ maxHp: 100 }],
		currentZoneType: "field",
		currentZoneIndex: 0,
		currentEnemy: { hp: 1 },
		attackInterval: null,
		setTimeout(callback) { scheduledTimeouts.push(callback); return scheduledTimeouts.length; },
		setInterval() { combatIntervalsStarted += 1; return combatIntervalsStarted; },
		clearInterval() {},
		getTotals() { return { aspdMs: 500 }; },
		playerAttack() {},
		updateFullUI() {},
		updateCombatUI() {},
	};
	combatContext.window = combatContext;
	combatContext.isAccountGameRuntimePaused = () => combatPaused;
	vm.runInNewContext(combatSource, combatContext, { filename: "combat-system.js" });
	combatContext.scheduleFieldRespawn(0, 0);
	const firstRespawnCallback = scheduledTimeouts.shift();
	firstRespawnCallback();
	assert.equal(combatContext.currentEnemy.hp, 1, "paused respawn callback mutated the visible enemy");
	assert.equal(combatContext.fieldEnemyHp["0"], 0, "paused respawn callback mutated field HP");
	combatContext.startAutoAttack();
	assert.equal(combatIntervalsStarted, 0, "paused runtime restarted auto attack");
	combatPaused = false;
	const resumedRespawnCallback = scheduledTimeouts.shift();
	resumedRespawnCallback();
	assert.equal(combatContext.currentEnemy.hp, 100, "respawn did not reconcile after runtime resumed");
	assert.equal(combatIntervalsStarted, 1, "auto attack did not restart exactly once after respawn resumed");

	assert.match(css, /grid-template-columns:\s*repeat\(2,/);
	assert.match(css, /@media \(max-width: 700px\)[\s\S]+\.account-slots-grid\s*\{\s*grid-template-columns:\s*1fr/);
	assert.match(css, /:focus-visible/);
	assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);

	console.log("v370 account character gate smoke passed");
	console.log("- UUID character context / slot-index backend key: ok");
	console.log("- session/local token persistence and bearer policy: ok");
	console.log("- backend-authoritative load / displaced-local backup / auth-gated single boot: ok");
	console.log("- serialized DB writes / pending-unsynced recovery / retryable network failure / 401+403 recovery: ok");
	console.log("- escaped account UI / custom delete modal / responsive accessibility: ok");
}

run().catch((error) => {
	console.error(error);
	process.exitCode = 1;
});
