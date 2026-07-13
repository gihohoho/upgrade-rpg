<template>
  <ShellCard
    label="Game"
    title="게임 화면 Vue 이식 준비"
    description="현재 실제 게임은 아직 루트 index.html과 legacy src/에서 실행합니다. v272에서는 Vue shell에서 FastAPI health GET만 먼저 확인합니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>index.html</code></li>
      <li>나중에 이식할 후보: <code>src/state</code>, <code>src/systems</code>, <code>src/ui</code></li>
      <li>이번 단계에서는 장비/스킬/보스/필드 같은 게임 콘텐츠를 추가하지 않습니다.</li>
    </ul>

    <ReadOnlyApiStatusPanel
      title="게임 Vue Shell 안전 GET API 상태 확인"
      description="게임 master-data/save-slots는 DB 상태에 영향을 받으므로 아직 자동 호출하지 않고, 공통 /health만 먼저 확인합니다."
      :checks="gameStatusChecks"
    />

    <section class="api-route-preview" aria-label="Game read-only API route preview">
      <h3>v272 읽기 전용 게임 API 준비 목록</h3>
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
