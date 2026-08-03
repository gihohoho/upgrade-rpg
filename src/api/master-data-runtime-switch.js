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

	function getBootPolicy() {
		if (window.RpgBackendMasterDataBootPolicy && typeof window.RpgBackendMasterDataBootPolicy.getBackendMasterDataBootPolicy === "function") {
			return window.RpgBackendMasterDataBootPolicy.getBackendMasterDataBootPolicy();
		}
		const legacyEnabled = readStorage(STORAGE_KEY) === "1" || window.__UPGRADE_RPG_USE_BACKEND_MASTER_DATA__ === true;
		return {
			mode: legacyEnabled ? "backend" : "static",
			includeAssets: true,
			timeoutMs: 5000,
			shouldTryBackend: legacyEnabled,
			required: false,
			fallbackToStaticJs: true,
		};
	}

	function isBackendMasterDataModeEnabled() {
		return !!getBootPolicy().shouldTryBackend;
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
		const policy = getBootPolicy();
		const status = {
			modeEnabled: isBackendMasterDataModeEnabled(),
			bootPolicy: policy,
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

	function isMissingAsset(value) {
		return value === undefined || value === null || value === "" || value === "undefined";
	}

	function buildStaticDropAssetIndex() {
		const byName = {};
		const byNameAndType = {};
		const collectDrops = (bosses) => {
			(Array.isArray(bosses) ? bosses : []).forEach((boss) => {
				(Array.isArray(boss.drops) ? boss.drops : []).forEach((drop) => {
					if (!drop || !drop.name || !drop.img) return;
					byName[drop.name] = drop;
					byNameAndType[`${drop.name}::${drop.type || ""}`] = drop;
				});
			});
		};
		try {
			if (typeof bossList !== "undefined") collectDrops(bossList);
			if (typeof specialBossList !== "undefined") collectDrops(specialBossList);
		} catch (error) {
			// 정적 보스 데이터가 아직 없다면 무시합니다.
		}
		return { byName, byNameAndType };
	}

	function hydrateMissingAssetsFromStaticData(legacyData) {
		const hydrated = {
			characters: 0,
			skills: 0,
			bosses: 0,
			bossDrops: 0,
			itemTemplates: 0,
			fieldZones: 0,
		};

		try {
			if (typeof characterMasterData !== "undefined") {
				Object.entries(legacyData.characterMasterData || {}).forEach(([id, character]) => {
					const staticCharacter = characterMasterData[id];
					if (character && staticCharacter && isMissingAsset(character.img) && staticCharacter.img) {
						character.img = staticCharacter.img;
						hydrated.characters += 1;
					}
				});
			}
		} catch (error) {
			// 캐릭터 정적 데이터가 없으면 무시합니다.
		}

		try {
			if (typeof skillMasterData !== "undefined") {
				Object.entries(legacyData.skillMasterData || {}).forEach(([id, skill]) => {
					const staticSkill = skillMasterData[id];
					if (skill && staticSkill && isMissingAsset(skill.img) && staticSkill.img) {
						skill.img = staticSkill.img;
						hydrated.skills += 1;
					}
				});
			}
		} catch (error) {
			// 스킬 정적 데이터가 없으면 무시합니다.
		}

		const staticBosses = [];
		try {
			if (typeof bossList !== "undefined") staticBosses.push(...bossList.map((boss) => ({ ...boss, isSpecial: false })));
			if (typeof specialBossList !== "undefined") staticBosses.push(...specialBossList.map((boss) => ({ ...boss, isSpecial: true })));
		} catch (error) {
			// 정적 보스 데이터가 없으면 무시합니다.
		}
		const staticBossByKey = {};
		staticBosses.forEach((boss) => {
			if (!boss) return;
			staticBossByKey[`${boss.isSpecial ? "special" : "normal"}::${boss.id}`] = boss;
			if (boss.name) staticBossByKey[`name::${boss.name}`] = boss;
		});

		const hydrateBossList = (bosses) => {
			(Array.isArray(bosses) ? bosses : []).forEach((boss) => {
				const staticBoss = staticBossByKey[`${boss.isSpecial ? "special" : "normal"}::${boss.id}`] || staticBossByKey[`name::${boss.name}`];
				if (!staticBoss) return;
				if (isMissingAsset(boss.img) && staticBoss.img) {
					boss.img = staticBoss.img;
					hydrated.bosses += 1;
				}
				const staticDropsByName = {};
				(Array.isArray(staticBoss.drops) ? staticBoss.drops : []).forEach((drop) => {
					if (drop && drop.name) staticDropsByName[drop.name] = drop;
				});
				(Array.isArray(boss.drops) ? boss.drops : []).forEach((drop) => {
					const staticDrop = drop && staticDropsByName[drop.name];
					if (!staticDrop || !staticDrop.img) return;
					if (isMissingAsset(drop.img)) {
						drop.img = staticDrop.img;
						hydrated.bossDrops += 1;
					}
					if (drop.raw && isMissingAsset(drop.raw.img)) drop.raw.img = staticDrop.img;
				});
			});
		};
		hydrateBossList(legacyData.bossList);
		hydrateBossList(legacyData.specialBossList);

		const dropAssetIndex = buildStaticDropAssetIndex();
		(Array.isArray(legacyData.itemTemplateList) ? legacyData.itemTemplateList : []).forEach((item) => {
			if (!item || !item.name) return;
			const staticDrop = dropAssetIndex.byNameAndType[`${item.name}::${item.type || ""}`] || dropAssetIndex.byName[item.name];
			if (!staticDrop || !staticDrop.img) return;
			if (isMissingAsset(item.img)) {
				item.img = staticDrop.img;
				hydrated.itemTemplates += 1;
			}
			if (item.raw && isMissingAsset(item.raw.img)) item.raw.img = staticDrop.img;
		});

		try {
			if (typeof zones !== "undefined") {
				const staticZoneByLevel = {};
				const staticZoneByName = {};
				(Array.isArray(zones) ? zones : []).forEach((zone) => {
					if (!zone) return;
					if (zone.level !== undefined && zone.level !== null) staticZoneByLevel[String(zone.level)] = zone;
					if (zone.name) staticZoneByName[zone.name] = zone;
				});
				(Array.isArray(legacyData.fieldZones) ? legacyData.fieldZones : []).forEach((field) => {
					if (!field) return;
					const staticField = staticZoneByLevel[String(field.level)] || staticZoneByName[field.name];
					if (!staticField || !staticField.img) return;
					if (isMissingAsset(field.img)) {
						field.img = staticField.img;
						hydrated.fieldZones += 1;
					}
				});
			}
		} catch (error) {
			// 필드 정적 데이터가 없으면 무시합니다. render 단계에서 안전한 기본 이미지로 한 번 더 방어합니다.
		}

		legacyData.staticAssetHydration = hydrated;
		return hydrated;
	}

	function applyLegacyMasterData(legacyData, options) {
		if (!legacyData || typeof legacyData !== "object") {
			throw new Error("적용할 legacy master-data가 없습니다.");
		}

		const shouldHydrateStaticAssets = !options || options.hydrateStaticAssets !== false;
		const assetHydration = shouldHydrateStaticAssets ? hydrateMissingAssetsFromStaticData(legacyData) : null;

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

		if (typeof applyWeaponMasterSkillIconAssets === "function") {
			applyWeaponMasterSkillIconAssets(skillMasterData);
		}
		if (typeof applyEquipmentIconAssets === "function") applyEquipmentIconAssets();
		if (Array.isArray(legacyData.itemTemplateList) && typeof normalizeItemIcon === "function") {
			legacyData.itemTemplateList.forEach((item) => {
				normalizeItemIcon(item);
				if (item && item.raw) normalizeItemIcon(item.raw);
			});
		}
		if (typeof player !== "undefined" && typeof normalizePlayerItemIcons === "function") {
			normalizePlayerItemIcons(player);
		}

		const missing = Object.entries(applied).filter(([, ok]) => !ok).map(([key]) => key);
		const status = setStatus({
			state: missing.length ? "applied_with_missing_targets" : "applied",
			applied,
			missing,
			counts: legacyData.counts || {},
			defaultCharacterId: legacyData.defaultCharacterId || null,
			includeAssets: !!(options && options.includeAssets),
			assetHydration,
		});

		window.backendAppliedMasterData = legacyData;
		return status;
	}

	async function loadAndApplyBackendMasterData(options) {
		assertAdapterReady();
		const policy = getBootPolicy();
		const includeAssets = options && options.includeAssets !== undefined ? !!options.includeAssets : !!policy.includeAssets;
		const timeoutMs = options && options.timeoutMs !== undefined ? Number(options.timeoutMs) : Number(policy.timeoutMs || 5000);
		setStatus({ state: "loading", includeAssets, timeoutMs, bootPolicy: policy });
		const snapshot = await window.RpgMasterDataAdapter.loadAdaptedMasterDataFromApi({ includeAssets, timeoutMs });
		if (!snapshot.validation || snapshot.validation.ok !== true) {
			const failures = snapshot.validation ? snapshot.validation.failures : [];
			throw new Error(`master-data adapter 검증 실패: ${failures.join(", ")}`);
		}
		const status = applyLegacyMasterData(snapshot.legacyData, { includeAssets, hydrateStaticAssets: !includeAssets });
		status.snapshot = snapshot;
		return status;
	}

	async function applyBackendMasterDataBeforeGameStart() {
		const policy = getBootPolicy();
		if (!policy.shouldTryBackend) {
			return setStatus({ state: "static_js_mode", bootPolicy: policy });
		}

		try {
			const status = await loadAndApplyBackendMasterData({ includeAssets: policy.includeAssets, timeoutMs: policy.timeoutMs });
			console.log("[Upgrade RPG] backend master-data runtime mode applied", {
				mode: policy.mode,
				includeAssets: policy.includeAssets,
				counts: status.counts,
				applied: status.applied,
				assetHydration: status.assetHydration,
			});
			return status;
		} catch (error) {
			const state = policy.required ? "failed_required_backend_static_js_continued" : "failed_fallback_to_static_js";
			console.warn("[Upgrade RPG] backend master-data runtime mode failed. 기존 JS 데이터로 계속 실행합니다.", error);
			return setStatus({
				state,
				bootPolicy: policy,
				errorMessage: error && error.message ? error.message : String(error),
			});
		}
	}

	function setBackendMasterDataMode(enabled, options) {
		const shouldEnable = !!enabled;
		if (window.RpgBackendMasterDataBootPolicy) {
			return shouldEnable
				? window.RpgBackendMasterDataBootPolicy.enableBackendMasterDataMode(options || {})
				: window.RpgBackendMasterDataBootPolicy.disableBackendMasterDataMode(options || {});
		}

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
		const policy = getBootPolicy();
		const summary = {
			modeEnabled: isBackendMasterDataModeEnabled(),
			bootPolicy: policy,
			state: status.state,
			counts: status.counts || null,
			applied: status.applied || null,
			missing: status.missing || [],
			assetHydration: status.assetHydration || null,
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
		getBootPolicy,
		isBackendMasterDataModeEnabled,
		setBackendMasterDataMode,
		enableBackendMasterDataMode,
		disableBackendMasterDataMode,
		getBackendMasterDataRuntimeStatus,
		checkBackendMasterDataRuntimeMode,
		hydrateMissingAssetsFromStaticData,
		applyLegacyMasterData,
		loadAndApplyBackendMasterData,
		applyBackendMasterDataBeforeGameStart,
	};

	window.enableBackendMasterDataMode = enableBackendMasterDataMode;
	window.disableBackendMasterDataMode = disableBackendMasterDataMode;
	window.checkBackendMasterDataRuntimeMode = checkBackendMasterDataRuntimeMode;
	window.getBackendMasterDataRuntimeStatus = getBackendMasterDataRuntimeStatus;

	wrapWindowOnload();
	setStatus({ state: getBootPolicy().shouldTryBackend ? "backend_auto_waiting_for_page_load" : "static_js_mode" });
})();
