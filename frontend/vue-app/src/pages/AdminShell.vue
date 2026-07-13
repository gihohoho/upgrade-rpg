<template>
  <ShellCard
    label="Admin"
    title="관리자 페이지 Vue 이식 준비"
    description="현재 실제 관리자 도구는 아직 루트 admin.html에서 실행합니다. v276~v279에서는 안전한 GET 도메인·카탈로그·상세 조회만 Vue shell에서 확인합니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>admin.html</code></li>
      <li>현재 Vue 연결 범위: 상태 확인, 도메인 목록, 검색/상태/정렬/페이지네이션, 선택 row 상세</li>
      <li>relations와 Preview/Apply/write는 계약과 화면 경계를 다시 확인한 뒤 단계적으로 옮깁니다.</li>
    </ul>

    <ReadOnlyApiStatusPanel
      title="관리자 안전 GET API 상태 확인"
      description="FastAPI 서버가 켜져 있으면 /health와 /admin/requirements를 자동으로 확인합니다. 둘 다 DB 수정이 없는 조회 API입니다."
      :checks="adminStatusChecks"
    />

    <AdminMasterDomainPanel @domain-selected="handleDomainSelected" />

    <AdminMasterCatalogMiniPanel
      :domain="selectedDomain?.key || ''"
      :domain-label="selectedDomain?.label || ''"
      :searchable-fields="selectedDomain?.searchableFields || []"
      :supports-enabled-filter="Boolean(selectedDomain?.supportsEnabledFilter)"
      :default-sort="selectedDomain?.defaultSort || 'id_asc'"
      :selected-row-id="selectedRow?.rowId || null"
      @row-selected="handleRowSelected"
    />

    <AdminMasterDetailPanel
      :domain="selectedRow?.domain || ''"
      :row-id="selectedRow?.rowId || null"
      :row-title="selectedRow?.title || ''"
      @clear-selection="handleRowSelected(null)"
    />

    <section class="api-route-preview" aria-label="Admin read-only API route preview">
      <h3>읽기 전용 관리자 API 준비 목록</h3>
      <p>도메인·카탈로그·상세 GET까지 화면에 연결했습니다. relations와 모든 Preview/Apply/write는 아직 제외합니다.</p>
      <ul class="api-route-preview__list">
        <li v-for="route in adminRoutes" :key="route.name">
          <code>GET</code>
          <span>{{ route.path }}</span>
          <small>{{ route.name }}</small>
        </li>
      </ul>
    </section>
  </ShellCard>
</template>

<script setup>
import { ref } from 'vue';
import ShellCard from '@/components/ShellCard.vue';
import ReadOnlyApiStatusPanel from '@/components/ReadOnlyApiStatusPanel.vue';
import AdminMasterDomainPanel from '@/components/AdminMasterDomainPanel.vue';
import AdminMasterCatalogMiniPanel from '@/components/AdminMasterCatalogMiniPanel.vue';
import AdminMasterDetailPanel from '@/components/AdminMasterDetailPanel.vue';
import { ADMIN_READONLY_ROUTES, adminReadOnlyApi, healthReadOnlyApi } from '@/api';

const selectedDomain = ref(null);
const selectedRow = ref(null);
const adminRoutes = Object.entries(ADMIN_READONLY_ROUTES).map(([name, path]) => ({ name, path }));

const adminStatusChecks = [
  {
    key: 'health',
    label: 'FastAPI /health',
    description: '백엔드 서버가 응답하는지만 확인합니다. DB를 사용하지 않습니다.',
    run: () => healthReadOnlyApi.fetchHealth(),
  },
  {
    key: 'admin-requirements',
    label: 'Admin /requirements',
    description: '관리자 read-only 화면의 기본 요구사항 응답만 확인합니다. write 요청이 아닙니다.',
    run: () => adminReadOnlyApi.fetchRequirements(),
    summarize: (response) => ({
      type: response?.type || '',
      status: response?.data?.readOnlyOverviewReady ? '준비 완료' : '확인 필요',
    }),
  },
];

function handleDomainSelected(domain) {
  selectedDomain.value = domain;
  selectedRow.value = null;
}

function handleRowSelected(row) {
  selectedRow.value = row;
}
</script>
