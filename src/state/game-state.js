/**
 * game-state.js
 *
 * 백엔드 분리 준비 2차 정리 - 1순위 적용본
 * ------------------------------------------------------------
 * 기존 코드가 바로 깨지지 않도록 `player`, `currentZoneIndex` 같은 전역 이름은 유지합니다.
 * 대신 실제 데이터는 아래 3개 영역으로 나눠 보관합니다.
 *
 * 1) gameState.server
 *    - 나중에 PostgreSQL/FastAPI로 저장·불러오기 해야 하는 데이터
 *    - 예: player, 인벤토리, 장비, 스킬, 기록관, 필드 진행도, 보스 쿨타임
 *
 * 2) gameState.client
 *    - 브라우저 화면에서만 필요한 UI 상태
 *    - 예: 선택한 슬롯, 인벤토리/보스/필드 패널 열림 여부
 *
 * 3) gameState.runtime
 *    - 실행 중에만 필요한 임시 상태
 *    - 예: 현재 전투 중인 보스, 현재 몬스터 HP, 자동공격 타이머, 버프 상태
 *
 * 이후 FastAPI로 옮길 때는 gameState.server만 DB 저장 대상으로 보면 됩니다.
 */

function createDefaultPlayerState() {
	return {
		gold: 0,
		baseAttack: 1250,
		farmAtkBonus: 0,
		addAttackSpeed: 150,
		basicAtkDmgInc: 0,
		skillDmgInc: 0,
		allDmgInc: 0,
		addSkillAtkChance: 0,
		addSkillAtkMult: 0,
		basicCritChance: 0,
		basicCritDmg: 0,
		skillCritChance: 0,
		skillCritDmg: 0,
		equipment: new Array(15).fill(null),
		inventory: [],
		maxInventorySize: 60,
		storage: [],
		trash: [],
		mailbox: [],
		maxStorageSize: 60,

		// 현재 캐릭터 구조입니다.
		// 기존 코드 호환을 위해 player.skills는 유지하지만,
		// 실제 기준은 player.userCharacters[currentCharacterId].skills 입니다.
		currentCharacterId: typeof getDefaultCharacterId === "function" ? getDefaultCharacterId() : "weapon_master",
		ownedCharacterIds: [typeof getDefaultCharacterId === "function" ? getDefaultCharacterId() : "weapon_master"],
		userCharacters: (() => {
			const characterId = typeof getDefaultCharacterId === "function" ? getDefaultCharacterId() : "weapon_master";
			const skills = typeof createDefaultCharacterSkillState === "function" ? createDefaultCharacterSkillState(characterId) : {
				lightsabre: { level: 1, isUpgraded: false },
				ironStrike: { level: 0, isUpgraded: false },
				overdrive: { level: 0 },
				baldo: { level: 0 },
				illusionSword: { level: 0 },
				deepSword: { level: 0 },
				tempestStrike: { level: 0 },
				heavenlyStrike: { level: 0, lastUsed: 0 },
			};
			return { [characterId]: { characterId, skills } };
		})(),
		skills: typeof createDefaultCharacterSkillState === "function"
			? createDefaultCharacterSkillState(typeof getDefaultCharacterId === "function" ? getDefaultCharacterId() : "weapon_master")
			: {
				lightsabre: { level: 1, isUpgraded: false },
				ironStrike: { level: 0, isUpgraded: false },
				overdrive: { level: 0 },
				baldo: { level: 0 },
				illusionSword: { level: 0 },
				deepSword: { level: 0 },
				tempestStrike: { level: 0 },
				heavenlyStrike: { level: 0, lastUsed: 0 },
			},

		specialBossCD: {},
		firstEquipSkillDropGiven: {},
		records: {
			playTimeMs: 0,
			totalGoldEarned: 0,
			totalMonsterKills: 0,
			totalBossKills: 0,
			monsterKillsByName: {},
			bossKillsByName: {},
			enhanceFailByItem: {},
			collection: {},
			itemDropsByName: {},
			itemDryStreakByName: {},
		},
	};
}

