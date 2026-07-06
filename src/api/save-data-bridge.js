(function () {
	"use strict";

	const LOCAL_SAVE_KEY = "idleRpgSaveV22";
	const DEFAULT_SLOT_KEY = "default";
	const DEFAULT_TIMEOUT_MS = 2500;

	function readLocalSaveSnapshot(saveKey) {
		const key = saveKey || LOCAL_SAVE_KEY;
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
		const local = readLocalSaveSnapshot(opts.saveKey || LOCAL_SAVE_KEY);
		if (!local.exists) {
			throw new Error(`${local.key} localStorage 저장 데이터가 없습니다.`);
		}
		if (local.error || !local.snapshot) {
			throw new Error(`localStorage 저장 데이터를 JSON으로 읽을 수 없습니다: ${local.error || "unknown"}`);
		}

		return {
			saveVersion: local.snapshot.saveVersion !== undefined ? Number(local.snapshot.saveVersion) : null,
			clientSaveKey: local.key,
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			snapshot: local.snapshot,
			summary: opts.summary || buildLocalSaveSummary(local.snapshot),
			source: opts.source || "localStorage-manual-push",
			note: opts.note || null,
		};
	}

	async function pushLocalSaveToBackend(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.saveGameSnapshot !== "function") {
			throw new Error("RpgGameApi.saveGameSnapshot을 찾을 수 없습니다.");
		}
		const opts = options || {};
		const payload = buildBackendSavePayload(opts);
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

	async function loadBackendSaveSnapshot(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.loadGameSnapshot !== "function") {
			throw new Error("RpgGameApi.loadGameSnapshot을 찾을 수 없습니다.");
		}
		const opts = options || {};
		const response = await window.RpgGameApi.loadGameSnapshot({
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		console.log("[Upgrade RPG] backend save snapshot loaded", {
			status: response && response.data ? response.data.status : null,
			exists: response && response.data ? response.data.exists : null,
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			summary: response && response.payload ? response.payload.summary : null,
		});
		return response;
	}

	async function checkBackendSaveSnapshotBridge(options) {
		const local = readLocalSaveSnapshot((options || {}).saveKey || LOCAL_SAVE_KEY);
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

	window.UPGRADE_RPG_LOCAL_SAVE_KEY = LOCAL_SAVE_KEY;
	window.readLocalSaveSnapshot = readLocalSaveSnapshot;
	window.buildBackendSavePayload = buildBackendSavePayload;
	window.pushLocalSaveToBackend = pushLocalSaveToBackend;
	window.loadBackendSaveSnapshot = loadBackendSaveSnapshot;
	window.checkBackendSaveSnapshotBridge = checkBackendSaveSnapshotBridge;
})();
