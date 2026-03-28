from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


def _event_payload(
    plate_text: str,
    direction: str,
    vehicle_type: str = "motorbike",
    track_id: str = "track-template",
) -> dict:
    return {
        "camera_id": TEST_CAMERA_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "direction": direction,
        "vehicle_type": vehicle_type,
        "track_id": track_id,
        "plate_text": plate_text,
        "confidence": 0.95,
        "snapshot_url": None,
    }


def test_event_response_contains_barrier_fields(client: TestClient) -> None:
    payload = _event_payload("29A-55555", "in", track_id="barrier-api-1")
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert "barrier_action" in body
    assert "barrier_reason" in body
    assert "registration_status" in body


def test_unknown_vehicle_in_auto_temporary_register(client: TestClient) -> None:
    payload = _event_payload("30F-88888", "in", track_id="barrier-api-2")
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert body["registration_status"] == "temporary_registered"
    assert body["barrier_action"] == "open"


def test_temporary_vehicle_out_hold_then_verify_open(client: TestClient) -> None:
    plate = "30F-99999"

    in_res = client.post("/api/v1/events", json=_event_payload(plate, "in", track_id="barrier-api-3-in"))
    assert in_res.status_code == 200

    out_res = client.post("/api/v1/events", json=_event_payload(plate, "out", track_id="barrier-api-3-out"))
    assert out_res.status_code == 200
    out_body = out_res.json()
    assert out_body["barrier_action"] == "hold"
    assert out_body["needs_verification"] is True

    verify_res = client.post(f"/api/v1/barrier-actions/verify?plate={plate}&actor=guard_1")
    assert verify_res.status_code == 200
    verify_body = verify_res.json()
    assert verify_body["barrier_action"] == "open"
    assert verify_body["needs_verification"] is False
    assert verify_body["verified_by"] == "guard_1"


def test_barrier_log_query(client: TestClient) -> None:
    plate = "51A-12345"
    client.post("/api/v1/events", json=_event_payload(plate, "in", track_id="barrier-api-4-in"))
    client.post("/api/v1/events", json=_event_payload(plate, "out", track_id="barrier-api-4-out"))

    logs_res = client.get(f"/api/v1/barrier-actions?plate={plate}")
    assert logs_res.status_code == 200
    rows = logs_res.json()
    assert len(rows) >= 2
    assert "barrier_reason" in rows[0]
    assert "created_at" in rows[0]
