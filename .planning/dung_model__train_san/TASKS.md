# TASKS — Pretrained LPR Import Flow

**Branch**: `feat/pretrained-lpr-import-flow`
**Mục tiêu**: Dùng model pretrained để chạy detection + OCR, import 50 ảnh VNLP vào hệ thống như event thật, hiển thị được trên backend/dashboard, không phụ thuộc train.

---

## Milestone 1 — Chuẩn bị model và cấu hình runtime

### Task 1.1: Chuẩn hóa thư mục model trong dự án
- [ ] Tạo cấu trúc lưu model (vd: `apps/backend/models/` hoặc `assets/models/`)
- [ ] Document rõ 4 model hỗ trợ:
  - `LP_detector.pt`
  - `LP_ocr.pt`
  - `LP_detector_nano_61.pt`
  - `LP_ocr_nano_62.pt`
- [ ] Quy ước model mặc định (full hoặc nano)

### Task 1.2: Viết script tải model pretrained
- [ ] Tạo script `scripts/download_pretrained_models.py`
- [ ] Hỗ trợ skip nếu file đã tồn tại
- [ ] In ra checksum/size sau khi tải
- [ ] Log rõ link nguồn để trace

### Task 1.3: Cấu hình backend để đọc model path
- [ ] Thêm env/config:
  - `LPR_DETECT_MODEL_PATH`
  - `LPR_OCR_MODEL_PATH`
  - `LPR_DEVICE` (`cpu`/`cuda`)
- [ ] Validate path khi backend boot
- [ ] Fallback hợp lý nếu model thiếu

---

## Milestone 2 — Inference pipeline (detect plate + OCR)

### Task 2.1: Thiết kế interface typed cho inference
- [ ] Tạo `DetectionResult`, `OcrResult`, `LprResult`
- [ ] Define trường bắt buộc: bbox, plate_text, confidence, raw_text, normalized_text
- [ ] Đảm bảo type-check pass

### Task 2.2: Implement module plate detection
- [ ] Load model detection 1 lần (singleton/service)
- [ ] Input ảnh đường dẫn hoặc ndarray
- [ ] Trả danh sách bbox + conf

### Task 2.3: Implement module OCR
- [ ] Crop từ bbox và chạy OCR model
- [ ] Hỗ trợ nhiều thử nghiệm deskew/rotate (nếu cần)
- [ ] Trả text + confidence

### Task 2.4: Post-process biển số VN
- [ ] Normalize ký tự dễ nhầm (O/0, I/1, B/8, S/5)
- [ ] Chuẩn hóa format biển 1 dòng/2 dòng
- [ ] Gán `ocr_status` (`success`/`failed`/`partial`)

### Task 2.5: Unit tests cho inference service
- [ ] Test load model thành công/thất bại
- [ ] Test output typed
- [ ] Test post-process regex cơ bản

---

## Milestone 3 — Seed & import 50 ảnh vào DB như event thật

### Task 3.1: Seed dữ liệu camera
- [ ] Seed `student_gate` camera
- [ ] Seed `lecturer_gate` camera
- [ ] Tránh tạo trùng (idempotent)

### Task 3.2: Script chọn ngẫu nhiên 50 ảnh
- [ ] Nguồn: `data/external/vnlp/VNLP_detection/detection/two_rows_label_xe_may`
- [ ] Random có seed cố định để reproducible
- [ ] Sinh danh sách input manifest (để audit)

### Task 3.3: Import script gọi inference + API
- [ ] Tạo `scripts/import_vnlp_pretrained_events.py`
- [ ] Với mỗi ảnh:
  - chạy detect + OCR
  - map payload theo `/events`
  - gửi API để backend ghi DB
- [ ] Có retry/log lỗi theo từng ảnh
- [ ] In summary cuối: total/success/failed/OCR success rate

### Task 3.4: Ghi dữ liệu tài chính đúng rule
- [ ] Nếu plate mới: tạo `accounts` balance 100000
- [ ] Tạo `transactions` init +100000
- [ ] Mỗi event charge -2000
- [ ] Cho phép balance âm

### Task 3.5: Integration test import
- [ ] Sau import có ~50 `vehicle_events`
- [ ] `plate_reads` có confidence hợp lệ
- [ ] `accounts`/`transactions` khớp rule nghiệp vụ

---

## Milestone 4 — Dashboard & API verification

### Task 4.1: Verify API contract
- [ ] Endpoint `/events` nhận payload đầy đủ
- [ ] Endpoint search theo plate + time-range trả dữ liệu đúng
- [ ] Endpoint stats phản ánh dữ liệu import

### Task 4.2: Dashboard hiển thị dữ liệu import
- [ ] Realtime/recent events có bản ghi mới
- [ ] OCR success rate cập nhật
- [ ] Search plate theo thời gian hoạt động
- [ ] Balance và lịch sử charge hiển thị đúng

### Task 4.3: Smoke test end-to-end
- [ ] Chạy import script 1 lần sạch
- [ ] Chụp minh chứng UI + API response mẫu
- [ ] Ghi lại runbook thao tác

---

## Milestone 5 — Tài liệu hóa & bàn giao

### Task 5.1: Cập nhật runbook
- [ ] Cách tải model
- [ ] Cách seed camera
- [ ] Cách import 50 ảnh
- [ ] Cách kiểm tra DB và dashboard

### Task 5.2: Cập nhật artifacts liên quan
- [ ] Ghi quyết định “không train, dùng pretrained” vào implementation note
- [ ] Cập nhật test plan cho luồng import pretrained

### Task 5.3: Checklist nghiệm thu
- [ ] Không phụ thuộc bước train
- [ ] Import 50 ảnh thành công
- [ ] Dữ liệu vào DB và dashboard đúng
- [ ] Type-check/lint pass

---

## Ưu tiên thực thi đề xuất
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

---

## Definition of Done
- Có branch riêng cho feature.
- Có pipeline pretrained inference hoạt động.
- Có script import 50 ảnh chạy ổn định.
- Dữ liệu event + plate_read + account + transaction đúng rule.
- Dashboard tra cứu/hiển thị đúng dữ liệu import.
