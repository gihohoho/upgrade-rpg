import type { BossOption } from '@/api/contracts';
import {
  addResultLog,
  createGameActionResult,
  formatCompactNumber,
  getNormalBossSkillDropRate,
  isFirstEquipSkillGuaranteeBoss,
  type GameActionResult,
} from '@/game/domain';
import type { TownHudSkill, TownHudStat, TownHudViewModel } from './townHud';

export type BossCombatType = 'normal' | 'special';

export interface BossCombatBoss {
  index: number;
  code: string;
  name: string;
  tier: number;
  tierLabel: string;
  bossType: BossCombatType;
  typeLabel: string;
  sigilText: string;
  hp: number;
  hpLabel: string;
  description: string;
  entryCondition: string;
  cooldownLabel: string;
  dropRuleLabel: string;
  skillDropRateLabel: string;
  equipmentSkillGuarantee: boolean;
  dropHighlights: string[];
}

export interface BossCombatSource {
  town: TownHudViewModel;
  bosses: BossOption[];
  preferredIndex?: number | null;
  createdAt: number;
}

export interface BossCombatViewModel {
  zoneType: 'boss';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  avatarText: string;
  levelLabel: string;
  goldLabel: string;
  stats: TownHudStat[];
  skills: TownHudSkill[];
  bosses: BossCombatBoss[];
  selectedIndex: number;
  selectedBoss: BossCombatBoss;
  bossHp: number;
  bossHpLabel: string;
  bossHpPercent: 100;
  action: GameActionResult;
  masterDataConnected: true;
  snapshotConnected: false;
  runtimeConnected: false;
  randomConnected: false;
}

export function createBossCombatViewModel(source: BossCombatSource): BossCombatViewModel {
  const bosses = source.bosses
    .filter((boss) => boss.isEnabled)
    .slice()
    .sort(compareBosses)
    .map(normalizeBoss);
  if (!bosses.length) throw new Error('활성 보스가 없습니다.');

  const selectedIndex = clampBossIndex(source.preferredIndex, bosses.length);
  const selectedBoss = bosses[selectedIndex];

  return {
    zoneType: 'boss',
    accountCharacterId: source.town.accountCharacterId,
    characterName: source.town.characterName,
    characterLabel: source.town.characterLabel,
    avatarText: source.town.avatarText,
    levelLabel: source.town.levelLabel,
    goldLabel: source.town.goldLabel,
    stats: source.town.stats.map((stat) => ({ ...stat })),
    skills: source.town.skills.map((skill) => ({ ...skill })),
    bosses,
    selectedIndex,
    selectedBoss,
    bossHp: selectedBoss.hp,
    bossHpLabel: `${selectedBoss.hpLabel} / ${selectedBoss.hpLabel}`,
    bossHpPercent: 100,
    action: createBossPreviewAction(selectedBoss, source.createdAt),
    masterDataConnected: true,
    snapshotConnected: false,
    runtimeConnected: false,
    randomConnected: false,
  };
}

function compareBosses(left: BossOption, right: BossOption): number {
  const typeOrder = Number(left.bossType === 'special') - Number(right.bossType === 'special');
  return typeOrder
    || resolveBossTier(left) - resolveBossTier(right)
    || left.code.localeCompare(right.code);
}

function normalizeBoss(boss: BossOption, index: number): BossCombatBoss {
  const tier = resolveBossTier(boss);
  const isSpecial = boss.bossType === 'special';
  const hp = toNonNegativeFiniteNumber(boss.hp);
  const summonRules = asRecord(boss.summonRules);
  const raw = asRecord(summonRules.raw);
  const rawSkillDropRate = toNonNegativeFiniteNumber(raw.skillDropRate);
  const skillDropRate = getNormalBossSkillDropRate({
    id: tier,
    isSpecial,
    skillDropRate: rawSkillDropRate,
  });
  const equipmentSkillGuarantee = isFirstEquipSkillGuaranteeBoss({ id: tier, isSpecial });
  const drops = arrayOfStrings(summonRules.dropsList).map(stripMarkup).filter(Boolean);

  return {
    index,
    code: boss.code,
    name: boss.name,
    tier,
    tierLabel: isSpecial ? `SPECIAL ${Math.max(1, tier - 100)}` : `TIER ${tier}`,
    bossType: boss.bossType,
    typeLabel: isSpecial ? '특수 보스' : '일반 보스',
    sigilText: boss.name.trim().slice(0, 1) || '王',
    hp,
    hpLabel: formatCompactNumber(hp),
    description: stripMarkup(stringValue(summonRules.desc1) || boss.description) || '보스존에 출현하는 강력한 적입니다.',
    entryCondition: stripMarkup(stringValue(summonRules.reqLvl)) || '상세 입장 판정은 snapshot 연결 뒤 적용됩니다.',
    cooldownLabel: formatCooldown(boss.cooldownSeconds, isSpecial),
    dropRuleLabel: raw.dropRateDoubled === true ? '표시된 드랍률 2배 규칙 포함' : 'master-data 드랍 규칙 사용',
    skillDropRateLabel: skillDropRate > 0 ? `${formatPercent(skillDropRate)} 기본 스킬북` : '기본 스킬북 드랍 없음',
    equipmentSkillGuarantee,
    dropHighlights: drops.slice(0, 3),
  };
}

function createBossPreviewAction(boss: BossCombatBoss, createdAt: number): GameActionResult {
  const result = createGameActionResult('boss.preview.select', {
    bossIndex: boss.index,
    bossCode: boss.code,
    bossType: boss.bossType,
    mode: 'display-only',
  }, createdAt);
  return addResultLog(result, `[미리보기] ${boss.name} 표시 상태를 열었습니다.`);
}

function resolveBossTier(boss: BossOption): number {
  const tier = boss.tier === null ? Number.NaN : Number(boss.tier);
  if (Number.isFinite(tier)) return Math.max(1, Math.trunc(tier));
  const codeTier = Number(boss.code.match(/(\d+)$/)?.[1]);
  return Number.isFinite(codeTier) ? Math.max(1, Math.trunc(codeTier)) : Number.MAX_SAFE_INTEGER;
}

function clampBossIndex(value: number | null | undefined, bossCount: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 0;
  return Math.min(bossCount - 1, Math.max(0, Math.trunc(parsed)));
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

function arrayOfStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
}

function stripMarkup(value: unknown): string {
  return stringValue(value)
    .replace(/<[^>]*>/g, ' ')
    .replace(/^\*+/, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function formatPercent(rate: number): string {
  const percent = rate * 100;
  return `${percent.toFixed(percent >= 1 ? 2 : 3).replace(/0+$/, '').replace(/\.$/, '')}%`;
}

function formatCooldown(seconds: number, isSpecial: boolean): string {
  const normalized = Math.max(0, Math.trunc(Number(seconds) || 0));
  if (!normalized) return isSpecial ? '쿨타임 정보 없음' : '소환 쿨타임 없음';
  const minutes = Math.floor(normalized / 60);
  const remainder = normalized % 60;
  return remainder ? `${minutes}분 ${remainder}초 쿨타임` : `${minutes}분 쿨타임`;
}
