import type { GameSaveIntegrity } from '@/api/contracts';
import { applyServerSavePayload, cloneDomainValue, type GameServerState } from '@/game/domain';

export interface SelectedCharacterIdentity {
  slotKey: `character-${number}`;
  accountCharacterId: string;
  characterCode: string;
}

export interface LoadedGameSnapshot {
  slotKey: `character-${number}`;
  accountCharacterId: string;
  saveVersion: number | null;
  serverState: GameServerState;
  isEmpty: boolean;
  source: string | null;
  updatedAt: string | null;
  integrity: GameSaveIntegrity | null;
}

export class GameSnapshotContractError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'GameSnapshotContractError';
  }
}

export function applyLoadedGameSnapshot(
  payload: unknown,
  expected: SelectedCharacterIdentity,
): LoadedGameSnapshot {
  if (!isRecord(payload) || payload.status !== 'loaded' || payload.exists !== true) {
    throw new GameSnapshotContractError('선택한 캐릭터의 서버 저장 응답이 완전하지 않습니다.');
  }
  if (payload.slotKey !== expected.slotKey || payload.accountCharacterId !== expected.accountCharacterId) {
    throw new GameSnapshotContractError('서버 저장의 캐릭터 식별 정보가 현재 선택과 일치하지 않습니다.');
  }
  const accountCharacter = payload.accountCharacter;
  if (!isRecord(accountCharacter)
    || accountCharacter.id !== expected.accountCharacterId
    || accountCharacter.characterCode !== expected.characterCode) {
    throw new GameSnapshotContractError('서버 저장의 캐릭터 정보가 현재 선택과 일치하지 않습니다.');
  }
  if (payload.snapshot !== null && !isRecord(payload.snapshot)) {
    throw new GameSnapshotContractError('서버 저장 snapshot 형식이 올바르지 않습니다.');
  }

  const snapshot = payload.snapshot ?? {};
  const isEmpty = Object.keys(snapshot).length === 0;
  const serverState = applyServerSavePayload(snapshot, { defaultCharacterId: expected.characterCode });
  if (serverState.player.currentCharacterId !== expected.characterCode) {
    throw new GameSnapshotContractError('서버 저장의 캐릭터 종류가 현재 선택과 일치하지 않습니다.');
  }

  return {
    slotKey: expected.slotKey,
    accountCharacterId: expected.accountCharacterId,
    saveVersion: normalizeSaveVersion(payload.saveVersion),
    serverState: cloneDomainValue(serverState),
    isEmpty,
    source: nullableString(payload.source),
    updatedAt: nullableString(payload.updatedAt),
    integrity: normalizeIntegrity(payload.integrity),
  };
}

function normalizeSaveVersion(value: unknown): number | null {
  const parsed = Number(value);
  return value === null || value === undefined || !Number.isSafeInteger(parsed) || parsed < 0 ? null : parsed;
}

function normalizeIntegrity(value: unknown): GameSaveIntegrity | null {
  if (!isRecord(value) || typeof value.ok !== 'boolean' || !Array.isArray(value.warnings)) return null;
  return cloneDomainValue({
    ...value,
    warnings: value.warnings.filter((warning): warning is string => typeof warning === 'string'),
  }) as GameSaveIntegrity;
}

function nullableString(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value : null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
