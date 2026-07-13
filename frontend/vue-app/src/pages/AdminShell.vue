<template>
  <ShellCard
    label="Admin"
    title="관리자 페이지 Vue 이식 준비"
    description="현재 실제 관리자 도구는 아직 루트 admin.html에서 실행합니다. v271에서는 Vue에서 사용할 읽기 전용 API 경로와 client 구조만 준비했습니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>admin.html</code></li>
      <li>초기 이식 후보: 읽기 전용 카탈로그, 상세 조회, 안내 패널</li>
      <li>Preview/Apply/write 관련 기능은 계약과 요청 body를 다시 확인한 뒤 가장 나중에 옮깁니다.</li>
    </ul>

    <section class="api-route-preview" aria-label="Admin read-only API route preview">
      <h3>v271 읽기 전용 관리자 API 준비 목록</h3>
      <p>아래 경로들은 Vue shell에서 바로 호출하지 않고, API client 구조와 이름만 먼저 고정했습니다.</p>
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
import { ADMIN_READONLY_ROUTES } from '@/api';

const adminRoutes = Object.entries(ADMIN_READONLY_ROUTES).map(([name, path]) => ({ name, path }));
</script>
