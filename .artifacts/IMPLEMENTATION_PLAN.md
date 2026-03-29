# IMPLEMENTATION PLAN
## Kế hoạch triển khai chi tiết (scope 1 camera, typed-first)

**Version**: 2.1  
**Ngày cập nhật**: 2026-03-27  
**Phạm vi**: 1 luồng camera, 2 kịch bản cổng, có rule số dư/thu phí theo lượt

---

## 0) Mục tiêu triển khai
Triển khai prototype end-to-end theo luồng bắt buộc:

`Video input` → `Detect vehicle` → `Track` → `Count in/out` → `Detect plate` → `OCR` → `Post-process` → `Send event` → `Dashboard`

Bổ sung nghiệp vụ tài chính:
- Khởi tạo số dư mỗi người/phương tiện: **100,000 VND**.
- Mỗi lượt vào hoặc ra trừ: **2,000 VND**.
- **Cho phép số dư âm**.

---

## 1) Scope lock checklist
- [x] Chỉ xử lý 1 stream camera.
- [x] Cổng sinh viên: xe máy.
- [x] Cổng giảng viên: xe máy + ô tô.
- [x] Dashboard có tra cứu biển số theo khoảng thời gian.
- [x] Áp dụng rule tài chính 100,000 khởi tạo / -2,000 mỗi lượt / cho phép âm.

---

## 2) Work Breakdown Structure (WBS)

## Phase 1 — Finalize PRD + data/architecture (Tuần 1)
### Deliverables
- PRD 2.1 đã chốt
- Kiến trúc single-stream
- Data contract event + transaction

### Checklist
- [x] Chốt schema event và schema transaction.
- [x] Chốt typed stack và quality gates.
- [x] Chốt KPI cho counting, OCR, latency, finance rule.

---

## Phase 2 — Public data setup (Tuần 1-2)
### Deliverables
- Bộ dữ liệu công khai biển số Việt Nam đã tải
- Data manifest đầy đủ nguồn/citation

### Checklist
- [x] Tạo thư mục `data/raw`, `data/external`, `data/processed`.
- [x] Tải VNLP (repo + drive link trong README).
- [x] (Tùy chọn) Bổ sung Kaggle/Roboflow.
- [ ] Chuẩn hóa annotation về YOLO/COCO.
- [x] Tách train/val/test.
- [x] Lưu `dataset_manifest.json` (source URL, số mẫu, giấy phép/ghi chú sử dụng).

---

## Phase 3 — Detect/Track/Count baseline (Tuần 3-4)
### Deliverables
- Module detect/track/count chạy với 1 stream
- Báo cáo sai số đếm v1
- File cấu hình line/zone cho 2 kịch bản cổng

### Checklist
- [ ] Ingest video 1 stream (file/RTSP) + fallback khi mất kết nối.
- [ ] Detect `motorbike`, `car` + ghi log confidence.
- [ ] Tích hợp tracker (ByteTrack/BoT-SORT) + cấu hình `track_buffer`.
- [ ] Cấu hình line/zone cho:
  - [ ] Cổng sinh viên (xe máy)
  - [ ] Cổng giảng viên (xe máy + ô tô)
- [ ] Luật đếm in/out theo vector hướng chuyển động.
- [ ] Chống đếm trùng (debounce theo track_id + time window).
- [ ] Ghi event tối thiểu: `timestamp, direction, vehicle_type, track_id`.
- [ ] Báo cáo sai số đếm theo từng kịch bản cổng.

---

## Phase 4 — LPR/OCR + robustification (Tuần 5-7)
### Deliverables
- Module biển số VN hoạt động
- Báo cáo OCR accuracy + error analysis
- Bộ regex + post-process cho biển số VN

### Checklist
- [ ] Plate detection (bbox) + crop ảnh biển số.
- [ ] Chọn frame tốt nhất trước OCR (sharpness + confidence).
- [ ] Deblur/căn chỉnh khi cần.
- [ ] OCR + hậu xử lý regex biển số VN (1 hàng/2 hàng).
- [ ] Hiệu chỉnh phối cảnh/rotation cho biển số nghiêng.
- [ ] Chuẩn hóa ký tự dễ nhầm (O/0, I/1, B/8, S/5).
- [ ] Đánh giá OCR theo điều kiện ngày/đêm/chói/mưa nếu có dữ liệu.
- [ ] Báo cáo lỗi phổ biến + đề xuất cải thiện dữ liệu.

---

## Phase 5 — Backend + DB + Finance rule (Tuần 8-9)
### Deliverables
- API event/search/stats
- Module tài chính theo lượt

