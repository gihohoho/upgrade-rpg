<template>
  <GameFieldCombatShell v-if="game.isField" />
  <GameTownShell v-else />
</template>

<script setup lang="ts">
import GameFieldCombatShell from './GameFieldCombatShell.vue';
import GameTownShell from './GameTownShell.vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
</script>
