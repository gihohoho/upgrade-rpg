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

export interface MasterDataCharacterPayload {
  characters: CharacterOption[];
  fieldZones?: FieldZoneOption[];
  bosses?: BossOption[];
}
