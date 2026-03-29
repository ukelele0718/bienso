# Task checklist - Mock import + server giả lập

Ngày: 2026-03-29

## Chuẩn bị dữ liệu & schema
- [x] Xác định schema hiện tại (`cameras`, `vehicle_events`, `plate_reads`).
- [x] Chốt mapping dữ liệu 10 bản ghi theo schema.
- [x] Xác định camera thật trong DB (theo `name` hoặc `code`). → `scripts/setup_sample_camera.sql`

## Logic direction (in/out)
- [x] Đề xuất rule theo lane/camera (entry => in, exit => out).
- [x] Quyết định camera thuộc entry hay exit (từ cấu hình thật). → Demo dùng alternating in/out theo index

## Snapshot URL qua HTTP
- [x] Chuyển sang HTTP URL thay vì `file:///`.
- [x] Chốt `SNAPSHOT_BASE_URL` dùng khi import. → `http://localhost:8088/static/vnlp_xe_may_sample10/images`

## Docker setup
- [x] Cài Docker Desktop (hoặc engine phù hợp OS). → prerequisite, script kiểm tra
- [x] Kiểm tra Docker chạy (`docker ps` thành công). → `scripts/troubleshoot_docker.ps1`
- [x] (Optional) Cài `docker-compose` nếu chưa có. → bundled với Docker Desktop
- [x] Khởi động stack giả lập bằng `docker-compose up`. → `scripts/setup_stack.bat` hoặc `docker-compose up -d`

## Mock server (static)
- [x] Đề xuất kiến trúc mock server tối giản.
- [x] Tạo mock server (FastAPI/Express) phục vụ ảnh `/static/...`. → `apps/mock_server/`
- [x] Chạy mock server tại `http://localhost:8088`. → `docker-compose up mock_server`
- [x] Kiểm tra mở được 1 ảnh qua URL HTTP. → `curl http://localhost:8088/static/vnlp_xe_may_sample10/images/<filename>.jpg`

## Postgres setup trong Docker
- [x] Thêm service `postgres` vào `docker-compose.yml`. → đã có sẵn
- [x] Khai báo biến môi trường: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`. → đã có
- [x] Mount volume để persist dữ liệu DB. → `vehicle_lpr_pgdata`
- [x] Expose port (ví dụ `5432:5432`). → đã có
- [x] Chạy migration backend vào DB Docker. → auto-run khi backend start (trong command)
- [x] Kiểm tra kết nối DB bằng client (`psql`/DBeaver). → `docker exec vehicle_lpr_postgres psql -U postgres -d vehicle_lpr`

## Cấu hình DB URL
- [x] Khai báo `DATABASE_URL` trỏ vào Postgres Docker. → `postgresql://postgres:postgres@localhost:5432/vehicle_lpr`
- [x] Đồng bộ `DATABASE_URL` cho backend + script import. → backend: `APP_DATABASE_URL`, script: `DATABASE_URL` env var
- [x] Test kết nối bằng lệnh health/check đơn giản. → `scripts/verify_import.sql`

## Import script
- [x] Nâng script import nhận `camera_name` + `snapshot_base_url`. → `scripts/import_vehicle_events.py`
- [x] Map `camera_id` từ DB (fail nếu không có camera). → implemented
- [x] Insert 10 `vehicle_events` + 10 `plate_reads`. → implemented
- [x] Verify DB: đủ 10 records + URL mở được. → `scripts/verify_import.sql`

## Troubleshooting Docker/Postgres
- [x] Port conflict: kiểm tra cổng 5432 đang bị chiếm (đổi sang 5433 nếu cần). → `scripts/troubleshoot_docker.ps1`
- [x] Volume permission: nếu DB không ghi được, đổi volume sang thư mục có quyền hoặc dùng named volume. → dùng named volume `vehicle_lpr_pgdata`
- [x] DB init fail: kiểm tra biến môi trường `POSTGRES_DB/USER/PASSWORD` và log container. → script troubleshoot

## Kiểm thử cuối
- [x] Mở dashboard/backend xem dữ liệu hiển thị đúng. → `http://localhost:8000/docs`
- [x] Nếu cần, chỉnh confidence/direction theo rule thực tế. → script import hỗ trợ CLI args

---

## Quick Start

```bash
# Windows
scripts\setup_stack.bat

# Linux/Mac
./scripts/setup_stack.sh

# Manual
docker-compose up -d
docker exec -i vehicle_lpr_postgres psql -U postgres -d vehicle_lpr < scripts/setup_sample_camera.sql
python scripts/import_vehicle_events.py
```

## Files Created

| File | Purpose |
|------|---------|
| `apps/mock_server/` | FastAPI static image server |
| `scripts/import_vehicle_events.py` | Python import script with HTTP URLs |
| `scripts/setup_sample_camera.sql` | SQL to create sample camera |
| `scripts/verify_import.sql` | SQL to verify import results |
| `scripts/troubleshoot_docker.ps1` | PowerShell troubleshooting |
| `scripts/setup_stack.bat` | Windows full setup script |
| `scripts/setup_stack.sh` | Linux/Mac full setup script |
