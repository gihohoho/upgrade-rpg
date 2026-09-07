<template>
  <span class="owned-item-icon" aria-hidden="true">
    <img v-if="url && !failed" :src="url" alt="" loading="lazy" @error="failed = true" />
    <span v-else>{{ item.iconText }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { InventoryItemView } from '@/game/adapters/inventoryEquipment';

const props = defineProps<{ item: InventoryItemView }>();
// Bundle only repository-owned images. Snapshot URLs cannot contact arbitrary hosts.
const assets = import.meta.glob('../../../../../src/assets/{equipment,special-equipment,skill-books}/**/*.png', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;
const url = computed(() => {
  const path = props.item.iconUrl?.replace(/^\.?\//, '').split('?')[0];
  return path ? assets[`../../../../../${path}`] ?? null : null;
});
const failed = ref(false);
watch(url, () => { failed.value = false; });
</script>

<style scoped>
.owned-item-icon { display: inline-flex; align-items: center; justify-content: center; width: 2.5rem; height: 2.5rem; flex-shrink: 0; }
.owned-item-icon img { display: block; width: 100%; height: 100%; object-fit: cover; }
</style>
