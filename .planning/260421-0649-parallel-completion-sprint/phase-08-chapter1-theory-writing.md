# Phase 08: Chapter 1 Theory Writing

**Ưu tiên**: 🟡 Documentation
**Branch**: main (chỉ markdown, không conflict)
**Worktree**: Main
**Ước tính**: 5-6 giờ (1-2 phiên viết)

---

## Bối cảnh

Chương 1 của báo cáo chính thức cần viết thành văn bản học thuật (~12-15 trang A4).

Nguồn research đã có: [plans/reports/researcher-260414-chapter1-theory-references.md](../../plans/reports/researcher-260414-chapter1-theory-references.md) — 19 references, 5 sections đã tổng hợp.

**User là người viết chính**, AI chỉ hỗ trợ:
- Expand từng section từ outline
- Tìm thêm tài liệu nếu cần
- Review + suggest cải thiện

---

## Cấu trúc Chương 1

### 1.1. Đặt vấn đề + Tổng quan bài toán (2-3 trang)

- Bối cảnh quản lý phương tiện tại cơ sở giáo dục
- Nhu cầu thực tế tại ĐHBK Hà Nội
- Đối tượng quản lý: cán bộ, sinh viên, khách
- Mục tiêu đồ án
- Phạm vi prototype (1-2 camera, xe máy + ô tô)

### 1.2. Tổng quan ANPR/LPR (2-3 trang)

- Định nghĩa Automatic Number Plate Recognition
- Lịch sử phát triển (traditional → deep learning)
- Pipeline chuẩn: Vehicle Detection → Plate Localization → OCR
- Thách thức: lighting, angle, occlusion, motion blur, multi-row plates
- Tổng quan hệ thống thương mại vs academic research

### 1.3. Công nghệ YOLO (2-3 trang)

- Kiến trúc YOLO: single-shot detector
- Evolution: v1 → v8
- YOLOv8 Nano: kiến trúc, params, performance trên COCO
- YOLOv5 cho char-level detection: cách dùng trong OCR

### 1.4. Multi-Object Tracking với SORT (2-3 trang)

- Bài toán MOT: định nghĩa, thách thức
- Kalman Filter: state prediction + update (7-dim state vector)
- Hungarian Algorithm: optimal assignment O(n³)
- SORT = Kalman + Hungarian + IoU matching
- So sánh SORT vs DeepSORT vs ByteTrack

### 1.5. Công nghệ web cho hệ thống giám sát (2 trang)

- FastAPI: async Python, Pydantic validation
- PostgreSQL: ACID, JSON support
- React + TypeScript: component model, type safety
- Docker: containerization cho deployment
- Brief survey các hệ thống giám sát tương tự

### 1.6. Biển số xe Việt Nam (1-2 trang)

- Thông tư 58/2020/TT-BGTVT và Thông tư 24/2023/TT-BCA
- Format biển: 2-digit province + 1-2 letter series + 4-5 digits
- Các loại biển: trắng, vàng, xanh, đỏ
- 1 hàng vs 2 hàng layout

---

## Workflow

### Option A: User viết, AI review

1. User viết section theo outline
2. AI review: check học thuật, grammar, reference đầy đủ
3. AI đề xuất cải thiện câu từ
4. User finalize

### Option B: AI draft, User edit

1. AI viết draft từng section dựa trên research report
2. User đọc, sửa theo style của bản thân
3. AI tìm thêm references nếu user yêu cầu

**Đề xuất**: Option B cho section 1.2-1.5 (lý thuyết — AI biết rõ hơn), Option A cho 1.1 + 1.6 (bối cảnh — user biết rõ hơn).

---

## Files ownership

- File mới: `reports/2026-04-15/chapter1-theory.md` (hoặc user chọn path khác)
- **KHÔNG CONFLICT** với bất kỳ phase nào (chỉ markdown, khu vực riêng)

---

## Tiêu chí thành công

- [ ] 6 sections viết xong (≥12 trang A4)
- [ ] Mỗi section có ≥3 references
- [ ] Học thuật tone (tiếng Việt + English technical terms)
- [ ] Review bởi cả 2 SV + GVHD (nếu có cơ hội)

---

## Output

- File `reports/2026-04-15/chapter1-theory.md`
- Khi viết báo cáo chính thức: integrate vào file chính
- Có thể build riêng .docx bằng skill `thesis-report` sau
