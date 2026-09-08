<template>
  <p v-if="game.recoveryWarning" class="game-recovery-warning" role="alert">{{ game.recoveryWarning }}</p>
  <section
    v-if="!gameReady"
    class="game-snapshot-gate"
    aria-live="polite"
    :aria-busy="game.snapshotLoad.status === 'loading'"
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
    <span v-else-if="game.snapshotLoad.status !== 'recovery'" class="game-snapshot-gate__spinner" aria-hidden="true" />
    <small>서버 저장을 불러온 뒤에만 직렬 자동·수동 저장을 시작합니다.</small>
  </section>

  <div
    v-else
    class="game-legacy-frame"
    :aria-hidden="(game.isUtilityScreen || mobilePanel !== null) || undefined"
    :inert="game.isUtilityScreen || mobilePanel !== null || game.saveTransitioning"
    :aria-busy="game.saveTransitioning"
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
      <button type="button" aria-haspopup="dialog" @click="openMobilePanel('profile')">
        <span aria-hidden="true">♟</span> 내 정보
      </button>
      <button type="button" aria-haspopup="dialog" @click="openMobilePanel('inventory')">
        <span aria-hidden="true">▦</span> 가방
      </button>
    </nav>
  </div>

  <Teleport to="body">
    <div v-if="game.recovery" class="game-recovery-backdrop">
      <section ref="recoveryModal" class="game-recovery-modal" role="dialog" aria-modal="true" aria-labelledby="game-recovery-title" aria-describedby="game-recovery-description" tabindex="-1">
        <p class="vue-shell__eyebrow">저장 복구 · {{ selectedCharacterName }}</p>
        <h2 id="game-recovery-title">어떤 저장으로 이어갈까요?</h2>
        <p id="game-recovery-description">서버에 반영되지 않은 이 기기 저장이 있습니다. 선택하기 전에는 게임과 자동 저장을 시작하지 않습니다.</p>
        <div class="game-recovery-copies">
          <article v-for="(copy, key) in game.recovery" :key="key">
            <h3>{{ key === 'local' ? '이 기기 저장' : '서버 저장' }}</h3>
            <dl>
              <div><dt>기록 시각</dt><dd>{{ recoveryDate(copy.capturedAt) }}</dd></div>
              <div><dt>레벨</dt><dd>{{ recoveryNumber(copy.snapshot, 'level') }}</dd></div>
              <div><dt>Gold</dt><dd>{{ recoveryNumber(copy.snapshot, 'gold') }}</dd></div>
            </dl>
            <p>{{ key === 'local' ? '이 진행 상태를 불러와 서버에 다시 전송합니다. 서버의 진행 상태가 교체됩니다.' : '이 기기 진행 상태를 별도 복구 백업으로 남긴 뒤 서버 저장을 사용합니다.' }}</p>
            <button class="account-button account-button--primary" type="button" :disabled="recoveryBusy" @click="chooseRecovery(key)">{{ key === 'local' ? '이 기기 저장 사용' : '서버 저장 사용' }}</button>
          </article>
        </div>
        <p class="game-recovery-note">시각만으로 최신 저장을 판단하지 않습니다. 다중 기기 동시 저장 보호는 아직 제공되지 않습니다. 복구본에는 로그인 토큰을 넣지 않습니다.</p>
        <button ref="recoveryCancel" class="account-button account-button--ghost" type="button" :disabled="recoveryBusy" @click="cancelRecovery">취소 · 캐릭터 선택으로</button>
        <p v-if="recoveryBusy" role="status">선택한 저장을 확인하고 있습니다…</p>
      </section>
    </div>
  </Teleport>

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
          <section v-if="game.itemAction.message" class="game-item-save-status" aria-live="polite" :aria-busy="game.itemAction.busy || game.saveQueue.active">
            <p>{{ game.itemAction.message }}</p>
            <p v-if="game.saveQueue.message">{{ game.saveQueue.message }}</p>
            <p v-if="game.recoveryWarning" role="alert">{{ game.recoveryWarning }}</p>
            <button v-if="game.saveQueue.errorKind === 'retryable'" class="account-button account-button--primary" type="button" :disabled="game.saveQueue.active || game.itemAction.busy" @click="itemActions.retry">서버 저장 재시도</button>
            <p v-else-if="game.saveQueue.errorKind === 'conflict'">마을의 수동 저장 창에서 서버를 확인하고 복구본을 선택해 주세요.</p>
          </section>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useModalAccessibility } from '@/composables/useModalAccessibility';
