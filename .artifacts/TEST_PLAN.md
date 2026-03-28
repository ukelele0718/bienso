# TEST_PLAN
## Kế hoạch kiểm thử chi tiết (Unit → API → Integration → UI)

**Dự án**: Hệ thống đếm phương tiện & nhận dạng biển số (1 camera)  
**Ngày cập nhật**: 2026-03-27  
**Mục tiêu**: Liệt kê đầy đủ test cases có checkbox để theo dõi tiến độ kiểm thử.

---

## 1) Phạm vi kiểm thử
- Backend API (FastAPI + PostgreSQL)
- Rule nghiệp vụ số dư (100,000 khởi tạo, -2,000/lượt, cho phép âm)
- Pipeline dữ liệu event (AI -> API -> DB)
- Dashboard UI (realtime, tra cứu, số dư, thống kê)
- Typed quality gates (Python type hints + TypeScript strict)

---

## 2) Unit Test Cases

## 2.1 Unit test - Business Rule (Số dư)
- [ ] Khởi tạo account mới khi plate xuất hiện lần đầu.
- [ ] Số dư khởi tạo đúng 100,000 VND.
- [ ] Event đầu tiên bị trừ đúng 2,000 VND.
- [ ] Nhiều event liên tiếp trừ đúng mỗi lượt 2,000 VND.
- [ ] Số dư được phép âm sau đủ số lượt.
- [ ] Transaction type `init` được tạo đúng khi account mới.
- [ ] Transaction type `event_charge` được tạo cho mỗi event in/out.
- [ ] `balance_after_vnd` ở transaction khớp số dư thực tế account.

## 2.2 Unit test - CRUD / Query logic
- [ ] `create_event` tạo đủ `vehicle_events` + `plate_reads`.
- [ ] `list_events` filter theo `plate` hoạt động đúng.
- [ ] `list_events` filter theo `from_time` hoạt động đúng.
- [ ] `list_events` filter theo `to_time` hoạt động đúng.
- [ ] `list_events` filter theo `direction` hoạt động đúng.
- [ ] `list_events` filter theo `vehicle_type` hoạt động đúng.
- [ ] `get_account` trả đúng dữ liệu với plate hợp lệ.
- [ ] `get_account` ném lỗi NotFound với plate không tồn tại.
- [ ] `list_transactions` trả đúng thứ tự/thông tin lịch sử giao dịch.

## 2.3 Unit test - Tính toán thống kê
- [ ] `get_realtime_stats` tính đúng `total_in`.
- [ ] `get_realtime_stats` tính đúng `total_out`.
- [ ] `get_realtime_stats` tính đúng `ocr_success_rate` khi có dữ liệu.
- [ ] `get_realtime_stats` không lỗi chia 0 khi chưa có event.
- [ ] `get_ocr_rate` trả đúng tỷ lệ OCR.

## 2.4 Unit test - Barrier decision logic
- [ ] Hàm quyết định barrier trả `open` cho `registered + in`.
- [ ] Hàm quyết định barrier trả `open` cho `temporary_registered + in`.
- [ ] Hàm quyết định barrier trả `hold` cho `temporary_registered + out`.
- [ ] Hàm quyết định barrier trả `hold` cho `unknown + out`.
- [ ] Hệ thống gán `barrier_reason` đúng theo từng nhánh rule.
- [ ] Hệ thống bật `needs_verification=true` khi `barrier_action=hold`.
- [ ] Verify thành công cập nhật trạng thái từ `hold -> open` đúng rule.
- [ ] Verify thất bại giữ nguyên `hold` và không phát lệnh mở.

---

## 3) API Test Cases (HTTP level)

## 3.1 API - Event endpoints
- [ ] `POST /api/v1/events` trả 200 với payload hợp lệ.
- [ ] `POST /api/v1/events` từ chối direction không hợp lệ.
- [ ] `POST /api/v1/events` từ chối vehicle_type không hợp lệ.
- [ ] `POST /api/v1/events` từ chối confidence ngoài [0,1].
- [ ] `GET /api/v1/events` trả danh sách event đúng schema.
- [ ] `GET /api/v1/events` filter plate hoạt động đúng.
- [ ] `GET /api/v1/events` filter khoảng thời gian hoạt động đúng.

