(function () {
	"use strict";

	const STORAGE_KEY = "upgradeRpgUseBackendMasterData";
	const STATUS_KEY = "backendMasterDataRuntimeStatus";

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
			// localStorage 사용이 막힌 환경에서는 현재 세션 상태만 사용합니다.
		}
	}

	function removeStorage(key) {
		try {
			if (window.localStorage) window.localStorage.removeItem(key);
		} catch (error) {
			// localStorage 사용이 막힌 환경에서는 무시합니다.
		}
	}

	function isBackendMasterDataModeEnabled() {
		return readStorage(STORAGE_KEY) === "1" || window.__UPGRADE_RPG_USE_BACKEND_MASTER_DATA__ === true;
	}

	function cloneJson(value) {
		if (value === undefined) return undefined;
		try {
			return JSON.parse(JSON.stringify(value));
		} catch (error) {
			return value;
		}
	}

	function replaceObject(target, source) {
		if (!target || typeof target !== "object" || Array.isArray(target)) return false;
		Object.keys(target).forEach((key) => delete target[key]);
		Object.assign(target, cloneJson(source || {}));
		return true;
	}

	function replaceArray(target, source) {
		if (!Array.isArray(target)) return false;
		target.splice(0, target.length, ...cloneJson(Array.isArray(source) ? source : []));
		return true;
	}

	function setStatus(nextStatus) {
		const status = {
			modeEnabled: isBackendMasterDataModeEnabled(),
			updatedAt: new Date().toISOString(),
			...(window[STATUS_KEY] || {}),
			...(nextStatus || {}),
		};
		window[STATUS_KEY] = status;
		return status;
	}

	function getBackendMasterDataRuntimeStatus() {
		return window[STATUS_KEY] || setStatus({ state: "idle" });
	}

	function assertAdapterReady() {
		if (!window.RpgMasterDataAdapter || typeof window.RpgMasterDataAdapter.loadAdaptedMasterDataFromApi !== "function") {
			throw new Error("RpgMasterDataAdapter가 준비되지 않았습니다. master-data-adapter.js 로딩 순서를 확인하세요.");
		}
	}

	function applyLegacyMasterData(legacyData) {
		if (!legacyData || typeof legacyData !== "object") {
			throw new Error("적용할 legacy master-data가 없습니다.");
		}

		const applied = {
			characterMasterData: false,
			skillMasterData: false,
			bossList: false,
			specialBossList: false,
			zones: false,
		};

		// 이 파일은 index.html에서 모든 기존 데이터 파일이 로드된 뒤 실행됩니다.
		// 기존 파일의 top-level const는 재할당할 수 없으므로, 객체/배열 내부만 교체합니다.
		if (typeof characterMasterData !== "undefined") {
			applied.characterMasterData = replaceObject(characterMasterData, legacyData.characterMasterData);
		}
		if (typeof skillMasterData !== "undefined") {
			applied.skillMasterData = replaceObject(skillMasterData, legacyData.skillMasterData);
		}
		if (typeof bossList !== "undefined") {
			applied.bossList = replaceArray(bossList, legacyData.bossList);
		}
		if (typeof specialBossList !== "undefined") {
			applied.specialBossList = replaceArray(specialBossList, legacyData.specialBossList);
		}
		if (typeof zones !== "undefined") {
			applied.zones = replaceArray(zones, legacyData.fieldZones);
		}

		const missing = Object.entries(applied).filter(([, ok]) => !ok).map(([key]) => key);
		const status = setStatus({
			state: missing.length ? "applied_with_missing_targets" : "applied",
			applied,
			missing,
			counts: legacyData.counts || {},
			defaultCharacterId: legacyData.defaultCharacterId || null,
			includeAssets: true,
		});

		window.backendAppliedMasterData = legacyData;
		return status;
	}

	async function loadAndApplyBackendMasterData(options) {
		assertAdapterReady();
		const includeAssets = options && options.includeAssets !== undefined ? !!options.includeAssets : true;
		setStatus({ state: "loading", includeAssets });
		const snapshot = await window.RpgMasterDataAdapter.loadAdaptedMasterDataFromApi({ includeAssets });
		if (!snapshot.validation || snapshot.validation.ok !== true) {
			const failures = snapshot.validation ? snapshot.validation.failures : [];
			throw new Error(`master-data adapter 검증 실패: ${failures.join(", ")}`);
		}
		const status = applyLegacyMasterData(snapshot.legacyData);
		status.snapshot = snapshot;
		return status;
	}

	async function applyBackendMasterDataBeforeGameStart() {
		if (!isBackendMasterDataModeEnabled()) {
			return setStatus({ state: "disabled" });
		}

		try {
			const status = await loadAndApplyBackendMasterData({ includeAssets: true });
			console.log("[Upgrade RPG] backend master-data runtime mode applied", {
				counts: status.counts,
				applied: status.applied,
			});
			return status;
		} catch (error) {
			console.warn("[Upgrade RPG] backend master-data runtime mode failed. 기존 JS 데이터로 계속 실행합니다.", error);
			return setStatus({ state: "failed_fallback_to_static_js", errorMessage: error && error.message ? error.message : String(error) });
		}
	}

	function setBackendMasterDataMode(enabled, options) {
		const shouldEnable = !!enabled;
		if (shouldEnable) {
			writeStorage(STORAGE_KEY, "1");
			window.__UPGRADE_RPG_USE_BACKEND_MASTER_DATA__ = true;
		} else {
			removeStorage(STORAGE_KEY);
			window.__UPGRADE_RPG_USE_BACKEND_MASTER_DATA__ = false;
		}

		const status = setStatus({ state: shouldEnable ? "enabled_reload_required" : "disabled_reload_required" });
		const shouldReload = !options || options.reload !== false;
		if (shouldReload && window.location && typeof window.location.reload === "function") {
			window.location.reload();
		}
		return status;
	}

	function enableBackendMasterDataMode(options) {
		return setBackendMasterDataMode(true, options || {});
	}

	function disableBackendMasterDataMode(options) {
		return setBackendMasterDataMode(false, options || {});
	}

	async function checkBackendMasterDataRuntimeMode() {
		const status = getBackendMasterDataRuntimeStatus();
		const summary = {
			modeEnabled: isBackendMasterDataModeEnabled(),
			state: status.state,
			counts: status.counts || null,
			applied: status.applied || null,
			missing: status.missing || [],
			errorMessage: status.errorMessage || null,
		};
		if (summary.modeEnabled && status.state === "disabled") {
			summary.note = "모드는 켜져 있지만 아직 적용 전입니다. 페이지를 새로고침하세요.";
		}
		console.log("[Upgrade RPG] backend master-data runtime mode status", summary);
		return summary;
	}

	function wrapWindowOnload() {
		const originalOnload = window.onload;
		if (originalOnload && originalOnload.__backendMasterDataWrapped) return;

		const wrappedOnload = async function backendMasterDataWrappedOnload(event) {
			await applyBackendMasterDataBeforeGameStart();
			if (typeof originalOnload === "function") return originalOnload.call(this, event);
			return undefined;
		};
		wrappedOnload.__backendMasterDataWrapped = true;
		window.onload = wrappedOnload;
	}

	window.RpgBackendMasterDataRuntime = {
		STORAGE_KEY,
		isBackendMasterDataModeEnabled,
		setBackendMasterDataMode,
		enableBackendMasterDataMode,
		disableBackendMasterDataMode,
		getBackendMasterDataRuntimeStatus,
		checkBackendMasterDataRuntimeMode,
		applyLegacyMasterData,
		loadAndApplyBackendMasterData,
		applyBackendMasterDataBeforeGameStart,
	};

	window.enableBackendMasterDataMode = enableBackendMasterDataMode;
	window.disableBackendMasterDataMode = disableBackendMasterDataMode;
	window.checkBackendMasterDataRuntimeMode = checkBackendMasterDataRuntimeMode;
	window.getBackendMasterDataRuntimeStatus = getBackendMasterDataRuntimeStatus;

	wrapWindowOnload();
	setStatus({ state: isBackendMasterDataModeEnabled() ? "enabled_waiting_for_page_load" : "disabled" });
})();
