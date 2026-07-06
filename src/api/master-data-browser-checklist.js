(function () {
	"use strict";

	const CHECKLIST_VERSION = "v091.backend-master-data-browser-checklist";

	const REQUIRED_HELPERS = [
		"enableBackendMasterDataMode",
		"disableBackendMasterDataMode",
		"checkBackendMasterDataRuntimeMode",
		"checkBackendMasterDataRuntimeIntegrity",
		"getBackendMasterDataRuntimeDebugSnapshot",
	];

	const REQUIRED_RENDER_FUNCTIONS = [
		"renderUI",
		"renderSkills",
		"renderBossZone",
		"renderSpecialBossZone",
		"renderFieldZone",
	];

	const REQUIRED_GAME_FUNCTIONS = [
		"toggleBossPanel",
		"toggleSpecialBossPanel",
		"toggleFieldZone",
		"openTestItemModal",
		"openTestSpecialItemModal",
		"giveBeginnerItem",
	];

	const REQUIRED_DOM_IDS = [
		"battle-zone",
		"enemy-image-placeholder",
		"enemy-name",
		"enemy-hp-bar",
		"enemy-hp-text",
		"char-panel",
		"inventory-container",
		"boss-grid",
		"special-boss-grid",
		"field-list-container",
		"test-item-modal",
		"test-special-item-modal",
	];

	const MINIMUM_COUNTS = {
		characters: 1,
		skills: 8,
		itemTemplates: 245,
		normalBosses: 39,
		specialBosses: 6,
		fieldZones: 40,
	};

	function isObject(value) {
		return value && typeof value === "object" && !Array.isArray(value);
	}

	function asArray(value) {
		return Array.isArray(value) ? value : [];
	}

	function safeRead(readFn, fallback) {
		try {
			return readFn();
		} catch (error) {
			return fallback;
		}
	}

	function safeCall(name, args) {
		try {
			if (typeof window[name] === "function") {
				return { ok: true, value: window[name].apply(window, args || []) };
			}
			if (typeof globalThis[name] === "function") {
				return { ok: true, value: globalThis[name].apply(globalThis, args || []) };
			}
			return { ok: false, error: `${name} 함수를 찾을 수 없습니다.` };
		} catch (error) {
			return { ok: false, error: error && error.message ? error.message : String(error) };
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

	function countObjectKeys(value) {
		return isObject(value) ? Object.keys(value).length : 0;
	}

	function getActiveDataSnapshot() {
		const characterData = safeRead(() => characterMasterData, {});
		const skillData = safeRead(() => skillMasterData, {});
		const normalBosses = safeRead(() => bossList, []);
		const specialBosses = safeRead(() => specialBossList, []);
		const fieldZones = safeRead(() => zones, []);
		const applied = window.backendAppliedMasterData || null;

		return {
			counts: {
				characters: countObjectKeys(characterData),
				skills: countObjectKeys(skillData),
				itemTemplates: applied && Array.isArray(applied.itemTemplateList) ? applied.itemTemplateList.length : null,
				normalBosses: asArray(normalBosses).length,
				specialBosses: asArray(specialBosses).length,
				fieldZones: asArray(fieldZones).length,
			},
			samples: {
				firstSkillCode: Object.keys(characterData).length ? Object.keys(characterData)[0] : null,
				lightsabreProcRate: skillData && skillData.lightsabre ? skillData.lightsabre.baseProcRate : undefined,
				firstNormalBoss: normalBosses && normalBosses[0] ? pickBossSample(normalBosses[0]) : null,
				firstSpecialBoss: specialBosses && specialBosses[0] ? pickBossSample(specialBosses[0]) : null,
				firstFieldZone: fieldZones && fieldZones[0] ? pickFieldSample(fieldZones[0]) : null,
			},
		};
	}

	function pickBossSample(boss) {
		return {
			id: boss.id,
			name: boss.name,
			title: boss.title,
			maxHp: boss.maxHp,
			hasImage: !!boss.img,
			dropsCount: Array.isArray(boss.drops) ? boss.drops.length : Array.isArray(boss.dropsList) ? boss.dropsList.length : 0,
		};
	}

	function pickFieldSample(field) {
		return {
			level: field.level,
			name: field.name,
			maxHp: field.maxHp,
			goldReward: field.goldReward,
			hasImage: !!field.img,
		};
	}

	function refreshRenderablePanels() {
		const calls = [];
		["renderUI", "renderSkills", "renderBossZone", "renderSpecialBossZone", "renderFieldZone"].forEach((name) => {
			const result = safeCall(name);
			calls.push({ name, ok: result.ok, error: result.error || null });
		});
		return calls;
	}

	function countDom(selector) {
		return document.querySelectorAll(selector).length;
	}

	function getDomSnapshot() {
		return {
			bossGridSlots: countDom("#boss-grid .boss-slot"),
			specialBossGridSlots: countDom("#special-boss-grid .boss-slot"),
			fieldRows: countDom("#field-list-container .field-row"),
			fieldSlots: countDom("#field-list-container .boss-slot"),
			inventorySlots: countDom("#inventory-container .item-slot"),
			normalEquipSlots: countDom("#equip-normal .item-slot"),
			specialEquipSlots: countDom("#equip-special .item-slot"),
			skillSlots: countDom(".skill-slot, .skill-card, [data-skill-id]"),
		};
	}

	function makeCheck(id, label, ok, details, level, fix) {
		return {
			id,
			label,
			ok: !!ok,
			level: level || (ok ? "pass" : "fail"),
			details: details === undefined ? null : details,
			fix: fix || null,
		};
	}

	function addFunctionChecks(results, names, category) {
		names.forEach((name) => {
			const exists = typeof window[name] === "function" || typeof globalThis[name] === "function";
			results.push(makeCheck(
				`${category}.${name}`,
				`${name} 함수 존재`,
				exists,
				{ name },
				undefined,
				`${name} 함수가 없으면 index.html script 로딩 순서 또는 파일 누락을 확인하세요.`
			));
		});
	}

	function addDomChecks(results) {
		REQUIRED_DOM_IDS.forEach((id) => {
			const exists = !!document.getElementById(id);
			results.push(makeCheck(
				`dom.${id}`,
				`#${id} 요소 존재`,
				exists,
				{ id },
				undefined,
				`index.html에서 #${id} 요소가 삭제되었는지 확인하세요.`
			));
		});
	}

	function addCountChecks(results, snapshot) {
		Object.entries(MINIMUM_COUNTS).forEach(([key, minimum]) => {
			const actual = snapshot.counts[key];
			if (actual === null && key === "itemTemplates") {
				results.push(makeCheck(
					`counts.${key}`,
					`${key} 개수 확인`,
					false,
					{ actual, expectedMinimum: minimum },
					"warn",
					"itemTemplates는 백엔드 master-data 적용 후 window.backendAppliedMasterData에서 확인됩니다. 백엔드 모드를 켠 뒤 다시 검사하세요."
				));
				return;
			}
			results.push(makeCheck(
				`counts.${key}`,
				`${key} 최소 개수`,
				Number(actual || 0) >= minimum,
				{ actual, expectedMinimum: minimum },
				undefined,
				"seed import, master-data API, runtime switch 적용 상태를 확인하세요."
			));
		});
	}

	function addRenderedPanelChecks(results, domSnapshot) {
		results.push(makeCheck("render.bossGrid", "일반보스 그리드 렌더링", domSnapshot.bossGridSlots >= 12, { actual: domSnapshot.bossGridSlots, expectedMinimum: 12 }, undefined, "renderBossZone() 실행 또는 bossList 데이터를 확인하세요."));
		results.push(makeCheck("render.specialBossGrid", "특수보스 그리드 렌더링", domSnapshot.specialBossGridSlots >= 6, { actual: domSnapshot.specialBossGridSlots, expectedMinimum: 6 }, undefined, "renderSpecialBossZone() 실행 또는 specialBossList 데이터를 확인하세요."));
		results.push(makeCheck("render.fieldZone", "필드존 목록 렌더링", domSnapshot.fieldSlots >= 8, { actual: domSnapshot.fieldSlots, expectedMinimum: 8 }, undefined, "renderFieldZone() 실행 또는 zones/fieldGroups 데이터를 확인하세요."));
		results.push(makeCheck("render.inventory", "인벤토리 슬롯 렌더링", domSnapshot.inventorySlots > 0, { actual: domSnapshot.inventorySlots }, undefined, "renderUI() 실행 또는 #inventory-container를 확인하세요."));
		results.push(makeCheck("render.equipment", "장비 슬롯 렌더링", domSnapshot.normalEquipSlots + domSnapshot.specialEquipSlots >= 15, { normal: domSnapshot.normalEquipSlots, special: domSnapshot.specialEquipSlots }, undefined, "renderUI() 실행 또는 장비 슬롯 DOM id를 확인하세요."));
	}

	function addRuntimeChecks(results, options, integritySummary) {
		const status = getRuntimeStatus();
		const enabled = isBackendModeEnabled();
		const state = status && status.state ? status.state : null;
		const requireBackendMode = options.requireBackendMode !== false;
		const acceptedAppliedStates = ["applied", "applied_with_missing_targets"];

		results.push(makeCheck("runtime.switchReady", "백엔드 master-data 런타임 스위치 준비", !!window.RpgBackendMasterDataRuntime, { hasRuntime: !!window.RpgBackendMasterDataRuntime }, undefined, "src/api/master-data-runtime-switch.js 로딩 여부를 확인하세요."));
		results.push(makeCheck("runtime.validatorReady", "런타임 검증기 준비", !!window.RpgBackendMasterDataRuntimeValidator, { hasValidator: !!window.RpgBackendMasterDataRuntimeValidator }, undefined, "src/api/master-data-runtime-validator.js 로딩 여부를 확인하세요."));
		results.push(makeCheck("runtime.modeEnabled", "백엔드 데이터 모드 ON", !requireBackendMode || enabled, { enabled, requireBackendMode }, requireBackendMode && !enabled ? "fail" : "pass", "브라우저 Console에서 enableBackendMasterDataMode()를 실행한 뒤 새로고침하세요."));
		results.push(makeCheck("runtime.modeApplied", "백엔드 데이터 적용 완료", !requireBackendMode || acceptedAppliedStates.includes(state), { state }, requireBackendMode && !acceptedAppliedStates.includes(state) ? "fail" : "pass", "FastAPI 서버가 켜져 있는지 확인하고 페이지를 새로고침하세요."));
		if (integritySummary) {
			results.push(makeCheck("runtime.integrity", "기존 런타임 무결성 검사 통과", integritySummary.ok === true, integritySummary, integritySummary.ok ? "pass" : "fail", "checkBackendMasterDataRuntimeIntegrity({ requireBackendMode: true }) 결과의 failures를 확인하세요."));
		}
	}

	function addSampleChecks(results, snapshot) {
		const samples = snapshot.samples || {};
		results.push(makeCheck("sample.normalBoss", "첫 일반보스 샘플 확인", !!(samples.firstNormalBoss && samples.firstNormalBoss.maxHp), samples.firstNormalBoss, undefined, "bossList[0] 데이터 변환을 확인하세요."));
		results.push(makeCheck("sample.specialBoss", "첫 특수보스 샘플 확인", !!(samples.firstSpecialBoss && samples.firstSpecialBoss.maxHp), samples.firstSpecialBoss, undefined, "specialBossList[0] 데이터 변환을 확인하세요."));
		results.push(makeCheck("sample.fieldZone", "첫 필드 샘플 확인", !!(samples.firstFieldZone && samples.firstFieldZone.maxHp), samples.firstFieldZone, undefined, "zones[0] 데이터 변환을 확인하세요."));
		results.push(makeCheck("sample.lightsabreProcRate", "lightsabre procRate null 유지", samples.lightsabreProcRate === null, { actual: samples.lightsabreProcRate, expected: null }, undefined, "v087 nullable skill field 보정이 적용됐는지 확인하세요."));
	}

	function buildManualChecklist() {
		return [
			"브라우저 Console에서 enableBackendMasterDataMode() 실행 후 자동 새로고침 확인",
			"Console에서 runBackendMasterDataBrowserChecklist() 실행 후 ok: true 확인",
			"보스존 입장 버튼 클릭 → 일반보스 목록/툴팁/소환 클릭이 기존과 같은지 확인",
			"특수보스 패널 클릭 → 특수보스 목록/쿨타임 표시/소환 제한이 기존과 같은지 확인",
			"필드존 선택 클릭 → 필드 목록/입장 조건/툴팁이 기존과 같은지 확인",
			"장비지급/특수보스 장비지급 모달 클릭 → 아이템 목록이 비어 있지 않은지 확인",
			"인벤토리 열기 → 장비 슬롯/아이템 슬롯이 깨지지 않는지 확인",
			"문제가 없으면 disableBackendMasterDataMode()로 OFF 복귀 가능 여부 확인",
		];
	}

	function summarizeResults(results) {
		const failCount = results.filter((check) => check.level === "fail" && !check.ok).length;
		const warnCount = results.filter((check) => check.level === "warn" && !check.ok).length;
		return {
			ok: failCount === 0,
			failCount,
			warnCount,
			passCount: results.filter((check) => check.ok).length,
			total: results.length,
		};
	}

	function runBackendMasterDataBrowserChecklist(options) {
		const opts = {
			requireBackendMode: true,
			refreshPanels: true,
			log: true,
			...(options || {}),
		};
		const refreshResults = opts.refreshPanels ? refreshRenderablePanels() : [];
		const integritySummary = typeof window.checkBackendMasterDataRuntimeIntegrity === "function"
			? window.checkBackendMasterDataRuntimeIntegrity({ requireBackendMode: opts.requireBackendMode })
			: null;
		const snapshot = getActiveDataSnapshot();
		const domSnapshot = getDomSnapshot();
		const results = [];

		addFunctionChecks(results, REQUIRED_HELPERS, "helper");
		addFunctionChecks(results, REQUIRED_RENDER_FUNCTIONS, "renderFunction");
		addFunctionChecks(results, REQUIRED_GAME_FUNCTIONS, "gameFunction");
		addDomChecks(results);
		addRuntimeChecks(results, opts, integritySummary);
		addCountChecks(results, snapshot);
		addRenderedPanelChecks(results, domSnapshot);
		addSampleChecks(results, snapshot);

		const summary = summarizeResults(results);
		const report = {
			ok: summary.ok,
			version: CHECKLIST_VERSION,
			options: opts,
			summary,
			runtimeStatus: getRuntimeStatus(),
			dataSnapshot: snapshot,
			domSnapshot,
			refreshResults,
			results,
			manualChecklist: buildManualChecklist(),
		};

		if (opts.log) {
			const logger = report.ok ? console.log : console.warn;
			logger("[Upgrade RPG] backend master-data browser checklist", report);
			if (console.table) {
				console.table(results.map((check) => ({
					id: check.id,
					ok: check.ok,
					level: check.level,
					label: check.label,
				})));
			}
		}
		return report;
	}

	function assertBackendMasterDataBrowserChecklist(options) {
		const report = runBackendMasterDataBrowserChecklist(options || {});
		if (!report.ok) {
			const failed = report.results.filter((check) => check.level === "fail" && !check.ok).map((check) => check.id).join(", ");
			throw new Error(`backend master-data browser checklist failed: ${failed}`);
		}
		return report;
	}

	function printBackendMasterDataManualChecklist() {
		const list = buildManualChecklist();
		console.log("[Upgrade RPG] backend master-data manual checklist");
		list.forEach((item, index) => console.log(`${index + 1}. ${item}`));
		return list;
	}

	window.RpgBackendMasterDataBrowserChecklist = {
		CHECKLIST_VERSION,
		REQUIRED_HELPERS,
		REQUIRED_RENDER_FUNCTIONS,
		REQUIRED_GAME_FUNCTIONS,
		REQUIRED_DOM_IDS,
		MINIMUM_COUNTS,
		runBackendMasterDataBrowserChecklist,
		assertBackendMasterDataBrowserChecklist,
		printBackendMasterDataManualChecklist,
		buildManualChecklist,
		getActiveDataSnapshot,
		getDomSnapshot,
	};

	window.runBackendMasterDataBrowserChecklist = runBackendMasterDataBrowserChecklist;
	window.assertBackendMasterDataBrowserChecklist = assertBackendMasterDataBrowserChecklist;
	window.printBackendMasterDataManualChecklist = printBackendMasterDataManualChecklist;
})();
