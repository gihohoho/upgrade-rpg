import type {
  CharacterSkillOption,
  EnhancementGroupOption,
  EnhancementLevelOption,
  ItemTemplateOption,
  SkillLevelOption,
  SkillOption,
} from '@/api/contracts';
import { addResultLog, createGameActionResult, type GameActionResult } from '@/game/domain';
import { normalizeInventoryItemTemplate, type InventoryItemView } from './inventoryEquipment';
import type { TownHudViewModel } from './townHud';

export type SkillTone = 'passive' | 'buff' | 'active' | 'awakening';

export interface SkillEnhancementSkillView {
  id: string;
  stateKey: string;
  slotKey: string;
  name: string;
  description: string;
  effectLines: string[];
  tone: SkillTone;
  currentLevel: number;
  bonusLevel: number;
  effectiveLevel: number;
  maxLevel: number;
  procRateLabel: string;
  coefficientLabel: string;
  cooldownLabel: string;
  bookName: string;
  firstUseResultLevel: number;
  firstUseRule: string;
  bonusGroup: string | null;
  awakened: boolean;
  masterDataConnected: true;
  snapshotConnected: boolean;
}

export interface EnhancementStepView {
  groupCode: string;
  fromLevel: number;
  toLevel: number;
  levelLabel: string;
  successRate: number;
  successRateLabel: string;
  goldCost: number;
  goldCostLabel: string;
  costSourceLabel: string;
  materialCount: number;
  materialLabel: string;
  resultStats: { label: string; value: string }[];
  failureLabel: string;
}

export interface EnhancementGroupView {
  code: string;
  name: string;
  description: string;
  maxLevel: number;
  itemCount: number;
  stepCount: number;
}

export interface SkillEnhancementSource {
  town: TownHudViewModel;
  skills: SkillOption[];
  characterSkills: CharacterSkillOption[];
  skillLevels: SkillLevelOption[];
  itemTemplates: ItemTemplateOption[];
  enhancementGroups: EnhancementGroupOption[];
  enhancementLevels: EnhancementLevelOption[];
  preferredSkillId?: string | null;
  preferredItemCode?: string | null;
  preferredEnhancementLevel?: number | null;
  createdAt: number;
}

export interface SkillEnhancementViewModel {
  zoneType: 'skill-enhancement';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  levelLabel: string;
  goldLabel: string;
  skills: SkillEnhancementSkillView[];
  selectedSkill: SkillEnhancementSkillView;
  enhancementGroups: EnhancementGroupView[];
  enhancementItems: InventoryItemView[];
  selectedEnhancementItem: InventoryItemView;
  selectedEnhancementGroup: EnhancementGroupView;
  enhancementSteps: EnhancementStepView[];
  selectedEnhancementStep: EnhancementStepView;
  action: GameActionResult;
  masterDataConnected: true;
  snapshotConnected: boolean;
  skillMutationConnected: false;
  itemMutationConnected: false;
  randomResultConnected: false;
  saveConnected: false;
}

const SLOT_ORDER = ['Q', 'W', 'E', 'R', 'T', 'F', 'D', 'SQ', 'SW', 'M'] as const;
const BOOK_NAMES: Record<string, string> = {
  Q: '스킬강화권',
  W: '강력한 스킬강화권',
  E: '빛나는 스킬강화권',
  R: '화려한 스킬강화권',
  T: '찬란한 스킬강화권',
  F: '해방된 스킬강화권',
  D: '천공의 스킬강화권',
  SQ: '심연의 스킬강화권',
  SW: '-초월- 심연의 스킬강화권',
  M: '진 각성 스킬강화권',
};
const STAT_LABELS: Record<string, string> = {
  atk: '공격력',
  sdmg: '스킬 피해',
  alldmg: '모든 피해',
  curveAtkInc: '공격력 곡선',
  curveSmult: '스킬 계수 곡선',
  extraSmult: '추가 스킬 계수',
};

