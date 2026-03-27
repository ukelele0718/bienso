import type { Account, RealtimeStats, VehicleEvent } from './types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function fetchRealtimeStats(): Promise<RealtimeStats> {
  const res = await fetch(`${BASE_URL}/api/v1/stats/realtime`);
  if (!res.ok) throw new Error('Failed to fetch realtime stats');
  return (await res.json()) as RealtimeStats;
}

export async function fetchEvents(): Promise<VehicleEvent[]> {
  const res = await fetch(`${BASE_URL}/api/v1/events`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return (await res.json()) as VehicleEvent[];
}

export async function fetchAccount(plateText: string): Promise<Account> {
  const res = await fetch(`${BASE_URL}/api/v1/accounts/${encodeURIComponent(plateText)}`);
  if (!res.ok) throw new Error('Failed to fetch account');
  return (await res.json()) as Account;
}
