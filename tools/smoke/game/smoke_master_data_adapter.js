const fs = require("fs");
const path = require("path");
const vm = require("vm");

const projectRoot = path.resolve(__dirname, "..", "..", "..");
const adapterPath = path.join(projectRoot, "src", "api", "master-data-adapter.js");
const bridgePath = path.join(projectRoot, "src", "api", "master-data-bridge.js");
const clientPath = path.join(projectRoot, "src", "api", "game-api-client.js");
const indexPath = path.join(projectRoot, "index.html");
const seedDir = path.join(projectRoot, "backend", "seeds", "generated");

function assert(condition, message) {
	if (!condition) {
		console.error(message);
		process.exit(1);
	}
}

function readJson(name, fallback) {
	const filePath = path.join(seedDir, name);
	if (!fs.existsSync(filePath)) return fallback;
	return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function stripAsset(value) {
	if (typeof value === "string" && value.startsWith("data:image/")) return null;
	if (Array.isArray(value)) return value.map(stripAsset);
	if (value && typeof value === "object") {
		return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, stripAsset(item)]));
	}
	return value;
}

function secondsFromMs(value) {
	if (value === null || value === undefined || value === "") return null;
	return Number(value) / 1000;
}

function inferEnhanceGroup(item) {
	if (item.isTalisman || item.isEmblem) return "talisman_emblem";
	if (["normal", "abyss", "special", "avatar"].includes(item.type)) return "normal_equipment";
	return null;
}

