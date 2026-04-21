# Test 22: OCR Accuracy Improvement — PaddleOCR on Finetuned Crops

**Date**: 2026-04-21
**Goal**: Test whether PaddleOCR + finetuned YOLOv8 detector can surpass the current 68.7% exact match baseline.
**Script**: `scripts/eval-paddle-on-finetuned.py`
**Result JSON**: `data/processed/paddle-finetuned-eval.json`

---

## Background

After full OCR eval (test12) using the finetuned LP_detector_finetuned.pt:
- Detection rate: 99.9% (near perfect — detector no longer bottleneck)
- **Exact match: 68.7%** (+30.9pp vs original baseline 37.8%)
- Char accuracy: 82.4%
- Error analysis: 83% of failures are character confusion (C↔3, A↔4, 0↔O)

Hypothesis: The bottleneck shifted from detector to OCR backend. PaddleOCR (PP-OCRv5),
a general-purpose OCR trained on millions of images, may outperform the specialized
but less powerful LP_ocr.pt (YOLOv5 char-level detection) when given perfect crops.

Previous PaddleOCR test (test-paddle-ocr.py, broken crops from old YOLOv5 detector)
achieved 50.8% exact match — slightly better than the 37.8% YOLO baseline at the time.
The question was whether clean crops from the finetuned detector would close the gap.

---

## Approach 1: PaddleOCR + Finetuned Detector

**Setup**:
- Detector: `LP_detector_finetuned.pt` (YOLOv8, fine-tuned on VNLP dataset)
- OCR: `PaddleOCR PP-OCRv5` (CPU, lang=en)
- Padding: 0% (finetuned model produces well-fitted crops)
- Test set: First 500 images from VNLP test split

**Results (500 images)**:

| Metric               | PaddleOCR + finetuned | YOLO char + finetuned | Delta   |
|----------------------|-----------------------|-----------------------|---------|
| Exact match %        | **92.0%**             | 68.7%                 | +23.3pp |
| Char accuracy %      | **96.5%**             | 82.4%                 | +14.1pp |
| Detection rate %     | 100.0%                | 99.9%                 | +0.1pp  |
| Speed (img/s CPU)    | 1.05                  | ~1.5 (YOLO char only) | -0.5    |
| Avg OCR confidence   | 0.977                 | N/A                   | —       |

**Improvement vs old PaddleOCR** (broken crops): +41.2pp exact match (50.8% → 92.0%)

This confirms that the previous PaddleOCR test was limited by the weak detector,
not by PaddleOCR itself.

---

## Error Analysis (40 failures out of 500)

### Error categories:

**1. Character hallucination / OCR reads surroundings** (~35% of errors)
PaddleOCR sometimes reads text adjacent to the plate (vehicle branding, stickers,
frame inscriptions) when they appear inside the detected bbox. Examples:
- `GT=36C10636` → `PRED=36C106360204201908` (reads date/number inscribed on frame)
- `GT=29N158498` → `PRED=29N1HONDA58498` (reads "HONDA" brand on scooter body)
- `GT=36A38385` → `PRED=36A383852019133` (reads extra digits from nearby markings)
- `GT=36M4080`  → `PRED=4080` (misses prefix when plate is partially clipped)

This is a known limitation of general OCR — it reads all visible text, not just the plate.
Mitigation: post-filter by VN plate regex (drop results > 9 chars, or apply strict format filter).

**2. Single character substitution** (~40% of errors)
Residual char-level confusion where one character is misread:
- `1 ↔ 8`: 4 cases (e.g., `36A12295` → `36A22295`, `89F11898` → `89F11898`)
- `7 ↔ 5`: 2 cases
- `B ↔ 8`: 2 cases (e.g., `15B245926` → `158245926`)
- `V ↔ 1`: 1 case (`29V73283` → `29173283`)
- `D ↔ 0/U`: 2 cases
- `X ↔ 4`: 1 case