### Checklist
- [x] Tạo bảng `accounts`, `transactions`.
- [x] Khởi tạo số dư mặc định 100,000 VND cho account mới.
- [x] Khi có event in/out: ghi transaction -2,000 VND.
- [x] Cho phép balance âm.
- [x] API tra cứu lịch sử giao dịch theo biển số/khoảng thời gian.
- [x] Audit log thao tác truy cập dữ liệu biển số và tài chính.

---

## Phase 6 — Dashboard TypeScript (Tuần 10-11)
### Deliverables
- Dashboard realtime + search + traffic stats + account balance

### Checklist
- [x] Realtime in/out counters.
- [x] Danh sách biển số gần nhất.
- [x] Tra cứu theo biển số + khoảng thời gian.
- [x] Biểu đồ lưu lượng giờ/ngày.
- [x] Hiển thị OCR success rate.
- [x] Hiển thị balance hiện tại + lịch sử trừ tiền.

---

## Phase 7 — Integration & typed QA (Tuần 12)
### Deliverables
- Bản tích hợp hoàn chỉnh
- Báo cáo KPI + test report

### Checklist
- [x] End-to-end test 2 kịch bản cổng.
- [x] Verify luồng tài chính theo event.
- [x] Verify tra cứu theo biển số/time-range.
- [ ] Type-check pass:
  - [ ] Python: `mypy/pyright`
  - [x] TypeScript: `tsc --noEmit`
- [x] Lint + integration tests pass.

---

## 3) Thách thức & hướng giải quyết (chốt theo yêu cầu)
- **Luồng xe hỗn hợp trong cùng khung hình**: cần tập dữ liệu đa dạng và luật đếm ổn định.  
  - [ ] Bổ sung data nhiều mật độ xe
  - [ ] Tối ưu line/zone + debounce

- **Điều kiện ngày/đêm, mưa, ngược sáng**: cần tăng cường dữ liệu hoặc tiền xử lý phù hợp.  
  - [ ] Augmentation cho low-light/glare
  - [ ] Tiền xử lý contrast/denoise

- **Biển số mờ, bẩn, che khuất**: cần bước chọn frame tốt nhất, deblur/căn chỉnh và hậu xử lý.  
  - [ ] Best-frame selector
  - [ ] Deblur và adaptive sharpening
  - [ ] Post-process regex + confidence threshold

- **Che khuất giữa nhiều xe**: cần tracking tốt để tránh đếm sai và chọn đúng ảnh biển số.  
  - [ ] Tinh chỉnh tracker thresholds
  - [ ] Track persistence + re-ID nếu cần

- **Góc nghiêng camera**: cần hiệu chỉnh phối cảnh/rotation trước OCR.  
  - [ ] Perspective transform trước OCR
  - [ ] Rotation normalization

---

## 4) Typed Quality Gate (bắt buộc)
- [x] 100% public function có type annotations.
- [x] API contracts typed bằng Pydantic + TS types.
- [x] Không merge nếu type-check fail.

---

## 5) KPI nghiệm thu
- [x] End-to-end chạy ổn định 1 camera.
- [ ] Sai số đếm trong ngưỡng mục tiêu.
- [ ] OCR accuracy đạt mục tiêu prototype.
- [x] Rule 100,000 / -2,000 / cho phép âm chạy đúng toàn bộ test cases.
- [x] Dashboard search theo biển số + thời gian chạy đúng.
- [x] Rule thanh chắn hoạt động đúng:
  - [x] xe đã đăng ký vào: mở tự động
  - [x] xe lạ vào: tự động đăng ký tạm và mở
  - [x] xe đăng ký tạm ra: giữ chặn, yêu cầu xác thực, xác thực xong mới mở

---

## 6) Tài liệu tham khảo (trích nguồn đầy đủ)
1. Axis Communications. *License plate capture (White Paper)*, Dec 2024. URL: https://whitepapers.axis.com/en-us/license-plate-capture
2. Ultralytics Docs. *Multi-Object Tracking with Ultralytics YOLO*. URL: https://docs.ultralytics.com/modes/track/
3. fict-labs. *VNLP: Vietnamese license plate dataset* (GitHub). URL: https://github.com/fict-labs/VNLP
4. Trinh, T.-A.-L., Pham, T. A., Hoang, V.-D. (2022). *Layout-invariant license plate detection and recognition*. MAPR 2022.
5. Pham, T. A. (2023). *Effective deep neural networks for license plate detection and recognition*. The Visual Computer, 39(3), 927–941.
