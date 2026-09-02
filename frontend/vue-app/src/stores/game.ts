import { computed, ref, shallowRef } from 'vue';
import { defineStore } from 'pinia';
import type {
  AccountCharacterSlot,
  BossOption,
  CharacterSkillOption,
  EnhancementGroupOption,
  EnhancementLevelOption,
  FieldZoneOption,
  ItemTemplateOption,
  SkillLevelOption,
  SkillOption,
} from '@/api/contracts';
import { createBossCombatViewModel, type BossCombatViewModel } from '@/game/adapters/bossCombat';
import { createFieldCombatViewModel, type FieldCombatViewModel } from '@/game/adapters/fieldCombat';
import {
  createInventoryEquipmentViewModel,
  type InventoryEquipmentViewModel,
} from '@/game/adapters/inventoryEquipment';
import {
  createStorageTrashViewModel,
  type StorageTrashContainerKey,
  type StorageTrashViewModel,
} from '@/game/adapters/storageTrash';
import {
  createSkillEnhancementViewModel,
  type SkillEnhancementViewModel,
} from '@/game/adapters/skillEnhancement';
import {
  cloneDefaultSettingPreview,
  createShopSettingsViewModel,
  type SettingPreviewKey,
  type SettingPreviewState,
  type ShopCategoryKey,
  type ShopSettingsViewModel,
} from '@/game/adapters/shopSettings';
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
  const storageTrashModel = shallowRef<StorageTrashViewModel | null>(null);
  const storageCompactedPreview = ref(false);
  const trashCompactedPreview = ref(false);
  const selectedStorageTrashItemCode = ref<string | null>(null);
  const selectedStorageTrashContainer = ref<StorageTrashContainerKey | null>(null);
  const storageTrashLastAction = ref<StorageTrashContainerKey | null>(null);
  const skillEnhancementModel = shallowRef<SkillEnhancementViewModel | null>(null);
  const skillSources = shallowRef<SkillOption[]>([]);
  const characterSkillSources = shallowRef<CharacterSkillOption[]>([]);
  const skillLevelSources = shallowRef<SkillLevelOption[]>([]);
  const enhancementGroupSources = shallowRef<EnhancementGroupOption[]>([]);
  const enhancementLevelSources = shallowRef<EnhancementLevelOption[]>([]);
  const selectedSkillId = ref<string | null>(null);
  const selectedEnhancementItemCode = ref<string | null>(null);
  const selectedEnhancementLevel = ref<number | null>(null);
  const shopSettingsModel = shallowRef<ShopSettingsViewModel | null>(null);
  const selectedShopCategory = ref<ShopCategoryKey>('all');
  const selectedShopItemCode = ref<string | null>(null);
  const settingPreview = ref<SettingPreviewState>(cloneDefaultSettingPreview());
  const shopSettingsLastAction = ref<string | null>(null);
  const screen = ref<'town' | 'field' | 'boss' | 'inventory' | 'storage-trash' | 'skill-enhancement' | 'shop-settings'>('town');
  const contextSignature = ref('');
  const activeFeatureKey = ref<TownFeatureKey | null>(null);

  const activeFeature = computed(() => (
    activeFeatureKey.value ? TOWN_FEATURES[activeFeatureKey.value] : null
  ));
  const isTown = computed(() => screen.value === 'town' && model.value?.zoneType === 'town');
  const isField = computed(() => screen.value === 'field' && fieldModel.value?.zoneType === 'field');
  const isBoss = computed(() => screen.value === 'boss' && bossModel.value?.zoneType === 'boss');
  const isInventory = computed(() => screen.value === 'inventory' && inventoryModel.value?.zoneType === 'inventory');
  const isStorageTrash = computed(() => screen.value === 'storage-trash' && storageTrashModel.value?.zoneType === 'storage-trash');
  const isSkillEnhancement = computed(() => screen.value === 'skill-enhancement' && skillEnhancementModel.value?.zoneType === 'skill-enhancement');
  const isShopSettings = computed(() => screen.value === 'shop-settings' && shopSettingsModel.value?.zoneType === 'shop-settings');

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
    resetStorageTrashPreview();
    resetSkillEnhancementPreview();
    resetShopSettingsPreview();
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

  function enterStorageTrashPreview() {
    if (!inventoryModel.value || !itemTemplateSources.value.length) return false;
    storageCompactedPreview.value = false;
    trashCompactedPreview.value = false;
    selectedStorageTrashItemCode.value = null;
    selectedStorageTrashContainer.value = null;
    storageTrashLastAction.value = null;
    rebuildStorageTrashPreview();
    screen.value = 'storage-trash';
    return true;
  }

  function selectStorageTrashPreview(container: StorageTrashContainerKey, itemCode: string) {
    selectedStorageTrashContainer.value = container;
    selectedStorageTrashItemCode.value = itemCode;
    storageTrashLastAction.value = null;
    rebuildStorageTrashPreview();
  }

  function toggleStorageTrashCompactPreview(container: StorageTrashContainerKey) {
    if (container === 'storage') storageCompactedPreview.value = !storageCompactedPreview.value;
    else trashCompactedPreview.value = !trashCompactedPreview.value;
    storageTrashLastAction.value = container;
    rebuildStorageTrashPreview();
  }

  function rebuildStorageTrashPreview() {
    if (!inventoryModel.value || !itemTemplateSources.value.length) return;
    storageTrashModel.value = createStorageTrashViewModel({
      inventory: inventoryModel.value,
      itemTemplates: itemTemplateSources.value,
      storageCompactPreview: storageCompactedPreview.value,
      trashCompactPreview: trashCompactedPreview.value,
      preferredItemCode: selectedStorageTrashItemCode.value,
      preferredContainer: selectedStorageTrashContainer.value,
      lastActionContainer: storageTrashLastAction.value,
      createdAt: 0,
    });
    selectedStorageTrashItemCode.value = storageTrashModel.value.selectedItem.code;
    selectedStorageTrashContainer.value = storageTrashModel.value.selectedContainer;
  }

  function returnInventoryPreview() {
    if (!inventoryModel.value && model.value && itemTemplateSources.value.length) rebuildInventoryPreview();
    if (!inventoryModel.value) returnTown();
    screen.value = 'inventory';
    storageTrashModel.value = null;
  }

  function enterSkillEnhancementPreview(source: {
    skills: SkillOption[];
    characterSkills: CharacterSkillOption[];
    skillLevels: SkillLevelOption[];
    itemTemplates: ItemTemplateOption[];
    enhancementGroups: EnhancementGroupOption[];
    enhancementLevels: EnhancementLevelOption[];
  }) {
    if (!model.value || !source.skills.length || !source.enhancementGroups.length || !source.enhancementLevels.length) return false;
    skillSources.value = source.skills.slice();
    characterSkillSources.value = source.characterSkills.slice();
    skillLevelSources.value = source.skillLevels.slice();
    if (source.itemTemplates.length) itemTemplateSources.value = source.itemTemplates.slice();
    enhancementGroupSources.value = source.enhancementGroups.slice();
    enhancementLevelSources.value = source.enhancementLevels.slice();
    selectedSkillId.value = null;
    selectedEnhancementItemCode.value = null;
    selectedEnhancementLevel.value = null;
    rebuildSkillEnhancementPreview();
    screen.value = 'skill-enhancement';
    activeFeatureKey.value = null;
    return true;
  }

  function selectSkillEnhancementSkill(skillId: string) {
    selectedSkillId.value = skillId;
    rebuildSkillEnhancementPreview();
  }

  function selectEnhancementItem(itemCode: string) {
    selectedEnhancementItemCode.value = itemCode;
    selectedEnhancementLevel.value = null;
    rebuildSkillEnhancementPreview();
  }

  function selectEnhancementLevel(fromLevel: number) {
    selectedEnhancementLevel.value = fromLevel;
    rebuildSkillEnhancementPreview();
  }

  function rebuildSkillEnhancementPreview() {
    if (!model.value || !skillSources.value.length || !itemTemplateSources.value.length) return;
    skillEnhancementModel.value = createSkillEnhancementViewModel({
      town: model.value,
      skills: skillSources.value,
      characterSkills: characterSkillSources.value,
      skillLevels: skillLevelSources.value,
      itemTemplates: itemTemplateSources.value,
      enhancementGroups: enhancementGroupSources.value,
      enhancementLevels: enhancementLevelSources.value,
      preferredSkillId: selectedSkillId.value,
      preferredItemCode: selectedEnhancementItemCode.value,
      preferredEnhancementLevel: selectedEnhancementLevel.value,
      createdAt: 0,
    });
    selectedSkillId.value = skillEnhancementModel.value.selectedSkill.id;
    selectedEnhancementItemCode.value = skillEnhancementModel.value.selectedEnhancementItem.code;
    selectedEnhancementLevel.value = skillEnhancementModel.value.selectedEnhancementStep.fromLevel;
  }

  function enterShopSettingsPreview(itemTemplates: ItemTemplateOption[]) {
    if (!model.value || !itemTemplates.length) return false;
    itemTemplateSources.value = itemTemplates.slice();
    selectedShopCategory.value = 'all';
    selectedShopItemCode.value = null;
    settingPreview.value = cloneDefaultSettingPreview();
    shopSettingsLastAction.value = null;
    rebuildShopSettingsPreview();
    screen.value = 'shop-settings';
    activeFeatureKey.value = null;
    return true;
  }

  function selectShopCategory(category: ShopCategoryKey) {
    selectedShopCategory.value = category;
    selectedShopItemCode.value = null;
    shopSettingsLastAction.value = null;
    rebuildShopSettingsPreview();
  }

  function selectShopItem(itemCode: string) {
    selectedShopItemCode.value = itemCode;
    shopSettingsLastAction.value = null;
    rebuildShopSettingsPreview();
  }

  function toggleSettingPreview(key: SettingPreviewKey) {
    settingPreview.value = { ...settingPreview.value, [key]: !settingPreview.value[key] };
    const definition = shopSettingsModel.value?.settings.find((setting) => setting.key === key);
    shopSettingsLastAction.value = `${definition?.label ?? key} ${settingPreview.value[key] ? 'ON' : 'OFF'}`;
    rebuildShopSettingsPreview();
  }

  function resetSettingPreview() {
    settingPreview.value = cloneDefaultSettingPreview();
    shopSettingsLastAction.value = '기본값 복원';
    rebuildShopSettingsPreview();
  }

  function rebuildShopSettingsPreview() {
    if (!model.value || !itemTemplateSources.value.length) return;
    shopSettingsModel.value = createShopSettingsViewModel({
      town: model.value,
      itemTemplates: itemTemplateSources.value,
      preferredCategory: selectedShopCategory.value,
      preferredItemCode: selectedShopItemCode.value,
      settingPreview: settingPreview.value,
      lastAction: shopSettingsLastAction.value,
      createdAt: 0,
    });
    selectedShopCategory.value = shopSettingsModel.value.selectedCategory;
    selectedShopItemCode.value = shopSettingsModel.value.selectedItem.code;
  }

  function returnTown() {
    screen.value = 'town';
    fieldModel.value = null;
    bossModel.value = null;
    inventoryModel.value = null;
    storageTrashModel.value = null;
    skillEnhancementModel.value = null;
    shopSettingsModel.value = null;
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
    resetStorageTrashPreview();
    resetSkillEnhancementPreview();
    resetShopSettingsPreview();
    screen.value = 'town';
    contextSignature.value = '';
    activeFeatureKey.value = null;
  }

  function resetStorageTrashPreview() {
    storageTrashModel.value = null;
    storageCompactedPreview.value = false;
    trashCompactedPreview.value = false;
    selectedStorageTrashItemCode.value = null;
    selectedStorageTrashContainer.value = null;
    storageTrashLastAction.value = null;
  }

  function resetSkillEnhancementPreview() {
    skillEnhancementModel.value = null;
    skillSources.value = [];
    characterSkillSources.value = [];
    skillLevelSources.value = [];
    enhancementGroupSources.value = [];
    enhancementLevelSources.value = [];
    selectedSkillId.value = null;
    selectedEnhancementItemCode.value = null;
    selectedEnhancementLevel.value = null;
  }

  function resetShopSettingsPreview() {
    shopSettingsModel.value = null;
    selectedShopCategory.value = 'all';
    selectedShopItemCode.value = null;
    settingPreview.value = cloneDefaultSettingPreview();
    shopSettingsLastAction.value = null;
  }

  return {
    model,
    fieldModel,
    bossModel,
    inventoryModel,
    storageTrashModel,
    skillEnhancementModel,
    shopSettingsModel,
    activeFeature,
    isTown,
    isField,
    isBoss,
    isInventory,
    isStorageTrash,
    isSkillEnhancement,
    isShopSettings,
    enterTown,
    enterFieldPreview,
    selectFieldPreview,
    enterBossPreview,
    selectBossPreview,
    enterInventoryPreview,
    selectInventoryPreview,
    toggleInventoryCompactPreview,
    enterStorageTrashPreview,
    selectStorageTrashPreview,
    toggleStorageTrashCompactPreview,
    returnInventoryPreview,
    enterSkillEnhancementPreview,
    selectSkillEnhancementSkill,
    selectEnhancementItem,
    selectEnhancementLevel,
    enterShopSettingsPreview,
    selectShopCategory,
    selectShopItem,
    toggleSettingPreview,
    resetSettingPreview,
    returnTown,
    openFeature,
    closeFeature,
    resetShell,
  };
});
