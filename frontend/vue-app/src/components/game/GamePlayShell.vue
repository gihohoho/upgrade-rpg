<template>
  <GameShopSettingsShell v-if="game.isShopSettings" />
  <GameSkillEnhancementShell v-else-if="game.isSkillEnhancement" />
  <GameStorageTrashShell v-else-if="game.isStorageTrash" />
  <GameInventoryEquipmentShell v-else-if="game.isInventory" />
  <GameBossCombatShell v-else-if="game.isBoss" />
  <GameFieldCombatShell v-else-if="game.isField" />
  <GameTownShell v-else />
</template>

<script setup lang="ts">
import GameInventoryEquipmentShell from './GameInventoryEquipmentShell.vue';
import GameShopSettingsShell from './GameShopSettingsShell.vue';
import GameSkillEnhancementShell from './GameSkillEnhancementShell.vue';
import GameStorageTrashShell from './GameStorageTrashShell.vue';
import GameBossCombatShell from './GameBossCombatShell.vue';
import GameFieldCombatShell from './GameFieldCombatShell.vue';
import GameTownShell from './GameTownShell.vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
</script>
