"""Send detection events to the backend API."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .pipeline import Event

logger = logging.getLogger(__name__)

DEFAULT_BACKEND_URL = "http://localhost:8000"
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


def send_event(
    event: Event,
    backend_url: str = DEFAULT_BACKEND_URL,
) -> dict | None:
    """POST an event to the backend /api/v1/events endpoint.

    Returns the response JSON on success, None on failure after retries.
    """
    url = f"{backend_url.rstrip('/')}/api/v1/events"
    payload = {
        "camera_id": event.camera_id,
        "timestamp": event.timestamp.isoformat(),
        "direction": event.direction,
        "vehicle_type": event.vehicle_type,
        "track_id": event.track_id,
        "plate_text": event.plate_text,
        "confidence": event.confidence,
        "snapshot_url": event.snapshot_path,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning("Attempt %d/%d failed: %s", attempt, MAX_RETRIES, exc)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    logger.error("Failed to send event after %d attempts", MAX_RETRIES)
    return None


def send_events_batch(
    events: list[Event],
    backend_url: str = DEFAULT_BACKEND_URL,
) -> list[dict | None]:
    """Send multiple events sequentially."""
    return [send_event(e, backend_url) for e in events]
