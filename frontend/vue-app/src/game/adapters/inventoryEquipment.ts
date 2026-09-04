import type { ItemTemplateOption } from '@/api/contracts';
import {
  addResultLog,
  compactItemSlots,
  countOccupiedItemSlots,
  createGameActionResult,
  findFirstEmptyItemSlot,
  placeItemInFirstEmptySlot,
  type GameActionResult,
  type ItemSlot,
} from '@/game/domain';
import type { TownHudViewModel } from './townHud';

export type ItemFrameTone = 'basic' | 'uncommon' | 'rare' | 'transcendent' | 'liberated' | 'radiant' | 'dark' | 'luminous';
export type InventoryPreviewLocation = 'inventory' | 'equipment';

export interface InventoryItemView {
  code: string;
  name: string;
  iconText: string;
  itemType: string;
  typeLabel: string;
  tier: number | null;
  tierLabel: string;
  frameTone: ItemFrameTone;
  frameLabel: string;
  description: string;
  statSummary: string;
  stackLabel: string;
  equipSlotIndex: number | null;
}

export interface InventorySlotView {
  index: number;
  number: number;
  item: InventoryItemView | null;
}

export interface EquipmentSlotView extends InventorySlotView {
  label: string;
  group: 'normal' | 'special';
}

export interface InventoryEquipmentSource {
  town: TownHudViewModel;
  itemTemplates: ItemTemplateOption[];
  compactPreview: boolean;
  preferredItemCode?: string | null;
  createdAt: number;
}

export interface InventoryEquipmentViewModel {
  zoneType: 'inventory';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  avatarText: string;
  levelLabel: string;
  goldLabel: string;
  equipmentSlots: EquipmentSlotView[];
  inventorySlots: InventorySlotView[];
  selectedItem: InventoryItemView;
  selectedLocation: InventoryPreviewLocation;
  selectedSlotNumber: number;
  occupiedCount: number;
  totalCapacity: 60;
  visibleSlotCount: 24;
  nextEmptySlotNumber: number;
  compactPreview: boolean;
  compactMovedCount: number;
  action: GameActionResult;
  masterDataConnected: true;
  snapshotConnected: false;
  itemMutationConnected: false;
}

const EQUIPMENT_SLOT_LABELS = [
  '스킬·모든 피해', '공격력', '평타 피해', '복합 장비 A', '복합 장비 B', '초보자·여유',
  '특수 무기', '특수 목걸이', '특수 반지', '무기 아바타', '오라 아바타', '클론 레어',
  '탈리스만 A', '탈리스만 B', '휘장',
] as const;
const NORMAL_SLOT_BY_GROUP: Record<string, number> = {
  skill_all: 0,
  atk_inc: 1,
  normal_dmg: 2,
  skill_chance: 3,
  normal_crit: 4,
  beginner: 5,
};
const PREVIEW_INVENTORY_POSITIONS = [0, 2, 5, 6, 10, 14, 18] as const;
const NORMAL_FAMILY_STAGE_TONES: Record<number, ItemFrameTone> = {
  21: 'basic', 22: 'rare', 23: 'transcendent', 24: 'basic', 25: 'rare', 26: 'transcendent',
  30: 'basic', 31: 'rare', 35: 'transcendent', 36: 'liberated',
};
const FRAME_LABELS: Record<ItemFrameTone, string> = {
  basic: '기본', uncommon: '강력', rare: '빛나는', transcendent: '초월', liberated: '해방',
  radiant: '찬란', dark: '심연', luminous: '영롱',
};

export function createInventoryEquipmentViewModel(source: InventoryEquipmentSource): InventoryEquipmentViewModel {
  const items = source.itemTemplates.slice().sort(compareTemplates).map(normalizeInventoryItemTemplate);
  if (!items.length) throw new Error('아이템 master-data가 없습니다.');

  const equipmentSlots = createEquipmentSlots(items);
  const equippedCodes = new Set(equipmentSlots.flatMap((slot) => slot.item ? [slot.item.code] : []));
  const inventoryCandidates = selectInventoryCandidates(items, equippedCodes);
  const spacedSlots: ItemSlot<InventoryItemView>[] = [];
  inventoryCandidates.forEach((item, index) => {
    const target = PREVIEW_INVENTORY_POSITIONS[index] ?? index;
    spacedSlots[target] = item;
  });

  const compacted = compactItemSlots(spacedSlots);
  const displayItems: ItemSlot<InventoryItemView>[] = source.compactPreview ? compacted.slots : spacedSlots.slice();
  const occupiedCount = countOccupiedItemSlots(displayItems);
  const nextEmptyIndex = findFirstEmptyItemSlot(displayItems, 60);
  const incomingPreview = placeItemInFirstEmptySlot(displayItems, items[0], 60);
  if (incomingPreview.index !== nextEmptyIndex) throw new Error('첫 빈 칸 규칙이 일치하지 않습니다.');

  const inventorySlots = Array.from({ length: 24 }, (_, index): InventorySlotView => ({
    index,
    number: index + 1,
    item: displayItems[index] ?? null,
  }));
  const selected = findSelectedItem(equipmentSlots, inventorySlots, source.preferredItemCode);

  return {
    zoneType: 'inventory',
    accountCharacterId: source.town.accountCharacterId,
    characterName: source.town.characterName,
    characterLabel: source.town.characterLabel,
    avatarText: source.town.avatarText,
    levelLabel: source.town.levelLabel,
    goldLabel: source.town.goldLabel,
    equipmentSlots,
    inventorySlots,
    selectedItem: selected.item,
    selectedLocation: selected.location,
    selectedSlotNumber: selected.slotNumber,
    occupiedCount,
    totalCapacity: 60,
    visibleSlotCount: 24,
    nextEmptySlotNumber: nextEmptyIndex + 1,
    compactPreview: source.compactPreview,
    compactMovedCount: compacted.moved,
    action: createInventoryPreviewAction(source.compactPreview, compacted.moved, occupiedCount, source.createdAt),
    masterDataConnected: true,
    snapshotConnected: false,
    itemMutationConnected: false,
  };
}

