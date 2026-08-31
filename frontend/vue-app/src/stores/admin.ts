import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { adminReadOnlyApi } from '@/api';
import { useAccountStore } from './account';

export type AdminAccessStage = 'idle' | 'checking' | 'login' | 'forbidden' | 'ready' | 'retry';

interface RequestOptions {
  signal?: AbortSignal;
}

interface CatalogQuery {
  domain: string;
  limit?: number;
  page?: number;
  sort?: string;
  query?: string;
  enabled?: string;
}

interface DetailQuery {
  domain: string;
  rowId: number;
}

interface RelationsQuery extends DetailQuery {
  limit?: number;
}

export const useAdminStore = defineStore('admin', () => {
  const account = useAccountStore();
  const accessStage = ref<AdminAccessStage>('idle');
  const accessMessage = ref('');
  const busy = computed(() => account.busy || accessStage.value === 'checking');

  function updateAccessFromAccount() {
    if (!account.isAuthenticated) {
      accessStage.value = account.stage === 'retry' ? 'retry' : 'login';
      accessMessage.value = account.notice;
      return false;
    }
    if (!account.isAdmin) {
      accessStage.value = 'forbidden';
      accessMessage.value = '이 계정에는 관리자 권한이 없습니다.';
      return false;
    }
    accessStage.value = 'ready';
    accessMessage.value = '';
    return true;
  }

  async function checkAccess() {
    accessStage.value = 'checking';
    accessMessage.value = '';
    const authenticated = await account.ensureSession();
    if (!authenticated) return updateAccessFromAccount();
    return updateAccessFromAccount();
  }

  async function login(identifier: string, password: string, keepLogin: boolean) {
    accessStage.value = 'checking';
    accessMessage.value = '';
    const authenticated = await account.loginSession(identifier, password, keepLogin);
    if (!authenticated) return updateAccessFromAccount();
    return updateAccessFromAccount();
  }

  async function logout() {
    await account.logout();
    accessStage.value = 'login';
    accessMessage.value = '';
  }

  function requestOptions(options: RequestOptions = {}) {
    return { ...options, token: account.accessToken };
  }

  async function guardRequest<T>(request: () => Promise<T>): Promise<T> {
    try {
      return await request();
    } catch (error) {
      const status = Number((error as { status?: number })?.status ?? 0);
      if (status === 401 || status === 403) {
        if (status === 401) {
          account.invalidateSession('로그인 정보가 만료되었습니다. 관리자 계정으로 다시 로그인해 주세요.');
          accessStage.value = 'login';
          accessMessage.value = account.notice;
        } else {
          account.markAdminDenied();
          accessStage.value = 'forbidden';
          accessMessage.value = '현재 계정의 관리자 권한이 확인되지 않아 관리자 화면을 닫았습니다.';
        }
      }
      throw error;
    }
  }

  function fetchRequirements(options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchRequirements(requestOptions(options)));
  }

  function fetchMasterDomains(options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchMasterDomains(requestOptions(options)));
  }

  function fetchMasterCatalog(query: CatalogQuery, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchMasterCatalog(query, requestOptions(options)));
  }

  function fetchMasterDetail(query: DetailQuery, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchMasterDetail(query, requestOptions(options)));
  }

  function fetchMasterRelations(query: RelationsQuery, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchMasterRelations(query, requestOptions(options)));
  }

  return {
    accessStage,
    accessMessage,
    busy,
    checkAccess,
    login,
    logout,
    fetchRequirements,
    fetchMasterDomains,
    fetchMasterCatalog,
    fetchMasterDetail,
    fetchMasterRelations,
  };
});