## 3.2 API - Account/Transaction endpoints
- [ ] `GET /api/v1/accounts/{plate}` trả đúng số dư.
- [ ] `GET /api/v1/accounts/{plate}` trả 404 với plate chưa tồn tại.
- [ ] `GET /api/v1/accounts/{plate}/transactions` trả đúng lịch sử.
- [ ] `GET /api/v1/accounts/{plate}/transactions` trả 404 nếu account không tồn tại.

## 3.3 API - Stats endpoints
- [ ] `GET /api/v1/stats/realtime` trả đủ fields `total_in/total_out/ocr_success_rate`.
- [ ] `GET /api/v1/stats/ocr-success-rate` trả đúng format.
- [ ] `GET /api/v1/stats/traffic` trả 200 và đúng schema (dù chưa có dữ liệu).
- [ ] `GET /health` trả `status=ok`.

## 3.4 API - Barrier logic endpoints/fields
- [ ] `POST /api/v1/events` trả thêm `barrier_action` đúng rule.
- [ ] `POST /api/v1/events` trả `barrier_reason` tương ứng decision branch.
- [ ] `POST /api/v1/events` với xe lạ vào: response có `registration_status=temporary_registered`.
- [ ] `POST /api/v1/events` với xe tạm đăng ký ra: response có `barrier_action=hold`.
- [ ] API verify (nếu có endpoint riêng) chuyển trạng thái `hold -> open` khi xác thực thành công.
- [ ] API verify trả lỗi đúng khi thiếu dữ liệu xác thực hoặc xác thực thất bại.
- [ ] Endpoint truy vấn log barrier (nếu có) trả đủ trường `action/reason/needs_verification/actor/timestamp`.

---

## 4) Database & Migration Test Cases

## 4.1 Migration
- [ ] Chạy migration 001 thành công trên DB trống.
- [ ] Chạy migration lặp lại không gây lỗi nghiêm trọng (idempotency cơ bản).
- [ ] Tạo đủ bảng: cameras, vehicle_events, plate_reads, accounts, transactions, audit_logs.
- [ ] Tạo đủ index theo thiết kế.

## 4.2 Constraints / Integrity
- [ ] FK `vehicle_events.camera_id -> cameras.id` hoạt động đúng.
- [ ] FK `plate_reads.event_id -> vehicle_events.id` hoạt động đúng.
- [ ] FK `transactions.account_id -> accounts.id` hoạt động đúng.
- [ ] Check constraint `direction IN (in,out)` hoạt động đúng.
- [ ] Check constraint `vehicle_type IN (motorbike,car)` hoạt động đúng.
- [ ] Check constraint `ocr_status` hoạt động đúng.
- [ ] Check constraint `transactions.type` hoạt động đúng.
- [ ] Unique `accounts.plate_text` hoạt động đúng.

---

## 5) Integration Test Cases

## 5.1 API + DB Integration
- [ ] Tạo event có plate -> DB tạo account + transactions đúng.
- [ ] Tạo event không plate -> không tạo account/transaction sai.
- [ ] Dữ liệu trả ra từ API khớp dữ liệu lưu DB.
- [ ] Truncate/reset fixture sau mỗi test hoạt động đúng.

## 5.2 AI payload compatibility
- [ ] Payload từ AI giả lập map đúng schema API.
- [ ] Timestamp ISO format từ AI parse đúng.
- [ ] Track ID chuỗi bất kỳ vẫn xử lý đúng.
- [ ] Plate null/empty xử lý an toàn.

---

## 6) UI Test Cases (Dashboard)

## 6.1 UI - Realtime page
- [ ] Hiển thị được cards realtime (`in/out/ocr rate`).
- [ ] Bảng sự kiện hiển thị đúng cột yêu cầu.
- [ ] Trạng thái loading hiển thị đúng khi chờ API.
- [ ] Trạng thái empty hiển thị đúng khi chưa có dữ liệu.
- [ ] Trạng thái error + retry hoạt động đúng khi API lỗi.

## 6.2 UI - Search page
- [ ] Filter theo biển số hoạt động đúng.
- [ ] Filter theo khoảng thời gian hoạt động đúng.
- [ ] Kết quả tìm kiếm khớp dữ liệu backend.
- [ ] Mở chi tiết event hiển thị đủ metadata.

