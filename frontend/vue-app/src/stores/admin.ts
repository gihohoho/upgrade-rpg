import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { adminPreviewApi, adminReadOnlyApi } from '@/api';
import type { AdminPreviewEnvelope, AdminPreviewKind, JsonRecord } from '@/api/adminPreviewApi';
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

interface ChangeLogQuery {
  limit?: number;
  sort?: string;
  action?: string;
  targetType?: string;
  targetId?: string;
  changedKey?: string;
  applied?: boolean;
}

export const useAdminStore = defineStore('admin', () => {
  const account = useAccountStore();
  const accessStage = ref<AdminAccessStage>('idle');
  const accessMessage = ref('');
  const previewBusy = ref(false);
  const previewKind = ref<AdminPreviewKind | null>(null);
  const previewResult = ref<AdminPreviewEnvelope | null>(null);
  const previewError = ref('');
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
    clearPreview();
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
        clearPreview();
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

  function fetchMasterCreateBlueprint(domain: string, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchMasterCreateBlueprint({ domain }, requestOptions(options)));
  }

  function fetchChangeLogs(query: ChangeLogQuery = {}, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchChangeLogs(query, requestOptions(options)));
  }

  function fetchChangeLogDetail(changeLogId: number, options: RequestOptions = {}) {
    return guardRequest(() => adminReadOnlyApi.fetchChangeLogDetail({ changeLogId }, requestOptions(options)));
  }

  function clearPreview() {
    previewKind.value = null;
    previewResult.value = null;
    previewError.value = '';
  }

  async function runPreview(kind: AdminPreviewKind, request: () => Promise<AdminPreviewEnvelope>) {
    previewBusy.value = true;
    previewKind.value = kind;
    previewResult.value = null;
    previewError.value = '';
    try {
      const response = await guardRequest(request);
      previewResult.value = response;
      return response;
    } catch (error) {
      previewError.value = String((error as { message?: string })?.message || 'Preview 요청을 처리하지 못했습니다.');
      throw error;
    } finally {
      previewBusy.value = false;
    }
  }

  function previewCreate(payload: { domain: string; draft: JsonRecord; reason?: string; signal?: AbortSignal }) {
    return runPreview('create', () => adminPreviewApi.previewCreate({ ...payload, token: account.accessToken }));
  }

  function previewEdit(payload: { domain: string; rowId: number; draft: JsonRecord; baseValues: JsonRecord; reason?: string; signal?: AbortSignal }) {
    return runPreview('edit', () => adminPreviewApi.previewEdit({ ...payload, token: account.accessToken }));
  }

  function previewRollback(payload: { changeLogId: number; reason?: string; signal?: AbortSignal }) {
    return runPreview('rollback', () => adminPreviewApi.previewRollback({ ...payload, token: account.accessToken }));
  }

  function previewCreateDelete(payload: { changeLogId: number; reason?: string; signal?: AbortSignal }) {
    return runPreview('create-delete', () => adminPreviewApi.previewCreateDelete({ ...payload, token: account.accessToken }));
  }

  function previewCreateDeleteRestore(payload: { changeLogId: number; reason?: string; signal?: AbortSignal }) {
    return runPreview('create-delete-restore', () => adminPreviewApi.previewCreateDeleteRestore({ ...payload, token: account.accessToken }));
  }

  return {
    accessStage,
    accessMessage,
    busy,
    previewBusy,
    previewKind,
    previewResult,
    previewError,
    checkAccess,
    login,
    logout,
    fetchRequirements,
    fetchMasterDomains,
    fetchMasterCatalog,
    fetchMasterDetail,
    fetchMasterRelations,
    fetchMasterCreateBlueprint,
    fetchChangeLogs,
    fetchChangeLogDetail,
    clearPreview,
    previewCreate,
    previewEdit,
    previewRollback,
    previewCreateDelete,
    previewCreateDeleteRestore,
  };
});
