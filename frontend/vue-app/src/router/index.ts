import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { pinia } from '@/stores/pinia';
import { useAdminStore } from '@/stores';
import AdminAccessPage from '@/pages/AdminAccessPage.vue';
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
      requiresAdmin: true,
    },
  },
  {
    path: '/admin/access',
    name: 'admin-access',
    component: AdminAccessPage,
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

router.beforeEach(async (to) => {
  if (!to.meta.requiresAdmin) return true;
  const admin = useAdminStore(pinia);
  if (await admin.checkAccess()) return true;
  return {
    name: 'admin-access',
    query: { reason: admin.accessStage === 'forbidden' ? 'permission' : 'login' },
    replace: true,
  };
});
