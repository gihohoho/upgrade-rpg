import {
  createDefaultServerState,
  formatCompactNumber,
  getBaseAttackByAttackSpeed,
  type GameServerState,
} from '@/game/domain';

export type TownFeatureKey = 'record' | 'codex' | 'ranking' | 'mailbox' | 'inventory' | 'field' | 'boss' | 'save';

export interface TownProgressSummary {
  gold: number | string | null;
  level: number | null;
  currentZoneIndex: number | null;
  currentZoneType: string | null;
  updatedAt: string | null;
}

export interface TownHudSource {
  accountCharacterId: string;
  slotKey: string;
  characterName: string;
  characterCode: string;
  characterLabel: string;
  progress: TownProgressSummary | null;
}

export interface TownHudStat {
  key: string;
  label: string;
  value: string;
  tone: 'attack' | 'skill' | 'speed' | 'all' | 'basic';
}

export interface TownHudSkill {
  key: string;
  slotKey: string;
  name: string;
  level: number;
  tone: 'passive' | 'buff' | 'active' | 'ultimate';
}

export interface TownFeatureDefinition {
  key: TownFeatureKey;
  icon: string;
  label: string;
  description: string;
  nextStep: string;
}

export interface TownHudViewModel {
  serverState: GameServerState;
  accountCharacterId: string;
  slotKey: string;
  characterName: string;
  characterCode: string;
  characterLabel: string;
  avatarText: string;
  zoneType: 'town';
  zoneLabel: string;
  levelLabel: string;
  goldLabel: string;
  recentSaveZoneLabel: string;
  updatedAt: string | null;
  stats: TownHudStat[];
  skills: TownHudSkill[];
  snapshotConnected: false;
}

export const TOWN_FEATURES: Record<TownFeatureKey, TownFeatureDefinition> = {
  record: {
    key: 'record',
    icon: '記',
    label: '기록관',
    description: '누적 처치와 획득 기록을 확인하는 공간입니다.',
    nextStep: '서버 snapshot과 기록 데이터 연결 단계에서 열립니다.',
  },
  codex: {
    key: 'codex',
    icon: '鑑',
    label: '도감',
    description: '획득한 장비와 수집 보너스를 확인하는 공간입니다.',
    nextStep: '인벤토리·장비 UI 이전 단계에서 열립니다.',
  },
  ranking: {
    key: 'ranking',
    icon: '榜',
    label: '랭킹',
    description: '캐릭터 성장 기록을 비교하는 공간입니다.',
    nextStep: '랭킹 데이터 계약을 연결한 뒤 열립니다.',
  },
  mailbox: {
    key: 'mailbox',
    icon: '郵',
    label: '우편함',
    description: '보상과 안내 우편을 확인하는 공간입니다.',
    nextStep: '우편함 item adapter를 연결한 뒤 열립니다.',
  },
  inventory: {
    key: 'inventory',
    icon: '囊',
    label: '인벤토리',
    description: '장비와 소모품을 빈 칸 그대로 관리합니다.',
    nextStep: '인벤토리·장비 UI 이전 단계에서 열립니다.',
  },
  field: {
    key: 'field',
    icon: '野',
    label: '필드존',
    description: '일반 몬스터와 자동 전투를 시작하는 지역입니다.',
    nextStep: '전투 runtime과 timer를 연결한 뒤 입장할 수 있습니다.',
  },
  boss: {
    key: 'boss',
    icon: '王',
    label: '보스존',
    description: '일반·특수 보스를 선택하고 도전하는 지역입니다.',
    nextStep: '보스 전투 UI와 runtime을 연결한 뒤 입장할 수 있습니다.',
  },
  save: {
    key: 'save',
    icon: '存',
    label: '수동 저장',
    description: '현재 캐릭터의 진행 상태를 서버에 저장합니다.',
    nextStep: 'snapshot load와 단일 저장 queue 단계에서 활성화됩니다.',
  },
};

