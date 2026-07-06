(function () {
	"use strict";

	const EXPECTED_MINIMUMS = {
		characters: 1,
		skills: 8,
		itemTemplates: 245,
		normalBosses: 39,
		specialBosses: 6,
		fieldZones: 40,
	};

	const REQUIRED_DOM_IDS = [
		"battle-zone",
		"enemy-image-placeholder",
		"enemy-name",
		"enemy-hp-bar",
		"enemy-hp-text",
		"field-info-panel",
		"boss-info-panel",
		"char-panel",
		"inventory-container",
		"player-gold",
		"boss-grid",
		"special-boss-grid",
		"field-list-container",
	];

	function asArray(value) {
		return Array.isArray(value) ? value : [];
	}

	function countObjectKeys(value) {
		return value && typeof value === "object" && !Array.isArray(value) ? Object.keys(value).length : 0;
	}

	function safeReadGlobal(readFn, fallback) {
		try {
			return readFn();
		} catch (error) {
			return fallback;
		}
	}

	function getRuntimeStatus() {
		if (window.RpgBackendMasterDataRuntime && typeof window.RpgBackendMasterDataRuntime.getBackendMasterDataRuntimeStatus === "function") {
			return window.RpgBackendMasterDataRuntime.getBackendMasterDataRuntimeStatus();
		}
		return null;
	}

	function isBackendModeEnabled() {
		if (window.RpgBackendMasterDataRuntime && typeof window.RpgBackendMasterDataRuntime.isBackendMasterDataModeEnabled === "function") {
			return window.RpgBackendMasterDataRuntime.isBackendMasterDataModeEnabled();
		}
		return false;
	}

	function getStaticGlobalCounts() {
		const characterData = safeReadGlobal(() => characterMasterData, null);
		const skillData = safeReadGlobal(() => skillMasterData, null);
		const normalBosses = safeReadGlobal(() => bossList, []);
		const specialBosses = safeReadGlobal(() => specialBossList, []);
		const fieldZones = safeReadGlobal(() => zones, []);

		return {
			characters: countObjectKeys(characterData),
			skills: countObjectKeys(skillData),
			normalBosses: asArray(normalBosses).length,
			specialBosses: asArray(specialBosses).length,
			fieldZones: asArray(fieldZones).length,
		};
	}

	function getAppliedBackendCounts() {
		const applied = window.backendAppliedMasterData || null;
		if (!applied) return null;
		return {
			characters: countObjectKeys(applied.characterMasterData),
			skills: countObjectKeys(applied.skillMasterData),
			itemTemplates: asArray(applied.itemTemplateList).length,
			normalBosses: asArray(applied.bossList).length,
			specialBosses: asArray(applied.specialBossList).length,
			fieldZones: asArray(applied.fieldZones).length,
		};
	}

	function getActiveCounts() {
		const staticCounts = getStaticGlobalCounts();
		const appliedCounts = getAppliedBackendCounts();
		return {
			...staticCounts,
			itemTemplates: appliedCounts ? appliedCounts.itemTemplates : null,
		};
	}

	function collectCountFailures(counts, requireItemTemplates) {
		const failures = [];
		Object.entries(EXPECTED_MINIMUMS).forEach(([key, minimum]) => {
			if (key === "itemTemplates" && !requireItemTemplates && counts[key] === null) return;
			const actual = Number(counts[key] || 0);
			if (actual < minimum) {
				failures.push({
					type: "count_too_low",
					key,
					expectedMinimum: minimum,
					actual,
				});
			}
		});
		return failures;
	}

	function collectDomFailures() {
		return REQUIRED_DOM_IDS
			.filter((id) => !document.getElementById(id))
			.map((id) => ({ type: "missing_dom", id }));
	}

	function collectBackendModeFailures(options, runtimeStatus) {
		const failures = [];
		const requireBackendMode = !!(options && options.requireBackendMode);
		const enabled = isBackendModeEnabled();
		const state = runtimeStatus && runtimeStatus.state;
		const acceptableAppliedStates = ["applied", "applied_with_missing_targets"];

		if (requireBackendMode && !enabled) {
			failures.push({ type: "backend_mode_disabled", message: "백엔드 master-data 모드가 꺼져 있습니다." });
		}
		if (requireBackendMode && enabled && !acceptableAppliedStates.includes(state)) {
			failures.push({
				type: "backend_mode_not_applied",
				state: state || null,
				message: "백엔드 master-data 모드가 켜져 있지만 아직 적용 완료 상태가 아닙니다.",
			});
		}
		if (enabled && state === "failed_fallback_to_static_js") {
			failures.push({
				type: "backend_mode_failed",
				state,
				errorMessage: runtimeStatus && runtimeStatus.errorMessage ? runtimeStatus.errorMessage : null,
			});
		}
		return failures;
	}

	function getSampleData() {
		const normalBosses = safeReadGlobal(() => bossList, []);
		const specialBosses = safeReadGlobal(() => specialBossList, []);
		const fieldZones = safeReadGlobal(() => zones, []);
		const skillData = safeReadGlobal(() => skillMasterData, {});
		const firstNormalBoss = asArray(normalBosses)[0] || null;
		const firstSpecialBoss = asArray(specialBosses)[0] || null;
		const firstZone = asArray(fieldZones)[0] || null;
		return {
			firstNormalBoss: firstNormalBoss ? { id: firstNormalBoss.id, name: firstNormalBoss.name, maxHp: firstNormalBoss.maxHp } : null,
			firstSpecialBoss: firstSpecialBoss ? { id: firstSpecialBoss.id, name: firstSpecialBoss.name, maxHp: firstSpecialBoss.maxHp } : null,
			firstZone: firstZone ? { level: firstZone.level, name: firstZone.name, maxHp: firstZone.maxHp, goldReward: firstZone.goldReward } : null,
			lightsabreProcRate: skillData && skillData.lightsabre ? skillData.lightsabre.baseProcRate : undefined,
		};
	}

	function checkBackendMasterDataRuntimeIntegrity(options) {
		const opts = options || {};
		const runtimeStatus = getRuntimeStatus();
		const modeEnabled = isBackendModeEnabled();
		const activeCounts = getActiveCounts();
		const appliedCounts = getAppliedBackendCounts();
		const failures = [
			...collectCountFailures(activeCounts, !!appliedCounts),
			...collectDomFailures(),
			...collectBackendModeFailures(opts, runtimeStatus),
		];
		const summary = {
			ok: failures.length === 0,
			modeEnabled,
			requireBackendMode: !!opts.requireBackendMode,
			runtimeState: runtimeStatus && runtimeStatus.state ? runtimeStatus.state : null,
			activeCounts,
			appliedCounts,
			appliedTargets: runtimeStatus && runtimeStatus.applied ? runtimeStatus.applied : null,
			missingTargets: runtimeStatus && runtimeStatus.missing ? runtimeStatus.missing : [],
			samples: getSampleData(),
			failures,
		};

		if (summary.ok) {
			console.log("[Upgrade RPG] backend master-data runtime integrity check passed", summary);
		} else {
			console.warn("[Upgrade RPG] backend master-data runtime integrity check failed", summary);
		}
		return summary;
	}

	function assertBackendMasterDataRuntimeIntegrity(options) {
		const summary = checkBackendMasterDataRuntimeIntegrity(options || {});
		if (!summary.ok) {
			throw new Error(`backend master-data runtime integrity check failed: ${summary.failures.map((failure) => failure.type).join(", ")}`);
		}
		return summary;
	}

	function getBackendMasterDataRuntimeDebugSnapshot() {
		return {
			status: getRuntimeStatus(),
			modeEnabled: isBackendModeEnabled(),
			activeCounts: getActiveCounts(),
			appliedCounts: getAppliedBackendCounts(),
			samples: getSampleData(),
		};
	}

	window.RpgBackendMasterDataRuntimeValidator = {
		EXPECTED_MINIMUMS,
		REQUIRED_DOM_IDS,
		getStaticGlobalCounts,
		getAppliedBackendCounts,
		getActiveCounts,
		checkBackendMasterDataRuntimeIntegrity,
		assertBackendMasterDataRuntimeIntegrity,
		getBackendMasterDataRuntimeDebugSnapshot,
	};

	window.checkBackendMasterDataRuntimeIntegrity = checkBackendMasterDataRuntimeIntegrity;
	window.assertBackendMasterDataRuntimeIntegrity = assertBackendMasterDataRuntimeIntegrity;
	window.getBackendMasterDataRuntimeDebugSnapshot = getBackendMasterDataRuntimeDebugSnapshot;
})();
