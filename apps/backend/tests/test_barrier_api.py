from __future__ import annotations

"""Template API tests for barrier logic.

These tests are intentionally scaffolded so QA can fill/adjust expected fields
when barrier endpoints/response fields are finalized.
"""

from datetime import datetime

import pytest
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


@pytest.mark.api
def test_event_response_contains_barrier_fields_template(client: TestClient) -> None:
    payload = _event_payload("29A-55555", "in", track_id="barrier-api-1")
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200

    body = res.json()
    # TODO: remove skips once backend adds fields to response contract
    pytest.skip("TODO: assert barrier_action/barrier_reason/registration_status in response")
    # Example assertions:
    # assert "barrier_action" in body
    # assert "barrier_reason" in body
    # assert "registration_status" in body


@pytest.mark.api
def test_unknown_vehicle_in_auto_temporary_register_template(client: TestClient) -> None:
    payload = _event_payload("30F-88888", "in", track_id="barrier-api-2")
    res = client.post("/api/v1/events", json=payload)
    assert res.status_code == 200

    pytest.skip("TODO: assert registration_status == temporary_registered and barrier_action == open")


@pytest.mark.api
def test_temporary_vehicle_out_hold_template(client: TestClient) -> None:
    plate = "30F-99999"

    in_res = client.post("/api/v1/events", json=_event_payload(plate, "in", track_id="barrier-api-3-in"))
    assert in_res.status_code == 200

    out_res = client.post("/api/v1/events", json=_event_payload(plate, "out", track_id="barrier-api-3-out"))
    assert out_res.status_code == 200

    pytest.skip("TODO: assert second response has barrier_action == hold and needs_verification == true")


@pytest.mark.api
def test_verify_endpoint_success_template(client: TestClient) -> None:
    pytest.skip("TODO: call verify success endpoint then assert barrier opens")


@pytest.mark.api
def test_verify_endpoint_fail_template(client: TestClient) -> None:
    pytest.skip("TODO: call verify fail endpoint then assert barrier remains hold")


@pytest.mark.api
def test_barrier_log_query_template(client: TestClient) -> None:
    pytest.skip("TODO: query barrier action log endpoint and validate reason/timestamp/actor")
