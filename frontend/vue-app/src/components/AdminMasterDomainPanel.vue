<template>
  <section class="admin-readonly-panel" aria-label="관리자 마스터 도메인 목록">
    <div class="admin-readonly-panel__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v276 · GET domains</p>
        <h3>마스터 데이터 도메인</h3>
        <p>
          <code>GET /admin/master-data/domains</code> 응답의 <code>payload.domains</code>만 읽습니다.
          선택은 아래 카탈로그 조회 대상을 바꿀 뿐, DB를 수정하지 않습니다.
        </p>
      </div>
      <button type="button" class="admin-readonly-panel__button" :disabled="status === 'loading'" @click="loadDomains">
        {{ status === 'loading' ? '불러오는 중...' : '도메인 다시 불러오기' }}
      </button>
    </div>

    <div v-if="status === 'loading'" class="admin-readonly-panel__state" data-state="loading">
      도메인 목록을 확인하고 있습니다.
    </div>

    <div v-else-if="status === 'error'" class="admin-readonly-panel__state" data-state="error">
      <strong>도메인 조회 오류</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="status === 'empty'" class="admin-readonly-panel__state" data-state="empty">
      서버 응답은 성공했지만 표시할 도메인이 없습니다.
    </div>

    <template v-else-if="status === 'success'">
      <div class="admin-domain-summary">
        <span>도메인 <strong>{{ domains.length }}</strong>개</span>
        <span>기본 도메인 <code>{{ defaultDomain || '-' }}</code></span>
        <span class="admin-domain-summary__readonly">조회 전용</span>
      </div>

      <ul class="admin-domain-list">
        <li v-for="domain in domains" :key="domain.key">
          <button
            type="button"
            class="admin-domain-card"
            :class="{ 'admin-domain-card--selected': selectedKey === domain.key }"
            :aria-pressed="selectedKey === domain.key"
            @click="selectDomain(domain)"
          >
            <span class="admin-domain-card__title">
              <strong>{{ domain.label || domain.key }}</strong>
              <code>{{ domain.key }}</code>
            </span>
            <span class="admin-domain-card__description">{{ domain.description || '설명 없음' }}</span>
            <span class="admin-domain-card__counts">
              <span>전체 {{ formatCount(domain.total) }}</span>
              <span v-if="domain.supportsEnabledFilter">활성 {{ formatCount(domain.enabled) }}</span>
              <span v-if="domain.supportsEnabledFilter">비활성 {{ formatCount(domain.disabled) }}</span>
            </span>
          </button>
        </li>
      </ul>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAdminStore } from '@/stores';

const admin = useAdminStore();

const emit = defineEmits(['domain-selected']);

const status = ref('idle');
const domains = ref([]);
const defaultDomain = ref('');
const selectedKey = ref('');
const errorMessage = ref('');

function formatCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? count.toLocaleString('ko-KR') : '-';
}

function formatError(error) {
  if (error?.status) {
    return `HTTP ${error.status}: ${error.message}`;
  }
  return error?.message || '알 수 없는 오류가 발생했습니다.';
}

function normalizeDomains(response) {
  const payload = response?.payload && typeof response.payload === 'object' ? response.payload : {};
  const normalizedDomains = Array.isArray(payload.domains)
    ? payload.domains.filter((domain) => domain && typeof domain.key === 'string' && domain.key.trim())
    : [];

  return {
    domains: normalizedDomains,
    defaultDomain: typeof payload.defaultDomain === 'string' ? payload.defaultDomain : '',
  };
}

function selectDomain(domain) {
  if (!domain?.key) return;
  selectedKey.value = domain.key;
  emit('domain-selected', domain);
}

async function loadDomains() {
  status.value = 'loading';
  errorMessage.value = '';

  try {
    const response = await admin.fetchMasterDomains();
    const normalized = normalizeDomains(response);
    domains.value = normalized.domains;
    defaultDomain.value = normalized.defaultDomain;

    if (domains.value.length === 0) {
      selectedKey.value = '';
      status.value = 'empty';
      emit('domain-selected', null);
      return;
    }

    const nextDomain =
      domains.value.find((domain) => domain.key === selectedKey.value)
      || domains.value.find((domain) => domain.key === defaultDomain.value)
      || domains.value[0];

    status.value = 'success';
    selectDomain(nextDomain);
  } catch (error) {
    domains.value = [];
    selectedKey.value = '';
    status.value = 'error';
    errorMessage.value = formatError(error);
    emit('domain-selected', null);
  }
}

onMounted(() => {
  loadDomains();
});
</script>
