(function () {
	"use strict";

	const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";
	const API_BASE_URL_STORAGE_KEY = "upgradeRpgApiBaseUrl";
	const ADMIN_WRITE_DEV_KEY_STORAGE_KEY = "upgradeRpgAdminWriteDevKey";
	const DEFAULT_REQUEST_TIMEOUT_MS = 1500;

	function trimTrailingSlash(value) {
		return String(value || "").replace(/\/+$/, "");
	}

	function getApiBaseUrl() {
		const configuredFromWindow = window.__UPGRADE_RPG_API_BASE_URL__;
		let configuredFromStorage = null;

		try {
			configuredFromStorage = window.localStorage ? window.localStorage.getItem(API_BASE_URL_STORAGE_KEY) : null;
		} catch (error) {
			configuredFromStorage = null;
		}

		return trimTrailingSlash(configuredFromWindow || configuredFromStorage || DEFAULT_API_BASE_URL);
	}

	function setApiBaseUrl(baseUrl) {
		const nextBaseUrl = trimTrailingSlash(baseUrl);
		if (!nextBaseUrl) throw new Error("API base URL이 비어 있습니다.");

		window.__UPGRADE_RPG_API_BASE_URL__ = nextBaseUrl;
		try {
			if (window.localStorage) window.localStorage.setItem(API_BASE_URL_STORAGE_KEY, nextBaseUrl);
		} catch (error) {
			// localStorage를 쓸 수 없는 환경에서도 현재 창에서는 동작하게 둡니다.
		}
		return nextBaseUrl;
	}

	function getAdminWriteDevKey() {
		try {
			return window.sessionStorage ? String(window.sessionStorage.getItem(ADMIN_WRITE_DEV_KEY_STORAGE_KEY) || "") : "";
		} catch (error) {
			return "";
		}
	}

	function setAdminWriteDevKey(value) {
		const nextValue = String(value || "").trim();
		try {
			if (window.sessionStorage) {
				if (nextValue) window.sessionStorage.setItem(ADMIN_WRITE_DEV_KEY_STORAGE_KEY, nextValue);
				else window.sessionStorage.removeItem(ADMIN_WRITE_DEV_KEY_STORAGE_KEY);
			}
		} catch (error) {
			// sessionStorage를 쓸 수 없는 환경에서는 현재 입력값만 반환합니다.
		}
		return nextValue;
	}

	function clearAdminWriteDevKey() {
		return setAdminWriteDevKey("");
	}

	function getAdminWriteHeaders() {
		const key = getAdminWriteDevKey();
		return key ? { "X-Admin-Dev-Key": key } : {};
	}

	function hasAdminWriteDevKey() {
		return !!getAdminWriteDevKey();
	}

	function buildUrl(path, query) {
		const baseUrl = getApiBaseUrl();
		const cleanPath = String(path || "").startsWith("/") ? path : `/${path}`;
		const url = new URL(`${baseUrl}${cleanPath}`);
		Object.entries(query || {}).forEach(([key, value]) => {
			if (value === undefined || value === null || value === "") return;
			url.searchParams.set(key, String(value));
		});
		return url.toString();
	}

	async function request(path, options) {
		const requestOptions = options || {};
		const url = buildUrl(path, requestOptions.query);
		const timeoutMs = Number(requestOptions.timeoutMs || 0);
		let timeoutId = null;
		let controller = null;

		if (timeoutMs > 0 && typeof AbortController !== "undefined") {
			controller = new AbortController();
			timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
		}

		let response;
		try {
			response = await fetch(url, {
				method: requestOptions.method || "GET",
				headers: {
					Accept: "application/json",
					...(requestOptions.body ? { "Content-Type": "application/json" } : {}),
					...(requestOptions.headers || {}),
				},
				body: requestOptions.body ? JSON.stringify(requestOptions.body) : undefined,
				signal: controller ? controller.signal : undefined,
			});
		} catch (error) {
			if (error && error.name === "AbortError") {
				const timeoutError = new Error(`API 요청 시간이 초과되었습니다: ${timeoutMs}ms`);
				timeoutError.url = url;
				timeoutError.timeoutMs = timeoutMs;
				throw timeoutError;
			}
			throw error;
		} finally {
			if (timeoutId) window.clearTimeout(timeoutId);
		}

		let json = null;
		try {
			json = await response.json();
		} catch (error) {
			json = null;
		}

		if (!response.ok) {
			const message = json && json.error && json.error.message ? json.error.message : `API 요청 실패: HTTP ${response.status}`;
			const apiError = new Error(message);
			apiError.status = response.status;
			apiError.response = json;
			apiError.url = url;
			throw apiError;
		}

		if (!json || json.ok !== true) {
			const apiError = new Error("API 응답 형식이 올바르지 않습니다.");
			apiError.response = json;
			apiError.url = url;
			throw apiError;
		}

		return json;
	}

	async function fetchMasterData(options) {
		const includeAssets = !!(options && options.includeAssets);
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/game/master-data", {
			query: includeAssets ? { includeAssets: true } : undefined,
			timeoutMs,
		});
	}

	async function listGameSaveSlots(options) {
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/game/save-slots", {
			timeoutMs,
		});
	}

	async function fetchAdminOverview(options) {
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/admin/overview", {
			timeoutMs,
		});
	}

	async function listAdminSaveSnapshots(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const limit = opts.limit !== undefined ? Number(opts.limit) : undefined;
		const userId = opts.userId !== undefined && opts.userId !== null && opts.userId !== "" ? Number(opts.userId) : undefined;
		const slotKey = opts.slotKey !== undefined ? String(opts.slotKey || "").trim() : undefined;
		const source = opts.source !== undefined ? String(opts.source || "").trim() : undefined;
		const defaultOnly = opts.defaultOnly === true ? true : undefined;
		const sort = opts.sort !== undefined ? String(opts.sort || "").trim() : undefined;
		return request("/admin/save-snapshots", {
			query: {
				limit,
				userId,
				slotKey,
				source,
				defaultOnly,
				sort,
			},
			timeoutMs,
		});
	}


	async function listAdminMasterCatalogDomains(options) {
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/admin/master-data/domains", {
			timeoutMs,
		});
	}

	async function listAdminMasterCatalogRows(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const domain = opts.domain !== undefined ? String(opts.domain || "").trim() : undefined;
		const limit = opts.limit !== undefined ? Number(opts.limit) : undefined;
		const page = opts.page !== undefined ? Number(opts.page) : undefined;
		const query = opts.query !== undefined ? String(opts.query || "").trim() : undefined;
		const enabled = opts.enabled !== undefined ? String(opts.enabled || "").trim() : undefined;
		const sort = opts.sort !== undefined ? String(opts.sort || "").trim() : undefined;
		return request("/admin/master-data/catalog", {
			query: {
				domain,
				limit,
				page,
				query,
				enabled,
				sort,
			},
			timeoutMs,
		});
	}

	async function fetchAdminMasterCreateBlueprint(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const domain = opts.domain !== undefined ? String(opts.domain || "").trim() : undefined;
		return request("/admin/master-data/create-blueprint", {
			query: {
				domain,
			},
			timeoutMs,
		});
	}


	async function previewAdminMasterDataCreate(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		return request("/admin/master-data/create-preview", {
			method: "POST",
			body: {
				domain: opts.domain !== undefined ? String(opts.domain || "").trim() : "",
				draft: opts.draft || {},
				reason: opts.reason || undefined,
				dryRun: true,
			},
			timeoutMs,
		});
	}


	async function applyAdminMasterDataCreate(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		return request("/admin/master-data/create-apply", {
			method: "POST",
			body: {
				domain: opts.domain !== undefined ? String(opts.domain || "").trim() : "",
				draft: opts.draft || {},
				reason: opts.reason || undefined,
				confirmText: opts.confirmText || "",
				dryRun: false,
			},
			timeoutMs,
			headers: getAdminWriteHeaders(),
		});
	}

	async function fetchAdminMasterDataDetail(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const domain = opts.domain !== undefined ? String(opts.domain || "").trim() : undefined;
		const id = opts.id !== undefined ? Number(opts.id) : (opts.rowId !== undefined ? Number(opts.rowId) : undefined);
		return request("/admin/master-data/detail", {
			query: {
				domain,
				id,
			},
			timeoutMs,
		});
	}


	async function fetchAdminMasterDataRelations(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const domain = opts.domain !== undefined ? String(opts.domain || "").trim() : undefined;
		const id = opts.id !== undefined ? Number(opts.id) : (opts.rowId !== undefined ? Number(opts.rowId) : undefined);
		const limit = opts.limit !== undefined ? Number(opts.limit) : undefined;
		return request("/admin/master-data/relations", {
			query: {
				domain,
				id,
				limit,
			},
			timeoutMs,
		});
	}



	async function previewAdminMasterDataEdit(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		return request("/admin/master-data/edit-preview", {
			method: "POST",
			body: {
				domain: opts.domain !== undefined ? String(opts.domain || "").trim() : "",
				id: opts.id !== undefined ? Number(opts.id) : (opts.rowId !== undefined ? Number(opts.rowId) : undefined),
				draft: opts.draft || {},
				baseValues: opts.baseValues || undefined,
				reason: opts.reason || undefined,
				dryRun: true,
			},
			timeoutMs,
		});
	}

	async function applyAdminMasterDataEdit(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		return request("/admin/master-data/edit-apply", {
			method: "POST",
			body: {
				domain: opts.domain !== undefined ? String(opts.domain || "").trim() : "",
				id: opts.id !== undefined ? Number(opts.id) : (opts.rowId !== undefined ? Number(opts.rowId) : undefined),
				draft: opts.draft || {},
				baseValues: opts.baseValues || undefined,
				reason: opts.reason || undefined,
				confirmText: opts.confirmText || "",
				dryRun: false,
			},
			timeoutMs,
			headers: getAdminWriteHeaders(),
		});
	}

	async function listAdminChangeLogs(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const limit = opts.limit !== undefined ? Number(opts.limit) : undefined;
		const targetType = opts.targetType !== undefined ? String(opts.targetType || "").trim() : undefined;
		const targetId = opts.targetId !== undefined ? String(opts.targetId || "").trim() : undefined;
		const action = opts.action !== undefined ? String(opts.action || "").trim() : undefined;
		const changedKey = opts.changedKey !== undefined ? String(opts.changedKey || "").trim() : undefined;
		const applied = opts.applied !== undefined && opts.applied !== "" ? opts.applied : undefined;
		const sort = opts.sort !== undefined ? String(opts.sort || "").trim() : undefined;
		return request("/admin/change-logs", {
			query: { limit, targetType, targetId, action, changedKey, applied, sort },
			timeoutMs,
		});
	}


	async function fetchAdminChangeLogDetail(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const id = opts.id !== undefined ? Number(opts.id) : (opts.changeLogId !== undefined ? Number(opts.changeLogId) : undefined);
		return request(`/admin/change-logs/${id}`, {
			timeoutMs,
		});
	}

	async function previewAdminChangeLogRollback(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const id = opts.id !== undefined ? Number(opts.id) : (opts.changeLogId !== undefined ? Number(opts.changeLogId) : undefined);
		return request(`/admin/change-logs/${id}/rollback-preview`, {
			method: "POST",
			body: {
				reason: opts.reason || undefined,
				dryRun: true,
			},
			timeoutMs,
		});
	}

	async function applyAdminChangeLogRollback(options) {
		const opts = options || {};
		const timeoutMs = opts.timeoutMs !== undefined ? Number(opts.timeoutMs) : undefined;
		const id = opts.id !== undefined ? Number(opts.id) : (opts.changeLogId !== undefined ? Number(opts.changeLogId) : undefined);
		return request(`/admin/change-logs/${id}/rollback-apply`, {
			method: "POST",
			body: {
				reason: opts.reason || undefined,
				confirmText: opts.confirmText || "",
				dryRun: false,
			},
			timeoutMs,
			headers: getAdminWriteHeaders(),
		});
	}

	async function saveGameSnapshot(payload, options) {
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/game/save", {
			method: "POST",
			body: payload || {},
			timeoutMs,
		});
	}

	async function loadGameSnapshot(options) {
		const slotKey = options && options.slotKey ? options.slotKey : undefined;
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : undefined;
		return request("/game/load", {
			query: slotKey ? { slotKey } : undefined,
			timeoutMs,
		});
	}

	window.RpgGameApi = {
		DEFAULT_API_BASE_URL,
		API_BASE_URL_STORAGE_KEY,
		ADMIN_WRITE_DEV_KEY_STORAGE_KEY,
		DEFAULT_REQUEST_TIMEOUT_MS,
		getApiBaseUrl,
		setApiBaseUrl,
		getAdminWriteDevKey,
		setAdminWriteDevKey,
		clearAdminWriteDevKey,
		getAdminWriteHeaders,
		hasAdminWriteDevKey,
		buildUrl,
		request,
		fetchMasterData,
		listGameSaveSlots,
		saveGameSnapshot,
		fetchAdminOverview,
		listAdminSaveSnapshots,
		listAdminMasterCatalogDomains,
		listAdminMasterCatalogRows,
		fetchAdminMasterCreateBlueprint,
		previewAdminMasterDataCreate,
		applyAdminMasterDataCreate,
		fetchAdminMasterDataDetail,
		fetchAdminMasterDataRelations,
		previewAdminMasterDataEdit,
		applyAdminMasterDataEdit,
		listAdminChangeLogs,
		fetchAdminChangeLogDetail,
		previewAdminChangeLogRollback,
		applyAdminChangeLogRollback,
		loadGameSnapshot,
	};
})();
