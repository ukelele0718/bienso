from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Literal


Direction = Literal["in", "out"]
VehicleType = Literal["motorbike", "car"]


@dataclass
class Event:
    camera_id: str
    timestamp: datetime
    direction: Direction
    vehicle_type: VehicleType
    track_id: str
    plate_text: str | None
    confidence: float | None
    snapshot_path: str | None


def run_pipeline(video_source: str, camera_id: str) -> Iterator[Event]:
    """Placeholder generator for AI pipeline.

    TODO: Replace with detector + tracker + plate detection + OCR.
    """
    _ = video_source
    now = datetime.utcnow()
    yield Event(
        camera_id=camera_id,
        timestamp=now,
        direction="in",
        vehicle_type="motorbike",
        track_id="track_1",
        plate_text="29A-12345",
        confidence=0.9,
        snapshot_path=None,
    )
