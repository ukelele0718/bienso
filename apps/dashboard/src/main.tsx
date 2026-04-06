import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';

import {
  createPretrainedImportJob,
  createPretrainedInferJob,
  fetchAccount,
  fetchBarrierActions,
  fetchEvents,
  fetchOcrRate,
  fetchPretrainedJob,
  fetchPretrainedJobs,
  fetchRealtimeStats,
  fetchTraffic,
  fetchTransactions,
} from './api';
import type {
  BarrierActionOut,
  EventOut,
  PretrainedJobOut,
  RealtimeStatOut,
  TrafficStatOut,
} from './api-types';

const cardStyle: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: 12,
  padding: 16,
  boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
};

function App(): React.JSX.Element {
  const [realtime, setRealtime] = useState<RealtimeStatOut | null>(null);
  const [ocrRate, setOcrRate] = useState<number | null>(null);
  const [events, setEvents] = useState<EventOut[]>([]);
  const [traffic, setTraffic] = useState<TrafficStatOut[]>([]);
  const [plateQuery, setPlateQuery] = useState('');
  const [fromTime, setFromTime] = useState('');
  const [toTime, setToTime] = useState('');
  const [searchEvents, setSearchEvents] = useState<EventOut[]>([]);
  const [accountBalance, setAccountBalance] = useState<number | null>(null);
  const [transactionsCount, setTransactionsCount] = useState<number | null>(null);
  const [barrierActions, setBarrierActions] = useState<BarrierActionOut[]>([]);
  const [pretrainedJobs, setPretrainedJobs] = useState<PretrainedJobOut[]>([]);
  const [selectedPretrainedJob, setSelectedPretrainedJob] = useState<PretrainedJobOut | null>(null);
  const [showPretrainedDrawer, setShowPretrainedDrawer] = useState(false);
  const [pretrainedSource, setPretrainedSource] = useState('demo://frame-001.jpg');
  const [pretrainedModelVersion, setPretrainedModelVersion] = useState('mock-v1');
  const [pretrainedThreshold, setPretrainedThreshold] = useState('0.5');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadRealtime();
  }, []);

  async function loadRealtime(): Promise<void> {
    try {
      setLoading(true);
      const [realtimeRes, eventsRes, ocrRes, trafficRes, pretrainedRes] = await Promise.all([
        fetchRealtimeStats(),
        fetchEvents(),
        fetchOcrRate(),
        fetchTraffic('hour'),
        fetchPretrainedJobs(1, 6),
      ]);
      setRealtime(realtimeRes);
      setEvents(eventsRes.slice(0, 8));
      setOcrRate(ocrRes.success_rate);
      setTraffic(trafficRes);
      setPretrainedJobs(pretrainedRes.items);
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
      const [account, transactions, barrier, eventsRes] = await Promise.all([
        fetchAccount(plateQuery),
        fetchTransactions(plateQuery),
        fetchBarrierActions(plateQuery),
        fetchEvents({
          plate: plateQuery,
          from_time: fromTime || undefined,
          to_time: toTime || undefined,
        }),
      ]);
      setAccountBalance(account.balance_vnd);
      setTransactionsCount(transactions.length);
      setBarrierActions(barrier);
      setSearchEvents(eventsRes);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateInferJob(): Promise<void> {
    try {
      setLoading(true);
      await createPretrainedInferJob({
        model_version: pretrainedModelVersion,
        source: pretrainedSource,
        threshold: pretrainedThreshold ? Number(pretrainedThreshold) : null,
      });
      const jobs = await fetchPretrainedJobs(1, 6);
      setPretrainedJobs(jobs.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateImportJob(): Promise<void> {
    try {
      setLoading(true);
      await createPretrainedImportJob({
        model_version: pretrainedModelVersion,
        source: pretrainedSource,
        items: [
          { plate_text: '51G12345', confidence: 0.9, vehicle_type: 'motorbike' },
          { plate_text: '99X99999', confidence: 0.78, vehicle_type: 'car' },
        ],
      });
      const jobs = await fetchPretrainedJobs(1, 6);
      setPretrainedJobs(jobs.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function openPretrainedJobDetail(jobId: string): Promise<void> {
    try {
      setLoading(true);
      const row = await fetchPretrainedJob(jobId);
      setSelectedPretrainedJob(row);
      setShowPretrainedDrawer(true);
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
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <input
              value={plateQuery}
              onChange={(event) => setPlateQuery(event.target.value)}
              placeholder="Plate number"
              style={{ flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
            />
            <input
              type="datetime-local"
              value={fromTime}
              onChange={(event) => setFromTime(event.target.value)}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
            />
            <input
              type="datetime-local"
              value={toTime}
              onChange={(event) => setToTime(event.target.value)}
              style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
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
        <h3 style={{ marginTop: 0 }}>Pretrained Import (Mocked)</h3>
        <div style={{ display: 'grid', gap: 10, gridTemplateColumns: '2fr 1fr 1fr auto auto' }}>
          <input
            value={pretrainedSource}
            onChange={(event) => setPretrainedSource(event.target.value)}
            placeholder="source"
            style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
          />
          <input
            value={pretrainedModelVersion}
            onChange={(event) => setPretrainedModelVersion(event.target.value)}
            placeholder="model version"
            style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
          />
          <input
            value={pretrainedThreshold}
            onChange={(event) => setPretrainedThreshold(event.target.value)}
            placeholder="threshold"
            style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
          />
          <button
            type="button"
            onClick={handleCreateInferJob}
            disabled={loading}
            style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
          >
            Create Infer Job
          </button>
          <button
            type="button"
            onClick={handleCreateImportJob}
            disabled={loading}
            style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #cbd5f5' }}
          >
            Create Import Job
          </button>
        </div>

        <div style={{ marginTop: 12 }}>
          {pretrainedJobs.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No pretrained jobs yet</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#475569' }}>
                  <th style={{ paddingBottom: 8 }}>Job ID</th>
                  <th style={{ paddingBottom: 8 }}>Type</th>
                  <th style={{ paddingBottom: 8 }}>Status</th>
                  <th style={{ paddingBottom: 8 }}>Source</th>
                  <th style={{ paddingBottom: 8 }}>Processed</th>
                </tr>
              </thead>
              <tbody>
                {pretrainedJobs.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => void openPretrainedJobDetail(row.id)}
                    style={{ cursor: 'pointer' }}
                    title="Click to view details"
                  >
                    <td style={{ padding: '6px 0', fontFamily: 'monospace' }}>{row.id.slice(0, 8)}</td>
                    <td style={{ padding: '6px 0' }}>{row.job_type}</td>
                    <td style={{ padding: '6px 0' }}>{row.status}</td>
                    <td style={{ padding: '6px 0' }}>{row.source}</td>
                    <td style={{ padding: '6px 0' }}>
                      {row.processed_items}/{row.total_items}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      <section style={{ marginTop: 24, display: 'grid', gap: 16, gridTemplateColumns: '1fr 1fr' }}>
        <div style={cardStyle}>
          <h3 style={{ marginTop: 0 }}>Search results</h3>
          {searchEvents.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No events for search</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#475569' }}>
                  <th style={{ paddingBottom: 8 }}>Time</th>
                  <th style={{ paddingBottom: 8 }}>Plate</th>
                  <th style={{ paddingBottom: 8 }}>Dir</th>
                  <th style={{ paddingBottom: 8 }}>Barrier</th>
                </tr>
              </thead>
              <tbody>
                {searchEvents.map((event) => (
                  <tr key={event.id}>
                    <td style={{ padding: '6px 0' }}>{new Date(event.timestamp).toLocaleString()}</td>
                    <td style={{ padding: '6px 0' }}>{event.plate_text ?? '--'}</td>
                    <td style={{ padding: '6px 0' }}>{event.direction}</td>
                    <td style={{ padding: '6px 0' }}>{event.barrier_action ?? '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={cardStyle}>
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
        </div>
      </section>

      {showPretrainedDrawer && selectedPretrainedJob ? (
        <div
          style={{
            position: 'fixed',
            top: 0,
            right: 0,
            width: 420,
            height: '100vh',
            background: '#ffffff',
            boxShadow: '-12px 0 30px rgba(15, 23, 42, 0.18)',
            padding: 20,
            overflowY: 'auto',
            zIndex: 1000,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Pretrained Job Detail</h3>
            <button
              type="button"
              onClick={() => setShowPretrainedDrawer(false)}
              style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #cbd5f5' }}
            >
              Close
            </button>
          </div>

          <div style={{ marginTop: 12, fontSize: 14, lineHeight: 1.6 }}>
            <div><strong>ID:</strong> <span style={{ fontFamily: 'monospace' }}>{selectedPretrainedJob.id}</span></div>
            <div><strong>Type:</strong> {selectedPretrainedJob.job_type}</div>
            <div><strong>Status:</strong> {selectedPretrainedJob.status}</div>
            <div><strong>Source:</strong> {selectedPretrainedJob.source}</div>
            <div><strong>Model:</strong> {selectedPretrainedJob.model_version}</div>
            <div><strong>Threshold:</strong> {selectedPretrainedJob.threshold ?? '--'}</div>
            <div><strong>Processed:</strong> {selectedPretrainedJob.processed_items}/{selectedPretrainedJob.total_items}</div>
          </div>

          <h4 style={{ marginTop: 18 }}>Items</h4>
          {selectedPretrainedJob.items && selectedPretrainedJob.items.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#475569' }}>
                  <th style={{ paddingBottom: 8 }}>Plate</th>
                  <th style={{ paddingBottom: 8 }}>Conf</th>
                  <th style={{ paddingBottom: 8 }}>Type</th>
                </tr>
              </thead>
              <tbody>
                {selectedPretrainedJob.items.map((item) => (
                  <tr key={item.id}>
                    <td style={{ padding: '6px 0' }}>{item.plate_text ?? '--'}</td>
                    <td style={{ padding: '6px 0' }}>{item.confidence ?? '--'}</td>
                    <td style={{ padding: '6px 0' }}>{item.vehicle_type ?? '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: '#94a3b8' }}>No items</p>
          )}
        </div>
      ) : null}
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
