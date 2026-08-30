<template>
  <section class="account-card" aria-labelledby="account-auth-title">
    <header class="account-card__header">
      <span class="account-card__mark" aria-hidden="true">UR</span>
      <div>
        <p class="account-card__eyebrow">Account gate</p>
        <h2 id="account-auth-title">{{ isVerification ? '이메일을 확인해 주세요' : '모험가 계정 접속' }}</h2>
        <p>
          {{ isVerification
            ? '메일의 인증 버튼을 누른 뒤 로그인하면 캐릭터 슬롯으로 이동합니다.'
            : '로그인과 캐릭터 선택이 끝나기 전에는 게임과 자동 저장을 시작하지 않습니다.' }}
        </p>
      </div>
    </header>

    <template v-if="isVerification">
      <div class="account-verification-callout">
        <span>인증메일 요청 주소</span>
        <strong>{{ account.pendingEmail || '가입한 이메일 주소를 입력해 주세요' }}</strong>
        <p>메일 도착까지 몇 분 걸릴 수 있습니다. 스팸함을 확인하고 잠시 기다린 뒤 한 번만 다시 요청해 주세요.</p>
      </div>
      <form class="account-form" @submit.prevent="submitResend">
        <label class="account-field">
          <span>가입 이메일</span>
          <input
            v-model.trim="resendEmail"
            name="email"
            type="email"
            autocomplete="email"
            maxlength="254"
            required
            placeholder="example@email.com"
          />
        </label>
        <div class="account-form__actions">
          <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="account.showLogin()">
            로그인 화면으로
          </button>
          <button class="account-button account-button--primary" type="submit" :disabled="account.busy">
            {{ account.busy ? '요청 중…' : '인증메일 다시 받기' }}
          </button>
        </div>
      </form>
    </template>

    <template v-else>
      <div class="account-tabs" role="tablist" aria-label="계정 접속 방법">
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'login'"
          :class="{ 'is-active': mode === 'login' }"
          @click="mode = 'login'"
        >
          로그인
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'register'"
          :class="{ 'is-active': mode === 'register' }"
          @click="mode = 'register'"
        >
          회원가입
        </button>
      </div>

      <form v-if="mode === 'login'" class="account-form" @submit.prevent="submitLogin">
        <label class="account-field">
          <span>아이디 또는 이메일</span>
          <input
            v-model.trim="loginForm.identifier"
            name="identifier"
            autocomplete="username"
            maxlength="254"
            autocapitalize="none"
            spellcheck="false"
            required
            placeholder="아이디 또는 가입 이메일"
          />
        </label>
        <label class="account-field">
          <span>비밀번호</span>
          <input
            v-model="loginForm.password"
            name="password"
            type="password"
            autocomplete="current-password"
            maxlength="72"
            required
            placeholder="비밀번호를 입력하세요"
          />
        </label>
        <label class="account-keep-login">
          <input v-model="loginForm.keepLogin" name="keepLogin" type="checkbox" />
          <span><strong>로그인 유지</strong>체크하지 않으면 이 브라우저 탭을 모두 닫을 때 로그인이 해제됩니다.</span>
        </label>
        <button class="account-button account-button--primary account-button--wide" type="submit" :disabled="account.busy">
          {{ account.busy ? '계정 확인 중…' : '로그인' }}
        </button>
        <button class="account-link" type="button" @click="openVerificationHelp">인증메일을 다시 받아야 하나요?</button>
      </form>

      <form v-else class="account-form" @submit.prevent="submitRegister">
        <label class="account-field">
          <span>사용할 아이디</span>
          <input
            v-model.trim="registerForm.username"
            name="username"
            autocomplete="username"
            minlength="4"
            maxlength="24"
            pattern="[a-z0-9][a-z0-9_]{3,23}"
            autocapitalize="none"
            spellcheck="false"
            required
            placeholder="영문 소문자·숫자·_ 4~24자"
          />
          <small>영문 소문자 또는 숫자로 시작하고 `_`만 추가로 사용할 수 있습니다.</small>
        </label>
        <label class="account-field">
          <span>가입 이메일</span>
          <input
            v-model.trim="registerForm.email"
            name="email"
            type="email"
            autocomplete="email"
            maxlength="254"
            required
            placeholder="example@email.com"
          />
          <small>인증과 계정 복구에 사용하는 실제 수신 가능한 주소가 필요합니다.</small>
        </label>
        <div class="account-form__columns">
          <label class="account-field">
            <span>비밀번호</span>
            <input
              v-model="registerForm.password"
              name="password"
              type="password"
              autocomplete="new-password"
              minlength="8"
              maxlength="72"
              required
              placeholder="문자·숫자 포함 8자 이상"
            />
          </label>
          <label class="account-field">
            <span>비밀번호 확인</span>
            <input
              v-model="registerForm.passwordConfirm"
              name="passwordConfirm"
              type="password"
              autocomplete="new-password"
              minlength="8"
              maxlength="72"
              required
              placeholder="한 번 더 입력하세요"
            />
          </label>
        </div>
        <button class="account-button account-button--primary account-button--wide" type="submit" :disabled="account.busy">
          {{ account.busy ? '가입 요청 중…' : '인증메일 요청하고 가입하기' }}
        </button>
      </form>
    </template>

    <p v-if="localError" class="account-notice" data-tone="error" role="alert">{{ localError }}</p>
    <p v-if="account.notice" class="account-notice" :data-tone="account.noticeTone" role="status" aria-live="polite">
      {{ account.notice }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useAccountStore } from '@/stores';

const account = useAccountStore();
const mode = ref<'login' | 'register'>('login');
const localError = ref('');
const resendEmail = ref(account.pendingEmail);
const isVerification = computed(() => account.stage === 'verification');

const loginForm = reactive({ identifier: '', password: '', keepLogin: false });
const registerForm = reactive({ username: '', email: '', password: '', passwordConfirm: '' });

watch(() => account.pendingEmail, (email) => {
  if (email) resendEmail.value = email;
});

async function submitLogin() {
  localError.value = '';
  await account.login(loginForm.identifier, loginForm.password, loginForm.keepLogin);
}

async function submitRegister() {
  localError.value = '';
  if (registerForm.password !== registerForm.passwordConfirm) {
    localError.value = '비밀번호 확인이 일치하지 않습니다.';
    return;
  }
  if (!/[A-Za-z가-힣]/.test(registerForm.password) || !/\d/.test(registerForm.password)) {
    localError.value = '비밀번호에는 문자와 숫자가 각각 하나 이상 필요합니다.';
    return;
  }
  await account.register(
    registerForm.username,
    registerForm.email,
    registerForm.password,
    registerForm.passwordConfirm,
  );
}

async function submitResend() {
  localError.value = '';
  await account.resendVerification(resendEmail.value);
}

function openVerificationHelp() {
  account.pendingEmail = loginForm.identifier.includes('@') ? loginForm.identifier.trim().toLowerCase() : '';
  account.stage = 'verification';
  account.notice = '';
  resendEmail.value = account.pendingEmail;
}
</script>
