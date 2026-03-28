import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';

import {
  fetchAccount,
  fetchBarrierActions,
  fetchEvents,
  fetchOcrRate,
  fetchRealtimeStats,
  fetchTraffic,
  fetchTransactions,
} from './api';
import type { BarrierActionOut, EventOut, RealtimeStatOut, TrafficStatOut } from './api-types';

const cardStyle: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: 12,
  padding: 16,
  boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
};

function App() {
  const [realtime, setRealtime] = useState<RealtimeStatOut | null>(null);
  const [ocrRate, setOcrRate] = useState<number | null>(null);
  const [events, setEvents] = useState<EventOut[]>([]);
  const [traffic, setTraffic] = useState<TrafficStatOut[]>([]);
  const [plateQuery, setPlateQuery] = useState('');
  const [accountBalance, setAccountBalance] = useState<number | null>(null);
  const [transactionsCount, setTransactionsCount] = useState<number | null>(null);
  const [barrierActions, setBarrierActions] = useState<BarrierActionOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadRealtime();
  }, []);

  async function loadRealtime(): Promise<void> {
    try {
      setLoading(true);
      const [realtimeRes, eventsRes, ocrRes, trafficRes] = await Promise.all([
        fetchRealtimeStats(),
        fetchEvents(),
        fetchOcrRate(),
        fetchTraffic('hour'),
      ]);
      setRealtime(realtimeRes);
      setEvents(eventsRes.slice(0, 8));
      setOcrRate(ocrRes.success_rate);
      setTraffic(trafficRes);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(): Promise<void> {
    if (!plateQuery.trim()) return;
    try {
      setLoading(true);
      const [account, transactions, barrier] = await Promise.all([
        fetchAccount(plateQuery),
        fetchTransactions(plateQuery),
        fetchBarrierActions(plateQuery),
      ]);
      setAccountBalance(account.balance_vnd);
      setTransactionsCount(transactions.length);
      setBarrierActions(barrier);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  const trafficSummary = useMemo(() => {
    return traffic.map((bucket) => `${bucket.bucket}: ${bucket.total_in}/${bucket.total_out}`).join(' • ');
  }, [traffic]);

  return (
    <div style={{ background: '#f8fafc', minHeight: '100vh', padding: 24, fontFamily: 'Inter, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0 }}>Vehicle LPR Dashboard</h1>
          <p style={{ margin: '6px 0 0', color: '#64748b' }}>Realtime monitor & barrier decision overview</p>
        </div>
        <button
          type="button"
          onClick={loadRealtime}
          style={{ padding: '10px 16px', borderRadius: 8, border: '1px solid #cbd5f5' }}
        >
          Refresh
        </button>
      </header>

      {error ? (
        <div style={{ ...cardStyle, background: '#fee2e2', color: '#991b1b', marginBottom: 16 }}>{error}</div>
      ) : null}

      <section style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
        <div style={cardStyle}>
          <p style={{ margin: 0, color: '#64748b' }}>Total In</p>
          <h2 style={{ margin: '8px 0' }}>{realtime?.total_in ?? '--'}</h2>
        </div>
        <div style={cardStyle}>
          <p style={{ margin: 0, color: '#64748b' }}>Total Out</p>
          <h2 style={{ margin: '8px 0' }}>{realtime?.total_out ?? '--'}</h2>
        </div>
        <div style={cardStyle}>
          <p style={{ margin: 0, color: '#64748b' }}>OCR Success</p>
          <h2 style={{ margin: '8px 0' }}>{ocrRate !== null ? `${ocrRate.toFixed(1)}%` : '--'}</h2>
        </div>
        <div style={cardStyle}>
          <p style={{ margin: 0, color: '#64748b' }}>Traffic summary</p>
          <p style={{ margin: '8px 0', fontWeight: 600 }}>{trafficSummary || '--'}</p>
        </div>
      </section>

      <section style={{ marginTop: 24, display: 'grid', gap: 16, gridTemplateColumns: '2fr 1fr' }}>
        <div style={cardStyle}>
          <h3 style={{ marginTop: 0 }}>Realtime events</h3>
          {events.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No events yet</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#475569' }}>
                  <th style={{ paddingBottom: 8 }}>Time</th>
                  <th style={{ paddingBottom: 8 }}>Plate</th>
                  <th style={{ paddingBottom: 8 }}>Type</th>
                  <th style={{ paddingBottom: 8 }}>Dir</th>
                  <th style={{ paddingBottom: 8 }}>Barrier</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id}>
                    <td style={{ padding: '6px 0', color: '#0f172a' }}>
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: '6px 0' }}>{event.plate_text ?? '--'}</td>
                    <td style={{ padding: '6px 0' }}>{event.vehicle_type}</td>
                    <td style={{ padding: '6px 0' }}>{event.direction}</td>
                    <td style={{ padding: '6px 0' }}>{event.barrier_action ?? '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={cardStyle}>
          <h3 style={{ marginTop: 0 }}>Search account</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={plateQuery}
              onChange={(event) => setPlateQuery(event.target.value)}
              placeholder="Plate number"
              style={{ flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
            />
            <button
              type="button"
              onClick={handleSearch}
              disabled={loading}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
            >
              Search
            </button>
          </div>

          <div style={{ marginTop: 16 }}>
            <p style={{ margin: 0, color: '#64748b' }}>Balance</p>
            <h3 style={{ margin: '6px 0' }}>{accountBalance !== null ? `${accountBalance} VND` : '--'}</h3>
            <p style={{ margin: 0, color: '#64748b' }}>Transactions</p>
            <p style={{ margin: '6px 0', fontWeight: 600 }}>{transactionsCount ?? '--'}</p>
          </div>
        </div>
      </section>

      <section style={{ marginTop: 24, ...cardStyle }}>
        <h3 style={{ marginTop: 0 }}>Barrier decisions</h3>
        {barrierActions.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No barrier logs</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {barrierActions.map((row) => (
              <li key={row.id}>
                {row.plate_text ?? '--'} → {row.barrier_action} ({row.barrier_reason})
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