function createDefaultServerState() {
	return {
		player: createDefaultPlayerState(),
		progress: {
			currentZoneIndex: 0,
			currentZoneType: "field",
			fieldEnemyHp: {},
			fieldRespawnEndAt: {},
		},
	};
}

function createDefaultClientState() {
	return {
		selectedSlot: { type: null, index: -1 },
		panels: {
			isInvOpen: false,
			isBossPanelOpen: false,
			isSpecialBossPanelOpen: false,
			isFieldPanelOpen: false,
		},
	};
}

function createDefaultRuntimeState() {
	return {
		activeBuffs: {
			ironStrike: { active: false, timer: 0 },
			overdrive: { active: false, timer: 0 },
		},
		combat: {
			isFightingBoss: false,
			currentBossHp: 0,
			currentBoss: null,
			lastSummonedBoss: null,
			autoBossSummon: false,
			specialBossReturnState: null,
			autoSpecialBossEnabled: false,
			autoSpecialBossId: null,
			autoSpecialBossInProgress: false,
			equipDropEnabled: true,
			attackInterval: null,
		},
		field: {
			currentEnemy: { hp: 0 },
		},
	};
}

const gameState = {
	server: createDefaultServerState(),
	client: createDefaultClientState(),
	runtime: createDefaultRuntimeState(),
};

window.gameState = gameState;

function bindStateAlias(name, target, key) {
	Object.defineProperty(window, name, {
		configurable: true,
		get() {
			return target[key];
		},
		set(value) {
			target[key] = value;
		},
	});
}

function bindNestedStateAlias(name, root, path) {
	Object.defineProperty(window, name, {
		configurable: true,
		get() {
			return path.reduce((acc, cur) => (acc ? acc[cur] : undefined), root);
		},
		set(value) {
			let target = root;
			for (let i = 0; i < path.length - 1; i++) target = target[path[i]];
			target[path[path.length - 1]] = value;
		},
	});
}

// 기존 코드 호환용 전역 이름입니다. 실제 저장 위치는 gameState 내부입니다.
bindStateAlias("player", gameState.server, "player");
bindNestedStateAlias("currentZoneIndex", gameState, ["server", "progress", "currentZoneIndex"]);
bindNestedStateAlias("currentZoneType", gameState, ["server", "progress", "currentZoneType"]);
bindNestedStateAlias("fieldEnemyHp", gameState, ["server", "progress", "fieldEnemyHp"]);
bindNestedStateAlias("fieldRespawnEndAt", gameState, ["server", "progress", "fieldRespawnEndAt"]);

bindNestedStateAlias("selectedSlot", gameState, ["client", "selectedSlot"]);
bindNestedStateAlias("isInvOpen", gameState, ["client", "panels", "isInvOpen"]);
bindNestedStateAlias("isBossPanelOpen", gameState, ["client", "panels", "isBossPanelOpen"]);
bindNestedStateAlias("isSpecialBossPanelOpen", gameState, ["client", "panels", "isSpecialBossPanelOpen"]);
bindNestedStateAlias("isFieldPanelOpen", gameState, ["client", "panels", "isFieldPanelOpen"]);

bindNestedStateAlias("activeBuffs", gameState, ["runtime", "activeBuffs"]);
bindNestedStateAlias("isFightingBoss", gameState, ["runtime", "combat", "isFightingBoss"]);
bindNestedStateAlias("currentBossHp", gameState, ["runtime", "combat", "currentBossHp"]);
bindNestedStateAlias("currentBoss", gameState, ["runtime", "combat", "currentBoss"]);
bindNestedStateAlias("lastSummonedBoss", gameState, ["runtime", "combat", "lastSummonedBoss"]);
bindNestedStateAlias("autoBossSummon", gameState, ["runtime", "combat", "autoBossSummon"]);
bindNestedStateAlias("specialBossReturnState", gameState, ["runtime", "combat", "specialBossReturnState"]);
bindNestedStateAlias("autoSpecialBossEnabled", gameState, ["runtime", "combat", "autoSpecialBossEnabled"]);
bindNestedStateAlias("autoSpecialBossId", gameState, ["runtime", "combat", "autoSpecialBossId"]);
bindNestedStateAlias("autoSpecialBossInProgress", gameState, ["runtime", "combat", "autoSpecialBossInProgress"]);
bindNestedStateAlias("equipDropEnabled", gameState, ["runtime", "combat", "equipDropEnabled"]);
bindNestedStateAlias("attackInterval", gameState, ["runtime", "combat", "attackInterval"]);
bindNestedStateAlias("currentEnemy", gameState, ["runtime", "field", "currentEnemy"]);

