<template>
  <section class="admin-access-card" aria-labelledby="admin-access-title">
    <header class="account-card__header">
      <span class="account-card__mark admin-access-card__mark" aria-hidden="true">A</span>
      <div>
        <p class="account-card__eyebrow">Admin access</p>
        <h2 id="admin-access-title">관리자 계정 확인</h2>
        <p>관리자 화면과 조회 요청은 로그인한 계정의 서버 권한을 확인한 뒤에만 시작합니다.</p>
      </div>
    </header>

    <div v-if="admin.accessStage === 'checking' || admin.accessStage === 'idle'" class="admin-access-state" aria-live="polite">
      <span class="account-loading__mark" aria-hidden="true">UR</span>
      <div><strong>관리자 권한을 확인하고 있습니다</strong><p>확인이 끝날 때까지 관리자 화면은 생성하지 않습니다.</p></div>
    </div>

    <div v-else-if="admin.accessStage === 'retry'" class="admin-access-state" data-tone="error">
      <span class="account-loading__mark" aria-hidden="true">↻</span>
      <div>
        <strong>서버에 연결하지 못했습니다</strong>
        <p>{{ admin.accessMessage || '로그인 정보는 유지했습니다. 서버가 준비된 뒤 다시 확인해 주세요.' }}</p>
        <button class="account-button account-button--primary" type="button" :disabled="admin.busy" @click="retryAccess">
          다시 확인
        </button>
      </div>
    </div>

    <div v-else-if="admin.accessStage === 'forbidden'" class="admin-access-denied">
      <span class="admin-access-denied__icon" aria-hidden="true">!</span>
      <div>
        <strong>관리자 권한이 없는 계정입니다</strong>
        <p><code>{{ account.user?.username }}</code> 계정으로는 관리자 데이터와 도구를 표시하지 않습니다.</p>
        <div class="account-form__actions">
          <RouterLink class="account-button account-button--ghost" to="/game">게임 화면으로</RouterLink>
          <button class="account-button account-button--primary" type="button" :disabled="admin.busy" @click="logoutForAnotherAccount">
            다른 계정으로 로그인
          </button>
        </div>
      </div>
    </div>

    <form v-else class="account-form admin-access-form" @submit.prevent="submitLogin">
      <label class="account-field">
        <span>관리자 아이디 또는 이메일</span>
        <input
          v-model.trim="form.identifier"
          name="identifier"
          autocomplete="username"
          maxlength="254"
          autocapitalize="none"
          spellcheck="false"
          required
          placeholder="관리자 계정"
        />
      </label>
      <label class="account-field">
        <span>비밀번호</span>
        <input
          v-model="form.password"
          name="password"
          type="password"
          autocomplete="current-password"
          maxlength="72"
          required
          placeholder="비밀번호를 입력하세요"
        />
      </label>
      <label class="account-keep-login">
        <input v-model="form.keepLogin" name="keepLogin" type="checkbox" />
        <span><strong>로그인 유지</strong>공용 기기에서는 선택하지 마세요.</span>
      </label>
      <button class="account-button account-button--primary account-button--wide" type="submit" :disabled="admin.busy">
        {{ admin.busy ? '권한 확인 중…' : '관리자 계정으로 로그인' }}
      </button>
      <p v-if="admin.accessMessage || (account.noticeTone === 'error' && account.notice)" class="account-notice" data-tone="error" role="alert">
        {{ admin.accessMessage || account.notice }}
      </p>
    </form>

    <div class="admin-access-boundary">
      <strong>보호 범위</strong>
      <p>일반 계정에는 관리자 컴포넌트를 렌더링하지 않으며, 관리자 GET과 dry-run Preview 요청에 Bearer 인증을 함께 보냅니다. 실제 Apply와 dev key는 아직 연결하지 않습니다.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAccountStore, useAdminStore } from '@/stores';

const router = useRouter();
const account = useAccountStore();
const admin = useAdminStore();
const form = reactive({ identifier: '', password: '', keepLogin: false });

async function submitLogin() {
  const authorized = await admin.login(form.identifier, form.password, form.keepLogin);
  form.password = '';
  if (authorized) await router.replace({ name: 'admin-shell' });
}

async function retryAccess() {
  const authorized = await admin.checkAccess();
  if (authorized) await router.replace({ name: 'admin-shell' });
}

async function logoutForAnotherAccount() {
  await admin.logout();
  form.identifier = '';
  form.password = '';
}

onMounted(() => {
  if (admin.accessStage === 'idle') void retryAccess();
});
</script>
