export type CombatRuntimeTargetType = 'field' | 'boss';
export type CombatRuntimeStatus = 'idle' | 'running' | 'paused' | 'defeated';
export type CombatRuntimePauseReason = 'manual' | 'utility' | 'visibility' | null;

export interface CombatRuntimeTarget {
  type: CombatRuntimeTargetType;
  key: string;
  name: string;
  maxHp: number;
  attackDamage: number;
  intervalMs: number;
}

export interface CombatRuntimeSnapshot {
  status: CombatRuntimeStatus;
  targetType: CombatRuntimeTargetType | null;
  targetKey: string;
  targetName: string;
  maxHp: number;
  currentHp: number;
  hpPercent: number;
  attackDamage: number;
  intervalMs: number;
  attackCount: number;
  lastDamage: number;
  lastTickAt: number | null;
  pauseReason: CombatRuntimePauseReason;
  serverStateConnected: false;
  rewardsConnected: false;
  randomConnected: false;
}

export interface CombatRuntimeScheduler {
  now(): number;
  schedule(callback: () => void, delayMs: number): unknown;
  cancel(handle: unknown): void;
}

export interface CombatRuntimeController {
  engage(target: CombatRuntimeTarget): boolean;
  pause(reason?: Exclude<CombatRuntimePauseReason, null>): boolean;
  resume(reason?: Exclude<CombatRuntimePauseReason, null>): boolean;
  restart(): boolean;
  stop(): void;
  destroy(): void;
  getSnapshot(): CombatRuntimeSnapshot;
}

const browserScheduler: CombatRuntimeScheduler = {
  now: () => Date.now(),
  schedule: (callback, delayMs) => globalThis.setInterval(callback, delayMs),
  cancel: (handle) => globalThis.clearInterval(handle as number),
};

export function createIdleCombatRuntimeSnapshot(): CombatRuntimeSnapshot {
  return {
    status: 'idle',
    targetType: null,
    targetKey: '',
    targetName: '',
    maxHp: 0,
    currentHp: 0,
    hpPercent: 0,
    attackDamage: 0,
    intervalMs: 0,
    attackCount: 0,
    lastDamage: 0,
    lastTickAt: null,
    pauseReason: null,
    serverStateConnected: false,
    rewardsConnected: false,
    randomConnected: false,
  };
}

export function createCombatRuntimeController(
  onChange: (snapshot: CombatRuntimeSnapshot) => void,
  scheduler: CombatRuntimeScheduler = browserScheduler,
): CombatRuntimeController {
  let state = createIdleCombatRuntimeSnapshot();
  let timerHandle: unknown = null;
  let destroyed = false;

  function snapshot(): CombatRuntimeSnapshot {
    return { ...state };
  }

  function publish() {
    onChange(snapshot());
  }

  function clearTimer() {
    if (timerHandle === null) return;
    scheduler.cancel(timerHandle);
    timerHandle = null;
  }

  function start(): boolean {
    if (destroyed || !state.targetType || state.currentHp <= 0 || state.status === 'running') return false;
    state = { ...state, status: 'running', pauseReason: null };
    timerHandle = scheduler.schedule(tick, state.intervalMs);
    publish();
    return true;
  }

  function tick() {
    if (destroyed || state.status !== 'running' || state.currentHp <= 0) return;
    const damage = Math.min(state.currentHp, state.attackDamage);
    const currentHp = Math.max(0, state.currentHp - damage);
    state = {
      ...state,
      currentHp,
      hpPercent: state.maxHp > 0 ? currentHp / state.maxHp * 100 : 0,
      attackCount: state.attackCount + 1,
      lastDamage: damage,
      lastTickAt: scheduler.now(),
      status: currentHp <= 0 ? 'defeated' : 'running',
    };
    if (currentHp <= 0) clearTimer();
    publish();
  }

  function engage(target: CombatRuntimeTarget): boolean {
    if (destroyed) return false;
    clearTimer();
    const maxHp = Math.max(1, Number(target.maxHp) || 1);
    const attackDamage = Math.max(1, Number(target.attackDamage) || 1);
    const intervalMs = Math.max(100, Number(target.intervalMs) || 100);
    state = {
      ...createIdleCombatRuntimeSnapshot(),
      targetType: target.type,
      targetKey: String(target.key),
      targetName: String(target.name),
      maxHp,
      currentHp: maxHp,
      hpPercent: 100,
      attackDamage,
      intervalMs,
    };
    publish();
    return start();
  }

  function pause(reason: Exclude<CombatRuntimePauseReason, null> = 'manual'): boolean {
    if (destroyed || state.status !== 'running') return false;
    clearTimer();
    state = { ...state, status: 'paused', pauseReason: reason };
    publish();
    return true;
  }

  function resume(reason?: Exclude<CombatRuntimePauseReason, null>): boolean {
    if (destroyed || state.status !== 'paused') return false;
    if (reason && state.pauseReason !== reason) return false;
    return start();
  }

  function restart(): boolean {
    if (destroyed || !state.targetType) return false;
    clearTimer();
    state = {
      ...state,
      status: 'idle',
      currentHp: state.maxHp,
      hpPercent: 100,
      attackCount: 0,
      lastDamage: 0,
      lastTickAt: null,
      pauseReason: null,
    };
    publish();
    return start();
  }

  function stop() {
    clearTimer();
    state = { ...state, status: 'idle', pauseReason: null };
    publish();
  }

  function destroy() {
    stop();
    destroyed = true;
  }

  return { engage, pause, resume, restart, stop, destroy, getSnapshot: snapshot };
}
