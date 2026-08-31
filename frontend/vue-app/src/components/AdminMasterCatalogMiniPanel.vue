<template>
  <section class="admin-readonly-panel" aria-label="관리자 마스터 카탈로그 조회">
    <div class="admin-readonly-panel__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v278 · GET catalog controls</p>
        <h3>선택 도메인 카탈로그</h3>
        <p>
          기존 <code>GET /admin/master-data/catalog</code> query만 사용합니다.
          검색·활성 상태·정렬·페이지 이동은 조회 조건만 바꾸며 DB를 수정하지 않습니다.
        </p>
      </div>
      <button
        type="button"
        class="admin-readonly-panel__button"
        :disabled="!domain || status === 'loading'"
        @click="loadCatalog"
      >
        {{ status === 'loading' ? '불러오는 중...' : '현재 조건 다시 조회' }}
      </button>
    </div>

    <div v-if="!domain" class="admin-readonly-panel__state" data-state="idle">
      위에서 도메인 목록을 불러오면 카탈로그가 자동으로 표시됩니다.
    </div>

    <template v-else>
      <form class="admin-catalog-controls" @submit.prevent="applySearch">
        <label class="admin-catalog-control admin-catalog-control--search">
          <span>검색어</span>
          <input
            v-model="queryInput"
            type="search"
            maxlength="80"
            :placeholder="searchPlaceholder"
            :disabled="status === 'loading'"
          />
        </label>

        <label class="admin-catalog-control">
          <span>활성 상태</span>
          <select v-model="enabledFilter" :disabled="!supportsEnabledFilter || status === 'loading'" @change="applyImmediateFilters">
            <option value="all">전체</option>
            <option value="enabled">활성만</option>
            <option value="disabled">비활성만</option>
          </select>
        </label>

        <label class="admin-catalog-control">
          <span>정렬</span>
          <select v-model="sort" :disabled="status === 'loading'" @change="applyImmediateFilters">
            <option value="id_asc">ID 오름차순</option>
            <option value="code_asc">코드 오름차순</option>
            <option value="name_asc">이름 오름차순</option>
            <option value="sort_asc">표시 순서</option>
            <option value="updated_desc">최근 수정순</option>
          </select>
        </label>

        <div class="admin-catalog-controls__actions">
          <button type="submit" class="admin-readonly-panel__button" :disabled="status === 'loading'">검색</button>
          <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" :disabled="status === 'loading'" @click="resetFilters">
            초기화
          </button>
        </div>
      </form>

      <p v-if="!supportsEnabledFilter" class="admin-catalog-controls__hint">
        이 도메인은 활성/비활성 필드가 없어 해당 필터가 자동으로 비활성화됩니다.
      </p>

      <div v-if="status === 'loading'" class="admin-readonly-panel__state" data-state="loading">
        <strong>{{ domainLabel || domain }}</strong> 카탈로그를 조회하고 있습니다.
      </div>

      <div v-else-if="status === 'error'" class="admin-readonly-panel__state" data-state="error">
        <strong>카탈로그 조회 오류</strong>
        <p>{{ errorMessage }}</p>
      </div>

      <div v-else-if="status === 'empty'" class="admin-readonly-panel__state" data-state="empty">
        <strong>{{ domainLabel || domain }}</strong>에서 현재 조건에 맞는 row를 찾지 못했습니다.
        <p>검색어 또는 활성 상태 필터를 초기화해보세요.</p>
      </div>

      <template v-else-if="status === 'success' && catalog">
        <div class="admin-catalog-summary">
          <span><strong>{{ catalog.domainLabel || domainLabel || domain }}</strong></span>
          <span>현재 {{ formatCount(catalog.count) }}개</span>
          <span>검색 결과 {{ formatCount(catalog.total) }}개</span>
          <span>전체 {{ formatCount(catalog.totalAll) }}개</span>
          <span>페이지 {{ catalog.page || 1 }} / {{ catalog.totalPages || 1 }}</span>
          <span v-if="catalog.filters?.query">검색 <code>{{ catalog.filters.query }}</code></span>
          <span v-if="catalog.filters?.enabled && catalog.filters.enabled !== 'all'">상태 <code>{{ catalog.filters.enabled }}</code></span>
          <span class="admin-domain-summary__readonly">조회 전용</span>
        </div>

        <ul v-if="catalog.filters?.warnings?.length" class="admin-catalog-warnings" aria-label="카탈로그 조회 경고">
          <li v-for="warning in catalog.filters.warnings" :key="warning">{{ warning }}</li>
        </ul>

        <div class="admin-catalog-table-wrap">
          <table class="admin-catalog-table">
            <thead>
              <tr>
                <th scope="col">상세</th>
                <th v-for="column in catalog.columns" :key="column.key" scope="col">
                  {{ column.label || column.key }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in catalog.rows"
                :key="`${domain}-${row.id}`"
                :class="{ 'admin-catalog-table__row--selected': selectedRowId === row.id }"
              >
                <td>
                  <button type="button" class="admin-catalog-detail-button" @click="selectRow(row)">
                    {{ selectedRowId === row.id ? '선택됨' : '상세 보기' }}
                  </button>
                </td>
                <td v-for="column in catalog.columns" :key="column.key" :title="formatCellValue(row.cells?.[column.key])">
                  {{ formatCellValue(row.cells?.[column.key]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <nav class="admin-catalog-pagination" aria-label="카탈로그 페이지 이동">
          <button
            type="button"
            class="admin-readonly-panel__button admin-readonly-panel__button--secondary"
            :disabled="status === 'loading' || !catalog.hasPrevPage"
            @click="movePage(-1)"
          >
            이전 페이지
          </button>
          <span>{{ catalog.page || 1 }} / {{ catalog.totalPages || 1 }}</span>
          <button
            type="button"
            class="admin-readonly-panel__button admin-readonly-panel__button--secondary"
            :disabled="status === 'loading' || !catalog.hasNextPage"
            @click="movePage(1)"
          >
            다음 페이지
          </button>
        </nav>
      </template>
    </template>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useAdminStore } from '@/stores';

const admin = useAdminStore();

const props = defineProps({
  domain: {
    type: String,
    default: '',
  },
  domainLabel: {
    type: String,
    default: '',
  },
  searchableFields: {
    type: Array,
    default: () => [],
  },
  supportsEnabledFilter: {
    type: Boolean,
    default: false,
  },
  defaultSort: {
    type: String,
    default: 'id_asc',
  },
  selectedRowId: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits(['row-selected']);

const status = ref('idle');
const catalog = ref(null);
const errorMessage = ref('');
const queryInput = ref('');
const appliedQuery = ref('');
const enabledFilter = ref('all');
const sort = ref('id_asc');
const page = ref(1);
let activeController = null;

const searchPlaceholder = computed(() => {
  if (!props.searchableFields.length) return '검색 가능한 필드가 없습니다';
  return `검색 가능: ${props.searchableFields.join(', ')}`;
});

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
    filters: payload.filters && typeof payload.filters === 'object' ? payload.filters : {},
  };
}

function selectRow(row) {
  const rowId = Number(row?.id);
  if (!Number.isInteger(rowId) || rowId <= 0) return;
  emit('row-selected', {
    domain: props.domain,
    rowId,
    title: row?.cells?.name || row?.cells?.code || `#${rowId}`,
  });
}

function applySearch() {
  appliedQuery.value = queryInput.value.trim().slice(0, 80);
  page.value = 1;
  loadCatalog();
}

function applyImmediateFilters() {
  page.value = 1;
  loadCatalog();
}

function resetFilters() {
  queryInput.value = '';
  appliedQuery.value = '';
  enabledFilter.value = 'all';
  sort.value = normalizeSort(props.defaultSort);
  page.value = 1;
  loadCatalog();
}

function movePage(offset) {
  const nextPage = page.value + offset;
  if (nextPage < 1) return;
  if (catalog.value?.totalPages && nextPage > catalog.value.totalPages) return;
  page.value = nextPage;
  loadCatalog();
}

function normalizeSort(value) {
  const allowed = new Set(['id_asc', 'code_asc', 'name_asc', 'sort_asc', 'updated_desc']);
  return allowed.has(value) ? value : 'id_asc';
}

async function loadCatalog() {
  if (!props.domain) {
    status.value = 'idle';
    catalog.value = null;
    emit('row-selected', null);
    return;
  }

  activeController?.abort();
  activeController = new AbortController();
  status.value = 'loading';
  catalog.value = null;
  errorMessage.value = '';
  emit('row-selected', null);

  try {
    const response = await admin.fetchMasterCatalog(
      {
        domain: props.domain,
        limit: 20,
        page: page.value,
        sort: sort.value,
        query: appliedQuery.value,
        enabled: props.supportsEnabledFilter ? enabledFilter.value : 'all',
      },
      { signal: activeController.signal },
    );
    const normalized = normalizeCatalog(response);
    catalog.value = normalized;
    page.value = Number(normalized.page) || page.value;
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
    queryInput.value = '';
    appliedQuery.value = '';
    enabledFilter.value = 'all';
    sort.value = normalizeSort(props.defaultSort);
    page.value = 1;
    loadCatalog();
  },
  { immediate: true },
);

watch(
  () => props.defaultSort,
  (nextSort) => {
    if (!props.domain) return;
    sort.value = normalizeSort(nextSort);
  },
);

onBeforeUnmount(() => {
  activeController?.abort();
});
</script>
