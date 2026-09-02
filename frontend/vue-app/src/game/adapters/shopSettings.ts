import type { ItemTemplateOption } from '@/api/contracts';
import { addResultLog, createGameActionResult, type GameActionResult } from '@/game/domain';
import { normalizeInventoryItemTemplate, type InventoryItemView } from './inventoryEquipment';
import type { TownHudViewModel } from './townHud';

export type ShopCategoryKey = 'all' | 'normal' | 'special_equip' | 'skill_book';
export type SettingPreviewKey = 'autoBossSummon' | 'autoSpecialBossEnabled' | 'equipDropEnabled';

export interface SettingPreviewState {
  autoBossSummon: boolean;
  autoSpecialBossEnabled: boolean;
  equipDropEnabled: boolean;
}

export interface ShopCatalogItemView extends InventoryItemView {
  baseCost: number | null;
  baseCostLabel: string;
  sellPrice: number | null;
  sellPriceLabel: string;
  purchasePriceLabel: '구매 가격 미등록';
  pricingStatus: 'reference-only' | 'unpriced';
}

export interface ShopCategoryView {
  key: ShopCategoryKey;
  label: string;
  count: number;
}

export interface SettingPreviewView {
  key: SettingPreviewKey;
  label: string;
  description: string;
  caution: string;
  enabled: boolean;
  defaultEnabled: boolean;
  changed: boolean;
}

export interface ShopSettingsSource {
  town: TownHudViewModel;
  itemTemplates: ItemTemplateOption[];
  preferredCategory?: ShopCategoryKey | null;
  preferredItemCode?: string | null;
  settingPreview?: SettingPreviewState;
  lastAction?: string | null;
  createdAt: number;
}

export interface ShopSettingsViewModel {
  zoneType: 'shop-settings';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  levelLabel: string;
  goldLabel: string;
  categories: ShopCategoryView[];
  selectedCategory: ShopCategoryKey;
  catalogItems: ShopCatalogItemView[];
  visibleItems: ShopCatalogItemView[];
  selectedItem: ShopCatalogItemView;
  pricedReferenceCount: number;
  settings: SettingPreviewView[];
  changedSettingCount: number;
  action: GameActionResult;
  masterDataConnected: true;
  commerceConnected: false;
  runtimeConnected: false;
  persistenceConnected: false;
}

export const DEFAULT_SETTING_PREVIEW: Readonly<SettingPreviewState> = Object.freeze({
  autoBossSummon: false,
  autoSpecialBossEnabled: false,
  equipDropEnabled: true,
});

const CATEGORY_LABELS: Record<ShopCategoryKey, string> = {
  all: '전체',
  normal: '일반 장비',
  special_equip: '특수 장비',
  skill_book: '스킬 강화권',
};

const SETTING_DEFINITIONS: Array<Omit<SettingPreviewView, 'enabled' | 'changed'>> = [
  {
    key: 'autoBossSummon',
    label: '일반 보스 자동 소환',
    description: '일반 보스를 처치한 뒤 다음 보스를 자동으로 소환하는 기존 옵션입니다.',
    caution: '전투 runtime 연결 전이라 현재 전투에는 반영되지 않습니다.',
    defaultEnabled: DEFAULT_SETTING_PREVIEW.autoBossSummon,
  },
  {
    key: 'autoSpecialBossEnabled',
    label: '특수 보스 자동 사냥',
    description: '선택한 특수 보스의 쿨타임이 끝나면 이동하는 기존 옵션입니다.',
    caution: '대상 보스 선택과 자동 이동은 전투 runtime 단계에서 연결합니다.',
    defaultEnabled: DEFAULT_SETTING_PREVIEW.autoSpecialBossEnabled,
  },
  {
    key: 'equipDropEnabled',
    label: '일반 보스 장비 드랍',
    description: '일반 보스의 장비 드랍 여부를 정하는 기존 옵션입니다.',
    caution: '특수 보스는 이 설정과 관계없이 항상 드랍하는 기존 규칙을 유지합니다.',
    defaultEnabled: DEFAULT_SETTING_PREVIEW.equipDropEnabled,
  },
];

