"""
Tests for server-side event deduplication by (plate_text, direction) within a time window.

Dedup logic: if an event for the same (plate, direction) exists within
APP_EVENT_DEDUP_WINDOW_SEC seconds, return the existing event instead of creating a new one.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import PlateRead

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


def _event_payload(
    plate_text: str,
    direction: str = "in",
    timestamp: datetime | None = None,
) -> dict:
    ts = timestamp or datetime.now(UTC)
    return {
        "camera_id": TEST_CAMERA_ID,
        "timestamp": ts.isoformat(),
        "direction": direction,
        "vehicle_type": "motorbike",
        "track_id": f"track-dedup-{plate_text}-{direction}",
        "plate_text": plate_text,
        "confidence": 0.92,
        "snapshot_url": None,
    }


def _count_events_for_plate(db: Session, plate_text: str) -> int:
    """Count distinct PlateRead rows linked to the given plate_text."""
    rows = db.query(PlateRead).filter(PlateRead.plate_text == plate_text).all()
    return len(rows)


# ---------------------------------------------------------------------------
# Test 1: same plate + same direction within window → only 1 event created
# ---------------------------------------------------------------------------

def test_dedup_same_plate_same_direction_skipped(
    client: TestClient, db_session: Session
) -> None:
    """Two POSTs within 5 s for same (plate, direction) → only 1 event in DB."""
    plate = "36H82613"
    now = datetime.now(UTC)

    res1 = client.post("/api/v1/events", json=_event_payload(plate, "in", now))
    assert res1.status_code == 200

    # Second event 5 seconds later — within default 30-second window
    res2 = client.post("/api/v1/events", json=_event_payload(plate, "in", now + timedelta(seconds=5)))
    assert res2.status_code == 200

    # Should return the SAME event id
    assert res1.json()["id"] == res2.json()["id"]

    # Only one PlateRead row for this plate
    count = _count_events_for_plate(db_session, plate)
    assert count == 1


# ---------------------------------------------------------------------------
# Test 2: same plate but different direction → both created
# ---------------------------------------------------------------------------

def test_dedup_same_plate_different_direction_not_skipped(
    client: TestClient, db_session: Session
) -> None:
    """IN then OUT for same plate within window → both events created."""
    plate = "51G12300"
    now = datetime.now(UTC)

    res_in = client.post("/api/v1/events", json=_event_payload(plate, "in", now))
    assert res_in.status_code == 200

    res_out = client.post("/api/v1/events", json=_event_payload(plate, "out", now + timedelta(seconds=3)))
    assert res_out.status_code == 200

    # Different event ids
    assert res_in.json()["id"] != res_out.json()["id"]

    # Two PlateRead rows (one per event)
    count = _count_events_for_plate(db_session, plate)
    assert count == 2


# ---------------------------------------------------------------------------
# Test 3: 2nd POST arrives after the window expires → both created
# ---------------------------------------------------------------------------

def test_dedup_after_window_expires(
    client: TestClient, db_session: Session
) -> None:
    """2nd POST with timestamp 35 s later → new event created (window is 30 s)."""
    plate = "29B99001"
    now = datetime.now(UTC)

    res1 = client.post("/api/v1/events", json=_event_payload(plate, "in", now))
    assert res1.status_code == 200

    # 35 seconds later — outside the 30-second dedup window
    res2 = client.post("/api/v1/events", json=_event_payload(plate, "in", now + timedelta(seconds=35)))
    assert res2.status_code == 200

    # Different event ids — second one was NOT deduped
    assert res1.json()["id"] != res2.json()["id"]

    count = _count_events_for_plate(db_session, plate)
    assert count == 2


# ---------------------------------------------------------------------------
# Test 4: different plates → both created regardless
# ---------------------------------------------------------------------------

def test_dedup_different_plates_not_skipped(
    client: TestClient, db_session: Session
) -> None:
    """Different plates at the same moment → both events created."""
    now = datetime.now(UTC)

    res1 = client.post("/api/v1/events", json=_event_payload("30F11111", "in", now))
    assert res1.status_code == 200

    res2 = client.post("/api/v1/events", json=_event_payload("30F22222", "in", now))
    assert res2.status_code == 200

    assert res1.json()["id"] != res2.json()["id"]

    assert _count_events_for_plate(db_session, "30F11111") == 1
    assert _count_events_for_plate(db_session, "30F22222") == 1


# ---------------------------------------------------------------------------
# Test 5: dedup disabled when window = 0 → duplicate created
# ---------------------------------------------------------------------------

def test_dedup_disabled_with_zero_window(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With event_dedup_window_sec=0, no dedup occurs → both events created."""
    from app.config import settings

    monkeypatch.setattr(settings, "event_dedup_window_sec", 0)

    plate = "99X00001"
    now = datetime.now(UTC)

    res1 = client.post("/api/v1/events", json=_event_payload(plate, "in", now))
    assert res1.status_code == 200

    res2 = client.post("/api/v1/events", json=_event_payload(plate, "in", now + timedelta(seconds=2)))
    assert res2.status_code == 200

    # When dedup is off, both events are stored
    assert res1.json()["id"] != res2.json()["id"]

    count = _count_events_for_plate(db_session, plate)
    assert count == 2
