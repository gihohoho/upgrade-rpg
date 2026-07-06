(function () {
	"use strict";

	const EXPECTED_MINIMUM_COUNTS = {
		characters: 1,
		skills: 8,
		characterSkills: 8,
		skillLevels: 64,
		itemTemplates: 245,
		bosses: 45,
		fieldZones: 40,
		dropTables: 45,
		dropTableItems: 245,
		enhancementGroups: 2,
		enhancementLevels: 26,
	};

	function getPayload(apiResponse) {
		return (apiResponse && apiResponse.payload) || {};
	}

	function getCounts(payload) {
		return (payload && payload.counts) || {};
	}

	function validateMasterDataPayload(payload) {
		const counts = getCounts(payload);
		const failures = Object.entries(EXPECTED_MINIMUM_COUNTS)
			.map(([key, expectedMinimum]) => ({
				key,
				expectedMinimum,
				actual: Number(counts[key] || 0),
			}))
			.filter((item) => item.actual < item.expectedMinimum);

		return {
			ok: failures.length === 0,
			counts,
			failures,
		};
	}

	function containsInlineDataUrl(value) {
		if (typeof value === "string") return value.startsWith("data:image/");
		if (Array.isArray(value)) return value.some((item) => containsInlineDataUrl(item));
		if (value && typeof value === "object") return Object.values(value).some((item) => containsInlineDataUrl(item));
		return false;
	}

	function validateDefaultAssetPolicy(payload) {
		return {
			ok: !containsInlineDataUrl(payload),
			assetPolicy: payload ? payload.assetPolicy : null,
		};
	}

	async function loadMasterDataFromApi(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.fetchMasterData !== "function") {
			throw new Error("RpgGameApi가 준비되지 않았습니다. src/api/game-api-client.js 로딩 순서를 확인하세요.");
		}

		const includeAssets = !!(options && options.includeAssets);
		const apiResponse = await window.RpgGameApi.fetchMasterData({ includeAssets });
		const payload = getPayload(apiResponse);
		const validation = validateMasterDataPayload(payload);
		const assetValidation = includeAssets ? { ok: true, assetPolicy: payload.assetPolicy } : validateDefaultAssetPolicy(payload);

		const snapshot = {
			loadedAt: new Date().toISOString(),
			includeAssets,
			apiBaseUrl: window.RpgGameApi.getApiBaseUrl(),
			apiResponse,
			payload,
			counts: validation.counts,
			validation,
			assetValidation,
		};

		window.backendMasterDataSnapshot = snapshot;
		return snapshot;
	}

	async function checkMasterDataApi(options) {
		const snapshot = await loadMasterDataFromApi(options || {});
		const countOk = snapshot.validation.ok;
		const assetOk = snapshot.assetValidation.ok;
		const ok = countOk && assetOk;

		const summary = {
			ok,
			includeAssets: snapshot.includeAssets,
			apiBaseUrl: snapshot.apiBaseUrl,
			counts: snapshot.counts,
			countFailures: snapshot.validation.failures,
			assetPolicyOk: assetOk,
		};

		if (ok) {
			console.log("[Upgrade RPG] master-data API check passed", summary);
		} else {
			console.warn("[Upgrade RPG] master-data API check failed", summary);
		}
		return summary;
	}

	function getCachedMasterData() {
		return window.backendMasterDataSnapshot || null;
	}

	window.RpgMasterDataBridge = {
		EXPECTED_MINIMUM_COUNTS,
		getPayload,
		getCounts,
		validateMasterDataPayload,
		containsInlineDataUrl,
		validateDefaultAssetPolicy,
		loadMasterDataFromApi,
		checkMasterDataApi,
		getCachedMasterData,
	};

	// 브라우저 콘솔에서 초보자도 바로 실행할 수 있도록 짧은 별칭을 둡니다.
	window.loadBackendMasterData = loadMasterDataFromApi;
	window.checkBackendMasterData = checkMasterDataApi;
	window.getCachedBackendMasterData = getCachedMasterData;
})();
