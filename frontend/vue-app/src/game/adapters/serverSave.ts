import type { GameSaveRequestBody } from '@/api/contracts';
import {
  cloneDomainValue,
  createServerSavePayload,
  type GameServerState,
} from '@/game/domain';
import type { SelectedCharacterIdentity } from './serverSnapshot';

export type GameSaveReason = 'auto' | 'manual' | 'character-switch' | 'logout';

export interface SelectedCharacterSaveSource extends SelectedCharacterIdentity {
  userId: number;
  saveVersion: number | null;
  serverState: GameServerState;
}

export interface AcceptedGameSave {
  slotKey: `character-${number}`;
  accountCharacterId: string;
  saveVersion: number;
  updatedAt: string | null;
  integrityOk: boolean | null;
}

export class GameSaveContractError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GameSaveContractError';
  }
}

const SAVE_REASON_META: Record<GameSaveReason, { source: string; note: string }> = {
  auto: { source: 'vue-auto-save', note: 'Vue 60초 자동 저장' },
  manual: { source: 'vue-manual-save', note: '사용자가 실행한 Vue 수동 저장' },
  'character-switch': { source: 'vue-character-switch', note: 'Vue 캐릭터 전환 전 최종 저장' },
  logout: { source: 'vue-account-logout', note: 'Vue 로그아웃 전 최종 저장' },
};

export function createSelectedCharacterSaveRequest(
  source: SelectedCharacterSaveSource,
  reason: GameSaveReason,
  createdAt = new Date().toISOString(),
): GameSaveRequestBody {
  const saveVersion = normalizeSaveVersion(source.saveVersion);
  const snapshot = createServerSavePayload(source.serverState, saveVersion);
  if (snapshot.player.currentCharacterId !== source.characterCode) {
    throw new GameSaveContractError('저장할 캐릭터 종류가 현재 선택과 일치하지 않습니다.');
  }
  const meta = SAVE_REASON_META[reason];
  return cloneDomainValue({
    accountCharacterId: source.accountCharacterId,
    slotKey: source.slotKey,
    saveVersion,
    clientSaveKey: `upgradeRpgVue:${source.userId}:${source.accountCharacterId}`,
    snapshot,
    summary: {
      saveVersion,
      gold: snapshot.player.gold,
      level: readNonNegativeInteger(snapshot.player.level),
      currentCharacterId: snapshot.player.currentCharacterId,
      currentZoneIndex: snapshot.currentZoneIndex,
      currentZoneType: snapshot.currentZoneType,
      inventoryItems: countFilled(snapshot.player.inventory),
      storageItems: countFilled(snapshot.player.storage),
      trashItems: countFilled(snapshot.player.trash),
      mailboxItems: countFilled(snapshot.player.mailbox),
      createdAt,
    },
    source: meta.source,
    note: meta.note,
  });
}

export function acceptSelectedCharacterSave(
  payload: unknown,
  expected: SelectedCharacterIdentity,
): AcceptedGameSave {
  if (!isRecord(payload) || payload.status !== 'saved' || payload.exists !== true) {
    throw new GameSaveContractError('서버 저장 응답이 완전하지 않습니다.');
  }
  if (payload.slotKey !== expected.slotKey || payload.accountCharacterId !== expected.accountCharacterId) {
    throw new GameSaveContractError('서버 저장 응답의 캐릭터 식별 정보가 현재 선택과 일치하지 않습니다.');
  }
  const accountCharacter = payload.accountCharacter;
  if (!isRecord(accountCharacter)
    || accountCharacter.id !== expected.accountCharacterId
    || accountCharacter.characterCode !== expected.characterCode) {
    throw new GameSaveContractError('서버 저장 응답의 캐릭터 정보가 현재 선택과 일치하지 않습니다.');
  }
  const saveVersion = normalizeSaveVersion(payload.saveVersion);
  return {
    slotKey: expected.slotKey,
    accountCharacterId: expected.accountCharacterId,
    saveVersion,
    updatedAt: nullableString(payload.updatedAt),
    integrityOk: isRecord(payload.integrity) && typeof payload.integrity.ok === 'boolean'
      ? payload.integrity.ok
      : null,
  };
}

export function cloneSelectedCharacterSaveRequest(request: GameSaveRequestBody): GameSaveRequestBody {
  return cloneDomainValue(request);
}

function normalizeSaveVersion(value: unknown): number {
  if (value === null || value === undefined) return 0;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 0 || parsed > 999) {
    throw new GameSaveContractError('저장 버전 형식이 올바르지 않습니다.');
  }
  return parsed;
}

function readNonNegativeInteger(value: unknown): number | null {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.max(0, Math.trunc(parsed)) : null;
}

function countFilled(value: unknown): number {
  return Array.isArray(value) ? value.filter(Boolean).length : 0;
}

function nullableString(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value : null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
