import { computed, ref, shallowRef } from 'vue';
import { defineStore } from 'pinia';
import type { AccountCharacterSlot, BossOption, FieldZoneOption, ItemTemplateOption } from '@/api/contracts';
import { createBossCombatViewModel, type BossCombatViewModel } from '@/game/adapters/bossCombat';
import { createFieldCombatViewModel, type FieldCombatViewModel } from '@/game/adapters/fieldCombat';
import {
  createInventoryEquipmentViewModel,
  type InventoryEquipmentViewModel,
} from '@/game/adapters/inventoryEquipment';
import {
  createTownHudViewModel,
  TOWN_FEATURES,
  type TownFeatureKey,
  type TownHudViewModel,
} from '@/game/adapters/townHud';

export const useGameStore = defineStore('game', () => {
  const model = shallowRef<TownHudViewModel | null>(null);
  const fieldModel = shallowRef<FieldCombatViewModel | null>(null);
  const fieldZoneSources = shallowRef<FieldZoneOption[]>([]);
  const bossModel = shallowRef<BossCombatViewModel | null>(null);
  const bossSources = shallowRef<BossOption[]>([]);
  const inventoryModel = shallowRef<InventoryEquipmentViewModel | null>(null);
  const itemTemplateSources = shallowRef<ItemTemplateOption[]>([]);
  const inventoryCompactedPreview = ref(false);
  const selectedInventoryItemCode = ref<string | null>(null);
  const screen = ref<'town' | 'field' | 'boss' | 'inventory'>('town');
  const contextSignature = ref('');
  const activeFeatureKey = ref<TownFeatureKey | null>(null);

  const activeFeature = computed(() => (
    activeFeatureKey.value ? TOWN_FEATURES[activeFeatureKey.value] : null
  ));
  const isTown = computed(() => screen.value === 'town' && model.value?.zoneType === 'town');
  const isField = computed(() => screen.value === 'field' && fieldModel.value?.zoneType === 'field');
  const isBoss = computed(() => screen.value === 'boss' && bossModel.value?.zoneType === 'boss');
  const isInventory = computed(() => screen.value === 'inventory' && inventoryModel.value?.zoneType === 'inventory');

  function enterTown(slot: AccountCharacterSlot, characterLabel: string) {
    if (!slot.occupied || !slot.accountCharacterId || !slot.accountCharacter) {
      resetShell();
      return;
    }
    const signature = [
      slot.accountCharacterId,
      slot.slotKey,
      slot.progress?.updatedAt ?? '',
      characterLabel,
    ].join(':');
    screen.value = 'town';
    if (signature === contextSignature.value && model.value) return;
    model.value = createTownHudViewModel({
      accountCharacterId: slot.accountCharacterId,
      slotKey: slot.slotKey,
      characterName: slot.accountCharacter.name,
      characterCode: slot.accountCharacter.characterCode,
      characterLabel,
      progress: slot.progress,
    });
    contextSignature.value = signature;
    fieldModel.value = null;
    fieldZoneSources.value = [];
    bossModel.value = null;
    bossSources.value = [];
    inventoryModel.value = null;
    itemTemplateSources.value = [];
    inventoryCompactedPreview.value = false;
    selectedInventoryItemCode.value = null;
    activeFeatureKey.value = null;
  }

  function enterFieldPreview(zones: FieldZoneOption[]) {
    if (!model.value || !zones.length) return false;
    fieldZoneSources.value = zones.slice();
    const preferredIndex = model.value.recentSaveZoneType === 'field'
      ? model.value.recentSaveZoneIndex
      : 0;
    fieldModel.value = createFieldCombatViewModel({
      town: model.value,
      fieldZones: fieldZoneSources.value,
      preferredIndex,
      createdAt: 0,
    });
    screen.value = 'field';
    activeFeatureKey.value = null;
    return true;
  }

  function selectFieldPreview(index: number) {
    if (!model.value || !fieldZoneSources.value.length) return;
    fieldModel.value = createFieldCombatViewModel({
      town: model.value,
      fieldZones: fieldZoneSources.value,
      preferredIndex: index,
      createdAt: 0,
    });
  }

  function enterBossPreview(bosses: BossOption[]) {
    if (!model.value || !bosses.length) return false;
    bossSources.value = bosses.slice();
    bossModel.value = createBossCombatViewModel({
      town: model.value,
      bosses: bossSources.value,
      preferredIndex: 0,
      createdAt: 0,
    });
    screen.value = 'boss';
    activeFeatureKey.value = null;
    return true;
  }

  function selectBossPreview(index: number) {
    if (!model.value || !bossSources.value.length) return;
    bossModel.value = createBossCombatViewModel({
      town: model.value,
      bosses: bossSources.value,
      preferredIndex: index,
      createdAt: 0,
    });
  }

  function enterInventoryPreview(itemTemplates: ItemTemplateOption[]) {
    if (!model.value || !itemTemplates.length) return false;
    itemTemplateSources.value = itemTemplates.slice();
    inventoryCompactedPreview.value = false;
    selectedInventoryItemCode.value = null;
    rebuildInventoryPreview();
    screen.value = 'inventory';
    activeFeatureKey.value = null;
    return true;
  }

  function selectInventoryPreview(itemCode: string) {
    if (!itemTemplateSources.value.length) return;
    selectedInventoryItemCode.value = itemCode;
    rebuildInventoryPreview();
  }

  function toggleInventoryCompactPreview() {
    if (!itemTemplateSources.value.length) return;
    inventoryCompactedPreview.value = !inventoryCompactedPreview.value;
    rebuildInventoryPreview();
  }

  function rebuildInventoryPreview() {
    if (!model.value || !itemTemplateSources.value.length) return;
    inventoryModel.value = createInventoryEquipmentViewModel({
      town: model.value,
      itemTemplates: itemTemplateSources.value,
      compactPreview: inventoryCompactedPreview.value,
      preferredItemCode: selectedInventoryItemCode.value,
      createdAt: 0,
    });
    selectedInventoryItemCode.value = inventoryModel.value.selectedItem.code;
  }

  function returnTown() {
    screen.value = 'town';
    fieldModel.value = null;
    bossModel.value = null;
    inventoryModel.value = null;
  }

  function openFeature(key: TownFeatureKey) {
    activeFeatureKey.value = key;
  }

  function closeFeature() {
    activeFeatureKey.value = null;
  }

  function resetShell() {
    model.value = null;
    fieldModel.value = null;
    fieldZoneSources.value = [];
    bossModel.value = null;
    bossSources.value = [];
    inventoryModel.value = null;
    itemTemplateSources.value = [];
    inventoryCompactedPreview.value = false;
    selectedInventoryItemCode.value = null;
    screen.value = 'town';
    contextSignature.value = '';
    activeFeatureKey.value = null;
  }

  return {
    model,
    fieldModel,
    bossModel,
    inventoryModel,
    activeFeature,
    isTown,
    isField,
    isBoss,
    isInventory,
    enterTown,
    enterFieldPreview,
    selectFieldPreview,
    enterBossPreview,
    selectBossPreview,
    enterInventoryPreview,
    selectInventoryPreview,
    toggleInventoryCompactPreview,
    returnTown,
    openFeature,
    closeFeature,
    resetShell,
  };
});
