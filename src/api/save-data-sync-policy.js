(function () {
	"use strict";

	const SAVE_SYNC_MODE_STORAGE_KEY = "upgradeRpgBackendSaveSyncMode";
	const SAVE_SYNC_STATUS_STORAGE_KEY = "upgradeRpgBackendSaveSyncStatus";
	const SAVE_SYNC_MODE_INIT_STORAGE_KEY = "upgradeRpgBackendSaveSyncModeInitializedV102";
	const DEFAULT_MODE = "manual_dual";
	const DEFAULT_TIMEOUT_MS = 3000;

	let isSyncing = false;

	function getActiveLocalSaveKey() {
		return typeof window.getCurrentAccountLocalSaveKey === "function"
			? window.getCurrentAccountLocalSaveKey()
			: (window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22");
	}

	function getActiveBackendSlotKey() {
		return typeof window.getCurrentAccountBackendSlotKey === "function"
			? window.getCurrentAccountBackendSlotKey()
			: (window.UPGRADE_RPG_BACKEND_SLOT_KEY || "default");
	}

	function getActiveAccountCharacterId() {
		return typeof window.getCurrentAccountCharacterId === "function" ? window.getCurrentAccountCharacterId() : null;
	}

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

	function removeStorage(key) {
		try {
			if (window.localStorage) window.localStorage.removeItem(key);
		} catch (error) {
			// localStorage가 막힌 환경에서는 기본값으로만 동작합니다.
		}
	}

	function isLocalDevelopment() {
		try {
			const protocol = window.location && window.location.protocol;
			const host = window.location && window.location.hostname;
			return protocol === "file:" || host === "localhost" || host === "127.0.0.1";
		} catch (error) {
			return true;
		}
	}

	function normalizeStoredBackendSaveSyncMode() {
		const storedMode = readStorage(SAVE_SYNC_MODE_STORAGE_KEY);
		const initialized = readStorage(SAVE_SYNC_MODE_INIT_STORAGE_KEY);
		if (initialized !== "1" && storedMode === "local_only" && isLocalDevelopment()) {
			// v101 테스트 중 local 버튼을 눌러 저장된 값 때문에 다음 접속마다 local로 시작하는 문제를 방지합니다.
			// v102 최초 적용 시 한 번만 기본값인 manual_dual로 되돌리고, 이후 사용자가 local을 누르면 그대로 유지됩니다.
			writeStorage(SAVE_SYNC_MODE_STORAGE_KEY, DEFAULT_MODE);
			writeStorage(SAVE_SYNC_MODE_INIT_STORAGE_KEY, "1");
			return DEFAULT_MODE;
		}
		if (initialized !== "1") writeStorage(SAVE_SYNC_MODE_INIT_STORAGE_KEY, "1");
		return storedMode;
	}

	function dispatchBackendSaveSyncEvent(name, detail) {
		try {
			window.dispatchEvent(new CustomEvent(`upgrade-rpg:backend-save-sync-${name}`, { detail: detail || {} }));
		} catch (error) {
			// CustomEvent를 지원하지 않는 환경에서는 배지 자동 새로고침으로 보정합니다.
		}
	}

	function getBackendSaveSyncMode() {
		const mode = normalizeStoredBackendSaveSyncMode();
		if (mode === "local_only" || mode === "manual_dual") return mode;
		return DEFAULT_MODE;
	}

	function setBackendSaveSyncMode(mode, options) {
		const nextMode = mode === "local_only" ? "local_only" : "manual_dual";
		writeStorage(SAVE_SYNC_MODE_STORAGE_KEY, nextMode);
		writeStorage(SAVE_SYNC_MODE_INIT_STORAGE_KEY, "1");
		const modeStatus = setBackendSaveSyncStatus({
			ok: null,
			state: nextMode === "manual_dual" ? "ready_manual_dual" : "local_only_mode",
			reason: "mode-change",
		});
		dispatchBackendSaveSyncEvent("mode", { mode: nextMode, status: modeStatus });
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
			ok: status.ok === undefined || status.ok === null ? null : !!status.ok,
			state: status.state || (status.ok ? "synced" : "failed"),
			updatedAt: nowIso(),
			mode: getBackendSaveSyncMode(),
			reason: status.reason || null,
			slotKey: status.slotKey || getActiveBackendSlotKey(),
			saveVersion: status.saveVersion !== undefined ? status.saveVersion : null,
			error: status.error || null,
			summary: status.summary || null,
			responseData: status.responseData || null,
		};
		writeStorage(SAVE_SYNC_STATUS_STORAGE_KEY, JSON.stringify(nextStatus));
		window.__upgradeRpgBackendSaveSyncStatus = nextStatus;
		dispatchBackendSaveSyncEvent("status", nextStatus);
		return nextStatus;
	}

	function getBackendSaveSyncPolicy() {
		const mode = getBackendSaveSyncMode();
		return {
			mode,
			manualDualWriteEnabled: mode === "manual_dual",
			fallbackToLocalStorage: true,
			localSaveKey: getActiveLocalSaveKey(),
			defaultSlotKey: getActiveBackendSlotKey(),
			accountCharacterId: getActiveAccountCharacterId(),
			defaultTimeoutMs: DEFAULT_TIMEOUT_MS,
			status: getBackendSaveSyncStatus(),
		};
	}

	function shouldSyncBackendOnManualSave() {
		return getBackendSaveSyncMode() === "manual_dual";
	}

	function resetBackendSaveSyncModeToDefault() {
		removeStorage(SAVE_SYNC_MODE_STORAGE_KEY);
		removeStorage(SAVE_SYNC_MODE_INIT_STORAGE_KEY);
		const mode = getBackendSaveSyncMode();
		const status = setBackendSaveSyncStatus({
			ok: null,
			state: "ready_manual_dual",
			reason: "reset-default-mode",
		});
		dispatchBackendSaveSyncEvent("mode", { mode, status });
		return getBackendSaveSyncPolicy();
	}

	function recordBackendSaveManualSaveCooldown(options) {
		const opts = options || {};
		const remainSeconds = opts.remainSeconds !== undefined ? opts.remainSeconds : null;
		return setBackendSaveSyncStatus({
			ok: null,
			state: "skipped_manual_save_cooldown",
			reason: opts.reason || "manual-save-cooldown",
			error: remainSeconds !== null ? `수동 저장 쿨타임입니다. ${remainSeconds}초 후 다시 시도할 수 있습니다.` : "수동 저장 쿨타임입니다.",
		});
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
			const requestOptions = {
				saveKey: opts.saveKey || getActiveLocalSaveKey(),
				slotKey: opts.slotKey || getActiveBackendSlotKey(),
				accountCharacterId: opts.accountCharacterId || getActiveAccountCharacterId(),
				timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
				verifyTimeoutMs: opts.verifyTimeoutMs !== undefined ? opts.verifyTimeoutMs : opts.timeoutMs,
				source: opts.source || "manual-save-dual-write",
				note: opts.note || "수동 저장 버튼에서 localStorage 저장 직후 백엔드 DB에도 저장했습니다.",
				log: opts.log,
			};
			const shouldVerify = opts.verify !== false && typeof window.pushLocalSaveToBackendAndVerify === "function";
			const syncResult = shouldVerify
				? await window.pushLocalSaveToBackendAndVerify(requestOptions)
				: { ok: true, saveResponse: await window.pushLocalSaveToBackend(requestOptions), verify: null };
			const response = syncResult.saveResponse || syncResult.response;
			const payload = response && response.payload ? response.payload : {};
			const verify = syncResult.verify || null;
			const verified = !!(verify && verify.ok);
			const integrity = payload.integrity || (verify && verify.backend ? verify.backend.integrity : null);
			const status = setBackendSaveSyncStatus({
				ok: shouldVerify ? verified : true,
				state: shouldVerify ? (verified ? "synced_verified" : "saved_verify_failed") : "synced",
				reason: opts.reason || "manual-save",
				slotKey: payload.slotKey || opts.slotKey || getActiveBackendSlotKey(),
				saveVersion: payload.saveVersion,
				summary: payload.summary || null,
				responseData: {
					...(response && response.data ? response.data : {}),
					verified: shouldVerify ? verified : null,
					diffCount: verify ? verify.diffCount : null,
					integrity,
				},
				error: shouldVerify && !verified && verify ? verify.error : null,
			});
			if (opts.log !== false) {
				logSaveSync(
					shouldVerify
						? (verified ? "[저장] 백엔드 DB 저장 후 localStorage와 동일한 것까지 확인했습니다." : "[저장] DB 저장은 완료됐지만 검증이 실패했습니다. SAVE DATA preview로 차이를 확인하세요.")
						: "[저장] 백엔드 DB에도 세이브 스냅샷을 저장했습니다.",
					verified || !shouldVerify,
				);
			}
			return { ok: !shouldVerify || verified, response, verify, status };
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
	window.BACKEND_SAVE_SYNC_MODE_INIT_STORAGE_KEY = SAVE_SYNC_MODE_INIT_STORAGE_KEY;
	window.getBackendSaveSyncMode = getBackendSaveSyncMode;
	window.getBackendSaveSyncPolicy = getBackendSaveSyncPolicy;
	window.getBackendSaveSyncStatus = getBackendSaveSyncStatus;
	window.enableBackendSaveDualWrite = enableBackendSaveDualWrite;
	window.disableBackendSaveDualWrite = disableBackendSaveDualWrite;
	window.resetBackendSaveSyncModeToDefault = resetBackendSaveSyncModeToDefault;
	window.recordBackendSaveManualSaveCooldown = recordBackendSaveManualSaveCooldown;
	window.syncLatestLocalSaveToBackend = syncLatestLocalSaveToBackend;
	window.requestBackendSaveAfterManualSave = requestBackendSaveAfterManualSave;
	window.checkBackendSaveSyncPolicy = checkBackendSaveSyncPolicy;
})();
