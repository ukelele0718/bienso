# Kế hoạch Test tổng thể dự án (End-to-End)

**Ngày**: 2026-04-13
**Mục tiêu**: Verify toàn bộ luồng từ AI Engine → Backend → Dashboard hoạt động đúng.

---

## Kiến trúc hệ thống

```
 ┌─────────────────┐
 │    AI Engine     │  Video/Image → Detect → Track → OCR → Event
 │  (pipeline.py)   │
 └────────┬────────┘
          │ POST /api/v1/events (EventIn payload)
          ▼
 ┌─────────────────┐      ┌──────────────┐
 │  Backend (8000) │ ───► │  PostgreSQL   │
 │  FastAPI + CRUD │      │  (5432)       │
 └────────┬────────┘      └──────────────┘
          │ JSON API
          ▼
 ┌─────────────────┐
 │ Dashboard (5173) │  React + TypeScript
 │  Quản lý bãi xe  │
 └─────────────────┘
```

---

## Phase 1 — Backend Unit Tests (không cần services bên ngoài)

> Database: SQLite in-memory → Không cần Postgres

- [ ] 1.1 Chạy toàn bộ test suite hiện có
  ```
  bash scripts/quick-test.sh
  ```
  **Expected**: 56/56 tests pass, mypy clean, tsc clean

- [ ] 1.2 Verify normalize_plate_text (13 tests)
- [ ] 1.3 Verify barrier_rules (8 tests)
- [ ] 1.4 Verify seeded mode (full flow)
- [ ] 1.5 Verify pretrained endpoints (19 tests)

---

## Phase 2 — Backend API Smoke (backend chạy thật)

> Cần: Backend server chạy trên :8000

- [ ] 2.1 Start backend
  ```
  bash scripts/quick-backend.sh
  ```
- [ ] 2.2 Health check
  ```
  curl http://localhost:8000/health
  ```
- [ ] 2.3 POST 1 event thủ công bằng demo payload
  ```
  curl -X POST http://localhost:8000/api/v1/events \
    -H "Content-Type: application/json" \
    -d '{"camera_id":"cam_test","timestamp":"2026-04-13T20:00:00Z",
         "direction":"in","vehicle_type":"motorbike",
         "track_id":"track_1","plate_text":"36H82613","confidence":0.9}'
  ```
- [ ] 2.4 Verify response có barrier_action (open/hold), registration_status
- [ ] 2.5 GET /api/v1/events — verify event vừa tạo xuất hiện
- [ ] 2.6 GET /api/v1/accounts — verify account tự tạo
- [ ] 2.7 GET /api/v1/stats/realtime — verify stats cập nhật
- [ ] 2.8 POST /api/v1/accounts/{plate}/mark-registered — đổi status
- [ ] 2.9 POST event OUT cho cùng plate → verify barrier_action = open (đã registered)

---

## Phase 3 — AI Engine → Backend Integration

> Cần: Backend chạy trên :8000 + Models đã download

- [ ] 3.1 Chạy pipeline trên video test (trungdinh22-demo.mp4) + gửi events về backend
  ```python
  import sys
  sys.path.insert(0, 'apps/ai_engine')
  from src.pipeline import run_pipeline
  from src.event_sender import send_event

  for event in run_pipeline('data/test-videos/trungdinh22-demo.mp4', 'cam_gate_1', max_frames=60):
      if event.plate_text:
          result = send_event(event, 'http://localhost:8000')
          print(f'{event.plate_text} → {result}')
  ```
- [ ] 3.2 Verify events xuất hiện trong GET /api/v1/events
- [ ] 3.3 Verify accounts tự tạo cho mỗi biển số unique
- [ ] 3.4 Verify barrier_actions được tạo đúng logic:
  - Biển mới → `temporary_registered` + `open` (IN)
  - Biển temporary → `hold` + `needs_verification` (OUT)
- [ ] 3.5 Verify transactions: initial balance + charges
- [ ] 3.6 Kiểm tra deduplicate: cùng 1 biển nhiều frame → chỉ tạo 1 account

