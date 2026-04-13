# 03 — Chạy Backend API

Backend là FastAPI server, nhận events từ AI Engine, lưu DB, cung cấp API cho Dashboard.

## Cách 1: SQLite (nhanh, không cần cài thêm gì)

Phù hợp để demo và phát triển. Không cần PostgreSQL.

```bash
# Từ thư mục gốc project
APP_DATABASE_URL="sqlite+pysqlite:///./demo.db" \
PYTHONPATH=apps/backend \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Windows CMD** (không hỗ trợ biến inline):
```cmd
set APP_DATABASE_URL=sqlite+pysqlite:///./demo.db
set PYTHONPATH=apps/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Windows PowerShell**:
```powershell
$env:APP_DATABASE_URL = "sqlite+pysqlite:///./demo.db"
$env:PYTHONPATH = "apps/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Tables tự tạo lần đầu chạy (chỉ khi dùng SQLite).

## Cách 2: PostgreSQL (production-like)

```bash
# 1. Tạo database
psql -U postgres -c "CREATE DATABASE vehicle_lpr;"

# 2. Chạy migrations
PYTHONPATH=apps/backend python apps/backend/scripts/run_migrations.py

# 3. Start server
PYTHONPATH=apps/backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Cấu hình qua biến môi trường:

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `APP_DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr` | Connection string |
| `APP_INITIAL_BALANCE_VND` | `100000` | Số dư ban đầu khi tạo account |
| `APP_CHARGE_PER_EVENT_VND` | `2000` | Phí mỗi lượt vào/ra |

## Cách 3: Docker

```bash
docker-compose up postgres backend
```

## Kiểm tra

```bash
# Health check
curl http://localhost:8000/health
# Mong đợi: {"status":"ok","time":"..."}

# Test tạo event
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "cam_test",
    "timestamp": "2026-04-13T12:00:00Z",
    "direction": "in",
    "vehicle_type": "motorbike",
    "track_id": "track_1",
    "plate_text": "29A12345",
    "confidence": 0.85
  }'
# Mong đợi: JSON với barrier_action, registration_status
```

Nếu health check trả `{"status":"ok"}` → backend sẵn sàng.

Tiếp → [04-chay-dashboard.md](04-chay-dashboard.md)