export function createSkillEnhancementViewModel(source: SkillEnhancementSource): SkillEnhancementViewModel {
  const skills = createSkillViews(source);
  if (!skills.length) throw new Error('스킬 master-data가 없습니다.');
  const selectedSkill = skills.find((skill) => skill.id === source.preferredSkillId) ?? skills[0];

  const enabledGroups = source.enhancementGroups.filter((group) => group.isEnabled);
  const enabledCodes = new Set(enabledGroups.map((group) => group.code));
  const enhancementTemplates = source.itemTemplates
    .filter((item) => item.enhanceGroupCode && enabledCodes.has(item.enhanceGroupCode))
    .slice()
    .sort(compareEnhancementTemplates);
  if (!enhancementTemplates.length) throw new Error('강화 가능한 아이템 master-data가 없습니다.');
  const selectedTemplate = enhancementTemplates.find((item) => item.code === source.preferredItemCode)
    ?? enhancementTemplates[0];
  const selectedEnhancementItem = normalizeInventoryItemTemplate(selectedTemplate);
  const selectedGroupSource = enabledGroups.find((group) => group.code === selectedTemplate.enhanceGroupCode);
  if (!selectedGroupSource) throw new Error('선택한 아이템의 강화 그룹을 찾을 수 없습니다.');

  const enhancementGroups = enabledGroups.map((group) => ({
    code: group.code,
    name: group.name,
    description: plainText(group.description) || '강화 단계별 규칙을 확인합니다.',
    maxLevel: nonNegativeInteger(group.maxLevel),
    itemCount: enhancementTemplates.filter((item) => item.enhanceGroupCode === group.code).length,
    stepCount: source.enhancementLevels.filter((step) => step.groupCode === group.code).length,
  }));
  const selectedEnhancementGroup = enhancementGroups.find((group) => group.code === selectedGroupSource.code);
  if (!selectedEnhancementGroup) throw new Error('표시할 강화 그룹이 없습니다.');

  const enhancementSteps = source.enhancementLevels
    .filter((step) => step.groupCode === selectedEnhancementGroup.code)
    .slice()
    .sort((left, right) => left.fromLevel - right.fromLevel)
    .map((step) => createEnhancementStep(step, selectedTemplate));
  if (!enhancementSteps.length) throw new Error('표시할 강화 단계가 없습니다.');
  const selectedEnhancementStep = enhancementSteps.find((step) => step.fromLevel === source.preferredEnhancementLevel)
    ?? enhancementSteps[0];

  const action = createGameActionResult('skill-enhancement.preview.open', {
    mode: 'display-only',
    selectedSkill: selectedSkill.slotKey,
    selectedItemCode: selectedEnhancementItem.code,
    selectedEnhancementLevel: selectedEnhancementStep.fromLevel,
  }, source.createdAt);
  addResultLog(action, '[미리보기] 스킬 레벨과 강화 규칙을 읽기 전용으로 구성했습니다.');

  return {
    zoneType: 'skill-enhancement',
    accountCharacterId: source.town.accountCharacterId,
    characterName: source.town.characterName,
    characterLabel: source.town.characterLabel,
    levelLabel: source.town.levelLabel,
    goldLabel: source.town.goldLabel,
    skills,
    selectedSkill,
    enhancementGroups,
    enhancementItems: enhancementTemplates.map(normalizeInventoryItemTemplate),
    selectedEnhancementItem,
    selectedEnhancementGroup,
    enhancementSteps,
    selectedEnhancementStep,
    action,
    masterDataConnected: true,
    snapshotConnected: source.town.snapshotConnected,
    skillMutationConnected: false,
    itemMutationConnected: false,
    randomResultConnected: false,
    saveConnected: false,
  };
}

