import { useState } from 'react';

import { adjustBalance, fetchAccount, markRegistered } from '../api';
import type { AccountOut } from '../api-types';

interface Props {
  plateText: string;
  account: AccountOut | null;
  onRefresh: (plate: string) => Promise<void>;
}

const buttonStyle: React.CSSProperties = {
  padding: '7px 12px',
  borderRadius: 8,
  border: '1px solid #cbd5f5',
  cursor: 'pointer',
  background: '#fff',
  fontSize: '13px',
};

const primaryButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  background: '#3b82f6',
  color: '#fff',
  border: '1px solid #3b82f6',
};

const dangerButtonStyle: React.CSSProperties = {
  ...buttonStyle,
  background: '#dcfce7',
  color: '#166534',
  border: '1px solid #bbf7d0',
};

export function AccountDetailActions({ plateText, account, onRefresh }: Props): React.JSX.Element | null {
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [adjusting, setAdjusting] = useState(false);
  const [adjustAmount, setAdjustAmount] = useState('');
  const [loadingMark, setLoadingMark] = useState(false);
  const [loadingAdjust, setLoadingAdjust] = useState(false);

  if (!account) return null;

  async function handleMarkRegistered(): Promise<void> {
    setLoadingMark(true);
    setActionError(null);
    setActionMsg(null);
    try {
      await markRegistered(plateText);
      setActionMsg('Account marked as registered.');
      await onRefresh(plateText);
    } catch (e) {
      setActionError(String(e));
    } finally {
      setLoadingMark(false);
    }
  }

  async function handleAdjustBalance(): Promise<void> {
    const amount = parseInt(adjustAmount, 10);
    if (isNaN(amount)) {
      setActionError('Amount must be a valid integer (can be negative).');
      return;
    }
    setLoadingAdjust(true);
    setActionError(null);
    setActionMsg(null);
    try {
      const result = await adjustBalance(plateText, amount, 'Manual adjustment');
      setActionMsg(`Balance adjusted. New balance: ${result.new_balance_vnd.toLocaleString()} VND`);
      setAdjusting(false);
      setAdjustAmount('');
      await onRefresh(plateText);
    } catch (e) {
      setActionError(String(e));
    } finally {
      setLoadingAdjust(false);
    }
  }

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {account.registration_status === 'temporary_registered' && (
          <button
            type="button"
            onClick={() => { void handleMarkRegistered(); }}
            disabled={loadingMark}
            style={dangerButtonStyle}
          >
            {loadingMark ? 'Marking...' : 'Mark as Registered'}
          </button>
        )}
        <button
          type="button"
          onClick={() => {
            setAdjusting((prev) => !prev);
            setActionError(null);
            setActionMsg(null);
          }}
          style={buttonStyle}
        >
          Adjust Balance
        </button>
      </div>

      {adjusting && (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }}>
          <input
            type="number"
            value={adjustAmount}
            onChange={(e) => setAdjustAmount(e.target.value)}
            placeholder="Amount (e.g. -5000 or 10000)"
            style={{ padding: '6px 10px', borderRadius: 8, border: '1px solid #cbd5f5', minWidth: 200 }}
          />
          <button
            type="button"
            onClick={() => { void handleAdjustBalance(); }}
            disabled={loadingAdjust}
            style={primaryButtonStyle}
          >
            {loadingAdjust ? 'Saving...' : 'Confirm'}
          </button>
          <button
            type="button"
            onClick={() => { setAdjusting(false); setAdjustAmount(''); setActionError(null); }}
            style={buttonStyle}
          >
            Cancel
          </button>
        </div>
      )}

      {actionError && (
        <p style={{ color: '#991b1b', fontSize: '13px', margin: '6px 0 0' }}>{actionError}</p>
      )}
      {actionMsg && (
        <p style={{ color: '#166534', fontSize: '13px', margin: '6px 0 0' }}>{actionMsg}</p>
      )}
    </div>
  );
}
