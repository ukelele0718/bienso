# 06 — Chạy demo End-to-End

Chạy toàn bộ luồng: Video → AI Engine → Backend → Dashboard.

## Yêu cầu

- Đã hoàn thành bước 01–05
- Models đã có trong `models/`
- Video test đã có trong `data/test-videos/`

## Bước 1: Mở 3 terminals

### Terminal 1 — Backend

```bash
# Linux/Mac/Git Bash
APP_DATABASE_URL="sqlite+pysqlite:///./demo.db" \
PYTHONPATH=apps/backend \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

```powershell
# Windows PowerShell
$env:APP_DATABASE_URL = "sqlite+pysqlite:///./demo.db"
$env:PYTHONPATH = "apps/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Chờ thấy: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 — Dashboard

```bash
cd apps/dashboard
npm run dev
```

Chờ thấy: `Local: http://localhost:5173/`

### Terminal 3 — AI Engine

```bash
python scripts/run-e2e-demo.py \
  --video data/test-videos/trungdinh22-demo.mp4 \
  --camera cam_gate_1 \
  --direction in \
  --max-frames 60
```

## Bước 2: Quan sát kết quả

### Terminal 3 (AI Engine) sẽ in:

```
[demo] Video: data/test-videos/trungdinh22-demo.mp4
[demo] Camera: cam_gate_1, Direction: in
[demo] Backend: http://localhost:8000
[demo] Max frames: 60

[detect] car       track=track_3    plate=36H82613       conf=0.90
[sent]   → backend OK  status=temporary_registered  barrier=open

[done] 47.2s elapsed
[done] 6 raw events, 2 sent to backend
```

### Browser (Dashboard) http://localhost:5173 sẽ hiển thị:

- **Events**: biển số 36H82613, loại xe car, camera cam_gate_1
- **Accounts**: 1 account biển 36H82613, balance giảm dần
- **Stats**: tổng xe vào, tỉ lệ OCR

## Tham số script

```
python scripts/run-e2e-demo.py --help

  --video       Đường dẫn video file (bắt buộc)
  --camera      Camera ID gửi về backend (mặc định: cam_gate_1)
  --direction   Hướng: in hoặc out (mặc định: in)
  --backend     URL backend (mặc định: http://localhost:8000)
  --max-frames  Giới hạn số frames xử lý (mặc định: xử lý hết)
```

## Ví dụ nâng cao

### Chạy toàn bộ video (không giới hạn frames)

```bash
python scripts/run-e2e-demo.py \
  --video data/test-videos/trungdinh22-demo.mp4 \
  --camera cam_gate_1
```

### Chạy video tự quay

```bash
python scripts/run-e2e-demo.py \
  --video data/test-videos/video-tu-quay.mp4 \
  --camera cam_cong_truoc \
  --direction in
```

### Chạy xe ra (sau khi đã chạy xe vào)

```bash
python scripts/run-e2e-demo.py \
  --video data/test-videos/video-xe-ra.mp4 \
  --camera cam_cong_truoc \
  --direction out
```

## Reset dữ liệu

Xóa database SQLite để bắt đầu lại:

```bash
rm demo.db
# Restart backend → tự tạo tables mới
```

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|-----------|
| `ModuleNotFoundError: filterpy` | Chưa cài deps AI Engine | `pip install filterpy lap seaborn pandas` |
| `No module named 'app.main'` | Thiếu PYTHONPATH | Đảm bảo `PYTHONPATH=apps/backend` |
| `Cannot open video source` | Sai đường dẫn video | Kiểm tra file tồn tại |
| `Connection refused :8000` | Backend chưa chạy | Start backend trước (Terminal 1) |
| `[sent] → backend FAILED` | Backend lỗi hoặc chưa sẵn sàng | Kiểm tra Terminal 1 có lỗi không |
| Chạy rất chậm (<1 FPS) | Đang dùng CPU | Bình thường nếu không có GPU. Dùng `--max-frames 30` để test nhanh |
