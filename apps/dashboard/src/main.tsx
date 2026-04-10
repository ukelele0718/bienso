import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';

import {
  fetchAccount,
  fetchAccounts,
  fetchAccountsSummary,
  fetchBarrierActions,
  fetchEvents,
  fetchImportBatches,
  fetchImportBatchesSummary,
  fetchOcrRate,
  fetchRealtimeStats,
  fetchTraffic,
  fetchTransactions,
  verifyBarrier,
} from './api';
import type {
  AccountListItem,
  AccountsSummaryResponse,
  BarrierActionOut,
  EventOut,
  ImportBatchesSummaryResponse,
  ImportBatchOut,
  RealtimeStatOut,
  TrafficStatOut,
} from './api-types';
import { ImportSummarySection } from './components/ImportSummarySection';
import { VerifyQueueSection } from './components/VerifyQueueSection';

const cardStyle: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: 12,
  padding: 16,
  boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
};

const tableHeaderStyle: React.CSSProperties = {
  textAlign: 'left',
  color: '#475569',
  paddingBottom: 8,
};

const tableCellStyle: React.CSSProperties = {
  padding: '6px 0',
};

const inputStyle: React.CSSProperties = {
  padding: '8px 12px',
  borderRadius: 8,
  border: '1px solid #cbd5f5',
};

const buttonStyle: React.CSSProperties = {
  padding: '8px 12px',
  borderRadius: 8,
  border: '1px solid #cbd5f5',
  cursor: 'pointer',
  background: '#fff',
};

const primaryButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  background: '#3b82f6',
  color: '#fff',
  border: '1px solid #3b82f6',
};

const paginationButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  padding: '6px 10px',
  fontSize: '12px',
};

