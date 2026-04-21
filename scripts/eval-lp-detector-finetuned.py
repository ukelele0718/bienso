"""Evaluate fine-tuned LP detector against baseline on VNLP test split.

Supports both YOLOv5 (torch.hub) and YOLOv8 (ultralytics) detector models.
Swaps out the detector while keeping the same LP_ocr model.

Usage:
    # Baseline (YOLOv5 LP_detector.pt):
    python scripts/eval-lp-detector-finetuned.py --detector v5 --limit 500

    # Fine-tuned (YOLOv8 LP_detector_finetuned.pt):
    python scripts/eval-lp-detector-finetuned.py --detector v8 --limit 500

    # Compare both sequentially:
    python scripts/eval-lp-detector-finetuned.py --compare --limit 500
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import cv2
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"
DET_V5_PATH = PROJECT_ROOT / "models" / "LP_detector.pt"
DET_V8_PATH = PROJECT_ROOT / "models" / "LP_detector_finetuned.pt"
OCR_MODEL_PATH = PROJECT_ROOT / "models" / "LP_ocr.pt"
DET_CONF = 0.25
OCR_CONF = 0.25


def parse_ground_truth_from_filename(filename: str) -> str | None:
    name = Path(filename).stem
    parts = name.split("_")
    if len(parts) >= 4:
        return parts[3].upper()
    return None


def normalize_plate(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text).upper()


def ocr_from_crop(ocr_model, crop_img) -> tuple[str, float]:
    """Run YOLOv5 OCR model on plate crop."""
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
        bot_indices = sorted_by_y.index[split_idx + 1:]
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


def load_detector(mode: str):
    """Load detector. mode: 'v5' for baseline YOLOv5, 'v8' for fine-tuned YOLOv8."""
    if mode == "v5":
        print(f"  Loading YOLOv5 baseline detector: {DET_V5_PATH.name}")
        model = torch.hub.load("ultralytics/yolov5", "custom", path=str(DET_V5_PATH), trust_repo=True)
        model.conf = DET_CONF
        return model, "v5"
    elif mode == "v8":
        if not DET_V8_PATH.exists():
            print(f"ERROR: Fine-tuned model not found: {DET_V8_PATH}")
            print("  Run scripts/train-lp-detector.py first")
            sys.exit(1)
        from ultralytics import YOLO
        print(f"  Loading YOLOv8 fine-tuned detector: {DET_V8_PATH.name}")
        model = YOLO(str(DET_V8_PATH))
        return model, "v8"
    else:
        raise ValueError(f"Unknown mode: {mode}")


def detect_v5(model, img_path: str) -> tuple[int, int, int, int] | None:
    """Returns best bbox (x1,y1,x2,y2) or None."""
    results = model(img_path)
    df = results.pandas().xyxy[0]
    if df.empty:
        return None
    best = df.sort_values("confidence", ascending=False).iloc[0]
    return int(best["xmin"]), int(best["ymin"]), int(best["xmax"]), int(best["ymax"])


def detect_v8(model, img_path: str) -> tuple[int, int, int, int] | None:
    """Returns best bbox (x1,y1,x2,y2) or None."""
    results = model(img_path, conf=DET_CONF, verbose=False)
    if not results or len(results[0].boxes) == 0:
        return None
    boxes = results[0].boxes
    # Pick highest confidence
    confs = boxes.conf.tolist()
    best_idx = confs.index(max(confs))
    x1, y1, x2, y2 = [int(v) for v in boxes.xyxy[best_idx].tolist()]
    return x1, y1, x2, y2


def run_evaluation(detector_mode: str, limit: int | None, ocr_model) -> dict:
    """Run detector + OCR evaluation on test split."""
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]
    if limit:
        test_entries = test_entries[:limit]

    det_model, det_type = load_detector(detector_mode)

    detect_fn = detect_v5 if det_type == "v5" else detect_v8

    print(f"  Running eval on {len(test_entries)} test images...")
    total = 0
    detected = 0
    exact_match = 0
    char_correct = 0
    char_total = 0
    conf_sum = 0.0

    t0 = time.time()

    for i, entry in enumerate(test_entries):
        img_path = DATA_DIR / entry["path"].replace("\\", "/")
        if not img_path.exists():
            continue

        gt_plate = parse_ground_truth_from_filename(img_path.name)
        if not gt_plate:
            continue

        gt_norm = normalize_plate(gt_plate)
        total += 1

        bbox = detect_fn(det_model, str(img_path))
        if bbox is None:
            continue

        detected += 1
        x1, y1, x2, y2 = bbox

        img = cv2.imread(str(img_path))
        if img is None:
            continue
        crop = img[max(0, y1):y2, max(0, x1):x2]
        if crop.size == 0:
            continue

        pred_text, avg_conf = ocr_from_crop(ocr_model, crop)
        pred_norm = normalize_plate(pred_text)
        conf_sum += avg_conf

        if pred_norm == gt_norm:
            exact_match += 1

        for j in range(max(len(gt_norm), len(pred_norm))):
            char_total += 1
            if j < len(gt_norm) and j < len(pred_norm):
                if gt_norm[j] == pred_norm[j]:
                    char_correct += 1

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (len(test_entries) - i - 1) / rate if rate > 0 else 0
            print(f"    [{i+1}/{len(test_entries)}] {rate:.1f} img/s ETA {eta:.0f}s")

    elapsed = time.time() - t0

    det_rate = (detected / total * 100) if total > 0 else 0
    exact_rate = (exact_match / detected * 100) if detected > 0 else 0
    char_acc = (char_correct / char_total * 100) if char_total > 0 else 0
    avg_conf = (conf_sum / detected) if detected > 0 else 0

    return {
        "detector": detector_mode,
        "total": total,
        "detected": detected,
        "detection_rate_pct": round(det_rate, 1),
        "exact_match": exact_match,
        "exact_match_rate_pct": round(exact_rate, 1),
        "char_accuracy_pct": round(char_acc, 1),
        "avg_conf": round(avg_conf, 3),
        "elapsed_s": round(elapsed, 1),
        "img_per_s": round(total / elapsed, 1) if elapsed > 0 else 0,
    }


def print_results(r: dict) -> None:
    mode = "YOLOv5 Baseline (LP_detector.pt)" if r["detector"] == "v5" else "YOLOv8 Fine-tuned (LP_detector_finetuned.pt)"
    print(f"\n  Detector: {mode}")
    print(f"  Images evaluated:    {r['total']}")
    print(f"  Plates detected:     {r['detected']} ({r['detection_rate_pct']}%)")
    print(f"  Exact match:         {r['exact_match']} ({r['exact_match_rate_pct']}%)")
    print(f"  Char accuracy:       {r['char_accuracy_pct']}%")
    print(f"  Avg OCR confidence:  {r['avg_conf']}")
    print(f"  Throughput:          {r['img_per_s']} img/s")
    print(f"  Elapsed:             {r['elapsed_s']}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate LP detector fine-tuning impact on OCR")
    parser.add_argument("--detector", choices=["v5", "v8"], default="v8",
                        help="Which detector to eval: v5=baseline, v8=finetuned")
    parser.add_argument("--compare", action="store_true",
                        help="Compare both v5 and v8 sequentially")
    parser.add_argument("--limit", type=int, default=500,
                        help="Number of test images (default 500)")
    args = parser.parse_args()

    print("=" * 60)
    print("  LP Detector Evaluation")
    print("=" * 60)
    print(f"  Test images: {args.limit or 'all'}")

    # Load OCR model once (shared across runs)
    print("\n  Loading OCR model...")
    ocr_model = torch.hub.load("ultralytics/yolov5", "custom", path=str(OCR_MODEL_PATH), trust_repo=True)
    ocr_model.conf = OCR_CONF

    if args.compare:
        modes = ["v5", "v8"]
    else:
        modes = [args.detector]

    all_results = []
    for mode in modes:
        print(f"\n--- Evaluating {mode.upper()} ---")
        r = run_evaluation(mode, args.limit, ocr_model)
        print_results(r)
        all_results.append(r)

    if len(all_results) == 2:
        r1, r2 = all_results
        print("\n  Comparison (v8 fine-tuned vs v5 baseline):")
        det_delta = r2["detection_rate_pct"] - r1["detection_rate_pct"]
        em_delta = r2["exact_match_rate_pct"] - r1["exact_match_rate_pct"]
        char_delta = r2["char_accuracy_pct"] - r1["char_accuracy_pct"]
        print(f"    Detection rate:  {r1['detection_rate_pct']}% → {r2['detection_rate_pct']}% ({det_delta:+.1f}pp)")
        print(f"    Exact match:     {r1['exact_match_rate_pct']}% → {r2['exact_match_rate_pct']}% ({em_delta:+.1f}pp)")
        print(f"    Char accuracy:   {r1['char_accuracy_pct']}% → {r2['char_accuracy_pct']}% ({char_delta:+.1f}pp)")

        target_det = r2["detection_rate_pct"] >= 95
        target_em = em_delta >= 10
        print(f"\n  Targets:")
        print(f"    Detection ≥95%: {'PASS' if target_det else 'FAIL'} ({r2['detection_rate_pct']}%)")
        print(f"    ExactMatch +10pp: {'PASS' if target_em else 'FAIL'} ({em_delta:+.1f}pp)")

    # Save results
    out_path = PROJECT_ROOT / "data" / "processed" / "lp_detector_eval_results.json"
    out_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n  Results saved: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
