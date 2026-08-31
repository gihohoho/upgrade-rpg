<template>
  <ShellCard
    label="Admin"
    title="관리자 조회와 변경 전 검증"
    description="서버에서 관리자 권한을 확인한 계정에만 조회와 dry-run Preview를 표시합니다. 실제 Apply는 계속 admin.html에서만 실행합니다."
  >
    <section class="admin-session-bar" aria-label="현재 관리자 계정">
      <div>
        <span class="admin-session-bar__status"><i aria-hidden="true" /> 관리자 인증 완료</span>
        <strong>{{ account.user?.username }}</strong>
        <small>서버가 확인한 <code>isAdmin=true</code> 계정으로만 아래 조회 화면을 생성했습니다.</small>
      </div>
      <button class="account-button account-button--ghost" type="button" :disabled="admin.busy" @click="logoutAdmin">
        관리자 로그아웃
      </button>
    </section>

    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>admin.html</code></li>
      <li>현재 Vue 연결 범위: 상태 확인, 도메인·카탈로그·상세·관계 조회, 생성·수정·되돌리기 Preview</li>
      <li>연관 row 상세 이동과 이전 상세 돌아가기는 GET 조회만 사용합니다.</li>
      <li>Preview POST는 항상 <code>dryRun: true</code>이며 Apply/dev key/write는 계속 제외합니다.</li>
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
      :selected-row-id="selectedRow?.domain === selectedDomain?.key ? selectedRow?.rowId : undefined"
      @row-selected="handleRowSelected"
    />

    <AdminMasterDetailPanel
      :domain="selectedRow?.domain || ''"
      :row-id="selectedRow?.rowId || undefined"
      :row-title="selectedRow?.title || ''"
      :navigation-depth="selectionHistory.length"
      @back-selection="handleBackSelection"
      @clear-selection="clearRowSelection"
    />

    <AdminMasterRelationsPanel
      :domain="selectedRow?.domain || ''"
      :row-id="selectedRow?.rowId || undefined"
      :row-title="selectedRow?.title || ''"
      @related-row-selected="handleRelatedRowSelected"
    />

    <AdminPreviewWorkspace
      :domain="selectedDomain?.key || ''"
      :domain-label="selectedDomain?.label || ''"
      :row-id="selectedRow?.domain === selectedDomain?.key ? selectedRow?.rowId : undefined"
      :row-title="selectedRow?.domain === selectedDomain?.key ? selectedRow?.title : ''"
    />

    <section class="api-route-preview" aria-label="Admin read-only API route preview">
      <h3>읽기 전용 관리자 API 준비 목록</h3>
      <p>도메인·카탈로그·상세·관계 GET을 연결했습니다. 별도 Preview 작업대는 허용된 dry-run POST만 사용하고 Apply/write는 제외합니다.</p>
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

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import ShellCard from '@/components/ShellCard.vue';
import ReadOnlyApiStatusPanel from '@/components/ReadOnlyApiStatusPanel.vue';
import AdminMasterDomainPanel from '@/components/AdminMasterDomainPanel.vue';
import AdminMasterCatalogMiniPanel from '@/components/AdminMasterCatalogMiniPanel.vue';
import AdminMasterDetailPanel from '@/components/AdminMasterDetailPanel.vue';
import AdminMasterRelationsPanel from '@/components/AdminMasterRelationsPanel.vue';
import AdminPreviewWorkspace from '@/components/admin/AdminPreviewWorkspace.vue';
import { ADMIN_READONLY_ROUTES, healthReadOnlyApi } from '@/api';
import { useAccountStore, useAdminStore } from '@/stores';

interface AdminDomain {
  key: string;
  label?: string;
  searchableFields?: string[];
  supportsEnabledFilter?: boolean;
  defaultSort?: string;
}

interface AdminRowSelection {
  domain: string;
  rowId: number;
  title: string;
}

const router = useRouter();
const account = useAccountStore();
const admin = useAdminStore();

const selectedDomain = ref<AdminDomain | null>(null);
const selectedRow = ref<AdminRowSelection | null>(null);
const selectionHistory = ref<AdminRowSelection[]>([]);
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
    run: () => admin.fetchRequirements(),
    summarize: (response: unknown) => {
      const value = response as { type?: string; data?: { readOnlyOverviewReady?: boolean } };
      return {
        type: value?.type || '',
        status: value?.data?.readOnlyOverviewReady ? '준비 완료' : '확인 필요',
      };
    },
  },
];

function handleDomainSelected(domain: AdminDomain | null) {
  selectedDomain.value = domain;
  selectedRow.value = null;
  selectionHistory.value = [];
}

function handleRowSelected(row: AdminRowSelection | null) {
  selectedRow.value = row;
  selectionHistory.value = [];
}

function handleRelatedRowSelected(row: AdminRowSelection | null) {
  if (!row?.domain || !row?.rowId) return;
  if (selectedRow.value) {
    selectionHistory.value.push(selectedRow.value);
  }
  selectedRow.value = row;
}

function handleBackSelection() {
  selectedRow.value = selectionHistory.value.pop() || null;
}

function clearRowSelection() {
  selectedRow.value = null;
  selectionHistory.value = [];
}

async function logoutAdmin() {
  await admin.logout();
}

watch(
  () => admin.accessStage,
  (stage) => {
    if (stage !== 'ready') void router.replace({ name: 'admin-access' });
  },
);
</script>
