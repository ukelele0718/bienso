# Phase 07: Hoàn thiện Báo cáo Chính thức

**Ưu tiên**: 🟡 Trung bình — tổng hợp tất cả kết quả từ Phase 01-06
**Trạng thái**: ⬜ Pending
**Phụ thuộc**: Phase 01, 02, 03, 04, 05, 06
**Ước tính**: ~3 giờ

---

## Bối cảnh

Báo cáo tiến độ (.md + .docx) đã có cấu trúc 5 chương hoàn chỉnh.
Cần update với kết quả thực tế từ các phase trước + điền thông tin còn thiếu.

---

## Việc cần làm

### 1. Cập nhật số liệu thực nghiệm (Ch.4)

Sau Phase 01 + 03:
- Update bảng OCR baseline: exact match, char accuracy (trước/sau post-processing)
- Update bảng eval 3,731 ảnh (kết quả mới)
- Thêm phân tích lỗi OCR chi tiết (confusion matrix ký tự)
- Update E2E video test nếu chạy lại

### 2. Cập nhật trạng thái tính năng (Ch.3)

Sau Phase 01:
- Mục 3.2.3 (Hậu xử lý): ⚠ → ✅ (regex + char mapping đã implement)

Sau Phase 02:
- Thêm mô tả snapshot saving vào Ch.3.2 hoặc Ch.3.3

Sau Phase 04:
- Mục 3.3.2 (Dashboard): Cập nhật trạng thái từng tính năng (❓ → ✅ hoặc ⚠)

### 3. Thêm hình ảnh mới

Sau Phase 05:
- Cập nhật Hình 9, 10 (dashboard screenshots)
- Thêm Hình 12, 13 nếu có (account detail, snapshot)

### 4. Điền thông tin phân công công việc (Mục 8)

Bảng 12 (phân công viết báo cáo) và Bảng 13 (phân công code) hiện **trống cột "Người viết/làm"**.

Cần điền:
- Hà Văn Quang — MSSV: 20210718
- Nguyễn Hữu Cần — MSSV: 20223882

### 5. Cập nhật bảng tiến độ 16 tuần (Mục 1)

Bảng 1 — update trạng thái các tuần:
- Tuần 5-6 (Tracking): SORT xong, đếm xe = config-based (không cần line-crossing)
- Tuần 7-8 (OCR): Sau Phase 01 → update %
- Tuần 9-10 (Hậu xử lý OCR): Sau Phase 01+03 → update %
- Tuần 13-14 (Dashboard): Sau Phase 04 → update %
- Tuần 15 (Tích hợp): Sau Phase 02 → update %

### 6. Cập nhật bảng thống kê tổng hợp (Mục 6)

Bảng 9 — update nếu có thay đổi:
- OCR exact match (sau post-processing)
- Tổng dòng code (nếu thêm code mới)
- Git commits count

### 7. Cập nhật kế hoạch giai đoạn tiếp theo (Mục 7)

Đánh dấu các việc đã hoàn thành từ Bảng 10, 11:
- ✅ Full OCR evaluation
- ✅ Regex hậu xử lý
- ✅ Char mapping
- ✅ Screenshot dashboard
- Còn lại: đếm xe, benchmark GPU, video test thêm, lý thuyết

### 8. Rebuild .docx

Sau khi update .md xong:
- Chạy `node reports/2026-04-13/docx/build-report.js` để tạo .docx mới
- Verify: mở .docx, kiểm tra format, hình ảnh, bảng

---

## Files cần sửa

| File | Hành động |
|------|----------|
| `reports/2026-04-13/bao-cao-dinh-ky-tien-do.md` | Update toàn bộ nội dung |
| `reports/2026-04-13/docx/build-report.js` | Sửa nếu thêm hình mới |
| `reports/2026-04-13/images/` | Thêm hình mới từ Phase 05 |

---

## Mâu thuẫn cần giải quyết trong báo cáo

1. **Đếm xe**: Mục 3.1.3 ghi "❌ Chưa triển khai" + kế hoạch line-crossing, nhưng Mục 9.3 giải thích camera direction-based (không cần line-crossing). → Cần thống nhất: nếu thiết kế là config-based thì 3.1.3 nên ghi "✅ Theo thiết kế config-based" hoặc rõ ràng hơn.

2. **Duplicate events**: Lần test 2 (101 frames) vẫn có 2 events cho cùng biển 36H82613 do SORT tạo track mới. → Cần ghi rõ đây là known limitation và hướng fix (deduplicate by plate_text).

---

## Tiêu chí hoàn thành

- [ ] Tất cả số liệu trong báo cáo khớp với kết quả test thực tế
- [ ] Không còn trạng thái ❓ (thay bằng ✅, ⚠, hoặc ❌ kèm lý do)
- [ ] Bảng phân công điền đầy đủ tên
- [ ] .docx build thành công, format đúng
- [ ] Mâu thuẫn đếm xe / duplicate events được giải quyết rõ ràng
