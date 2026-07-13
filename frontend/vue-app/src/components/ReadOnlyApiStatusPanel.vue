<template>
  <section class="api-status-panel" :aria-label="title">
    <div class="api-status-panel__header">
      <div>
        <p class="api-status-panel__eyebrow">GET API smoke</p>
        <h3>{{ title }}</h3>
        <p>{{ description }}</p>
      </div>
      <button type="button" class="api-status-panel__retry" :disabled="isRunning" @click="runChecks">
        {{ isRunning ? '확인 중...' : '다시 확인' }}
      </button>
    </div>

    <ul class="api-status-panel__list">
      <li v-for="check in checkStates" :key="check.key" :data-status="check.status">
        <div class="api-status-panel__item-head">
          <strong>{{ check.label }}</strong>
          <span class="api-status-panel__chip">{{ statusLabelMap[check.status] }}</span>
        </div>
        <p>{{ check.description }}</p>
        <dl v-if="check.summary" class="api-status-panel__summary">
          <div>
            <dt>응답 type</dt>
            <dd>{{ check.summary.type || '-' }}</dd>
          </div>
          <div>
            <dt>상태</dt>
            <dd>{{ check.summary.status || '-' }}</dd>
          </div>
        </dl>
        <p v-if="check.error" class="api-status-panel__error">{{ check.error }}</p>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  checks: {
    type: Array,
    required: true,
  },
});

const statusLabelMap = Object.freeze({
  idle: '대기',
  loading: '확인 중',
  success: '성공',
  error: '오류',
});

const checkStates = ref(createInitialStates());
const isRunning = computed(() => checkStates.value.some((check) => check.status === 'loading'));

function createInitialStates() {
  return props.checks.map((check) => ({
    key: check.key,
    label: check.label,
    description: check.description,
    run: check.run,
    status: 'idle',
    summary: null,
    error: '',
  }));
}

function summarizeResponse(response) {
  return {
    type: response?.type || '',
    status: response?.data?.status || response?.payload?.status || response?.status || '',
  };
}

function formatError(error) {
  if (error?.status) {
    return `HTTP ${error.status}: ${error.message}`;
  }
  if (error?.name === 'AbortError') {
    return '요청이 취소되었습니다.';
  }
  return error?.message || '알 수 없는 오류가 발생했습니다.';
}

async function runChecks() {
  checkStates.value = createInitialStates().map((check) => ({ ...check, status: 'loading' }));

  const results = await Promise.all(
    checkStates.value.map(async (check) => {
      try {
        const response = await check.run();
        return {
          ...check,
          status: 'success',
          summary: summarizeResponse(response),
          error: '',
        };
      } catch (error) {
        return {
          ...check,
          status: 'error',
          summary: null,
          error: formatError(error),
        };
      }
    }),
  );

  checkStates.value = results;
}

onMounted(() => {
  runChecks();
});
</script>
