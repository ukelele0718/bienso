# Product Requirements Document (PRD)
## Hệ thống đếm phương tiện & nhận dạng biển số (prototype 1 camera)

**Phiên bản**: 2.1  
**Ngày cập nhật**: 2026-03-27  
**Trạng thái**: Ready for execution

---

## 1) Mục tiêu sản phẩm
Xây dựng prototype end-to-end cho bài toán quản lý phương tiện ra/vào bằng thị giác máy tính, tập trung **duy nhất 1 luồng camera**.

Hệ thống cần:
- Đếm lượt phương tiện vào/ra.
- Nhận dạng biển số Việt Nam.
- Lưu sự kiện + ảnh minh chứng vào server/CSDL.
- Hiển thị dashboard realtime, thống kê, tra cứu.
- Hỗ trợ nghiệp vụ số dư: khởi tạo 100,000 VND, mỗi lượt vào/ra trừ 2,000 VND, cho phép âm.
- **Tự động điều khiển thanh chắn theo quy tắc nhận diện biển số**:
  - Xe đã đăng ký: vào tự động, so khớp DB và mở thanh chắn.
  - Xe lạ: vào vẫn cho qua và tự động tạo đăng ký tạm.
  - Lúc xe lạ ra: chặn lại để xác thực trước khi mở thanh chắn.

---

## 2) Phạm vi triển khai

### 2.1 In-scope
- Chỉ xử lý **1 luồng video/camera**.
- Hai kịch bản cổng:
  1. Cổng sinh viên: xe máy.
  2. Cổng giảng viên: xe máy + ô tô.
- Dữ liệu thử nghiệm: dataset công khai từ internet, ưu tiên biển số chuẩn Việt Nam.
- Luồng bắt buộc:
  - `Video` → detect vehicle → track → count in/out → detect plate → OCR → post-process → kiểm tra đăng ký biển số trong DB → quyết định thanh chắn (open/hold) → send event to server → dashboard.
- Server/CSDL lưu: nhật ký sự kiện, ảnh minh chứng, biển số, thời gian, loại phương tiện.
- Dashboard hiển thị:
  - realtime số lượt vào/ra,
  - lưu lượng giờ/ngày,
  - danh sách biển số gần nhất,
  - tra cứu theo biển số + khoảng thời gian,
  - tỉ lệ nhận dạng thành công,
  - số dư và lịch sử trừ tiền theo biển số.

### 2.2 Out-of-scope
- Multi-camera orchestration.
- Tích hợp barrier/gate hardware production.
- Triển khai full campus ngay từ đầu.

---

## 3) Ràng buộc công nghệ (typed-first)
- AI + Backend: Python 3.11+ với type hinting nghiêm ngặt.
- Dashboard: TypeScript + React.
- Bắt buộc type-check trước tích hợp.

---

## 4) Personas & Use Cases

### 4.1 Personas
- **Bảo vệ cổng**: theo dõi realtime xe vào/ra, kiểm tra event mới.
- **Phòng quản trị**: xem lưu lượng theo giờ/ngày, tỉ lệ OCR.
- **Sinh viên**: **tra cứu lượt vào/ra của mình** theo biển số và khoảng thời gian.
- **Quản trị hệ thống**: theo dõi sức khỏe pipeline, cấu hình line/zone.

### 4.2 Use cases chính
- UC01: Ghi nhận event in/out theo camera.
- UC02: Nhận dạng biển số Việt Nam cho mỗi event.
- UC03: Tra cứu event theo biển số + khoảng thời gian.
- UC04: Xem thống kê realtime và lịch sử.
- UC05: Tính và hiển thị số dư tài khoản biển số:
  - Số dư khởi tạo: 100,000 VND.
  - Mỗi lượt in/out: -2,000 VND.
  - Cho phép âm.
- UC06: Điều khiển thanh chắn tự động theo đăng ký biển số:
  - Xe đã đăng ký vào: mở thanh chắn tự động.
  - Xe lạ vào: tự động tạo đăng ký tạm và mở thanh chắn.
  - Xe lạ ra: giữ thanh chắn ở trạng thái chặn, yêu cầu xác thực thủ công/OTP/mã nhân viên bảo vệ trước khi mở.

---

## 5) Functional Requirements

### 5.1 AI Pipeline
- FR-01: Nhận 1 nguồn video (file hoặc RTSP).
- FR-02: Detect class `motorbike`, `car`.
- FR-03: Tracking theo `track_id` ổn định.
- FR-04: Đếm vào/ra theo line hoặc zone.
- FR-05: Detect vùng biển số.
- FR-06: OCR biển số.
- FR-07: Hậu xử lý chuỗi theo regex biển số Việt Nam.
- FR-08: Chọn frame tốt nhất trước OCR.

