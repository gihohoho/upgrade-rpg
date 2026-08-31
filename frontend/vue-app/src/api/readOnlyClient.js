import { getApiBaseUrl } from './config';

export class ReadOnlyApiError extends Error {
  constructor(message, { status, url, body } = {}) {
    super(message);
    this.name = 'ReadOnlyApiError';
    this.status = status;
    this.url = url;
    this.body = body;
  }
}

export function buildApiUrl(path, query = {}) {
  const url = new URL(`${getApiBaseUrl()}${path}`);

  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    url.searchParams.set(key, String(value));
  });

  return url.toString();
}

export async function requestReadOnly(path, { query = {}, signal, token = '' } = {}) {
  const url = buildApiUrl(path, query);
  const response = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    signal,
  });

  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    throw new ReadOnlyApiError(`GET ${path} failed with status ${response.status}`, {
      status: response.status,
      url,
      body,
    });
  }

  return body;
}
