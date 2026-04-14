"""Compare OCR baseline vs post-processing on VNLP test set.

Usage: python scripts/eval-with-postprocess.py
"""
import json
import re
import sys
import time
from pathlib import Path

import cv2
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apps.ai_engine.src.plate_ocr import apply_char_mapping, validate_vn_plate_format

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "external"
MANIFEST = PROJECT_ROOT / "data" / "processed" / "dataset_manifest.json"
DET_MODEL = PROJECT_ROOT / "models" / "LP_detector.pt"
OCR_MODEL = PROJECT_ROOT / "models" / "LP_ocr.pt"
OUTPUT = PROJECT_ROOT / "data" / "processed" / "postprocess_eval_results.json"


def normalize(t):
    return re.sub(r"[^A-Za-z0-9]", "", t).upper()


def ocr_crop(model, crop):
    results = model(crop)
    df = results.pandas().xyxy[0]
    if df.empty:
        return "", 0.0
    df["xc"] = (df["xmin"] + df["xmax"]) / 2
    df["yc"] = (df["ymin"] + df["ymax"]) / 2
    avg_h = (df["ymax"] - df["ymin"]).mean()
    sy = df.sort_values("yc").reset_index(drop=True)
    yc = sy["yc"].tolist()
    si, mg = None, 0
    for i in range(len(yc) - 1):
        g = yc[i + 1] - yc[i]
        if g > mg:
            mg, si = g, i
    two = si is not None and mg > avg_h * 0.3
    if two:
        top = sy.iloc[: si + 1].sort_values("xc")
        bot = sy.iloc[si + 1 :].sort_values("xc")
        od = pd.concat([top, bot])
    else:
        od = df.sort_values("xc")
    text = "".join(str(c) for c in od["name"].tolist()).upper()
    conf = float(od["confidence"].mean())
    return text, conf


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    test_entries = [e for e in manifest["entries"] if e["split"] == "test"]

    print(f"Loading models...")
    det = torch.hub.load("ultralytics/yolov5", "custom", path=str(DET_MODEL), trust_repo=True)
    det.conf = 0.25
    ocr = torch.hub.load("ultralytics/yolov5", "custom", path=str(OCR_MODEL), trust_repo=True)
    ocr.conf = 0.25

    print(f"Running on {len(test_entries)} test images...")
    total = detected = 0
    ex_base = ex_post = 0
    cc_base = cc_post = ct_base = ct_post = 0
    valid_base = valid_post = 0
    errors = []
    t0 = time.time()

    for i, entry in enumerate(test_entries):
        p = entry["path"].replace("\\", "/")
        img_path = DATA_DIR / p
        if not img_path.exists():
            continue
        parts = img_path.stem.split("_")
        if len(parts) < 4:
            continue
        gt = normalize(parts[3])
        total += 1

        ddf = det(str(img_path)).pandas().xyxy[0]
        if ddf.empty:
            continue
        detected += 1
        best = ddf.sort_values("confidence", ascending=False).iloc[0]
        x1, y1, x2, y2 = int(best["xmin"]), int(best["ymin"]), int(best["xmax"]), int(best["ymax"])
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        crop = img[max(0, y1):y2, max(0, x1):x2]
        if crop.size == 0:
            continue

        raw, conf = ocr_crop(ocr, crop)
        base = normalize(raw)
        post = normalize(apply_char_mapping(base))

        if base == gt:
            ex_base += 1
        if post == gt:
            ex_post += 1

        vb, _ = validate_vn_plate_format(base)
        vp, _ = validate_vn_plate_format(post)
        if vb:
            valid_base += 1
        if vp:
            valid_post += 1

        # char accuracy
        for j in range(max(len(gt), len(base))):
            ct_base += 1
            if j < len(gt) and j < len(base) and gt[j] == base[j]:
                cc_base += 1
        for j in range(max(len(gt), len(post))):
            ct_post += 1
            if j < len(gt) and j < len(post) and gt[j] == post[j]:
                cc_post += 1

        if post != gt and len(errors) < 30:
            errors.append({"gt": gt, "base": base, "post": post, "file": img_path.name})

        if (i + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1}/{len(test_entries)}] {rate:.1f} img/s")

    elapsed = time.time() - t0
    ca_base = cc_base / ct_base * 100 if ct_base else 0
    ca_post = cc_post / ct_post * 100 if ct_post else 0

    results = {
        "total": total,
        "detected": detected,
        "detection_rate": round(detected / total * 100, 1) if total else 0,
        "baseline_exact": ex_base,
        "baseline_exact_rate": round(ex_base / detected * 100, 1) if detected else 0,
        "baseline_char_accuracy": round(ca_base, 1),
        "baseline_valid_format": valid_base,
        "postprocess_exact": ex_post,
        "postprocess_exact_rate": round(ex_post / detected * 100, 1) if detected else 0,
        "postprocess_char_accuracy": round(ca_post, 1),
        "postprocess_valid_format": valid_post,
        "improvement_exact": ex_post - ex_base,
        "elapsed_s": round(elapsed, 1),
        "throughput": round(total / elapsed, 1) if elapsed else 0,
        "sample_errors": errors,
    }

    print(f"\n{'='*60}")
    print(f"  OCR EVAL: BASELINE vs POST-PROCESSING ({total} images, {elapsed:.0f}s)")
    print(f"{'='*60}")
    print(f"  Detection rate:     {detected}/{total} ({results['detection_rate']}%)")
    print(f"")
    print(f"  {'':20s} {'Baseline':>12s}  {'Post-process':>12s}")
    print(f"  {'Exact match':20s} {ex_base:>5d} ({results['baseline_exact_rate']:>5.1f}%)  {ex_post:>5d} ({results['postprocess_exact_rate']:>5.1f}%)")
    print(f"  {'Char accuracy':20s} {ca_base:>11.1f}%  {ca_post:>11.1f}%")
    print(f"  {'Valid VN format':20s} {valid_base:>12d}  {valid_post:>12d}")
    print(f"")
    print(f"  Improvement: +{ex_post - ex_base} exact matches (+{(ex_post-ex_base)/detected*100:.1f}%)")
    print(f"{'='*60}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
