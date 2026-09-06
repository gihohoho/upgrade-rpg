import type { GameSaveRequestBody } from '@/api/contracts';
import type { SelectedCharacterIdentity } from '@/game/adapters/serverSnapshot';

export interface RecoveryIdentity extends SelectedCharacterIdentity { userId: number }
export interface RecoveryCopy {
  snapshot: GameSaveRequestBody['snapshot'];
  saveVersion: number;
  capturedAt: string;
  pending: boolean;
}
interface RecoveryEnvelope {
  schema: 1;
  identity: RecoveryIdentity;
  current: RecoveryCopy;
  backups: RecoveryCopy[];
}
export interface RecoveryRead { raw: string | null; entry: RecoveryEnvelope | null }
export interface RecoveryStorage { getItem(key: string): string | null; setItem(key: string, value: string): void }
export class LocalRecoveryError extends Error {}
export class RecoveryChangedError extends LocalRecoveryError {}

export function recoveryKey(identity: RecoveryIdentity): string {
  if (!Number.isSafeInteger(identity.userId) || identity.userId <= 0
    || !/^character-[1-8]$/.test(identity.slotKey)
    || !/^[a-f0-9]{32}$/.test(identity.accountCharacterId)
    || !identity.characterCode) throw new LocalRecoveryError('복구본의 계정·캐릭터 식별 정보가 올바르지 않습니다.');
  return `upgradeRpgVueRecovery:v1:${identity.userId}:${identity.slotKey}:${identity.accountCharacterId}`;
}

export function createLocalRecovery(getStorage: () => RecoveryStorage = () => window.localStorage) {
  function read(identity: RecoveryIdentity): RecoveryRead {
    try {
      const raw = getStorage().getItem(recoveryKey(identity));
      if (raw === null) return { raw, entry: null };
      const entry = JSON.parse(raw) as RecoveryEnvelope;
      if (entry.schema !== 1 || !entry.identity
        || Object.keys(identity).some((key) => entry.identity[key as keyof RecoveryIdentity] !== identity[key as keyof RecoveryIdentity])
        || !Array.isArray(entry.backups) || !validCopy(entry.current, identity)
        || !entry.backups.every((copy) => validCopy(copy, identity))) throw new Error('invalid');
      return { raw, entry };
    } catch {
      throw new LocalRecoveryError('이 기기 복구본을 안전하게 읽을 수 없습니다. 원본은 변경하지 않았습니다. 브라우저 저장소 설정을 확인해 주세요.');
    }
  }

  function write(identity: RecoveryIdentity, previous: RecoveryRead, current: RecoveryCopy, archive = false): RecoveryRead {
    try {
      const storage = getStorage();
      const key = recoveryKey(identity);
      if (storage.getItem(key) !== previous.raw) throw new RecoveryChangedError('다른 탭에서 복구본이 변경되었습니다. 서버 저장을 다시 불러와 선택해 주세요.');
      const backups = previous.entry?.backups.slice() ?? [];
      const old = previous.entry?.current;
      if (archive && old && !sameSnapshot(old, current)
        && !backups.some((backup) => JSON.stringify(backup) === JSON.stringify(old))) backups.push(old);
      const entry: RecoveryEnvelope = { schema: 1, identity: { ...identity }, current, backups };
      const raw = JSON.stringify(entry);
      storage.setItem(key, raw); // snapshot and pending marker commit together; no token is accepted here.
      return { raw, entry: JSON.parse(raw) as RecoveryEnvelope };
    } catch (error) {
      if (error instanceof RecoveryChangedError) throw error;
      throw new LocalRecoveryError('이 기기에 복구본을 기록하지 못했습니다. 저장 공간·브라우저 설정을 확인하고 서버 저장 결과를 확인해 주세요.');
    }
  }

  function capture(identity: RecoveryIdentity, request: GameSaveRequestBody, previous: RecoveryRead): RecoveryRead {
    const current: RecoveryCopy = {
      snapshot: request.snapshot, saveVersion: request.saveVersion,
      capturedAt: new Date().toISOString(), pending: true,
    };
    if (!validCopy(current, identity)) throw new LocalRecoveryError('복구할 게임 저장 형식이 올바르지 않습니다.');
    return write(identity, previous, current);
  }

  function acknowledge(identity: RecoveryIdentity, captured: RecoveryRead): RecoveryRead | null {
    const latest = read(identity);
    if (!captured.entry || latest.raw !== captured.raw) return null; // An old response cannot clear a newer pending copy.
    return write(identity, latest, { ...captured.entry.current, pending: false });
  }
  return { read, write, capture, acknowledge };
}

export function sameSnapshot(left: RecoveryCopy, right: RecoveryCopy): boolean {
  return left.saveVersion === right.saveVersion && JSON.stringify(left.snapshot) === JSON.stringify(right.snapshot);
}

function validCopy(copy: RecoveryCopy, identity: RecoveryIdentity): boolean {
  return Boolean(copy && Number.isSafeInteger(copy.saveVersion) && copy.saveVersion >= 0 && copy.saveVersion <= 999
    && typeof copy.pending === 'boolean' && typeof copy.capturedAt === 'string' && Number.isFinite(Date.parse(copy.capturedAt))
    && copy.snapshot && typeof copy.snapshot === 'object' && !Array.isArray(copy.snapshot)
    && copy.snapshot.saveVersion === copy.saveVersion
    && copy.snapshot.player && typeof copy.snapshot.player === 'object' && !Array.isArray(copy.snapshot.player)
    && (copy.snapshot.player as Record<string, unknown>).currentCharacterId === identity.characterCode);
}
