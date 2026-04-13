# Tích hợp Detect_redlight vào AI Engine

**Ngày tạo**: 2026-04-13
**Cập nhật**: 2026-04-13 — Phase A-H hoàn thành, pipeline hoạt động end-to-end.
**Nguồn tham khảo**: https://github.com/Cannguyen123/Detect_redlight
**Mục tiêu**: Biến `apps/ai_engine/` từ placeholder thành pipeline thật — detect xe, tracking, detect biển số, OCR, gửi event về backend.
**Trạng thái**: Phase A-H ✅ hoàn thành | Phase I (backend connection) chưa làm

---

## Tổng quan kiến trúc

```
Video/Image Input
    │
    ├─► [vehicle_detector.py]  YOLOv8n detect xe (car, motorbike, bus, truck)
    │
    ├─► [sort_tracker.py]      SORT tracker gán ID theo frame
    │
    ├─► [plate_detector.py]    YOLO custom detect vùng biển số
    │
    ├─► [plate_ocr.py]         YOLOv5 char-level OCR (có sẵn LP_ocr.pt)
    │                          + gap-based 2-row clustering
    │
    ├─► [interpolation.py]     Linear interpolation bbox cho frame miss
    │
    ├─► [pipeline.py]          Orchestrate toàn bộ flow, yield Event objects
    │
    └─► POST /api/v1/events    Gửi EventIn payload về backend
```

## Models cần có

| Model | Nguồn | Đường dẫn |
|-------|-------|-----------|
| `yolov8n.pt` | Public ultralytics (auto-download) | Cache mặc định |
| `number_plate.pt` | Repo Cần (committed trong git) | `models/number_plate.pt` |
| `LP_detector.pt` | Đã có trong project | `models/LP_detector.pt` |
| `LP_ocr.pt` | Đã có trong project | `models/LP_ocr.pt` |

**Lưu ý**: `LP_detector.pt` (YOLOv5) vs `number_plate.pt` (YOLOv8) — cần benchmark chọn 1 hoặc giữ cả 2 tùy kết quả.

---

## Phase A — Download model + Setup cấu trúc

**Branch**: `feat/ai-engine-pipeline`

- [ ] A.1 Download `number_plate.pt` từ repo Cần → `models/number_plate.pt`
- [ ] A.2 Đảm bảo `models/` nằm trong `.gitignore` (không commit model vào git)
- [ ] A.3 Tạo `models/README.md` — ghi rõ nguồn download từng model
- [ ] A.4 Cập nhật `apps/ai_engine/requirements.txt`:
  - `opencv-python`, `numpy`, `torch`, `ultralytics`
  - `filterpy`, `scipy` (cho SORT tracker)
  - `lap` (optional, fallback scipy)
- [ ] A.5 Tạo cấu trúc thư mục:
  ```
  apps/ai_engine/
  ├── src/
  │   ├── __init__.py
  │   ├── pipeline.py          (refactor từ placeholder)
  │   ├── vehicle_detector.py  (mới)
  │   ├── sort_tracker.py      (mới)
  │   ├── plate_detector.py    (mới)
  │   ├── plate_ocr.py         (mới)
  │   ├── interpolation.py     (mới)
  │   └── config.py            (mới — model paths, thresholds)
  └── requirements.txt
  ```

---

## Phase B — SORT Tracker

Tham khảo: `Cannguyen123/Detect_redlight/src/Sort.py` (GPL-3.0 license, credit Alex Bewley)

- [ ] B.1 Tạo `apps/ai_engine/src/sort_tracker.py`
  - Refactor class `Sort` + `KalmanBoxTracker` từ repo Cần
  - Bỏ `matplotlib`, `skimage`, `argparse` imports (chỉ cần cho demo, không cần cho pipeline)
  - Giữ: `KalmanBoxTracker`, `Sort`, `iou_batch`, `associate_detections_to_trackers`
  - Thêm type hints cơ bản
  - Thêm docstring ghi credit nguồn gốc + license
- [ ] B.2 Test thủ công: init `Sort()`, feed dummy detections qua 5 frames, verify track IDs ổn định

---

## Phase C — Vehicle Detector

Tham khảo: `Cannguyen123/Detect_redlight/src/main.py` (phần vehicle detection)

- [ ] C.1 Tạo `apps/ai_engine/src/vehicle_detector.py`
  - Class `VehicleDetector`:
    - `__init__(model_path: str, confidence: float = 0.5)`
    - `detect(frame: np.ndarray) -> list[Detection]` — return list bbox + class + score
  - Vehicle whitelist: `car`, `motorcycle`, `bus`, `truck` (filter từ COCO classes)
  - Dùng `ultralytics.YOLO` cho YOLOv8
- [ ] C.2 Test thủ công: load `yolov8n.pt`, chạy detect trên 1 frame từ video/ảnh mẫu

---

## Phase D — Plate Detector

Có 2 model cần benchmark:
- `models/LP_detector.pt` (YOLOv5, đã có) — load qua `torch.hub`
- `models/number_plate.pt` (YOLOv8, từ repo Cần) — load qua `ultralytics.YOLO`

- [ ] D.1 Tạo `apps/ai_engine/src/plate_detector.py`
  - Class `PlateDetector`:
    - `__init__(model_path: str, model_type: Literal["yolov5", "yolov8"], confidence: float = 0.5)`
    - `detect(frame: np.ndarray) -> list[PlateDetection]` — return bbox + score + crop
  - Hỗ trợ cả 2 loại model (YOLOv5 via torch.hub, YOLOv8 via ultralytics)
