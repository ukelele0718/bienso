# Product Requirements Document (PRD)
## Sprint mục tiêu: có model tạm sau ~30 phút train

**Phiên bản**: 1.0 (planning sprint)  
**Ngày cập nhật**: 2026-03-29  
**Trạng thái**: Ready for quick execution

---

## 1) Bối cảnh và mục tiêu sprint
Dự án hiện đã có nền backend/dashboard tương đối hoàn chỉnh, nhưng cần một model detector tạm để mở khóa bước tích hợp tiếp theo.

Mục tiêu sprint này:
- Tạo nhanh một plate detector baseline trong ~30 phút.
- Dùng model này cho test pipeline runtime/event/dashboard.
- Ưu tiên tốc độ có kết quả hơn tối ưu độ chính xác.

---

## 2) Problem statement
Ở thời điểm hiện tại, thiếu model thực tế để:
- chạy thử detect/crop biển số end-to-end,
- kiểm tra luồng gửi event và hiển thị dashboard,
- giảm rủi ro tích hợp ở giai đoạn sau.

Nếu tiếp tục chờ full-train/full-data, tiến độ tích hợp sẽ bị chậm.

---

## 3) Scope sprint 30 phút

### 3.1 In-scope
- Train nhanh **plate detector** từ Kaggle dataset đã có sẵn.
- Dùng subset nhỏ để đảm bảo hoàn thành trong timebox.
- Xuất artifact tối thiểu:
  - `best.pt`
  - `results.csv`
  - sample prediction images
- Ghi run note ngắn để tái lập.

### 3.2 Out-of-scope
- Full-train chất lượng cao trên toàn bộ data.
- OCR fine-tuning.
- Vehicle detector full training.
- Chốt KPI chất lượng cuối dự án.

---

## 4) Dataset & train profile chuẩn

### Dataset
- Source: `G:/TTMT/datn/data/external/kaggle/archive`
- Format: YOLOv8, 1 class `Licence-Plate`
- Subset target:
  - train: 320 ảnh
  - valid: 96 ảnh

### Train profile
- model: `yolov8n.pt`
- imgsz: 512
- batch: 8 (fallback 4)
- workers: 2
- epochs: 12 (fallback 8)
- cache: False
- device: GPU 0

---

## 5) Functional requirements (sprint-specific)
- FR-01: Có thể tạo subset train/valid nhỏ từ Kaggle source trong vài phút.
- FR-02: Train chạy hết mà không OOM trong cấu hình fallback.
- FR-03: Sinh ra `best.pt` và logs metrics cơ bản.
- FR-04: Có thể chạy prediction sample để kiểm tra nhanh bằng mắt.
- FR-05: Artifact được lưu có tổ chức, dễ dùng cho bước tích hợp tiếp theo.

---

## 6) Non-functional requirements
- NFR-01: Tổng thời gian execution mục tiêu 23–33 phút, trần 35 phút.
- NFR-02: Quy trình dễ tái lập với profile rõ ràng.
- NFR-03: Không gây thay đổi phá vỡ các module backend/dashboard hiện có.

---

## 7) Success criteria
Sprint được xem là thành công khi đạt đủ:
1. Có file `best.pt` từ run nhanh.
2. Train hoàn tất không lỗi nghiêm trọng/OOM (hoặc đã fallback hợp lệ).
3. Prediction sample cho thấy box bám biển số ở mức chấp nhận để demo tích hợp.
4. Có run note (config + thời gian + metric cơ bản + giới hạn).

---

## 8) Known limitations (bắt buộc ghi rõ)
- Model sprint này chỉ là quick baseline.
- Metric từ subset nhỏ có độ tin cậy hạn chế.
- Không dùng kết quả này để nghiệm thu cuối cùng.
- Cần full-train và benchmark lại ở sprint kế tiếp.

---

## 9) Kế hoạch tiếp nối ngay sau sprint
1. Gắn `best.pt` vào luồng detect/crop thực tế.
2. Chạy integration test với backend event + dashboard.
3. Mở sprint full-train Kaggle đầy đủ.
4. Sau đó mới hợp nhất nguồn lớn hơn (VNLP/khác) và OCR tuning.

---

## 10) Decision log
- Quyết định ưu tiên `time-to-first-model` thay vì quality tối đa.
- Chọn `yolov8n` và subset nhỏ để bám sát giới hạn GTX 1650 4GB.
- Chấp nhận đánh đổi chất lượng để giảm rủi ro tiến độ tích hợp.