import { useOwnedItemActions } from '@/composables/useOwnedItemActions';
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
const itemActions = useOwnedItemActions();
const world = ref<HTMLElement | null>(null);
const recoveryModal = ref<HTMLElement | null>(null);
const recoveryCancel = ref<HTMLButtonElement | null>(null);
const recoveryBusy = ref(false);
const utilityModal = ref<HTMLElement | null>(null);
const utilityClose = ref<HTMLButtonElement | null>(null);
const mobileModal = ref<HTMLElement | null>(null);
const mobileClose = ref<HTMLButtonElement | null>(null);
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
  : game.snapshotLoad.status === 'recovery' ? '저장 선택을 기다리고 있습니다' : '게임 저장을 불러오는 중입니다');
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
});

useModalAccessibility({ panel: utilityModal, initialFocus: utilityClose, fallbackFocus: world, isOpen: () => game.isUtilityScreen, close: closeUtility });
useModalAccessibility({ panel: mobileModal, initialFocus: mobileClose, isOpen: () => mobilePanel.value !== null, close: closeMobilePanel });
useModalAccessibility({ panel: recoveryModal, initialFocus: recoveryCancel, fallbackFocus: world, isOpen: () => Boolean(game.recovery), close: cancelRecovery, canClose: () => !recoveryBusy.value });

watch(gameReady, (ready) => {
  stopAutosaveTimer();
  if (ready) autosaveTimer = window.setInterval(() => void runAutosave(), 60_000);
}, { immediate: true });

function closeUtility() {
  game.closeUtilityPreview();
}

async function initializeSelectedGame() {
  const slot = account.selectedCharacter;
  const token = account.accessToken;
  const userId = account.user?.id;
  if (!token || userId === undefined || !slot?.occupied || !slot.accountCharacterId || !slot.accountCharacter) {
    game.resetShell();
    return;
  }
  const outcome = await game.loadSelectedCharacterSnapshot({
    token,
    userId,
    slot,
    characterLabel: selectedCharacterLabel.value,
  });
  if (account.accessToken !== token || account.user?.id !== userId || account.selectedCharacter?.accountCharacterId !== slot.accountCharacterId) return;
  if (outcome === 'session-invalid') {
    account.invalidateSession('로그인 정보가 만료되었거나 이 캐릭터에 접근할 수 없습니다. 다시 로그인해 주세요.');
  }
}

function recoveryDate(value: string) { return new Date(value).toLocaleString('ko-KR'); }
function recoveryNumber(snapshot: Record<string, unknown>, key: string) { const number = Number((snapshot.player as Record<string, unknown>)?.[key]); return Number.isFinite(number) ? number.toLocaleString('ko-KR') : '정보 없음'; }
function cancelRecovery() { if (!recoveryBusy.value) changeCharacter(); }
async function chooseRecovery(choice: 'local' | 'server') {
  const token = account.accessToken;
  const userId = account.user?.id;
  const characterId = account.selectedCharacter?.accountCharacterId;
  if (!token || userId === undefined || recoveryBusy.value) return;
  recoveryBusy.value = true;
  try {
    const outcome = await game.resolveRecovery(choice, token, userId);
    if (account.accessToken !== token || account.user?.id !== userId || account.selectedCharacter?.accountCharacterId !== characterId) return;
    if (outcome === 'session-invalid') account.invalidateSession('복구본은 보존했습니다. 다시 로그인해 주세요.');
  } finally { recoveryBusy.value = false; }
}

async function runAutosave() {
  const slot = account.selectedCharacter;
  const userId = account.user?.id;
  const token = account.accessToken;
  if (game.saveTransitioning
    || game.saveQueue.errorKind === 'conflict'
    || !account.accessToken
    || userId === undefined
    || !slot) return;
  const outcome = await game.enqueueSelectedCharacterSave({
    token,
    userId,
    slot,
    reason: 'auto',
  });
  if (account.accessToken !== token || account.selectedCharacter?.accountCharacterId !== slot.accountCharacterId) return;
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

function openMobilePanel(panel: 'profile' | 'inventory') {
  game.pauseCombatRuntime('utility');
  mobilePanel.value = panel;
}

function closeMobilePanel() {
  mobilePanel.value = null;
  game.resumeCombatRuntime('utility');
}

function handleVisibilityChange() {
  if (document.hidden) game.pauseCombatRuntime('visibility');
  else game.resumeCombatRuntime('visibility');
}

onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange);
  window.addEventListener('beforeunload', game.preserveLocalProgress);
});

onBeforeUnmount(() => {
  stopAutosaveTimer();
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('beforeunload', game.preserveLocalProgress);
  game.preserveLocalProgress();
  game.resetShell();
});
</script>