---

## Phase 4 — Dashboard UI Verification

> Cần: Backend :8000 + Dashboard :5173

- [ ] 4.1 Start dashboard
  ```
  bash scripts/quick-dashboard.sh
  ```
- [ ] 4.2 Mở browser http://localhost:5173
- [ ] 4.3 Verify trang chính hiển thị:
  - [ ] Realtime stats (tổng xe vào/ra, xe đang trong bãi)
  - [ ] Events list (events từ AI Engine xuất hiện)
  - [ ] Accounts list (biển số + balance + status)
- [ ] 4.4 Verify verify queue:
  - [ ] Có barrier actions với `needs_verification = true`
  - [ ] Click verify → action được xác nhận
- [ ] 4.5 Verify account management:
  - [ ] Click account → xem transactions
  - [ ] Mark registered
  - [ ] Adjust balance
- [ ] 4.6 Verify traffic stats chart (group by hour)
- [ ] 4.7 Verify OCR success rate

---

## Phase 5 — Full Stack Docker

> Cần: Docker Desktop chạy

- [ ] 5.1 Start full stack
  ```
  docker-compose up --build
  ```
- [ ] 5.2 Wait for health checks pass (postgres → backend → mock_server)
- [ ] 5.3 Lặp lại Phase 2.2–2.9 trên Docker (port 8000)
- [ ] 5.4 Verify mock_server :8088 serve static images
- [ ] 5.5 Run CI regression test locally
  ```
  python scripts/test_seeded_flow.py --base-url http://localhost:8000
  ```

---

## Phase 6 — Edge Cases & Error Handling

- [ ] 6.1 POST event không có plate_text → verify ocr_status = "failed"
- [ ] 6.2 POST event plate_text rỗng "" → verify xử lý đúng
- [ ] 6.3 POST event confidence = 0.0 → verify vẫn tạo event
- [ ] 6.4 POST event timestamp trong quá khứ → verify chấp nhận
- [ ] 6.5 POST event với plate_text có ký tự đặc biệt "29A-123.45" → verify normalize
- [ ] 6.6 AI Engine xử lý ảnh không có xe → verify 0 events, không crash
- [ ] 6.7 AI Engine xử lý ảnh có xe nhưng không đọc được biển → verify event với plate_text=None
- [ ] 6.8 Backend không chạy → event_sender retry 3 lần rồi return None

---

## Thứ tự thực hiện

```
Phase 1 (unit tests) ──► Phase 2 (API smoke) ──► Phase 3 (AI→Backend) ──► Phase 4 (Dashboard) ──► Phase 6 (edge cases)
                                                                                                         │
                                                Phase 5 (Docker full stack) ◄────────────────────────────┘
```

**Phase 1**: Không cần gì, chạy ngay
**Phase 2-3**: Cần start backend (SQLite mode OK, không cần Postgres)
**Phase 4**: Cần backend + dashboard cùng chạy
**Phase 5**: Cần Docker Desktop
**Phase 6**: Tùy chọn, chạy lúc nào cũng được

---

## Checklist nhanh trước khi test

- [ ] Models có trong `models/`: LP_detector.pt, LP_ocr.pt, yolov8n.pt
- [ ] Video test có trong `data/test-videos/`: trungdinh22-demo.mp4
- [ ] Dependencies backend: `pip install -r apps/backend/requirements.txt`
- [ ] Dependencies AI engine: `pip install filterpy lap seaborn pandas`
- [ ] Dependencies dashboard: `cd apps/dashboard && npm install`
- [ ] Port 8000 và 5173 trống

---

## Tiêu chí pass/fail

| Phase | Pass criteria |
|-------|--------------|
| 1 | 56/56 tests, mypy + tsc clean |
| 2 | All 9 API checks return expected responses |
| 3 | ≥1 plate detected, event in DB, account auto-created, barrier logic correct |
| 4 | Dashboard renders data, verify queue works, accounts manageable |
| 5 | Docker stack healthy, regression test pass |
| 6 | No crashes on edge cases, graceful error handling |
