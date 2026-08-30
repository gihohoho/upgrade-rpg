import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import AdminShell from '@/pages/AdminShell.vue';
import GameShell from '@/pages/GameShell.vue';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/game',
  },
  {
    path: '/game',
    name: 'game-shell',
    component: GameShell,
    meta: {
      legacyEntry: 'index.html',
    },
  },
  {
    path: '/admin',
    name: 'admin-shell',
    component: AdminShell,
    meta: {
      legacyEntry: 'admin.html',
    },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});
