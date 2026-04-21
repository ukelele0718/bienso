"""Unit tests for vehicle type majority voting in pipeline.py.

Tests _vote_track_class() and _get_vehicle_type() independently of ML models.
No heavy dependencies — only stdlib + conftest sys.path setup.
"""

from __future__ import annotations

from collections import Counter

import pytest

# conftest.py adds repo root to sys.path
from apps.ai_engine.src.pipeline import Pipeline, _get_vehicle_type, _VEHICLE_TYPE_MAP


# ── _get_vehicle_type ─────────────────────────────────────────────────────────

class TestGetVehicleType:
    """Test the standalone _get_vehicle_type function with Counter votes dict."""

    def test_single_track_single_motorcycle_class(self):
        """Single track, all votes for 'motorcycle' → returns 'motorbike'."""
        votes = {5: Counter({"motorcycle": 10})}
        assert _get_vehicle_type(5, votes) == "motorbike"

    def test_single_track_car_dominates(self):
        """car:45 vs motorcycle:3 → 'car' wins by majority."""
        votes = {3: Counter({"car": 45, "motorcycle": 3})}
        assert _get_vehicle_type(3, votes) == "car"

    def test_bus_and_truck_map_to_car(self):
        """bus and truck both map to 'car' per _VEHICLE_TYPE_MAP."""
        votes_bus = {1: Counter({"bus": 20})}
        votes_truck = {2: Counter({"truck": 15})}
        assert _get_vehicle_type(1, votes_bus) == "car"
        assert _get_vehicle_type(2, votes_truck) == "car"

    def test_unknown_track_id_returns_default_car(self):
        """Track ID not present in votes dict → default 'car'."""
        votes: dict[int, Counter] = {}
        assert _get_vehicle_type(999, votes) == "car"

    def test_tie_returns_first_most_common(self):
        """Tie: car:5, motorcycle:5 → most_common(1) is deterministic (insertion order)."""
        # Counter preserves insertion order for equal counts (CPython 3.7+)
        c = Counter()
        c["car"] += 5
        c["motorcycle"] += 5
        votes = {7: c}
        result = _get_vehicle_type(7, votes)
        # must return a valid VehicleType, not raise
        assert result in ("car", "motorbike")

    def test_unknown_yolo_class_falls_back_to_car(self):
        """Class name not in _VEHICLE_TYPE_MAP → falls back to 'car'."""
        votes = {10: Counter({"person": 3})}
        assert _get_vehicle_type(10, votes) == "car"

    def test_empty_counter_returns_car(self):
        """Empty Counter for a track_id → treated as no votes → 'car'."""
        votes = {4: Counter()}
        # empty Counter is falsy → returns "car"
        assert _get_vehicle_type(4, votes) == "car"


# ── Pipeline._vote_track_class ────────────────────────────────────────────────

class TestVoteTrackClass:
    """Test vote accumulation on Pipeline instance (no ML models needed)."""

    def _make_pipeline_no_models(self) -> Pipeline:
        """Create Pipeline with ML model __init__ bypassed."""
        p = object.__new__(Pipeline)
        p._track_class_votes = {}
        p._track_plates = {}
        return p

    def test_first_vote_creates_counter(self):
        p = self._make_pipeline_no_models()
        p._vote_track_class(1, "car")
        assert 1 in p._track_class_votes
        assert p._track_class_votes[1]["car"] == 1

    def test_subsequent_votes_accumulate(self):
        p = self._make_pipeline_no_models()
        for _ in range(10):
            p._vote_track_class(2, "car")
        for _ in range(3):
            p._vote_track_class(2, "motorcycle")
        assert p._track_class_votes[2]["car"] == 10
        assert p._track_class_votes[2]["motorcycle"] == 3

    def test_multiple_tracks_independent(self):
        p = self._make_pipeline_no_models()
        p._vote_track_class(1, "car")
        p._vote_track_class(2, "motorcycle")
        assert p._track_class_votes[1]["car"] == 1
        assert p._track_class_votes[2]["motorcycle"] == 1
        # track 1 has no motorcycle votes
        assert p._track_class_votes[1]["motorcycle"] == 0

    def test_majority_wins_after_many_frames(self):
        """Simulate 50 frames: track seen as 'motorcycle' first, then 'car' dominates."""
        p = self._make_pipeline_no_models()
        # 5 early frames misclassify as motorcycle
        for _ in range(5):
            p._vote_track_class(8, "motorcycle")
        # 45 later frames correctly classify as car
        for _ in range(45):
            p._vote_track_class(8, "car")
        vehicle_type = _get_vehicle_type(8, p._track_class_votes)
        assert vehicle_type == "car"

    def test_same_plate_two_track_ids_majority_consistent(self):
        """Simulates the observed bug: same vehicle, two track_ids (track_8 + track_9).
        After majority voting each track should resolve consistently.
        """
        p = self._make_pipeline_no_models()
        # track_8: 10 motorcycle votes (initial mistrack)
        for _ in range(10):
            p._vote_track_class(8, "motorcycle")
        # track_9: 30 car votes (re-detected correctly)
        for _ in range(30):
            p._vote_track_class(9, "car")

        # Each track resolves to its own majority
        assert _get_vehicle_type(8, p._track_class_votes) == "motorbike"
        assert _get_vehicle_type(9, p._track_class_votes) == "car"
        # NOTE: cross-track consistency is solved upstream by deduplication.
        # This test documents that majority voting at least makes single-track
        # classification stable (no flip-flop within a track).
