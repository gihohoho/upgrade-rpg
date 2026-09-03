<template>
  <div
    v-if="game.model"
    class="game-legacy-frame"
    :aria-hidden="(game.isUtilityScreen || mobilePanel !== null) || undefined"
    :inert="game.isUtilityScreen || mobilePanel !== null"
  >
    <GameLegacySidebar class="game-legacy-frame__sidebar" variant="profile" />

    <main
      ref="world"
      class="game-legacy-frame__world"
      tabindex="-1"
      :aria-hidden="game.isUtilityScreen || undefined"
      :inert="game.isUtilityScreen"
    >
      <GameBossCombatShell v-if="game.isBoss || game.utilityBackground === 'boss'" />
      <GameFieldCombatShell v-else-if="game.isField || game.utilityBackground === 'field'" />
      <GameTownShell v-else :background="game.isUtilityScreen" />
    </main>

    <GameLegacySidebar class="game-legacy-frame__sidebar" variant="inventory" />

    <nav class="game-mobile-dock" aria-label="캐릭터 정보와 가방">
      <button type="button" aria-haspopup="dialog" @click="openMobilePanel('profile', $event)">
        <span aria-hidden="true">♟</span> 내 정보
      </button>
      <button type="button" aria-haspopup="dialog" @click="openMobilePanel('inventory', $event)">
        <span aria-hidden="true">▦</span> 가방
      </button>
    </nav>
  </div>

  <Teleport to="body">
    <div v-if="game.isUtilityScreen" class="game-utility-modal-backdrop" @click.self="closeUtility">
      <section
        ref="utilityModal"
        class="game-utility-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="game-utility-modal-title"
        tabindex="-1"
      >
        <header class="game-utility-modal__titlebar">
          <div>
            <span aria-hidden="true">◇</span>
            <strong id="game-utility-modal-title">{{ utilityTitle }}</strong>
            <small>게임 창</small>
          </div>
          <button ref="utilityClose" type="button" aria-label="창 닫기" @click="closeUtility">×</button>
        </header>
        <div class="game-utility-modal__body">
          <GameShopSettingsShell v-if="game.isShopSettings" />
          <GameSkillEnhancementShell v-else-if="game.isSkillEnhancement" />
          <GameStorageTrashShell v-else-if="game.isStorageTrash" />
          <GameInventoryEquipmentShell v-else-if="game.isInventory" />
        </div>
      </section>
    </div>
  </Teleport>

  <Teleport to="body">
    <div v-if="mobilePanel" class="game-mobile-panel-backdrop" @click.self="closeMobilePanel">
      <section
        ref="mobileModal"
        class="game-mobile-panel-modal"
        role="dialog"
        aria-modal="true"
        :aria-label="mobilePanel === 'profile' ? '내 정보' : '가방'"
        tabindex="-1"
      >
        <button ref="mobileClose" class="game-mobile-panel-modal__close" type="button" aria-label="창 닫기" @click="closeMobilePanel">×</button>
        <GameLegacySidebar :variant="mobilePanel" compact />
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';
import GameLegacySidebar from './GameLegacySidebar.vue';
import GameInventoryEquipmentShell from './GameInventoryEquipmentShell.vue';
import GameShopSettingsShell from './GameShopSettingsShell.vue';
import GameSkillEnhancementShell from './GameSkillEnhancementShell.vue';
import GameStorageTrashShell from './GameStorageTrashShell.vue';
import GameBossCombatShell from './GameBossCombatShell.vue';
import GameFieldCombatShell from './GameFieldCombatShell.vue';
import GameTownShell from './GameTownShell.vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
const world = ref<HTMLElement | null>(null);
const utilityModal = ref<HTMLElement | null>(null);
const utilityClose = ref<HTMLButtonElement | null>(null);
const mobileModal = ref<HTMLElement | null>(null);
const mobileClose = ref<HTMLButtonElement | null>(null);
const mobileTrigger = ref<HTMLElement | null>(null);
const mobilePanel = ref<'profile' | 'inventory' | null>(null);
const utilityTitle = computed(() => {
  if (game.isInventory) return '가방과 장비';
  if (game.isStorageTrash) return '보관함과 휴지통';
  if (game.isSkillEnhancement) return '스킬과 강화';
  if (game.isShopSettings) return '상점과 설정';
  return '게임 기능';
});

watch(() => game.isUtilityScreen, (open) => {
  if (!open) return;
  mobilePanel.value = null;
  void nextTick(() => (utilityClose.value ?? utilityModal.value)?.focus());
});

function closeUtility() {
  game.closeUtilityPreview();
  void nextTick(() => world.value?.focus());
}

function openMobilePanel(panel: 'profile' | 'inventory', event: Event) {
  mobileTrigger.value = event.currentTarget as HTMLElement;
  mobilePanel.value = panel;
  void nextTick(() => (mobileClose.value ?? mobileModal.value)?.focus());
}

function closeMobilePanel() {
  mobilePanel.value = null;
  void nextTick(() => mobileTrigger.value?.focus());
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return;
  if (mobilePanel.value) closeMobilePanel();
  else if (game.isUtilityScreen) closeUtility();
}

window.addEventListener('keydown', handleKeydown);
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown));
</script>
