(function () {
	"use strict";

	const VERSION = "v110.backend-save-data-integrity-verify";
	const DEFAULT_SLOT_KEY = "default";
	const DEFAULT_TIMEOUT_MS = 3000;

	function stableStringify(value) {
		const seen = new WeakSet();
		function normalize(input) {
			if (!input || typeof input !== "object") return input;
			if (seen.has(input)) return "[Circular]";
			seen.add(input);
			if (Array.isArray(input)) return input.map(normalize);
			return Object.keys(input).sort().reduce((acc, key) => {
				acc[key] = normalize(input[key]);
				return acc;
			}, {});
		}
		try {
			return JSON.stringify(normalize(value));
		} catch (error) {
			return null;
		}
	}

	function getBackendSnapshotFromLoadResponse(response) {
		const payload = response && response.payload ? response.payload : null;
		if (!payload || payload.exists === false) return null;
		return payload.snapshot || null;
	}

	function getBackendIntegrityFromLoadResponse(response) {
		const payload = response && response.payload ? response.payload : null;
		return payload && payload.integrity ? payload.integrity : null;
	}

	function compareSnapshotsForIntegrity(localSnapshot, backendSnapshot) {
		if (typeof window.compareSaveSnapshots === "function") {
			return window.compareSaveSnapshots(localSnapshot, backendSnapshot);
		}
		const localRaw = stableStringify(localSnapshot);
		const backendRaw = stableStringify(backendSnapshot);
		return {
			diffs: [],
			diffCount: localRaw === backendRaw ? 0 : 1,
			sameRawSnapshot: !!localRaw && !!backendRaw && localRaw === backendRaw,
			sameImportantSummary: !!localRaw && !!backendRaw && localRaw === backendRaw,
			localRawLength: localRaw ? localRaw.length : 0,
			backendRawLength: backendRaw ? backendRaw.length : 0,
		};
	}

	async function verifyBackendSaveSnapshotIntegrity(options) {
		const opts = options || {};
		const slotKey = opts.slotKey || DEFAULT_SLOT_KEY;
		const timeoutMs = opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS;
		const local = window.readLocalSaveSnapshot
			? window.readLocalSaveSnapshot(opts.saveKey || window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22")
			: { exists: false, snapshot: null, error: "readLocalSaveSnapshot 함수를 찾을 수 없습니다." };
		const result = {
			ok: false,
			version: VERSION,
			slotKey,
			local: {
				exists: !!local.exists,
				key: local.key || opts.saveKey || window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22",
				error: local.error || null,
			},
			backend: {
				exists: false,
				status: null,
				error: null,
				integrity: null,
				updatedAt: null,
			},
			comparison: null,
			sameRawSnapshot: false,
			sameImportantSummary: false,
			diffCount: null,
			error: null,
			response: null,
		};

		if (!local.exists) {
			result.error = "localStorage 세이브가 없습니다.";
			if (opts.log !== false) console.warn("[Upgrade RPG] backend save verify failed", result);
			return result;
		}
		if (local.error || !local.snapshot) {
			result.error = `localStorage 세이브를 읽을 수 없습니다: ${local.error || "unknown"}`;
			if (opts.log !== false) console.warn("[Upgrade RPG] backend save verify failed", result);
			return result;
		}
		if (!window.loadBackendSaveSnapshot || typeof window.loadBackendSaveSnapshot !== "function") {
			result.error = "loadBackendSaveSnapshot 함수를 찾을 수 없습니다.";
			if (opts.log !== false) console.warn("[Upgrade RPG] backend save verify failed", result);
			return result;
		}

		try {
			const response = await window.loadBackendSaveSnapshot({ slotKey, timeoutMs });
			result.response = response;
			const payload = response && response.payload ? response.payload : {};
			const backendSnapshot = getBackendSnapshotFromLoadResponse(response);
			result.backend.exists = !!backendSnapshot;
			result.backend.status = payload.status || null;
			result.backend.updatedAt = payload.updatedAt || null;
			result.backend.integrity = getBackendIntegrityFromLoadResponse(response);

			if (!backendSnapshot) {
				result.error = "백엔드 DB 세이브가 비어 있습니다.";
				if (opts.log !== false) console.warn("[Upgrade RPG] backend save verify failed", result);
				return result;
			}

			const comparison = compareSnapshotsForIntegrity(local.snapshot, backendSnapshot);
			result.comparison = comparison;
			result.sameRawSnapshot = !!comparison.sameRawSnapshot;
			result.sameImportantSummary = !!comparison.sameImportantSummary;
			result.diffCount = comparison.diffCount;
			result.ok = !!comparison.sameRawSnapshot;
			if (!result.ok) result.error = "localStorage와 백엔드 DB 스냅샷이 완전히 같지 않습니다.";

			if (opts.log !== false) {
				console.log("[Upgrade RPG] backend save integrity verify", result);
				if (comparison.diffs && comparison.diffs.length && console.table) console.table(comparison.diffs);
			}
			return result;
		} catch (error) {
			result.backend.error = error && error.message ? error.message : String(error);
			result.error = result.backend.error;
			if (opts.log !== false) console.warn("[Upgrade RPG] backend save verify failed", result);
			return result;
		}
	}

	async function pushLocalSaveToBackendAndVerify(options) {
		const opts = options || {};
		if (!window.pushLocalSaveToBackend || typeof window.pushLocalSaveToBackend !== "function") {
			throw new Error("pushLocalSaveToBackend 함수를 찾을 수 없습니다.");
		}
		const saveResponse = await window.pushLocalSaveToBackend(opts);
		const verify = await verifyBackendSaveSnapshotIntegrity({
			saveKey: opts.saveKey,
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			timeoutMs: opts.verifyTimeoutMs !== undefined ? opts.verifyTimeoutMs : opts.timeoutMs,
			log: opts.log,
		});
		return {
			ok: !!(verify && verify.ok),
			saveResponse,
			verify,
		};
	}

	async function checkBackendSaveIntegrityReady(options) {
		const result = {
			ok: !!(
				window.readLocalSaveSnapshot &&
				window.loadBackendSaveSnapshot &&
				window.pushLocalSaveToBackend &&
				window.compareSaveSnapshots
			),
			version: VERSION,
			readLocalReady: typeof window.readLocalSaveSnapshot === "function",
			loadBackendReady: typeof window.loadBackendSaveSnapshot === "function",
			pushBackendReady: typeof window.pushLocalSaveToBackend === "function",
			compareReady: typeof window.compareSaveSnapshots === "function",
		};
		if (!options || options.log !== false) console.log("[Upgrade RPG] backend save integrity check", result);
		return result;
	}

	window.RpgBackendSaveIntegrity = {
		VERSION,
		stableStringify,
		verifyBackendSaveSnapshotIntegrity,
		pushLocalSaveToBackendAndVerify,
		checkBackendSaveIntegrityReady,
	};
	window.verifyBackendSaveSnapshotIntegrity = verifyBackendSaveSnapshotIntegrity;
	window.pushLocalSaveToBackendAndVerify = pushLocalSaveToBackendAndVerify;
	window.checkBackendSaveIntegrityReady = checkBackendSaveIntegrityReady;
})();