export function createShopSettingsViewModel(source: ShopSettingsSource): ShopSettingsViewModel {
  const catalogItems = source.itemTemplates
    .slice()
    .sort(compareTemplates)
    .map(toCatalogItem);
  if (!catalogItems.length) throw new Error('상점에 표시할 아이템 master-data가 없습니다.');

  const selectedCategory = normalizeCategory(source.preferredCategory, catalogItems);
  const visibleItems = selectedCategory === 'all'
    ? catalogItems
    : catalogItems.filter((item) => item.itemType === selectedCategory);
  const selectedItem = visibleItems.find((item) => item.code === source.preferredItemCode) ?? visibleItems[0];
  if (!selectedItem) throw new Error('선택한 상점 분류에 표시할 아이템이 없습니다.');

  const settingPreview = normalizeSettingPreview(source.settingPreview);
  const settings = SETTING_DEFINITIONS.map((definition): SettingPreviewView => ({
    ...definition,
    enabled: settingPreview[definition.key],
    changed: settingPreview[definition.key] !== definition.defaultEnabled,
  }));

  return {
    zoneType: 'shop-settings',
    accountCharacterId: source.town.accountCharacterId,
    characterName: source.town.characterName,
    characterLabel: source.town.characterLabel,
    levelLabel: source.town.levelLabel,
    goldLabel: source.town.goldLabel,
    categories: (Object.keys(CATEGORY_LABELS) as ShopCategoryKey[]).map((key) => ({
      key,
      label: CATEGORY_LABELS[key],
      count: key === 'all' ? catalogItems.length : catalogItems.filter((item) => item.itemType === key).length,
    })).filter((category) => category.key === 'all' || category.count > 0),
    selectedCategory,
    catalogItems,
    visibleItems,
    selectedItem,
    pricedReferenceCount: catalogItems.filter((item) => item.baseCost !== null || item.sellPrice !== null).length,
    settings,
    changedSettingCount: settings.filter((setting) => setting.changed).length,
    action: createPreviewAction(source.lastAction, selectedCategory, selectedItem, settings, source.createdAt),
    masterDataConnected: true,
    commerceConnected: false,
    runtimeConnected: false,
    persistenceConnected: false,
  };
}

export function cloneDefaultSettingPreview(): SettingPreviewState {
  return { ...DEFAULT_SETTING_PREVIEW };
}

function toCatalogItem(item: ItemTemplateOption): ShopCatalogItemView {
  const normalized = normalizeInventoryItemTemplate(item);
  const options = asRecord(item.options);
  const raw = asRecord(options.raw);
  const baseCost = nullablePrice(options.baseCost ?? raw.baseCost);
  const sellPrice = nullablePrice(options.sellPrice ?? raw.sellPrice);
  return {
    ...normalized,
    baseCost,
    baseCostLabel: baseCost === null ? '강화 기준 비용 미등록' : `${formatNumber(baseCost)} Gold`,
    sellPrice,
    sellPriceLabel: sellPrice === null ? '판매 값 미등록' : `${formatNumber(sellPrice)} Gold`,
    purchasePriceLabel: '구매 가격 미등록',
    pricingStatus: baseCost !== null || sellPrice !== null ? 'reference-only' : 'unpriced',
  };
}

function normalizeCategory(category: ShopCategoryKey | null | undefined, items: ShopCatalogItemView[]): ShopCategoryKey {
  if (category && (category === 'all' || items.some((item) => item.itemType === category))) return category;
  return 'all';
}

function normalizeSettingPreview(input: SettingPreviewState | undefined): SettingPreviewState {
  return {
    autoBossSummon: Boolean(input?.autoBossSummon ?? DEFAULT_SETTING_PREVIEW.autoBossSummon),
    autoSpecialBossEnabled: Boolean(input?.autoSpecialBossEnabled ?? DEFAULT_SETTING_PREVIEW.autoSpecialBossEnabled),
    equipDropEnabled: Boolean(input?.equipDropEnabled ?? DEFAULT_SETTING_PREVIEW.equipDropEnabled),
  };
}

function createPreviewAction(
  lastAction: string | null | undefined,
  category: ShopCategoryKey,
  item: ShopCatalogItemView,
  settings: SettingPreviewView[],
  createdAt: number,
): GameActionResult {
  const result = createGameActionResult('shop-settings.preview', {
    mode: 'display-only',
    category,
    itemCode: item.code,
    changedSettingCount: settings.filter((setting) => setting.changed).length,
  }, createdAt);
  const message = lastAction
    ? `[설정 미리보기] ${lastAction} 화면 상태만 바꿨습니다.`
    : `[상점 미리보기] ${item.name}의 등록된 비용 정보만 읽었습니다.`;
  return addResultLog(result, message);
}

function compareTemplates(left: ItemTemplateOption, right: ItemTemplateOption): number {
  return categoryOrder(left.itemType) - categoryOrder(right.itemType)
    || resolveTier(left) - resolveTier(right)
    || left.name.localeCompare(right.name)
    || left.code.localeCompare(right.code);
}

function categoryOrder(itemType: string): number {
  if (itemType === 'normal') return 0;
  if (itemType === 'special_equip') return 1;
  if (itemType === 'skill_book') return 2;
  return 3;
}

function resolveTier(item: ItemTemplateOption): number {
  const options = asRecord(item.options);
  const raw = asRecord(options.raw);
  const parsed = Number(options.tier ?? raw.tier ?? item.grade);
  return Number.isFinite(parsed) ? parsed : Number.MAX_SAFE_INTEGER;
}

function nullablePrice(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 0 }).format(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}
