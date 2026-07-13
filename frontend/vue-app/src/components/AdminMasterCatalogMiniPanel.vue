<template>
  <section class="admin-readonly-panel" aria-label="관리자 마스터 카탈로그 첫 페이지">
    <div class="admin-readonly-panel__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v277 · GET catalog</p>
        <h3>선택 도메인 첫 카탈로그</h3>
        <p>
          선택된 도메인의 첫 페이지를 <code>limit=20</code>, <code>page=1</code>, <code>sort=id_asc</code>로만 조회합니다.
          검색·페이지 이동·상세·관계·수정 기능은 아직 연결하지 않습니다.
        </p>
      </div>
      <button
        type="button"
        class="admin-readonly-panel__button"
        :disabled="!domain || status === 'loading'"
        @click="loadCatalog"
      >
        {{ status === 'loading' ? '불러오는 중...' : '첫 20개 다시 조회' }}
      </button>
    </div>

    <div v-if="!domain" class="admin-readonly-panel__state" data-state="idle">
      위에서 도메인 목록을 불러오면 첫 카탈로그가 자동으로 표시됩니다.
    </div>

    <div v-else-if="status === 'loading'" class="admin-readonly-panel__state" data-state="loading">
      <strong>{{ domainLabel || domain }}</strong> 첫 페이지를 조회하고 있습니다.
    </div>

    <div v-else-if="status === 'error'" class="admin-readonly-panel__state" data-state="error">
      <strong>카탈로그 조회 오류</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="status === 'empty'" class="admin-readonly-panel__state" data-state="empty">
      <strong>{{ domainLabel || domain }}</strong> 도메인에 표시할 row가 없습니다.
    </div>

    <template v-else-if="status === 'success' && catalog">
      <div class="admin-catalog-summary">
        <span><strong>{{ catalog.domainLabel || domainLabel || domain }}</strong></span>
        <span>현재 {{ formatCount(catalog.count) }}개</span>
        <span>전체 {{ formatCount(catalog.total) }}개</span>
        <span>페이지 {{ catalog.page || 1 }} / {{ catalog.totalPages || 1 }}</span>
        <span class="admin-domain-summary__readonly">조회 전용</span>
      </div>

      <div class="admin-catalog-table-wrap">
        <table class="admin-catalog-table">
          <thead>
            <tr>
              <th v-for="column in catalog.columns" :key="column.key" scope="col">
                {{ column.label || column.key }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in catalog.rows" :key="`${domain}-${row.id}`">
              <td v-for="column in catalog.columns" :key="column.key">
                {{ formatCellValue(row.cells?.[column.key]) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue';
import { adminReadOnlyApi } from '@/api';

const props = defineProps({
  domain: {
    type: String,
    default: '',
  },
  domainLabel: {
    type: String,
    default: '',
  },
});

const status = ref('idle');
const catalog = ref(null);
const errorMessage = ref('');
let activeController = null;

function formatCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? count.toLocaleString('ko-KR') : '-';
}

function formatCellValue(value) {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '예' : '아니오';
  if (typeof value === 'object') {
    const serialized = JSON.stringify(value);
    return serialized.length > 80 ? `${serialized.slice(0, 77)}...` : serialized;
  }
  return String(value);
}

function formatError(error) {
  if (error?.name === 'AbortError') return '';
  if (error?.status) return `HTTP ${error.status}: ${error.message}`;
  return error?.message || '알 수 없는 오류가 발생했습니다.';
}

function normalizeCatalog(response) {
  const payload = response?.payload && typeof response.payload === 'object' ? response.payload : {};
  return {
    ...payload,
    columns: Array.isArray(payload.columns) ? payload.columns.filter((column) => column?.key) : [],
    rows: Array.isArray(payload.rows) ? payload.rows.filter((row) => row && typeof row === 'object') : [],
  };
}

async function loadCatalog() {
  if (!props.domain) {
    status.value = 'idle';
    catalog.value = null;
    return;
  }

  activeController?.abort();
  activeController = new AbortController();
  status.value = 'loading';
  catalog.value = null;
  errorMessage.value = '';

  try {
    const response = await adminReadOnlyApi.fetchMasterCatalog(
      {
        domain: props.domain,
        limit: 20,
        page: 1,
        sort: 'id_asc',
      },
      { signal: activeController.signal },
    );
    const normalized = normalizeCatalog(response);
    catalog.value = normalized;
    status.value = normalized.rows.length > 0 ? 'success' : 'empty';
  } catch (error) {
    if (error?.name === 'AbortError') return;
    status.value = 'error';
    errorMessage.value = formatError(error);
  }
}

watch(
  () => props.domain,
  () => {
    loadCatalog();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  activeController?.abort();
});
</script>
