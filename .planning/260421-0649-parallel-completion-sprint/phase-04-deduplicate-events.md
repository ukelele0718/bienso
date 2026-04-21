# Phase 04: Deduplicate Events by plate_text

**Ưu tiên**: 🟡 Fix
**Branch**: `fix/dedup-events`
**Worktree**: Main (sau Batch 1)
**Phụ thuộc**: Phase 01 (OCR ổn định)
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Known issue: Cùng biển số bị gửi nhiều event khi SORT tạo track mới (vd: biển 36H82613 có 2 events ở 2 track IDs khác nhau trong lần test 101 frames).

Demo script `scripts/run-e2e-demo.py` đã dedup bằng `(track_id, plate_text)` — KHÔNG đủ khi track_id thay đổi.

---

## Giải pháp: Time-window deduplication

Dedup bằng `plate_text` trong window 30 giây. Nếu cùng biển số xuất hiện lần 2 trong 30s → bỏ qua (không gửi event mới).

### Vị trí implement

Có 2 chỗ có thể implement:

**Option A: Client-side (AI Engine)**
- File: `scripts/run-e2e-demo.py` hoặc `apps/ai_engine/src/event_sender.py`
- Lưu dict `{plate_text: last_sent_time}` trong memory
- Khi detect plate → kiểm tra last_sent, skip nếu <30s

**Option B: Server-side (Backend)**
- File: `apps/backend/app/crud.py` — hàm `create_event()`
- Query DB: last event cho plate_text trong 30s qua
- Nếu có → skip create, return existing event

**Chọn Option B** vì:
- AI Engine có thể restart → mất state → dedup client-side bị reset
- Dashboard có thể thấy nhiều event nếu 2 AI Engine chạy cùng lúc
- DB là single source of truth

---

## Yêu cầu

### 1. Sửa crud.py

```python
def create_event(db: Session, payload: dict) -> tuple[VehicleEvent, BarrierAction | None]:
    plate_text = normalize_plate_text(payload.get("plate_text"))
    
    # Dedup: check last event for this plate within 30s window
    if plate_text:
        dedup_window = timedelta(seconds=settings.event_dedup_window_sec)
        cutoff = payload["timestamp"] - dedup_window
        recent = db.execute(
            select(VehicleEvent)
            .join(PlateRead)
            .where(PlateRead.plate_text == plate_text)
            .where(VehicleEvent.timestamp >= cutoff)
            .order_by(VehicleEvent.timestamp.desc())
        ).scalars().first()
        
        if recent:
            # Skip: return existing event + last barrier action
            return recent, None  # or fetch existing barrier
    
    # ... rest of existing logic
```

### 2. Config

File `apps/backend/app/config.py`:
```python
event_dedup_window_sec: int = 30
```

Env var: `APP_EVENT_DEDUP_WINDOW_SEC=30`

### 3. Tests

Tạo test case:
- Send event cho biển X → create thành công
- Send lại biển X trong 10s → SKIP (return existing)
- Send lại biển X sau 35s → create mới
- Send biển Y (khác biển X) → create bình thường

Add vào `apps/backend/tests/test_dedup_events.py`.

### 4. Consideration: Direction flip

Edge case: Xe vào (IN) rồi RA (OUT) trong 30s → 2 events khác direction cho cùng biển.
→ Dedup nên dựa trên `(plate_text, direction)` thay vì chỉ `plate_text`.

---

## Files ownership

- `apps/backend/app/crud.py` (sửa create_event)
- `apps/backend/app/config.py` (thêm settings)
- `apps/backend/tests/test_dedup_events.py` (MỚI)

---

## Tiêu chí thành công

- [ ] Unit tests pass (4+ cases)
- [ ] Backend tests 56/56 vẫn pass (không regress)
- [ ] E2E test trên trungdinh22-demo.mp4 (300 frames): **chỉ 1 event cho biển 36H82613** (hiện 2)
- [ ] Config flag cho phép tắt dedup (= 0 → disabled)

---

## Rủi ro

- Dedup sai có thể skip event hợp lệ → người lái thực sự vào lần 2 trong 30s mà không được record
- Solution: dedup theo `(plate, direction)` thay vì chỉ `plate`
- Mitigation: config window 30s khá ngắn, người thực không vào 2 lần trong 30s

---

## Output

- Branch `fix/dedup-events` sẵn sàng merge
- Report `test_plans_and_reports/test10-dedup-events.md`
- E2E rerun cho thấy kết quả sạch hơn
