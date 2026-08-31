import type { ItemSlot } from './types';

export interface SlotMutationResult<T> {
  slots: ItemSlot<T>[];
  index: number;
}

export interface SlotClearResult<T> extends SlotMutationResult<T> {
  item: T | null;
}

export interface SlotCompactResult<T> {
  slots: T[];
  moved: number;
  occupied: number;
}

export function countOccupiedItemSlots<T>(items: unknown): number {
  if (!Array.isArray(items)) return 0;
  return items.reduce<number>((count, item) => count + (item ? 1 : 0), 0);
}

export function trimTrailingEmptyItemSlots<T>(items: ItemSlot<T>[]): ItemSlot<T>[] {
  const slots = [...items];
  while (slots.length > 0 && !slots[slots.length - 1]) slots.pop();
  return slots;
}

export function findFirstEmptyItemSlot<T>(items: ItemSlot<T>[], maxSize: unknown): number {
  const safeMaxSize = normalizeCapacity(maxSize);
  for (let index = 0; index < safeMaxSize; index += 1) {
    if (!items[index]) return index;
  }
  return -1;
}

export function hasEmptyItemSlot<T>(items: ItemSlot<T>[], maxSize: unknown): boolean {
  return findFirstEmptyItemSlot(items, maxSize) !== -1;
}

export function placeItemInFirstEmptySlot<T>(items: ItemSlot<T>[], item: T | null | undefined, maxSize: unknown): SlotMutationResult<T> {
  const slots = [...items];
  if (!item) return { slots, index: -1 };
  const index = findFirstEmptyItemSlot(slots, maxSize);
  if (index !== -1) slots[index] = item;
  return { slots, index };
}

export function clearItemSlot<T>(items: ItemSlot<T>[], index: number): SlotClearResult<T> {
  const slots = [...items];
  if (index < 0 || !slots[index]) return { slots, index: -1, item: null };
  const item = slots[index] as T;
  slots[index] = null;
  return { slots: trimTrailingEmptyItemSlots(slots), index, item };
}

export function compactItemSlots<T>(items: ItemSlot<T>[]): SlotCompactResult<T> {
  const occupiedItems = items.filter(Boolean) as T[];
  const moved = occupiedItems.reduce((count, item, index) => count + (items[index] !== item ? 1 : 0), 0);
  return { slots: occupiedItems, moved, occupied: occupiedItems.length };
}

function normalizeCapacity(value: unknown) {
  const parsed = Number.parseInt(String(value ?? ''), 10);
  return Math.max(0, Number.isFinite(parsed) ? parsed : 0);
}
