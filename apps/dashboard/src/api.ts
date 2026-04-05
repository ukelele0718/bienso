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

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function parseJson<T>(res: Response, message: string): Promise<T> {
  if (!res.ok) {
    throw new Error(message);
  }
  return (await res.json()) as T;
}

export async function fetchRealtimeStats(): Promise<RealtimeStatOut> {
  const res = await fetch(`${BASE_URL}/api/v1/stats/realtime`);
  return parseJson<RealtimeStatOut>(res, 'Failed to fetch realtime stats');
}

export async function fetchOcrRate(): Promise<OcrRateOut> {
  const res = await fetch(`${BASE_URL}/api/v1/stats/ocr-success-rate`);
  return parseJson<OcrRateOut>(res, 'Failed to fetch OCR success rate');
}

export async function fetchTraffic(groupBy: 'hour' | 'day'): Promise<TrafficStatOut[]> {
  const res = await fetch(`${BASE_URL}/api/v1/stats/traffic?group_by=${groupBy}`);
  return parseJson<TrafficStatOut[]>(res, 'Failed to fetch traffic stats');
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
  const res = await fetch(`${BASE_URL}/api/v1/events${suffix}`);
  return parseJson<EventOut[]>(res, 'Failed to fetch events');
}

export async function fetchAccount(plateText: string): Promise<AccountOut> {
  const res = await fetch(`${BASE_URL}/api/v1/accounts/${encodeURIComponent(plateText)}`);
  return parseJson<AccountOut>(res, 'Failed to fetch account');
}

export async function fetchTransactions(plateText: string): Promise<TransactionOut[]> {
  const res = await fetch(
    `${BASE_URL}/api/v1/accounts/${encodeURIComponent(plateText)}/transactions`
  );
  return parseJson<TransactionOut[]>(res, 'Failed to fetch transactions');
}

export async function fetchBarrierActions(plateText?: string): Promise<BarrierActionOut[]> {
  const query = plateText ? `?plate=${encodeURIComponent(plateText)}` : '';
  const res = await fetch(`${BASE_URL}/api/v1/barrier-actions${query}`);
  return parseJson<BarrierActionOut[]>(res, 'Failed to fetch barrier actions');
}

// Seeded mode API functions
export async function fetchAccounts(params?: {
  plate?: string;
  registration_status?: string;
  page?: number;
  page_size?: number;
}): Promise<AccountListResponse> {
  const query = new URLSearchParams();
  if (params?.plate) query.set('plate', params.plate);
  if (params?.registration_status) query.set('registration_status', params.registration_status);
  if (params?.page) query.set('page', String(params.page));
  if (params?.page_size) query.set('page_size', String(params.page_size));

  const suffix = query.toString() ? `?${query.toString()}` : '';
  const res = await fetch(`${BASE_URL}/api/v1/accounts${suffix}`);
  return parseJson<AccountListResponse>(res, 'Failed to fetch accounts');
}

export async function fetchAccountsSummary(): Promise<AccountsSummaryResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/accounts/summary`);
  return parseJson<AccountsSummaryResponse>(res, 'Failed to fetch accounts summary');
}

export async function fetchImportBatches(limit = 20): Promise<ImportBatchOut[]> {
  const res = await fetch(`${BASE_URL}/api/v1/import-batches?limit=${limit}`);
  return parseJson<ImportBatchOut[]>(res, 'Failed to fetch import batches');
}

export async function fetchImportBatchesSummary(): Promise<ImportBatchesSummaryResponse> {
  const res = await fetch(`${BASE_URL}/api/v1/import-batches/summary`);
  return parseJson<ImportBatchesSummaryResponse>(res, 'Failed to fetch import batches summary');
}

export async function verifyBarrier(plate: string, actor: string): Promise<BarrierActionOut> {
  const query = new URLSearchParams();
  query.set('plate', plate);
  query.set('actor', actor);
  const res = await fetch(`${BASE_URL}/api/v1/barrier-actions/verify?${query.toString()}`, {
    method: 'POST',
  });
  return parseJson<BarrierActionOut>(res, 'Failed to verify barrier action');
}
