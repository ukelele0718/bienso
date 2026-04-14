"""License plate OCR using YOLOv5 character-level detection.

Handles Vietnamese 2-row plates via gap-based row clustering.
Logic adapted from scripts/eval-ocr-baseline.py.
"""

from __future__ import annotations

import re

import numpy as np
import torch

from . import config

# ── Post-processing tables ────────────────────────────────────
# Common OCR confusions: letter that looks like a digit
CHAR_TO_DIGIT: dict[str, str] = {
    "O": "0", "I": "1", "S": "5", "B": "8", "G": "6", "Z": "2", "D": "0",
}
# Common OCR confusions: digit that looks like a letter
DIGIT_TO_CHAR: dict[str, str] = {
    "0": "O", "1": "I", "5": "S", "8": "B", "6": "G", "2": "Z",
}

# Vietnamese plate regex patterns (after char-mapping, no separators)
VN_PLATE_PATTERNS: list[str] = [
    r"^\d{2}[A-Z]\d{5}$",       # 29A12345  (standard)
    r"^\d{2}[A-Z]\d{4}$",        # 29A1234   (old 7-char)
    r"^\d{2}[A-Z]{2}\d{5}$",     # 29AB12345 (2022 new format)
    r"^\d{2}[A-Z]{2}\d{4}$",     # 29AB1234
]
_COMPILED_PATTERNS = [re.compile(p) for p in VN_PLATE_PATTERNS]


def apply_char_mapping(plate_text: str) -> str:
    """Position-aware character correction for Vietnamese plates.

    Vietnamese format: XX[Y|YY]NNNNN
      - pos 0,1   → digits  (province number)
      - pos 2     → letter  (series letter)
      - pos 2,3   → letters (new 2022 two-letter series)
      - remaining → digits  (sequence number)

    Only applied when length is 7–9 (valid plate range).
    """
    if not plate_text or not (7 <= len(plate_text) <= 9):
        return plate_text

    chars = list(plate_text.upper())
    n = len(chars)

    # Determine how many leading letters the series uses (1 or 2).
    # Heuristic: if position 3 is also a letter (and we have >=9 chars or pos3 is alpha),
    # treat positions 2-3 as the letter zone.
    two_letter_series = (n >= 9) or (n >= 8 and chars[3].isalpha())
    letter_end = 4 if two_letter_series else 3  # exclusive index where digits start

    for i, ch in enumerate(chars):
        if i < 2:
            # must be digit
            if ch.isalpha() and ch in CHAR_TO_DIGIT:
                chars[i] = CHAR_TO_DIGIT[ch]
        elif i < letter_end:
            # must be letter
            if ch.isdigit() and ch in DIGIT_TO_CHAR:
                chars[i] = DIGIT_TO_CHAR[ch]
        else:
            # must be digit
            if ch.isalpha() and ch in CHAR_TO_DIGIT:
                chars[i] = CHAR_TO_DIGIT[ch]

    return "".join(chars)


def validate_vn_plate_format(plate_text: str) -> tuple[bool, str | None]:
    """Validate plate text against known Vietnamese plate patterns.

    Returns:
        (is_valid, matched_pattern_string) — matched_pattern is None when invalid.
    """
    if not plate_text:
        return False, None
    text = plate_text.upper()
    for pattern, compiled in zip(VN_PLATE_PATTERNS, _COMPILED_PATTERNS):
        if compiled.match(text):
            return True, pattern
    return False, None


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
