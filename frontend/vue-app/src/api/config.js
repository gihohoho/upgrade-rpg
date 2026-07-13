export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export function getApiBaseUrl() {
  const envBaseUrl = import.meta.env?.VITE_API_BASE_URL;
  const baseUrl = envBaseUrl && envBaseUrl.trim() ? envBaseUrl.trim() : DEFAULT_API_BASE_URL;
  return baseUrl.replace(/\/+$/, '');
}
