(function () {
	"use strict";

	function unwrapPayload(apiResponseOrPayload) {
		return (apiResponseOrPayload && apiResponseOrPayload.payload) || apiResponseOrPayload || {};
	}

	function asArray(value) {
		return Array.isArray(value) ? value : [];
	}

	function asNumberOrNull(value) {
		if (value === null || value === undefined || value === "") return null;
		const numberValue = Number(value);
		return Number.isFinite(numberValue) ? numberValue : null;
	}

	function asMilliseconds(seconds) {
		const numberValue = asNumberOrNull(seconds);
		return numberValue === null ? null : numberValue * 1000;
	}

	function cloneJson(value) {
		if (value === undefined) return undefined;
		try {
			return JSON.parse(JSON.stringify(value));
		} catch (error) {
			return value;
		}
	}

	function containsInlineDataUrl(value) {
		if (typeof value === "string") return value.startsWith("data:image/");
		if (Array.isArray(value)) return value.some((item) => containsInlineDataUrl(item));
		if (value && typeof value === "object") return Object.values(value).some((item) => containsInlineDataUrl(item));
		return false;
	}

	function mapBy(items, key) {
		const map = {};
		asArray(items).forEach((item) => {
			const value = item && item[key];
			if (value !== undefined && value !== null && value !== "") map[String(value)] = item;
		});
		return map;
	}

	function groupBy(items, key) {
		const groups = {};
		asArray(items).forEach((item) => {
			const value = item && item[key];
			if (value === undefined || value === null || value === "") return;
			const groupKey = String(value);
			if (!groups[groupKey]) groups[groupKey] = [];
			groups[groupKey].push(item);
		});
		return groups;
	}

	function parseBossId(code, tier) {
		if (Number.isFinite(Number(tier))) return Number(tier);
		const match = String(code || "").match(/boss_(\d+)/);
		return match ? Number(match[1]) : null;
	}

	function inferDefaultCharacterId(characters, characterSkills) {
		const enabledCharacters = asArray(characters).filter((character) => character && character.isEnabled !== false);
		const skillCharacterCodes = new Set(asArray(characterSkills).map((row) => row.characterCode).filter(Boolean));
		const firstWithSkills = enabledCharacters.find((character) => skillCharacterCodes.has(character.code));
		return (firstWithSkills && firstWithSkills.code) || (enabledCharacters[0] && enabledCharacters[0].code) || null;
	}

	function buildCharacterMasterData(payload) {
		const characters = asArray(payload.characters);
		const characterSkillGroups = groupBy(payload.characterSkills, "characterCode");
		const output = {};

		characters.forEach((character) => {
			if (!character || !character.code) return;
			const skillIds = asArray(characterSkillGroups[character.code])
				.slice()
				.sort((a, b) => Number(a.sortOrder || 0) - Number(b.sortOrder || 0))
				.map((row) => row.skillCode)
				.filter(Boolean);

			output[character.code] = {
				id: character.code,
				name: character.name,
				description: character.description,
				img: character.imageUrl || null,
				hasImage: !!character.hasImage,
				isEnabled: character.isEnabled !== false,
				skillIds,
				meta: cloneJson(character.meta || {}),
			};
		});

		return output;
	}

	function getMaxSkillLevel(skillLevels, skillCode) {
		let maxLevel = 0;
		asArray(skillLevels).forEach((row) => {
			if (row.skillCode !== skillCode) return;
			const level = Number(row.level || 0);
			if (level > maxLevel) maxLevel = level;
		});
		return maxLevel;
	}

	function buildSkillMasterData(payload) {
		const output = {};
		const skillLevels = asArray(payload.skillLevels);

		asArray(payload.skills).forEach((skill) => {
			if (!skill || !skill.code) return;
			const options = skill.options || {};
			const raw = options.raw || {};
			const awakening = options.awakening || raw.awakening || null;
			const cooldownMs = raw.cooldownMs !== undefined && raw.cooldownMs !== null ? raw.cooldownMs : asMilliseconds(skill.cooldownSeconds);

			output[skill.code] = {
				id: skill.code,
				slotKey: skill.slotKey || raw.slotKey || "",
				name: skill.name || raw.name || skill.code,
				img: skill.iconUrl || raw.img || null,
				hasIcon: !!skill.hasIcon,
				description: skill.description || raw.description || "",
				effectHtml: options.effectHtml || raw.effectHtml || "",
				maxLevel: Number(raw.maxLevel ?? getMaxSkillLevel(skillLevels, skill.code) ?? 0),
				skillType: options.skillType || raw.skillType || null,
				baseProcRate: skill.procRate === undefined ? raw.baseProcRate ?? null : skill.procRate,
				damageMultiplier: options.damageMultiplier ?? raw.damageMultiplier ?? null,
				cooldownMs,
				bonusGroup: options.bonusGroup ?? raw.bonusGroup ?? null,
				awakening: cloneJson(awakening),
				raw: cloneJson(raw),
			};
		});

		return output;
	}

	function inferEnhanceGroup(item) {
		if (!item) return null;
		if (item.enhanceGroupCode) return item.enhanceGroupCode;
		const raw = (item.options && item.options.raw) || {};
		if (raw.isTalisman || raw.isEmblem) return "talisman_emblem";
		if (["normal", "abyss", "special", "avatar"].includes(item.itemType || raw.type)) return "normal_equipment";
		return null;
	}

	function buildItemTemplateList(payload) {
		return asArray(payload.itemTemplates).map((item) => {
			const options = item.options || {};
			const raw = options.raw || {};
			const tier = options.tier ?? raw.tier ?? item.grade ?? null;
			return {
				templateKey: item.code,
				code: item.code,
				name: item.name || raw.name || item.code,
				type: item.itemType || raw.type || "unknown",
				tier: tier === null ? null : Number(tier),
				grade: item.grade,
				img: item.iconUrl || raw.img || null,
				hasIcon: !!item.hasIcon,
				equipGroup: options.equipGroup ?? raw.equipGroup ?? item.equipSlot ?? null,
				equipLimit: options.equipLimit ?? raw.equipLimit ?? null,
				equipText: item.description || raw.equipText || null,
				specialSlotIdx: options.specialSlotIdx ?? raw.specialSlotIdx ?? null,
				isTalisman: !!raw.isTalisman,
				isEmblem: !!raw.isEmblem,
				sellPrice: options.sellPrice ?? raw.sellPrice ?? null,
				baseCost: options.baseCost ?? raw.baseCost ?? null,
				baseIlv: options.baseIlv ?? raw.baseIlv ?? null,
				baseStats: cloneJson(item.baseStats || raw.baseStats || {}),
				specialStats: cloneJson(options.specialStats ?? raw.specialStats ?? null),
				enhanceGroupCode: inferEnhanceGroup(item),
				stackable: !!item.stackable,
				raw: cloneJson(raw),
			};
		});
	}

	function buildDropTables(payload) {
		const dropTables = asArray(payload.dropTables);
		const dropItemsByTable = groupBy(payload.dropTableItems, "dropTableCode");
		const itemByCode = mapBy(payload.itemTemplates, "code");

		return dropTables.map((table) => {
			const raw = (table.rules && table.rules.raw) || {};
			const items = asArray(dropItemsByTable[table.code])
				.slice()
				.sort((a, b) => Number((a.conditions && a.conditions.sortOrder) || a.id || 0) - Number((b.conditions && b.conditions.sortOrder) || b.id || 0))
				.map((row) => {
					const item = itemByCode[row.itemTemplateCode] || {};
					const itemRaw = (item.options && item.options.raw) || (row.conditions && row.conditions.raw) || {};
					return {
						dropTableCode: row.dropTableCode,
						itemTemplateCode: row.itemTemplateCode,
						itemName: item.name || itemRaw.name || row.itemTemplateCode,
						itemType: item.itemType || itemRaw.type || null,
						rate: row.rate,
						quantityMin: row.minQuantity,
						quantityMax: row.maxQuantity,
						conditions: cloneJson(row.conditions || {}),
						raw: cloneJson(itemRaw),
					};
				});

			return {
				id: table.code,
				code: table.code,
				bossId: raw.bossId || parseBossId(table.ownerCode, null),
				bossName: raw.bossName || null,
				bossType: raw.bossType || null,
				title: table.description || raw.title || "",
				rawEquipDropRate: raw.rawEquipDropRate ?? null,
				rawSkillDropRate: raw.rawSkillDropRate ?? null,
				rawTalismanDropRate: raw.rawTalismanDropRate ?? null,
				rawEmblemDropRate: raw.rawEmblemDropRate ?? null,
				items,
				raw: cloneJson(raw),
			};
		});
	}

	function buildBossLists(payload) {
		const dropTableByOwnerCode = {};
		asArray(payload.dropTables).forEach((table) => {
			if (table.ownerCode) dropTableByOwnerCode[table.ownerCode] = table;
		});
		const dropItemsByTable = groupBy(payload.dropTableItems, "dropTableCode");
		const itemTemplates = mapBy(payload.itemTemplates, "code");

		const bosses = asArray(payload.bosses).map((boss) => {
			const summonRules = boss.summonRules || {};
			const raw = summonRules.raw || {};
			const id = parseBossId(boss.code, boss.tier);
			const table = dropTableByOwnerCode[boss.code] || null;
			const dropRows = table ? asArray(dropItemsByTable[table.code]) : [];
			const drops = dropRows.map((row) => {
				const template = itemTemplates[row.itemTemplateCode] || {};
				const templateOptions = template.options || {};
				return cloneJson(templateOptions.raw || row.conditions && row.conditions.raw || {
					name: template.name || row.itemTemplateCode,
					type: template.itemType || null,
				});
			});

			return {
				id,
				code: boss.code,
				isSpecial: boss.bossType === "special",
				name: boss.name || raw.name || boss.code,
				title: summonRules.title || raw.title || boss.description || "",
				desc1: summonRules.desc1 || raw.desc1 || "",
				desc2: summonRules.desc2 || raw.desc2 || "",
				desc3: summonRules.desc3 || raw.desc3 || "",
				reqLvl: summonRules.reqLvl || raw.reqLvl || null,
				img: boss.imageUrl || raw.img || null,
				hasImage: !!boss.hasImage,
				maxHp: boss.hp,
				cooldownMs: raw.cooldownMs !== undefined && raw.cooldownMs !== null ? raw.cooldownMs : asMilliseconds(boss.cooldownSeconds),
				dropsList: cloneJson(summonRules.dropsList || raw.dropsList || []),
				drops,
				dropTableCode: table ? table.code : null,
				raw: cloneJson(raw),
			};
		});

		bosses.sort((a, b) => Number(a.id || 0) - Number(b.id || 0));
		return {
			bossList: bosses.filter((boss) => !boss.isSpecial),
			specialBossList: bosses.filter((boss) => boss.isSpecial),
		};
	}

	function buildFieldZones(payload) {
		return asArray(payload.fieldZones)
			.slice()
			.sort((a, b) => Number(a.sortOrder || 0) - Number(b.sortOrder || 0))
			.map((zone) => ({
				level: zone.sortOrder,
				code: zone.code,
				name: zone.name,
				enemyName: zone.description === zone.name ? "" : zone.description || "",
				maxHp: zone.enemyHp,
				goldReward: zone.goldReward,
				req: cloneJson(zone.entryRules || {}),
				farm: zone.farmRules && Object.keys(zone.farmRules).length ? cloneJson(zone.farmRules) : null,
				isEnabled: zone.isEnabled !== false,
			}));
	}

	function buildEnhancementRules(payload) {
		const apiRules = payload.enhancementRules || {};
		const groupRawRules = {};
		asArray(payload.enhancementGroups).forEach((group) => {
			groupRawRules[group.code] = group.rules && group.rules.raw ? cloneJson(group.rules.raw) : cloneJson(group.rules || {});
		});
		return {
			apiRules: cloneJson(apiRules),
			normalEquipment: groupRawRules.normal_equipment || null,
			talismanAndEmblem: groupRawRules.talisman_emblem || null,
			groups: cloneJson(payload.enhancementGroups || []),
			levels: cloneJson(payload.enhancementLevels || []),
		};
	}

	function createLegacyMasterDataFromPayload(apiResponseOrPayload) {
		const payload = unwrapPayload(apiResponseOrPayload);
		const characters = buildCharacterMasterData(payload);
		const skills = buildSkillMasterData(payload);
		const itemTemplateList = buildItemTemplateList(payload);
		const itemTemplateMap = mapBy(itemTemplateList, "templateKey");
		const dropTables = buildDropTables(payload);
		const bossLists = buildBossLists(payload);
		const fieldZones = buildFieldZones(payload);
		const defaultCharacterId = inferDefaultCharacterId(payload.characters, payload.characterSkills);

		return {
			createdAt: new Date().toISOString(),
			source: "api.master-data",
			assetPolicy: cloneJson(payload.assetPolicy || {}),
			counts: cloneJson(payload.counts || {}),
			defaultCharacterId,
			characterMasterData: characters,
			skillMasterData: skills,
			itemTemplateList,
			itemTemplateMap,
			dropTables,
			bossList: bossLists.bossList,
			specialBossList: bossLists.specialBossList,
			fieldZones,
			enhancementRules: buildEnhancementRules(payload),
			originalPayload: payload,
		};
	}

	function validateLegacyMasterData(legacyData) {
		const failures = [];
		const counts = {
			characters: Object.keys(legacyData.characterMasterData || {}).length,
			skills: Object.keys(legacyData.skillMasterData || {}).length,
			itemTemplates: asArray(legacyData.itemTemplateList).length,
			bosses: asArray(legacyData.bossList).length + asArray(legacyData.specialBossList).length,
			normalBosses: asArray(legacyData.bossList).length,
			specialBosses: asArray(legacyData.specialBossList).length,
			fieldZones: asArray(legacyData.fieldZones).length,
			dropTables: asArray(legacyData.dropTables).length,
		};

		if (!legacyData.defaultCharacterId) failures.push("defaultCharacterId가 없습니다.");
		if (counts.characters < 1) failures.push("캐릭터 데이터가 없습니다.");
		if (counts.skills < 8) failures.push("스킬 데이터가 8개 미만입니다.");
		if (counts.itemTemplates < 245) failures.push("아이템 템플릿이 245개 미만입니다.");
		if (counts.normalBosses < 39) failures.push("일반 보스가 39개 미만입니다.");
		if (counts.specialBosses < 6) failures.push("특수 보스가 6개 미만입니다.");
		if (counts.fieldZones < 40) failures.push("필드 구역이 40개 미만입니다.");
		if (legacyData.skillMasterData && legacyData.skillMasterData.lightsabre && legacyData.skillMasterData.lightsabre.baseProcRate !== null) {
			failures.push("lightsabre.baseProcRate는 null이어야 합니다.");
		}

		return {
			ok: failures.length === 0,
			counts,
			failures,
			hasInlineAsset: containsInlineDataUrl(legacyData),
		};
	}

	async function loadAdaptedMasterDataFromApi(options) {
		if (!window.RpgMasterDataBridge || typeof window.RpgMasterDataBridge.loadMasterDataFromApi !== "function") {
			throw new Error("RpgMasterDataBridge가 준비되지 않았습니다. master-data-bridge.js 로딩 순서를 확인하세요.");
		}

		const snapshot = await window.RpgMasterDataBridge.loadMasterDataFromApi(options || {});
		const legacyData = createLegacyMasterDataFromPayload(snapshot.payload);
		const validation = validateLegacyMasterData(legacyData);
		const adaptedSnapshot = {
			loadedAt: new Date().toISOString(),
			includeAssets: !!(options && options.includeAssets),
			apiSnapshot: snapshot,
			legacyData,
			validation,
		};

		window.backendAdaptedMasterDataSnapshot = adaptedSnapshot;
		return adaptedSnapshot;
	}

	async function checkBackendMasterDataAdapter(options) {
		const snapshot = await loadAdaptedMasterDataFromApi(options || {});
		const summary = {
			ok: snapshot.validation.ok,
			includeAssets: snapshot.includeAssets,
			counts: snapshot.validation.counts,
			failures: snapshot.validation.failures,
			hasInlineAsset: snapshot.validation.hasInlineAsset,
		};
		if (summary.ok) {
			console.log("[Upgrade RPG] master-data adapter check passed", summary);
		} else {
			console.warn("[Upgrade RPG] master-data adapter check failed", summary);
		}
		return summary;
	}

	function getCachedAdaptedMasterData() {
		return window.backendAdaptedMasterDataSnapshot || null;
	}

	window.RpgMasterDataAdapter = {
		unwrapPayload,
		containsInlineDataUrl,
		buildCharacterMasterData,
		buildSkillMasterData,
		buildItemTemplateList,
		buildDropTables,
		buildBossLists,
		buildFieldZones,
		buildEnhancementRules,
		createLegacyMasterDataFromPayload,
		validateLegacyMasterData,
		loadAdaptedMasterDataFromApi,
		checkBackendMasterDataAdapter,
		getCachedAdaptedMasterData,
	};

	window.loadAdaptedBackendMasterData = loadAdaptedMasterDataFromApi;
	window.checkBackendMasterDataAdapter = checkBackendMasterDataAdapter;
	window.getCachedAdaptedBackendMasterData = getCachedAdaptedMasterData;
})();
