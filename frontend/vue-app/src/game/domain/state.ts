import type {
  CharacterSkillMap,
  DomainRecord,
  GameClientState,
  GameProgressState,
  GameRuntimeState,
  GameServerState,
  GameState,
  PlayerRecords,
  PlayerState,
  ServerSavePayload,
} from './types';

export const DEFAULT_CHARACTER_ID = 'weapon_master';
export const EQUIPMENT_SLOT_COUNT = 15;
export const MIN_ITEM_CONTAINER_SIZE = 60;

export interface PlayerFactoryOptions {
  defaultCharacterId?: string;
  createSkillState?: (characterId: string) => CharacterSkillMap;
}

export function cloneDomainValue<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => cloneDomainValue(item)) as T;
  if (isRecord(value)) {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, cloneDomainValue(item)])) as T;
  }
  return value;
}

export function createDefaultSkillState(): CharacterSkillMap {
  return {
    lightsabre: { level: 1, isUpgraded: false },
    ironStrike: { level: 0, isUpgraded: false },
    overdrive: { level: 0 },
    baldo: { level: 0 },
    illusionSword: { level: 0 },
    deepSword: { level: 0 },
    tempestStrike: { level: 0 },
    heavenlyStrike: { level: 0, lastUsed: 0 },
  };
}

export function createDefaultPlayerRecords(): PlayerRecords {
  return {
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
  };
}

export function createDefaultPlayerState(options: PlayerFactoryOptions = {}): PlayerState {
  const characterId = options.defaultCharacterId || DEFAULT_CHARACTER_ID;
  const createSkills = options.createSkillState || (() => createDefaultSkillState());
  const characterSkills = cloneDomainValue(createSkills(characterId));
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
    equipment: new Array(EQUIPMENT_SLOT_COUNT).fill(null),
    inventory: [],
    maxInventorySize: MIN_ITEM_CONTAINER_SIZE,
    storage: [],
    trash: [],
    mailbox: [],
    maxStorageSize: MIN_ITEM_CONTAINER_SIZE,
    currentCharacterId: characterId,
    ownedCharacterIds: [characterId],
    userCharacters: {
      [characterId]: { characterId, skills: cloneDomainValue(characterSkills) },
    },
    skills: cloneDomainValue(characterSkills),
    specialBossCD: {},
    firstEquipSkillDropGiven: {},
    records: createDefaultPlayerRecords(),
  };
}

export function createDefaultProgressState(): GameProgressState {
  return {
    currentZoneIndex: 0,
    currentZoneType: 'field',
    fieldEnemyHp: {},
    fieldRespawnEndAt: {},
  };
}

export function createDefaultServerState(options: PlayerFactoryOptions = {}): GameServerState {
  return { player: createDefaultPlayerState(options), progress: createDefaultProgressState() };
}

export function createDefaultClientState(): GameClientState {
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

export function createDefaultRuntimeState(): GameRuntimeState {
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
    field: { currentEnemy: { hp: 0 } },
  };
}

export function createDefaultGameState(options: PlayerFactoryOptions = {}): GameState {
  return {
    server: createDefaultServerState(options),
    client: createDefaultClientState(),
    runtime: createDefaultRuntimeState(),
  };
}

export function normalizePlayerState(input: unknown, options: PlayerFactoryOptions = {}): PlayerState {
  const defaults = createDefaultPlayerState(options);
  const source = isRecord(input) ? cloneDomainValue(input) : {};
  const result = { ...defaults, ...source } as PlayerState;

  for (const [key, value] of Object.entries(defaults)) {
    if (result[key] === undefined || result[key] === null) result[key] = cloneDomainValue(value);
  }

  const equipment = Array.isArray(source.equipment) ? [...source.equipment] : [];
  if (equipment.length < EQUIPMENT_SLOT_COUNT) equipment.push(...new Array(EQUIPMENT_SLOT_COUNT - equipment.length).fill(null));
  result.equipment = equipment.map((item) => item || null);

  for (const key of ['inventory', 'storage', 'trash', 'mailbox'] as const) {
    result[key] = Array.isArray(source[key]) ? [...source[key]] : [];
  }

  result.maxInventorySize = normalizeContainerSize(source.maxInventorySize);
  result.maxStorageSize = normalizeContainerSize(source.maxStorageSize);
  result.skills = mergeSkillDefaults(source.skills, defaults.skills);
  result.specialBossCD = isRecord(source.specialBossCD) ? source.specialBossCD as Record<string, number> : {};
  result.firstEquipSkillDropGiven = isRecord(source.firstEquipSkillDropGiven) ? source.firstEquipSkillDropGiven as Record<string, boolean> : {};
  result.records = normalizePlayerRecords(source.records, defaults.records);
  return result;
}

