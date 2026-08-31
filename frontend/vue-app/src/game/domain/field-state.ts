export interface FieldState {
  enemyHpByZone: Record<string, number>;
  respawnEndAtByZone: Record<string, number>;
}

export interface FieldStateResult extends FieldState {
  hp: number;
  respawnPending: boolean;
}

export function resolveFieldEnemyState(state: FieldState, zoneIndex: number, zoneMaxHp: number, now: number): FieldStateResult {
  const key = String(zoneIndex);
  const enemyHpByZone = { ...state.enemyHpByZone };
  const respawnEndAtByZone = { ...state.respawnEndAtByZone };
  const respawnEndAt = Number(respawnEndAtByZone[key]) || 0;
  if (respawnEndAt && now >= respawnEndAt) {
    enemyHpByZone[key] = zoneMaxHp;
    delete respawnEndAtByZone[key];
  }

  const currentHp = Number(enemyHpByZone[key]);
  if (!Number.isFinite(currentHp)) enemyHpByZone[key] = zoneMaxHp;
  return {
    enemyHpByZone,
    respawnEndAtByZone,
    hp: enemyHpByZone[key],
    respawnPending: Boolean(respawnEndAtByZone[key]),
  };
}

export function scheduleFieldRespawn(state: FieldState, zoneIndex: number, delayMs: number, now: number): FieldStateResult {
  const key = String(zoneIndex);
  const enemyHpByZone = { ...state.enemyHpByZone, [key]: 0 };
  const respawnEndAtByZone = { ...state.respawnEndAtByZone, [key]: now + Math.max(0, delayMs) };
  return { enemyHpByZone, respawnEndAtByZone, hp: 0, respawnPending: true };
}

export function completeFieldRespawn(state: FieldState, zoneIndex: number, zoneMaxHp: number, now: number): FieldStateResult {
  const key = String(zoneIndex);
  const enemyHpByZone = { ...state.enemyHpByZone };
  const respawnEndAtByZone = { ...state.respawnEndAtByZone };
  const endAt = Number(respawnEndAtByZone[key]) || 0;
  if (!endAt || now < endAt) {
    return { enemyHpByZone, respawnEndAtByZone, hp: Number(enemyHpByZone[key]) || 0, respawnPending: Boolean(endAt) };
  }
  enemyHpByZone[key] = zoneMaxHp;
  delete respawnEndAtByZone[key];
  return { enemyHpByZone, respawnEndAtByZone, hp: zoneMaxHp, respawnPending: false };
}
