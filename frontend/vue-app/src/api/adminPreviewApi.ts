import { requestApi } from './http';
import type { ApiEnvelope } from './contracts';

export type AdminPreviewKind = 'create' | 'edit' | 'rollback' | 'create-delete' | 'create-delete-restore';
export type JsonRecord = Record<string, unknown>;

export interface AdminPreviewChange {
  key?: string;
  label?: string;
  before?: unknown;
  after?: unknown;
  current?: unknown;
  expectedAfter?: unknown;
  rollbackTo?: unknown;
  base?: unknown;
  reason?: string;
  relation?: JsonRecord | null;
}

export interface AdminPreviewPayload extends JsonRecord {
  status?: string;
  readOnly?: boolean;
  dryRun?: boolean;
  writeBlocked?: boolean;
  note?: string;
  warnings?: string[];
  domain?: string;
  domainLabel?: string;
  id?: number;
  changeLogId?: number;
  createApplyReady?: boolean;
  editApplyReady?: boolean;
  applyReady?: boolean;
  rollbackReady?: boolean;
  createDeleteReady?: boolean;
  createDeleteRestoreReady?: boolean;
  wouldBeValid?: boolean;
  currentMatchesAfter?: boolean;
  targetRowMissing?: boolean;
  idConflict?: boolean;
  codeConflict?: boolean;
  diffCount?: number;
  errorCount?: number;
  staleCount?: number;
  dependencyBlockerCount?: number;
  validationErrorCount?: number;
  acceptedFields?: AdminPreviewChange[];
  rejectedFields?: AdminPreviewChange[];
  acceptedChanges?: AdminPreviewChange[];
  rejectedChanges?: AdminPreviewChange[];
  staleChanges?: AdminPreviewChange[];
  changes?: AdminPreviewChange[];
  currentMismatches?: AdminPreviewChange[];
  dependencyChecks?: AdminPreviewChange[];
  validationErrors?: AdminPreviewChange[];
}

export type AdminPreviewEnvelope = ApiEnvelope<AdminPreviewPayload, JsonRecord>;

interface PreviewOptions {
  token: string;
  reason?: string;
  signal?: AbortSignal;
}

export const ADMIN_PREVIEW_ROUTES = Object.freeze({
  create: '/admin/master-data/create-preview',
  edit: '/admin/master-data/edit-preview',
  rollback: '/admin/change-logs/{changeLogId}/rollback-preview',
  createDelete: '/admin/change-logs/{changeLogId}/create-delete-preview',
  createDeleteRestore: '/admin/change-logs/{changeLogId}/create-delete-restore-preview',
});

function changeLogRoute(template: string, changeLogId: number) {
  return template.replace('{changeLogId}', encodeURIComponent(String(changeLogId)));
}

function previewBody(reason?: string): JsonRecord {
  return { reason: reason?.trim() || undefined, dryRun: true };
}

export const adminPreviewApi = {
  previewCreate(options: PreviewOptions & { domain: string; draft: JsonRecord }) {
    return requestApi<AdminPreviewPayload>(ADMIN_PREVIEW_ROUTES.create, {
      method: 'POST',
      token: options.token,
      signal: options.signal,
      body: {
        domain: options.domain.trim(),
        draft: options.draft,
        ...previewBody(options.reason),
      },
    });
  },

  previewEdit(options: PreviewOptions & { domain: string; rowId: number; draft: JsonRecord; baseValues: JsonRecord }) {
    return requestApi<AdminPreviewPayload>(ADMIN_PREVIEW_ROUTES.edit, {
      method: 'POST',
      token: options.token,
      signal: options.signal,
      body: {
        domain: options.domain.trim(),
        id: options.rowId,
        draft: options.draft,
        baseValues: options.baseValues,
        ...previewBody(options.reason),
      },
    });
  },

  previewRollback(options: PreviewOptions & { changeLogId: number }) {
    return requestApi<AdminPreviewPayload>(changeLogRoute(ADMIN_PREVIEW_ROUTES.rollback, options.changeLogId), {
      method: 'POST',
      token: options.token,
      signal: options.signal,
      body: previewBody(options.reason),
    });
  },

  previewCreateDelete(options: PreviewOptions & { changeLogId: number }) {
    return requestApi<AdminPreviewPayload>(changeLogRoute(ADMIN_PREVIEW_ROUTES.createDelete, options.changeLogId), {
      method: 'POST',
      token: options.token,
      signal: options.signal,
      body: previewBody(options.reason),
    });
  },

  previewCreateDeleteRestore(options: PreviewOptions & { changeLogId: number }) {
    return requestApi<AdminPreviewPayload>(changeLogRoute(ADMIN_PREVIEW_ROUTES.createDeleteRestore, options.changeLogId), {
      method: 'POST',
      token: options.token,
      signal: options.signal,
      body: previewBody(options.reason),
    });
  },
};
