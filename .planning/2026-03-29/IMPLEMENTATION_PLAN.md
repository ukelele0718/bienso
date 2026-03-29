# IMPLEMENTATION PLAN
## Kế hoạch triển khai theo hướng **train nhanh 30 phút** (model tạm cho bước tiếp theo)

**Version**: 2.0  
**Ngày cập nhật**: 2026-03-29  
**Mục tiêu sprint hiện tại**: có `best.pt` khả dụng trong ~30 phút để tích hợp nhanh vào pipeline runtime/backend/dashboard.

---

## 0) Mục tiêu ngắn hạn (P0)
Trong phiên làm việc này, ưu tiên **time-to-first-model** thay vì tối ưu chất lượng cuối:

- Có 1 model plate detector tạm thời từ Kaggle dataset.
- Tổng thời gian mục tiêu: 20–35 phút (bao gồm chuẩn bị subset + train + validate nhanh).
- Model dùng cho:
  - test detect/crop biển số,
  - test luồng event end-to-end,
  - test demo tạm cho bước tích hợp tiếp theo.

**Không dùng model này để kết luận KPI cuối kỳ.**

---

## 1) Scope lock cho sprint 30 phút
- [x] Chỉ train **plate detection** (chưa train OCR full, chưa train vehicle detector full).
- [x] Chỉ dùng nguồn `data/external/kaggle/archive` cho vòng nhanh.
- [x] Chỉ cần artifact tạm: `best.pt`, `results.csv`, sample predictions.
- [x] Chấp nhận metric trung bình, miễn inference nhìn hợp lý.
- [x] Các phase full-data/full-quality sẽ lùi sang sprint sau.

---

## 2) Cấu hình chuẩn cho run nhanh

### 2.1 Dataset
- Nguồn: `G:/TTMT/datn/data/external/kaggle/archive`
- Format: YOLOv8 (1 class `Licence-Plate`)
- Subset khuyến nghị cho 30 phút:
  - train: `320`
  - valid: `96`

### 2.2 Train profile
- model: `yolov8n.pt`
- imgsz: `512`
- batch: `8` (fallback `4` nếu OOM)
- workers: `2`
- epochs: `12` (fallback `8` nếu cần về đúng 30 phút)
- cache: `False`
- device: `0`
- plots: `False`

### 2.3 Tiêu chí dừng sớm thực dụng
- Train chạy hết không OOM.
- Có `best.pt`.
- Prediction trên sample nhìn đúng vùng biển số ở mức chấp nhận được.

---

## 3) WBS rút gọn theo thời gian thực

## Phase A — Chuẩn bị subset + sanity check (5–10 phút)
### Deliverables
- Subset dataset tách riêng cho run nhanh.
- Sanity check 20–30 ảnh.

### Checklist
- [ ] Tạo subset `train=320`, `valid=96`.
- [ ] Đảm bảo image/label khớp 1:1.
- [ ] Kiểm nhanh label không bị lỗi nghiêm trọng.

## Phase B — Train nhanh (12–22 phút)
### Deliverables
- Run train hoàn tất với profile nhanh.

### Checklist
- [ ] Chạy `yolov8n` với `imgsz=512`, `epochs=12`.
- [ ] Nếu OOM: giảm batch từ 8 xuống 4.
- [ ] Nếu vượt timebox: giảm epoch xuống 8.

## Phase C — Validate + đóng gói artifact (3–6 phút)
### Deliverables
- `best.pt`
- `results.csv`
- 10 ảnh prediction đại diện

### Checklist
- [ ] Validate nhanh trên valid subset.
- [ ] Lưu artifact vào thư mục run có timestamp.
- [ ] Ghi note ngắn: profile, thời gian, metric cơ bản, hạn chế.

---

## 4) Bảng timebox mục tiêu

| Hạng mục | Mục tiêu | Trần tối đa |
| --- | --- | --- |
| Chuẩn bị subset + kiểm nhanh | 5–8 phút | 10 phút |
| Train | 15–20 phút | 22 phút |
| Validate + lưu artifact | 3–5 phút | 6 phút |
| **Tổng** | **23–33 phút** | **35 phút** |

---

## 5) Rủi ro và phương án fallback
- **OOM VRAM** → giảm `batch=4`, giữ nguyên các tham số còn lại.
- **Train chậm quá mốc 30 phút** → giảm `epochs=8`.
- **Prediction kém** → vẫn chấp nhận làm model tạm; lên lịch full train sau.
- **Dataset drift** → chỉ dùng cho bước tích hợp tạm, chưa dùng để đánh giá cuối.

---

## 6) Cập nhật roadmap tổng thể sau sprint nhanh
Sau khi có model tạm, ưu tiên kế tiếp:
1. Gắn `best.pt` vào pipeline detect/crop runtime.
2. Kiểm thử nhanh end-to-end với backend event + dashboard.
3. Chốt lại kế hoạch full-train (Kaggle full rồi mới tới hợp nhất VNLP/nguồn khác).
4. Mở lại phase OCR và benchmark chính thức.

---

## 7) KPI hoàn thành sprint này
- [ ] Có `best.pt` dùng được tạm.
- [ ] Tổng thời gian run xấp xỉ 30 phút (±5 phút chấp nhận).
- [ ] Có minh chứng prediction hợp lý trên sample.
- [ ] Có run note để tái lập profile nhanh.

---

## 8) Ghi chú quản trị kỳ vọng
- Đây là **model tạm cho integration**.
- Không so sánh công bằng với các mô hình train đầy đủ.
- Không dùng để chốt KPI nghiệm thu dự án.
- Mọi báo cáo demo cần ghi rõ: “quick baseline 30-minute run”.
