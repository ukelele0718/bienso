"""OCR eval experiment: Use ground truth bbox from filename instead of LP_detector.

Purpose: Isolate OCR accuracy from plate detector accuracy.
If this achieves >80% exact match, the bottleneck is the plate detector (not OCR).
If still low (~40%), the bottleneck is the OCR model itself.

GT bbox format from VNLP filename:
    {idx}_{frame}_{cls}_{plate}_{x1}_{y1}_{x2}_{y2}.jpg
    Example: 4_2780_1_36C07119_126_179_491_245.jpg
    parts[4:8] = [126, 179, 491, 245]  (x1, y1, x2, y2 in full image coords)

Usage:
    python scripts/eval-ocr-gt-bbox.py --limit 500
    python scripts/eval-ocr-gt-bbox.py              # full test split
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import cv2
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"
OCR_MODEL_PATH = PROJECT_ROOT / "models" / "LP_ocr.pt"
OCR_CONF_THRESHOLD = 0.25


def parse_filename(filename: str) -> tuple[str | None, tuple[int, int, int, int] | None]:
    """Parse GT plate text and bbox from VNLP filename.

    Returns (plate_text, (x1, y1, x2, y2)) or (None, None) on failure.
    Format: {idx}_{frame}_{cls}_{plate}_{x1}_{y1}_{x2}_{y2}.jpg
    """
    name = Path(filename).stem
    parts = name.split("_")
    if len(parts) < 8:
        return None, None
    gt_plate = parts[3].upper()
    try:
        x1, y1, x2, y2 = int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7])
    except (ValueError, IndexError):
        return gt_plate, None
    return gt_plate, (x1, y1, x2, y2)


def normalize_plate(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def ocr_from_crop(ocr_model, crop_img) -> tuple[str, float]:
    results = ocr_model(crop_img)
    detections = results.pandas().xyxy[0]
    if detections.empty:
        return "", 0.0

    df = detections.copy()
    df["x_center"] = (df["xmin"] + df["xmax"]) / 2
    df["y_center"] = (df["ymin"] + df["ymax"]) / 2
    avg_char_height = (df["ymax"] - df["ymin"]).mean()

    sorted_by_y = df.sort_values("y_center").reset_index(drop=True)
    y_centers = sorted_by_y["y_center"].tolist()

    split_idx = None
    max_gap = 0
    if len(y_centers) >= 2:
        for i in range(len(y_centers) - 1):
            gap = y_centers[i + 1] - y_centers[i]
            if gap > max_gap:
                max_gap = gap
                split_idx = i

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
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]
    if limit:
        test_entries = test_entries[:limit]

    print(f"[eval-gt] Variant: Ground truth bbox (no LP_detector, OCR only)")
    print(f"[eval-gt] Loading OCR model only (no plate detector needed)...")
    ocr_model = torch.hub.load(
        "ultralytics/yolov5", "custom", path=str(OCR_MODEL_PATH), trust_repo=True
    )
    ocr_model.conf = OCR_CONF_THRESHOLD

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[eval-gt] Device: {device}")
    print(f"[eval-gt] Running on {len(test_entries)} images...")

    total = 0
    skipped_no_bbox = 0
    ocr_attempted = 0
    exact_match = 0
    char_correct = 0
    char_total = 0
    confidence_sum = 0.0
    errors: list[dict] = []
    ocr_empty = 0

    t0 = time.time()

    for i, entry in enumerate(test_entries):
        img_path = DATA_DIR / Path(entry["path"])
        if not img_path.exists():
            continue

        gt_plate, bbox = parse_filename(img_path.name)
        if not gt_plate:
            continue

        gt_normalized = normalize_plate(gt_plate)
        total += 1

        if bbox is None:
            # Filename doesn't have 8 parts — skip
            skipped_no_bbox += 1
            errors.append({"file": img_path.name, "gt": gt_normalized, "pred": "", "error": "no_gt_bbox"})
            continue

        x1, y1, x2, y2 = bbox
        img = cv2.imread(str(img_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        # Clamp gt bbox to image bounds
        x1c = max(0, min(x1, w))
        y1c = max(0, min(y1, h))
        x2c = max(0, min(x2, w))
        y2c = max(0, min(y2, h))

        crop = img[y1c:y2c, x1c:x2c]
        if crop.size == 0:
            errors.append({"file": img_path.name, "gt": gt_normalized, "pred": "", "error": "empty_crop"})
            continue

        ocr_attempted += 1
        pred_text, avg_conf = ocr_from_crop(ocr_model, crop)
        pred_normalized = normalize_plate(pred_text)
        confidence_sum += avg_conf

        if not pred_normalized:
            ocr_empty += 1

        if pred_normalized == gt_normalized:
            exact_match += 1

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
                "bbox": [x1, y1, x2, y2],
            })

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(test_entries) - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(test_entries)}] {rate:.1f} img/s, ETA: {eta:.0f}s")

    elapsed = time.time() - t0

    # Detection rate is 100% (we use GT bbox, no detector)
    exact_match_rate = (exact_match / ocr_attempted * 100) if ocr_attempted > 0 else 0
    char_accuracy = (char_correct / char_total * 100) if char_total > 0 else 0
    avg_confidence = (confidence_sum / ocr_attempted) if ocr_attempted > 0 else 0
    ocr_empty_rate = (ocr_empty / ocr_attempted * 100) if ocr_attempted > 0 else 0

    results = {
        "variant": "gt-bbox",
        "note": "Uses ground truth bbox from filename — isolates OCR accuracy from plate detector",
        "ocr_conf_threshold": OCR_CONF_THRESHOLD,
        "total_images": total,
        "skipped_no_bbox": skipped_no_bbox,
        "ocr_attempted": ocr_attempted,
        "detection_rate_pct": 100.0,  # GT bbox, no detector needed
        "exact_match": exact_match,
        "exact_match_rate_pct": round(exact_match_rate, 1),
        "char_accuracy_pct": round(char_accuracy, 1),
        "ocr_empty_pct": round(ocr_empty_rate, 1),
        "avg_ocr_confidence": round(avg_confidence, 3),
        "elapsed_seconds": round(elapsed, 1),
        "images_per_second": round(total / elapsed, 1) if elapsed > 0 else 0,
        "sample_errors": errors[:20],
    }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OCR eval using ground truth bbox — isolates OCR from detector"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test images")
    args = parser.parse_args()

    results = run_evaluation(limit=args.limit)

    print("\n" + "=" * 60)
    print("  GT-BBOX OCR EVALUATION (ground truth crop, no detector)")
    print("=" * 60)
    print(f"  Images evaluated:    {results['total_images']}")
    print(f"  Skipped (no bbox):   {results['skipped_no_bbox']}")
    print(f"  OCR attempted:       {results['ocr_attempted']}")
    print(f"  Exact match:         {results['exact_match']} ({results['exact_match_rate_pct']}%)")
    print(f"  Character accuracy:  {results['char_accuracy_pct']}%")
    print(f"  OCR returned empty:  {results['ocr_empty_pct']}%")
    print(f"  Avg OCR confidence:  {results['avg_ocr_confidence']}")
    print(f"  Throughput:          {results['images_per_second']} img/s")
    print(f"  Elapsed:             {results['elapsed_seconds']}s")
    print("=" * 60)

    threshold = 80.0
    em = results["exact_match_rate_pct"]
    if em >= threshold:
        print(f"\n  >> CONCLUSION: OCR alone achieves {em}% (>={threshold}%).")
        print(f"     Bottleneck is LP_DETECTOR, not OCR model.")
    else:
        print(f"\n  >> CONCLUSION: OCR alone achieves only {em}% (<{threshold}%).")
        print(f"     Bottleneck is OCR MODEL or GT-bbox quality, not just the detector.")

    if results["sample_errors"]:
        print(f"\n  Sample errors (first {min(10, len(results['sample_errors']))}):")
        for e in results["sample_errors"][:10]:
            gt = e.get("gt", "")
            pred = e.get("pred", "")
            err = e.get("error", "")
            conf = e.get("conf", "")
            if err:
                print(f"    {e['file']}: {err}")
            else:
                print(f"    GT={gt} PRED={pred} conf={conf}")

    out_path = PROJECT_ROOT / "data" / "processed" / "eval-gt-bbox.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
