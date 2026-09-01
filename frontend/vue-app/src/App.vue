<template>
  <a class="skip-link" href="#main-content">본문으로 바로가기</a>

  <div class="app-layout" :class="{ 'app-layout--menu-open': app.sidebarOpen }">
    <button
      v-if="app.sidebarOpen"
      class="app-layout__scrim"
      type="button"
      aria-label="메뉴 밖 영역 닫기"
      @click="app.closeSidebar"
    />

    <aside class="app-sidebar" aria-label="Vue 전환 메뉴">
      <div class="app-sidebar__header">
        <div class="app-brand">
          <span class="app-brand__mark" aria-hidden="true">U</span>
          <div>
            <strong>Upgrade RPG</strong>
            <span>Vue workspace</span>
          </div>
        </div>
        <button class="app-sidebar__close" type="button" aria-label="메뉴 닫기" @click="app.closeSidebar">
          <span aria-hidden="true">×</span>
        </button>
      </div>

      <nav class="vue-shell__nav" aria-label="Vue shell navigation">
        <RouterLink to="/game" @click="app.closeSidebar">
          <span class="vue-shell__nav-icon" aria-hidden="true">◆</span>
          <span><strong>게임 화면</strong><small>플레이 UI 전환</small></span>
        </RouterLink>
        <RouterLink to="/admin" @click="app.closeSidebar">
          <span class="vue-shell__nav-icon" aria-hidden="true">▦</span>
          <span><strong>관리자 화면</strong><small>데이터 관리 UI</small></span>
        </RouterLink>
      </nav>

      <section class="migration-summary" aria-label="Vue 전환 진행 상황">
        <div class="migration-summary__heading">
          <span>전환 단계</span>
          <strong>{{ app.progressLabel }}</strong>
        </div>
        <ol>
          <li v-for="item in app.milestones" :key="item.key" :data-state="item.state">
            <span aria-hidden="true" />
            {{ item.label }}
          </li>
        </ol>
      </section>
    </aside>

    <main id="main-content" class="vue-shell">
      <header class="vue-shell__header">
        <button class="vue-shell__menu" type="button" aria-label="메뉴 열기" @click="app.toggleSidebar">
          <span aria-hidden="true">☰</span>
        </button>
        <div>
          <p class="vue-shell__eyebrow">Upgrade RPG · v388</p>
          <h1>Vue 전환 작업공간</h1>
          <p>기존 서비스는 유지하면서, 새 화면을 안전하게 하나씩 옮깁니다.</p>
        </div>
        <span class="vue-shell__phase"><i aria-hidden="true" /> 인벤토리·장비 UI 기반 완료</span>
      </header>

      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores';

const app = useAppStore();
</script>