export function normalizeProgressState(input: unknown): GameProgressState {
  const source = isRecord(input) ? cloneDomainValue(input) : {};
  return {
    ...source,
    currentZoneIndex: source.currentZoneIndex === undefined || source.currentZoneIndex === null ? 0 : Number(source.currentZoneIndex),
    currentZoneType: String(source.currentZoneType || 'field'),
    fieldEnemyHp: isRecord(source.fieldEnemyHp) ? source.fieldEnemyHp as Record<string, number> : {},
    fieldRespawnEndAt: isRecord(source.fieldRespawnEndAt) ? source.fieldRespawnEndAt as Record<string, number> : {},
  };
}

export function normalizeGameState(input: unknown, options: PlayerFactoryOptions = {}): GameState {
  const source = isRecord(input) ? cloneDomainValue(input) : {};
  const server = isRecord(source.server) ? source.server : {};
  return {
    server: {
      ...server,
      player: normalizePlayerState(server.player, options),
      progress: normalizeProgressState(server.progress),
    },
    client: isClientState(source.client) ? cloneDomainValue(source.client) : createDefaultClientState(),
    runtime: isRuntimeState(source.runtime) ? cloneDomainValue(source.runtime) : createDefaultRuntimeState(),
  };
}

export function createServerSavePayload(server: GameServerState, saveVersion: string | number): ServerSavePayload {
  const normalized = {
    player: normalizePlayerState(server.player),
    progress: normalizeProgressState(server.progress),
  };
  return cloneDomainValue({
    saveVersion,
    player: normalized.player,
    currentZoneIndex: normalized.progress.currentZoneIndex,
    currentZoneType: normalized.progress.currentZoneType,
    fieldEnemyHp: normalized.progress.fieldEnemyHp,
    fieldRespawnEndAt: normalized.progress.fieldRespawnEndAt,
  });
}

export function applyServerSavePayload(input: unknown, options: PlayerFactoryOptions = {}): GameServerState {
  const source = isRecord(input) ? input : {};
  const defaultPlayer = createDefaultPlayerState(options);
  const playerInput = isRecord(source.player) ? { ...defaultPlayer, ...source.player } : defaultPlayer;
  return {
    player: normalizePlayerState(playerInput, options),
    progress: normalizeProgressState({
      currentZoneIndex: toIntegerOrZero(source.currentZoneIndex),
      currentZoneType: source.currentZoneType || 'field',
      fieldEnemyHp: isRecord(source.fieldEnemyHp) ? source.fieldEnemyHp : {},
      fieldRespawnEndAt: isRecord(source.fieldRespawnEndAt) ? source.fieldRespawnEndAt : {},
    }),
  };
}

function normalizePlayerRecords(input: unknown, defaults: PlayerRecords): PlayerRecords {
  const source = isRecord(input) ? input : {};
  const result = { ...defaults, ...source } as PlayerRecords;
  for (const [key, value] of Object.entries(defaults)) {
    if (result[key] === undefined || result[key] === null) result[key] = cloneDomainValue(value);
  }
  return result;
}

function mergeSkillDefaults(input: unknown, defaults: CharacterSkillMap): CharacterSkillMap {
  const source = isRecord(input) ? cloneDomainValue(input) : {};
  const result = source as CharacterSkillMap;
  for (const [key, value] of Object.entries(defaults)) {
    if (!isRecord(result[key])) result[key] = cloneDomainValue(value);
  }
  return result;
}

function normalizeContainerSize(value: unknown) {
  const parsed = Number.parseInt(String(value ?? ''), 10);
  return Number.isFinite(parsed) && parsed >= MIN_ITEM_CONTAINER_SIZE ? parsed : MIN_ITEM_CONTAINER_SIZE;
}

function toIntegerOrZero(value: unknown) {
  const parsed = Number.parseInt(String(value ?? ''), 10);
  return Number.isFinite(parsed) ? parsed : 0;
}

function isClientState(value: unknown): value is GameClientState {
  return isRecord(value) && isRecord(value.selectedSlot) && isRecord(value.panels);
}

function isRuntimeState(value: unknown): value is GameRuntimeState {
  return isRecord(value) && isRecord(value.activeBuffs) && isRecord(value.combat) && isRecord(value.field);
}

function isRecord(value: unknown): value is DomainRecord {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
