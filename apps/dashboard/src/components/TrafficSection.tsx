import { useEffect, useState } from 'react';

import { fetchTraffic } from '../api';
import type { TrafficStatOut } from '../api-types';

const cardStyle: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: 12,
  padding: 16,
  boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
};

const toggleButtonStyle = (active: boolean): React.CSSProperties => ({
  padding: '5px 14px',
  borderRadius: 6,
  border: '1px solid #cbd5f5',
  cursor: 'pointer',
  background: active ? '#3b82f6' : '#fff',
  color: active ? '#fff' : '#0f172a',
  fontWeight: active ? 600 : 400,
  fontSize: '13px',
});

const tableHeaderStyle: React.CSSProperties = {
  textAlign: 'left',
  color: '#475569',
  paddingBottom: 8,
  paddingRight: 16,
  fontWeight: 600,
  fontSize: '13px',
};

const tableCellStyle: React.CSSProperties = {
  padding: '6px 16px 6px 0',
  fontSize: '13px',
};

export function TrafficSection(): React.JSX.Element {
  const [groupBy, setGroupBy] = useState<'hour' | 'day'>('hour');
  const [traffic, setTraffic] = useState<TrafficStatOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load(by: 'hour' | 'day'): Promise<void> {
    setLoading(true);
    try {
      const data = await fetchTraffic(by);
      setTraffic(data);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load(groupBy);
  }, [groupBy]);

  const totalIn = traffic.reduce((s, r) => s + r.total_in, 0);
  const totalOut = traffic.reduce((s, r) => s + r.total_out, 0);

  return (
    <section style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ margin: 0 }}>Traffic Statistics</h3>
        <div style={{ display: 'flex', gap: 6 }}>
          <button type="button" style={toggleButtonStyle(groupBy === 'hour')} onClick={() => setGroupBy('hour')}>
            By Hour
          </button>
          <button type="button" style={toggleButtonStyle(groupBy === 'day')} onClick={() => setGroupBy('day')}>
            By Day
          </button>
        </div>
      </div>

      {error ? (
        <p style={{ color: '#991b1b' }}>Error: {error}</p>
      ) : loading ? (
        <p style={{ color: '#94a3b8' }}>Loading...</p>
      ) : traffic.length === 0 ? (
        <p style={{ color: '#94a3b8' }}>No traffic data.</p>
      ) : (
        <>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={tableHeaderStyle}>Time bucket</th>
                <th style={{ ...tableHeaderStyle, textAlign: 'right' }}>In</th>
                <th style={{ ...tableHeaderStyle, textAlign: 'right' }}>Out</th>
                <th style={{ ...tableHeaderStyle, textAlign: 'right' }}>Total</th>
              </tr>
            </thead>
            <tbody>
              {traffic.map((row) => (
                <tr key={row.bucket} style={{ borderTop: '1px solid #e2e8f0' }}>
                  <td style={tableCellStyle}>{row.bucket}</td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', color: '#166534' }}>{row.total_in}</td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', color: '#92400e' }}>{row.total_out}</td>
                  <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 600 }}>
                    {row.total_in + row.total_out}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr style={{ borderTop: '2px solid #cbd5e1' }}>
                <td style={{ ...tableCellStyle, fontWeight: 700 }}>Total</td>
                <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 700, color: '#166534' }}>{totalIn}</td>
                <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 700, color: '#92400e' }}>{totalOut}</td>
                <td style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 700 }}>{totalIn + totalOut}</td>
              </tr>
            </tfoot>
          </table>
        </>
      )}
    </section>
  );
}
