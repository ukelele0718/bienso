import React from 'react';

import type { ImportBatchesSummaryResponse, ImportBatchOut } from '../api-types';

type Props = {
  summary: ImportBatchesSummaryResponse | null;
  batches: ImportBatchOut[];
  onRefresh: () => void;
  loading?: boolean;
  error?: string | null;
};

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

const buttonStyle: React.CSSProperties = {
  padding: '8px 12px',
  borderRadius: 8,
  border: '1px solid #cbd5f5',
  cursor: 'pointer',
  background: '#fff',
};

export function ImportSummarySection({ summary, batches, onRefresh, loading = false, error }: Props): React.JSX.Element {
  return (
    <section style={{ marginTop: 24 }}>
      <div style={cardStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0 }}>Import Summary</h3>
          <button type="button" onClick={onRefresh} style={buttonStyle} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Import Data'}
          </button>
        </div>

        {error ? (
          <div style={{ marginBottom: 12, color: '#b91c1c', background: '#fee2e2', padding: 10, borderRadius: 8 }}>
            {error}
          </div>
        ) : null}

        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', marginBottom: 16 }}>
          <div style={{ ...cardStyle, boxShadow: 'none', border: '1px solid #e2e8f0' }}>
            <p style={{ margin: 0, color: '#64748b' }}>Total Batches</p>
            <h4 style={{ margin: '8px 0 0' }}>{summary?.total_batches ?? '--'}</h4>
          </div>
          <div style={{ ...cardStyle, boxShadow: 'none', border: '1px solid #e2e8f0' }}>
            <p style={{ margin: 0, color: '#64748b' }}>Imported</p>
            <h4 style={{ margin: '8px 0 0' }}>{summary?.total_imported ?? '--'}</h4>
          </div>
          <div style={{ ...cardStyle, boxShadow: 'none', border: '1px solid #e2e8f0' }}>
            <p style={{ margin: 0, color: '#64748b' }}>Skipped</p>
            <h4 style={{ margin: '8px 0 0' }}>{summary?.total_skipped ?? '--'}</h4>
          </div>
          <div style={{ ...cardStyle, boxShadow: 'none', border: '1px solid #e2e8f0' }}>
            <p style={{ margin: 0, color: '#64748b' }}>Invalid</p>
            <h4 style={{ margin: '8px 0 0' }}>{summary?.total_invalid ?? '--'}</h4>
          </div>
        </div>

        {batches.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No import batches found</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={tableHeaderStyle}>Batch ID</th>
                <th style={tableHeaderStyle}>Source</th>
                <th style={tableHeaderStyle}>Seed Group</th>
                <th style={tableHeaderStyle}>Imported</th>
                <th style={tableHeaderStyle}>Skipped</th>
                <th style={tableHeaderStyle}>Invalid</th>
                <th style={tableHeaderStyle}>Created At</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((batch) => (
                <tr key={batch.id} style={{ borderTop: '1px solid #e2e8f0' }}>
                  <td style={{ ...tableCellStyle, fontFamily: 'monospace' }}>{batch.id.slice(0, 8)}...</td>
                  <td style={tableCellStyle}>{batch.source}</td>
                  <td style={tableCellStyle}>{batch.seed_group ?? '--'}</td>
                  <td style={tableCellStyle}>{batch.imported_count}</td>
                  <td style={tableCellStyle}>{batch.skipped_count}</td>
                  <td style={tableCellStyle}>{batch.invalid_count}</td>
                  <td style={tableCellStyle}>{new Date(batch.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