function getStatusBadge(status?: string | null): React.JSX.Element {
  const colors: Record<string, { bg: string; text: string }> = {
    registered: { bg: '#dcfce7', text: '#166534' },
    temporary_registered: { bg: '#fef3c7', text: '#92400e' },
    unknown: { bg: '#e2e8f0', text: '#475569' },
  };
  const { bg, text } = colors[status ?? 'unknown'] ?? colors.unknown;
  return (
    <span
      style={{
        background: bg,
        color: text,
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: '12px',
        fontWeight: 500,
      }}
    >
      {status ?? 'unknown'}
    </span>
  );
}

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Seeded mode state
  const [accountsSummary, setAccountsSummary] = useState<AccountsSummaryResponse | null>(null);
  const [accountsList, setAccountsList] = useState<AccountListItem[]>([]);
  const [accountsTotal, setAccountsTotal] = useState(0);
  const [accountsPage, setAccountsPage] = useState(1);
  const [accountsPageSize] = useState(10);
  const [accountsPlateFilter, setAccountsPlateFilter] = useState('');
  const [accountsStatusFilter, setAccountsStatusFilter] = useState('');
  const [verifyQueue, setVerifyQueue] = useState<BarrierActionOut[]>([]);
  const [verifyingPlate, setVerifyingPlate] = useState<string | null>(null);
  const [importBatches, setImportBatches] = useState<ImportBatchOut[]>([]);
  const [importSummary, setImportSummary] = useState<ImportBatchesSummaryResponse | null>(null);

  useEffect(() => {
    void loadRealtime();
    void loadAccountsSummary();
    void loadAccountsList();
    void loadVerifyQueue();
    void loadImportSummary();
  }, []);

  // Reload accounts list when filters or page changes
  useEffect(() => {
    void loadAccountsList();
  }, [accountsPage, accountsStatusFilter]);

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

  async function loadAccountsSummary(): Promise<void> {
    try {
      const summary = await fetchAccountsSummary();
      setAccountsSummary(summary);
    } catch (err) {
      console.error('Failed to load accounts summary:', err);
    }
  }

  const loadAccountsList = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchAccounts({
        plate: accountsPlateFilter || undefined,
        registration_status: accountsStatusFilter || undefined,
        page: accountsPage,
        page_size: accountsPageSize,
      });
      setAccountsList(response.items);
      setAccountsTotal(response.total);
    } catch (err) {
      console.error('Failed to load accounts list:', err);
    }
  }, [accountsPlateFilter, accountsStatusFilter, accountsPage, accountsPageSize]);

  async function loadVerifyQueue(): Promise<void> {
    try {
      const actions = await fetchBarrierActions();
      const pending = actions.filter((a) => a.needs_verification && !a.verified_by);
      setVerifyQueue(pending);
    } catch (err) {
      console.error('Failed to load verify queue:', err);
    }
  }

  async function loadImportSummary(): Promise<void> {
    try {
      const [summary, batches] = await Promise.all([
        fetchImportBatchesSummary(),
        fetchImportBatches(10),
      ]);
      setImportSummary(summary);
      setImportBatches(batches);
    } catch (err) {
      console.error('Failed to load import summary:', err);
    }
  }

  async function handleVerify(plate: string): Promise<void> {
    try {
      setVerifyingPlate(plate);
      await verifyBarrier(plate, 'dashboard_operator');
      await loadVerifyQueue();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify');
    } finally {
      setVerifyingPlate(null);
    }
  }

  function handleAccountsSearch(): void {
    setAccountsPage(1);
    void loadAccountsList();
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

  const trafficSummary = useMemo(() => {
    return traffic.map((bucket) => `${bucket.bucket}: ${bucket.total_in}/${bucket.total_out}`).join(' • ');
  }, [traffic]);

  const totalPages = Math.ceil(accountsTotal / accountsPageSize);

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

      <section style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
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
        <div style={{ ...cardStyle, background: '#eff6ff' }}>
          <p style={{ margin: 0, color: '#3b82f6' }}>Total Accounts</p>
          <h2 style={{ margin: '8px 0', color: '#1d4ed8' }}>{accountsSummary?.total_accounts ?? '--'}</h2>
        </div>
        <div style={{ ...cardStyle, background: '#dcfce7' }}>
          <p style={{ margin: 0, color: '#166534' }}>Registered</p>
          <h2 style={{ margin: '8px 0', color: '#166534' }}>{accountsSummary?.registered_accounts ?? '--'}</h2>
        </div>
        <div style={{ ...cardStyle, background: '#fef3c7' }}>
          <p style={{ margin: 0, color: '#92400e' }}>Temporary</p>
          <h2 style={{ margin: '8px 0', color: '#92400e' }}>{accountsSummary?.temporary_registered_accounts ?? '--'}</h2>
        </div>
      </section>

      {/* Traffic Summary Row */}
      <section style={{ marginTop: 16 }}>
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

      {/* Account List Section */}
      <section style={{ marginTop: 24 }}>
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ margin: 0 }}>Account List</h3>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                type="text"
                value={accountsPlateFilter}
                onChange={(e) => setAccountsPlateFilter(e.target.value)}
                placeholder="Search by plate..."
                style={{ ...inputStyle, minWidth: 180 }}
                onKeyDown={(e) => e.key === 'Enter' && handleAccountsSearch()}
              />
              <select
                value={accountsStatusFilter}
                onChange={(e) => {
                  setAccountsStatusFilter(e.target.value);
                  setAccountsPage(1);
                }}
                style={{ ...inputStyle, minWidth: 160 }}
                aria-label="Filter by registration status"
              >
                <option value="">All Status</option>
                <option value="registered">Registered</option>
                <option value="temporary_registered">Temporary</option>
              </select>
              <button type="button" onClick={handleAccountsSearch} style={buttonStyle}>
                Search
              </button>
            </div>
          </div>

          {accountsList.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No accounts found</p>
          ) : (
            <>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={tableHeaderStyle}>Plate</th>
                    <th style={tableHeaderStyle}>Balance (VND)</th>
                    <th style={tableHeaderStyle}>Registration Status</th>
                  </tr>
                </thead>
                <tbody>
                  {accountsList.map((account) => (
                    <tr key={account.plate_text} style={{ borderTop: '1px solid #e2e8f0' }}>
                      <td style={{ ...tableCellStyle, fontWeight: 600, fontFamily: 'monospace' }}>
                        {account.plate_text}
                      </td>
                      <td style={tableCellStyle}>
                        {account.balance_vnd.toLocaleString()}
                      </td>
                      <td style={tableCellStyle}>
                        {getStatusBadge(account.registration_status)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
                <span style={{ color: '#64748b', fontSize: '14px' }}>
                  Showing {((accountsPage - 1) * accountsPageSize) + 1} - {Math.min(accountsPage * accountsPageSize, accountsTotal)} of {accountsTotal}
                </span>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    type="button"
                    onClick={() => setAccountsPage(Math.max(1, accountsPage - 1))}
                    disabled={accountsPage <= 1}
                    style={{
                      ...paginationButtonStyle,
                      opacity: accountsPage <= 1 ? 0.5 : 1,
                      cursor: accountsPage <= 1 ? 'not-allowed' : 'pointer',
                    }}
                  >
                    Previous
                  </button>
                  <span style={{ padding: '6px 12px', fontSize: '14px' }}>
                    Page {accountsPage} of {totalPages || 1}
                  </span>
                  <button
                    type="button"
                    onClick={() => setAccountsPage(Math.min(totalPages, accountsPage + 1))}
                    disabled={accountsPage >= totalPages}
                    style={{
                      ...paginationButtonStyle,
                      opacity: accountsPage >= totalPages ? 0.5 : 1,
                      cursor: accountsPage >= totalPages ? 'not-allowed' : 'pointer',
                    }}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </section>

      <ImportSummarySection
        summary={importSummary}
        batches={importBatches}
        onRefresh={() => {
          void loadImportSummary();
        }}
      />

      <VerifyQueueSection
        queue={verifyQueue}
        verifyingPlate={verifyingPlate}
        onRefresh={() => {
          void loadVerifyQueue();
        }}
        onVerify={(plate) => {
          void handleVerify(plate);
        }}
      />
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