function buildApiPayloadFromSeed({ includeAssets = false } = {}) {
	const characters = readJson("characters.json", []);
	const skills = readJson("skills.json", []);
	const items = readJson("item_templates.json", []);
	const bosses = readJson("bosses.json", []);
	const fields = readJson("field_zones.json", []);
	const dropTables = readJson("drop_tables.json", []);
	const dropItems = readJson("drop_table_items.json", []);
	const enhancement = readJson("enhancement_rules.json", {});
	const asset = (value) => (includeAssets ? value : stripAsset(value));

	const characterSkills = [];
	characters.forEach((character) => {
		(character.skillIds || []).forEach((skillCode, index) => {
			characterSkills.push({ characterCode: character.id, skillCode, sortOrder: index, isDefault: !!character.isDefault });
		});
	});

	const skillLevels = [];
	skills.forEach((skill) => {
		for (let level = 0; level <= Number(skill.maxLevel || 0); level += 1) {
			skillLevels.push({
				skillCode: skill.id,
				level,
				damageMultiplier: skill.damageMultiplier,
				procRateBonus: 0,
				options: { source: "seed", level },
			});
		}
	});

	const enhancementGroups = [
		{
			code: "normal_equipment",
			name: "일반 장비 강화",
			description: "일반 장비/심연 장비 강화 규칙",
			maxLevel: enhancement.normalEquipment ? enhancement.normalEquipment.maxLevel : 20,
			rules: { source: "seed", raw: enhancement.normalEquipment || {} },
			isEnabled: true,
		},
		{
			code: "talisman_emblem",
			name: "탈리스만/빛나는 휘장 강화",
			description: "0강 동일 아이템 재료를 사용해 강화하는 규칙",
			maxLevel: enhancement.talismanAndEmblem ? enhancement.talismanAndEmblem.maxLevel : 6,
			rules: { source: "seed", raw: enhancement.talismanAndEmblem || {} },
			isEnabled: true,
		},
	];

	return {
		characters: characters.map((character) => ({
			code: character.id,
			name: character.name,
			description: character.description,
			imageUrl: null,
			hasImage: false,
			isEnabled: true,
			meta: asset({ source: "seed", raw: character }),
		})),
		skills: skills.map((skill) => ({
			code: skill.id,
			name: skill.name,
			slotKey: skill.slotKey,
			description: skill.description,
			iconUrl: includeAssets ? skill.img : null,
			hasIcon: !!skill.img,
			procRate: skill.baseProcRate,
			cooldownSeconds: secondsFromMs(skill.cooldownMs),
			options: asset({
				source: "seed",
				skillType: skill.skillType,
				effectHtml: skill.effectHtml,
				damageMultiplier: skill.damageMultiplier,
				bonusGroup: skill.bonusGroup,
				awakening: skill.awakening,
				raw: skill,
			}),
		})),
		skillLevels,
		characterSkills,
		itemTemplates: items.map((item) => ({
			code: item.templateKey,
			name: item.name,
			itemType: item.type,
			grade: item.tier !== null && item.tier !== undefined ? String(item.tier) : item.grade,
			iconUrl: includeAssets ? item.img : null,
			hasIcon: !!item.img,
			description: item.equipText || item.description || null,
			stackable: ["skillBook", "material", "consumable"].includes(item.type),
			equipSlot: item.equipGroup || item.specialSlotIdx || null,
			enhanceGroupCode: inferEnhanceGroup(item),
			baseStats: item.baseStats || {},
			options: asset({
				source: "seed",
				tier: item.tier,
				equipGroup: item.equipGroup,
				equipLimit: item.equipLimit,
				specialSlotIdx: item.specialSlotIdx,
				specialStats: item.specialStats,
				sellPrice: item.sellPrice,
				baseCost: item.baseCost,
				baseIlv: item.baseIlv,
				raw: item.raw || item,
			}),
		})),
		bosses: bosses.map((boss) => ({
			code: `boss_${boss.id}`,
			name: boss.name,
			tier: boss.id,
			bossType: boss.isSpecial ? "special" : "normal",
			hp: boss.maxHp,
			imageUrl: includeAssets ? boss.img : null,
			hasImage: !!boss.img,
			description: boss.title || boss.desc1,
			summonRules: asset({
				source: "seed",
				title: boss.title,
				desc1: boss.desc1,
				desc2: boss.desc2,
				desc3: boss.desc3,
				reqLvl: boss.reqLvl,
				dropsList: boss.dropsList || [],
				dropRateDoubled: boss.dropRateDoubled,
				raw: boss,
			}),
			cooldownSeconds: secondsFromMs(boss.cooldownMs),
			isEnabled: true,
		})),
		fieldZones: fields.map((zone) => ({
			code: `field_${zone.level}`,
			name: zone.name,
			sortOrder: zone.level,
			enemyHp: zone.maxHp,
			goldReward: zone.goldReward,
			description: zone.enemyName || zone.name,
			entryRules: zone.req || {},
			farmRules: zone.farm || {},
			isEnabled: true,
		})),
		dropTables: dropTables.map((table) => ({
			code: table.id,
			ownerType: "boss",
			ownerCode: `boss_${table.bossId}`,
			description: table.title,
			rules: { source: "seed", raw: table },
			isEnabled: true,
		})),
		dropTableItems: dropItems.map((item, index) => ({
			id: index + 1,
			dropTableCode: item.dropTableId,
			itemTemplateCode: item.itemTemplateKey,
			rate: item.rate,
			minQuantity: item.quantityMin,
			maxQuantity: item.quantityMax,
			conditions: asset({ source: "seed", bossId: item.bossId, sortOrder: item.sortOrder, raw: item.raw || item }),
		})),
		enhancementGroups,
		enhancementLevels: [],
		enhancementRules: { groups: enhancementGroups, levels: [] },
		assetPolicy: { includeAssets, mode: includeAssets ? "inline-data-url" : "metadata-only" },
		counts: {
			characters: characters.length,
			skills: skills.length,
			characterSkills: characterSkills.length,
			skillLevels: skillLevels.length,
			itemTemplates: items.length,
			bosses: bosses.length,
			fieldZones: fields.length,
			dropTables: dropTables.length,
			dropTableItems: dropItems.length,
			enhancementGroups: enhancementGroups.length,
			enhancementLevels: 26,
		},
	};
}

assert(fs.existsSync(adapterPath), "src/api/master-data-adapter.js 파일이 없습니다.");

const indexHtml = fs.readFileSync(indexPath, "utf8");
const clientTagIndex = indexHtml.indexOf('src="src/api/game-api-client.js?v=378"');
const bridgeTagIndex = indexHtml.indexOf('src="src/api/master-data-bridge.js"');
const adapterTagIndex = indexHtml.indexOf('src="src/api/master-data-adapter.js?v=400"');
const dataTagIndex = indexHtml.indexOf('src="src/data/skills.js?v=378"');
assert(clientTagIndex >= 0, "index.html에 game-api-client.js script 태그가 없습니다.");
assert(bridgeTagIndex >= 0, "index.html에 master-data-bridge.js script 태그가 없습니다.");
assert(adapterTagIndex >= 0, "index.html에 master-data-adapter.js script 태그가 없습니다.");
assert(clientTagIndex < bridgeTagIndex, "game-api-client.js는 master-data-bridge.js보다 먼저 로드되어야 합니다.");
assert(bridgeTagIndex < adapterTagIndex, "master-data-bridge.js는 master-data-adapter.js보다 먼저 로드되어야 합니다.");
assert(adapterTagIndex < dataTagIndex, "master-data-adapter.js는 기존 데이터 파일보다 먼저 로드되어도 안전해야 합니다.");

