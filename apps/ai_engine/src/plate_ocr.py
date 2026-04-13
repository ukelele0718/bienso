"""License plate OCR using YOLOv5 character-level detection.

Handles Vietnamese 2-row plates via gap-based row clustering.
Logic adapted from scripts/eval-ocr-baseline.py.
"""

from __future__ import annotations

import re

import numpy as np
import torch

from . import config


class PlateOCR:
    """Read license plate text from a cropped plate image."""

    def __init__(
        self,
        model_path: str | None = None,
        confidence: float | None = None,
    ) -> None:
        path = model_path or str(config.OCR_MODEL)
        self.confidence = confidence or config.OCR_CONFIDENCE
        self.model = torch.hub.load(
            "ultralytics/yolov5", "custom", path=path, trust_repo=True,
        )
        self.model.conf = self.confidence

    def read(self, plate_crop: np.ndarray) -> tuple[str | None, float]:
        """OCR a plate crop image.

        Returns:
            (plate_text, avg_confidence) or (None, 0.0) if unreadable.
        """
        if plate_crop.size == 0:
            return None, 0.0

        results = self.model(plate_crop)
        df = results.pandas().xyxy[0]

        if df.empty:
            return None, 0.0

        chars = []
        for _, row in df.iterrows():
            chars.append({
                "label": str(row["name"]),
                "x_center": (row["xmin"] + row["xmax"]) / 2,
                "y_center": (row["ymin"] + row["ymax"]) / 2,
                "height": row["ymax"] - row["ymin"],
                "confidence": row["confidence"],
            })

        text = self._cluster_and_read(chars)
        if not text:
            return None, 0.0

        avg_conf = sum(c["confidence"] for c in chars) / len(chars)
        return text, avg_conf

    def _cluster_and_read(self, chars: list[dict]) -> str:
        """Gap-based 2-row clustering for Vietnamese plates.

        Sort by Y, find largest gap between consecutive chars.
        If gap > 30% of avg char height → 2 rows.
        Each row sorted left→right, concatenated top→bottom.
        """
        if not chars:
            return ""

        # single char → return directly
        if len(chars) == 1:
            return chars[0]["label"].upper()

        sorted_by_y = sorted(chars, key=lambda c: c["y_center"])
        avg_height = sum(c["height"] for c in chars) / len(chars)

        # find largest Y gap
        max_gap = 0.0
        split_idx = -1
        for i in range(len(sorted_by_y) - 1):
            gap = sorted_by_y[i + 1]["y_center"] - sorted_by_y[i]["y_center"]
            if gap > max_gap:
                max_gap = gap
                split_idx = i

        # decide if 2-row split needed
        if max_gap > config.OCR_ROW_GAP_RATIO * avg_height and split_idx >= 0:
            top_row = sorted_by_y[: split_idx + 1]
            bottom_row = sorted_by_y[split_idx + 1:]
        else:
            top_row = sorted_by_y
            bottom_row = []

        # sort each row left→right
        top_row.sort(key=lambda c: c["x_center"])
        bottom_row.sort(key=lambda c: c["x_center"])

        text = "".join(c["label"] for c in top_row + bottom_row)
        text = re.sub(r"[^A-Za-z0-9]", "", text).upper()
        return text
