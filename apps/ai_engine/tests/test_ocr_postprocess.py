"""Tests for OCR post-processing: char mapping and plate format validation."""

from __future__ import annotations

import pytest

# conftest.py adds repo root to sys.path; no heavy ML deps triggered here
from apps.ai_engine.src.plate_ocr import apply_char_mapping, validate_vn_plate_format


# ── apply_char_mapping ────────────────────────────────────────────────────────

class TestApplyCharMapping:
    def test_digit_positions_correct_letter_to_digit(self):
        # "O9A12345" → pos0 'O' should become '0'
        assert apply_char_mapping("O9A12345") == "09A12345"

    def test_digit_position_1_corrected(self):
        # "2IA12345" → pos1 'I' should become '1'
        assert apply_char_mapping("2IA12345") == "21A12345"

    def test_letter_position_2_corrected_digit_to_char(self):
        # "291I2345" → pos2 '1' mapped to 'I', pos3 'I' stays (two-letter heuristic)
        assert apply_char_mapping("291I2345") == "29II2345"
        assert apply_char_mapping("29112345") == "29I12345"

    def test_trailing_digits_corrected(self):
        # "29AI234S" → pos6 'S' should become '5'
        assert apply_char_mapping("29AI234S") == "29AI2345"

    def test_all_correct_unchanged(self):
        assert apply_char_mapping("29A12345") == "29A12345"

    def test_two_letter_series_province_digits_corrected(self):
        # "O9AB12345" → pos0 'O' → '0'
        result = apply_char_mapping("O9AB12345")
        assert result[0] == "0"
        assert result[1] == "9"

    def test_two_letter_series_letters_preserved(self):
        result = apply_char_mapping("29AB12345")
        assert result[2] == "A"
        assert result[3] == "B"

    def test_trailing_digit_position_in_two_letter(self):
        # "29ABl234S" — pos8 'S' → '5'
        assert apply_char_mapping("29AB1234S") == "29AB12345"

    def test_too_short_returns_unchanged(self):
        short = "29A"
        assert apply_char_mapping(short) == short

    def test_too_long_returns_unchanged(self):
        long_plate = "29A123456789"
        assert apply_char_mapping(long_plate) == long_plate

    def test_empty_string_returns_empty(self):
        assert apply_char_mapping("") == ""

    def test_none_returns_none(self):
        # function signature accepts str, but guard against bad input
        # apply_char_mapping has `if not plate_text` guard
        assert apply_char_mapping("") == ""

    def test_b_corrected_to_8_in_digit_position(self):
        # "29A1234B" → pos7 'B' → '8'
        assert apply_char_mapping("29A1234B") == "29A12348"

    def test_z_corrected_to_2_in_digit_position(self):
        assert apply_char_mapping("29A1234Z") == "29A12342"

    def test_8_corrected_to_b_in_letter_position(self):
        # "298 12345" → pos2 '8' → 'B'
        assert apply_char_mapping("29812345") == "29B12345"

    def test_mixed_corrections(self):
        # "O9I12345" → '0','9','I'(letter ok),'1','2','3','4','5'
        # pos0 O→0, pos1 9 stays, pos2 I stays (it's a letter)
        result = apply_char_mapping("O9I12345")
        assert result == "09I12345"


# ── validate_vn_plate_format ──────────────────────────────────────────────────

class TestValidateVnPlateFormat:
    @pytest.mark.parametrize("plate,expected_valid", [
        ("29A12345", True),   # standard 8-char
        ("51B1234", True),    # old 7-char
        ("36AB12345", True),  # new 2022 9-char
        ("29AB1234", True),   # new 2022 8-char
        ("29a12345", True),   # lowercase should still match (upper() applied)
        ("9A12345", False),   # only 1 province digit
        ("29A1234567", False),# too many trailing digits
        ("ABC12345", False),  # 3 leading letters
        ("", False),          # empty
        ("2912345", False),   # missing letter series
        ("29A1234X", False),  # letter in digit zone
    ])
    def test_patterns(self, plate: str, expected_valid: bool):
        is_valid, pattern = validate_vn_plate_format(plate)
        assert is_valid == expected_valid

    def test_returns_matched_pattern_string_when_valid(self):
        is_valid, pattern = validate_vn_plate_format("29A12345")
        assert is_valid is True
        assert pattern is not None
        assert "\\d{2}" in pattern

    def test_returns_none_pattern_when_invalid(self):
        is_valid, pattern = validate_vn_plate_format("INVALID")
        assert is_valid is False
        assert pattern is None

    def test_none_input(self):
        is_valid, pattern = validate_vn_plate_format(None)  # type: ignore[arg-type]
        assert is_valid is False
        assert pattern is None


# ── Integration: mapping then validation ──────────────────────────────────────

class TestMappingThenValidation:
    def test_ocr_error_corrected_then_valid(self):
        # Raw OCR: "O9A1234S" (O instead of 0, S instead of 5)
        corrected = apply_char_mapping("O9A1234S")
        assert corrected == "09A12345"
        is_valid, _ = validate_vn_plate_format(corrected)
        assert is_valid is True

    def test_two_letter_ocr_corrected_then_valid(self):
        corrected = apply_char_mapping("O9AB1234S")
        assert corrected == "09AB12345"
        is_valid, _ = validate_vn_plate_format(corrected)
        assert is_valid is True

    def test_already_clean_plate_stays_valid(self):
        corrected = apply_char_mapping("51F12345")
        is_valid, _ = validate_vn_plate_format(corrected)
        assert is_valid is True
