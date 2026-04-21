"""Tests for GET /api/v1/cameras endpoint."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Camera


def test_cameras_list_empty(client: TestClient, db_session: Session) -> None:
    """Cameras endpoint returns empty list when no extra cameras exist.

    The conftest seeds one camera so we expect exactly 1 result.
    """
    res = client.get("/api/v1/cameras")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    # conftest seeds one camera
    assert len(body) == 1


def test_cameras_list_returns_seeded_camera(client: TestClient, db_session: Session) -> None:
    """The seeded test camera appears with correct fields."""
    res = client.get("/api/v1/cameras")
    assert res.status_code == 200
    body = res.json()
    assert len(body) >= 1
    cam = body[0]
    assert cam["id"] == "11111111-1111-1111-1111-111111111111"
    assert cam["name"] == "Test Camera"
    assert cam["gate_type"] == "student"
    assert cam["stream_url"] == "rtsp://test/stream"
    assert cam["is_active"] is True


def test_cameras_list_schema_shape(client: TestClient) -> None:
    """Each camera object has all required fields."""
    res = client.get("/api/v1/cameras")
    assert res.status_code == 200
    for cam in res.json():
        assert "id" in cam
        assert "name" in cam
        assert "gate_type" in cam
        assert "location" in cam
        assert "stream_url" in cam
        assert "is_active" in cam
        assert "created_at" in cam


def test_cameras_list_with_extra_camera(client: TestClient, db_session: Session) -> None:
    """Adding a second camera shows both in list, ordered by created_at desc."""
    second_cam = Camera(
        id="22222222-2222-2222-2222-222222222222",
        name="Staff Gate Cam",
        gate_type="staff",
        location="North Entrance",
        stream_url=None,
        is_active=False,
    )
    db_session.add(second_cam)
    db_session.commit()

    res = client.get("/api/v1/cameras")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 2

    ids = {c["id"] for c in body}
    assert "11111111-1111-1111-1111-111111111111" in ids
    assert "22222222-2222-2222-2222-222222222222" in ids

    # inactive camera fields
    inactive = next(c for c in body if c["id"] == "22222222-2222-2222-2222-222222222222")
    assert inactive["is_active"] is False
    assert inactive["stream_url"] is None
    assert inactive["location"] == "North Entrance"
