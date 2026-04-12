"""Baseline OCR evaluation script.

Runs LP_detector + LP_ocr on VNLP test images, compares OCR output
against ground truth from filenames.

Usage:
    python scripts/eval-ocr-baseline.py --limit 50
    python scripts/eval-ocr-baseline.py              # full test split
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import torch

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"
DET_MODEL_PATH = PROJECT_ROOT / "models" / "LP_detector.pt"
OCR_MODEL_PATH = PROJECT_ROOT / "models" / "LP_ocr.pt"
DET_CONF_THRESHOLD = 0.25
OCR_CONF_THRESHOLD = 0.25


def parse_ground_truth_from_filename(filename: str) -> str | None:
    """Extract plate text from VNLP filename pattern:
    {idx}_{frame}_{cls}_{plate}_{x1}_{y1}_{x2}_{y2}.jpg
    """
    name = Path(filename).stem
    parts = name.split("_")
    if len(parts) >= 4:
        return parts[3].upper()
    return None


def normalize_plate(text: str) -> str:
    """Strip non-alphanumeric and uppercase for comparison."""
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def ocr_from_crop(ocr_model: torch.nn.Module, crop_img) -> tuple[str, float]:
    """Run OCR model on a cropped plate image, return (text, avg_confidence).

    Handles 2-row Vietnamese plates by finding the largest vertical gap
    in character Y-centers to split rows, then reading left-to-right per row.
    """
    results = ocr_model(crop_img)
    detections = results.pandas().xyxy[0]
    if detections.empty:
        return "", 0.0

    df = detections.copy()
    df["x_center"] = (df["xmin"] + df["xmax"]) / 2
    df["y_center"] = (df["ymin"] + df["ymax"]) / 2
    avg_char_height = (df["ymax"] - df["ymin"]).mean()

    # Sort by y_center to find the largest gap for row splitting
    sorted_by_y = df.sort_values("y_center").reset_index(drop=True)
    y_centers = sorted_by_y["y_center"].tolist()

    split_idx = None
    if len(y_centers) >= 2:
        max_gap = 0
        for i in range(len(y_centers) - 1):
            gap = y_centers[i + 1] - y_centers[i]
            if gap > max_gap:
                max_gap = gap
                split_idx = i

    # Only split if gap is significant relative to char height
    is_two_row = split_idx is not None and max_gap > avg_char_height * 0.3

    if is_two_row:
        top_indices = sorted_by_y.index[: split_idx + 1]
        bot_indices = sorted_by_y.index[split_idx + 1 :]
        top_row = sorted_by_y.loc[top_indices].sort_values("x_center")
        bot_row = sorted_by_y.loc[bot_indices].sort_values("x_center")
        ordered_df = pd.concat([top_row, bot_row])
    else:
        ordered_df = df.sort_values("x_center")

    chars = [str(c) for c in ordered_df["name"].tolist()]
    confs = ordered_df["confidence"].tolist()

    text = "".join(chars)
    avg_conf = sum(confs) / len(confs) if confs else 0.0
    return text.upper(), avg_conf


def run_evaluation(limit: int | None = None) -> dict:
    """Run detector + OCR on test split images and compute metrics."""
    # Load manifest
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]
    if limit:
        test_entries = test_entries[:limit]

    print(f"[eval] Loading models...")
    det_model = torch.hub.load(
        "ultralytics/yolov5", "custom", path=str(DET_MODEL_PATH), trust_repo=True
    )
    det_model.conf = DET_CONF_THRESHOLD

    ocr_model = torch.hub.load(
        "ultralytics/yolov5", "custom", path=str(OCR_MODEL_PATH), trust_repo=True
    )
    ocr_model.conf = OCR_CONF_THRESHOLD

    print(f"[eval] Running on {len(test_entries)} images...")
    # Metrics accumulators
    total = 0
    detected = 0  # plate bbox found
    ocr_attempted = 0
    exact_match = 0
    char_correct = 0
    char_total = 0
    confidence_sum = 0.0
    errors: list[dict] = []

    t0 = time.time()

    for i, entry in enumerate(test_entries):
        img_path = DATA_DIR / entry["path"].replace("\\", "/")
        if not img_path.exists():
            continue

        gt_plate = parse_ground_truth_from_filename(img_path.name)
        if not gt_plate:
            continue

        gt_normalized = normalize_plate(gt_plate)
        total += 1

        # Step 1: Detect plate bbox
        det_results = det_model(str(img_path))
        det_df = det_results.pandas().xyxy[0]

        if det_df.empty:
            errors.append({"file": img_path.name, "gt": gt_normalized, "pred": "", "error": "no_detection"})
            continue

        detected += 1
        # Use highest confidence detection
        best = det_df.sort_values("confidence", ascending=False).iloc[0]
        x1, y1, x2, y2 = int(best["xmin"]), int(best["ymin"]), int(best["xmax"]), int(best["ymax"])

        # Crop plate region
        import cv2
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        crop = img[max(0, y1):y2, max(0, x1):x2]
        if crop.size == 0:
            continue

        # Step 2: OCR on crop
        ocr_attempted += 1
        pred_text, avg_conf = ocr_from_crop(ocr_model, crop)
        pred_normalized = normalize_plate(pred_text)
        confidence_sum += avg_conf

        # Step 3: Compare
        if pred_normalized == gt_normalized:
            exact_match += 1

        # Character-level accuracy
        for j in range(max(len(gt_normalized), len(pred_normalized))):
            char_total += 1
            if j < len(gt_normalized) and j < len(pred_normalized):
                if gt_normalized[j] == pred_normalized[j]:
                    char_correct += 1

        if pred_normalized != gt_normalized:
            errors.append({
                "file": img_path.name,
                "gt": gt_normalized,
                "pred": pred_normalized,
                "conf": round(avg_conf, 3),
            })

        # Progress
        if (i + 1) % 10 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(test_entries) - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(test_entries)}] {rate:.1f} img/s, ETA: {eta:.0f}s")

    elapsed = time.time() - t0

    # Compute metrics
    detection_rate = (detected / total * 100) if total > 0 else 0
    exact_match_rate = (exact_match / ocr_attempted * 100) if ocr_attempted > 0 else 0
    char_accuracy = (char_correct / char_total * 100) if char_total > 0 else 0
    avg_confidence = (confidence_sum / ocr_attempted) if ocr_attempted > 0 else 0

    results = {
        "total_images": total,
        "plates_detected": detected,
        "detection_rate_pct": round(detection_rate, 1),
        "ocr_attempted": ocr_attempted,
        "exact_match": exact_match,
        "exact_match_rate_pct": round(exact_match_rate, 1),
        "char_accuracy_pct": round(char_accuracy, 1),
        "avg_ocr_confidence": round(avg_confidence, 3),
        "elapsed_seconds": round(elapsed, 1),
        "images_per_second": round(total / elapsed, 1) if elapsed > 0 else 0,
        "sample_errors": errors[:20],
    }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline OCR evaluation")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test images")
    args = parser.parse_args()

    results = run_evaluation(limit=args.limit)

    print("\n" + "=" * 60)
    print("  BASELINE OCR EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Images evaluated:    {results['total_images']}")
    print(f"  Plates detected:     {results['plates_detected']} ({results['detection_rate_pct']}%)")
    print(f"  OCR attempted:       {results['ocr_attempted']}")
    print(f"  Exact match:         {results['exact_match']} ({results['exact_match_rate_pct']}%)")
    print(f"  Character accuracy:  {results['char_accuracy_pct']}%")
    print(f"  Avg OCR confidence:  {results['avg_ocr_confidence']}")
    print(f"  Throughput:          {results['images_per_second']} img/s")
    print(f"  Elapsed:             {results['elapsed_seconds']}s")
    print("=" * 60)

    if results["sample_errors"]:
        print(f"\n  Sample errors (first {len(results['sample_errors'])}):")
        for e in results["sample_errors"][:10]:
            gt = e.get("gt", "")
            pred = e.get("pred", "")
            err = e.get("error", "")
            conf = e.get("conf", "")
            if err:
                print(f"    {e['file']}: {err}")
            else:
                print(f"    GT={gt} PRED={pred} conf={conf}")

    # Save JSON results
    out_path = PROJECT_ROOT / "data" / "processed" / "baseline_eval_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
