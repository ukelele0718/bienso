# Test 17 — WebSocket Realtime Push

**Date**: 2026-04-21
**Phase**: Phase 07 — WebSocket realtime push from backend to dashboard

---

## Implementation Summary

### Backend (`apps/backend/app/main.py`)

Added `ConnectionManager` class (25 lines) with:
- `connect(ws)` — accepts and registers WebSocket
- `disconnect(ws)` — removes from active set
- `broadcast(message)` — sends JSON to all active connections; removes dead ones

Added `/ws/events` WebSocket endpoint:
- Accepts connections via manager
- Loops receiving keepalive text (discards content)
- Handles `WebSocketDisconnect` gracefully

Changed `create_event` handler from `def` to `async def` to enable native `asyncio.create_task()`:
- After DB commit, broadcasts `{"type": "new_event", ...}` to all connected WS clients
- Fire-and-forget via `asyncio.create_task()` — does not block HTTP response
- Broadcast includes: `event_id`, `plate_text`, `direction`, `vehicle_type`, `timestamp`, `snapshot_url`

### Frontend (`apps/dashboard/src/useEventsWs.ts`) — new file, 71 lines

`useEventsWs(onNewEvent)` hook:
- Connects to `ws://{API_BASE}/ws/events` on mount
- Exponential backoff reconnect (1s → 2s → 4s → ... → 30s max)
- Stable callback ref pattern — reconnect closure always calls latest `onNewEvent`
- Keepalive ping every 25s to prevent idle timeout disconnects
- Cleanup on unmount: cancel reconnect, close socket

Env var: `VITE_USE_WEBSOCKET=false` disables the hook entirely (defaults to enabled).

### Frontend (`apps/dashboard/src/main.tsx`)

Wired `useEventsWs` in `App` component:
- On new event: prepend to `events` state (capped at 8), then call `loadRealtime()` to refresh stats
- Polling via `loadRealtime` is **preserved** as fallback — WebSocket is additive enhancement only

---

## Test Results

### Backend Tests

```
101 passed, 2 warnings in 3.53s
```

New tests in `apps/backend/tests/test_websocket.py` (6 tests):

| Test | Result |
|------|--------|
| `test_websocket_connect` | PASS |
| `test_websocket_multiple_clients_connect` | PASS |
| `test_websocket_reconnect_after_close` | PASS |
| `test_websocket_broadcast_on_event_create` | PASS |
| `test_websocket_broadcast_contains_all_fields` | PASS |
| `test_websocket_no_broadcast_without_subscribers` | PASS |

Total: **101 backend tests** (was 95 before this phase; +6 WebSocket).

### TypeScript Check

```
npx tsc --noEmit → no output (clean)
```

---

## Key Design Decisions

### Why async def for create_event handler?

Converting to `async def` allows `asyncio.create_task()` directly. The alternative (sync handler + `call_soon_threadsafe`) worked in production but caused test timing issues with Starlette's `TestClient`. Sync SQLAlchemy operations inside an async handler are fine for this workload (DB calls are fast; no true async DB needed for prototype).

### Why not broadcast from crud.create_event?

`crud.py` is a pure sync DB layer — injecting async concerns would violate separation of concerns and complicate testing. The HTTP handler owns the broadcast responsibility.

### Starlette TestClient + WebSocket broadcast

`TestClient.websocket_connect` runs the ASGI app in a background thread sharing the same asyncio event loop. `asyncio.create_task()` from the async HTTP handler schedules the broadcast coroutine; it executes before `ws.receive_json()` returns, making tests deterministic. No sleep or explicit synchronization needed.

---

## Known Limitations

1. **No browser verification** — code review OK, unit tests pass, but end-to-end browser test not performed (out of scope for this phase).
2. **Single broadcast type** — only `new_event` is broadcast. Barrier verify, account changes, etc. are not pushed via WS (would require additional broadcast calls in those handlers).
3. **No auth on WS endpoint** — `/ws/events` is open. Acceptable for prototype with CORS-only protection.
4. **SQLAlchemy sync in async handler** — blocks the event loop briefly per request. Acceptable for prototype; production would use async SQLAlchemy.
5. **`test_backend.db` cleanup** — tests fail if a stale DB exists from prior runs (UNIQUE constraint on camera seed). Workaround: `rm test_backend.db` before first run. This is a pre-existing conftest issue, not introduced by this phase.

---

## Migration / Feature Flag

```bash
# Disable WebSocket in dashboard (falls back to polling only)
VITE_USE_WEBSOCKET=false npm run dev

# Default (WebSocket enabled)
npm run dev
```

No backend flag needed — the `/ws/events` endpoint is always available; clients can choose not to connect.
