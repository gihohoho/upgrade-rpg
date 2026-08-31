<template>
  <section class="admin-readonly-panel" aria-label="선택한 마스터 데이터 관계 목록">
    <div class="admin-readonly-panel__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v280~v281 · GET relations</p>
        <h3>선택 row 관계 목록</h3>
        <p>
          <code>GET /admin/master-data/relations</code>의 축약된 관계 그룹만 표시합니다.
          연관 row 버튼은 해당 row의 GET 상세로 이동할 뿐, DB나 관계 값을 수정하지 않습니다.
        </p>
      </div>
      <button
        type="button"
        class="admin-readonly-panel__button"
        :disabled="!domain || !rowId || status === 'loading'"
        @click="loadRelations"
      >
        {{ status === 'loading' ? '불러오는 중...' : '관계 다시 조회' }}
      </button>
    </div>

    <div v-if="!domain || !rowId" class="admin-readonly-panel__state" data-state="idle">
      카탈로그에서 row를 선택하면 연결된 마스터 데이터가 조회 전용으로 표시됩니다.
    </div>

    <div v-else-if="status === 'loading'" class="admin-readonly-panel__state" data-state="loading">
      <strong>{{ rowTitle || `#${rowId}` }}</strong> 관계를 조회하고 있습니다.
    </div>

    <div v-else-if="status === 'error'" class="admin-readonly-panel__state" data-state="error">
      <strong>관계 조회 오류</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="status === 'empty'" class="admin-readonly-panel__state" data-state="empty">
      <strong>{{ relations?.title || rowTitle || `#${rowId}` }}</strong>에 표시할 연결 row가 없습니다.
      <p>관계가 없는 도메인 또는 아직 연결 데이터가 없는 row일 수 있습니다.</p>
    </div>

    <template v-else-if="status === 'success' && relations">
      <div class="admin-catalog-summary">
        <span><strong>{{ relations.title || rowTitle || `#${rowId}` }}</strong></span>
        <span>{{ relations.domainLabel || domain }}</span>
        <span>관계 그룹 {{ formatCount(relations.groupCount) }}개</span>
        <span>관련 row {{ formatCount(relations.totalRelatedRows) }}개</span>
        <span>그룹당 최대 {{ formatCount(relations.limitPerGroup) }}개</span>
        <span class="admin-domain-summary__readonly">조회 전용</span>
      </div>

      <ul v-if="relations.warnings.length" class="admin-catalog-warnings" aria-label="관계 조회 경고">
        <li v-for="warning in relations.warnings" :key="warning">{{ warning }}</li>
      </ul>

      <div class="admin-relations-groups">
        <article v-for="group in relations.groups" :key="`${group.domain}-${group.label}`" class="admin-relations-group">
          <header class="admin-relations-group__header">
            <div>
              <h4>{{ group.label || group.domainLabel || group.domain }}</h4>
              <p>
                <code>{{ group.domain }}</code>
                · 전체 {{ formatCount(group.count) }}개
                · 표시 {{ formatCount(group.shown) }}개
              </p>
            </div>
            <span v-if="group.limited" class="admin-relations-group__limited">일부만 표시</span>
          </header>

          <div class="admin-catalog-table-wrap admin-relations-table-wrap">
            <table class="admin-catalog-table">
              <thead>
                <tr>
                  <th scope="col">상세</th>
                  <th v-for="column in group.columns" :key="column.key" scope="col">
                    {{ column.label || column.key }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in group.rows" :key="`${group.domain}-${row.id}`">
                  <td>
                    <button
                      type="button"
                      class="admin-catalog-detail-button"
                      @click="openRelatedDetail(group, row)"
                    >
                      이 row 상세
                    </button>
                  </td>
                  <td v-for="column in group.columns" :key="column.key" :title="formatValue(row.cells?.[column.key])">
                    {{ formatValue(row.cells?.[column.key]) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <p class="admin-detail-note">
        연관 row 상세 이동은 현재 선택 기록을 보존합니다. 상세 패널의 <strong>이전 상세로</strong> 버튼으로 돌아올 수 있습니다.
      </p>
    </template>
  </section>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue';
import { useAdminStore } from '@/stores';

const admin = useAdminStore();

const props = defineProps({
  domain: {
    type: String,
    default: '',
  },
  rowId: {
    type: Number,
    default: null,
  },
  rowTitle: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['related-row-selected']);

const status = ref('idle');
const relations = ref(null);
const errorMessage = ref('');
let activeController = null;

function formatCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? count.toLocaleString('ko-KR') : '0';
}

function formatValue(value) {
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

function normalizeRelations(response) {
  const payload = response?.payload && typeof response.payload === 'object' ? response.payload : {};
  const groups = Array.isArray(payload.groups)
    ? payload.groups
      .filter((group) => group && typeof group === 'object' && typeof group.domain === 'string')
      .map((group) => ({
        ...group,
        columns: Array.isArray(group.columns) ? group.columns.filter((column) => column?.key) : [],
        rows: Array.isArray(group.rows) ? group.rows.filter((row) => row && typeof row === 'object') : [],
      }))
    : [];

  return {
    ...payload,
    groups,
    warnings: Array.isArray(payload.warnings) ? payload.warnings : [],
  };
}

function openRelatedDetail(group, row) {
  const rowId = Number(row?.id);
  if (!group?.domain || !Number.isInteger(rowId) || rowId <= 0) return;

  emit('related-row-selected', {
    domain: group.domain,
    domainLabel: group.domainLabel || group.domain,
    rowId,
    title: row?.title || row?.cells?.name || row?.cells?.code || `#${rowId}`,
  });
}

async function loadRelations() {
  if (!props.domain || !props.rowId) {
    status.value = 'idle';
    relations.value = null;
    return;
  }

  activeController?.abort();
  activeController = new AbortController();
  status.value = 'loading';
  relations.value = null;
  errorMessage.value = '';

  try {
    const response = await admin.fetchMasterRelations(
      { domain: props.domain, rowId: props.rowId, limit: 20 },
      { signal: activeController.signal },
    );
    const normalized = normalizeRelations(response);
    relations.value = normalized;
    status.value = normalized.status === 'loaded' && normalized.groups.length > 0 ? 'success' : 'empty';
  } catch (error) {
    if (error?.name === 'AbortError') return;
    status.value = 'error';
    errorMessage.value = formatError(error);
  }
}

watch(
  () => [props.domain, props.rowId],
  () => {
    loadRelations();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  activeController?.abort();
});
</script>
