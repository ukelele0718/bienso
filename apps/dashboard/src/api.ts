import type {
  AccountListResponse,
  AccountOut,
  AccountsSummaryResponse,
  BarrierActionOut,
  CameraOut,
  EventOut,
  ImportBatchesSummaryResponse,
  ImportBatchOut,
  OcrRateOut,
  PretrainedImportIn,
  PretrainedInferIn,
  PretrainedJobOut,
  PretrainedJobsPageOut,
  PretrainedJobsSummaryOut,
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

export async function markRegistered(plate: string): Promise<void> {
  const res = await fetch(
    `${BASE_URL}/api/v1/accounts/${encodeURIComponent(plate)}/mark-registered`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error('Failed to mark account as registered');
}

export async function adjustBalance(
  plate: string,
  amountVnd: number,
  reason: string
): Promise<{ new_balance_vnd: number }> {
  const res = await fetch(
    `${BASE_URL}/api/v1/accounts/${encodeURIComponent(plate)}/adjust-balance`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount_vnd: amountVnd, reason }),
    }
  );
  if (!res.ok) throw new Error('Failed to adjust balance');
  const data = (await res.json()) as { plate_text: string; balance_vnd: number };
  return { new_balance_vnd: data.balance_vnd };
}

export async function fetchCameras(): Promise<CameraOut[]> {
  const res = await fetch(`${BASE_URL}/api/v1/cameras`);
  return parseJson<CameraOut[]>(res, 'Failed to fetch cameras');
}

export async function createPretrainedInferJob(payload: PretrainedInferIn): Promise<PretrainedJobOut> {
  const res = await fetch(`${BASE_URL}/api/v1/pretrained/infer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseJson<PretrainedJobOut>(res, 'Failed to create pretrained infer job');
}

export async function createPretrainedImportJob(payload: PretrainedImportIn): Promise<PretrainedJobOut> {
  const res = await fetch(`${BASE_URL}/api/v1/pretrained/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseJson<PretrainedJobOut>(res, 'Failed to create pretrained import job');
}

export async function fetchPretrainedJobs(page = 1, pageSize = 20): Promise<PretrainedJobsPageOut> {
  const query = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  const res = await fetch(`${BASE_URL}/api/v1/pretrained/jobs?${query.toString()}`);
  return parseJson<PretrainedJobsPageOut>(res, 'Failed to fetch pretrained jobs');
}

export async function fetchPretrainedJob(jobId: string): Promise<PretrainedJobOut> {
  const res = await fetch(`${BASE_URL}/api/v1/pretrained/jobs/${encodeURIComponent(jobId)}`);
  return parseJson<PretrainedJobOut>(res, 'Failed to fetch pretrained job detail');
}

export async function fetchPretrainedJobsSummary(): Promise<PretrainedJobsSummaryOut> {
  const res = await fetch(`${BASE_URL}/api/v1/pretrained/jobs/summary`);
  return parseJson<PretrainedJobsSummaryOut>(res, 'Failed to fetch pretrained jobs summary');
}
