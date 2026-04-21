# Test 9: Vehicle Type Majority Voting

**Date**: 2026-04-21
**Status**: PASS

---

## Problem

In `pipeline.py`, vehicle type was stored as the class observed at **first detection**:

```python
self._track_classes: dict[int, str] = {}          # before
self._track_classes[best_tid] = vd.class_name     # overwrites on re-detection
```

When a vehicle disappears and SORT creates a new `track_id`, YOLOv8 might temporarily
classify it differently. Observed on `trungdinh22-demo.mp4`:

| track_id | plate      | vehicle_type (before) |
|----------|------------|-----------------------|
| track_8  | 14K117970  | motorbike             |
| track_9  | 14K117970  | car                   |

Same physical vehicle → 2 conflicting types. 1/3 mismatch (50% wrong for that plate).

---

## Fix

Replaced `_track_classes: dict[int, str]` with `_track_class_votes: dict[int, Counter]`.

Each frame's detection casts one vote. `_get_vehicle_type()` reads the majority winner:

```python
self._track_class_votes: dict[int, Counter] = {}

def _vote_track_class(self, track_id: int, class_name: str) -> None:
    if track_id not in self._track_class_votes:
        self._track_class_votes[track_id] = Counter()
    self._track_class_votes[track_id][class_name] += 1

def _get_vehicle_type(track_id: int, vehicle_classes: dict[int, Counter]) -> VehicleType:
    votes = vehicle_classes.get(track_id)
    if not votes:
        return "car"
    most_common_cls = votes.most_common(1)[0][0]
    return _VEHICLE_TYPE_MAP.get(most_common_cls, "car")
```

Vote logging added at event emit:
```
log.info("track=%s votes=%s → %s", tid, dict(votes), vehicle_type)
```

Files changed:
- `apps/ai_engine/src/pipeline.py` — imports `Counter`, replaces dict, adds `_vote_track_class()`, updates both `process_frame` and `process_frame_visual`

---

## Unit Tests

File: `apps/ai_engine/tests/test_vehicle_majority_voting.py`

### Results

```
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_single_track_single_motorcycle_class  PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_single_track_car_dominates           PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_bus_and_truck_map_to_car             PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_unknown_track_id_returns_default_car PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_tie_returns_first_most_common        PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_unknown_yolo_class_falls_back_to_car PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestGetVehicleType::test_empty_counter_returns_car            PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestVoteTrackClass::test_first_vote_creates_counter           PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestVoteTrackClass::test_subsequent_votes_accumulate          PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestVoteTrackClass::test_multiple_tracks_independent          PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestVoteTrackClass::test_majority_wins_after_many_frames      PASSED
apps/ai_engine/tests/test_vehicle_majority_voting.py::TestVoteTrackClass::test_same_plate_two_track_ids_majority_consistent PASSED

12 passed
```

Total AI engine tests: **45/45 passed** (33 OCR + 12 new majority voting).

---

## All Tests

| Suite                  | Count | Status |
|------------------------|-------|--------|
| AI engine (OCR)        | 33    | PASS   |
| AI engine (voting new) | 12    | PASS   |
| Backend                | 86    | PASS   |

Backend tests: run via `python -m pytest apps/backend/tests/ -v` — 86 passed, 2 deprecation warnings (unrelated to this change).

---

## E2E Demo — Before vs After

Video: `data/test-videos/trungdinh22-demo.mp4`, max-frames=300, --no-backend

### Before (first-detection wins)

| plate      | track_id | vehicle_type |
|------------|----------|--------------|
| 36H82613   | track_3  | car          |
| 36H82613   | track_5  | car          |
| 14K117970  | track_8  | **motorbike** |
| 14K117970  | track_9  | **car**       |

Same physical vehicle `14K117970` → conflicting types across track IDs.

### After (majority voting)

```
[detect] car       track=track_3    plate=36H82613       conf=0.90
[detect] car       track=track_5    plate=36H82613       conf=0.90
[detect] car       track=track_8    plate=14K117970      conf=0.85
[detect] car       track=track_9    plate=14K117970      conf=0.86
```

| plate      | track_id | vehicle_type |
|------------|----------|--------------|
| 36H82613   | track_3  | car          |
| 36H82613   | track_5  | car          |
| 14K117970  | track_8  | **car**      |
| 14K117970  | track_9  | **car**      |

Mismatch eliminated. Both track_8 and track_9 for plate `14K117970` now resolve to `car`.

Demo stats: 300 frames, 29.9s, 23 raw events → 4 unique sent.

---

## Recommendation

Majority voting is a minimal, zero-cost fix that makes per-track classification stable
against transient misdetections. It does NOT fix the cross-track duplication (same plate
appearing under two track_ids) — that is a known separate issue (deduplication by
`plate_text` is listed in CLAUDE.md "Còn lại"). The voting fix is a prerequisite for any
future deduplication logic: once you merge events by plate_text, the vehicle_type must
already be consistent across tracks, which this fix ensures.

No changes to `_VEHICLE_TYPE_MAP`, barrier rules, or backend API — callers unaffected.