## 6.3 UI - Account/Balance page
- [ ] Tra cứu account theo biển số trả đúng số dư.
- [ ] Hiển thị số dư âm đúng định dạng.
- [ ] Hiển thị lịch sử transactions đầy đủ.
- [ ] Liên kết transaction với event (nếu có event_id) hoạt động đúng.

## 6.4 UI - Stats page
- [ ] Biểu đồ lưu lượng giờ/ngày hiển thị đúng.
- [ ] OCR success rate hiển thị đúng.
- [ ] Bộ lọc thời gian cập nhật biểu đồ đúng.

---

## 7) End-to-End (E2E) Test Cases
- [ ] Luồng chuẩn: tạo event in -> kiểm tra realtime -> kiểm tra số dư.
- [ ] Luồng chuẩn: tạo event out -> kiểm tra counter out tăng.
- [ ] Luồng nhiều event cùng 1 plate -> số dư giảm tuyến tính.
- [ ] Luồng âm tiền: đủ số event để balance < 0.
- [ ] Luồng tra cứu: nhập plate + time range -> trả đúng dữ liệu.

## 7.1 E2E - Logic thanh chắn (open/hold/verify)
- [ ] Xe đã đăng ký vào cổng (`registered` + `in`) => `barrier_action=open`.
- [ ] Xe lạ vào cổng lần đầu (`unknown` + `in`) => tự tạo `temporary_registered` và `barrier_action=open`.
- [ ] Xe tạm đăng ký ra cổng (`temporary_registered` + `out`) => `barrier_action=hold`.
- [ ] Khi `hold`, UI/guard console hiển thị trạng thái `needs_verification=true`.
- [ ] Sau thao tác verify thành công => hệ thống ghi log verify và đổi hành động sang `open`.
- [ ] Verify thất bại => vẫn giữ `hold`, không mở thanh chắn.
- [ ] Mọi quyết định thanh chắn được ghi vào log đầy đủ (reason, actor, timestamp).

---

## 8) Non-functional Test Cases

## 8.1 Performance
- [ ] Đo latency từ `POST /events` tới hiển thị dashboard.
- [ ] Đo throughput API khi gửi nhiều event liên tiếp.
- [ ] Đánh giá truy vấn search khi dữ liệu tăng.

## 8.2 Reliability
- [ ] Backend restart không mất schema/data (với volume DB).
- [ ] Xử lý lỗi DB tạm thời (timeout/disconnect) không crash toàn app.

## 8.3 Security cơ bản
- [ ] Không lộ stacktrace nội bộ ra response production mode.
- [ ] Validate input ngăn payload sai format.
- [ ] Kiểm tra endpoint không cho dữ liệu sai kiểu.

---

## 9) Typed Quality Gate Test Cases

## 9.1 Python
- [ ] `mypy/pyright` pass cho backend.
- [ ] Không có function public thiếu type annotation.

## 9.2 TypeScript
- [ ] `tsc --noEmit` pass cho dashboard.
- [ ] Không dùng `any` trong module chính.

---

## 10) Regression Checklist (mỗi lần release)
- [ ] Re-run toàn bộ Unit tests.
- [ ] Re-run API tests cho event/account/stats.
- [ ] Re-run balance rule tests.
- [ ] Re-run smoke UI tests (realtime/search/account).
- [ ] Re-run migration test trên DB mới.

---

## 11) Test Data Checklist
- [ ] Có seed camera hợp lệ cho FK trước khi test.
- [ ] Có dữ liệu test cho plate hợp lệ VN.
- [ ] Có dữ liệu test plate null/không đọc được.
- [ ] Có dữ liệu test cho mốc thời gian cũ/mới để kiểm tra filter.
- [ ] Có dữ liệu đủ nhiều để test trường hợp balance âm.

---

## 12) Tiến độ thực thi test (Tracking)
- [ ] Hoàn thành Unit tests
- [ ] Hoàn thành API tests
- [ ] Hoàn thành Integration tests
- [ ] Hoàn thành UI tests
- [ ] Hoàn thành E2E tests
- [ ] Hoàn thành Non-functional tests
- [ ] Hoàn thành Typed quality gates
