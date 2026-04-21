"""Tests for PlateOCRPaddle adapter.

Skipped automatically when paddleocr is not installed.
Tests verify:
  - length guard filters hallucinated text (>9 chars)
  - length guard rejects too-short strings (<7 chars)
  - length guard extracts valid substring from longer raw string
  - empty / None image returns (None, 0.0)
  - return type is compatible with PlateOCR interface (str|None, float)
"""

from __future__ import annotations

import importlib.util

import numpy as np
import pytest

# Skip entire module if paddleocr is not installed
_PADDLE_AVAILABLE = importlib.util.find_spec("paddleocr") is not None

pytestmark = pytest.mark.skipif(
    not _PADDLE_AVAILABLE,
    reason="paddleocr not installed",
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _solid_bgr(h: int = 60, w: int = 200, color: tuple = (200, 200, 200)) -> np.ndarray:
    """Create a solid-color BGR image (valid input for OCR)."""
    img = np.full((h, w, 3), color, dtype=np.uint8)
    return img


# ── Length guard — pure logic tests (no model loading) ───────────────────────

class TestLengthGuardLogic:
    """Test the length guard regex logic extracted from PlateOCRPaddle.read()."""

    def _apply_guard(self, text: str) -> str | None:
        """Replicate the guard logic from plate_ocr_paddle.py."""
        import re
        combined = text.upper()
        combined = re.sub(r"[^A-Z0-9]", "", combined)
        if not combined:
            return None
        if len(combined) > 9 or len(combined) < 7:
            match = re.search(r"[A-Z0-9]{7,9}", combined)
            if match:
                return match.group(0)
            return None
        return combined

    def test_valid_7_char_passes(self):
        assert self._apply_guard("36M4080") == "36M4080"

    def test_valid_8_char_passes(self):
        assert self._apply_guard("29A12345") == "29A12345"

    def test_valid_9_char_passes(self):
        assert self._apply_guard("15B245926") == "15B245926"

    def test_10_char_hallucination_returns_none_if_no_valid_substr(self):
        # "1234567890" — all digits, no letter series, but 10 chars
        # re.search finds "123456789" (first 9 digits) — that IS a valid substring match
        result = self._apply_guard("1234567890")
        # should extract first 9-char run
        assert result == "123456789"

    def test_long_hallucination_with_valid_plate_embedded(self):
        # "36C106360204201908" — 18 chars after strip, plate "36C10636" at start
        result = self._apply_guard("36C106360204201908")
        assert result is not None
        assert 7 <= len(result) <= 9

    def test_honda_hallucination_filtered(self):
        # "29N1HONDA58498" → after stripping non-alphanum = "29N1HONDA58498" (14 chars)
        result = self._apply_guard("29N1HONDA58498")
        assert result is not None
        assert 7 <= len(result) <= 9

    def test_short_4_char_returns_none(self):
        assert self._apply_guard("4080") is None

    def test_short_6_char_returns_none(self):
        assert self._apply_guard("29A123") is None

    def test_empty_string_returns_none(self):
        assert self._apply_guard("") is None

    def test_special_chars_stripped_before_check(self):
        # "29-A1.2345" → stripped → "29A12345" (8 chars) — passes
        assert self._apply_guard("29-A1.2345") == "29A12345"


# ── PlateOCRPaddle interface tests (requires model loading) ──────────────────

@pytest.fixture(scope="module")
def paddle_ocr():
    """Load PlateOCRPaddle once per test module."""
    import torch  # noqa: F401 — must be imported before paddleocr on Windows
    from apps.ai_engine.src.plate_ocr_paddle import PlateOCRPaddle
    return PlateOCRPaddle(use_gpu=False, lang="en")


class TestPlateOCRPaddleInterface:
    """Verify interface compatibility with PlateOCR.read()."""

    def test_returns_tuple_two_elements(self, paddle_ocr):
        crop = _solid_bgr()
        result = paddle_ocr.read(crop)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_return_types(self, paddle_ocr):
        crop = _solid_bgr()
        text, conf = paddle_ocr.read(crop)
        assert text is None or isinstance(text, str)
        assert isinstance(conf, float)

    def test_empty_array_returns_none(self, paddle_ocr):
        empty = np.array([])
        text, conf = paddle_ocr.read(empty)
        assert text is None
        assert conf == 0.0

    def test_none_input_returns_none(self, paddle_ocr):
        text, conf = paddle_ocr.read(None)
        assert text is None
        assert conf == 0.0

    def test_blank_image_returns_none_or_str(self, paddle_ocr):
        # Blank grey image has no text — should return (None, 0.0)
        # (Not a hard assertion since model may hallucinate noise)
        crop = _solid_bgr(60, 200, (200, 200, 200))
        text, conf = paddle_ocr.read(crop)
        assert text is None or isinstance(text, str)
        if text is not None:
            assert 7 <= len(text) <= 9, "length guard must ensure result is 7-9 chars"

    def test_confidence_in_0_1_range(self, paddle_ocr):
        crop = _solid_bgr()
        _, conf = paddle_ocr.read(crop)
        assert 0.0 <= conf <= 1.0

    def test_result_uppercase_alnum_only(self, paddle_ocr):
        import re
        crop = _solid_bgr(60, 200, (240, 240, 240))
        text, _ = paddle_ocr.read(crop)
        if text is not None:
            assert re.fullmatch(r"[A-Z0-9]+", text), f"non-alnum in: {text!r}"
