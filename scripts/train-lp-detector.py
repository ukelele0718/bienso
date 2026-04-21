"""Fine-tune a YOLOv8 license plate detector on the VNLP dataset.

Strategy:
- Start from yolov8n.pt (nano, 3.2M params) — fine-tuned to plate detection
- LP_detector.pt is YOLOv5 format (cannot be loaded by ultralytics directly)
- Train on VNLP train split (29,837 images), validate on val split (3,729 images)
- Target: 5-10 epochs within 2-hour time budget on GTX 1650 4GB

Usage:
    python scripts/train-lp-detector.py [--epochs 5] [--batch 8] [--img 640]

Output:
    runs/lp_detector_finetune/  -- training artifacts
    models/LP_detector_finetuned.pt  -- best weights copy
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_YAML = PROJECT_ROOT / "data" / "yolo-vnlp" / "data.yaml"
OUT_MODELS = PROJECT_ROOT / "models"
RUNS_DIR = PROJECT_ROOT / "runs"
BASE_WEIGHTS = PROJECT_ROOT / "models" / "yolov8n.pt"
RUN_NAME = "lp_detector_finetune"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8n plate detector on VNLP")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs (default: 5)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default: 8, reduce to 4 if OOM)")
    parser.add_argument("--img", type=int, default=640, help="Image size (default: 640)")
    parser.add_argument("--device", type=str, default="0", help="Device: '0' for GPU, 'cpu' for CPU")
    parser.add_argument("--workers", type=int, default=2, help="DataLoader workers (default: 2)")
    return parser.parse_args()


def check_prerequisites() -> None:
    if not DATA_YAML.exists():
        print(f"ERROR: data.yaml not found at {DATA_YAML}")
        print("  Run: python scripts/convert-vnlp-to-yolo.py first")
        sys.exit(1)

    if not BASE_WEIGHTS.exists():
        print(f"WARNING: {BASE_WEIGHTS} not found. Ultralytics will auto-download yolov8n.pt")

    train_dir = PROJECT_ROOT / "data" / "yolo-vnlp" / "train" / "images"
    if not train_dir.exists() or not any(train_dir.iterdir()):
        print(f"ERROR: Training images not found at {train_dir}")
        sys.exit(1)

    n_train = sum(1 for _ in train_dir.iterdir())
    print(f"  Training images found: {n_train}")


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("  LP Detector Fine-tuning (YOLOv8n on VNLP)")
    print("=" * 60)
    print(f"  Epochs:     {args.epochs}")
    print(f"  Batch:      {args.batch}")
    print(f"  Img size:   {args.img}")
    print(f"  Device:     {args.device}")
    print(f"  Data yaml:  {DATA_YAML}")
    print(f"  Base model: {BASE_WEIGHTS}")
    print()

    check_prerequisites()

    # Import ultralytics YOLO
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not installed. Run: pip install ultralytics")
        sys.exit(1)

    import torch
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name()}")
        mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  GPU memory: {mem:.1f} GB")

    # Load base model
    weights_path = str(BASE_WEIGHTS) if BASE_WEIGHTS.exists() else "yolov8n.pt"
    print(f"\n  Loading base model: {weights_path}")
    model = YOLO(weights_path)

    # Start training
    print(f"\n  Starting training...")
    t0 = time.time()

    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        results = model.train(
            data=str(DATA_YAML),
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.img,
            device=args.device,
            workers=args.workers,
            project=str(RUNS_DIR),
            name=RUN_NAME,
            exist_ok=True,
            # Optimizer settings
            optimizer="auto",
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=2.0,
            # Augmentation (moderate for fine-tuning)
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.0,
            # Logging
            verbose=True,
            save=True,
            save_period=-1,  # Only save best/last
            plots=True,
            val=True,
        )
        elapsed = time.time() - t0
        print(f"\n  Training complete in {elapsed/60:.1f} minutes")

    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print(f"\nERROR: GPU OOM! Try reducing batch size: --batch {args.batch // 2}")
            print(f"  Or reduce image size: --img 416")
        raise

    # Find best weights
    best_weights = RUNS_DIR / RUN_NAME / "weights" / "best.pt"
    last_weights = RUNS_DIR / RUN_NAME / "weights" / "last.pt"

    weights_to_copy = best_weights if best_weights.exists() else last_weights
    dst = OUT_MODELS / "LP_detector_finetuned.pt"

    if weights_to_copy.exists():
        shutil.copy2(weights_to_copy, dst)
        print(f"\n  Saved fine-tuned model to: {dst}")
    else:
        print(f"\nWARNING: Could not find weights at {best_weights} or {last_weights}")

    # Print final metrics summary
    print("\n  Final training metrics:")
    if hasattr(results, "results_dict"):
        for k, v in results.results_dict.items():
            if isinstance(v, float):
                print(f"    {k}: {v:.4f}")

    print(f"\n  Run artifacts: {RUNS_DIR / RUN_NAME}")
    print("=" * 60)


if __name__ == "__main__":
    main()
