# Luồng End-to-End mượt: Video → AI Engine → Backend → Dashboard

**Ngày**: 2026-04-13
**Nhánh**: `main` (merge từ `feat/ai-engine-pipeline`)
**Mục tiêu**: Cho 1 video đầu vào → hệ thống tự detect, OCR, gửi event, hiển thị trên dashboard — chạy mượt, không cần can thiệp thủ công.

---

## Trạng thái hiện tại

| Component | Main branch | Cần làm |
|-----------|-------------|---------|
| AI Engine | Placeholder (41 dòng) | Merge pipeline thật từ `feat/ai-engine-pipeline` |
| Backend | ✅ Hoạt động (18 endpoints, 56 tests) | Chạy trên SQLite để test nhanh |
| Dashboard | ✅ Hoạt động (React + Vite) | Đang connect `:8000` |
| Liên kết AI→Backend | event_sender.py có nhưng chưa merge | Merge + test |
| Liên kết Backend→Dashboard | ✅ API đã nối | Verify hiển thị events |

---

## Phase 1 — Merge AI Engine vào main

- [ ] 1.1 Merge `feat/ai-engine-pipeline` → `main`
- [ ] 1.2 Verify compile: tất cả Python files không có syntax error
- [ ] 1.3 Verify backend tests vẫn pass (56/56)
- [ ] 1.4 Push main

---

## Phase 2 — Backend chạy local (SQLite mode)

> Mục tiêu: backend chạy trên :8000 không cần Postgres

- [ ] 2.1 Start backend với SQLite
  ```
  APP_DATABASE_URL=sqlite+pysqlite:///./test_e2e.db \
  PYTHONPATH=apps/backend \
  python -m uvicorn app.main:app --port 8000
  ```
- [ ] 2.2 Verify health: `curl http://localhost:8000/health`
- [ ] 2.3 Verify POST event thủ công thành công

---

## Phase 3 — AI Engine chạy + gửi events về backend

> Mục tiêu: chạy pipeline trên video → events xuất hiện trong backend DB

- [ ] 3.1 Tạo script `scripts/run-e2e-demo.py`:
  - Nhận đầu vào: video path + camera_id
  - Chạy pipeline (max_frames tuỳ chọn)
  - Mỗi khi detect plate mới (chưa gửi) → send_event về backend
  - In log: plate detected, event sent, backend response
  - **Deduplicate**: không gửi lại cùng biển số cùng track

- [ ] 3.2 Chạy demo script trên `trungdinh22-demo.mp4`
  ```
  python scripts/run-e2e-demo.py \
    --video data/test-videos/trungdinh22-demo.mp4 \
    --camera cam_gate_1 \
    --backend http://localhost:8000 \
    --max-frames 60
  ```
- [ ] 3.3 Verify qua API:
  - GET /api/v1/events → events xuất hiện
  - GET /api/v1/accounts → accounts tự tạo
  - GET /api/v1/stats/realtime → stats cập nhật

---

## Phase 4 — Dashboard hiển thị dữ liệu

> Mục tiêu: mở browser, thấy events + accounts + stats từ video vừa chạy

- [ ] 4.1 Start dashboard: `cd apps/dashboard && npm run dev`
- [ ] 4.2 Mở http://localhost:5173
- [ ] 4.3 Verify hiển thị:
  - [ ] Events list: biển số, loại xe, thời gian, confidence
  - [ ] Accounts: biển số unique, balance, registration status
  - [ ] Realtime stats: tổng events, xe vào/ra
  - [ ] Barrier actions: open/hold decisions
- [ ] 4.4 Nếu dashboard không render đúng → fix

---

## Phase 5 — Chạy luồng liên tục (live demo)

> Mục tiêu: chạy cả 3 components đồng thời, feed video → dashboard cập nhật realtime

- [ ] 5.1 Terminal 1: Backend
  ```
  APP_DATABASE_URL=sqlite+pysqlite:///./demo.db \
  PYTHONPATH=apps/backend python -m uvicorn app.main:app --port 8000
  ```
- [ ] 5.2 Terminal 2: Dashboard
  ```
  cd apps/dashboard && npm run dev
  ```
- [ ] 5.3 Terminal 3: AI Engine
  ```
  python scripts/run-e2e-demo.py \
    --video data/test-videos/trungdinh22-demo.mp4 \
    --camera cam_gate_1
  ```
- [ ] 5.4 Quan sát dashboard: events xuất hiện dần khi video xử lý
- [ ] 5.5 Ghi nhận: tổng events, biển số unique, thời gian xử lý, lỗi nếu có

---

## Thứ tự thực hiện

```
Phase 1 (merge, 2 phút) → Phase 2 (backend, 3 phút) → Phase 3 (AI script, 10 phút)
                                                                    ↓
                                    Phase 4 (dashboard verify, 5 phút) → Phase 5 (live demo)
```

**Ước tính tổng**: ~25 phút nếu không gặp lỗi.

---

## File cần tạo mới

| File | Mục đích |
|------|---------|
| `scripts/run-e2e-demo.py` | Script demo chạy luồng AI → Backend |

## Rủi ro & mitigation

| Rủi ro | Xử lý |
|--------|-------|
| Backend SQLite migration fail | Dùng `create_all()` thay vì migration files |
| Model chưa download trên main | Models đã có trong `models/`, `.gitignore` chặn commit |
| Dashboard build fail | `npm install` + `npm run dev` |
| Pipeline chậm trên CPU | Giới hạn `max_frames=60` cho demo |
| Duplicate events (cùng plate nhiều frame) | Deduplicate trong demo script |