const fakePayload = buildApiPayloadFromSeed({ includeAssets: false });
const fakeResponse = { ok: true, payload: fakePayload };

const sandbox = {
	console,
	URL,
	Date,
	window: {},
	fetch: async (url) => ({
		ok: true,
		status: 200,
		json: async () => ({
			ok: true,
			responseVersion: "game-api-response.v1",
			type: "game.master_data",
			payload: String(url).includes("includeAssets=true") ? buildApiPayloadFromSeed({ includeAssets: true }) : fakePayload,
			error: null,
		}),
	}),
};
sandbox.window = sandbox;
sandbox.localStorage = {
	items: {},
	getItem(key) { return this.items[key] || null; },
	setItem(key, value) { this.items[key] = String(value); },
};

vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(clientPath, "utf8"), sandbox, { filename: clientPath });
vm.runInContext(fs.readFileSync(bridgePath, "utf8"), sandbox, { filename: bridgePath });
vm.runInContext(fs.readFileSync(adapterPath, "utf8"), sandbox, { filename: adapterPath });

assert(sandbox.RpgMasterDataAdapter, "RpgMasterDataAdapter 전역 객체가 생성되지 않았습니다.");
assert(typeof sandbox.checkBackendMasterDataAdapter === "function", "checkBackendMasterDataAdapter 콘솔 함수가 없습니다.");

const legacyData = sandbox.RpgMasterDataAdapter.createLegacyMasterDataFromPayload(fakeResponse);
const validation = sandbox.RpgMasterDataAdapter.validateLegacyMasterData(legacyData);
assert(validation.ok, `adapter validation failed: ${JSON.stringify(validation.failures)}`);
assert(legacyData.defaultCharacterId === "weapon_master", "defaultCharacterId가 weapon_master가 아닙니다.");
assert(legacyData.skillMasterData.lightsabre.baseProcRate === null, "lightsabre.baseProcRate null 보존 실패");
assert(legacyData.bossList.length === 39, "일반 보스 수가 39개가 아닙니다.");
assert(legacyData.specialBossList.length === 6, "특수 보스 수가 6개가 아닙니다.");
assert(legacyData.fieldZones.length === 40, "필드 수가 40개가 아닙니다.");
assert(legacyData.itemTemplateList.length === 245, "아이템 템플릿 수가 245개가 아닙니다.");
assert(validation.hasInlineAsset === false, "기본 adapter 결과에 inline data URL이 남아 있습니다.");

