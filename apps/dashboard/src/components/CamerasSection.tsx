import { useEffect, useState } from 'react';

import { fetchCameras } from '../api';
import type { CameraOut } from '../api-types';

const cardStyle: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: 12,
  padding: 16,
  boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
  marginTop: 24,
};

const tableHeaderStyle: React.CSSProperties = {
  textAlign: 'left',
  color: '#475569',
  paddingBottom: 8,
  paddingRight: 16,
};

const tableCellStyle: React.CSSProperties = {
  padding: '6px 16px 6px 0',
  verticalAlign: 'top',
};

export function CamerasSection(): React.JSX.Element {
  const [cameras, setCameras] = useState<CameraOut[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load(): Promise<void> {
    setLoading(true);
    try {
      const data = await fetchCameras();
      setCameras(data);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <section style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ margin: 0 }}>Cameras ({cameras.length})</h3>
        <button
          type="button"
          onClick={() => { void load(); }}
          disabled={loading}
          style={{ padding: '6px 12px', borderRadius: 8, border: '1px solid #cbd5f5', cursor: 'pointer', background: '#fff' }}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {error ? (
        <p style={{ color: '#991b1b' }}>Error: {error}</p>
      ) : cameras.length === 0 ? (
        <p style={{ color: '#94a3b8' }}>No cameras configured.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>Name</th>
              <th style={tableHeaderStyle}>Gate</th>
              <th style={tableHeaderStyle}>Location</th>
              <th style={tableHeaderStyle}>Stream</th>
              <th style={tableHeaderStyle}>Active</th>
            </tr>
          </thead>
          <tbody>
            {cameras.map((c) => (
              <tr key={c.id} style={{ borderTop: '1px solid #e2e8f0' }}>
                <td style={{ ...tableCellStyle, fontWeight: 600 }}>{c.name}</td>
                <td style={tableCellStyle}>{c.gate_type}</td>
                <td style={tableCellStyle}>{c.location ?? '—'}</td>
                <td style={tableCellStyle}>
                  {c.stream_url ? (
                    <a href={c.stream_url} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6' }}>
                      View stream
                    </a>
                  ) : (
                    '—'
                  )}
                </td>
                <td style={tableCellStyle}>
                  <span style={{ color: c.is_active ? '#166534' : '#991b1b', fontWeight: 600 }}>
                    {c.is_active ? 'Yes' : 'No'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
