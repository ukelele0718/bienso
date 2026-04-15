# Phase 01: OCR Post-processing (Regex + Char Mapping)

**Ưu tiên**: 🔴 Cao — ảnh hưởng trực tiếp nội dung Ch.3.2 và kết quả eval Ch.4
**Trạng thái**: ⬜ Pending
**Ước tính**: ~2 giờ

---

## Bối cảnh

Hiện tại `normalize_plate_text()` trong `apps/backend/app/crud.py:21-23` chỉ:
- Strip ký tự không phải chữ/số: `re.sub(r"[^A-Za-z0-9]", "", text)`
- Uppercase toàn bộ

Báo cáo mục 3.2.3 ghi rõ **chưa có**:
- Regex match format biển VN
- Bảng chuyển đổi ký tự dễ nhầm (0↔O, 1↔I, 5↔S, 8↔B)

OCR exact match hiện tại: **33.3%** — cải thiện post-processing có thể nâng lên 50-60%.

---

## Yêu cầu

### 1. Char Mapping (ký tự dễ nhầm)

Thêm hàm `apply_char_mapping()` vào AI Engine (trước khi gửi event về backend).

**Vị trí**: `apps/ai_engine/src/plate_ocr.py` — sau `_cluster_and_read()`

**Logic**:
- Vị trí số (position-aware): ở vị trí kỳ vọng là số → map O→0, I→1, S→5, B→8
- Vị trí chữ: ở vị trí kỳ vọng là chữ → map 0→O, 1→I, 5→S, 8→B
- Format biển VN tham chiếu (Thông tư 58/2020):
  - 1 hàng: `XXY-XXXXX` (2 số + 1 chữ + 5 số) hoặc `XXY-XXX.XX`
  - 2 hàng: `XXY` / `XXXXX` hoặc `XXY` / `XXX.XX`
  - X = số, Y = chữ cái tỉnh/thành

**Bảng mapping**:
```python
CHAR_TO_DIGIT = {"O": "0", "I": "1", "S": "5", "B": "8", "G": "6", "Z": "2", "D": "0"}
DIGIT_TO_CHAR = {"0": "O", "1": "I", "5": "S", "8": "B", "6": "G", "2": "Z"}
```

### 2. Regex Validation

Thêm hàm `validate_vn_plate_format()` — kiểm tra kết quả OCR có khớp format biển VN không.

**Patterns** (sau khi strip dấu):
```python
VN_PLATE_PATTERNS = [
    r"^\d{2}[A-Z]\d{5}$",        # 29A12345 (1 hàng, 5 số)
    r"^\d{2}[A-Z]\d{4}$",         # 29A1234 (1 hàng, 4 số — cũ)
    r"^\d{2}[A-Z]{2}\d{5}$",      # 29AB12345 (biển mới 2022)
    r"^\d{2}[A-Z]{2}\d{4}$",      # 29AB1234
    r"^\d{2}[A-Z]\d{3}[A-Z]{2}$", # 14K117XX → ít gặp
]
```

**Output**: `(plate_text, confidence_adjusted, is_valid_format: bool)`

### 3. Tích hợp vào pipeline

**File**: `apps/ai_engine/src/pipeline.py`
- Sau khi OCR trả kết quả, gọi `apply_char_mapping()` → `validate_vn_plate_format()`
- Gửi `is_valid_format` kèm event về backend (field mới hoặc metadata)

### 4. Update backend normalize

**File**: `apps/backend/app/crud.py`
- Giữ nguyên `normalize_plate_text()` (strip + upper) — đây là tầng cuối
- Thêm field `ocr_post_processed: bool` vào PlateRead nếu cần track

---

## Files cần sửa

| File | Hành động |
|------|----------|
| `apps/ai_engine/src/plate_ocr.py` | Thêm `apply_char_mapping()`, `validate_vn_plate_format()` |
| `apps/ai_engine/src/pipeline.py` | Tích hợp post-processing sau OCR |
| `apps/ai_engine/src/config.py` | Thêm config `ENABLE_CHAR_MAPPING`, `ENABLE_REGEX_VALIDATE` |
| `apps/backend/tests/test_normalize.py` | Thêm test cho char mapping edge cases |

---

## Tiêu chí hoàn thành

- [ ] `apply_char_mapping()` hoạt động đúng với 10+ test cases
- [ ] `validate_vn_plate_format()` match đúng các format biển VN
- [ ] Pipeline gọi post-processing trước khi gửi event
- [ ] Chạy lại eval 50 ảnh baseline → exact match tăng (mục tiêu >45%)
- [ ] Backend tests vẫn pass (56/56)
- [ ] Không break E2E flow hiện tại

---

## Rủi ro

- Char mapping quá aggressive có thể sửa sai chữ đúng → cần position-aware
- Regex quá strict có thể reject biển hợp lệ nhưng OCR miss 1 ký tự → chỉ dùng validate, không reject
