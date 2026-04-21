"""Tests for /ws/events WebSocket endpoint and broadcast-on-event-create."""
from __future__ import annotations

import time
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"

_EVENT_PAYLOAD = {
    "camera_id": TEST_CAMERA_ID,
    "direction": "in",
    "vehicle_type": "car",
    "track_id": "ws-track-1",
    "plate_text": "99X99999",
    "confidence": 0.95,
    "snapshot_url": None,
}


def _ts() -> str:
    return datetime.now(UTC).isoformat()


def test_websocket_connect(client: TestClient) -> None:
    """WebSocket /ws/events accepts connection and survives a ping."""
    with client.websocket_connect("/ws/events") as ws:
        ws.send_text("ping")
        # No disconnect — connection is healthy


def test_websocket_multiple_clients_connect(client: TestClient) -> None:
    """Multiple WebSocket clients can connect simultaneously."""
    with client.websocket_connect("/ws/events") as ws1:
        with client.websocket_connect("/ws/events") as ws2:
            ws1.send_text("ping")
            ws2.send_text("ping")


def test_websocket_reconnect_after_close(client: TestClient) -> None:
    """After closing, a new connection can be established."""
    with client.websocket_connect("/ws/events") as ws:
        ws.send_text("ping")

    # Re-connect after context exit
    with client.websocket_connect("/ws/events") as ws2:
        ws2.send_text("ping")


def test_websocket_broadcast_on_event_create(client: TestClient) -> None:
    """POST /events broadcasts a new_event message to connected WebSocket clients.

    NOTE: TestClient runs in synchronous mode with a shared in-process event loop.
    The broadcast fires via asyncio.ensure_future; TestClient's context manager
    flushes pending tasks before returning from __exit__, so the message is received
    reliably within the websocket_connect context.
    """
    with client.websocket_connect("/ws/events") as ws:
        payload = {**_EVENT_PAYLOAD, "timestamp": _ts(), "track_id": "ws-broadcast-1"}
        response = client.post("/api/v1/events", json=payload)
        assert response.status_code == 200

        # Receive broadcast with timeout
        data = ws.receive_json()
        assert data["type"] == "new_event"
        assert data["plate_text"] == "99X99999"
        assert data["direction"] == "in"
        assert data["vehicle_type"] == "car"
        assert "event_id" in data
        assert "timestamp" in data


def test_websocket_broadcast_contains_all_fields(client: TestClient) -> None:
    """Broadcast message includes all expected fields."""
    with client.websocket_connect("/ws/events") as ws:
        payload = {
            **_EVENT_PAYLOAD,
            "timestamp": _ts(),
            "track_id": "ws-fields-check",
            "plate_text": "51G12345",
            "snapshot_url": "/static/snapshots/test.jpg",
        }
        response = client.post("/api/v1/events", json=payload)
        assert response.status_code == 200

        data = ws.receive_json()
        assert data["type"] == "new_event"
        assert "event_id" in data
        assert "plate_text" in data
        assert "direction" in data
        assert "vehicle_type" in data
        assert "timestamp" in data
        assert "snapshot_url" in data
        assert data["snapshot_url"] == "/static/snapshots/test.jpg"


def test_websocket_no_broadcast_without_subscribers(client: TestClient) -> None:
    """POST /events succeeds even with no WebSocket clients connected."""
    payload = {**_EVENT_PAYLOAD, "timestamp": _ts(), "track_id": "no-ws-track"}
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 200
