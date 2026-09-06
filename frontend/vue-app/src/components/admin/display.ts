/** Shared presentation rules for the admin catalog, detail and preview panels. */
export function formatCount(value: unknown, fallback = '-'): string {
  const count = Number(value);
  return Number.isFinite(count) ? count.toLocaleString('ko-KR') : fallback;
}

export function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '예' : '아니오';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function formatCellValue(value: unknown): string {
  const formatted = formatValue(value);
  return typeof value === 'object' && formatted.length > 80
    ? `${formatted.slice(0, 77)}...`
    : formatted;
}

export function formatJson(value: unknown): string {
  if (value === null || value === undefined) return '-';
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function formatApiError(error: unknown, abortedMessage = ''): string {
  const detail = error as { name?: string; status?: number; message?: string } | null;
  if (detail?.name === 'AbortError') return abortedMessage;
  if (detail?.status) return `HTTP ${detail.status}: ${detail.message}`;
  return detail?.message || '알 수 없는 오류가 발생했습니다.';
}
