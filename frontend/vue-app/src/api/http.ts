import { getApiBaseUrl } from './config';
import type { ApiEnvelope } from './contracts';

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'DELETE';
  body?: Record<string, unknown>;
  token?: string;
  timeoutMs?: number;
  signal?: AbortSignal;
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;
  readonly retryAfterSeconds: number | null;
  readonly body: unknown;

  constructor(
    message: string,
    options: { status?: number; code?: string; retryAfterSeconds?: number | null; body?: unknown } = {},
  ) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = options.status ?? 0;
    this.code = options.code ?? '';
    this.retryAfterSeconds = options.retryAfterSeconds ?? null;
    this.body = options.body;
  }
}

function extractErrorCode(body: unknown): string {
  if (!body || typeof body !== 'object') return '';
  const source = body as Record<string, unknown>;
  const error = source.error && typeof source.error === 'object' ? source.error as Record<string, unknown> : null;
  const detail = source.detail && typeof source.detail === 'object' && !Array.isArray(source.detail)
    ? source.detail as Record<string, unknown>
    : null;
  const payload = source.payload && typeof source.payload === 'object' ? source.payload as Record<string, unknown> : null;
  return String(error?.code ?? detail?.code ?? payload?.code ?? source.code ?? '').trim().toLowerCase();
}

function extractErrorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== 'object') return fallback;
  const source = body as Record<string, unknown>;
  const error = source.error && typeof source.error === 'object' ? source.error as Record<string, unknown> : null;
  const detail = source.detail;
  if (typeof error?.message === 'string' && error.message.trim()) return error.message;
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item && typeof item === 'object' ? String((item as Record<string, unknown>).msg ?? '') : '')
      .filter(Boolean);
    if (messages.length) return messages.join(' / ');
  }
  if (detail && typeof detail === 'object') {
    const message = (detail as Record<string, unknown>).message;
    if (typeof message === 'string' && message.trim()) return message;
  }
  return fallback;
}

function parseRetryAfter(value: string | null): number | null {
  const seconds = Math.ceil(Number(value));
  return Number.isFinite(seconds) && seconds > 0 ? Math.min(seconds, 86_400) : null;
}

export async function requestApi<TPayload, TData = Record<string, unknown>>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<ApiEnvelope<TPayload, TData>> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), options.timeoutMs ?? 8_000);
  const abortFromCaller = () => controller.abort();
  options.signal?.addEventListener('abort', abortFromCaller, { once: true });

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      method: options.method ?? 'GET',
      cache: 'no-store',
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal,
    });

    const contentType = response.headers.get('content-type') ?? '';
    const body: unknown = contentType.includes('application/json') ? await response.json() : await response.text();
    if (!response.ok) {
      throw new ApiRequestError(extractErrorMessage(body, `요청을 처리하지 못했습니다. (HTTP ${response.status})`), {
        status: response.status,
        code: extractErrorCode(body),
        retryAfterSeconds: parseRetryAfter(response.headers.get('retry-after')),
        body,
      });
    }
    if (!body || typeof body !== 'object' || (body as { ok?: boolean }).ok !== true) {
      throw new ApiRequestError('API 응답 형식이 올바르지 않습니다.', { body });
    }
    return body as ApiEnvelope<TPayload, TData>;
  } catch (error) {
    if (error instanceof ApiRequestError) throw error;
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiRequestError('서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.');
    }
    throw new ApiRequestError('서버에 연결하지 못했습니다. 로그인 정보는 유지됩니다.');
  } finally {
    window.clearTimeout(timeoutId);
    options.signal?.removeEventListener('abort', abortFromCaller);
  }
}
