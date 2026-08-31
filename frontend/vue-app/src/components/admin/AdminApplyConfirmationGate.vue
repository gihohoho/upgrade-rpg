<template>
  <Teleport to="body">
    <div v-if="open" class="admin-apply-gate-backdrop" @click.self="closeGate">
      <section
        ref="dialog"
        class="admin-apply-gate"
        role="dialog"
        aria-modal="true"
        aria-labelledby="admin-apply-gate-title"
        aria-describedby="admin-apply-gate-description"
        tabindex="-1"
      >
        <header class="admin-apply-gate__header">
          <div>
            <p class="admin-readonly-panel__eyebrow">v383 · confirmation boundary</p>
            <h2 id="admin-apply-gate-title">Apply 전 마지막 확인 준비</h2>
            <p id="admin-apply-gate-description">
              {{ title }}의 최신 Preview와 관리자 본인 확인에 필요한 입력 경계만 점검합니다.
              이 창은 실제 Apply 요청을 보내지 않습니다.
            </p>
          </div>
          <button type="button" class="admin-apply-gate__close" aria-label="확인 창 닫기" @click="closeGate">×</button>
        </header>

        <div class="admin-apply-gate__lock" role="note">
          <strong>DB write 잠금 유지</strong>
          <span>Apply API와 dev key 헤더는 연결되지 않았습니다. 아래 민감 입력은 저장·로그·네트워크 전송 없이 창을 닫을 때 즉시 지웁니다.</span>
        </div>

        <ol class="admin-apply-gate__steps">
          <li :data-state="revalidationState">
            <span class="admin-apply-gate__step-number">1</span>
            <div>
              <strong>최신 Preview 다시 검증</strong>
              <p>같은 초안을 서버 Preview 전용 경로로 한 번 더 계산하고 직전 결과와 SHA-256 지문을 비교합니다.</p>
              <button
                type="button"
                class="admin-readonly-panel__button admin-readonly-panel__button--secondary"
                :disabled="revalidationState === 'checking'"
                data-testid="admin-apply-revalidate"
                @click="$emit('revalidate')"
              >
                {{ revalidationState === 'checking' ? '최신 상태 확인 중…' : 'Preview 다시 검증' }}
              </button>
              <p class="admin-apply-gate__status" :data-state="revalidationState" role="status" aria-live="polite">
                {{ revalidationMessage }}
              </p>
              <code class="admin-apply-gate__fingerprint">기준 {{ shortFingerprint }}</code>
            </div>
          </li>

          <li :data-state="phraseMatches ? 'success' : 'idle'">
            <span class="admin-apply-gate__step-number">2</span>
            <div>
              <strong>서버가 지정한 확인 문구</strong>
              <p>대소문자와 띄어쓰기를 포함해 아래 문구를 정확히 입력해야 합니다.</p>
              <code class="admin-apply-gate__phrase">{{ confirmationText }}</code>
              <label class="admin-apply-gate__field">
                <span>확인 문구 입력</span>
                <input
                  ref="firstInput"
                  v-model="confirmationInput"
                  type="text"
                  autocomplete="off"
                  autocapitalize="none"
                  spellcheck="false"
                  maxlength="80"
                  data-testid="admin-apply-confirmation-input"
                />
              </label>
            </div>
          </li>

          <li :data-state="identityReady ? 'success' : 'idle'">
            <span class="admin-apply-gate__step-number">3</span>
            <div>
              <strong>관리자 본인 확인 경계</strong>
              <p>현재 계정 비밀번호와 별도 dev key가 모두 있어야 다음 승인 단계에서 재인증을 연결할 수 있습니다.</p>
              <div class="admin-apply-gate__field-grid">
                <label class="admin-apply-gate__field">
                  <span>현재 비밀번호 <small>미전송</small></span>
                  <input v-model="passwordInput" type="password" autocomplete="current-password" maxlength="72" data-testid="admin-apply-password-input" />
                </label>
                <label class="admin-apply-gate__field">
                  <span>관리자 dev key <small>미전송</small></span>
                  <input v-model="devKeyInput" type="password" autocomplete="off" maxlength="256" spellcheck="false" data-testid="admin-apply-dev-key-input" />
                </label>
              </div>
            </div>
          </li>

          <li :data-state="acknowledged ? 'success' : 'idle'">
            <span class="admin-apply-gate__step-number">4</span>
            <label class="admin-apply-gate__acknowledgement">
              <input v-model="acknowledged" type="checkbox" />
              <span><strong>영향 범위를 다시 확인했습니다.</strong> Preview에 표시된 대상·diff·차단 사유를 검토했으며, 실제 적용은 별도 DB write 승인 뒤에만 진행합니다.</span>
            </label>
          </li>
        </ol>

        <div class="admin-apply-gate__summary" :data-ready="preparationReady">
          <strong>{{ preparationReady ? '입력 경계 준비 완료' : '아직 확인할 항목이 있습니다' }}</strong>
          <span>{{ preparationReady ? '실제 Apply 연결 전까지 모든 값은 이 창 안에만 유지됩니다.' : '4개 확인 단계를 모두 완료해도 이번 버전에서는 DB에 적용되지 않습니다.' }}</span>
        </div>

        <footer class="admin-apply-gate__actions">
          <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" @click="closeGate">취소하고 입력 지우기</button>
          <button
            type="button"
            class="admin-readonly-panel__button admin-apply-gate__disabled-apply"
            disabled
            data-testid="admin-apply-locked-button"
          >
            {{ preparationReady ? '준비 완료 · Apply는 별도 승인 필요' : '실제 Apply 잠김' }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';

type RevalidationState = 'idle' | 'checking' | 'success' | 'changed' | 'error';

const props = defineProps<{
  open: boolean;
  title: string;
  confirmationText: string;
  baselineFingerprint: string;
  revalidationState: RevalidationState;
  revalidationMessage: string;
}>();

const emit = defineEmits<{
  close: [];
  revalidate: [];
}>();

const dialog = ref<HTMLElement | null>(null);
const firstInput = ref<HTMLInputElement | null>(null);
const confirmationInput = ref('');
const passwordInput = ref('');
const devKeyInput = ref('');
const acknowledged = ref(false);

const phraseMatches = computed(() => confirmationInput.value.trim() === props.confirmationText);
const identityReady = computed(() => passwordInput.value.length > 0 && devKeyInput.value.length > 0);
const preparationReady = computed(() => (
  props.revalidationState === 'success'
  && phraseMatches.value
  && identityReady.value
  && acknowledged.value
));
const shortFingerprint = computed(() => props.baselineFingerprint ? `${props.baselineFingerprint.slice(0, 16)}…` : '계산 전');

function clearSensitiveInputs() {
  confirmationInput.value = '';
  passwordInput.value = '';
  devKeyInput.value = '';
  acknowledged.value = false;
}

function closeGate() {
  clearSensitiveInputs();
  emit('close');
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.open) closeGate();
}

watch(() => props.open, async (open) => {
  if (!open) {
    clearSensitiveInputs();
    window.removeEventListener('keydown', handleKeydown);
    return;
  }
  window.addEventListener('keydown', handleKeydown);
  await nextTick();
  dialog.value?.focus();
}, { immediate: true });

watch(() => props.revalidationState, (state) => {
  if (state === 'changed' || state === 'error') {
    clearSensitiveInputs();
  }
});

onBeforeUnmount(() => {
  clearSensitiveInputs();
  window.removeEventListener('keydown', handleKeydown);
});
</script>
