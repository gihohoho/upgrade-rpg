<template>
  <section
    v-if="!gameReady"
    class="game-snapshot-gate"
    aria-live="polite"
    :aria-busy="game.snapshotLoad.status !== 'error'"
  >
    <div class="game-snapshot-gate__crest" aria-hidden="true">◇</div>
    <p>Selected character · server snapshot</p>
    <h1>{{ loadTitle }}</h1>
    <p class="game-snapshot-gate__message">{{ loadMessage }}</p>
    <div v-if="selectedCharacterName" class="game-snapshot-gate__identity">
      <strong>{{ selectedCharacterName }}</strong>
      <span>{{ account.selectedCharacter?.slotKey }}</span>
    </div>
    <div v-if="game.snapshotLoad.status === 'error'" class="game-snapshot-gate__actions">
      <button class="account-button account-button--primary" type="button" @click="initializeSelectedGame">
        서버 저장 다시 불러오기
      </button>
      <button class="account-button account-button--ghost" type="button" @click="changeCharacter">
        캐릭터 다시 선택
      </button>
    </div>
    <span v-else class="game-snapshot-gate__spinner" aria-hidden="true" />
    <small>서버 저장을 불러온 뒤에만 직렬 자동·수동 저장을 시작합니다.</small>
  </section>

  <div
    v-else
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import GameLegacySidebar from './GameLegacySidebar.vue';
import GameInventoryEquipmentShell from './GameInventoryEquipmentShell.vue';
import GameShopSettingsShell from './GameShopSettingsShell.vue';
import GameSkillEnhancementShell from './GameSkillEnhancementShell.vue';
import GameStorageTrashShell from './GameStorageTrashShell.vue';
import GameBossCombatShell from './GameBossCombatShell.vue';
import GameFieldCombatShell from './GameFieldCombatShell.vue';
import GameTownShell from './GameTownShell.vue';
import { useAccountStore, useGameStore } from '@/stores';

const account = useAccountStore();
const game = useGameStore();
const world = ref<HTMLElement | null>(null);
const utilityModal = ref<HTMLElement | null>(null);
const utilityClose = ref<HTMLButtonElement | null>(null);
const mobileModal = ref<HTMLElement | null>(null);
const mobileClose = ref<HTMLButtonElement | null>(null);
const mobileTrigger = ref<HTMLElement | null>(null);
const mobilePanel = ref<'profile' | 'inventory' | null>(null);
let autosaveTimer: number | null = null;
const gameReady = computed(() => game.snapshotLoad.status === 'ready' && Boolean(game.model));
const selectedCharacterName = computed(() => account.selectedCharacter?.accountCharacter?.name ?? '');
const selectedCharacterLabel = computed(() => {
  const code = account.selectedCharacter?.accountCharacter?.characterCode;
  return account.characterOptions.find((option) => option.code === code)?.name ?? code ?? '캐릭터';
});
const loadTitle = computed(() => game.snapshotLoad.status === 'error'
  ? '게임 저장을 불러오지 못했습니다'
  : '게임 저장을 불러오는 중입니다');
const loadMessage = computed(() => game.snapshotLoad.message
  || '선택한 캐릭터와 서버 저장을 확인하고 있습니다.');
const utilityTitle = computed(() => {
  if (game.isInventory) return '가방과 장비';
  if (game.isStorageTrash) return '보관함과 휴지통';
  if (game.isSkillEnhancement) return '스킬과 강화';
  if (game.isShopSettings) return '상점과 설정';
  return '게임 기능';
});

watch([
  () => account.accessToken,
  () => account.selectedCharacter?.slotKey,
  () => account.selectedCharacter?.accountCharacterId,
], () => {
  void initializeSelectedGame();
}, { immediate: true });

watch(() => game.isUtilityScreen, (open) => {
  if (!open) return;
  mobilePanel.value = null;
  void nextTick(() => (utilityClose.value ?? utilityModal.value)?.focus());
});

watch(gameReady, (ready) => {
  stopAutosaveTimer();
  if (ready) autosaveTimer = window.setInterval(() => void runAutosave(), 60_000);
}, { immediate: true });

function closeUtility() {
  game.closeUtilityPreview();
  void nextTick(() => world.value?.focus());
}

async function initializeSelectedGame() {
  const slot = account.selectedCharacter;
  if (!account.accessToken || !slot?.occupied || !slot.accountCharacterId || !slot.accountCharacter) {
    game.resetShell();
    return;
  }
  const outcome = await game.loadSelectedCharacterSnapshot({
    token: account.accessToken,
    slot,
    characterLabel: selectedCharacterLabel.value,
  });
  if (outcome === 'session-invalid') {
    account.invalidateSession('로그인 정보가 만료되었거나 이 캐릭터에 접근할 수 없습니다. 다시 로그인해 주세요.');
  }
}

async function runAutosave() {
  const slot = account.selectedCharacter;
  const userId = account.user?.id;
  if (game.saveTransitioning
    || game.saveQueue.errorKind === 'conflict'
    || !account.accessToken
    || userId === undefined
    || !slot) return;
  const outcome = await game.enqueueSelectedCharacterSave({
    token: account.accessToken,
    userId,
    slot,
    reason: 'auto',
  });
  if (outcome === 'session-invalid') {
    account.invalidateSession('자동 저장 중 로그인 정보가 만료되었습니다. 다시 로그인해 주세요.');
  }
}

function stopAutosaveTimer() {
  if (autosaveTimer === null) return;
  window.clearInterval(autosaveTimer);
  autosaveTimer = null;
}

function changeCharacter() {
  game.resetShell();
  account.changeCharacter();
}

function openMobilePanel(panel: 'profile' | 'inventory', event: Event) {
  mobileTrigger.value = event.currentTarget as HTMLElement;
  game.pauseCombatRuntime('utility');
  mobilePanel.value = panel;
  void nextTick(() => (mobileClose.value ?? mobileModal.value)?.focus());
}

function closeMobilePanel() {
  mobilePanel.value = null;
  game.resumeCombatRuntime('utility');
  void nextTick(() => mobileTrigger.value?.focus());
}

function handleVisibilityChange() {
  if (document.hidden) game.pauseCombatRuntime('visibility');
  else game.resumeCombatRuntime('visibility');
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return;
  if (mobilePanel.value) closeMobilePanel();
  else if (game.isUtilityScreen) closeUtility();
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  document.addEventListener('visibilitychange', handleVisibilityChange);
});

onBeforeUnmount(() => {
  stopAutosaveTimer();
  window.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  game.resetShell();
});
</script>