function countOccupiedItemSlots(items) {
	if (!Array.isArray(items)) return 0;
	return items.reduce((count, item) => count + (item ? 1 : 0), 0);
}

function trimTrailingEmptyItemSlots(items) {
	if (!Array.isArray(items)) return items;
	while (items.length > 0 && !items[items.length - 1]) items.pop();
	return items;
}

function findFirstEmptyItemSlot(items, maxSize) {
	if (!Array.isArray(items)) return -1;
	const safeMaxSize = Math.max(0, parseInt(maxSize) || 0);
	for (let index = 0; index < safeMaxSize; index++) {
		if (!items[index]) return index;
	}
	return -1;
}

function hasEmptyItemSlot(items, maxSize) {
	return findFirstEmptyItemSlot(items, maxSize) !== -1;
}

function placeItemInFirstEmptySlot(items, item, maxSize) {
	if (!item || !Array.isArray(items)) return -1;
	const index = findFirstEmptyItemSlot(items, maxSize);
	if (index === -1) return -1;
	items[index] = item;
	return index;
}

function clearItemSlot(items, index) {
	if (!Array.isArray(items) || index < 0 || !items[index]) return null;
	const item = items[index];
	items[index] = null;
	trimTrailingEmptyItemSlots(items);
	return item;
}

function compactItemSlots(items) {
	if (!Array.isArray(items)) return { moved: 0, occupied: 0 };
	const occupiedItems = items.filter(Boolean);
	let moved = 0;
	occupiedItems.forEach((item, index) => {
		if (items[index] !== item) moved++;
	});
	items.splice(0, items.length, ...occupiedItems);
	return { moved, occupied: occupiedItems.length };
}

function ensurePlayerStateShape(targetPlayer = player) {
	const defaults = createDefaultPlayerState();
	if (!targetPlayer || typeof targetPlayer !== "object") targetPlayer = {};

	Object.keys(defaults).forEach((key) => {
		if (targetPlayer[key] === undefined || targetPlayer[key] === null) {
			targetPlayer[key] = Array.isArray(defaults[key]) ? [...defaults[key]] : defaults[key];
		}
	});

	if (!Array.isArray(targetPlayer.equipment) || targetPlayer.equipment.length < 15) {
		const nextEquipment = new Array(15).fill(null);
		if (Array.isArray(targetPlayer.equipment)) {
			for (let i = 0; i < targetPlayer.equipment.length; i++) nextEquipment[i] = targetPlayer.equipment[i] || null;
		}
		targetPlayer.equipment = nextEquipment;
	}

	["inventory", "storage", "trash", "mailbox"].forEach((key) => {
		if (!Array.isArray(targetPlayer[key])) targetPlayer[key] = [];
	});

	if (!targetPlayer.maxInventorySize || targetPlayer.maxInventorySize < 60) targetPlayer.maxInventorySize = 60;
	if (!targetPlayer.maxStorageSize || targetPlayer.maxStorageSize < 60) targetPlayer.maxStorageSize = 60;

	if (typeof normalizePlayerCharacterState === "function") {
		normalizePlayerCharacterState(targetPlayer);
	} else {
		if (!targetPlayer.skills || typeof targetPlayer.skills !== "object") targetPlayer.skills = {};
		Object.keys(defaults.skills).forEach((skillKey) => {
			if (!targetPlayer.skills[skillKey]) targetPlayer.skills[skillKey] = { ...defaults.skills[skillKey] };
		});
	}

	if (!targetPlayer.specialBossCD || typeof targetPlayer.specialBossCD !== "object") targetPlayer.specialBossCD = {};
	if (!targetPlayer.firstEquipSkillDropGiven || typeof targetPlayer.firstEquipSkillDropGiven !== "object") targetPlayer.firstEquipSkillDropGiven = {};
	if (!targetPlayer.records || typeof targetPlayer.records !== "object") targetPlayer.records = {};

	const recordDefaults = defaults.records;
	Object.keys(recordDefaults).forEach((key) => {
		if (targetPlayer.records[key] === undefined || targetPlayer.records[key] === null) {
			targetPlayer.records[key] = typeof recordDefaults[key] === "object" ? { ...recordDefaults[key] } : recordDefaults[key];
		}
	});

	return targetPlayer;
}

