"""AI Engine configuration — model paths, thresholds, class filters."""

from __future__ import annotations

import os
from pathlib import Path

# ── Model paths ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # datn/
MODELS_DIR = Path(os.getenv("AI_MODELS_DIR", str(_PROJECT_ROOT / "models")))

VEHICLE_MODEL = MODELS_DIR / os.getenv("AI_VEHICLE_MODEL", "yolov8n.pt")
PLATE_MODEL = MODELS_DIR / os.getenv("AI_PLATE_MODEL", "LP_detector.pt")
OCR_MODEL = MODELS_DIR / os.getenv("AI_OCR_MODEL", "LP_ocr.pt")

# ── Confidence thresholds ────────────────────────────────────
VEHICLE_CONFIDENCE = float(os.getenv("AI_VEHICLE_CONF", "0.5"))
PLATE_CONFIDENCE = float(os.getenv("AI_PLATE_CONF", "0.5"))
OCR_CONFIDENCE = float(os.getenv("AI_OCR_CONF", "0.3"))

# ── Vehicle classes (COCO) ───────────────────────────────────
VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]

# ── Tracker ──────────────────────────────────────────────────
TRACKER_MAX_AGE = int(os.getenv("AI_TRACKER_MAX_AGE", "1"))
TRACKER_MIN_HITS = int(os.getenv("AI_TRACKER_MIN_HITS", "3"))
TRACKER_IOU_THRESHOLD = float(os.getenv("AI_TRACKER_IOU", "0.3"))

# ── OCR row clustering ───────────────────────────────────────
OCR_ROW_GAP_RATIO = float(os.getenv("AI_OCR_ROW_GAP", "0.30"))

# ── OCR post-processing ──────────────────────────────────────
ENABLE_CHAR_MAPPING = os.environ.get("ENABLE_CHAR_MAPPING", "false").lower() == "true"
ENABLE_PLATE_VALIDATION = os.environ.get("ENABLE_PLATE_VALIDATION", "true").lower() == "true"

# ── OCR backend ──────────────────────────────────────────────
# "yolo"   — LP_ocr.pt char-level detection (default, fast ~1.5 img/s)
# "paddle" — PaddleOCR PP-OCRv5 (more accurate, ~1.0 img/s CPU)
# Override via: OCR_BACKEND=paddle
OCR_BACKEND = os.environ.get("OCR_BACKEND", "yolo").lower()

# ── Snapshot saving ──────────────────────────────────────────
SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR", "snapshots")
SNAPSHOT_PADDING = float(os.environ.get("SNAPSHOT_PADDING", "0.15"))
ENABLE_SNAPSHOT = os.environ.get("ENABLE_SNAPSHOT", "true").lower() == "true"
