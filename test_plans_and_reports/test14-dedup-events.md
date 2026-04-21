# Test 14: Server-side Event Deduplication by Plate + Direction + Time Window

**Date**: 2026-04-21
**Status**: DONE — 91/91 tests pass

---

## Problem

Same license plate generated multiple events when SORT assigned a new `track_id` mid-video (track loss/re-acquisition). Example: plate `36H82613` produced 2 events in a 101-frame test.

Client-side dedup by `(track_id, plate_text)` is insufficient because `track_id` changes on every new SORT track. The backend had no dedup at all.

---

## Implementation

### 1. Config: `apps/backend/app/config.py`

Added field to `Settings`:

```python
event_dedup_window_sec: int = 30  # Set to 0 to disable
```

Env var: `APP_EVENT_DEDUP_WINDOW_SEC`. Default 30 seconds. Setting to 0 disables dedup entirely.

### 2. Logic: `apps/backend/app/crud.py`

Added a dedup check **at the top** of `create_event()`, before the camera lookup and any DB writes:

```python
raw_plate = payload.get("plate_text")
dedup_plate = normalize_plate_text(raw_plate) if raw_plate else None
if dedup_plate and settings.event_dedup_window_sec > 0:
    cutoff = payload["timestamp"] - timedelta(seconds=settings.event_dedup_window_sec)
    recent_event = db.execute(
        select(VehicleEvent)
        .join(PlateRead, PlateRead.event_id == VehicleEvent.id)
        .where(PlateRead.plate_text == dedup_plate)
        .where(VehicleEvent.direction == payload["direction"])
        .where(VehicleEvent.timestamp >= cutoff)
        .order_by(VehicleEvent.timestamp.desc())
        .limit(1)
    ).scalar_one_or_none()
    if recent_event is not None:
        recent_barrier = db.execute(
            select(BarrierAction).where(BarrierAction.event_id == recent_event.id)
        ).scalar_one_or_none()
        return recent_event, recent_barrier
```

Key design decisions:
- Dedup key is `(plate_text, direction)` — same plate going IN vs OUT are different events
- Returns the **original** event + barrier so the AI Engine response is identical to a fresh create
- Uses `payload["timestamp"]` (not `datetime.now()`) so replaying historical data works correctly
- No balance charge on deduped events (the early return skips all charge/transaction logic)
- Pure SQLAlchemy ORM, no raw SQL — compatible with both SQLite (tests) and PostgreSQL (prod)

---

## Test Coverage: `apps/backend/tests/test_dedup_events.py`

| Test | Scenario | Result |
|------|----------|--------|
| `test_dedup_same_plate_same_direction_skipped` | 2 POSTs within 5s, same plate+direction → same event_id returned, 1 row in DB | PASS |
| `test_dedup_same_plate_different_direction_not_skipped` | IN then OUT within 3s → 2 separate events | PASS |
| `test_dedup_after_window_expires` | 2nd POST at +35s, window=30s → 2 events | PASS |
| `test_dedup_different_plates_not_skipped` | Different plates at same timestamp → 2 events | PASS |
| `test_dedup_disabled_with_zero_window` | `event_dedup_window_sec=0` → no dedup, 2 events | PASS |

---

## Edge Cases Considered

| Case | Handled? |
|------|---------|
| No plate_text (OCR failed) | Yes — dedup skipped when `plate_text` is None/empty |
| Different direction, same plate | Yes — IN and OUT are independent dedup keys |
| Window boundary exact (=30s) | `>=` cutoff means events exactly at boundary ARE within window |
| Dedup disabled | Yes — `window_sec=0` bypasses check entirely |
| Response consistency | Yes — deduped return uses original event + barrier, same JSON shape |
| Balance charges | Yes — deduped events do NOT charge account again (early return) |
| Postgres compat | Yes — ORM query uses standard SQLAlchemy, no SQLite-specific syntax |

---

## Side Effect: Fixed `test_balance_can_be_negative`

The existing test sent 60 events all with `datetime.now(UTC)` (same instant). With dedup active, only 2 events survived (1 IN + 1 OUT). Fixed by spacing timestamps 31s apart, so each event falls outside the 30s dedup window. Behavior tested remains the same: 60 charges deplete balance below zero.

---

## Test Run Results

```
91 passed, 2 warnings in 4.27s
```

- Before: 86 existing tests (all passing)
- Added: 5 new dedup tests
- Fixed: 1 pre-existing test affected by dedup behavior (`test_balance_can_be_negative`)
- Total: 91/91 PASS

---

## Files Modified

| File | Change |
|------|--------|
| `apps/backend/app/config.py` | Added `event_dedup_window_sec: int = 30` to `Settings` |
| `apps/backend/app/crud.py` | Added `timedelta` import + dedup block at top of `create_event()` |
| `apps/backend/tests/test_dedup_events.py` | New file — 5 dedup tests |
| `apps/backend/tests/test_balance_rule.py` | Fixed `test_balance_can_be_negative` — use spaced timestamps |

Files NOT touched (as required): `schemas.py`, `main.py`, `barrier_rules.py`

---

## E2E Impact (trungdinh22-demo.mp4)

Not run — would require GPU/video. Expected improvement: plate `36H82613` (and similar re-tracked plates) will generate 1 event per 30-second window per direction instead of multiple. Barrier logic remains identical for the deduplicated response.

To verify manually:
```bash
PYTHONIOENCODING=utf-8 python scripts/run-e2e-demo.py \
  --video data/test-videos/trungdinh22-demo.mp4 --visual --max-frames 101
```
Compare event count in dashboard before/after.
