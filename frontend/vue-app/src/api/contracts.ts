export interface ApiErrorBody {
  code?: string;
  message?: string;
  details?: Record<string, unknown>;
}

export interface ApiEnvelope<TPayload = Record<string, unknown>, TData = Record<string, unknown>> {
  ok: boolean;
  responseVersion: string;
  type: string;
  requestId: string;
  payload: TPayload;
  data: TData;
  meta: Record<string, unknown>;
  error: ApiErrorBody | null;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string | null;
  emailVerified: boolean;
  isAdmin: boolean;
  isActive?: boolean;
}

export interface LoginPayload {
  status: 'authenticated';
  accessToken: string;
  tokenType: 'bearer';
  expiresIn: number;
  user: AuthUser;
}

export interface AuthUserPayload {
  status: 'authenticated';
  user: AuthUser;
}

export interface RegisterPayload {
  status: 'verification_required';
  accessTokenIssued: false;
  user: AuthUser;
}

export interface AccountCharacterMetadata {
  id: string;
  slotIndex: number;
  name: string;
  characterCode: string;
  createdAt: string;
}

export interface AccountCharacterProgress {
  saveVersion: number | null;
  gold: number | string | null;
  level: number | null;
  currentZoneIndex: number | null;
  currentZoneType: string | null;
  updatedAt: string | null;
}

export interface AccountCharacterSlot {
  slotIndex: number;
  slotKey: `character-${number}`;
  occupied: boolean;
  unavailable?: boolean;
  accountCharacterId: string | null;
  accountCharacter: AccountCharacterMetadata | null;
  progress: AccountCharacterProgress | null;
}

export interface GameSaveIntegrity {
  algorithm?: string;
  snapshotSha256?: string;
  snapshotBytes?: number;
  saveVersion?: number | null;
  snapshotSaveVersion?: unknown;
  clientSaveKey?: string | null;
  slotKey?: string;
  summaryKeys?: string[];
  counts?: Record<string, number>;
  warnings: string[];
  ok: boolean;
}

export interface GameLoadPayload {
  userId: number;
  slotKey: `character-${number}`;
  slotIndex: number;
  accountCharacterId: string;
  accountCharacter: AccountCharacterMetadata;
  status: 'loaded';
  exists: boolean;
  clientSaveKey: string | null;
  saveVersion: number | null;
  snapshot: Record<string, unknown> | null;
  summary: Record<string, unknown> | null;
  source: string | null;
  note: string | null;
  integrity: GameSaveIntegrity | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface GameLoadData {
  status: 'loaded';
  userId: number;
  slotKey: `character-${number}`;
  accountCharacterId: string;
  exists: boolean;
  integrity: GameSaveIntegrity | null;
}

export interface GameSaveRequestBody extends Record<string, unknown> {
  accountCharacterId: string;
  slotKey: `character-${number}`;
  saveVersion: number;
  clientSaveKey: string;
  snapshot: Record<string, unknown>;
  summary: Record<string, unknown>;
  source: string;
  note: string | null;
}

export interface GameSavePayload extends Omit<GameLoadPayload, 'status'> {
  status: 'saved';
}

export interface GameSaveData {
  status: 'saved';
  userId: number;
  slotKey: `character-${number}`;
  accountCharacterId: string;
  saveVersion: number;
  integrity: GameSaveIntegrity | null;
}

export interface AccountCharactersPayload {
  status: 'loaded';
  slotCount: 8;
  occupiedCount: number;
  slots: AccountCharacterSlot[];
}

export interface CharacterOption {
  code: string;
  name: string;
  description?: string | null;
  isEnabled: boolean;
}

export interface FieldZoneOption {
  code: string;
  name: string;
  sortOrder: number;
  enemyHp: number | string;
  goldReward: number | string;
  description?: string | null;
  entryRules?: Record<string, unknown> | null;
  farmRules?: Record<string, unknown> | null;
  isEnabled: boolean;
}

export interface ItemTemplateOption {
  code: string;
  name: string;
  itemType: string;
  grade?: string | null;
  iconUrl?: string | null;
  hasIcon?: boolean;
  description?: string | null;
  stackable: boolean;
  equipSlot?: string | number | null;
  enhanceGroupCode?: string | null;
  baseStats?: Record<string, unknown> | null;
  options?: Record<string, unknown> | null;
  adminNote?: string | null;
}

export interface BossOption {
  code: string;
  name: string;
  tier: number | null;
  bossType: 'normal' | 'special';
  hp: number | string;
  imageUrl?: string | null;
  hasImage?: boolean;
  description?: string | null;
  summonRules?: Record<string, unknown> | null;
  cooldownSeconds: number;
  isEnabled: boolean;
}

export interface SkillOption {
  code: string;
  name: string;
  slotKey: string;
  description?: string | null;
  iconUrl?: string | null;
  hasIcon?: boolean;
  procRate?: number | string | null;
  cooldownSeconds?: number | null;
  options?: Record<string, unknown> | null;
}

export interface CharacterSkillOption {
  characterCode: string;
  skillCode: string;
  sortOrder: number;
  isDefault: boolean;
}

export interface SkillLevelOption {
  skillCode: string;
  level: number;
  damageMultiplier: number | string;
  procRateBonus: number | string;
  options?: Record<string, unknown> | null;
}

export interface EnhancementGroupOption {
  code: string;
  name: string;
  description?: string | null;
  maxLevel: number;
  rules?: Record<string, unknown> | null;
  isEnabled: boolean;
}

export interface EnhancementLevelOption {
  groupCode: string;
  fromLevel: number;
  toLevel: number;
  successRate: number | string;
  goldCost: number | string;
  materialRules?: Record<string, unknown> | null;
  resultStats?: Record<string, unknown> | null;
  failRules?: Record<string, unknown> | null;
}

export interface MasterDataCharacterPayload {
  characters: CharacterOption[];
  fieldZones?: FieldZoneOption[];
  bosses?: BossOption[];
  itemTemplates?: ItemTemplateOption[];
  skills?: SkillOption[];
  characterSkills?: CharacterSkillOption[];
  skillLevels?: SkillLevelOption[];
  enhancementGroups?: EnhancementGroupOption[];
  enhancementLevels?: EnhancementLevelOption[];
}
