import React from 'react';

import type { BarrierActionOut } from '../api-types';

type Props = {
  queue: BarrierActionOut[];
  verifyingPlate: string | null;
  onRefresh: () => void;
  onVerify: (plate: string) => void;
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

const primaryButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  background: '#3b82f6',
  color: '#fff',
  border: '1px solid #3b82f6',
};

export function VerifyQueueSection({
  queue,
  verifyingPlate,
  onRefresh,
  onVerify,
  loading = false,
  error,
}: Props): React.JSX.Element {
  return (
    <section style={{ marginTop: 24 }}>
      <div style={cardStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0 }}>
            Verification Queue
            {queue.length > 0 && (
              <span
                style={{
                  marginLeft: 8,
                  background: '#fef3c7',
                  color: '#92400e',
                  padding: '2px 8px',
                  borderRadius: 12,
                  fontSize: '14px',
                  fontWeight: 600,
                }}
              >
                {queue.length}
              </span>
            )}
          </h3>
          <button type="button" onClick={onRefresh} style={buttonStyle} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Queue'}
          </button>
        </div>

        {error ? (
          <div style={{ marginBottom: 12, color: '#b91c1c', background: '#fee2e2', padding: 10, borderRadius: 8 }}>
            {error}
          </div>
        ) : null}

        {queue.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No actions pending verification</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={tableHeaderStyle}>Plate</th>
                <th style={tableHeaderStyle}>Reason</th>
                <th style={tableHeaderStyle}>Time</th>
                <th style={tableHeaderStyle}>Action</th>
              </tr>
            </thead>
            <tbody>
              {queue.map((action) => (
                <tr key={action.id} style={{ borderTop: '1px solid #e2e8f0' }}>
                  <td style={{ ...tableCellStyle, fontWeight: 600, fontFamily: 'monospace' }}>
                    {action.plate_text ?? '--'}
                  </td>
                  <td style={tableCellStyle}>
                    <span style={{ color: '#dc2626' }}>{action.barrier_reason}</span>
                  </td>
                  <td style={tableCellStyle}>{new Date(action.created_at).toLocaleString()}</td>
                  <td style={tableCellStyle}>
                    <button
                      type="button"
                      onClick={() => action.plate_text && onVerify(action.plate_text)}
                      disabled={verifyingPlate === action.plate_text || !action.plate_text}
                      style={{
                        ...primaryButtonStyle,
                        opacity: verifyingPlate === action.plate_text ? 0.5 : 1,
                      }}
                    >
                      {verifyingPlate === action.plate_text ? 'Verifying...' : 'Verify'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
