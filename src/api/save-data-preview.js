(function () {
	"use strict";

	const VERSION = "v105.backend-save-data-preview-compare";
	const DEFAULT_SLOT_KEY = "default";
	const DEFAULT_TIMEOUT_MS = 2500;

	function isPlainObject(value) {
		return !!value && typeof value === "object" && !Array.isArray(value);
	}

	function countFilledItems(items) {
		return Array.isArray(items) ? items.filter(Boolean).length : 0;
	}

	function safeNumber(value) {
		const number = Number(value);
		return Number.isFinite(number) ? number : null;
	}

	function getPlayer(snapshot) {
		return snapshot && isPlainObject(snapshot.player) ? snapshot.player : {};
	}

	function getEquipmentKeys(player) {
		const equipment = player && isPlainObject(player.equipment) ? player.equipment : {};
		return Object.keys(equipment).filter((key) => equipment[key]).sort();
	}

	function summarizeSnapshot(snapshot) {
		if (!snapshot || !isPlainObject(snapshot)) {
			return {
				exists: false,
				saveVersion: null,
				level: null,
				gold: null,
				currentCharacterId: null,
				currentZoneIndex: null,
				currentZoneType: null,
				fieldEnemyHp: null,
				inventoryItems: 0,
				storageItems: 0,
				trashItems: 0,
				mailboxItems: 0,
				equippedSlots: 0,
				equipmentKeys: [],
			};
		}
		const player = getPlayer(snapshot);
		const equipmentKeys = getEquipmentKeys(player);
		return {
			exists: true,
			saveVersion: snapshot.saveVersion !== undefined ? snapshot.saveVersion : null,
			level: player.level !== undefined ? player.level : null,
			gold: player.gold !== undefined ? player.gold : null,
			currentCharacterId: snapshot.currentCharacterId || player.currentCharacterId || null,
			currentZoneIndex: snapshot.currentZoneIndex !== undefined ? snapshot.currentZoneIndex : null,
			currentZoneType: snapshot.currentZoneType || null,
			fieldEnemyHp: snapshot.fieldEnemyHp !== undefined ? safeNumber(snapshot.fieldEnemyHp) : null,
			inventoryItems: countFilledItems(player.inventory),
			storageItems: countFilledItems(player.storage),
			trashItems: countFilledItems(player.trash),
			mailboxItems: countFilledItems(player.mailbox),
			equippedSlots: equipmentKeys.length,
			equipmentKeys,
		};
	}

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

	function buildDiff(label, key, localSummary, backendSummary) {
		const localValue = localSummary ? localSummary[key] : null;
		const backendValue = backendSummary ? backendSummary[key] : null;
		const localText = Array.isArray(localValue) ? localValue.join(",") : localValue;
		const backendText = Array.isArray(backendValue) ? backendValue.join(",") : backendValue;
		if (String(localText) === String(backendText)) return null;
		return { key, label, local: localValue, backend: backendValue };
	}

	function compareSaveSnapshots(localSnapshot, backendSnapshot) {
		const localSummary = summarizeSnapshot(localSnapshot);
		const backendSummary = summarizeSnapshot(backendSnapshot);
		const diffDefinitions = [
			["저장 버전", "saveVersion"],
			["레벨", "level"],
			["골드", "gold"],
			["캐릭터", "currentCharacterId"],
			["필드 인덱스", "currentZoneIndex"],
			["필드 타입", "currentZoneType"],
			["필드 몬스터 HP", "fieldEnemyHp"],
			["인벤토리 아이템 수", "inventoryItems"],
			["창고 아이템 수", "storageItems"],
			["휴지통 아이템 수", "trashItems"],
			["우편 수", "mailboxItems"],
			["장착 슬롯 수", "equippedSlots"],
			["장착 슬롯 종류", "equipmentKeys"],
		];
		const diffs = diffDefinitions
			.map(([label, key]) => buildDiff(label, key, localSummary, backendSummary))
			.filter(Boolean);
		const localRaw = stableStringify(localSnapshot);
		const backendRaw = stableStringify(backendSnapshot);
		return {
			localSummary,
			backendSummary,
			diffs,
			diffCount: diffs.length,
			sameRawSnapshot: !!localRaw && !!backendRaw && localRaw === backendRaw,
			sameImportantSummary: diffs.length === 0,
			localRawLength: localRaw ? localRaw.length : 0,
			backendRawLength: backendRaw ? backendRaw.length : 0,
		};
	}

	function getRecommendation(local, backend, comparison) {
		if (!local.exists) return "local_missing";
		if (!backend.exists) return "backend_empty_push_local_first";
		if (comparison.sameRawSnapshot) return "same_snapshot_safe";
		if (comparison.sameImportantSummary) return "minor_or_hidden_difference_review_raw";
		return "different_review_before_restore";
	}

	function formatPreviewTableRows(diffs) {
		if (!diffs || !diffs.length) return [];
		return diffs.map((diff) => ({
			항목: diff.label,
			localStorage: Array.isArray(diff.local) ? diff.local.join(", ") : diff.local,
			backendDB: Array.isArray(diff.backend) ? diff.backend.join(", ") : diff.backend,
		}));
	}

	async function previewBackendSaveSnapshot(options) {
		const opts = options || {};
		const local = window.readLocalSaveSnapshot
			? window.readLocalSaveSnapshot(opts.saveKey || window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22")
			: { exists: false, snapshot: null, error: "readLocalSaveSnapshot 함수를 찾을 수 없습니다." };
		let backendResponse = null;
		let backendPayload = null;
		let backendError = null;
		try {
			if (!window.loadBackendSaveSnapshot || typeof window.loadBackendSaveSnapshot !== "function") {
				throw new Error("loadBackendSaveSnapshot 함수를 찾을 수 없습니다.");
			}
			backendResponse = await window.loadBackendSaveSnapshot({
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
			});
			backendPayload = backendResponse && backendResponse.payload ? backendResponse.payload : null;
		} catch (error) {
			backendError = error && error.message ? error.message : String(error);
		}

		const backendExists = !!(backendPayload && backendPayload.exists !== false && backendPayload.snapshot);
		const comparison = compareSaveSnapshots(local.snapshot, backendExists ? backendPayload.snapshot : null);
		const result = {
			ok: !local.error && !backendError,
			version: VERSION,
			local: {
				exists: !!local.exists,
				key: local.key || opts.saveKey || window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22",
				error: local.error || null,
				summary: comparison.localSummary,
			},
			backend: {
				exists: backendExists,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				status: backendPayload ? backendPayload.status : null,
				error: backendError,
				updatedAt: backendPayload ? backendPayload.updatedAt : null,
				source: backendPayload ? backendPayload.source : null,
				summary: comparison.backendSummary,
			},
			comparison,
			recommendation: getRecommendation(local, { exists: backendExists }, comparison),
			backendResponse,
		};

		if (opts.log !== false) {
			console.log("[Upgrade RPG] backend save preview", result);
			const rows = formatPreviewTableRows(comparison.diffs);
			if (rows.length && console.table) console.table(rows);
		}
		return result;
	}

	async function assertBackendSaveSnapshotPreview(options) {
		const result = await previewBackendSaveSnapshot(options || {});
		if (!result.local.exists) throw new Error("localStorage 세이브가 없습니다.");
		if (result.local.error) throw new Error(`localStorage 세이브 오류: ${result.local.error}`);
		if (result.backend.error) throw new Error(`백엔드 세이브 조회 오류: ${result.backend.error}`);
		return result;
	}

	window.RpgBackendSaveDataPreview = {
		VERSION,
		summarizeSnapshot,
		compareSaveSnapshots,
		previewBackendSaveSnapshot,
		assertBackendSaveSnapshotPreview,
	};
	window.summarizeSaveSnapshotForPreview = summarizeSnapshot;
	window.compareSaveSnapshots = compareSaveSnapshots;
	window.previewBackendSaveSnapshot = previewBackendSaveSnapshot;
	window.assertBackendSaveSnapshotPreview = assertBackendSaveSnapshotPreview;
})();
