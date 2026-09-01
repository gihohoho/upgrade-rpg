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
import {
  normalizeInventoryItemTemplate,
  type InventoryEquipmentViewModel,
  type InventoryItemView,
  type InventorySlotView,
} from './inventoryEquipment';

export type StorageTrashContainerKey = 'storage' | 'trash';

export interface StorageTrashContainerView {
  key: StorageTrashContainerKey;
  label: string;
  capacity: 60;
  visibleSlotCount: 20;
  occupiedCount: number;
  nextEmptySlotNumber: number;
  compactPreview: boolean;
  compactMovedCount: number;
  slots: InventorySlotView[];
}

export interface StorageTrashSource {
  inventory: InventoryEquipmentViewModel;
  itemTemplates: ItemTemplateOption[];
  storageCompactPreview: boolean;
  trashCompactPreview: boolean;
  preferredItemCode?: string | null;
  preferredContainer?: StorageTrashContainerKey | null;
  lastActionContainer?: StorageTrashContainerKey | null;
  createdAt: number;
}

export interface StorageTrashViewModel {
  zoneType: 'storage-trash';
  accountCharacterId: string;
  characterName: string;
  characterLabel: string;
  avatarText: string;
  levelLabel: string;
  goldLabel: string;
  storage: StorageTrashContainerView;
  trash: StorageTrashContainerView;
  selectedItem: InventoryItemView;
  selectedContainer: StorageTrashContainerKey;
  selectedSlotNumber: number;
  action: GameActionResult;
  masterDataConnected: true;
  snapshotConnected: false;
  itemMutationConnected: false;
  permanentDeleteConnected: false;
}

const STORAGE_POSITIONS = [0, 2, 6, 11, 15, 18] as const;
const TRASH_POSITIONS = [0, 4, 5, 10, 14, 18] as const;

export function createStorageTrashViewModel(source: StorageTrashSource): StorageTrashViewModel {
  const items = source.itemTemplates
    .map(normalizeInventoryItemTemplate)
    .sort((left, right) => left.itemType.localeCompare(right.itemType)
      || (left.tier ?? Number.MAX_SAFE_INTEGER) - (right.tier ?? Number.MAX_SAFE_INTEGER)
      || left.name.localeCompare(right.name)
      || left.code.localeCompare(right.code));
  if (!items.length) throw new Error('보관함·휴지통 미리보기에 사용할 아이템 master-data가 없습니다.');

  const storageItems = selectDiverseItems(items, new Set(), STORAGE_POSITIONS.length);
  const storageCodes = new Set(storageItems.map((item) => item.code));
  const trashItems = selectDiverseItems(items, storageCodes, TRASH_POSITIONS.length);
  const safeTrashItems = trashItems.length ? trashItems : storageItems.slice(0, 1);
  const storage = createContainerView('storage', storageItems, STORAGE_POSITIONS, source.storageCompactPreview);
  const trash = createContainerView('trash', safeTrashItems, TRASH_POSITIONS, source.trashCompactPreview);
  const selected = findSelectedItem(storage, trash, source.preferredContainer, source.preferredItemCode);

  return {
    zoneType: 'storage-trash',
    accountCharacterId: source.inventory.accountCharacterId,
    characterName: source.inventory.characterName,
    characterLabel: source.inventory.characterLabel,
    avatarText: source.inventory.avatarText,
    levelLabel: source.inventory.levelLabel,
    goldLabel: source.inventory.goldLabel,
    storage,
    trash,
    selectedItem: selected.item,
    selectedContainer: selected.container,
    selectedSlotNumber: selected.slotNumber,
    action: createPreviewAction(source.lastActionContainer ?? null, storage, trash, source.createdAt),
    masterDataConnected: true,
    snapshotConnected: false,
    itemMutationConnected: false,
    permanentDeleteConnected: false,
  };
}

