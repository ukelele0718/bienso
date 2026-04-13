# BÁO CÁO PHIÊN LÀM VIỆC TỐI — 2026-04-13

**Thời gian**: ~20:30 – 21:35 (khoảng 1h)
**Nhánh**: `feat/ai-engine-pipeline` → merge vào `main`
**Người thực hiện**: quang + Claude Opus 4.6
**Commits**: `31d8039`, `e842d54`

---

## MỤC LỤC

1. [Khảo sát đề tài & nhánh git](#1-khảo-sát)
2. [Tìm video test biển số VN](#2-video-test)
3. [Lập kế hoạch E2E smooth flow](#3-kế-hoạch)
4. [Thực thi: merge + backend + demo script + dashboard](#4-thực-thi)
5. [Kết quả luồng end-to-end](#5-kết-quả)
6. [Files thay đổi](#6-files)
7. [Tồn đọng & bước tiếp](#7-tồn-đọng)

---

## 1. Khảo sát đề tài & nhánh git

### Đọc tài liệu đề tài

Đọc 2 file đề xuất ĐATN:
- `bao_cao_de_xuat_de_tai_v1.md` — Báo cáo đề xuất chi tiết, bối cảnh ĐH Bách khoa HN
- `de_xuat_de_tai_he_thong_dem_xe_nhan_dang_bien_so.md` — Khung nội dung + kế hoạch 16 tuần

**Mục tiêu đề tài**: Thiết kế hệ thống đếm phương tiện, nhận dạng biển số và quản lý phương tiện ra/vào khu vực giám sát. Prototype end-to-end: Camera → AI Engine → Backend → Dashboard.

### Quét 5 nhánh git

| Nhánh | Vai trò | Trạng thái |
|-------|---------|-----------|
| `main` | Production | Stable, 56 tests |
| `feat/vnlp-seeded-backend-dashboard` | Backend seeded mode | Merged → integration |
| `feat/pretrained-lpr-import-flow` | Pretrained import API | Merged → integration |
| `feat/integration-seeded-pretrained` | Integration branch | Merged → main |
| `feat/ai-engine-pipeline` | AI Engine pipeline thật | **Merged → main phiên này** |

### Gap analysis vs đề tài

| Yêu cầu | Trạng thái |
|----------|-----------|
| Phát hiện phương tiện | ✅ YOLOv8n |
| Tracking | ✅ SORT |
| Đếm theo hướng/vùng | ❌ Chưa có |
| Phát hiện biển số | ✅ LP_detector.pt |
| OCR | ✅ LP_ocr.pt + 2-row |
| Hậu xử lý chuỗi | ⚠ Chỉ strip+uppercase |
| Backend API | ✅ 18 endpoints |
| Dashboard | ✅ React+TS |
| Ảnh minh chứng (snapshot) | ❌ Chưa có |

---

## 2. Tìm video test biển số VN

### Tìm kiếm
- Quét 10+ GitHub repos VN LPR (trungdinh22, mrzaizai2k, winter2897, Cannguyen123...)
- Tìm trên Pixabay, Pexels, Vecteezy — chủ yếu biển nước ngoài
- 2 video từ repo Cần (demo.mp4, vehicle_count_input2.mp4) — biển nước ngoài

### Tải được

| File | Nguồn | Nội dung |
|------|-------|---------|
| `trungdinh22-demo.gif` → `.mp4` | [trungdinh22/License-Plate-Recognition](https://github.com/trungdinh22/License-Plate-Recognition) | **Biển số VN**, 600x800, 10fps, 30s, 300 frames |
| `demo-redlight.mp4` | Cannguyen123/Detect_redlight | Traffic nước ngoài, 1114x720, 21s |
| `vehicle-count.mp4` | Cannguyen123/Detect_redlight | Traffic nước ngoài, 1280x720, 8s |

**GIF → MP4 conversion**: ffmpeg, 31MB GIF → 19MB MP4.

### Test pipeline trên video VN (300 frames)

| Track | Vehicle | Plate | Conf | Frames |
|-------|---------|-------|------|--------|
| track_3 | car | 36H82613 | 0.90 | 1 |
| track_5 | car | 36H82613 | 0.90 | 5 |
| track_8 | motorbike | 14K117970 | 0.86 | 11 |
| track_9 | car | 14K117970 | 0.86 | 6 |

2 biển số unique detect, FPS 2.1 (CPU mode).

---

## 3. Kế hoạch E2E smooth flow

Tạo `.planning/2026-04-13-e2e-smooth-flow/PLAN.md` — 5 phases:

1. Merge AI Engine → main
2. Backend chạy local (SQLite, không cần Postgres)
3. Script demo: video → AI → Backend
4. Dashboard verify
5. Live demo 3 terminals

---

## 4. Thực thi

### Phase 1 — Merge (fast-forward)
- `git merge feat/ai-engine-pipeline` → 14 files, +1548 lines
- Compile check: 20 files OK, 0 errors
- Backend tests: 56/56 pass (1.44s)

### Phase 2 — Backend SQLite mode

Thêm 2 thay đổi vào `apps/backend/app/main.py`:

**a) SQLite auto-create tables**
```python
@app.on_event("startup")
def _auto_create_tables():
    if "sqlite" in str(engine.url):
        Base.metadata.create_all(bind=engine)
```
Cho phép chạy demo không cần Postgres — tự tạo tables khi dùng SQLite.

**b) CORS middleware**
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```
Cho phép dashboard `:5173` gọi API backend `:8000` cross-origin.

**Verify**: Health check OK, POST event thủ công thành công:
```json
{
  "plate_text": "36H82613",
  "registration_status": "temporary_registered",
  "barrier_action": "open",
  "barrier_reason": "unknown_vehicle_auto_temporary_register"
}
```

### Phase 3 — Demo script

Tạo `scripts/run-e2e-demo.py`:
- CLI args: `--video`, `--camera`, `--backend`, `--max-frames`
- Chạy pipeline → detect plates → send_event về backend
- **Deduplicate**: track_id + plate_text → không gửi lại cùng biển cùng track
- Log mỗi detect + backend response

**Kết quả chạy 60 frames**:
```
[detect] car track=track_3 plate=36H82613     conf=0.90
[sent]   → backend OK  status=temporary_registered  barrier=open
[detect] car track=track_5 plate=36H82613     conf=0.90
[sent]   → backend OK  status=temporary_registered  barrier=open

[done] 47.2s elapsed, 6 raw events, 2 sent to backend
```

### Phase 4 — Dashboard verify

- Dashboard chạy trên `:5173`, trả HTTP 200
- Backend data verified qua API:
  - 3 events (1 thủ công + 2 từ AI)
  - 1 account: `36H82613`, balance 94,000 VND
  - Stats: 3 in, 0 out, OCR 100%

---

## 5. Kết quả luồng end-to-end

```
Video (trungdinh22-demo.mp4, biển VN)
  → AI Engine: YOLOv8 detect xe → SORT track → LP_detector detect biển → LP_ocr OCR
    → send_event: POST /api/v1/events (deduplicated)
      → Backend: tạo event + account + barrier_action + transaction
        → Dashboard: hiển thị events, accounts, stats
```

**Cách chạy demo 3 terminals**:
```bash
# T1: Backend
APP_DATABASE_URL="sqlite+pysqlite:///./demo.db" PYTHONPATH=apps/backend \
  python -m uvicorn app.main:app --port 8000

# T2: Dashboard
cd apps/dashboard && npm run dev

# T3: AI Engine
python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --camera cam_gate_1
```

---

## 6. Files thay đổi

### Commit `31d8039` — merge ai-engine-pipeline
14 files từ `feat/ai-engine-pipeline` (đã báo cáo trong session-report-afternoon.md).

### Commit `e842d54` — e2e demo infra

| File | Thay đổi |
|------|----------|
| `apps/backend/app/main.py` | +18 lines: CORS middleware + SQLite auto-create |
| `scripts/run-e2e-demo.py` | Mới, 78 lines: CLI demo script |
| `.planning/2026-04-13-e2e-smooth-flow/PLAN.md` | Mới: kế hoạch 5 phases |

---

## 7. Tồn đọng & bước tiếp

### Tồn đọng
1. **Đếm xe theo hướng (line-crossing/zone)** — yêu cầu đề tài, chưa implement
2. **Lưu snapshot ảnh minh chứng** — pipeline chưa save crop + gửi URL
3. **Hậu xử lý biển số VN** — cần regex match format XX-XXXXX / XXX-XXXXX
4. **FPS chậm (2.1 trên CPU)** — cần test trên GPU, optimize batch inference
5. **Dashboard chưa verify chi tiết** — cần screenshot + check từng component
6. **Backend tests chưa cover CORS + SQLite auto-create**
7. **Video test chỉ 1 video VN** — cần thêm video đa dạng (đêm, mưa, góc nghiêng)

### Bước tiếp đề xuất (ưu tiên)
1. Push main lên remote
2. Implement vehicle counting (line-crossing) — **yêu cầu cốt lõi của đề tài**
3. Lưu snapshot crop → backend
4. Hậu xử lý biển số VN (regex + confidence filter)
5. Full OCR evaluation trên 3,731 ảnh VNLP