function ensureProgressStateShape(progress = gameState.server.progress) {
	if (!progress || typeof progress !== "object") progress = {};
	if (progress.currentZoneIndex === undefined || progress.currentZoneIndex === null) progress.currentZoneIndex = 0;
	if (!progress.currentZoneType) progress.currentZoneType = "field";
	if (!progress.fieldEnemyHp || typeof progress.fieldEnemyHp !== "object") progress.fieldEnemyHp = {};
	if (!progress.fieldRespawnEndAt || typeof progress.fieldRespawnEndAt !== "object") progress.fieldRespawnEndAt = {};
	gameState.server.progress = progress;
	return progress;
}

function ensureGameStateShape() {
	gameState.server.player = ensurePlayerStateShape(gameState.server.player);
	ensureProgressStateShape(gameState.server.progress);
	if (!gameState.client || typeof gameState.client !== "object") gameState.client = createDefaultClientState();
	if (!gameState.runtime || typeof gameState.runtime !== "object") gameState.runtime = createDefaultRuntimeState();
	return gameState;
}

function getServerSavePayload(saveVersion) {
	ensureGameStateShape();
	return {
		saveVersion,
		player: gameState.server.player,
		currentZoneIndex: gameState.server.progress.currentZoneIndex,
		currentZoneType: gameState.server.progress.currentZoneType,
		fieldEnemyHp: gameState.server.progress.fieldEnemyHp,
		fieldRespawnEndAt: gameState.server.progress.fieldRespawnEndAt,
	};
}

function applyServerSavePayload(data) {
	if (!data || typeof data !== "object") return;
	gameState.server.player = ensurePlayerStateShape({ ...createDefaultPlayerState(), ...(data.player || {}) });
	gameState.server.progress = ensureProgressStateShape({
		currentZoneIndex: parseInt(data.currentZoneIndex) || 0,
		currentZoneType: data.currentZoneType || "field",
		fieldEnemyHp: data.fieldEnemyHp && typeof data.fieldEnemyHp === "object" ? data.fieldEnemyHp : {},
		fieldRespawnEndAt: data.fieldRespawnEndAt && typeof data.fieldRespawnEndAt === "object" ? data.fieldRespawnEndAt : {},
	});
}

function resetRuntimeState() {
	const defaults = createDefaultRuntimeState();
	gameState.runtime.activeBuffs = defaults.activeBuffs;
	gameState.runtime.combat = defaults.combat;
	gameState.runtime.field = defaults.field;
}

function getStateSplitDebugSnapshot() {
	return {
		server: gameState.server,
		client: gameState.client,
		runtime: gameState.runtime,
	};
}

const skillBookMapping = typeof createSkillBookMapping === "function" ? createSkillBookMapping() : {
	스킬강화권: "lightsabre",
	"강력한 스킬강화권": "ironStrike",
	"빛나는 스킬강화권": "overdrive",
	"화려한 스킬강화권": "baldo",
	"찬란한 스킬강화권": "illusionSword",
	"해방된 스킬강화권": "deepSword",
	"천공의 스킬강화권": "tempestStrike",
	"심연의 스킬강화권": "lightsabre",
	"-초월- 심연의 스킬강화권": "ironStrike",
	"-초월-심연의 스킬강화권": "ironStrike",
	"진 각성 스킬강화권": "heavenlyStrike",
};
