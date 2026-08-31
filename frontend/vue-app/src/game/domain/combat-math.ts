export const FIELD_START_ATTACK_SPEED = 150;
export const FIELD_MAX_ATTACK_SPEED = 400;
export const BASE_ATTACK_AT_START_SPEED = 1250;
export const BASE_ATTACK_GAIN_PER_ASPD = 15;

export interface BasicAttackTotals {
  attack: number;
  basicAtkDmgInc: number;
  allDmgInc: number;
  basicCritDmg: number;
}

export function clampFieldAttackSpeed(value: unknown): number {
  const parsed = Number.parseFloat(String(value ?? '')) || FIELD_START_ATTACK_SPEED;
  return Math.min(FIELD_MAX_ATTACK_SPEED, Math.max(FIELD_START_ATTACK_SPEED, parsed));
}

export function getBaseAttackByAttackSpeed(value: unknown): number {
  const attackSpeed = clampFieldAttackSpeed(value);
  return Math.floor(BASE_ATTACK_AT_START_SPEED + (attackSpeed - FIELD_START_ATTACK_SPEED) * BASE_ATTACK_GAIN_PER_ASPD);
}

export function formatCompactNumber(input: unknown, significantDigits = 4): string {
  const num = Number(input);
  if (Number.isNaN(num) || input === undefined || num === 0) return '0A';
  const units = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  const isNegative = num < 0;
  let value = Math.abs(num);
  let unitIndex = 0;

  while (value >= 10000 && unitIndex < units.length - 1) {
    value /= 10000;
    unitIndex += 1;
  }

  let integerDigits = value >= 1 ? Math.floor(Math.log10(value)) + 1 : 1;
  let decimals = Math.max(0, significantDigits - integerDigits);
  let rounded = Number(value.toFixed(decimals));
  if (rounded >= 10000 && unitIndex < units.length - 1) {
    rounded /= 10000;
    unitIndex += 1;
    integerDigits = rounded >= 1 ? Math.floor(Math.log10(rounded)) + 1 : 1;
    decimals = Math.max(0, significantDigits - integerDigits);
  }

  const text = decimals > 0
    ? rounded.toFixed(decimals).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1')
    : String(Math.round(rounded));
  return `${isNegative ? '-' : ''}${text}${units[unitIndex]}`;
}

export function rollChance(baseRate: number, percentIncrease: number, sample: number): boolean {
  return sample <= baseRate * (1 + percentIncrease / 100);
}

export function calculateBasicAttackDamage(totals: BasicAttackTotals, critical: boolean): number {
  const baseDamage = Math.max(Number(totals.attack) || 0, 1);
  const criticalMultiplier = critical ? 1 + (Number(totals.basicCritDmg) || 0) / 100 : 1;
  const damage = baseDamage
    * (1 + (Number(totals.basicAtkDmgInc) || 0) / 100)
    * (1 + (Number(totals.allDmgInc) || 0) / 100)
    * criticalMultiplier;
  return Number.isNaN(damage) ? 0 : damage;
}

export function clampDamageTextPosition(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
