"""Unit tests for normalize_plate_text function."""
from __future__ import annotations

import pytest

from app.crud import normalize_plate_text


class TestNormalizePlateText:
    """Test plate text normalization (strips non-alphanumeric, uppercases)."""

    def test_standard_one_row_plate(self) -> None:
        assert normalize_plate_text("29A-12345") == "29A12345"

    def test_standard_two_row_plate(self) -> None:
        assert normalize_plate_text("51G-123.45") == "51G12345"

    def test_already_normalized(self) -> None:
        assert normalize_plate_text("29A12345") == "29A12345"

    def test_lowercase_to_uppercase(self) -> None:
        assert normalize_plate_text("29a-12345") == "29A12345"

    def test_mixed_case(self) -> None:
        assert normalize_plate_text("51g-123.Ab") == "51G123AB"

    def test_spaces_stripped(self) -> None:
        assert normalize_plate_text("29A 123 45") == "29A12345"

    def test_special_characters_stripped(self) -> None:
        assert normalize_plate_text("29A/12345!@#") == "29A12345"

    def test_dots_stripped(self) -> None:
        assert normalize_plate_text("51G.123.45") == "51G12345"

    def test_empty_string(self) -> None:
        assert normalize_plate_text("") == ""

    def test_only_special_chars(self) -> None:
        assert normalize_plate_text("---...") == ""

    def test_confusable_chars_preserved(self) -> None:
        """O/0, I/1, B/8, S/5 are kept as-is (no substitution in normalize)."""
        assert normalize_plate_text("O0I1B8S5") == "O0I1B8S5"

    def test_unicode_stripped(self) -> None:
        # Unicode chars like Ã are non-alphanumeric and get stripped along with dashes
        assert normalize_plate_text("29Ã-12345") == "2912345"

    def test_tabs_newlines_stripped(self) -> None:
        assert normalize_plate_text("29A\t123\n45") == "29A12345"