// 실제 API → adapter → runtime 교체 → killEnemy → inventory 경로를 실행합니다.
// 선택적으로 공개 API 응답/배포 JS를 넣어 동일한 회귀를 배포 전후에 확인합니다.
function checkBossDropRuntime(payload, adapterSource = fs.readFileSync(adapterPath, "utf8")) {
	const context = {
		console, Date, Math: Object.create(Math),
		document: { getElementById: () => null },
		getTotals: () => ({ dropInc: 0 }),
		addLog() {}, showItemDropText() {}, updateCombatUI() {}, renderUI() {}, clearInterval() {},
	};
	context.window = context;
	vm.createContext(context);
	for (const file of ["src/state/game-state.js", "src/systems/item-system.js", "src/rules/boss-drop-rules.js", "src/systems/combat-system.js"]) {
		vm.runInContext(fs.readFileSync(path.join(projectRoot, file), "utf8"), context, { filename: file });
	}
	vm.runInContext(adapterSource, context);
	vm.runInContext("const bossList = []; const specialBossList = []; const characterMasterData = {}; const skillMasterData = {}; const zones = [];", context);
	vm.runInContext(fs.readFileSync(path.join(projectRoot, "src/api/master-data-runtime-switch.js"), "utf8"), context);
	const adapted = context.RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ ok: true, payload });
	context.RpgBackendMasterDataRuntime.applyLegacyMasterData(adapted, { hydrateStaticAssets: false });
	const bosses = vm.runInContext("[...bossList, ...specialBossList]", context);
	assert(bosses.length === 45, "드랍 회귀는 일반 39 + 특수 6 보스를 모두 검사해야 합니다.");
	let awardedItems = 0;
	const kill = (boss, roll = 1e-12, equipEnabled = true, capacity = 60) => {
		context.player = context.createDefaultPlayerState();
		context.player.maxInventorySize = capacity;
		context.player.maxStorageSize = capacity;
		context.player.firstEquipSkillDropGiven = { [boss.id]: true };
		context.currentBoss = JSON.parse(JSON.stringify(boss));
		context.currentZoneType = "boss_fight";
		context.equipDropEnabled = equipEnabled;
		context.autoBossSummon = false;
		context.Math.random = () => roll;
		context.killEnemy(boss);
		if (boss.isSpecial) assert(context.player.specialBossCD[boss.id] > Date.now(), `${boss.code}: 처치 cooldown 누락`);
		return context.player.inventory.filter(Boolean);
	};
	for (const boss of bosses) {
		const source = payload.bosses.find((row) => row.code === boss.code).summonRules.raw;
		assert(boss.dropTitle === "[획득 가능 아이템]", `${boss.code}: undefined 드랍 제목`);
		assert(boss.dropsList.length > 0 && !boss.dropsList.join().includes("undefined"), `${boss.code}: 드랍 목록 누락`);
		for (const key of ["equipDropRate", "skillDropRate", "talismanDropRate", "emblemDropRate"]) {
			assert(Number.isFinite(boss[key]) && boss[key] === (source[key] ?? 0), `${boss.code}: ${key} 누락/중복 보정`);
		}
		assert(kill(boss).length > 0, `${boss.code}: 처치 후 보상 없음`);
		assert(kill(boss, 0.999999).length === 0, `${boss.code}: 실패 확률에서 보상 발생`);
		assert(kill(boss, 1e-12, true, 0).length === 0, `${boss.code}: 가방 용량 초과`);
		for (const drop of boss.drops) {
			const singleDropBoss = { ...boss, drops: [drop] };
			const items = kill(singleDropBoss);
			assert(items.length === 1 && items[0].templateKey === drop.templateKey, `${boss.code}: ${drop.name} 실제 지급 실패`);
			assert(items[0].count === (drop.count || 1), `${boss.code}: ${drop.name} 수량 변경`);
			awardedItems += 1;
			if ((drop.type === "normal" || drop.type === "special_equip") && !drop.isTalisman && !drop.individualDropRate) {
				assert(kill(singleDropBoss, 1e-12, false).length === (boss.isSpecial ? 1 : 0), `${boss.code}: 장비 드랍 OFF 계약 변경`);
			}
		}
	}
	assert(awardedItems === 245, "245개 드랍 아이템의 실제 지급을 모두 확인해야 합니다.");
	assert(JSON.stringify(context.RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ ok: true, payload }).bossList) === JSON.stringify(adapted.bossList), "재변환 시 확률/원본 변경");
	console.log(`boss drop runtime passed: ${bosses.length} bosses, ${awardedItems} items, loss/full-inventory/equipment-toggle guards`);
}

checkBossDropRuntime(fakePayload);
checkBossDropRuntime(buildApiPayloadFromSeed({ includeAssets: true }));
const fallbackPayload = JSON.parse(JSON.stringify(fakePayload));
delete fallbackPayload.bosses[0].summonRules.raw.equipDropRate;
const fallbackBoss = sandbox.RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ ok: true, payload: fallbackPayload }).bossList[0];
assert(fallbackBoss.equipDropRate === 0.08, "drop table의 보정된 확률 fallback 실패");
fallbackPayload.bosses[0].summonRules.raw.equipDropRate = 0;
assert(sandbox.RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ ok: true, payload: fallbackPayload }).bossList[0].equipDropRate === 0, "명시적 0 확률 보존 실패");
if (process.argv[2]) {
	const live = JSON.parse(fs.readFileSync(path.resolve(process.argv[2]), "utf8").replace(/^\uFEFF/, ""));
	checkBossDropRuntime(live.payload, process.argv[3] ? fs.readFileSync(path.resolve(process.argv[3]), "utf8") : undefined);
}

(async () => {
	const result = await sandbox.checkBackendMasterDataAdapter();
	assert(result.ok === true, "브라우저 adapter 체크 함수가 실패했습니다.");
	const resultWithAssets = await sandbox.checkBackendMasterDataAdapter({ includeAssets: true });
	assert(resultWithAssets.ok === true, "includeAssets adapter 체크 함수가 실패했습니다.");
	console.log("master-data adapter smoke test passed");
})();
