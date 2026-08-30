<template>
  <ShellCard
    label="Game"
    title="게임 화면 전환 준비"
    description="현재 서비스 중인 게임은 그대로 유지합니다. v379부터 TypeScript·Pinia 기반 위에 계정과 캐릭터 선택부터 순서대로 옮깁니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>index.html</code></li>
      <li>새 Vue 화면 기반: <code>TypeScript</code>, <code>Pinia</code>, <code>Vue Router</code></li>
      <li>다음 순서: 로그인·이메일 인증 → 캐릭터 선택 → 실제 게임 UI</li>
      <li>게임 규칙은 UI와 분리해 기존 검증 결과를 유지하며 옮깁니다.</li>
    </ul>

    <ReadOnlyApiStatusPanel
      title="게임 Vue Shell 안전 GET API 상태 확인"
      description="게임 master-data/save-slots는 DB 상태에 영향을 받으므로 아직 자동 호출하지 않고, 공통 /health만 먼저 확인합니다."
      :checks="gameStatusChecks"
    />

    <section class="api-route-preview" aria-label="Game read-only API route preview">
      <h3>읽기 전용 게임 API 준비 목록</h3>
      <p>세이브 저장 같은 write API는 아직 Vue client에 연결하지 않았습니다.</p>
      <ul class="api-route-preview__list">
        <li v-for="route in gameRoutes" :key="route.name">
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
import { GAME_READONLY_ROUTES, gameReadOnlyApi, healthReadOnlyApi } from '@/api';

const gameRoutes = Object.entries(GAME_READONLY_ROUTES).map(([name, path]) => ({ name, path }));

const gameStatusChecks = [
  {
    key: 'health',
    label: 'FastAPI /health',
    description: '게임 API를 붙이기 전에 백엔드 서버 응답만 먼저 확인합니다.',
    run: () => healthReadOnlyApi.fetchHealth(),
  },
];

void gameReadOnlyApi;
</script>
