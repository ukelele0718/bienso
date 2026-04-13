# 05 — Chạy AI Engine

AI Engine xử lý video/ảnh → phát hiện xe → tracking → detect biển số → OCR → trả Event objects.

## Yêu cầu

- Models đã download vào `models/` (xem [02-download-models.md](02-download-models.md))
- Python dependencies đã cài (xem [01-clone-va-cai-dat.md](01-clone-va-cai-dat.md))

## Chuẩn bị video test

Tải video mẫu có biển số VN:

```bash
mkdir -p data/test-videos

# Video biển số VN từ trungdinh22 (32MB GIF → convert MP4)
curl -L -o data/test-videos/trungdinh22-demo.gif \
  https://github.com/trungdinh22/License-Plate-Recognition/raw/main/result/video_1.gif

ffmpeg -y -i data/test-videos/trungdinh22-demo.gif \
  -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
  data/test-videos/trungdinh22-demo.mp4
```

Nếu không có ffmpeg, dùng video tự quay (smartphone) đặt vào `data/test-videos/`.

## Chạy trên ảnh đơn

```python
import sys
sys.path.insert(0, 'apps/ai_engine')
from src.pipeline import run_single_image

events = run_single_image('path/to/image.jpg', camera_id='cam_1')
for e in events:
    print(f'Plate: {e.plate_text}, Confidence: {e.confidence}')
```

## Chạy trên video

```python
import sys
sys.path.insert(0, 'apps/ai_engine')
from src.pipeline import run_pipeline

for event in run_pipeline('data/test-videos/trungdinh22-demo.mp4', 'cam_1', max_frames=30):
    print(f'{event.vehicle_type} | {event.plate_text} | conf={event.confidence:.2f}')
```

## Pipeline bên trong

```
Frame → VehicleDetector (YOLOv8n)
          → SORT Tracker (Kalman filter, gán ID)
            → PlateDetector (LP_detector.pt)
              → PlateOCR (LP_ocr.pt, gap-based 2-row clustering)
                → Event(camera_id, timestamp, direction, vehicle_type,
                        track_id, plate_text, confidence, snapshot_path)
```

## Cấu hình qua biến môi trường

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `AI_MODELS_DIR` | `models/` | Thư mục chứa models |
| `AI_PLATE_MODEL` | `LP_detector.pt` | Model detect biển số |
| `AI_OCR_MODEL` | `LP_ocr.pt` | Model OCR ký tự |
| `AI_VEHICLE_CONF` | `0.5` | Ngưỡng confidence phát hiện xe |
| `AI_PLATE_CONF` | `0.5` | Ngưỡng confidence detect biển số |
| `AI_OCR_CONF` | `0.3` | Ngưỡng confidence OCR |

## Hiệu năng tham khảo

| Thiết bị | FPS | Ghi chú |
|----------|-----|---------|
| GTX 1650 (GPU) | ~10-15 | Khuyến nghị |
| CPU only | ~2 | Chậm, dùng `max_frames` để giới hạn |

Tiếp → [06-chay-e2e-demo.md](06-chay-e2e-demo.md)