- [ ] D.2 Quick benchmark: chạy cả 2 model trên 20 ảnh mẫu, so sánh detection rate + speed
  - **⚠ Dừng và báo kết quả trước khi chọn model chính**
- [ ] D.3 Chọn model chính dựa trên benchmark, ghi kết quả vào plan

---

## Phase E — Plate OCR (char-level)

Dùng model hiện có: `models/LP_ocr.pt` (YOLOv5 char-level) + logic từ `scripts/eval-ocr-baseline.py`

- [ ] E.1 Tạo `apps/ai_engine/src/plate_ocr.py`
  - Class `PlateOCR`:
    - `__init__(model_path: str, confidence: float = 0.3)`
    - `read(plate_crop: np.ndarray) -> tuple[str | None, float]` — return (text, confidence)
  - Logic OCR:
    - Detect từng ký tự bằng YOLOv5
    - Gap-based row clustering cho biển VN 2 hàng (threshold 30% avg char height)
    - Sort mỗi hàng left→right, nối top→bottom
    - Return text uppercase, strip non-alphanumeric
- [ ] E.2 Test trên 10 ảnh crop biển số, verify 2-row clustering hoạt động đúng

---

## Phase F — Bbox Interpolation

Tham khảo: `Cannguyen123/Detect_redlight/src/add_missing_data.py`

- [ ] F.1 Tạo `apps/ai_engine/src/interpolation.py`
  - Function `interpolate_tracks(results: dict) -> dict`
    - Input: `{frame_id: {car_id: {car_bbox, plate_bbox, plate_text, ...}}}`
    - Output: same dict với frame bị miss được fill linear interpolation
  - Refactor: bỏ CSV I/O, làm việc trực tiếp trên dict
  - Chỉ interpolate bbox, không interpolate text (giữ text từ frame gần nhất có confidence cao nhất)
- [ ] F.2 Test: tạo data giả với 3 frame gap, verify interpolation smooth

---

## Phase G — Config module

- [ ] G.1 Tạo `apps/ai_engine/src/config.py`
  ```python
  MODELS_DIR = "models"
  VEHICLE_MODEL = "yolov8n.pt"          # auto-download
  PLATE_MODEL = "number_plate.pt"       # hoặc LP_detector.pt sau benchmark
  OCR_MODEL = "LP_ocr.pt"
  VEHICLE_CONFIDENCE = 0.5
  PLATE_CONFIDENCE = 0.5
  OCR_CONFIDENCE = 0.3
  VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]
  ```
- [ ] G.2 Đọc từ environment variables nếu có (override defaults)

---

## Phase H — Pipeline Integration

Refactor `apps/ai_engine/src/pipeline.py` từ placeholder thành pipeline thật.

- [ ] H.1 Cập nhật `pipeline.py`:
  - Import `VehicleDetector`, `Sort`, `PlateDetector`, `PlateOCR`
  - `run_pipeline(video_source: str, camera_id: str) -> Iterator[Event]`:
    1. Open video source (file path hoặc RTSP URL)
    2. Mỗi frame: detect vehicles → update tracker → detect plates → OCR
    3. Gán plate cho vehicle (IoU check, tham khảo `get_car()` từ repo Cần)
    4. Yield `Event` cho mỗi plate detection mới/updated
  - Giữ nguyên `Event` dataclass interface (compatible với backend `EventIn`)
- [ ] H.2 Thêm mode xử lý ảnh đơn (không chỉ video):
  - `run_single_image(image_path: str, camera_id: str) -> list[Event]`
- [ ] H.3 Test end-to-end: chạy pipeline trên video mẫu, verify Event objects đúng format
  - **⚠ Nếu video dài > 30s, chỉ chạy 30s đầu rồi dừng báo kết quả**

---

## Phase I — Backend Connection (optional, nếu còn thời gian)

- [ ] I.1 Tạo `apps/ai_engine/src/event_sender.py`
  - Function `send_event(event: Event, backend_url: str)` → POST `/api/v1/events`
  - Retry logic đơn giản (3 lần, backoff 1s)
- [ ] I.2 Thêm CLI entry point: `python -m apps.ai_engine.src.pipeline --video <path> --camera <id> --backend <url>`
- [ ] I.3 Test: chạy pipeline → gửi event → verify trong database qua dashboard

---

## Thứ tự thực hiện

```
A (setup) → B (tracker) → C (vehicle) → D (plate detect) → E (OCR) → F (interpolation) → G (config) → H (pipeline) → I (backend)
```

**Ước tính**: Phase A-H là core, Phase I là nice-to-have.

---

## Lưu ý quan trọng

1. **License**: SORT tracker là GPL-3.0, phải ghi credit trong file
2. **Model size**: Không commit `.pt` files vào git — dùng `.gitignore` + README hướng dẫn download
3. **Lệnh chạy lâu**: Nếu benchmark/test cần > 2 phút → dừng và thông báo trước
4. **Giữ interface**: `Event` dataclass phải compatible với `EventIn` schema của backend
5. **Không dùng EasyOCR**: Đã thống nhất bỏ qua, chỉ dùng YOLOv5 char-level
