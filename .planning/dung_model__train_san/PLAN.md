# Plan: Dùng model train sẵn + import 50 ảnh vào DB

**Mục tiêu**: Bỏ qua bước training, dùng model pretrained từ repo `trungdinh22/License-Plate-Recognition` để chạy **plate detection + OCR**, tạo **event thật** theo `API_CONTRACT.md` và lưu vào DB theo `DB_SCHEMA.md`. Đồng thời seed dữ liệu cơ bản cho `cameras`, `accounts`, `transactions`.

---

## 1) Model pretrained cần dùng (từ repo tham chiếu)
**Repo**: https://github.com/trungdinh22/License-Plate-Recognition

### 1.1 Model plate detection
- `LP_detector.pt` (full)
  - Download: https://raw.githubusercontent.com/trungdinh22/License-Plate-Recognition/main/model/LP_detector.pt
- `LP_detector_nano_61.pt` (nhẹ)
  - Download: https://raw.githubusercontent.com/trungdinh22/License-Plate-Recognition/main/model/LP_detector_nano_61.pt

### 1.2 Model OCR
- `LP_ocr.pt` (full)
  - Download: https://raw.githubusercontent.com/trungdinh22/License-Plate-Recognition/main/model/LP_ocr.pt
- `LP_ocr_nano_62.pt` (nhẹ)
  - Download: https://raw.githubusercontent.com/trungdinh22/License-Plate-Recognition/main/model/LP_ocr_nano_62.pt

### 1.3 YOLOv5 codebase (bắt buộc cho inference)
- Link tải yolov5 old version theo README:
  - https://drive.google.com/file/d/1g1u7M4NmWDsMGOppHocgBKjbwtDA-uIu/view?usp=sharing

**Quy ước sử dụng**:
- Ưu tiên model full (`LP_detector.pt`, `LP_ocr.pt`) nếu máy đủ GPU/CPU.
- Có thể fallback sang nano để tăng tốc.

---

## 2) Dữ liệu import (50 ảnh ngẫu nhiên)
**Nguồn ảnh**:
`G:/TTMT/datn/data/external/vnlp/VNLP_detection/detection/two_rows_label_xe_may`

**Yêu cầu**:
- Random 50 ảnh từ thư mục trên.
- Dùng ảnh như nguồn event thật (snapshot).
- Lưu snapshot/crop theo cơ chế lưu trữ hiện có (local file hoặc object storage tuỳ backend).

---

## 3) Luồng xử lý import + inference + lưu DB

### 3.1 Pipeline tổng
1) Chọn ngẫu nhiên 50 ảnh.
2) Với mỗi ảnh:
   - Plate detection → bbox.
   - Crop theo bbox → OCR.
   - Hậu xử lý → `plate_text`, `confidence`.
3) Tạo event theo `API_CONTRACT.md` (POST `/events`).
4) Backend ghi vào DB theo `DB_SCHEMA.md`.

### 3.2 Ghi DB (theo API side effects)
- `vehicle_events`: lưu event chính.
- `plate_reads`: lưu kết quả OCR + confidence.
- `accounts` + `transactions`:
  - Nếu plate mới: tạo `accounts` balance=100000 + `transactions` init.
  - Mỗi event: `transactions` event_charge = -2000 (cho phép âm).

---

## 4) Seed data bắt buộc
### 4.1 Cameras
- Tạo tối thiểu **2 camera** để hợp lệ nghiệp vụ:
  - `student_gate` (motorbike)
  - `lecturer_gate` (motorbike + car)

### 4.2 Accounts
- Không seed thủ công trước.
- Được tạo tự động khi plate mới xuất hiện (theo rule DB_SCHEMA).

### 4.3 Transactions
- Khởi tạo tự động khi có account mới và khi có event.
- Không seed riêng.

---

## 5) Các hạng mục kỹ thuật cần triển khai

### 5.1 Tích hợp model pretrained
- Thêm script tải model về thư mục nội bộ dự án (ví dụ `models/` hoặc `assets/models/`).
- Thêm cấu hình đường dẫn model trong backend (config/env).

### 5.2 Inference pipeline
- Module đọc ảnh → detect plate → crop → OCR.
- Chuẩn hóa output: `plate_text`, `confidence`, `raw_text`.
- Mapping plate VN 1 dòng/2 dòng (normalize theo regex).

### 5.3 Import script
- Script CLI `scripts/import_vnlp_seed.py`:
  - Random 50 ảnh.
  - Gọi inference.
  - Gọi API `/events` để lưu DB.

### 5.4 Backend
- Endpoint `/events` theo `API_CONTRACT.md`.
- Logic tài chính theo `DB_SCHEMA.md`.
- Lưu snapshot/crop (local disk hoặc object storage).

---

## 6) Test plan nhanh
- Chạy import 50 ảnh → DB có 50 `vehicle_events`.
- Tỷ lệ OCR success được tính và xuất lên dashboard.
- Accounts + Transactions đúng rule (init + charge).

---

## 7) Deliverables
- Model pretrained tải về và cấu hình thành công.
- Script import 50 ảnh + gọi API.
- DB có dữ liệu thật từ OCR.
- Dashboard hiển thị dữ liệu hợp lệ.

---

## 8) Open Questions (cần xác nhận trước khi triển khai)
1) Lưu snapshot/crop vào local disk hay object storage?
2) Chọn model full hay nano làm mặc định?
3) Có cần tạo user/admin seed không?

---

## 9) Next Steps (đề xuất)
1) Xác nhận cấu hình lưu ảnh + model mặc định.
2) Implement download model script.
3) Implement inference module + import script.
4) Wire backend `/events` + DB.
5) Run import 50 ảnh và kiểm tra dashboard.
