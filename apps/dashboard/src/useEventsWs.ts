import { useEffect, useRef } from 'react';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

export interface WsNewEvent {
  type: 'new_event';
  event_id: string;
  plate_text: string | null;
  direction: string;
  vehicle_type: string;
  timestamp: string;
  snapshot_url: string | null;
}

/**
 * Subscribe to /ws/events and call onNewEvent for each broadcasted event.
 * Reconnects with exponential backoff (max 30s) on disconnect.
 * Sends keepalive ping every 25s.
 *
 * Enable by setting VITE_USE_WEBSOCKET=true in .env (defaults to enabled).
 */
export function useEventsWs(onNewEvent: (event: WsNewEvent) => void): void {
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<number>(0);
  // Stable ref so reconnect closure always calls the latest callback
  const onNewEventRef = useRef(onNewEvent);
  onNewEventRef.current = onNewEvent;

  useEffect(() => {
    const enabled = (import.meta.env.VITE_USE_WEBSOCKET as string | undefined) !== 'false';
    if (!enabled) return;

    let cancelled = false;

    const connect = (): void => {
      if (cancelled) return;
      const wsUrl = API_BASE.replace(/^http/, 'ws') + '/ws/events';
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = (): void => {
        retryRef.current = 0;
      };

      ws.onmessage = (msg: MessageEvent<string>): void => {
        try {
          const data = JSON.parse(msg.data) as WsNewEvent;
          if (data.type === 'new_event') {
            onNewEventRef.current(data);
          }
        } catch {
          // Ignore unparseable messages
        }
      };

      ws.onclose = (): void => {
        if (cancelled) return;
        const delay = Math.min(1000 * Math.pow(2, retryRef.current), 30000);
        retryRef.current += 1;
        setTimeout(connect, delay);
      };

      ws.onerror = (): void => {
        // onclose will fire after onerror and handle reconnect
      };
    };

    connect();

    // Keepalive ping every 25s to prevent idle timeout
    const keepalive = setInterval((): void => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 25000);

    return (): void => {
      cancelled = true;
      clearInterval(keepalive);
      wsRef.current?.close();
    };
  }, []); // Empty deps: connect once on mount, stable ref handles callback updates
}