function createSkillViews(source: SkillEnhancementSource): SkillEnhancementSkillView[] {
  const state = source.town.serverState.player.skills;
  const links = source.characterSkills
    .filter((link) => link.characterCode === source.town.characterCode)
    .sort((left, right) => left.sortOrder - right.sortOrder || left.skillCode.localeCompare(right.skillCode));
  const linkedCodes = links.length ? links.map((link) => link.skillCode) : source.skills.map((skill) => skill.code);
  const skillByCode = new Map(source.skills.map((skill) => [skill.code, skill]));
  const views: SkillEnhancementSkillView[] = [];

  for (const code of linkedCodes) {
    const skill = skillByCode.get(code);
    if (!skill) continue;
    const options = asRecord(skill.options);
    const raw = asRecord(options.raw);
    const skillState = state[skill.code] ?? { level: 0 };
    const baseLevel = nonNegativeInteger(skillState.level);
    const bonusGroup = nullableString(options.bonusGroup ?? raw.bonusGroup);
    views.push(createSkillView({
      id: skill.code,
      stateKey: skill.code,
      slotKey: skill.slotKey,
      name: skill.name,
      description: plainText(skill.description) || '스킬 설명이 없습니다.',
      effectHtml: stringValue(options.effectHtml ?? raw.effectHtml),
      skillType: stringValue(options.skillType ?? raw.skillType),
      currentLevel: skillState.isUpgraded ? 0 : baseLevel,
      maxLevel: findMaxSkillLevel(source.skillLevels, skill.code, raw.maxLevel),
      procRate: skill.procRate,
      coefficient: options.damageMultiplier ?? raw.damageMultiplier,
      cooldownSeconds: skill.cooldownSeconds,
      bonusGroup,
      awakened: false,
      snapshotConnected: source.town.snapshotConnected,
    }));

    const awakening = asRecord(options.awakening ?? raw.awakening);
    const awakeningSlot = stringValue(awakening.slotKey);
    if (awakeningSlot) {
      views.push(createSkillView({
        id: `${skill.code}:${awakeningSlot.toLowerCase()}`,
        stateKey: skill.code,
        slotKey: awakeningSlot,
        name: stringValue(awakening.name) || `${skill.name} 각성`,
        description: plainText(awakening.description) || '각성 스킬 설명이 없습니다.',
        effectHtml: stringValue(awakening.effectHtml),
        skillType: 'awakening',
        currentLevel: skillState.isUpgraded ? baseLevel : 0,
        maxLevel: findMaxSkillLevel(source.skillLevels, skill.code, raw.maxLevel),
        procRate: awakening.baseProcRate,
        coefficient: awakening.damageMultiplier,
        cooldownSeconds: null,
        bonusGroup: nullableString(awakening.bonusGroup),
        awakened: true,
        snapshotConnected: source.town.snapshotConnected,
      }));
    }
  }

  return views.sort((left, right) => slotOrder(left.slotKey) - slotOrder(right.slotKey) || left.id.localeCompare(right.id));
}

function createSkillView(input: {
  id: string;
  stateKey: string;
  slotKey: string;
  name: string;
  description: string;
  effectHtml: string;
  skillType: string;
  currentLevel: number;
  maxLevel: number;
  procRate: unknown;
  coefficient: unknown;
  cooldownSeconds: number | null | undefined;
  bonusGroup: string | null;
  awakened: boolean;
  snapshotConnected: boolean;
}): SkillEnhancementSkillView {
  const isDedicatedAwakening = input.slotKey === 'SQ' || input.slotKey === 'SW';
  const bonusLevel = 0;
  const firstUseResultLevel = isDedicatedAwakening ? 1 : Math.min(input.maxLevel, input.currentLevel + 1);
  return {
    id: input.id,
    stateKey: input.stateKey,
    slotKey: input.slotKey,
    name: input.name,
    description: input.description,
    effectLines: splitEffectLines(input.effectHtml),
    tone: resolveSkillTone(input.slotKey, input.skillType),
    currentLevel: input.currentLevel,
    bonusLevel,
    effectiveLevel: input.currentLevel + bonusLevel,
    maxLevel: input.maxLevel,
    procRateLabel: percentLabel(input.procRate),
    coefficientLabel: numberLabel(input.coefficient, '배'),
    cooldownLabel: input.cooldownSeconds ? `${numberLabel(input.cooldownSeconds, '초')}` : '상시·발동형',
    bookName: BOOK_NAMES[input.slotKey] ?? '전용 스킬강화권',
    firstUseResultLevel,
    firstUseRule: isDedicatedAwakening
      ? `기존 ${input.slotKey === 'SQ' ? 'Q' : 'W'} 레벨과 관계없이 첫 전용 강화권 결과는 Lv.1입니다.`
      : input.currentLevel >= input.maxLevel
        ? `현재 표시 기준 최대 Lv.${input.maxLevel}입니다.`
        : `전용 강화권 1개 사용 시 Lv.${firstUseResultLevel}이 됩니다.`,
    bonusGroup: input.bonusGroup,
    awakened: input.awakened,
    masterDataConnected: true,
    snapshotConnected: input.snapshotConnected,
  };
}