### 5.2 Backend/CSDL
- FR-09: API nhận event typed.
- FR-10: Lưu event + ảnh snapshot/crop + confidence.
- FR-11: API tra cứu event theo biển số và khoảng thời gian.
- FR-12: API thống kê realtime + traffic theo giờ/ngày.
- FR-13: Module tài chính theo biển số:
  - Khởi tạo 100,000 VND khi biển số xuất hiện lần đầu.
  - Trừ 2,000 VND cho mỗi event in/out.
  - Lưu lịch sử giao dịch.
  - Chấp nhận số dư âm.
- FR-14: Module đăng ký và trạng thái xe:
  - Lưu trạng thái `registered`, `temporary_registered`, `unknown`.
  - Xe lạ vào cổng: tự động tạo bản ghi đăng ký tạm.
- FR-15: Module điều khiển thanh chắn:
  - Trả quyết định `open` hoặc `hold` theo rule nghiệp vụ.
  - Ghi log quyết định thanh chắn cho mỗi event.
- FR-16: Module xác thực xe lạ khi ra cổng:
  - Nếu xe ở trạng thái `temporary_registered` và direction=`out` thì mặc định `hold`.
  - Chỉ mở khi xác thực thành công bởi bảo vệ/hệ thống.

### 5.3 Dashboard
- FR-14: Realtime counter vào/ra.
- FR-15: Danh sách biển số gần nhất.
- FR-16: Tra cứu theo biển số + khoảng thời gian.
- FR-17: Biểu đồ lưu lượng giờ/ngày.
- FR-18: Hiển thị OCR success rate.
- FR-19: Hiển thị số dư hiện tại và lịch sử trừ tiền.

---

## 6) Non-functional Requirements
- NFR-01: Latency camera → dashboard mục tiêu < 3 giây.
- NFR-02: Throughput xử lý tối thiểu 10 FPS (1 camera test).
- NFR-03: Sai số đếm mục tiêu prototype <= 7%.
- NFR-04: OCR full-match mục tiêu >= 85% trên tập test phù hợp.
- NFR-05: API schema typed, type-check pass bắt buộc.

---

## 7) Data model cốt lõi
- `vehicle_events(id, camera_id, timestamp, direction, vehicle_type, track_id)`
- `plate_reads(id, event_id, plate_text, confidence, snapshot_url, crop_url, ocr_status)`
- `accounts(id, plate_text, balance_vnd, created_at, updated_at)`
- `transactions(id, account_id, event_id, amount_vnd, balance_after_vnd, created_at)`

Nghiệp vụ tài chính:
- `initial_balance_vnd = 100000`
- `charge_per_event_vnd = -2000`

---

## 8) Dữ liệu công khai (biển số Việt Nam)

### 8.1 Nguồn ưu tiên
1. VNLP dataset (GitHub): https://github.com/fict-labs/VNLP
2. Kaggle (bổ sung, nếu cần)
3. Roboflow Universe (bổ sung, nếu cần)

### 8.2 Hướng dẫn tải về dự án
```bash
mkdir -p data/raw data/external data/processed
pip install gdown kaggle
# VNLP: lấy link Google Drive từ README rồi chạy
gdown --folder "<VNLP_GOOGLE_DRIVE_FOLDER_URL>" -O data/external/vnlp
```

---

## 9) Thách thức và hướng giải quyết
- **Luồng xe hỗn hợp trong cùng khung hình**: cần tập dữ liệu đa dạng và luật đếm ổn định.
- **Điều kiện ngày/đêm, mưa, ngược sáng**: cần tăng cường dữ liệu hoặc tiền xử lý phù hợp.
- **Biển số mờ, bẩn, che khuất**: cần bước chọn frame tốt nhất, deblur/căn chỉnh và hậu xử lý.
- **Che khuất giữa nhiều xe**: cần tracking tốt để tránh đếm sai và chọn đúng ảnh biển số.
- **Góc nghiêng camera**: cần hiệu chỉnh phối cảnh/rotation trước OCR.

---

## 10) KPI nghiệm thu
- KPI-01: End-to-end chạy ổn định 1 stream.
- KPI-02: Đếm in/out đúng trong ngưỡng mục tiêu.
- KPI-03: OCR đạt ngưỡng mục tiêu prototype.
- KPI-04: Dashboard tra cứu theo biển số + time-range hoạt động đúng.
- KPI-05: Rule 100,000/-2,000/cho phép âm chạy đúng.

---

## 11) Tài liệu tham khảo (trích nguồn đầy đủ)
1. Axis Communications AB. *License Plate Capture*, White Paper, Dec 2024. URL: https://whitepapers.axis.com/en-us/license-plate-capture
2. Ultralytics. *Multi-Object Tracking with Ultralytics YOLO* (Docs). URL: https://docs.ultralytics.com/modes/track/
3. fict-labs. *VNLP: Vietnamese license plate dataset* (GitHub). URL: https://github.com/fict-labs/VNLP
4. Trinh, T.-A.-L., Pham, T. A., & Hoang, V.-D. (2022). *Layout-invariant license plate detection and recognition*. International Conference on Multimedia Analysis and Pattern Recognition (MAPR 2022).
5. Pham, T. A. (2023). *Effective deep neural networks for license plate detection and recognition*. The Visual Computer, 39(3), 927–941.
