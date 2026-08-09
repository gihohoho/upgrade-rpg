(function () {
	"use strict";

	const LEGACY_LOCAL_SAVE_KEY = "idleRpgSaveV22";
	const LEGACY_DEFAULT_SLOT_KEY = "default";
	const DEFAULT_TIMEOUT_MS = 2500;
	let backendSaveWriteQueue = Promise.resolve();
	let queuedBackendSaveWrites = 0;

	function getCurrentLocalSaveKey(options) {
		const opts = options || {};
		if (opts.saveKey) return String(opts.saveKey);
		return typeof window.getCurrentAccountLocalSaveKey === "function"
			? window.getCurrentAccountLocalSaveKey()
			: LEGACY_LOCAL_SAVE_KEY;
	}

	function getCurrentBackendSlotKey(options) {
		const opts = options || {};
		if (opts.slotKey) return String(opts.slotKey);
		return typeof window.getCurrentAccountBackendSlotKey === "function"
			? window.getCurrentAccountBackendSlotKey()
			: LEGACY_DEFAULT_SLOT_KEY;
	}

	function getCurrentCharacterId(options) {
		const opts = options || {};
		if (opts.accountCharacterId) return String(opts.accountCharacterId).trim().toLowerCase();
		return typeof window.getCurrentAccountCharacterId === "function"
			? window.getCurrentAccountCharacterId()
			: null;
	}

	function readLocalSaveSnapshot(saveKey) {
		const key = saveKey || getCurrentLocalSaveKey();
		if (!window.localStorage) {
			return { key, exists: false, raw: null, snapshot: null, error: "localStorage를 사용할 수 없습니다." };
		}

		const raw = window.localStorage.getItem(key);
		if (!raw) return { key, exists: false, raw: null, snapshot: null, error: null };

		try {
			return { key, exists: true, raw, snapshot: JSON.parse(raw), error: null };
		} catch (error) {
			return { key, exists: true, raw, snapshot: null, error: error.message || String(error) };
		}
	}

	function countFilledItems(items) {
		if (!Array.isArray(items)) return 0;
		return items.filter(Boolean).length;
	}

	function buildLocalSaveSummary(snapshot) {
		const player = snapshot && snapshot.player && typeof snapshot.player === "object" ? snapshot.player : {};
		return {
			saveVersion: snapshot && snapshot.saveVersion !== undefined ? snapshot.saveVersion : null,
			gold: player.gold !== undefined ? player.gold : null,
			level: player.level !== undefined ? player.level : null,
			currentCharacterId: snapshot && snapshot.currentCharacterId ? snapshot.currentCharacterId : player.currentCharacterId || null,
			currentZoneIndex: snapshot && snapshot.currentZoneIndex !== undefined ? snapshot.currentZoneIndex : null,
			currentZoneType: snapshot && snapshot.currentZoneType ? snapshot.currentZoneType : null,
			inventoryItems: countFilledItems(player.inventory),
			storageItems: countFilledItems(player.storage),
			trashItems: countFilledItems(player.trash),
			mailboxItems: countFilledItems(player.mailbox),
			createdAt: new Date().toISOString(),
		};
	}

	function buildBackendSavePayload(options) {
		const opts = options || {};
		const local = readLocalSaveSnapshot(getCurrentLocalSaveKey(opts));
		if (!local.exists) {
			throw new Error(`${local.key} localStorage 저장 데이터가 없습니다.`);
		}
		if (local.error || !local.snapshot) {
			throw new Error(`localStorage 저장 데이터를 JSON으로 읽을 수 없습니다: ${local.error || "unknown"}`);
		}

		const accountCharacterId = getCurrentCharacterId(opts);
		const payload = {
			saveVersion: local.snapshot.saveVersion !== undefined ? Number(local.snapshot.saveVersion) : null,
			clientSaveKey: local.key,
			slotKey: getCurrentBackendSlotKey(opts),
			snapshot: local.snapshot,
			summary: opts.summary || buildLocalSaveSummary(local.snapshot),
			source: opts.source || "localStorage-manual-push",
			note: opts.note || null,
		};
		if (accountCharacterId) payload.accountCharacterId = accountCharacterId;
		return payload;
	}

	async function performBackendSaveWrite(payload, options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.saveGameSnapshot !== "function") {
			throw new Error("RpgGameApi.saveGameSnapshot을 찾을 수 없습니다.");
		}
		const opts = options || {};
		const response = await window.RpgGameApi.saveGameSnapshot(payload, {
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		console.log("[Upgrade RPG] local save pushed to backend", {
			status: response && response.data ? response.data.status : null,
			slotKey: payload.slotKey,
			saveVersion: payload.saveVersion,
			summary: payload.summary,
		});
		return response;
	}

	function pushLocalSaveToBackend(options) {
		const opts = options || {};
		const authSession = window.RpgAuthSession;
		const currentUser = authSession && typeof authSession.getCurrentUser === "function" ? authSession.getCurrentUser() : null;
		const currentCharacter = authSession && typeof authSession.getCurrentCharacter === "function" ? authSession.getCurrentCharacter() : null;
		const frozenOptions = {
			...opts,
			saveKey: getCurrentLocalSaveKey(opts),
			slotKey: getCurrentBackendSlotKey(opts),
			accountCharacterId: getCurrentCharacterId(opts),
			userId: opts.userId !== undefined ? opts.userId : (currentUser && (currentUser.userId || currentUser.id)),
			characterName: opts.characterName || (currentCharacter && currentCharacter.name) || "",
		};
		const pendingAtEnqueue = authSession && typeof authSession.getPendingUnsyncedSave === "function"
			? authSession.getPendingUnsyncedSave(frozenOptions)
			: null;
		const pendingTokenAtEnqueue = pendingAtEnqueue && (pendingAtEnqueue.markerId || pendingAtEnqueue.markedAt);
		const payload = buildBackendSavePayload(frozenOptions);
		queuedBackendSaveWrites += 1;
		const queuedWrite = backendSaveWriteQueue
			.catch(() => undefined)
			.then(() => performBackendSaveWrite(payload, frozenOptions));
		const trackedWrite = queuedWrite.then((response) => {
			if (pendingTokenAtEnqueue && authSession && typeof authSession.getPendingUnsyncedSave === "function" && typeof authSession.clearPendingUnsyncedSave === "function") {
				const pendingNow = authSession.getPendingUnsyncedSave(frozenOptions);
				const pendingTokenNow = pendingNow && (pendingNow.markerId || pendingNow.markedAt);
				if (pendingTokenNow === pendingTokenAtEnqueue) authSession.clearPendingUnsyncedSave(frozenOptions);
			}
			return response;
		}, (error) => {
			if (authSession && typeof authSession.markPendingUnsyncedSave === "function") {
				authSession.markPendingUnsyncedSave({
					...frozenOptions,
					status: Number(error && error.status) || null,
					reason: frozenOptions.source || "backend-save-failed",
				});
			}
			throw error;
		});
		backendSaveWriteQueue = trackedWrite;
		return trackedWrite.finally(() => {
			queuedBackendSaveWrites = Math.max(0, queuedBackendSaveWrites - 1);
		});
	}

	function getBackendSaveWriteQueueState() {
		return { queuedWrites: queuedBackendSaveWrites, idle: queuedBackendSaveWrites === 0 };
	}

	async function loadBackendSaveSnapshot(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.loadGameSnapshot !== "function") {
			throw new Error("RpgGameApi.loadGameSnapshot을 찾을 수 없습니다.");
		}
		const opts = options || {};
		const slotKey = getCurrentBackendSlotKey(opts);
		const accountCharacterId = getCurrentCharacterId(opts);
		const response = await window.RpgGameApi.loadGameSnapshot({
			slotKey,
			accountCharacterId,
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		console.log("[Upgrade RPG] backend save snapshot loaded", {
			status: response && response.data ? response.data.status : null,
			exists: response && response.data ? response.data.exists : null,
			slotKey,
			accountCharacterId,
			summary: response && response.payload ? response.payload.summary : null,
		});
		return response;
	}

	async function checkBackendSaveSnapshotBridge(options) {
		const local = readLocalSaveSnapshot(getCurrentLocalSaveKey(options));
		const result = {
			ok: false,
			localSaveKey: local.key,
			localExists: local.exists,
			localError: local.error,
			canBuildPayload: false,
			apiClientReady: !!(window.RpgGameApi && window.RpgGameApi.saveGameSnapshot && window.RpgGameApi.loadGameSnapshot),
			summary: null,
		};
		if (local.exists && local.snapshot && !local.error) {
			result.canBuildPayload = true;
			result.summary = buildLocalSaveSummary(local.snapshot);
		}
		result.ok = result.apiClientReady && result.canBuildPayload;
		console.log("[Upgrade RPG] backend save snapshot bridge check", result);
		return result;
	}

	try {
		Object.defineProperty(window, "UPGRADE_RPG_LOCAL_SAVE_KEY", { configurable: true, get: getCurrentLocalSaveKey });
		Object.defineProperty(window, "UPGRADE_RPG_BACKEND_SLOT_KEY", { configurable: true, get: getCurrentBackendSlotKey });
	} catch (error) {
		window.UPGRADE_RPG_LOCAL_SAVE_KEY = getCurrentLocalSaveKey();
		window.UPGRADE_RPG_BACKEND_SLOT_KEY = getCurrentBackendSlotKey();
	}
	window.LEGACY_LOCAL_SAVE_KEY = LEGACY_LOCAL_SAVE_KEY;
	window.getActiveSaveDataLocalKey = getCurrentLocalSaveKey;
	window.getActiveSaveDataBackendSlotKey = getCurrentBackendSlotKey;
	window.getActiveSaveDataAccountCharacterId = getCurrentCharacterId;
	window.readLocalSaveSnapshot = readLocalSaveSnapshot;
	window.buildBackendSavePayload = buildBackendSavePayload;
	window.pushLocalSaveToBackend = pushLocalSaveToBackend;
	window.enqueueBackendSaveSnapshotWrite = pushLocalSaveToBackend;
	window.getBackendSaveWriteQueueState = getBackendSaveWriteQueueState;
	window.loadBackendSaveSnapshot = loadBackendSaveSnapshot;
	window.checkBackendSaveSnapshotBridge = checkBackendSaveSnapshotBridge;
})();