function createContainerView(
  key: StorageTrashContainerKey,
  items: InventoryItemView[],
  positions: readonly number[],
  compactPreview: boolean,
): StorageTrashContainerView {
  const spacedSlots: ItemSlot<InventoryItemView>[] = [];
  items.forEach((item, index) => {
    spacedSlots[positions[index] ?? index] = item;
  });
  const compacted = compactItemSlots(spacedSlots);
  const displayItems: ItemSlot<InventoryItemView>[] = compactPreview ? compacted.slots : spacedSlots.slice();
  const occupiedCount = countOccupiedItemSlots(displayItems);
  const nextEmptyIndex = findFirstEmptyItemSlot(displayItems, 60);
  if (items[0]) {
    const incomingPreview = placeItemInFirstEmptySlot(displayItems, items[0], 60);
    if (incomingPreview.index !== nextEmptyIndex) throw new Error(`${containerLabel(key)} 첫 빈 칸 규칙이 일치하지 않습니다.`);
  }
  return {
    key,
    label: containerLabel(key),
    capacity: 60,
    visibleSlotCount: 20,
    occupiedCount,
    nextEmptySlotNumber: nextEmptyIndex + 1,
    compactPreview,
    compactMovedCount: compacted.moved,
    slots: Array.from({ length: 20 }, (_, index): InventorySlotView => ({
      index,
      number: index + 1,
      item: displayItems[index] ?? null,
    })),
  };
}

function selectDiverseItems(
  items: InventoryItemView[],
  excludedCodes: Set<string>,
  limit: number,
): InventoryItemView[] {
  const available = items.filter((item) => !excludedCodes.has(item.code));
  const selected: InventoryItemView[] = [];
  const add = (item: InventoryItemView | undefined) => {
    if (item && !selected.some((current) => current.code === item.code)) selected.push(item);
  };
  add(available.find((item) => item.itemType === 'skill_book'));
  add(available.find((item) => item.itemType === 'special_equip'));
  add(available.find((item) => item.frameTone === 'liberated'));
  add(available.find((item) => item.frameTone === 'transcendent'));
  add(available.find((item) => item.frameTone === 'rare'));
  add(available.find((item) => item.frameTone === 'basic'));
  for (const item of available) {
    add(item);
    if (selected.length >= limit) break;
  }
  return selected.slice(0, limit);
}

function findSelectedItem(
  storage: StorageTrashContainerView,
  trash: StorageTrashContainerView,
  preferredContainer: StorageTrashContainerKey | null | undefined,
  preferredItemCode: string | null | undefined,
): { item: InventoryItemView; container: StorageTrashContainerKey; slotNumber: number } {
  const containers = preferredContainer === 'trash' ? [trash, storage] : [storage, trash];
  for (const container of containers) {
    const match = container.slots.find((slot) => slot.item?.code === preferredItemCode);
    if (match?.item) return { item: match.item, container: container.key, slotNumber: match.number };
  }
  for (const container of containers) {
    const first = container.slots.find((slot) => slot.item);
    if (first?.item) return { item: first.item, container: container.key, slotNumber: first.number };
  }
  throw new Error('보관함·휴지통에 표시할 아이템이 없습니다.');
}

function createPreviewAction(
  lastActionContainer: StorageTrashContainerKey | null,
  storage: StorageTrashContainerView,
  trash: StorageTrashContainerView,
  createdAt: number,
): GameActionResult {
  const target = lastActionContainer === 'trash' ? trash : storage;
  const type = lastActionContainer ? `storage-trash.preview.compact-${lastActionContainer}` : 'storage-trash.preview.open';
  const result = createGameActionResult(type, {
    mode: 'display-only',
    container: lastActionContainer,
    storageOccupied: storage.occupiedCount,
    trashOccupied: trash.occupiedCount,
    moved: lastActionContainer ? target.compactMovedCount : 0,
  }, createdAt);
  if (!lastActionContainer) {
    return addResultLog(result, '[미리보기] 실제 보유 데이터가 아닌 master-data 샘플로 보관함과 휴지통을 열었습니다.');
  }
  return addResultLog(
    result,
    `[정렬 미리보기] ${target.label} ${target.occupiedCount}개 아이템의 상대 순서를 유지하며 빈 칸 ${target.compactMovedCount}곳을 앞당겼습니다.`,
  );
}

function containerLabel(key: StorageTrashContainerKey): string {
  return key === 'storage' ? '보관함' : '휴지통';
}