function createEnhancementStep(step: EnhancementLevelOption, item: ItemTemplateOption): EnhancementStepView {
  const configuredRate = clamp(Number(step.successRate), 0, 1);
  const successRate = step.groupCode === 'talisman_emblem' && configuredRate === 0 ? 1 : configuredRate;
  const configuredGold = nonNegativeNumber(step.goldCost);
  const options = asRecord(item.options);
  const raw = asRecord(options.raw);
  const itemBaseCost = nonNegativeNumber(options.baseCost ?? raw.baseCost);
  const goldCost = configuredGold || itemBaseCost;
  const materialRules = asRecord(step.materialRules);
  const isMaterialEnhancement = Object.keys(materialRules).length > 0 || step.groupCode === 'talisman_emblem';
  const materialCount = isMaterialEnhancement ? Math.pow(2, nonNegativeInteger(step.fromLevel)) : 0;
  const failRules = asRecord(step.failRules);
  return {
    groupCode: step.groupCode,
    fromLevel: nonNegativeInteger(step.fromLevel),
    toLevel: nonNegativeInteger(step.toLevel),
    levelLabel: `+${nonNegativeInteger(step.fromLevel)} → +${nonNegativeInteger(step.toLevel)}`,
    successRate,
    successRateLabel: percentLabel(successRate * 100),
    goldCost,
    goldCostLabel: goldCost ? `${formatInteger(goldCost)} Gold` : 'Gold 소모 없음',
    costSourceLabel: configuredGold ? '강화 단계 설정값' : itemBaseCost ? '아이템 기본 비용' : '재료 전용 강화',
    materialCount,
    materialLabel: materialCount ? `동일한 +0 장비 ${formatInteger(materialCount)}개` : '추가 재료 없음',
    resultStats: formatResultStats(step.resultStats),
    failureLabel: plainText(failRules.note) || '실패 시 강화 단계는 내려가지 않습니다.',
  };
}

function compareEnhancementTemplates(left: ItemTemplateOption, right: ItemTemplateOption): number {
  return String(left.enhanceGroupCode).localeCompare(String(right.enhanceGroupCode))
    || nullableTier(left.grade) - nullableTier(right.grade)
    || left.name.localeCompare(right.name)
    || left.code.localeCompare(right.code);
}

function formatResultStats(input: unknown): { label: string; value: string }[] {
  const result = asRecord(input);
  const progression = asRecord(result.statProgression);
  const rows: { label: string; value: string }[] = [];
  for (const [key, value] of Object.entries(progression)) {
    if (value !== null && value !== undefined) rows.push({ label: STAT_LABELS[key] ?? key, value: numberLabel(value) });
  }
  for (const key of ['curveAtkInc', 'curveSmult', 'extraSmult']) {
    const value = result[key];
    if (value !== null && value !== undefined) rows.push({ label: STAT_LABELS[key], value: numberLabel(value) });
  }
  return rows.length ? rows : [{ label: '결과 능력치', value: '세부 규칙 확정 대기' }];
}

function resolveSkillTone(slotKey: string, skillType: string): SkillTone {
  if (slotKey === 'SQ' || slotKey === 'SW' || slotKey === 'M') return 'awakening';
  if (skillType.includes('buff')) return 'buff';
  if (skillType.includes('passive') || slotKey === 'Q' || slotKey === 'W') return 'passive';
  return 'active';
}

function findMaxSkillLevel(levels: SkillLevelOption[], skillCode: string, fallback: unknown): number {
  const max = levels.filter((level) => level.skillCode === skillCode).reduce((value, level) => Math.max(value, level.level), 0);
  return max || nonNegativeInteger(fallback) || 7;
}

function splitEffectLines(value: string): string[] {
  return value
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]*>/g, ' ')
    .split(/\n+/)
    .map((line) => line.replace(/^[-·\s]+/, '').trim())
    .filter(Boolean);
}

function slotOrder(slotKey: string): number {
  const index = SLOT_ORDER.indexOf(slotKey as typeof SLOT_ORDER[number]);
  return index < 0 ? SLOT_ORDER.length : index;
}

function percentLabel(value: unknown): string {
  if (value === null || value === undefined || value === '') return '발동 확률 없음';
  const number = Number(value);
  if (!Number.isFinite(number)) return '발동 확률 없음';
  return `${number.toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1')}%`;
}

function numberLabel(value: unknown, suffix = ''): string {
  const number = Number(value);
  if (!Number.isFinite(number)) return '-';
  return `${number.toLocaleString('ko-KR', { maximumFractionDigits: 3 })}${suffix}`;
}

function formatInteger(value: number): string {
  return Math.trunc(value).toLocaleString('ko-KR');
}

function nonNegativeInteger(value: unknown): number {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.trunc(number)) : 0;
}

function nonNegativeNumber(value: unknown): number {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, number) : 0;
}

function nullableTier(value: unknown): number {
  const number = Number(value);
  return Number.isFinite(number) ? number : Number.MAX_SAFE_INTEGER;
}

function clamp(value: number, min: number, max: number): number {
  return Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : min;
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function stringValue(value: unknown): string {
  return typeof value === 'string' || typeof value === 'number' ? String(value).trim() : '';
}

function nullableString(value: unknown): string | null {
  const text = stringValue(value);
  return text || null;
}

function plainText(value: unknown): string {
  return stringValue(value).replace(/<br\s*\/?>/gi, ' ').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}
