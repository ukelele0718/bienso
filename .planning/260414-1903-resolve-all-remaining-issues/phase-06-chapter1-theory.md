# Phase 06: Viết Phần Lý Thuyết (Chương 1)

**Ưu tiên**: 🟡 Trung bình — bắt buộc cho báo cáo chính thức
**Trạng thái**: ⬜ Pending
**Ước tính**: ~5 giờ (nghiên cứu + viết)

---

## Bối cảnh

Báo cáo mục 2 (Chương 1) ghi:
> Trạng thái: Đề cương đã có, cần viết thành văn bản chính thức.

Chương 1 gộp từ Ch.1 (Mở đầu) + Ch.2 (Tổng quan bài toán và công nghệ) trong đề cương gốc.

Đã xác định:
- ✅ Bối cảnh bài toán tại ĐH Bách khoa Hà Nội
- ✅ Đối tượng quản lý (cán bộ, sinh viên, khách)
- ✅ Phạm vi prototype (1-2 camera, xe máy + ô tô)
- ✅ Hướng ứng dụng: kiểm soát ra/vào + bãi đỗ thông minh

Còn thiếu: **Phần lý thuyết tổng quan** — tìm paper/tài liệu cho YOLO, SORT, ANPR/LPR.

---

## Nội dung cần viết

### 1.1. Tổng quan bài toán quản lý phương tiện
- Bối cảnh thực tế tại cơ sở giáo dục (ĐHBK HN)
- Nhu cầu: kiểm soát ra/vào, quản lý bãi đỗ, thống kê lưu lượng
- Đối tượng: cán bộ, sinh viên, khách
- Phạm vi prototype

### 1.2. Tổng quan công nghệ nhận dạng biển số xe (ANPR/LPR)
- Lịch sử phát triển ANPR
- Pipeline chuẩn: Vehicle Detection → Plate Detection → Character Segmentation → OCR
- Các approach: traditional (Haar, HOG, SVM) vs deep learning (YOLO, SSD, Faster R-CNN)
- So sánh ưu/nhược điểm

### 1.3. Lý thuyết YOLO (You Only Look Once)
- Kiến trúc cơ bản YOLO: single-shot detector
- Các phiên bản: YOLOv1 → YOLOv8
- YOLOv8 Nano: kiến trúc, ưu điểm (nhẹ, nhanh, phù hợp edge)
- YOLOv5 cho plate detection và OCR: char-level detection approach

### 1.4. Lý thuyết SORT Tracker
- Multi-Object Tracking (MOT) overview
- Kalman Filter: mô hình trạng thái 7 chiều
- Hungarian Algorithm: bài toán gán tối ưu
- SORT = Kalman + Hungarian + IoU matching

### 1.5. Công nghệ web cho hệ thống giám sát
- FastAPI (Python): async, auto-docs, Pydantic validation
- PostgreSQL: ACID, JSON support
- React + TypeScript: component-based UI
- Docker: containerization cho deployment

---

## Tài liệu tham khảo chính

Đã có sẵn trong báo cáo [1]-[33], đặc biệt:
- [1] YOLO original (Redmon 2016)
- [3] YOLOv8 (Jocher 2023)
- [4] YOLOv5 (Jocher 2020)
- [5] SORT (Bewley 2016)
- [6] Kalman Filter (Kalman 1960)
- [7] Hungarian Method (Kuhn 1955)
- [8] ALPR Survey (Du 2013)
- [10] LPR Survey (Anagnostopoulos 2008)

Cần tìm thêm:
- Vietnamese plate format characteristics paper
- OCR char-level detection approach references
- Edge deployment / embedded AI references

---

## Files cần tạo/sửa

| File | Hành động |
|------|----------|
| Báo cáo chính thức (viết riêng) | Viết nội dung Ch.1 đầy đủ |
| `reports/2026-04-13/bao-cao-dinh-ky-tien-do.md` | Có thể update outline Ch.1 |

---

## Lưu ý

- Đây là phần **người viết** (Quang hoặc Cần), AI hỗ trợ tìm tài liệu + outline
- Nội dung phải viết bằng tiếng Việt, giọng học thuật
- Mỗi mục ~2-3 trang A4 (tổng Ch.1 khoảng 12-15 trang)
- Format: Times New Roman 13pt, line spacing 1.15 (theo ref docx)

---

## Tiêu chí hoàn thành

- [ ] Outline chi tiết Ch.1 (5 mục con) được duyệt
- [ ] Mỗi mục có ít nhất 3 tài liệu tham khảo
- [ ] Nội dung viết xong, review bởi cả 2 thành viên
- [ ] Tích hợp vào báo cáo chính thức
