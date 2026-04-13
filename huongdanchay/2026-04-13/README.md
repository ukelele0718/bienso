# Hướng dẫn chạy hệ thống End-to-End

**Ngày**: 2026-04-13
**Hệ thống**: Đếm phương tiện + Nhận dạng biển số + Quản lý ra/vào

---

## Kiến trúc tổng thể

```
Video/Camera ──► AI Engine (Python) ──► Backend API (FastAPI :8000) ──► Dashboard (React :5173)
                 │                        │
                 │ detect + OCR           │ lưu DB
                 │ gửi event HTTP         │
                 ▼                        ▼
              Models (.pt)            SQLite / PostgreSQL
```

## Yêu cầu hệ thống

| Phần mềm | Phiên bản tối thiểu | Ghi chú |
|-----------|---------------------|---------|
| Python | 3.11+ | Khuyến nghị 3.11–3.14 |
| Node.js | 18+ | Khuyến nghị 20+ |
| npm | 8+ | Đi kèm Node.js |
| Git | 2.30+ | |
| GPU (optional) | CUDA 11.8+ | Nếu có NVIDIA GPU, AI Engine nhanh hơn ~10x |

## Các file hướng dẫn

| File | Nội dung |
|------|----------|
| [01-clone-va-cai-dat.md](01-clone-va-cai-dat.md) | Clone repo, cài dependencies |
| [02-download-models.md](02-download-models.md) | Tải AI models (bắt buộc) |
| [03-chay-backend.md](03-chay-backend.md) | Khởi động Backend API |
| [04-chay-dashboard.md](04-chay-dashboard.md) | Khởi động Dashboard |
| [05-chay-ai-engine.md](05-chay-ai-engine.md) | Chạy AI Engine xử lý video |
| [06-chay-e2e-demo.md](06-chay-e2e-demo.md) | Chạy demo toàn bộ luồng |

## Chạy nhanh (đã cài đặt xong)

```bash
# Terminal 1 — Backend
APP_DATABASE_URL="sqlite+pysqlite:///./demo.db" PYTHONPATH=apps/backend \
  python -m uvicorn app.main:app --port 8000

# Terminal 2 — Dashboard
cd apps/dashboard && npm run dev

# Terminal 3 — AI Engine → Backend
python scripts/run-e2e-demo.py \
  --video data/test-videos/trungdinh22-demo.mp4 \
  --camera cam_gate_1

# Mở browser: http://localhost:5173
```
