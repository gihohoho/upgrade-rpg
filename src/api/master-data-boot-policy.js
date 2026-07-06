(function () {
	"use strict";

	const BOOT_MODE_STORAGE_KEY = "upgradeRpgMasterDataBootMode";
	const INCLUDE_ASSETS_STORAGE_KEY = "upgradeRpgBackendMasterDataIncludeAssets";
	const TIMEOUT_STORAGE_KEY = "upgradeRpgBackendMasterDataTimeoutMs";
	const LEGACY_ENABLED_STORAGE_KEY = "upgradeRpgUseBackendMasterData";

	const BOOT_MODES = {
		STATIC: "static",
		AUTO: "auto",
		BACKEND: "backend",
		REQUIRED: "required",
	};

	const DEFAULT_BOOT_MODE = BOOT_MODES.AUTO;
	const DEFAULT_TIMEOUT_MS = 1500;
	const DEFAULT_INCLUDE_ASSETS = false;

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
			// localStorage 사용이 막힌 환경에서는 현재 창 상태만 사용합니다.
		}
	}

	function removeStorage(key) {
		try {
			if (window.localStorage) window.localStorage.removeItem(key);
		} catch (error) {
			// localStorage 사용이 막힌 환경에서는 무시합니다.
		}
	}

	function normalizeBootMode(value) {
		const mode = String(value || "").trim().toLowerCase();
		if (Object.values(BOOT_MODES).includes(mode)) return mode;
		if (mode === "on" || mode === "enabled" || mode === "1") return BOOT_MODES.BACKEND;
		if (mode === "off" || mode === "disabled" || mode === "0") return BOOT_MODES.STATIC;
		return DEFAULT_BOOT_MODE;
	}

	function getStoredBootMode() {
		if (window.__UPGRADE_RPG_MASTER_DATA_BOOT_MODE__) {
			return normalizeBootMode(window.__UPGRADE_RPG_MASTER_DATA_BOOT_MODE__);
		}

		const modernMode = readStorage(BOOT_MODE_STORAGE_KEY);
		if (modernMode) return normalizeBootMode(modernMode);

		// v089까지 쓰던 ON/OFF 키와 호환합니다.
		if (readStorage(LEGACY_ENABLED_STORAGE_KEY) === "1" || window.__UPGRADE_RPG_USE_BACKEND_MASTER_DATA__ === true) {
			return BOOT_MODES.BACKEND;
		}

		return DEFAULT_BOOT_MODE;
	}

	function getStoredIncludeAssets() {
		if (window.__UPGRADE_RPG_BACKEND_MASTER_DATA_INCLUDE_ASSETS__ !== undefined) {
			return !!window.__UPGRADE_RPG_BACKEND_MASTER_DATA_INCLUDE_ASSETS__;
		}
		const stored = readStorage(INCLUDE_ASSETS_STORAGE_KEY);
		if (stored === "1") return true;
		if (stored === "0") return false;
		return DEFAULT_INCLUDE_ASSETS;
	}

	function getStoredTimeoutMs() {
		const fromWindow = Number(window.__UPGRADE_RPG_BACKEND_MASTER_DATA_TIMEOUT_MS__);
		if (Number.isFinite(fromWindow) && fromWindow > 0) return fromWindow;
		const fromStorage = Number(readStorage(TIMEOUT_STORAGE_KEY));
		if (Number.isFinite(fromStorage) && fromStorage > 0) return fromStorage;
		return DEFAULT_TIMEOUT_MS;
	}

	function getBackendMasterDataBootPolicy() {
		const mode = getStoredBootMode();
		const includeAssets = getStoredIncludeAssets();
		const timeoutMs = getStoredTimeoutMs();
		return {
			mode,
			includeAssets,
			timeoutMs,
			shouldTryBackend: mode !== BOOT_MODES.STATIC,
			required: mode === BOOT_MODES.REQUIRED,
			fallbackToStaticJs: mode === BOOT_MODES.AUTO || mode === BOOT_MODES.BACKEND,
			usesLegacyEnabledKey: readStorage(LEGACY_ENABLED_STORAGE_KEY) === "1",
		};
	}

	function setBackendMasterDataBootMode(mode, options) {
		const normalized = normalizeBootMode(mode);
		writeStorage(BOOT_MODE_STORAGE_KEY, normalized);
		if (normalized === BOOT_MODES.STATIC) removeStorage(LEGACY_ENABLED_STORAGE_KEY);
		if (normalized === BOOT_MODES.BACKEND || normalized === BOOT_MODES.REQUIRED) writeStorage(LEGACY_ENABLED_STORAGE_KEY, "1");
		if (normalized === BOOT_MODES.AUTO) removeStorage(LEGACY_ENABLED_STORAGE_KEY);
		window.__UPGRADE_RPG_MASTER_DATA_BOOT_MODE__ = normalized;

		const shouldReload = !options || options.reload !== false;
		if (shouldReload && window.location && typeof window.location.reload === "function") window.location.reload();
		return getBackendMasterDataBootPolicy();
	}

	function setBackendMasterDataIncludeAssets(enabled, options) {
		writeStorage(INCLUDE_ASSETS_STORAGE_KEY, enabled ? "1" : "0");
		window.__UPGRADE_RPG_BACKEND_MASTER_DATA_INCLUDE_ASSETS__ = !!enabled;
		const shouldReload = options && options.reload === true;
		if (shouldReload && window.location && typeof window.location.reload === "function") window.location.reload();
		return getBackendMasterDataBootPolicy();
	}

	function setBackendMasterDataTimeoutMs(timeoutMs) {
		const nextTimeout = Math.max(250, Number(timeoutMs) || DEFAULT_TIMEOUT_MS);
		writeStorage(TIMEOUT_STORAGE_KEY, String(nextTimeout));
		window.__UPGRADE_RPG_BACKEND_MASTER_DATA_TIMEOUT_MS__ = nextTimeout;
		return getBackendMasterDataBootPolicy();
	}

	function useStaticMasterDataMode(options) {
		return setBackendMasterDataBootMode(BOOT_MODES.STATIC, options || {});
	}

	function useAutoBackendMasterDataMode(options) {
		return setBackendMasterDataBootMode(BOOT_MODES.AUTO, options || {});
	}

	function enableBackendMasterDataMode(options) {
		return setBackendMasterDataBootMode(BOOT_MODES.BACKEND, options || {});
	}

	function requireBackendMasterDataMode(options) {
		return setBackendMasterDataBootMode(BOOT_MODES.REQUIRED, options || {});
	}

	function disableBackendMasterDataMode(options) {
		return useStaticMasterDataMode(options || {});
	}

	function printBackendMasterDataBootPolicy() {
		const policy = getBackendMasterDataBootPolicy();
		console.table ? console.table(policy) : console.log(policy);
		return policy;
	}

	window.RpgBackendMasterDataBootPolicy = {
		BOOT_MODE_STORAGE_KEY,
		INCLUDE_ASSETS_STORAGE_KEY,
		TIMEOUT_STORAGE_KEY,
		BOOT_MODES,
		DEFAULT_BOOT_MODE,
		DEFAULT_TIMEOUT_MS,
		DEFAULT_INCLUDE_ASSETS,
		normalizeBootMode,
		getBackendMasterDataBootPolicy,
		setBackendMasterDataBootMode,
		setBackendMasterDataIncludeAssets,
		setBackendMasterDataTimeoutMs,
		useStaticMasterDataMode,
		useAutoBackendMasterDataMode,
		enableBackendMasterDataMode,
		disableBackendMasterDataMode,
		requireBackendMasterDataMode,
		printBackendMasterDataBootPolicy,
	};

	window.getBackendMasterDataBootPolicy = getBackendMasterDataBootPolicy;
	window.setBackendMasterDataBootMode = setBackendMasterDataBootMode;
	window.setBackendMasterDataIncludeAssets = setBackendMasterDataIncludeAssets;
	window.setBackendMasterDataTimeoutMs = setBackendMasterDataTimeoutMs;
	window.useStaticMasterDataMode = useStaticMasterDataMode;
	window.useAutoBackendMasterDataMode = useAutoBackendMasterDataMode;
	window.requireBackendMasterDataMode = requireBackendMasterDataMode;
	window.printBackendMasterDataBootPolicy = printBackendMasterDataBootPolicy;
})();
