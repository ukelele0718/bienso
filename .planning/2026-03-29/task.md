# Task checklist - Mock import + server giả lập

Ngày: 2026-03-29

## Chuẩn bị dữ liệu & schema
- [x] Xác định schema hiện tại (`cameras`, `vehicle_events`, `plate_reads`).
- [x] Chốt mapping dữ liệu 10 bản ghi theo schema.
- [ ] Xác định camera thật trong DB (theo `name` hoặc `code`).

## Logic direction (in/out)
- [x] Đề xuất rule theo lane/camera (entry => in, exit => out).
- [ ] Quyết định camera thuộc entry hay exit (từ cấu hình thật).

## Snapshot URL qua HTTP
- [x] Chuyển sang HTTP URL thay vì `file:///`.
- [ ] Chốt `SNAPSHOT_BASE_URL` dùng khi import.

## Docker setup
- [ ] Cài Docker Desktop (hoặc engine phù hợp OS).
- [ ] Kiểm tra Docker chạy (`docker ps` thành công).
- [ ] (Optional) Cài `docker-compose` nếu chưa có.
- [ ] Khởi động stack giả lập bằng `docker-compose up`.

## Mock server (static)
- [x] Đề xuất kiến trúc mock server tối giản.
- [ ] Tạo mock server (FastAPI/Express) phục vụ ảnh `/static/...`.
- [ ] Chạy mock server tại `http://localhost:8088`.
- [ ] Kiểm tra mở được 1 ảnh qua URL HTTP.

## Postgres setup trong Docker
- [ ] Thêm service `postgres` vào `docker-compose.yml`.
- [ ] Khai báo biến môi trường: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- [ ] Mount volume để persist dữ liệu DB.
- [ ] Expose port (ví dụ `5432:5432`).
- [ ] Chạy migration backend vào DB Docker.
- [ ] Kiểm tra kết nối DB bằng client (`psql`/DBeaver).

## Cấu hình DB URL
- [ ] Khai báo `DATABASE_URL` trỏ vào Postgres Docker.
- [ ] Đồng bộ `DATABASE_URL` cho backend + script import.
- [ ] Test kết nối bằng lệnh health/check đơn giản.

## Import script
- [ ] Nâng script import nhận `camera_name` + `snapshot_base_url`.
- [ ] Map `camera_id` từ DB (fail nếu không có camera).
- [ ] Insert 10 `vehicle_events` + 10 `plate_reads`.
- [ ] Verify DB: đủ 10 records + URL mở được.

## Troubleshooting Docker/Postgres
- [ ] Port conflict: kiểm tra cổng 5432 đang bị chiếm (đổi sang 5433 nếu cần).
- [ ] Volume permission: nếu DB không ghi được, đổi volume sang thư mục có quyền hoặc dùng named volume.
- [ ] DB init fail: kiểm tra biến môi trường `POSTGRES_DB/USER/PASSWORD` và log container.

## Kiểm thử cuối
- [ ] Mở dashboard/backend xem dữ liệu hiển thị đúng.
- [ ] Nếu cần, chỉnh confidence/direction theo rule thực tế.
