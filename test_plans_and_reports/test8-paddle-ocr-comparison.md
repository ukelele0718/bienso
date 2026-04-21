# Test 8: PaddleOCR vs YOLO char-level — Comparison

**Date**: 21/04/2026
**Dataset**: VNLP test split, 500 random images (subset of 3,731)
**Hardware**: Windows 11, CPU only (paddlepaddle CPU version)
**PaddleOCR**: 3.4.1, PP-OCRv5, lang=en

---

## Results

| Metric | YOLO char-level (baseline, 3,731 full) | YOLO (500 sample) | **PaddleOCR (500)** |
|--------|----------------------------------------|-------------------|---------------------|
| Detection rate | 89.2% | ~89% | **90.2%** |
| Exact match | 37.8% | ~37.8% | **50.8%** ✅ |
| Char accuracy | 53.8% | ~54% | **62.6%** |
| Avg confidence | 0.835 | 0.82 | **0.959** |
| Throughput | 14.7 img/s GPU | 14.7 img/s GPU | 1.59 img/s CPU |

**Improvement: +13.0% exact match, +8.8% char accuracy.** PaddleOCR meaningfully beats baseline.

---

## Trade-offs

- ✅ Accuracy: +13% exact match — significant
- ✅ Higher confidence scores: 0.96 vs 0.82
- ⚠ Speed: 1.59 img/s CPU vs 14.7 img/s YOLO GPU — ~9x slower on CPU
- ⚠ Install size: paddlepaddle + paddleocr ≈ 250 MB
- Install complexity: Windows DLL ordering issues documented in `plate_ocr_paddle.py` docstring

---

## Error pattern analysis

Same dominant pattern as YOLO baseline: **missing "36" prefix** on 10+ sample errors:
```
GT=36C07119 → PRED=C07119    (missed 2-char prefix)
GT=36A00715 → PRED=36A007    (truncated suffix)
GT=36C01897 → PRED=01897     (missed 3 chars)
GT=36A42196 → PRED=42196     (missed prefix)
```

**→ Confirms Phase 01 finding**: LP_detector bbox is too tight → cuts off plate edges. Both YOLO and PaddleOCR feed on the same bad crops.

PaddleOCR still wins because it's more robust to distorted/partial crops, but the ceiling is capped by plate detector quality.

---

## Decision

**Recommendation: MERGE** PaddleOCR as optional backend, not replace YOLO.

Reasons:
1. +13% accuracy is too significant to ignore
2. Throughput 1.59 img/s is acceptable for non-realtime use cases (batch processing, offline eval)
3. Keep YOLO char-level for realtime pipeline (14.7 img/s GPU requirement)
4. Offer `OCR_BACKEND` config flag: `yolo` (default) | `paddle`

**Bigger win**: Combining PaddleOCR + better LP_detector (Phase 01's GT-bbox experiment reached 69.8%) likely reaches 75-80% exact match.

---

## Next Steps

1. Add `OCR_BACKEND` config flag in `apps/ai_engine/src/config.py`
2. Wire pipeline to swap backend based on flag
3. Run full 3,731-image eval on PaddleOCR for final numbers
4. Retrain LP_detector on VNLP train split (29,837 images) — **biggest impact** (84% of accuracy gap per Phase 01)
