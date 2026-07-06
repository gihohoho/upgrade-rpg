(function () {
	"use strict";

	const SAVE_SYNC_MODE_STORAGE_KEY = "upgradeRpgBackendSaveSyncMode";
	const SAVE_SYNC_STATUS_STORAGE_KEY = "upgradeRpgBackendSaveSyncStatus";
	const DEFAULT_MODE = "manual_dual";
	const DEFAULT_TIMEOUT_MS = 3000;

	let isSyncing = false;

	function nowIso() {
		return new Date().toISOString();
	}

	function readStorage(key) {
		try {
			return window.localStorage ? window.localStorage.getItem(key) : null;
		} catch (error) {
			return null;
		}
	}

	function writeStorage(key, value) {
		try {
			if (window.localStorage) window.localStorage.setItem(key, value);
		} catch (error) {
			// localStorage가 막힌 환경에서도 현재 탭에서는 게임이 계속 진행되어야 합니다.
		}
	}

	function getBackendSaveSyncMode() {
		const mode = readStorage(SAVE_SYNC_MODE_STORAGE_KEY);
		if (mode === "local_only" || mode === "manual_dual") return mode;
		return DEFAULT_MODE;
	}

	function setBackendSaveSyncMode(mode, options) {
		const nextMode = mode === "local_only" ? "local_only" : "manual_dual";
		writeStorage(SAVE_SYNC_MODE_STORAGE_KEY, nextMode);
		const shouldReload = !!(options && options.reload);
		if (typeof addLog === "function") {
			addLog(
				nextMode === "manual_dual"
					? "[저장] 백엔드 이중 저장 모드가 켜졌습니다. 수동 저장 시 DB에도 저장을 시도합니다."
					: "[저장] 로컬 저장 전용 모드로 전환했습니다.",
				true,
			);
		}
		if (shouldReload) window.location.reload();
		return getBackendSaveSyncPolicy();
	}

	function enableBackendSaveDualWrite(options) {
		return setBackendSaveSyncMode("manual_dual", options);
	}

	function disableBackendSaveDualWrite(options) {
		return setBackendSaveSyncMode("local_only", options);
	}

	function getBackendSaveSyncStatus() {
		const raw = readStorage(SAVE_SYNC_STATUS_STORAGE_KEY);
		if (!raw) {
			return {
				ok: null,
				state: "never_synced",
				updatedAt: null,
				mode: getBackendSaveSyncMode(),
				error: null,
				summary: null,
			};
		}
		try {
			return JSON.parse(raw);
		} catch (error) {
			return {
				ok: false,
				state: "invalid_status_json",
				updatedAt: nowIso(),
				mode: getBackendSaveSyncMode(),
				error: error.message || String(error),
				summary: null,
			};
		}
	}

	function setBackendSaveSyncStatus(status) {
		const nextStatus = {
			ok: !!status.ok,
			state: status.state || (status.ok ? "synced" : "failed"),
			updatedAt: nowIso(),
			mode: getBackendSaveSyncMode(),
			reason: status.reason || null,
			slotKey: status.slotKey || "default",
			saveVersion: status.saveVersion !== undefined ? status.saveVersion : null,
			error: status.error || null,
			summary: status.summary || null,
			responseData: status.responseData || null,
		};
		writeStorage(SAVE_SYNC_STATUS_STORAGE_KEY, JSON.stringify(nextStatus));
		window.__upgradeRpgBackendSaveSyncStatus = nextStatus;
		return nextStatus;
	}

	function getBackendSaveSyncPolicy() {
		const mode = getBackendSaveSyncMode();
		return {
			mode,
			manualDualWriteEnabled: mode === "manual_dual",
			fallbackToLocalStorage: true,
			localSaveKey: window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22",
			defaultSlotKey: "default",
			defaultTimeoutMs: DEFAULT_TIMEOUT_MS,
			status: getBackendSaveSyncStatus(),
		};
	}

	function shouldSyncBackendOnManualSave() {
		return getBackendSaveSyncMode() === "manual_dual";
	}

	function logSaveSync(message, isImportant) {
		if (typeof addLog === "function") {
			addLog(message, !!isImportant);
		} else {
			console.log(message);
		}
	}

	async function syncLatestLocalSaveToBackend(options) {
		const opts = options || {};
		if (isSyncing) {
			const status = setBackendSaveSyncStatus({
				ok: false,
				state: "skipped_already_syncing",
				reason: opts.reason || "manual-save",
				error: "이미 백엔드 저장 동기화가 진행 중입니다.",
			});
			return { skipped: true, status };
		}
		if (!window.pushLocalSaveToBackend || typeof window.pushLocalSaveToBackend !== "function") {
			const status = setBackendSaveSyncStatus({
				ok: false,
				state: "bridge_missing",
				reason: opts.reason || "manual-save",
				error: "pushLocalSaveToBackend 함수를 찾을 수 없습니다.",
			});
			if (opts.log !== false) logSaveSync("[저장] 백엔드 저장 브릿지를 찾을 수 없어 DB 저장을 건너뛰었습니다.");
			return { skipped: true, status };
		}

		isSyncing = true;
		try {
			const response = await window.pushLocalSaveToBackend({
				slotKey: opts.slotKey || "default",
				timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
				source: opts.source || "manual-save-dual-write",
				note: opts.note || "수동 저장 버튼에서 localStorage 저장 직후 백엔드 DB에도 저장했습니다.",
			});
			const payload = response && response.payload ? response.payload : {};
			const status = setBackendSaveSyncStatus({
				ok: true,
				state: "synced",
				reason: opts.reason || "manual-save",
				slotKey: payload.slotKey || opts.slotKey || "default",
				saveVersion: payload.saveVersion,
				summary: payload.summary || null,
				responseData: response && response.data ? response.data : null,
			});
			if (opts.log !== false) logSaveSync("[저장] 백엔드 DB에도 세이브 스냅샷을 저장했습니다.", true);
			return { ok: true, response, status };
		} catch (error) {
			const status = setBackendSaveSyncStatus({
				ok: false,
				state: "failed_fallback_to_local_storage",
				reason: opts.reason || "manual-save",
				error: error && error.message ? error.message : String(error),
			});
			if (opts.log !== false) {
				logSaveSync("[저장] 로컬 저장은 완료됐지만 백엔드 DB 저장은 실패했습니다. FastAPI 서버와 DB 상태를 확인하세요.");
			}
			console.warn("[Upgrade RPG] backend save sync failed", error);
			return { ok: false, error, status };
		} finally {
			isSyncing = false;
		}
	}

	async function requestBackendSaveAfterManualSave(options) {
		const opts = options || {};
		if (!shouldSyncBackendOnManualSave()) {
			const status = setBackendSaveSyncStatus({
				ok: true,
				state: "skipped_local_only_mode",
				reason: opts.reason || "manual-save",
			});
			return { skipped: true, status };
		}
		return syncLatestLocalSaveToBackend({
			...opts,
			reason: opts.reason || "manual-save",
			source: opts.source || "manual-save-dual-write",
		});
	}

	async function checkBackendSaveSyncPolicy(options) {
		const bridge = window.checkBackendSaveSnapshotBridge
			? await window.checkBackendSaveSnapshotBridge(options || {})
			: { ok: false, error: "checkBackendSaveSnapshotBridge 함수를 찾을 수 없습니다." };
		const result = {
			ok: !!(bridge && bridge.apiClientReady),
			policy: getBackendSaveSyncPolicy(),
			bridge,
		};
		console.log("[Upgrade RPG] backend save sync policy check", result);
		return result;
	}

	window.BACKEND_SAVE_SYNC_MODE_STORAGE_KEY = SAVE_SYNC_MODE_STORAGE_KEY;
	window.BACKEND_SAVE_SYNC_STATUS_STORAGE_KEY = SAVE_SYNC_STATUS_STORAGE_KEY;
	window.getBackendSaveSyncMode = getBackendSaveSyncMode;
	window.getBackendSaveSyncPolicy = getBackendSaveSyncPolicy;
	window.getBackendSaveSyncStatus = getBackendSaveSyncStatus;
	window.enableBackendSaveDualWrite = enableBackendSaveDualWrite;
	window.disableBackendSaveDualWrite = disableBackendSaveDualWrite;
	window.syncLatestLocalSaveToBackend = syncLatestLocalSaveToBackend;
	window.requestBackendSaveAfterManualSave = requestBackendSaveAfterManualSave;
	window.checkBackendSaveSyncPolicy = checkBackendSaveSyncPolicy;
})();
