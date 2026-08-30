<template>
  <div class="account-gate" :aria-busy="account.busy">
    <section v-if="account.stage === 'checking'" class="account-card account-loading" aria-live="polite">
      <span class="account-loading__mark" aria-hidden="true">UR</span>
      <div><h2>계정 정보를 확인하고 있습니다</h2><p>로그인과 캐릭터 선택 상태를 안전하게 불러오는 중입니다.</p></div>
    </section>

    <section v-else-if="account.stage === 'retry'" class="account-card account-retry" aria-labelledby="account-retry-title">
      <span class="account-loading__mark" aria-hidden="true">↻</span>
      <div>
        <h2 id="account-retry-title">서버에 연결하지 못했습니다</h2>
        <p>로그인 정보는 삭제하지 않았습니다. 서버가 준비된 뒤 다시 연결해 주세요.</p>
        <p v-if="account.notice" class="account-notice" data-tone="error" role="status">{{ account.notice }}</p>
        <div class="account-form__actions">
          <button class="account-button account-button--primary" type="button" :disabled="account.busy" @click="account.loadCharacters()">다시 연결</button>
          <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="account.logout">다른 계정으로 로그인</button>
        </div>
      </div>
    </section>

    <AuthPanel v-else-if="account.stage === 'anonymous' || account.stage === 'verification'" />
    <CharacterPanel v-else-if="account.stage === 'characters'" />

    <section v-else class="account-card account-card--ready" aria-labelledby="ready-character-title">
      <div class="ready-character">
        <span class="ready-character__avatar" aria-hidden="true">{{ account.selectedCharacter?.accountCharacter?.name.slice(0, 1) }}</span>
        <div>
          <p class="account-card__eyebrow">Ready to enter</p>
          <h2 id="ready-character-title">{{ account.selectedCharacter?.accountCharacter?.name }}</h2>
          <p>{{ selectedCharacterLabel }} · {{ account.selectedCharacter?.slotKey }}</p>
        </div>
        <span class="ready-character__status"><i aria-hidden="true" /> 접속 준비 완료</span>
      </div>
      <div class="account-ready-note">
        <strong>계정·캐릭터 gate 연결 완료</strong>
        <p>선택한 캐릭터 ID와 슬롯 키가 확인됐습니다. 실제 게임 snapshot load와 자동 저장은 다음 runtime 이전 단계에서 연결합니다.</p>
      </div>
      <div class="account-form__actions">
        <button class="account-button account-button--ghost" type="button" @click="account.changeCharacter">캐릭터 변경</button>
        <button class="account-button account-button--ghost" type="button" @click="account.logout">로그아웃</button>
        <button class="account-button account-button--primary" type="button" disabled title="게임 UI 이전 뒤 활성화됩니다">게임 시작 준비 중</button>
      </div>
      <p v-if="account.notice" class="account-notice" :data-tone="account.noticeTone" role="status">{{ account.notice }}</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import AuthPanel from './AuthPanel.vue';
import CharacterPanel from './CharacterPanel.vue';
import { useAccountStore } from '@/stores';

const account = useAccountStore();
const selectedCharacterLabel = computed(() => {
  const code = account.selectedCharacter?.accountCharacter?.characterCode;
  return account.characterOptions.find((option) => option.code === code)?.name ?? code ?? '캐릭터';
});

onMounted(() => account.initialize());
</script>