function compareTemplates(left: ItemTemplateOption, right: ItemTemplateOption): number {
  return left.itemType.localeCompare(right.itemType)
    || resolveTier(left) - resolveTier(right)
    || left.name.localeCompare(right.name)
    || left.code.localeCompare(right.code);
}

export function normalizeInventoryItemTemplate(item: ItemTemplateOption): InventoryItemView {
  const options = asRecord(item.options);
  const raw = asRecord(options.raw);
  const tier = nullableTier(options.tier ?? raw.tier ?? item.grade);
  const equipSlotIndex = resolveEquipmentSlot(item, options, raw);
  const frameTone = resolveFrameTone(item.name, item.itemType, tier);
  return {
    code: item.code,
    name: item.name,
    iconText: item.name.trim().replace(/^[-★\[]+/, '').slice(0, 1) || '物',
    itemType: item.itemType,
    typeLabel: formatTypeLabel(item.itemType),
    tier,
    tierLabel: tier === null ? '등급 정보 없음' : `Tier ${tier}`,
    frameTone,
    frameLabel: FRAME_LABELS[frameTone],
    description: stripMarkup(item.description) || formatDefaultDescription(item.itemType),
    statSummary: formatStatSummary(item.itemType, equipSlotIndex, options, raw),
    stackLabel: item.stackable ? '중첩 가능' : '개별 아이템',
    equipSlotIndex,
  };
}

function createEquipmentSlots(items: InventoryItemView[]): EquipmentSlotView[] {
  const pickedCodes = new Set<string>();
  return EQUIPMENT_SLOT_LABELS.map((label, index) => {
    const item = items.find((candidate) => candidate.equipSlotIndex === index && !pickedCodes.has(candidate.code)) ?? null;
    if (item) pickedCodes.add(item.code);
    return { index, number: index + 1, label, group: index < 6 ? 'normal' : 'special', item };
  });
}

function selectInventoryCandidates(items: InventoryItemView[], equippedCodes: Set<string>): InventoryItemView[] {
  const available = items.filter((item) => !equippedCodes.has(item.code));
  const selected: InventoryItemView[] = [];
  const add = (item: InventoryItemView | undefined) => {
    if (item && !selected.some((current) => current.code === item.code)) selected.push(item);
  };
  add(available.find((item) => item.itemType === 'skill_book'));
  add(available.find((item) => item.itemType === 'special_equip'));
  for (const item of available.filter((candidate) => candidate.itemType === 'normal')) {
    add(item);
    if (selected.length >= 6) break;
  }
  for (const item of available) {
    add(item);
    if (selected.length >= PREVIEW_INVENTORY_POSITIONS.length) break;
  }
  if (!selected.length) selected.push(items[0]);
  return selected.slice(0, PREVIEW_INVENTORY_POSITIONS.length);
}

function findSelectedItem(
  equipment: EquipmentSlotView[],
  inventory: InventorySlotView[],
  preferredItemCode: string | null | undefined,
): { item: InventoryItemView; location: InventoryPreviewLocation; slotNumber: number } {
  const inventoryMatch = inventory.find((slot) => slot.item?.code === preferredItemCode);
  if (inventoryMatch?.item) return { item: inventoryMatch.item, location: 'inventory', slotNumber: inventoryMatch.number };
  const equipmentMatch = equipment.find((slot) => slot.item?.code === preferredItemCode);
  if (equipmentMatch?.item) return { item: equipmentMatch.item, location: 'equipment', slotNumber: equipmentMatch.number };
  const firstInventory = inventory.find((slot) => slot.item);
  if (firstInventory?.item) return { item: firstInventory.item, location: 'inventory', slotNumber: firstInventory.number };
  const firstEquipment = equipment.find((slot) => slot.item);
  if (firstEquipment?.item) return { item: firstEquipment.item, location: 'equipment', slotNumber: firstEquipment.number };
  throw new Error('표시할 아이템이 없습니다.');
}

function createInventoryPreviewAction(compact: boolean, moved: number, occupied: number, createdAt: number): GameActionResult {
  const result = createGameActionResult(compact ? 'inventory.preview.compact' : 'inventory.preview.open', {
    mode: 'display-only',
    compact,
    moved,
    occupied,
  }, createdAt);
  return addResultLog(result, compact
    ? `[정렬 미리보기] ${occupied}개 아이템의 상대 순서를 유지하며 빈 칸 ${moved}곳을 앞당겼습니다.`
    : '[미리보기] 실제 보유 데이터가 아닌 master-data 샘플 배치를 열었습니다.');
}

function resolveEquipmentSlot(item: ItemTemplateOption, options: Record<string, unknown>, raw: Record<string, unknown>): number | null {
  if (item.itemType === 'skill_book') return null;
  const specialIndex = nullableInteger(options.specialSlotIdx ?? raw.specialSlotIdx ?? item.equipSlot);
  if (item.itemType === 'special_equip' && specialIndex !== null && specialIndex >= 6 && specialIndex <= 14) return specialIndex;
  const group = stringValue(options.equipGroup ?? raw.equipGroup ?? item.equipSlot);
  return NORMAL_SLOT_BY_GROUP[group] ?? null;
}

function resolveTier(item: ItemTemplateOption): number {
  const options = asRecord(item.options);
  const raw = asRecord(options.raw);
  return nullableTier(options.tier ?? raw.tier ?? item.grade) ?? Number.MAX_SAFE_INTEGER;
}

function resolveFrameTone(name: string, itemType: string, tier: number | null): ItemFrameTone {
  if (itemType === 'normal' && tier !== null && NORMAL_FAMILY_STAGE_TONES[tier]) return NORMAL_FAMILY_STAGE_TONES[tier];
  if (name.startsWith('★초월 연옥★')) return 'luminous';
  if (name.startsWith('★진 연옥★') || name.startsWith('★심연★')) return 'dark';
  if (name.startsWith('★연옥★')) return 'radiant';
  if (name.startsWith('-초월-')) return 'transcendent';
  if (name.startsWith('-진-')) return 'rare';
  if (name.startsWith('-현-')) return 'uncommon';
  if (name.startsWith('[기본]')) return 'basic';
  if (name.includes('영롱') || name.includes('천공') || name.includes('진 각성')) return 'luminous';
  if (name.includes('짙은') || name === '심연의 스킬강화권') return 'dark';
  if (name.includes('찬란') || name.includes('화려')) return 'radiant';
  if (name.includes('해방')) return 'liberated';
  if (name.includes('초월')) return 'transcendent';
  if (name.includes('빛나는')) return 'rare';
  if (name.includes('강력한')) return 'uncommon';
  return 'basic';
}

function formatTypeLabel(itemType: string): string {
  if (itemType === 'normal') return '일반 장비';
  if (itemType === 'special_equip') return '특수 장비';
  if (itemType === 'skill_book') return '스킬 강화권';
  return '아이템';
}

function formatDefaultDescription(itemType: string): string {
  if (itemType === 'skill_book') return '스킬 레벨 성장에 사용하는 강화권입니다.';
  if (itemType === 'special_equip') return '전용 슬롯에 장착하는 특수 장비입니다.';
  return '캐릭터 능력치를 높이는 장비입니다.';
}

function formatStatSummary(
  itemType: string,
  equipSlotIndex: number | null,
  options: Record<string, unknown>,
  raw: Record<string, unknown>,
): string {
  if (itemType === 'skill_book') return '스킬 성장 재료';
  if (equipSlotIndex !== null) return `${EQUIPMENT_SLOT_LABELS[equipSlotIndex]} 슬롯 대상`;
  const group = stringValue(options.equipGroup ?? raw.equipGroup);
  return group ? `장비 그룹 · ${group}` : '상세 능력치는 보유 장비 snapshot 매핑 뒤 계산';
}

function nullableTier(value: unknown): number | null {
  const parsed = Number(value);
  return value === null || value === undefined || value === '' || !Number.isFinite(parsed) ? null : Math.max(0, Math.trunc(parsed));
}

function nullableInteger(value: unknown): number | null {
  const parsed = Number(value);
  return value === null || value === undefined || value === '' || !Number.isFinite(parsed) ? null : Math.trunc(parsed);
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function stringValue(value: unknown): string {
  return typeof value === 'string' || typeof value === 'number' ? String(value).trim() : '';
}

function stripMarkup(value: unknown): string {
  return stringValue(value).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}
