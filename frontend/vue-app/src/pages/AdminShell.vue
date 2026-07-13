<template>
  <ShellCard
    label="Admin"
    title="관리자 페이지 Vue 이식 준비"
    description="현재 실제 관리자 도구는 아직 루트 admin.html에서 실행합니다. v272에서는 안전한 GET API만 Vue shell 화면에서 실제로 확인합니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>admin.html</code></li>
      <li>초기 이식 후보: 읽기 전용 카탈로그, 상세 조회, 안내 패널</li>
      <li>Preview/Apply/write 관련 기능은 계약과 요청 body를 다시 확인한 뒤 가장 나중에 옮깁니다.</li>
    </ul>

    <ReadOnlyApiStatusPanel
      title="관리자 안전 GET API 상태 확인"
      description="FastAPI 서버가 켜져 있으면 /health와 /admin/requirements를 자동으로 확인합니다. 둘 다 DB 수정이 없는 조회 API입니다."
      :checks="adminStatusChecks"
    />

    <section class="api-route-preview" aria-label="Admin read-only API route preview">
      <h3>v272 읽기 전용 관리자 API 준비 목록</h3>
      <p>아래 경로 중 자동 화면 확인은 안전한 일부 GET만 연결했습니다. Preview/Apply/write는 아직 제외합니다.</p>
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
import ShellCard from '@/components/ShellCard.vue';
import ReadOnlyApiStatusPanel from '@/components/ReadOnlyApiStatusPanel.vue';
import { ADMIN_READONLY_ROUTES, adminReadOnlyApi, healthReadOnlyApi } from '@/api';

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
  },
];
</script>
