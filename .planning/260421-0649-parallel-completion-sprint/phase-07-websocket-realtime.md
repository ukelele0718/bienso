# Phase 07: WebSocket Realtime Push

**Ưu tiên**: 🟠 Feature (có thể skip nếu thiếu thời gian)
**Branch**: `feat/websocket-realtime`
**Worktree**: WT-B2 (sau Phase 05 merge)
**Phụ thuộc**: Phase 05 (Dashboard ổn định)
**Ước tính**: 3-4 giờ

---

## Bối cảnh

Hiện tại dashboard dùng **polling** (fetch API định kỳ) → độ trễ cao, tốn request.
Mục 9.4 báo cáo đề xuất: "WebSocket push events thay vì polling".

---

## Thiết kế

### Backend: FastAPI WebSocket endpoint

```python
# apps/backend/app/main.py
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

active_connections: set[WebSocket] = set()

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_event(event_data: dict):
    for conn in list(active_connections):
        try:
            await conn.send_json(event_data)
        except:
            active_connections.discard(conn)
```

Trong `create_event()` sau khi commit:
```python
# after db.commit()
asyncio.create_task(broadcast_event({
    "type": "new_event",
    "plate": plate_text,
    "direction": direction,
    "timestamp": str(timestamp),
    "snapshot_url": ...,
}))
```

### Frontend: WebSocket hook

```typescript
// apps/dashboard/src/useEventsWs.ts
export function useEventsWs(onEvent: (event: EventOut) => void) {
  useEffect(() => {
    const ws = new WebSocket(`ws://${location.host.replace(':5173', ':8000')}/ws/events`);
    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      if (data.type === 'new_event') onEvent(data);
    };
    ws.onclose = () => {
      // reconnect after 3s
      setTimeout(() => {/* reinit */}, 3000);
    };
    return () => ws.close();
  }, []);
}
```

Trong `main.tsx`:
```tsx
useEventsWs((event) => {
  setEvents(prev => [event, ...prev].slice(0, 8));
  // update stats
});
```

---

## Yêu cầu

### 1. Backend

- Add `/ws/events` endpoint trong `main.py`
- Manage active connections (set)
- Broadcast from `create_event` sau commit
- Handle disconnect gracefully
- **Keep polling endpoints** as fallback

### 2. Frontend

- Create `useEventsWs` hook
- Auto-reconnect với exponential backoff
- Update events list + stats cards khi nhận message
- Fallback: nếu WebSocket fail → vẫn polling

### 3. Config

- Backend: không cần config mới (WebSocket cùng port 8000)
- Frontend env: `VITE_WS_URL` optional, default derive từ `VITE_API_BASE_URL`

### 4. Tests

- Backend: test WebSocket connect + receive + disconnect
- Frontend: manual test trên browser (2 tabs: 1 AI Engine, 1 dashboard)

---

## Files ownership (worktree B2)

- `apps/backend/app/main.py` (thêm WebSocket endpoint)
- `apps/backend/app/crud.py` (thêm broadcast call sau commit)
- `apps/backend/tests/test_websocket.py` (MỚI)
- `apps/dashboard/src/useEventsWs.ts` (MỚI)
- `apps/dashboard/src/main.tsx` (dùng hook)

---

## Tiêu chí thành công

- [ ] WebSocket connect thành công (dev tools Network → WS)
- [ ] Event mới hiện trên dashboard trong <500ms (vs polling ~5s)
- [ ] Disconnect + reconnect hoạt động
- [ ] Backend tests pass (thêm ≥3 test cases)
- [ ] Fallback polling vẫn OK nếu WebSocket disabled
- [ ] 2 dashboard tabs cùng lúc đều nhận event

---

## Rủi ro

- **Cao**: Async context trong SQLAlchemy có thể race condition với broadcast
- **TB**: Reconnect logic phức tạp, dễ bug
- **TB**: Mix sync + async trong FastAPI cần cẩn thận (broadcast sau sync commit)
- **Mitigation**: Giữ polling fallback; WebSocket là enhancement, không replace hoàn toàn

---

## Output

- Branch `feat/websocket-realtime`
- Demo clip: event từ AI Engine → dashboard <500ms
- Report `test_plans_and_reports/test13-websocket-realtime.md`
- Nếu bugs nặng → **không merge**, giữ branch để reference, polling vẫn đủ dùng
