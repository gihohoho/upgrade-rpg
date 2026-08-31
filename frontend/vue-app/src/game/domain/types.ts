export type DomainRecord = Record<string, unknown>;
export type ItemSlot<T> = T | null | undefined;

export interface GameItem extends DomainRecord {
  id?: string | number;
  name?: string;
  type?: string;
  level?: number;
  count?: number;
}

export interface CharacterSkillState extends DomainRecord {
  level: number;
  isUpgraded?: boolean;
  lastUsed?: number;
}

export type CharacterSkillMap = Record<string, CharacterSkillState>;

export interface UserCharacterState extends DomainRecord {
  characterId: string;
  skills: CharacterSkillMap;
}

export interface PlayerRecords extends DomainRecord {
  playTimeMs: number;
  totalGoldEarned: number;
  totalMonsterKills: number;
  totalBossKills: number;
  monsterKillsByName: Record<string, number>;
  bossKillsByName: Record<string, number>;
  enhanceFailByItem: Record<string, number>;
  collection: DomainRecord;
  itemDropsByName: Record<string, number>;
  itemDryStreakByName: Record<string, number>;
}

export interface PlayerState extends DomainRecord {
  gold: number;
  baseAttack: number;
  farmAtkBonus: number;
  addAttackSpeed: number;
  basicAtkDmgInc: number;
  skillDmgInc: number;
  allDmgInc: number;
  addSkillAtkChance: number;
  addSkillAtkMult: number;
  basicCritChance: number;
  basicCritDmg: number;
  skillCritChance: number;
  skillCritDmg: number;
  equipment: ItemSlot<GameItem>[];
  inventory: ItemSlot<GameItem>[];
  maxInventorySize: number;
  storage: ItemSlot<GameItem>[];
  trash: ItemSlot<GameItem>[];
  mailbox: ItemSlot<GameItem>[];
  maxStorageSize: number;
  currentCharacterId: string;
  ownedCharacterIds: string[];
  userCharacters: Record<string, UserCharacterState>;
  skills: CharacterSkillMap;
  specialBossCD: Record<string, number>;
  firstEquipSkillDropGiven: Record<string, boolean>;
  records: PlayerRecords;
}

export interface GameProgressState extends DomainRecord {
  currentZoneIndex: number;
  currentZoneType: string;
  fieldEnemyHp: Record<string, number>;
  fieldRespawnEndAt: Record<string, number>;
}

export interface GameServerState extends DomainRecord {
  player: PlayerState;
  progress: GameProgressState;
}

export interface SelectedItemSlot {
  type: string | null;
  index: number;
}

export interface GameClientState {
  selectedSlot: SelectedItemSlot;
  panels: {
    isInvOpen: boolean;
    isBossPanelOpen: boolean;
    isSpecialBossPanelOpen: boolean;
    isFieldPanelOpen: boolean;
  };
}

export interface GameRuntimeState {
  activeBuffs: {
    ironStrike: { active: boolean; timer: number };
    overdrive: { active: boolean; timer: number };
  };
  combat: {
    isFightingBoss: boolean;
    currentBossHp: number;
    currentBoss: DomainRecord | null;
    lastSummonedBoss: DomainRecord | null;
    autoBossSummon: boolean;
    specialBossReturnState: DomainRecord | null;
    autoSpecialBossEnabled: boolean;
    autoSpecialBossId: number | null;
    autoSpecialBossInProgress: boolean;
    equipDropEnabled: boolean;
    attackInterval: number | null;
  };
  field: {
    currentEnemy: { hp: number };
  };
}

export interface GameState {
  server: GameServerState;
  client: GameClientState;
  runtime: GameRuntimeState;
}

export interface ServerSavePayload extends DomainRecord {
  saveVersion: string | number;
  player: PlayerState;
  currentZoneIndex: number;
  currentZoneType: string;
  fieldEnemyHp: Record<string, number>;
  fieldRespawnEndAt: Record<string, number>;
}

export interface GameActionLog {
  message: string;
  important: boolean;
}

export interface GameActionEffect extends DomainRecord {
  type: string;
}

export interface GameActionResult<TPayload extends DomainRecord = DomainRecord> {
  ok: boolean;
  type: string;
  payload: TPayload;
  logs: GameActionLog[];
  effects: GameActionEffect[];
  ui: DomainRecord;
  data: DomainRecord;
  createdAt: number;
}
