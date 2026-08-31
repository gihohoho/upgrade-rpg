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

    <GameTownShell v-else />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import AuthPanel from './AuthPanel.vue';
import CharacterPanel from './CharacterPanel.vue';
import GameTownShell from '@/components/game/GameTownShell.vue';
import { useAccountStore } from '@/stores';

const account = useAccountStore();

onMounted(() => account.initialize());
</script>
