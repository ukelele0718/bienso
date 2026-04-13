# 02 — Download AI Models

Models không được commit vào git (quá lớn). Cần tải thủ công vào thư mục `models/`.

## Tạo thư mục

```bash
mkdir -p models
```

## Danh sách models

| File | Kích thước | Chức năng | Nguồn |
|------|-----------|-----------|-------|
| `LP_detector.pt` | ~41MB | Detect vùng biển số (YOLOv5) | VNLP training — hỏi team |
| `LP_ocr.pt` | ~41MB | OCR từng ký tự (YOLOv5) | VNLP training — hỏi team |
| `yolov8n.pt` | ~6MB | Detect xe (YOLOv8 nano, COCO) | Tự download lần đầu chạy |
| `number_plate.pt` | ~50MB | Detect biển số (YOLOv8, backup) | GitHub Cannguyen123 |

## Download

### LP_detector.pt + LP_ocr.pt (bắt buộc)

Hai model này từ quá trình training trên dataset VNLP. Liên hệ team để lấy, hoặc copy từ máy đã có:

```bash
# Copy từ máy khác (ví dụ USB/shared folder)
cp /path/to/LP_detector.pt models/
cp /path/to/LP_ocr.pt models/
```

### number_plate.pt (tùy chọn, backup)

```bash
curl -L -o models/number_plate.pt \
  https://raw.githubusercontent.com/Cannguyen123/Detect_redlight/main/model/number_plate.pt
```

### yolov8n.pt (tự động)

Model này tự download lần đầu chạy AI Engine. Không cần tải trước.
Nếu muốn tải sẵn:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mv yolov8n.pt models/
```

## Kiểm tra

```bash
ls -lh models/
# Kết quả mong đợi:
# LP_detector.pt   ~41MB
# LP_ocr.pt        ~41MB
# number_plate.pt  ~50MB  (tùy chọn)
# yolov8n.pt       ~6MB   (tùy chọn, tự download sau)
```

**Bắt buộc phải có**: `LP_detector.pt` và `LP_ocr.pt` trước khi chạy AI Engine.

Tiếp → [03-chay-backend.md](03-chay-backend.md)
