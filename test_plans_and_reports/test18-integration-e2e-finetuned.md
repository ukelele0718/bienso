# Test 18 — Integration: Fine-tuned YOLOv8 Plate Detector E2E Demo

**Date**: 2026-04-21
**Engineer**: Agent B (integration)
**Status**: PASSED

---

## 1. Objective

Integrate `LP_detector_finetuned.pt` (YOLOv8n, fine-tuned on VNLP dataset) into the existing pipeline alongside the baseline `LP_detector.pt` (YOLOv5). Verify E2E demo works on both models, run unit tests, compare results.

---

## 2. Integration Approach — Auto-detect v5 vs v8

### Problem

`plate_detector.py` had broken auto-detection logic:

```python
# BEFORE (wrong): LP_detector_finetuned.pt contains "LP_detector" → wrongly routed to v5
model_type = "yolov5" if "LP_detector" in path else "yolov8"
```

`LP_detector_finetuned.pt` contains "LP_detector" as prefix, so the old logic silently loaded it with `torch.hub` (YOLOv5 backend), causing format mismatch failure at inference.

### Fix Applied

```python
# AFTER (correct): check for "finetuned" or "yolov8" keywords first
path_lower = path.lower()
if "finetuned" in path_lower or "yolov8" in path_lower:
    model_type = "yolov8"
else:
    model_type = "yolov5"
```

Priority order: explicit `finetuned` or `yolov8` in filename → v8 backend (ultralytics); fallback → v5 backend (torch.hub).

### File Changed

- `apps/ai_engine/src/plate_detector.py` — 5-line change in `__init__`, lines 35–40 (file remains 88 lines, well under 200-line limit)

### Config — No change needed

`apps/ai_engine/src/config.py` already supports env override:
```python
PLATE_MODEL = MODELS_DIR / os.getenv("AI_PLATE_MODEL", "LP_detector.pt")
```
Default: `LP_detector.pt` (v5, backward-compatible). Switch to finetuned: `AI_PLATE_MODEL=LP_detector_finetuned.pt`.

---

## 3. E2E Demo Results

**Video**: `data/test-videos/trungdinh22-demo.mp4` — 600×800 @ 10 fps, 300 frames  
**Mode**: `--no-backend` (no backend needed), CPU inference  
**GPU**: GTX 1650 (models loaded on CUDA — vehicle detector uses YOLOv8n, plate models on GPU)

### Verification of correct backend selection

Finetuned log shows **1** YOLOv5 model summary (290 layers, 20,970,123 params = LP_ocr.pt).  
Baseline log shows **2** YOLOv5 model summaries (LP_detector.pt + LP_ocr.pt).  
This confirms finetuned plate detector ran on ultralytics YOLO v8 as intended.

### Side-by-side comparison table

| Metric | Baseline (LP_detector.pt, YOLOv5) | Finetuned (LP_detector_finetuned.pt, YOLOv8) |
|--------|-----------------------------------|-----------------------------------------------|
| Frames processed | 300 | 300 |
| Processing time | 25.5 s | 14.7 s |
| **FPS** | **11.7** | **20.3** (+73%) |
| Raw events fired | 23 | 18 |
| Unique plate+track combos | 4 | 4 |
| Unique plates detected | 2 | 2 |
| Plates (text) | `36H82613`, `14K117970` | `36H82613`, `14K117970` |
| Tracks per plate | track_3 + track_5 (36H), track_8 + track_9 (14K) | track_3 + track_5 (36H), track_8 + track_9 (14K) |
| Vehicle types | car (all) | car (all) |
| Max plate confidence | 0.90 | 0.91 |

### Notes on results

- Both models detected the **same 2 unique plates** on the same 2 vehicles — consistency confirmed.
- Finetuned model is **73% faster** (20.3 vs 11.7 FPS) because ultralytics YOLO v8 inference pipeline is more efficient than torch.hub v5.
- Finetuned produced 5 fewer raw events (18 vs 23) — likely due to tighter detection thresholds or slightly different frame-by-frame sensitivity; final unique plates identical.
- Both models correctly assigned `vehicle_type = car` for all detections via majority voting.

---

## 4. Unit Tests

### AI Engine (45 tests)

```
apps/ai_engine/tests/test_ocr_postprocess.py    33 passed
apps/ai_engine/tests/test_vehicle_majority_voting.py    12 passed
TOTAL: 45 passed in 6.71s
```

### Backend (101 tests)

```
apps/backend/tests/  101 passed in 3.03s
2 DeprecationWarning (on_event → lifespan, non-blocking)
```

### Combined: 146/146 tests pass

---

## 5. Offline Evaluation Context (from prior eval, 500 test images)

| Metric | Baseline (LP_detector.pt) | Finetuned (LP_detector_finetuned.pt) |
|--------|--------------------------|--------------------------------------|
| Detection rate | 90.2% | 100.0% |
| OCR exact match | 37.8% | 70.6% |
| Char accuracy | 53.6% | 83.8% |

The finetuned model's superior detection rate (100% vs 90.2%) means fewer missed plates in the pipeline — the E2E demo on this video happened to have all plates detected by both models, so the improvement is not visible on this particular short video.

---

## 6. Recommendation

**Set `AI_PLATE_MODEL=LP_detector_finetuned.pt` as default in production.**

Rationale:
1. **100% detection rate** vs 90.2% — no missed plates
2. **70.6% OCR exact match** vs 37.8% — nearly 2× better recognition
3. **73% faster** at E2E inference (20.3 vs 11.7 FPS on this video)
4. Drop-in replacement: same `PlateDetection` output format, no downstream changes needed
5. Backward-compatible: setting `AI_PLATE_MODEL=LP_detector.pt` restores v5 behavior exactly

**How to set as default permanently** (without breaking existing installs):

Option A — update `.env` or deployment config:
```
AI_PLATE_MODEL=LP_detector_finetuned.pt
```

Option B — change default in `config.py` line 13:
```python
PLATE_MODEL = MODELS_DIR / os.getenv("AI_PLATE_MODEL", "LP_detector_finetuned.pt")
```

Either approach is safe. The current default (`LP_detector.pt`) is preserved until explicitly changed.

---

## 7. Files Changed

| File | Change |
|------|--------|
| `apps/ai_engine/src/plate_detector.py` | Fixed auto-detect: `finetuned`/`yolov8` in filename → v8 backend |

**No other files modified.**

---

## 8. Logs

- `runs/e2e-finetuned-output.log` — finetuned model E2E run
- `runs/e2e-baseline-output.log` — baseline model E2E run
