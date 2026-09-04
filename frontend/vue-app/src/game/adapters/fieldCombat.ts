import type { FieldZoneOption } from '@/api/contracts';
import {
  addResultLog,
  calculateBasicAttackDamage,
  createGameActionResult,
  formatCompactNumber,
  getBaseAttackByAttackSpeed,
  resolveFieldEnemyState,
  type GameActionResult,
} from '@/game/domain';
import type { TownHudSkill, TownHudStat, TownHudViewModel } from './townHud';

export interface FieldCombatZone {
  index: number;
  code: string;
  level: number;
  name: string;
  description: string;
  enemyHp: number;
  enemyHpLabel: string;
  goldReward: number;
  goldRewardLabel: string;
  entryCondition: string;
  farmReward: string;
}

export interface FieldCombatSource {
  town: TownHudViewModel;
  fieldZones: FieldZoneOption[];
  preferredIndex?: number | null;
  createdAt: number;
}

export interface FieldCombatViewModel {
  zoneType: 'field';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  avatarText: string;
  levelLabel: string;
  goldLabel: string;
  zones: FieldCombatZone[];
  selectedIndex: number;
  selectedZone: FieldCombatZone;
  enemyHp: number;
  enemyHpLabel: string;
  enemyHpPercent: 100;
  basicAttackLabel: string;
  criticalAttackLabel: string;
  attackSpeedLabel: string;
  stats: TownHudStat[];
  skills: TownHudSkill[];
  action: GameActionResult;
  masterDataConnected: true;
  snapshotConnected: boolean;
  runtimeConnected: false;
}

export function createFieldCombatViewModel(source: FieldCombatSource): FieldCombatViewModel {
  const zones = source.fieldZones
    .filter((zone) => zone.isEnabled)
    .slice()
    .sort((left, right) => left.sortOrder - right.sortOrder || left.code.localeCompare(right.code))
    .map(normalizeZone);
  if (!zones.length) throw new Error('활성 필드 구역이 없습니다.');

  const selectedIndex = clampZoneIndex(source.preferredIndex, zones.length);
  const selectedZone = zones[selectedIndex];
  const fieldState = resolveFieldEnemyState(
    { enemyHpByZone: {}, respawnEndAtByZone: {} },
    selectedIndex,
    selectedZone.enemyHp,
    source.createdAt,
  );
  const player = source.town.serverState.player;
  const attack = getBaseAttackByAttackSpeed(player.addAttackSpeed);
  const totals = {
    attack,
    basicAtkDmgInc: player.basicAtkDmgInc,
    allDmgInc: player.allDmgInc,
    basicCritDmg: player.basicCritDmg,
  };

  return {
    zoneType: 'field',
    accountCharacterId: source.town.accountCharacterId,
    characterName: source.town.characterName,
    characterLabel: source.town.characterLabel,
    avatarText: source.town.avatarText,
    levelLabel: source.town.levelLabel,
    goldLabel: source.town.goldLabel,
    zones,
    selectedIndex,
    selectedZone,
    enemyHp: fieldState.hp,
    enemyHpLabel: `${formatCompactNumber(fieldState.hp)} / ${selectedZone.enemyHpLabel}`,
    enemyHpPercent: 100,
    basicAttackLabel: formatCompactNumber(calculateBasicAttackDamage(totals, false)),
    criticalAttackLabel: formatCompactNumber(calculateBasicAttackDamage(totals, true)),
    attackSpeedLabel: `${player.addAttackSpeed}%`,
    stats: source.town.stats.map((stat) => ({ ...stat })),
    skills: source.town.skills.map((skill) => ({ ...skill })),
    action: createFieldPreviewAction(selectedZone, source.createdAt),
    masterDataConnected: true,
    snapshotConnected: source.town.snapshotConnected,
    runtimeConnected: false,
  };
}

function normalizeZone(zone: FieldZoneOption, index: number): FieldCombatZone {
  const enemyHp = toNonNegativeFiniteNumber(zone.enemyHp);
  const goldReward = toNonNegativeFiniteNumber(zone.goldReward);
  const entryRules = asRecord(zone.entryRules);
  const farmRules = asRecord(zone.farmRules);
  return {
    index,
    code: zone.code,
    level: Math.max(1, Math.trunc(Number(zone.sortOrder) || index + 1)),
    name: zone.name,
    description: zone.description?.trim() || '골드 획득을 위한 일반 필드입니다.',
    enemyHp,
    enemyHpLabel: formatCompactNumber(enemyHp),
    goldReward,
    goldRewardLabel: formatCompactNumber(goldReward),
    entryCondition: stringValue(entryRules.text) || '상세 입장 판정은 후속 전투 규칙 단계에서 적용됩니다.',
    farmReward: formatFarmReward(farmRules),
  };
}

function createFieldPreviewAction(zone: FieldCombatZone, createdAt: number): GameActionResult {
  const result = createGameActionResult('field.preview.select', {
    zoneIndex: zone.index,
    zoneCode: zone.code,
    mode: 'display-only',
  }, createdAt);
  return addResultLog(result, `[미리보기] ${zone.name} 표시 상태를 열었습니다.`);
}

function clampZoneIndex(value: number | null | undefined, zoneCount: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0;
  return Math.min(zoneCount - 1, Math.max(0, Math.trunc(parsed)));
}

function toNonNegativeFiniteNumber(value: unknown): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.max(0, parsed) : 0;
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function formatFarmReward(rules: Record<string, unknown>): string {
  if (!Object.keys(rules).length) return '순수공격력 추가 보상 없음';
  const probability = Math.max(0, Number(rules.prob) || 0) * 100;
  const gain = Math.max(0, Number(rules.gain) || 0);
  const cap = stringValue(rules.capText);
  return `처치 시 ${probability}% 확률 · 성공 +${gain}${cap ? ` · 최대 ${cap}` : ''}`;
}
