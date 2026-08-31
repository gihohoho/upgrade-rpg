import { computed, ref } from 'vue';
import { defineStore } from 'pinia';

export type MigrationArea = 'foundation' | 'account' | 'admin' | 'game' | 'cutover';

interface MigrationMilestone {
  key: MigrationArea;
  label: string;
  state: 'done' | 'active' | 'waiting';
}

export const useAppStore = defineStore('app', () => {
  const sidebarOpen = ref(false);
  const milestones = ref<MigrationMilestone[]>([
    { key: 'foundation', label: 'Vue 공통 기반', state: 'done' },
    { key: 'account', label: '계정·캐릭터', state: 'done' },
    { key: 'admin', label: '관리자 화면', state: 'done' },
    { key: 'game', label: '게임 화면', state: 'active' },
    { key: 'cutover', label: '기본 화면 전환', state: 'waiting' },
  ]);

  const completedCount = computed(() => milestones.value.filter((item) => item.state === 'done').length);
  const progressLabel = computed(() => `${completedCount.value}/${milestones.value.length}`);

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value;
  }

  function closeSidebar() {
    sidebarOpen.value = false;
  }

  return { sidebarOpen, milestones, progressLabel, toggleSidebar, closeSidebar };
});