const SKILL_PRESENTATION = [
  { key: 'lightsabre', slotKey: 'Q', name: '광검 마스터리', tone: 'passive' },
  { key: 'ironStrike', slotKey: 'W', name: '극 귀검술 - 참철식', tone: 'passive' },
  { key: 'overdrive', slotKey: 'E', name: '오버 드라이브', tone: 'buff' },
  { key: 'baldo', slotKey: 'R', name: '발도', tone: 'active' },
  { key: 'illusionSword', slotKey: 'T', name: '환영검무', tone: 'active' },
  { key: 'deepSword', slotKey: 'F', name: '극 귀검술 - 심검', tone: 'active' },
  { key: 'tempestStrike', slotKey: 'D', name: '극 귀검술 - 폭풍식', tone: 'active' },
  { key: 'heavenlyStrike', slotKey: 'M', name: '천제극섬', tone: 'ultimate' },
] as const;

export function createTownHudViewModel(source: TownHudSource): TownHudViewModel {
  const serverState = createDefaultServerState({ defaultCharacterId: source.characterCode });
  serverState.progress.currentZoneType = 'town';
  const summaryGold = toNonNegativeFiniteNumber(source.progress?.gold);
  if (summaryGold !== null) serverState.player.gold = summaryGold;

  const attack = getBaseAttackByAttackSpeed(serverState.player.addAttackSpeed);
  const stats: TownHudStat[] = [
    { key: 'attack', label: '공격력', value: formatCompactNumber(attack), tone: 'attack' },
    { key: 'skill', label: '스킬 피해 증가', value: formatPercent(serverState.player.skillDmgInc), tone: 'skill' },
    { key: 'speed', label: '추가 공격속도', value: formatPercent(serverState.player.addAttackSpeed), tone: 'speed' },
    { key: 'all', label: '모든 피해 증가', value: formatPercent(serverState.player.allDmgInc), tone: 'all' },
    { key: 'basic', label: '평타 피해 증가', value: formatPercent(serverState.player.basicAtkDmgInc), tone: 'basic' },
  ];

  const skills: TownHudSkill[] = SKILL_PRESENTATION.map((item) => ({
    ...item,
    level: serverState.player.skills[item.key]?.level ?? 0,
  }));

  return {
    serverState,
    accountCharacterId: source.accountCharacterId,
    slotKey: source.slotKey,
    characterName: source.characterName,
    characterCode: source.characterCode,
    characterLabel: source.characterLabel,
    avatarText: source.characterName.trim().slice(0, 1) || '검',
    zoneType: 'town',
    zoneLabel: '마을',
    levelLabel: source.progress?.level === null || source.progress?.level === undefined
      ? '저장 없음'
      : `Lv.${Math.max(0, Math.trunc(source.progress.level))}`,
    goldLabel: formatCompactNumber(summaryGold ?? 0),
    recentSaveZoneLabel: formatRecentSaveZone(source.progress),
    updatedAt: source.progress?.updatedAt ?? null,
    stats,
    skills,
    snapshotConnected: false,
  };
}

function toNonNegativeFiniteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.max(0, parsed) : null;
}

function formatPercent(value: unknown): string {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return '0%';
  return `${Number.isInteger(parsed) ? parsed : parsed.toFixed(1).replace(/\.0$/, '')}%`;
}

function formatRecentSaveZone(progress: TownProgressSummary | null): string {
  if (!progress?.currentZoneType) return '최근 저장 구역 없음';
  if (progress.currentZoneType === 'town') return '최근 저장 · 마을';
  if (progress.currentZoneType === 'field') {
    const index = progress.currentZoneIndex === null ? null : Math.max(0, Math.trunc(progress.currentZoneIndex));
    return index === null ? '최근 저장 · 필드존' : `최근 저장 · 필드 ${index + 1}`;
  }
  if (progress.currentZoneType.startsWith('boss')) return '최근 저장 · 보스존';
  return `최근 저장 · ${progress.currentZoneType}`;
}
