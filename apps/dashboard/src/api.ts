import type {
  AccountListResponse,
  AccountOut,
  AccountsSummaryResponse,
  BarrierActionOut,
  EventOut,
  ImportBatchesSummaryResponse,
  ImportBatchOut,
  OcrRateOut,
  RealtimeStatOut,
  TrafficStatOut,
  TransactionOut,
} from './api-types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = BASE_URL ? `${BASE_URL}${path}` : path;
  const method = init?.method ?? 'GET';
  const startedAt = performance.now();

  console.debug('[api] request', { method, url, baseUrl: BASE_URL });

  try {
    const res = await fetch(url, init);
    const elapsedMs = Math.round(performance.now() - startedAt);
    console.debug('[api] response', {
      method,
      url,
      status: res.status,
      ok: res.ok,
      elapsedMs,
    });
    return res;
  } catch (error) {
    const elapsedMs = Math.round(performance.now() - startedAt);
    console.error('[api] network_error', {
      method,
      url,
      elapsedMs,
      error,
    });
    throw new Error(`Network error while calling ${path}: ${error instanceof Error ? error.message : 'unknown_error'}`);
  }
}

async function parseJson<T>(res: Response, message: string, path: string): Promise<T> {
  if (!res.ok) {
    let responseText = '';
    try {
      responseText = await res.text();
    } catch {
      responseText = '<unreadable_response_body>';
    }

    console.error('[api] http_error', {
      path,
      status: res.status,
      statusText: res.statusText,
      responseText,
    });

    throw new Error(`${message} (${res.status} ${res.statusText}) @ ${path}`);
  }

  return (await res.json()) as T;
}

export async function fetchRealtimeStats(): Promise<RealtimeStatOut> {
  const path = '/api/v1/stats/realtime';
  const res = await apiFetch(path);
  return parseJson<RealtimeStatOut>(res, 'Failed to fetch realtime stats', path);
}

export async function fetchOcrRate(): Promise<OcrRateOut> {
  const path = '/api/v1/stats/ocr-success-rate';
  const res = await apiFetch(path);
  return parseJson<OcrRateOut>(res, 'Failed to fetch OCR success rate', path);
}

export async function fetchTraffic(groupBy: 'hour' | 'day'): Promise<TrafficStatOut[]> {
  const path = `/api/v1/stats/traffic?group_by=${groupBy}`;
  const res = await apiFetch(path);
  return parseJson<TrafficStatOut[]>(res, 'Failed to fetch traffic stats', path);
}

export async function fetchEvents(params?: {
  plate?: string;
  from_time?: string;
  to_time?: string;
  direction?: 'in' | 'out';
  vehicle_type?: 'motorbike' | 'car';
}): Promise<EventOut[]> {
  const query = new URLSearchParams();
  if (params?.plate) query.set('plate', params.plate);
  if (params?.from_time) query.set('from_time', params.from_time);
  if (params?.to_time) query.set('to_time', params.to_time);
  if (params?.direction) query.set('direction', params.direction);
  if (params?.vehicle_type) query.set('vehicle_type', params.vehicle_type);

  const suffix = query.toString() ? `?${query.toString()}` : '';
  const path = `/api/v1/events${suffix}`;
  const res = await apiFetch(path);
  return parseJson<EventOut[]>(res, 'Failed to fetch events', path);
}

export async function fetchAccount(plateText: string): Promise<AccountOut> {
  const path = `/api/v1/accounts/${encodeURIComponent(plateText)}`;
  const res = await apiFetch(path);
  return parseJson<AccountOut>(res, 'Failed to fetch account', path);
}

export async function fetchTransactions(plateText: string): Promise<TransactionOut[]> {
  const path = `/api/v1/accounts/${encodeURIComponent(plateText)}/transactions`;
  const res = await apiFetch(path);
  return parseJson<TransactionOut[]>(res, 'Failed to fetch transactions', path);
}

export async function fetchBarrierActions(plateText?: string): Promise<BarrierActionOut[]> {
  const query = plateText ? `?plate=${encodeURIComponent(plateText)}` : '';
  const path = `/api/v1/barrier-actions${query}`;
  const res = await apiFetch(path);
  return parseJson<BarrierActionOut[]>(res, 'Failed to fetch barrier actions', path);
}

// Seeded mode API functions
export async function fetchAccounts(params?: {
  plate?: string;
  registration_status?: string;
  page?: number;
  page_size?: number;
  sort_by?: 'created_at' | 'balance_vnd' | 'plate_text';
  sort_order?: 'asc' | 'desc';
}): Promise<AccountListResponse> {
  const query = new URLSearchParams();
  if (params?.plate) query.set('plate', params.plate);
  if (params?.registration_status) query.set('registration_status', params.registration_status);
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));
  if (params?.sort_by) query.set('sort_by', params.sort_by);
  if (params?.sort_order) query.set('sort_order', params.sort_order);

  const suffix = query.toString() ? `?${query.toString()}` : '';
  const path = `/api/v1/accounts${suffix}`;
  const res = await apiFetch(path);
  return parseJson<AccountListResponse>(res, 'Failed to fetch accounts', path);
}

export async function fetchAccountsSummary(): Promise<AccountsSummaryResponse> {
  const path = '/api/v1/accounts/summary';
  const res = await apiFetch(path);
  return parseJson<AccountsSummaryResponse>(res, 'Failed to fetch accounts summary', path);
}

export async function fetchImportBatches(limit = 20): Promise<ImportBatchOut[]> {
  const path = `/api/v1/import-batches?limit=${limit}`;
  const res = await apiFetch(path);
  return parseJson<ImportBatchOut[]>(res, 'Failed to fetch import batches', path);
}

export async function fetchImportBatchesSummary(): Promise<ImportBatchesSummaryResponse> {
  const path = '/api/v1/import-batches/summary';
  const res = await apiFetch(path);
  return parseJson<ImportBatchesSummaryResponse>(res, 'Failed to fetch import batches summary', path);
}

export async function verifyBarrier(plate: string, actor: string): Promise<BarrierActionOut> {
  const query = new URLSearchParams();
  query.set('plate', plate);
  query.set('actor', actor);
  const path = `/api/v1/barrier-actions/verify?${query.toString()}`;
  const res = await apiFetch(path, { method: 'POST' });
  return parseJson<BarrierActionOut>(res, 'Failed to verify barrier action', path);
}
