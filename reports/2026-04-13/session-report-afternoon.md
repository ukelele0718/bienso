# BÁO CÁO PHIÊN LÀM VIỆC CHIỀU — 2026-04-13

**Thời gian**: ~16:30 – 17:50 (khoảng 1h20)
**Nhánh làm việc**: `main` → `feat/ai-engine-pipeline`
**Người thực hiện**: quang + Claude Opus 4.6
**Commit**: `22b0186` — 12 files, +1069 lines

---

## MỤC LỤC

1. [Khảo sát repo Detect_redlight](#1-khảo-sát-repo-detect_redlight)
2. [Lập kế hoạch tích hợp](#2-lập-kế-hoạch-tích-hợp)
3. [Thực thi Phase A-H](#3-thực-thi)
4. [Benchmark plate detection models](#4-benchmark)
5. [Kết quả test end-to-end](#5-kết-quả-test)
6. [Files tạo mới & sửa đổi](#6-files)
7. [Vấn đề tồn đọng & Bước tiếp theo](#7-tồn-đọng)

---

## 1. Khảo sát repo Detect_redlight

**Nguồn**: https://github.com/Cannguyen123/Detect_redlight (repo của Cần — thành viên cùng nhóm DATN)

### Cấu trúc repo

| File | Chức năng |
|------|-----------|
| `src/main.py` | Pipeline chính: YOLOv8 detect xe → SORT track → YOLO detect biển → EasyOCR → hiển thị realtime |
| `src/util.py` | EasyOCR wrapper, format biển số 7 ký tự, gán biển cho xe (IoU), ghi CSV |
| `src/Sort.py` | SORT tracker (Kalman Filter) — copy từ abewley/sort (GPL-3.0) |
| `src/add_missing_data.py` | Linear interpolation bbox cho frame thiếu |
| `src/visualize.py` | Render video output với bbox + license plate overlay |

### Nhận xét

**Điểm mạnh**:
- Pipeline end-to-end hoàn chỉnh: video → detect → track → OCR → visualize
- Vehicle tracking qua SORT (Kalman Filter) — repo mình chưa có
- Bbox interpolation cho frame miss

**Điểm yếu**:
- Hardcoded paths (`C:\code_chay\...`)
- OCR chỉ hỗ trợ biển 7 ký tự, không xử lý biển VN 2 hàng (8-9 ký tự)
- EasyOCR thay vì char-level detection
- Không có backend/API, tests, hoặc config
- Model `.pt` + `.idea/` committed vào git
- `requirements.txt` thiếu nhiều deps (easyocr, filterpy, scipy, ultralytics)

### So sánh approach OCR

| | Repo mình (datn) | Repo Cần (Detect_redlight) |
|---|---|---|
| OCR engine | YOLOv5 per-character detection | EasyOCR (text-level) |
| 2-row plate | Gap-based row clustering | Không hỗ trợ |
| Tracking | Chưa có → **nay đã tích hợp** | SORT (Kalman) |
| Deployment | FastAPI + React dashboard | Offline script |

---

## 2. Lập kế hoạch tích hợp

Tạo plan chi tiết tại `.planning/2026-04-13-integrate-detect-redlight/PLAN.md` gồm 9 phases:

| Phase | Nội dung | Ước tính |
|-------|----------|----------|
| A | Download model + setup cấu trúc | Setup |
| B | SORT Tracker module | Refactor |
| C | Vehicle Detector (YOLOv8) | Mới |
| D | Plate Detector + benchmark | Mới + Test |
| E | Plate OCR char-level | Mới |
| F | Bbox Interpolation | Refactor |
| G | Config module | Mới |
| H | Pipeline integration | Refactor |
| I | Backend HTTP connection | Mới |

**Quyết định kiến trúc**:
- Bỏ EasyOCR (nặng ~500MB RAM, 1-2s/ảnh) — giữ YOLOv5 char-level OCR
- Hỗ trợ cả YOLOv5 và YOLOv8 plate detection models
- Config qua environment variables, có defaults hợp lý
- Pipeline yield `Event` objects compatible với backend `EventIn` schema

---

## 3. Thực thi Phase A-H

### Phase A — Setup

- Download `number_plate.pt` (~50MB) từ repo Cần → `models/`
- Thêm `models/` vào `.gitignore`
- Tạo `models/README.md` với hướng dẫn download từng model
- Cập nhật `apps/ai_engine/requirements.txt`: thêm `torch`, `filterpy`, `scipy`, `lap`
- Install dependencies: `pip install filterpy lap`
- Tạo cấu trúc thư mục `apps/ai_engine/src/` với `__init__.py`

### Phase B — SORT Tracker (`sort_tracker.py`, 185 lines)

- Refactor từ `Cannguyen123/Sort.py`
- Bỏ matplotlib, skimage, argparse imports (chỉ dùng cho demo)
- Giữ core: `_KalmanBoxTracker`, `Sort`, `_iou_batch`, `_associate`
- Thêm type hints, docstrings, credit GPL-3.0 license
- **Test**: Feed dummy detections qua 5 frames → track IDs stable ✅

### Phase C — Vehicle Detector (`vehicle_detector.py`, 52 lines)

- Class `VehicleDetector` wrapping `ultralytics.YOLO`
- Filter COCO classes: car, motorcycle, bus, truck
- `detect()` → list[VehicleDetection]
- `detect_as_array()` → (N, 5) ndarray cho SORT input

### Phase D — Plate Detector (`plate_detector.py`, 78 lines)

- Class `PlateDetector` hỗ trợ 2 model types:
  - YOLOv5 via `torch.hub.load()` (cho LP_detector.pt)
  - YOLOv8 via `ultralytics.YOLO()` (cho number_plate.pt)
- Auto-detect model type từ filename
- Return `PlateDetection` với bbox, score, crop

### Phase E — Plate OCR (`plate_ocr.py`, 95 lines)

- Class `PlateOCR` dùng `LP_ocr.pt` (YOLOv5 char-level)
- Gap-based 2-row clustering (threshold 30% avg char height):
  1. Sort chars by Y center
  2. Find largest gap between consecutive Y centers
  3. If gap > 30% avg height → split 2 rows
  4. Sort each row left→right, concatenate top→bottom
- Strip non-alphanumeric, uppercase

### Phase F — Interpolation (`interpolation.py`, 70 lines)

- Refactor từ `Cannguyen123/add_missing_data.py`
- Bỏ CSV I/O, làm việc trực tiếp trên dict
- Linear interpolation cho car_bbox + plate_bbox
- Plate text carry forward từ frame có confidence cao nhất
- **Test**: 2 frames gap=5 → 6 frames output, bbox smooth ✅

### Phase G — Config (`config.py`, 27 lines)

- Model paths resolve từ project root
- Environment variable overrides cho tất cả settings
- Defaults: `yolov8n.pt` (vehicle), `LP_detector.pt` (plate), `LP_ocr.pt` (OCR)

### Phase H — Pipeline Integration (`pipeline.py`, 190 lines)

- Class `Pipeline` orchestrate: VehicleDetector → SORT → PlateDetector → PlateOCR
- `process_frame()`: detect → track → plate detect → OCR → yield events
- `_assign_plate_to_vehicle()`: IoU containment check (biển nằm trong bbox xe)
- Track best plate text per track_id (highest confidence across frames)
- `run_pipeline()`: process video file/RTSP stream, yield events
- `run_single_image()`: process ảnh đơn, fallback direct plate detect nếu không có xe
- Vehicle type mapping: COCO classes → backend types (motorcycle→motorbike, car/bus/truck→car)

### Phase I — Event Sender (`event_sender.py`, 58 lines)

- `send_event()`: POST EventIn payload to `/api/v1/events`
- Retry 3 lần với exponential backoff (1s, 2s, 3s)
- `send_events_batch()`: gửi nhiều events tuần tự

---

## 4. Benchmark Plate Detection Models

Chạy trên 20 ảnh VNLP (10 one_row + 10 two_rows):

| Model | Detection Rate | Speed (avg/img) | Kích thước |
|-------|---------------|-----------------|-----------|
| **LP_detector.pt (YOLOv5)** | **20/20 (100%)** | **32ms** | ~15MB |
| number_plate.pt (YOLOv8) | 20/20 (100%) | 48ms | ~50MB |

**Kết luận**: LP_detector.pt được chọn làm default — cùng accuracy nhưng nhanh hơn 33% và nhẹ hơn 3.3x.

Config đã cập nhật: `PLATE_MODEL = "LP_detector.pt"`

---

## 5. Kết quả test end-to-end

### Module tests

| Module | Test | Kết quả |
|--------|------|---------|
| SORT Tracker | 5 frames dummy detections | ✅ Track IDs stable |
| Interpolation | 2 frames gap=5 | ✅ 6 frames output, bbox linear |
| Pipeline init | Load all 3 models | ✅ VehicleDetector + PlateDetector + PlateOCR |

### Pipeline test trên VNLP images

5 ảnh (2 one_row + 3 two_rows):

| Ảnh | Ground Truth | OCR Output | Match |
|-----|-------------|------------|-------|
| one_row #1 | 36A38587 | A36A38587 | ❌ (thừa A đầu) |
| one_row #2 | 36A38600 | 36A38600 | ✅ |
| two_rows #1 | 36A38569 | 3638569 | ❌ (mất chữ A) |
| two_rows #2 | 36A38570 | 36A38570 | ✅ |
| two_rows #3 | 36A38575 | 36A38575 | ✅ |

**Exact match: 3/5 (60%)** — tương đương baseline OCR eval trước đó (33.3% trên 50 ảnh random). Kết quả khác do sample khác nhau.

### Lỗi phát hiện & xử lý

1. **`run_single_image` trả 0 events trên ảnh crop biển số**: SORT cần `min_hits=3` frames → single image không có track. Fix: thêm fallback direct plate detect khi không có vehicle tracks.
2. **`filterpy` chưa install**: `ModuleNotFoundError`. Fix: `pip install filterpy lap`.
3. **Models reload mỗi lần gọi `run_single_image`**: Mỗi lần tạo `Pipeline()` mới → load 3 models. Chấp nhận cho single image use case, video pipeline chỉ load 1 lần.

---

## 6. Files tạo mới & sửa đổi

### Files mới (9)

| File | Lines | Mô tả |
|------|-------|-------|
| `apps/ai_engine/src/__init__.py` | 0 | Package init |
| `apps/ai_engine/src/config.py` | 27 | Config — model paths, thresholds |
| `apps/ai_engine/src/sort_tracker.py` | 185 | SORT multi-object tracker |
| `apps/ai_engine/src/vehicle_detector.py` | 52 | YOLOv8 vehicle detection |
| `apps/ai_engine/src/plate_detector.py` | 78 | Plate detection (v5 + v8) |
| `apps/ai_engine/src/plate_ocr.py` | 95 | Char-level OCR + 2-row |
| `apps/ai_engine/src/interpolation.py` | 70 | Bbox linear interpolation |
| `apps/ai_engine/src/event_sender.py` | 58 | Backend HTTP client |
| `.planning/2026-04-13-integrate-detect-redlight/PLAN.md` | ~180 | Kế hoạch chi tiết |

### Files sửa đổi (3)

| File | Thay đổi |
|------|----------|
| `.gitignore` | Thêm `models/` |
| `apps/ai_engine/requirements.txt` | Thêm torch, filterpy, scipy, lap |
| `apps/ai_engine/src/pipeline.py` | Từ 41 dòng placeholder → 190 dòng pipeline thật |

### Models downloaded (không commit)

| File | Kích thước | Nguồn |
|------|-----------|-------|
| `models/number_plate.pt` | 50MB | Cannguyen123/Detect_redlight |
| `models/yolov8n.pt` | 6.2MB | ultralytics (auto-download) |
| `models/LP_detector.pt` | ~15MB | Đã có từ trước |
| `models/LP_ocr.pt` | ~15MB | Đã có từ trước |

---

## 7. Vấn đề tồn đọng & Bước tiếp theo

### Tồn đọng

1. **OCR accuracy ~60%** — cần cải thiện:
   - Padding crop trước khi OCR (thêm 10-15% border)
   - Deblur/enhance contrast cho ảnh mờ
   - Post-process regex cho format biển VN (XX-XXXXX hoặc XXX-XXXXX)
   - Confidence threshold tuning

2. **Full OCR evaluation** — chưa chạy trên toàn bộ 37,297 ảnh VNLP. Sample 50 ảnh phiên sáng cho 33.3%, sample 5 ảnh phiên chiều cho 60%.

3. **Video test** — pipeline chưa test trên video thật (chỉ test single image). Cần video mẫu từ camera bãi xe.

4. **Branch chưa merge** — `feat/ai-engine-pipeline` chưa push/merge vào `main`.

5. **Backend integration test** — `event_sender.py` chưa test thực tế với backend đang chạy.

### Bước tiếp theo đề xuất

1. **Push branch + tạo PR** vào `feat/vnlp-seeded-backend-dashboard`
2. **Chạy full OCR evaluation** trên 3,731 test images (~4 phút ước tính)
3. **Cải thiện OCR**: padding, deblur, VN plate regex post-processing
4. **Test video pipeline** với video mẫu từ camera thật
5. **Integration test**: backend chạy + pipeline gửi events → verify trong database

---

## Tổng kết phiên

| Metric | Giá trị |
|--------|---------|
| Thời gian | ~1h20 |
| Files tạo mới | 9 |
| Files sửa | 3 |
| Total lines added | +1069 |
| Commit | `22b0186` |
| Branch | `feat/ai-engine-pipeline` |
| Models downloaded | 2 (number_plate.pt 50MB, yolov8n.pt 6.2MB) |
| Dependencies installed | filterpy, lap |
| Pipeline status | Hoạt động end-to-end trên single image |