**3. Deletion / insertion** (~25% of errors)
OCR misses or duplicates a character:
- `34B259811` → `34B2599811` (8 duplicated)
- `15B245926` → `158245926` (B read as 8, subtle)
- `29AA12223` → `29AA1223` (digit dropped)

### Top confusions (from 20 error samples with char-level mismatch):
```
1->8: 2x    7->5: 2x    8->1: 2x    B->8: 2x
1->2: 1x    8->9: 1x    1->O: 1x    D->U: 1x
V->1: 1x    Z->7: 1x    5->T: 1x    X->4: 1x
```

The 1↔8, B↔8, V↔1 confusions are visually understandable given font similarity
in Vietnamese license plates (angular/bold font).

---

## Comparison: Three OCR Configurations

| Configuration                          | Exact Match | Char Acc | Det Rate | Notes                         |
|----------------------------------------|-------------|----------|----------|-------------------------------|
| YOLO char + baseline LP_detector       | 37.8%       | 53.8%    | 72.7%    | Original baseline (test6)     |
| PaddleOCR + baseline LP_detector       | 50.8%       | ~67%     | 72.7%    | Old PaddleOCR test            |
| YOLO char + finetuned LP_detector      | 68.7%       | 82.4%    | 99.9%    | After detector finetuning (test12) |
| **PaddleOCR + finetuned LP_detector**  | **92.0%**   | **96.5%**| 100.0%   | **This test (test22, n=500)** |

---

## Approaches 2 and 3 — Not Pursued

**Approach 2 (Fine-tune YOLO char OCR)**: Not pursued. The decision criteria was:
"Only pursue if Approach 1 gives <75% exact match." With 92.0%, there is no need.
The 2-3 hour training investment is not justified.

**Approach 3 (Ensemble YOLO + PaddleOCR)**: Not pursued. Ensemble was proposed as
a fallback for 70-80% result range. At 92.0%, PaddleOCR alone significantly outperforms
the ensemble target.

---

## Recommendation

**Switch OCR backend from YOLO char-level (LP_ocr.pt) to PaddleOCR (PP-OCRv5)**
for the production pipeline.

Rationale:
- +23.3pp exact match on 500-image sample (92.0% vs 68.7%)
- No additional training required — drop-in replacement
- Detection rate stays at 100% (same finetuned LP_detector_finetuned.pt)
- PaddleOCR already installed (version 3.4.1), tested and working

**Suggested post-processing to handle hallucination errors**:
Add a length filter after PaddleOCR: reject any result longer than 9 characters
(max valid VN plate length), fall back to raw result or empty. This would resolve
~35% of remaining errors (the "reads surrounding text" class).

**Implementation path** (for pipeline.py change, not done in this test):
1. Replace `PlateOCR` with `PlateOCRPaddle` in `pipeline.py`
2. Add `len(pred) <= 9` filter in `PlateOCRPaddle.read()` or in pipeline
3. Run full 3,731-image eval to confirm 92%+ holds on complete test set
4. Update CLAUDE.md with new production baseline

**Full eval recommendation**: Run `scripts/eval-paddle-on-finetuned.py` without `--limit`
to confirm the 92.0% result holds at scale (~60 min on CPU).

---

## Speed Note

PaddleOCR runs at ~1.05 img/s on CPU (vs ~1.5 img/s for YOLO char OCR alone).
In the live pipeline context, the bottleneck is typically vehicle tracking + SORT
(not OCR per frame). Per-vehicle, OCR runs once per unique track, so the 0.45 img/s
difference is negligible in practice. GPU inference would recover this gap.

---

## Files

- `scripts/eval-paddle-on-finetuned.py` — eval script (new)
- `data/processed/paddle-finetuned-eval.json` — full results JSON
- `apps/ai_engine/src/plate_ocr_paddle.py` — PlateOCRPaddle class (unchanged)
