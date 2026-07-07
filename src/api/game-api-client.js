(function () {
	"use strict";

	const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";
	const API_BASE_URL_STORAGE_KEY = "upgradeRpgApiBaseUrl";
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
		DEFAULT_REQUEST_TIMEOUT_MS,
		getApiBaseUrl,
		setApiBaseUrl,
		buildUrl,
		request,
		fetchMasterData,
		listGameSaveSlots,
		saveGameSnapshot,
		loadGameSnapshot,
	};
})();
