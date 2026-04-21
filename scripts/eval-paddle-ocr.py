"""PaddleOCR evaluation script — benchmark vs YOLO char-level baseline.

Runs LP_detector (YOLOv5, unchanged) + PaddleOCR on VNLP test images.
Compares results against ground truth from filenames.

Baseline to beat: 37.8% exact match, 53.8% char accuracy (YOLO char-level).

Import order note:
    torch is imported BEFORE plate_ocr_paddle to avoid a Windows DLL conflict.
    See plate_ocr_paddle.py module docstring for details.

Usage:
    python scripts/eval-paddle-ocr.py --limit 500
    python scripts/eval-paddle-ocr.py              # full test split (3,731)
    python scripts/eval-paddle-ocr.py --limit 3731 --out data/processed/paddle-ocr-cpu.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import cv2
import torch  # MUST come before plate_ocr_paddle import (Windows DLL order)

# Add ai_engine src to path for local import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "ai_engine" / "src"))
from plate_ocr_paddle import PlateOCRPaddle  # noqa: E402

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"
DET_MODEL_PATH = PROJECT_ROOT / "models" / "LP_detector.pt"
DET_CONF_THRESHOLD = 0.25
DEFAULT_OUT = PROJECT_ROOT / "data" / "processed" / "paddle-ocr-cpu.json"

# Baseline numbers from test6-full-ocr-eval-3731.md
BASELINE_EXACT_MATCH_PCT = 37.8
BASELINE_CHAR_ACCURACY_PCT = 53.8
BASELINE_DETECTION_RATE_PCT = 72.7
BASELINE_SPEED_IPS = 2.1  # img/s on CPU


def parse_ground_truth(filename: str) -> str | None:
    """Extract plate from VNLP filename: {idx}_{frame}_{cls}_{plate}_{x1}...jpg"""
    stem = Path(filename).stem
    parts = stem.split("_")
    if len(parts) >= 4:
        return parts[3].upper()
    return None


def normalize_plate(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def char_accuracy_counts(gt: str, pred: str) -> tuple[int, int]:
    """Return (correct_chars, total_chars) for position-wise comparison."""
    total = max(len(gt), len(pred))
    correct = sum(
        1
        for i in range(total)
        if i < len(gt) and i < len(pred) and gt[i] == pred[i]
    )
    return correct, total


def run_evaluation(limit: int | None) -> dict:
    """Main eval loop: detect plate → crop → PaddleOCR → compare with GT."""
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]
    if limit:
        test_entries = test_entries[:limit]

    print(f"[eval] Loading LP_detector (YOLOv5) from {DET_MODEL_PATH.name}...")
    det_model = torch.hub.load(
        "ultralytics/yolov5",
        "custom",
        path=str(DET_MODEL_PATH),
        trust_repo=True,
        verbose=False,
    )
    det_model.conf = DET_CONF_THRESHOLD

    print("[eval] Loading PaddleOCR (PP-OCRv5 CPU, lang=en)...")
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

        # Step 1: Detect plate bbox via LP_detector
        det_results = det_model(str(img_path))
        det_df = det_results.pandas().xyxy[0]

        if det_df.empty:
            error_samples.append(
                {"file": img_path.name, "gt": gt, "pred": "", "error": "no_detection"}
            )
            continue

        detected += 1
        best = det_df.sort_values("confidence", ascending=False).iloc[0]
        x1, y1 = int(best.xmin), int(best.ymin)
        x2, y2 = int(best.xmax), int(best.ymax)

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        crop = img[max(0, y1):y2, max(0, x1):x2]
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
        elif not is_exact:
            error_samples.append(record)

        # Progress every 50 images
        if (i + 1) % 50 == 0 or (i + 1) == len(test_entries):
            elapsed = time.time() - t0
            rate = total / elapsed if elapsed > 0 else 0
            eta = (len(test_entries) - i - 1) / rate if rate > 0 else 0
            em_pct = exact_match / ocr_attempted * 100 if ocr_attempted > 0 else 0
            print(
                f"  [{i+1:4d}/{len(test_entries)}] "
                f"{rate:.2f} img/s | exact={em_pct:.1f}% | ETA {eta:.0f}s"
            )

    elapsed = time.time() - t0
    detection_rate = detected / total * 100 if total > 0 else 0
    exact_match_rate = exact_match / ocr_attempted * 100 if ocr_attempted > 0 else 0
    char_accuracy_pct = char_correct_sum / char_total_sum * 100 if char_total_sum > 0 else 0
    avg_conf = confidence_sum / ocr_attempted if ocr_attempted > 0 else 0
    ips = total / elapsed if elapsed > 0 else 0

    return {
        "model": "PaddleOCR PP-OCRv5 (CPU, lang=en)",
        "paddleocr_version": "3.4.1",
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
        "vs_baseline": {
            "exact_match_delta_pct": round(exact_match_rate - BASELINE_EXACT_MATCH_PCT, 1),
            "char_accuracy_delta_pct": round(char_accuracy_pct - BASELINE_CHAR_ACCURACY_PCT, 1),
            "speed_delta_ips": round(ips - BASELINE_SPEED_IPS, 2),
        },
        "sample_correct": correct_samples[:5],
        "sample_errors": error_samples[:20],
    }


def print_summary(results: dict) -> None:
    b = results["vs_baseline"]

    def delta_str(val: float) -> str:
        return f"+{val:.1f}" if val >= 0 else f"{val:.1f}"

    print()
    print("=" * 65)
    print("  PADDLEOCR vs YOLO CHAR-LEVEL BASELINE")
    print("=" * 65)
    print(f"  Model:              {results['model']}")
    print(f"  Images evaluated:   {results['total_images']}")
    print(
        f"  Plates detected:    {results['plates_detected']}"
        f" ({results['detection_rate_pct']}%)"
    )
    print(f"  OCR attempted:      {results['ocr_attempted']}")
    print()
    print(f"  {'Metric':<25} {'PaddleOCR':>12} {'Baseline':>12} {'Delta':>8}")
    print(f"  {'-'*57}")
    print(
        f"  {'Exact match %':<25}"
        f" {results['exact_match_rate_pct']:>11.1f}%"
        f" {BASELINE_EXACT_MATCH_PCT:>11.1f}%"
        f" {delta_str(b['exact_match_delta_pct']):>7}%"
    )
    print(
        f"  {'Char accuracy %':<25}"
        f" {results['char_accuracy_pct']:>11.1f}%"
        f" {BASELINE_CHAR_ACCURACY_PCT:>11.1f}%"
        f" {delta_str(b['char_accuracy_delta_pct']):>7}%"
    )
    print(
        f"  {'Speed (img/s)':<25}"
        f" {results['images_per_second']:>12.2f}"
        f" {BASELINE_SPEED_IPS:>12.1f}"
        f" {delta_str(b['speed_delta_ips']):>8}"
    )
    print(f"  {'Avg OCR confidence':<25} {results['avg_ocr_confidence']:>12.3f}")
    print(f"  {'Elapsed (s)':<25} {results['elapsed_seconds']:>12.1f}")
    print("=" * 65)

    print(f"\n  Sample correct predictions (first 5):")
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
    delta = b["exact_match_delta_pct"]
    print()
    if em > 50:
        print(
            f"  RECOMMENDATION: PaddleOCR beats baseline by {delta_str(delta)}% exact match."
        )
        print("  Consider running full 3,731-image eval for final confirmation.")
    elif em > BASELINE_EXACT_MATCH_PCT:
        print(
            f"  RESULT: PaddleOCR marginally better ({delta_str(delta)}%). Consider full eval."
        )
    else:
        print(
            f"  RESULT: PaddleOCR did NOT beat baseline ({delta_str(delta)}%). Investigate."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate PaddleOCR vs YOLO baseline on VNLP dataset"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Max test images (default: all 3731)"
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT, help="Output JSON path"
    )
    args = parser.parse_args()

    results = run_evaluation(limit=args.limit)
    print_summary(results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved -> {args.out}")


if __name__ == "__main__":
    main()
