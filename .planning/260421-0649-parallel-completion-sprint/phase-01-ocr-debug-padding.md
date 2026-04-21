# Phase 01: OCR Debug — Root Cause Analysis

**Ưu tiên**: 🔴 Critical
**Branch**: `experiment/ocr-padding`
**Worktree**: Main
**Ước tính**: 2-3 giờ

---

## Bối cảnh

OCR hiện đạt 37.8% exact match trên 3,731 ảnh VNLP. Literature cho ALPR thường ≥95%. Có dấu hiệu bất thường — có thể fix bằng cách điều tra root cause, không cần đổi model.

Báo cáo lỗi hiện tại (từ test6):
- Thiếu ký tự: ~35% (vd: GT=36C07119, pred=C07119 → miss '36')
- Thừa ký tự: ~15%
- Nhầm hình dáng: ~25%
- Không detect biển: ~11%

Hypothesis: **Crop biển số không đủ padding** → OCR miss ký tự ở rìa.

---

## Yêu cầu thử nghiệm

### Thử nghiệm 1: Tăng padding crop

File `apps/ai_engine/src/pipeline.py` — hàm crop plate (tìm trong pipeline):
```python
# Thêm padding 10-15% khi crop plate từ frame
pad_x = int((x2 - x1) * 0.1)
pad_y = int((y2 - y1) * 0.15)
crop = frame[max(0, y1-pad_y):y2+pad_y, max(0, x1-pad_x):x2+pad_x]
```

Nhưng **quan trọng hơn**: script eval `scripts/eval-ocr-baseline.py` cũng crop biển — tăng padding ở đó.

### Thử nghiệm 2: Kiểm tra ground truth

Parse filename `4_2780_1_36C07119_126_179_491_245.jpg`:
- parts[3] = "36C07119" là plate text
- parts[4-7] = bbox (126, 179, 491, 245)

Verify:
1. Một vài ảnh: mở ảnh, crop theo bbox, kiểm tra có đúng vị trí biển không
2. Plate text có đúng với biển trong ảnh không (visual check)

### Thử nghiệm 3: Confidence threshold

Hiện tại OCR_CONFIDENCE = 0.3 (có thể quá thấp hoặc quá cao). Thử 0.25, 0.35 xem có thay đổi không.

### Thử nghiệm 4: Use ground truth bbox thay vì detect

Thay vì dùng LP_detector, dùng bbox từ filename → OCR trực tiếp. Nếu OCR accuracy vọt lên >80% → lỗi ở plate detector, không phải OCR. Đó là big insight.

---

## Workflow

1. Tạo branch `experiment/ocr-padding` từ main
2. Clone eval script → `scripts/eval-ocr-padding-v1.py`, `v2.py`, `v3.py` cho từng thử nghiệm
3. Chạy từng thử nghiệm → save JSON kết quả riêng vào `data/processed/eval-padding-v1.json` etc
4. Tổng hợp bảng so sánh
5. Nếu cải thiện → merge vào main + update report
6. Nếu không cải thiện → ghi lessons learned, giữ branch, không merge

---

## Files ownership

- `scripts/eval-ocr-padding-*.py` (3 script riêng)
- `data/processed/eval-padding-v*.json`
- **KHÔNG SỬA** `apps/ai_engine/src/` trong phase này (chỉ thử nghiệm qua scripts)
- Test report: `test_plans_and_reports/test7-ocr-padding-debug.md`

---

## Tiêu chí thành công

Ít nhất 1 thử nghiệm cho accuracy:
- Baseline: 37.8% exact
- Target: ≥50% exact (tăng 12%)
- Stretch: ≥70% exact

Nếu đạt target → merge logic vào `plate_detector.py` hoặc `pipeline.py`.
Nếu thử nghiệm 4 (GT bbox) đạt >70% → vấn đề ở plate detector → Phase 02 (PaddleOCR) có thể giải quyết luôn.

---

## Output

- Report tại `test_plans_and_reports/test7-ocr-padding-debug.md`
- Ít nhất 1 JSON file với kết quả eval
- Nếu positive: commit code change vào branch + recommend merge
