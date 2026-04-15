# Phase 03: Full OCR Evaluation (3,731+ ảnh)

**Ưu tiên**: 🔴 Cao — số liệu thực nghiệm Ch.4 cần đánh giá trên tập lớn
**Trạng thái**: ⬜ Pending
**Phụ thuộc**: Phase 01 (OCR post-processing) hoàn thành trước
**Ước tính**: ~1 giờ (5 phút chạy script + phân tích kết quả)

---

## Bối cảnh

Hiện tại chỉ eval trên 50 ảnh random:
- Detection rate: 96.0%
- Exact match: 33.3%
- Char accuracy: 51.0%

Script eval đã có: `scripts/eval-ocr-baseline.py` (263 dòng)
Dataset VNLP: 37,297 ảnh (one_row: 19,086 | two_rows: 12,618 | two_rows_xe_may: 5,593)

Mục tiêu: Eval trên ít nhất 3,731 ảnh (10% sample) với post-processing từ Phase 01.

---

## Yêu cầu

### 1. Chạy eval TRƯỚC Phase 01 (baseline mới)

```bash
python scripts/eval-ocr-baseline.py --sample 3731 --output reports/eval-3731-before-postprocess.json
```

### 2. Chạy eval SAU Phase 01 (có post-processing)

```bash
python scripts/eval-ocr-baseline.py --sample 3731 --postprocess --output reports/eval-3731-after-postprocess.json
```

### 3. So sánh kết quả

Tạo bảng so sánh before/after:

| Metric | 50 ảnh (cũ) | 3,731 ảnh (trước) | 3,731 ảnh (sau) |
|--------|-------------|-------------------|-----------------|
| Detection rate | 96.0% | ? | ? |
| Exact match | 33.3% | ? | ? |
| Char accuracy | 51.0% | ? | ? |

### 4. Phân tích lỗi chi tiết

Từ kết quả, phân loại lỗi:
- Thừa/thiếu ký tự
- Nhầm ký tự tương tự
- Biển mờ/nghiêng/che khuất
- 1 hàng vs 2 hàng accuracy

### 5. Update eval script nếu cần

**File**: `scripts/eval-ocr-baseline.py`
- Thêm flag `--postprocess` để bật char mapping + regex
- Thêm phân loại lỗi tự động
- Export confusion matrix cho ký tự

---

## Files cần sửa

| File | Hành động |
|------|----------|
| `scripts/eval-ocr-baseline.py` | Thêm --postprocess flag, phân loại lỗi |
| Tạo mới: `reports/eval-3731-results.md` | Kết quả eval chi tiết |

---

## Tiêu chí hoàn thành

- [ ] Eval chạy trên ≥3,731 ảnh không crash
- [ ] Có kết quả before/after post-processing
- [ ] Exact match sau post-processing > baseline 33.3%
- [ ] Phân loại lỗi OCR có thống kê rõ ràng
- [ ] Kết quả được ghi vào báo cáo Ch.4

---

## Lưu ý

⚠ **Thời gian chạy**: 3,731 ảnh × ~65ms/ảnh = ~4 phút (CPU). KHÔNG cần GPU.
Nếu chạy toàn bộ 37,297 ảnh = ~40 phút → chỉ chạy nếu có thời gian.
