<template>
  <section class="admin-readonly-panel" aria-label="선택한 마스터 데이터 상세">
    <div class="admin-readonly-panel__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v279~v281 · GET detail</p>
        <h3>선택 row 상세</h3>
        <p>
          표의 <strong>상세 보기</strong>를 누르면 <code>GET /admin/master-data/detail</code>의 안전하게 정리된 응답만 표시합니다.
          관계 목록은 별도 GET 패널에서 확인하며 편집·Preview·Apply·write는 연결하지 않습니다.
        </p>
      </div>
      <div class="admin-detail-actions">
        <button
          type="button"
          class="admin-readonly-panel__button"
          :disabled="!domain || !rowId || status === 'loading'"
          @click="loadDetail"
        >
          {{ status === 'loading' ? '불러오는 중...' : '상세 다시 조회' }}
        </button>
        <button
          v-if="navigationDepth > 0"
          type="button"
          class="admin-readonly-panel__button admin-readonly-panel__button--secondary"
          @click="goBackSelection"
        >
          이전 상세로
        </button>
        <button
          v-if="rowId"
          type="button"
          class="admin-readonly-panel__button admin-readonly-panel__button--secondary"
          @click="clearSelection"
        >
          선택 해제
        </button>
      </div>
    </div>

    <div v-if="!domain || !rowId" class="admin-readonly-panel__state" data-state="idle">
      위 카탈로그 표에서 <strong>상세 보기</strong>를 누르면 조회 전용 상세가 표시됩니다.
    </div>

    <div v-else-if="status === 'loading'" class="admin-readonly-panel__state" data-state="loading">
      <strong>{{ rowTitle || `#${rowId}` }}</strong> 상세를 조회하고 있습니다.
    </div>

    <div v-else-if="status === 'error'" class="admin-readonly-panel__state" data-state="error">
      <strong>상세 조회 오류</strong>
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="status === 'empty'" class="admin-readonly-panel__state" data-state="empty">
      선택한 row의 상세 응답을 찾지 못했습니다.
    </div>

    <template v-else-if="status === 'success' && detail">
      <div class="admin-catalog-summary">
        <span><strong>{{ detail.title || rowTitle || `#${rowId}` }}</strong></span>
        <span>{{ detail.domainLabel || domain }}</span>
        <span>ID {{ detail.id }}</span>
        <span>JSON 안전 미리보기 {{ detail.sanitizedJsonReturned ? '예' : '아니오' }}</span>
        <span>이미지 원본 반환 {{ detail.assetsReturned ? '예' : '아니오' }}</span>
        <span class="admin-domain-summary__readonly">조회 전용</span>
      </div>

      <ul v-if="detail.warnings?.length" class="admin-catalog-warnings" aria-label="상세 조회 경고">
        <li v-for="warning in detail.warnings" :key="warning">{{ warning }}</li>
      </ul>

      <section class="admin-detail-section">
        <h4>기본 필드</h4>
        <dl v-if="detail.fields.length" class="admin-detail-grid">
          <div v-for="field in detail.fields" :key="field.key">
            <dt>{{ field.label || field.key }}</dt>
            <dd>{{ formatValue(field.value) }}</dd>
          </div>
        </dl>
        <p v-else class="admin-detail-empty">표시할 기본 필드가 없습니다.</p>
      </section>

      <section v-if="detail.relationHints.length" class="admin-detail-section">
        <h4>관계 힌트</h4>
        <dl class="admin-detail-grid admin-detail-grid--compact">
          <div v-for="hint in detail.relationHints" :key="`${hint.label}-${formatValue(hint.value)}`">
            <dt>{{ hint.label }}</dt>
            <dd>{{ formatValue(hint.value) }}</dd>
          </div>
        </dl>
        <p class="admin-detail-note">숫자와 코드 힌트는 여기서 확인하고, 실제 축약 관계 목록은 아래 GET 관계 패널에서 확인합니다.</p>
      </section>

      <section v-if="detail.jsonFields.length" class="admin-detail-section">
        <h4>JSON 안전 미리보기</h4>
        <div class="admin-detail-json-list">
          <article v-for="field in detail.jsonFields" :key="field.key" class="admin-detail-json-card">
            <div class="admin-detail-json-card__header">
              <strong>{{ field.label || field.key }}</strong>
              <span>숨긴 asset {{ formatCount(field.hiddenAssetCount) }} · 축약 {{ formatCount(field.truncatedCount) }}</span>
            </div>
            <pre>{{ formatJson(field.preview) }}</pre>
          </article>
        </div>
      </section>

      <section v-if="detail.assetFields.length" class="admin-detail-section">
        <h4>Asset 필드 보호 상태</h4>
        <ul class="admin-detail-asset-list">
          <li v-for="field in detail.assetFields" :key="field.key">
            <strong>{{ field.label || field.key }}</strong>
            <span>{{ field.hidden ? '원본 숨김' : formatValue(field.value) }}</span>
          </li>
        </ul>
      </section>
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
  rowId: {
    type: Number,
    default: null,
  },
  rowTitle: {
    type: String,
    default: '',
  },
  navigationDepth: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(['clear-selection', 'back-selection']);

const status = ref('idle');
const detail = ref(null);
const errorMessage = ref('');
let activeController = null;

function formatCount(value) {
  const count = Number(value);
  return Number.isFinite(count) ? count.toLocaleString('ko-KR') : '0';
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '예' : '아니오';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function formatJson(value) {
  if (value === null || value === undefined) return '-';
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function formatError(error) {
  if (error?.name === 'AbortError') return '';
  if (error?.status) return `HTTP ${error.status}: ${error.message}`;
  return error?.message || '알 수 없는 오류가 발생했습니다.';
}

function normalizeDetail(response) {
  const payload = response?.payload && typeof response.payload === 'object' ? response.payload : {};
  return {
    ...payload,
    fields: Array.isArray(payload.fields) ? payload.fields.filter((field) => field && typeof field === 'object') : [],
    jsonFields: Array.isArray(payload.jsonFields) ? payload.jsonFields.filter((field) => field && typeof field === 'object') : [],
    assetFields: Array.isArray(payload.assetFields) ? payload.assetFields.filter((field) => field && typeof field === 'object') : [],
    relationHints: Array.isArray(payload.relationHints) ? payload.relationHints.filter((hint) => hint && typeof hint === 'object') : [],
    warnings: Array.isArray(payload.warnings) ? payload.warnings : [],
  };
}

function clearSelection() {
  emit('clear-selection');
}

function goBackSelection() {
  emit('back-selection');
}

async function loadDetail() {
  if (!props.domain || !props.rowId) {
    status.value = 'idle';
    detail.value = null;
    return;
  }

  activeController?.abort();
  activeController = new AbortController();
  status.value = 'loading';
  detail.value = null;
  errorMessage.value = '';

  try {
    const response = await adminReadOnlyApi.fetchMasterDetail(
      { domain: props.domain, rowId: props.rowId },
      { signal: activeController.signal },
    );
    const normalized = normalizeDetail(response);
    detail.value = normalized;
    status.value = normalized.status === 'loaded' ? 'success' : 'empty';
  } catch (error) {
    if (error?.name === 'AbortError') return;
    status.value = 'error';
    errorMessage.value = formatError(error);
  }
}

watch(
  () => [props.domain, props.rowId],
  () => {
    loadDetail();
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  activeController?.abort();
});
</script>
