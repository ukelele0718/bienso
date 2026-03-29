# Kế hoạch import 10 bản ghi + server giả lập

Ngày: 2026-03-29

## 1) Mục tiêu
- Import 10 bản ghi mẫu vào DB backend theo đúng schema hiện tại.
- `camera_id` lấy từ camera thật trong DB.
- `direction` theo logic rõ ràng (entry/exit).
- `snapshot_url` là HTTP URL (không dùng `file:///`).
- Dựng server giả lập đơn giản để test E2E.

---

## 2) Mapping schema hiện tại
Schema chính (từ migration):
- `cameras(id, name, gate_type, location, stream_url, is_active, created_at)`
- `vehicle_events(id, camera_id, timestamp, direction, vehicle_type, track_id, created_at)`
- `plate_reads(id, event_id, plate_text, confidence, snapshot_url, crop_url, ocr_status, created_at)`

Mapping đề xuất cho 10 mẫu:
- `camera_id`: truy theo camera thật (query theo `name` hoặc `camera_code` nếu có).
- `timestamp`: lấy NOW() - INTERVAL, tăng dần theo thứ tự file.
- `direction`: theo lane policy (xem phần 3).
- `vehicle_type`: `motorbike`.
- `track_id`: dùng string từ filename (đang có sẵn).
- `plate_text`: từ filename/annotation.
- `confidence`: cố định 0.85 hoặc random 0.80–0.95.
- `snapshot_url`: HTTP URL trỏ vào mock server.
- `ocr_status`: `success`.

---

## 3) Logic xác định direction (in/out)
**Ưu tiên khuyến nghị:** theo metadata camera/lane.

### Cách A (khuyến nghị)
- Camera “entry lane” => luôn `in`
- Camera “exit lane” => luôn `out`

Triển khai:
- Chọn camera thật trong DB (VD: `Gate A In`).
- Import script nhận `DIRECTION_MODE=by_camera`.
- Nếu camera thuộc nhóm entry => `direction='in'`, exit => `out`.

### Cách B (dự phòng)
- Nếu không có lane rõ ràng:
  - Theo thứ tự biển số: lần đầu `in`, lần sau `out`, xen kẽ.

---

## 4) `snapshot_url` bằng HTTP
**Mục tiêu:** tránh `file:///` để frontend/backend mô phỏng giống production.

Cấu hình:
- `SNAPSHOT_BASE_URL=http://localhost:8088/static/vnlp_xe_may_sample10/images`
- `snapshot_url = SNAPSHOT_BASE_URL + '/' + image_filename`

---

## 5) Thiết kế server giả lập (mock server)
### 5.1 Kiến trúc tối thiểu
- **Postgres**: DB backend.
- **Mock static server**: phục vụ ảnh qua HTTP.
- **(Optional) Mock API**: health check, hoặc push event giả.

### 5.2 Cấu trúc thư mục đề xuất
```
mock-server/
  app.py
  requirements.txt
  static/
    vnlp_xe_may_sample10/
      images/
        *.jpg
```

### 5.3 Chạy server (FastAPI hoặc Express)
- Mount `/static` folder.
- Health endpoint `/health` trả 200 OK.

Ví dụ URL test:
- `http://localhost:8088/static/vnlp_xe_may_sample10/images/4_1198_0_18u19495_469_149_615_264.jpg`

---

## 6) Thiết kế import script (SQL hoặc Python)
### 6.1 SQL script có tham số
- Nhận `camera_name`, `snapshot_base_url`.
- Query `camera_id` theo `camera_name`.
- Nếu không tồn tại -> fail.

Pseudo:
1. `SELECT id INTO camera_id FROM cameras WHERE name = :camera_name;`
2. `RAISE EXCEPTION` nếu NULL.
3. Insert `vehicle_events`.
4. Insert `plate_reads` với `snapshot_url` HTTP.

### 6.2 Python script (linh hoạt hơn)
- Load 10 mẫu từ CSV/manifest.
- Auto build URL, chọn direction theo rule.
- Insert vào DB qua `psycopg`.

---

## 7) Kịch bản chạy thử
1. Khởi động Postgres.
2. Chạy mock static server (port 8088).
3. Run import script (SQL/Python).
4. Query DB kiểm tra:
   - 10 `vehicle_events`
   - 10 `plate_reads`
   - `snapshot_url` mở được qua HTTP.

---

## 8) Checklist hoàn thiện
- [ ] Có camera thật trong DB với `name` cố định.
- [ ] Đã cấu hình `SNAPSHOT_BASE_URL`.
- [ ] Mock server chạy và truy cập được ảnh.
- [ ] Import script chạy không lỗi.
- [ ] Dữ liệu hiển thị đúng trên dashboard/backend.
