# Test 20 — Slides Update: Fine-tuned Detector Results

**Date**: 2026-04-21
**Build script**: `slides/build-slides.py`
**Output**: `slides/bao-ve-do-an.pptx`

---

## Slides Modified

### Slide 19 — OCR Evaluation (rewritten)

**Before**: "KẾT QUẢ PLATE DETECTION & OCR BASELINE"
- Standalone table with baseline metrics only (37.8% exact match)
- Error analysis bullets on right side

**After**: "4. ĐÁNH GIÁ OCR — TRƯỚC VÀ SAU FINE-TUNE"
- 5-column comparison table: Metric / Baseline LP_detector / Fine-tuned YOLOv8n / Cải thiện
- Rows: Detection rate (90.2% → 100.0%*), Exact match (37.8% → 70.6%), Char accuracy (53.8% → 83.8%), Avg confidence (0.835 → 0.921), Throughput
- Footer note: * 500-ảnh eval; full 3,731 đang chạy
- Green callout: "+32.7pp exact match — kết quả quan trọng nhất"

### Slide 20 — Detector Retrain Story (rebranded)

**Before**: "ĐÁNH GIÁ OCR TRÊN 3,731 ẢNH VNLP"
- Full eval comparison (50 ảnh vs 3,731 ảnh)
- Post-processing section (char mapping failed, TẮT mặc định)

**After**: "CẢI THIỆN BIỂN SỐ — FINE-TUNE YOLOv8n"
- Left: Bottleneck discovery story — GT bbox experiment → 69.8% ceiling → LP_detector is bottleneck
- Left: Training details — YOLOv8n, 29,837 VNLP images, 3 epochs, GTX 1650, mAP50 99.48%
- Right: Results table — Baseline 37.8% / GT ceiling 69.8% / Fine-tuned 70.6% ★
- Right: "Fine-tuned VƯỢT ceiling ground truth!"
- Green callout box: "+32.7pp exact match — kết quả quan trọng nhất sprint 21/04"

### Slide 23 — Stats Summary (updated numbers)

**Before** (left table):
- Unit tests: 89 (100% pass)

**After** (left table):
- Unit tests: 146 (100% pass)

**Before** (right table):
- Plate detection rate: 100%
- OCR exact match: 37.8% (3,731 ảnh)
- OCR char accuracy: 53.8% (3,731 ảnh)
- Backend test time: 1.48s
- OCR post-process tests: 33/33 pass

**After** (right table):
- Plate detection rate (finetuned): 100% (500 ảnh)
- OCR exact match (finetuned): 70.6% (500 ảnh)
- OCR char accuracy (finetuned): 83.8% (500 ảnh)
- Backend tests: 101/101 pass
- AI engine tests: 45/45 pass

### Slide 24 — Achievements (updated)

**Added** new bullet:
- ✅  Fine-tune LP_detector trên VNLP 29,837 ảnh → 70.6% exact match (+32.7pp)

**Updated** existing bullets:
- Backend: 56/56 → 101/101 tests pass
- OCR post-processing: 33/33 → 45/45 tests pass
- Font size slightly reduced (20 → 19) to fit 9 items

---

## Build Output

```
Created: G:\TTMT\datn\slides\bao-ve-do-an.pptx
Slides: 27
Size: 2320 KB
```

## Slide Count Verification

```python
from pptx import Presentation
prs = Presentation('slides/bao-ve-do-an.pptx')
print(f'Total slides: {len(prs.slides)}')
# Output: Total slides: 27
```

Result: **27 slides** — unchanged.
File modified: 2026-04-21 16:34:11

---

## Notes

- Slides 1–18 and 21–27 unchanged
- Used existing color scheme: HUST_BLUE, ACCENT_BLUE, GREEN, GRAY
- Slide 20 uses `MSO_SHAPE.ROUNDED_RECTANGLE` callout box (green fill, green border)
- 500-image numbers used for finetuned results; footnote added explaining full eval in progress
- Did NOT commit

---

## Definition of Done

- [x] Slide 19: updated with finetuned comparison
- [x] Slide 20: rebranded to Detector Retrain story
- [x] Slide 23: stats updated (tests 89→146, OCR 37.8%→70.6%)
- [x] Slide 24: achievements updated (added fine-tune, updated test counts)
- [x] .pptx rebuilt, 27 slides confirmed
- [x] Report at test_plans_and_reports/test20-slides-update.md
