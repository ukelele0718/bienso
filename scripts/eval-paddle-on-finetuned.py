"""PaddleOCR eval using the finetuned YOLOv8 plate detector (LP_detector_finetuned.pt).

Approach 1 of the OCR improvement experiment:
    Previous test (eval-paddle-ocr.py) used old LP_detector.pt (YOLOv5, ~72.7% det rate)
    and got 50.8% exact match vs 37.8% YOLO baseline on broken crops.

    This script uses LP_detector_finetuned.pt (YOLOv8, 99.9% det rate) which produces
    near-perfect crops — testing whether PaddleOCR can surpass YOLO char-level OCR
    at 68.7% exact match on the same finetuned-detector setup.

Baselines to beat (from test6 / test12 full-eval):
    - YOLO char OCR + finetuned detector: 68.7% exact, 82.4% char accuracy
    - PaddleOCR + baseline detector:      50.8% exact, ~67% char accuracy

Expected: With perfect crops, PaddleOCR may reach 80-85%.

Import order:
    torch MUST be imported before plate_ocr_paddle (Windows DLL load order).

Usage:
    PYTHONIOENCODING=utf-8 python scripts/eval-paddle-on-finetuned.py --limit 500
    PYTHONIOENCODING=utf-8 python scripts/eval-paddle-on-finetuned.py --limit 3731
    AI_PLATE_MODEL=LP_detector_finetuned.pt PYTHONIOENCODING=utf-8 \\
        python scripts/eval-paddle-on-finetuned.py --limit 500
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import cv2
import torch  # MUST come before plate_ocr_paddle import (Windows DLL order)
from ultralytics import YOLO

# Add ai_engine src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "ai_engine" / "src"))
from plate_ocr_paddle import PlateOCRPaddle  # noqa: E402

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"

# Respect AI_PLATE_MODEL env override, default to finetuned
_plate_model_name = os.getenv("AI_PLATE_MODEL", "LP_detector_finetuned.pt")
DET_MODEL_PATH = PROJECT_ROOT / "models" / _plate_model_name
DET_CONF_THRESHOLD = 0.25
PADDING_RATIO = 0.0  # no extra padding — model trained on tight crops already

DEFAULT_OUT = PROJECT_ROOT / "data" / "processed" / "paddle-finetuned-eval.json"

# Baselines for comparison
BASELINE_FINETUNED_YOLO_EXACT = 68.7   # YOLO char OCR + finetuned detector
BASELINE_FINETUNED_YOLO_CHAR = 82.4
BASELINE_PADDLE_OLD_EXACT = 50.8       # PaddleOCR + baseline (broken) detector
BASELINE_SPEED_IPS = 1.5


def parse_ground_truth(filename: str) -> str | None:
    """Extract plate text from VNLP filename: {idx}_{frame}_{cls}_{plate}_{x1}...jpg"""
    stem = Path(filename).stem
    parts = stem.split("_")
    if len(parts) >= 4:
        return parts[3].upper()
    return None


def normalize_plate(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def char_accuracy_counts(gt: str, pred: str) -> tuple[int, int]:
    """Position-wise comparison. Returns (correct_chars, total_chars)."""
    total = max(len(gt), len(pred))
    correct = sum(
        1
        for i in range(total)
        if i < len(gt) and i < len(pred) and gt[i] == pred[i]
    )
    return correct, total


def run_evaluation(limit: int | None) -> dict:
    """Main eval loop: finetuned YOLOv8 detect → crop → PaddleOCR → compare GT."""
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]
    if limit:
        test_entries = test_entries[:limit]

    print(f"[eval] Detector model: {DET_MODEL_PATH.name} (YOLOv8, finetuned)")
    if not DET_MODEL_PATH.exists():
        print(f"[eval] ERROR: Model not found at {DET_MODEL_PATH}")
        sys.exit(1)

    print(f"[eval] Loading LP_detector_finetuned (YOLOv8)...")
    det_model = YOLO(str(DET_MODEL_PATH))

    print(f"[eval] Loading PaddleOCR (PP-OCRv5 CPU, lang=en)...")
    paddle_ocr = PlateOCRPaddle(use_gpu=False, lang="en")
    print(f"[eval] Models ready. Evaluating {len(test_entries)} images...\n")

    total = 0
    detected = 0
    ocr_attempted = 0
    exact_match = 0
    char_correct_sum = 0
    char_total_sum = 0
    confidence_sum = 0.0

    correct_samples: list[dict] = []
    error_samples: list[dict] = []

    t0 = time.time()

    for i, entry in enumerate(test_entries):
        img_path = DATA_DIR / entry["path"].replace("\\", "/")
        if not img_path.exists():
            continue

        gt_raw = parse_ground_truth(img_path.name)
        if not gt_raw:
            continue

        gt = normalize_plate(gt_raw)
        total += 1

        # Step 1: Detect plate bbox via finetuned YOLOv8
        results = det_model(str(img_path), conf=DET_CONF_THRESHOLD, verbose=False)
        boxes = results[0].boxes

        if boxes is None or len(boxes) == 0:
            error_samples.append(
                {"file": img_path.name, "gt": gt, "pred": "", "error": "no_detection"}
            )
            continue

        detected += 1

        # Take highest-confidence box
        best_idx = int(boxes.conf.argmax())
        x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[best_idx].tolist()]

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        # Optional: add padding around detected bbox
        if PADDING_RATIO > 0:
            pw = int((x2 - x1) * PADDING_RATIO)
            ph = int((y2 - y1) * PADDING_RATIO)
            x1 = max(0, x1 - pw)
            y1 = max(0, y1 - ph)
            x2 = min(w, x2 + pw)
            y2 = min(h, y2 + ph)

        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        # Step 2: OCR via PaddleOCR
        ocr_attempted += 1
        pred_raw, conf = paddle_ocr.read(crop)
        pred = normalize_plate(pred_raw or "")
        confidence_sum += conf

        # Step 3: Metrics
        is_exact = pred == gt
        if is_exact:
            exact_match += 1

        c_correct, c_total = char_accuracy_counts(gt, pred)
        char_correct_sum += c_correct
        char_total_sum += c_total

        record = {"file": img_path.name, "gt": gt, "pred": pred, "conf": round(conf, 3)}

        if is_exact and len(correct_samples) < 10:
            correct_samples.append(record)
        elif not is_exact and len(error_samples) < 50:
            error_samples.append(record)

        # Progress every 50 images
        if (i + 1) % 50 == 0 or (i + 1) == len(test_entries):
            elapsed = time.time() - t0
            rate = total / elapsed if elapsed > 0 else 0
            eta = (len(test_entries) - i - 1) / rate if rate > 0 else 0
            em_pct = exact_match / ocr_attempted * 100 if ocr_attempted > 0 else 0
            print(
                f"  [{i+1:4d}/{len(test_entries)}] "
                f"{rate:.2f} img/s | exact={em_pct:.1f}% | det={detected}/{total} | ETA {eta:.0f}s"
            )

    elapsed = time.time() - t0
    detection_rate = detected / total * 100 if total > 0 else 0
    exact_match_rate = exact_match / ocr_attempted * 100 if ocr_attempted > 0 else 0
    char_accuracy_pct = char_correct_sum / char_total_sum * 100 if char_total_sum > 0 else 0
    avg_conf = confidence_sum / ocr_attempted if ocr_attempted > 0 else 0
    ips = total / elapsed if elapsed > 0 else 0

    return {
        "experiment": "Approach 1: PaddleOCR + finetuned YOLOv8 detector",
        "detector_model": DET_MODEL_PATH.name,
        "ocr_backend": "PaddleOCR PP-OCRv5 (CPU, lang=en)",
        "paddleocr_version": "3.4.1",
        "padding_ratio": PADDING_RATIO,
        "limit": limit,
        "total_images": total,
        "plates_detected": detected,
        "detection_rate_pct": round(detection_rate, 1),
        "ocr_attempted": ocr_attempted,
        "exact_match": exact_match,
        "exact_match_rate_pct": round(exact_match_rate, 1),
        "char_accuracy_pct": round(char_accuracy_pct, 1),
        "avg_ocr_confidence": round(avg_conf, 3),
        "elapsed_seconds": round(elapsed, 1),
        "images_per_second": round(ips, 2),
        "vs_finetuned_yolo": {
            "exact_match_delta_pct": round(exact_match_rate - BASELINE_FINETUNED_YOLO_EXACT, 1),
            "char_accuracy_delta_pct": round(char_accuracy_pct - BASELINE_FINETUNED_YOLO_CHAR, 1),
        },
        "vs_paddle_old": {
            "exact_match_delta_pct": round(exact_match_rate - BASELINE_PADDLE_OLD_EXACT, 1),
        },
        "sample_correct": correct_samples[:5],
        "sample_errors": error_samples[:20],
    }


def analyze_errors(error_samples: list[dict]) -> dict:
    """Count most common char confusion pairs from error samples."""
    from collections import Counter
    confusion: Counter = Counter()
    for e in error_samples:
        gt = e.get("gt", "")
        pred = e.get("pred", "")
        if not pred or e.get("error"):
            continue
        for j in range(min(len(gt), len(pred))):
            if gt[j] != pred[j]:
                confusion[f"{gt[j]}->{pred[j]}"] += 1
    return dict(confusion.most_common(15))


def print_summary(results: dict) -> None:
    b_yolo = results["vs_finetuned_yolo"]
    b_old = results["vs_paddle_old"]

    def delta_str(val: float) -> str:
        return f"+{val:.1f}" if val >= 0 else f"{val:.1f}"

    print()
    print("=" * 70)
    print("  PADDLEOCR (finetuned detector) vs BASELINES")
    print("=" * 70)
    print(f"  Detector:           {results['detector_model']}")
    print(f"  OCR backend:        {results['ocr_backend']}")
    print(f"  Images evaluated:   {results['total_images']}")
    print(
        f"  Plates detected:    {results['plates_detected']}"
        f" ({results['detection_rate_pct']}%)"
    )
    print(f"  OCR attempted:      {results['ocr_attempted']}")
    print()
    print(
        f"  {'Metric':<26} {'PaddleOCR+finetuned':>18} "
        f"{'YOLOchar+finetuned':>18} {'Delta':>8}"
    )
    print(f"  {'-' * 70}")
    print(
        f"  {'Exact match %':<26}"
        f" {results['exact_match_rate_pct']:>17.1f}%"
        f" {BASELINE_FINETUNED_YOLO_EXACT:>17.1f}%"
        f" {delta_str(b_yolo['exact_match_delta_pct']):>7}%"
    )
    print(
        f"  {'Char accuracy %':<26}"
        f" {results['char_accuracy_pct']:>17.1f}%"
        f" {BASELINE_FINETUNED_YOLO_CHAR:>17.1f}%"
        f" {delta_str(b_yolo['char_accuracy_delta_pct']):>7}%"
    )
    print(
        f"  {'Detection rate %':<26}"
        f" {results['detection_rate_pct']:>17.1f}%"
        f" {'99.9':>17}%"
    )
    print(f"  {'Speed (img/s)':<26} {results['images_per_second']:>18.2f}")
    print(f"  {'Elapsed (s)':<26} {results['elapsed_seconds']:>18.1f}")
    print()
    print(
        f"  vs old PaddleOCR (broken crops): "
        f"{delta_str(b_old['exact_match_delta_pct'])}% exact match"
    )
    print("=" * 70)

    # Error analysis
    errors = [e for e in results.get("sample_errors", []) if not e.get("error")]
    if errors:
        confusion = analyze_errors(errors)
        if confusion:
            print(f"\n  Top char confusions (in {len(errors)} error samples):")
            for pair, cnt in list(confusion.items())[:10]:
                print(f"    {pair}: {cnt}x")

    print(f"\n  Sample correct (first 5):")
    for s in results.get("sample_correct", [])[:5]:
        print(f"    GT={s['gt']:<12} PRED={s['pred']:<12} conf={s['conf']:.3f}")

    print(f"\n  Sample errors (first 10):")
    for e in results.get("sample_errors", [])[:10]:
        err = e.get("error", "")
        if err:
            print(f"    {e['file']}: {err}")
        else:
            print(f"    GT={e['gt']:<12} PRED={e['pred']:<12} conf={e.get('conf', 0):.3f}")

    em = results["exact_match_rate_pct"]
    delta = b_yolo["exact_match_delta_pct"]
    print()
    if em >= 80:
        print(
            f"  VERDICT: PaddleOCR + finetuned detector achieves {em:.1f}% exact match. "
            f"({delta_str(delta)}% vs YOLO char)"
        )
        print("  RECOMMENDATION: Switch OCR backend to PaddleOCR in production pipeline.")
        print("  Consider full 3,731-image eval to confirm.")
    elif em >= 68.7:
        print(
            f"  VERDICT: PaddleOCR + finetuned achieves {em:.1f}% "
            f"({delta_str(delta)}% vs YOLO char). Marginal improvement."
        )
        print("  RECOMMENDATION: Test Approach 3 (ensemble) for additional gain.")
    else:
        print(
            f"  VERDICT: PaddleOCR + finetuned achieves only {em:.1f}% "
            f"({delta_str(delta)}% vs YOLO char)."
        )
        print("  RECOMMENDATION: YOLO char-level OCR remains better. Skip PaddleOCR.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Approach 1: PaddleOCR with finetuned YOLOv8 plate detector"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Max test images (default: all 3731)"
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT, help="Output JSON path"
    )
    args = parser.parse_args()

    print(f"[eval] Approach 1: PaddleOCR + LP_detector_finetuned.pt")
    print(f"[eval] Baseline to beat: {BASELINE_FINETUNED_YOLO_EXACT}% exact (YOLO char + finetuned)\n")

    results = run_evaluation(limit=args.limit)
    print_summary(results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved -> {args.out}")


if __name__ == "__main__":
    main()
