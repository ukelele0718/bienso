import type {
  AccountOut,
  BarrierActionOut,
  EventOut,
  OcrRateOut,
  PretrainedImportIn,
  PretrainedInferIn,
  PretrainedJobOut,
  PretrainedJobsPageOut,
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

export async function fetchBarrierActions(plateText: string): Promise<BarrierActionOut[]> {
  const res = await fetch(`${BASE_URL}/api/v1/barrier-actions?plate=${encodeURIComponent(plateText)}`);
  return parseJson<BarrierActionOut[]>(res, 'Failed to fetch barrier actions');
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
