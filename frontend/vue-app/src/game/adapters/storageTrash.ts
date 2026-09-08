import type { ItemTemplateOption } from '@/api/contracts';
import {
  addResultLog,
  createGameActionResult,
  type GameActionResult,
  type PlayerState,
} from '@/game/domain';
import {
  createOwnedContainer,
  type InventoryEquipmentViewModel,
  type InventoryItemView,
  type InventorySlotView,
} from './inventoryEquipment';

export type StorageTrashContainerKey = 'storage' | 'trash';

export interface StorageTrashContainerView {
  key: StorageTrashContainerKey;
  label: string;
  capacity: number;
  visibleSlotCount: number;
  occupiedCount: number;
  nextEmptySlotNumber: number;
  compactPreview: boolean;
  compactMovedCount: number;
  slots: InventorySlotView[];
}

export interface StorageTrashSource {
  inventory: InventoryEquipmentViewModel;
  itemTemplates: ItemTemplateOption[];
  player: PlayerState;
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
  selectedItem: InventoryItemView | null;
  selectedContainer: StorageTrashContainerKey;
  selectedSlotNumber: number;
  action: GameActionResult;
  masterDataConnected: boolean;
  snapshotConnected: true;
  itemMutationConnected: true;
  permanentDeleteConnected: false;
}

export function createStorageTrashViewModel(source: StorageTrashSource): StorageTrashViewModel {
  const storage = createContainerView('storage', source, source.storageCompactPreview);
  const trash = createContainerView('trash', source, source.trashCompactPreview);
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
    masterDataConnected: source.itemTemplates.length > 0,
    snapshotConnected: true,
    itemMutationConnected: true,
    permanentDeleteConnected: false,
  };
}

function createContainerView(key: StorageTrashContainerKey, source: StorageTrashSource, compactPreview: boolean): StorageTrashContainerView {
  const view = createOwnedContainer(source.player[key], source.player.maxStorageSize, source.itemTemplates, key, compactPreview);
  return { ...view, key, label: containerLabel(key), visibleSlotCount: view.slots.length, compactPreview };
}

function findSelectedItem(
  storage: StorageTrashContainerView,
  trash: StorageTrashContainerView,
  preferredContainer: StorageTrashContainerKey | null | undefined,
  preferredItemCode: string | null | undefined,
): { item: InventoryItemView | null; container: StorageTrashContainerKey; slotNumber: number } {
  const containers = preferredContainer === 'trash' ? [trash, storage] : [storage, trash];
  for (const container of containers) {
    const match = container.slots.find((slot) => slot.item?.selectionKey === preferredItemCode);
    if (match?.item) return { item: match.item, container: container.key, slotNumber: match.number };
  }
  for (const container of containers) {
    const first = container.slots.find((slot) => slot.item);
    if (first?.item) return { item: first.item, container: container.key, slotNumber: first.number };
  }
  return { item: null, container: preferredContainer ?? 'storage', slotNumber: 0 };
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
    return addResultLog(result, '[보유 목록] 선택 캐릭터의 저장된 보관함과 휴지통을 읽었습니다.');
  }
  return addResultLog(
    result,
    `[정렬 미리보기] ${target.label} ${target.occupiedCount}개 아이템의 상대 순서를 유지하며 빈 칸 ${target.compactMovedCount}곳을 앞당겼습니다.`,
  );
}

function containerLabel(key: StorageTrashContainerKey): string {
  return key === 'storage' ? '보관함' : '휴지통';
}
