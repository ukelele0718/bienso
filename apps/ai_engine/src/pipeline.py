"""AI Engine pipeline — detect vehicles, track, read plates, yield events.

Orchestrates: VehicleDetector → SORT Tracker → PlateDetector → PlateOCR.
Outputs Event objects compatible with backend EventIn schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterator, Literal

import cv2
import numpy as np

from .plate_detector import PlateDetector
from .plate_ocr import PlateOCR
from .sort_tracker import Sort
from .vehicle_detector import VehicleDetector
from . import config


Direction = Literal["in", "out"]
VehicleType = Literal["motorbike", "car"]

# map COCO class names → backend vehicle types
_VEHICLE_TYPE_MAP: dict[str, VehicleType] = {
    "car": "car",
    "bus": "car",
    "truck": "car",
    "motorcycle": "motorbike",
}


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


def _assign_plate_to_vehicle(
    plate_bbox: np.ndarray,
    tracks: np.ndarray,
) -> int:
    """Find which tracked vehicle contains the plate (IoU containment).

    Returns track_id or -1 if no match.
    """
    px1, py1, px2, py2 = plate_bbox[:4]
    for trk in tracks:
        tx1, ty1, tx2, ty2, tid = trk.astype(int)
        if px1 >= tx1 and py1 >= ty1 and px2 <= tx2 and py2 <= ty2:
            return int(tid)
    return -1


def _get_vehicle_type(
    track_id: int,
    vehicle_classes: dict[int, str],
) -> VehicleType:
    """Map track_id → vehicle type from detection class."""
    cls_name = vehicle_classes.get(track_id, "car")
    return _VEHICLE_TYPE_MAP.get(cls_name, "car")


class Pipeline:
    """Full detection + tracking + OCR pipeline."""

    def __init__(self) -> None:
        self.vehicle_detector = VehicleDetector()
        self.plate_detector = PlateDetector()
        self.plate_ocr = PlateOCR()
        self.tracker = Sort(
            max_age=config.TRACKER_MAX_AGE,
            min_hits=config.TRACKER_MIN_HITS,
            iou_threshold=config.TRACKER_IOU_THRESHOLD,
        )
        # track_id → last known class name
        self._track_classes: dict[int, str] = {}
        # track_id → best plate text seen so far
        self._track_plates: dict[int, tuple[str, float]] = {}

    def process_frame(
        self,
        frame: np.ndarray,
        camera_id: str,
        direction: Direction = "in",
    ) -> list[Event]:
        """Process one frame, return events for plates detected."""
        # 1. detect vehicles
        vehicle_dets = self.vehicle_detector.detect(frame)
        det_array = self.vehicle_detector.detect_as_array(frame)

        # 2. update tracker
        tracks = self.tracker.update(det_array)

        # map track_id → class name from closest detection
        for vd in vehicle_dets:
            best_tid = _assign_plate_to_vehicle(
                np.array([*vd.bbox, 0]), tracks,
            )
            if best_tid > 0:
                self._track_classes[best_tid] = vd.class_name

        # 3. detect plates in full frame
        plates = self.plate_detector.detect(frame)
        events: list[Event] = []

        for plate in plates:
            # assign plate to a tracked vehicle
            tid = _assign_plate_to_vehicle(plate.bbox, tracks)
            if tid < 0:
                continue

            # 4. OCR
            text, conf = self.plate_ocr.read(plate.crop)

            # update best plate for this track
            if text:
                prev = self._track_plates.get(tid)
                if prev is None or conf > prev[1]:
                    self._track_plates[tid] = (text, conf)

            best = self._track_plates.get(tid)
            events.append(Event(
                camera_id=camera_id,
                timestamp=datetime.now(UTC),
                direction=direction,
                vehicle_type=_get_vehicle_type(tid, self._track_classes),
                track_id=f"track_{tid}",
                plate_text=best[0] if best else text,
                confidence=best[1] if best else conf,
                snapshot_path=None,
            ))

        return events

    def process_frame_visual(
        self,
        frame: np.ndarray,
        camera_id: str,
        direction: Direction = "in",
    ) -> tuple[np.ndarray, list[Event]]:
        """Process one frame and return annotated frame + events."""
        # 1. detect vehicles
        vehicle_dets = self.vehicle_detector.detect(frame)
        det_array = self.vehicle_detector.detect_as_array(frame)

        # 2. update tracker
        tracks = self.tracker.update(det_array)

        for vd in vehicle_dets:
            best_tid = _assign_plate_to_vehicle(
                np.array([*vd.bbox, 0]), tracks,
            )
            if best_tid > 0:
                self._track_classes[best_tid] = vd.class_name

        # draw tracked vehicles (green)
        annotated = frame.copy()
        for trk in tracks:
            x1, y1, x2, y2, tid = trk.astype(int)
            cls = self._track_classes.get(tid, "vehicle")
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, f"ID{tid} {cls}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 3. detect plates
        plates = self.plate_detector.detect(frame)
        events: list[Event] = []

        for plate in plates:
            tid = _assign_plate_to_vehicle(plate.bbox, tracks)

            # draw plate bbox (red)
            px1, py1, px2, py2 = plate.bbox.astype(int)
            cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 0, 255), 2)

            if tid < 0:
                cv2.putText(annotated, "plate?", (px1, py1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                continue

            # 4. OCR
            text, conf = self.plate_ocr.read(plate.crop)

            if text:
                prev = self._track_plates.get(tid)
                if prev is None or conf > prev[1]:
                    self._track_plates[tid] = (text, conf)

            best = self._track_plates.get(tid)
            plate_label = best[0] if best else (text or "???")
            plate_conf = best[1] if best else (conf or 0)

            # draw OCR text (yellow on dark bg)
            label = f"{plate_label} {plate_conf:.0%}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(annotated, (px1, py1 - th - 10), (px1 + tw + 4, py1), (0, 0, 0), -1)
            cv2.putText(annotated, label, (px1 + 2, py1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            events.append(Event(
                camera_id=camera_id,
                timestamp=datetime.now(UTC),
                direction=direction,
                vehicle_type=_get_vehicle_type(tid, self._track_classes),
                track_id=f"track_{tid}",
                plate_text=best[0] if best else text,
                confidence=best[1] if best else conf,
                snapshot_path=None,
            ))

        return annotated, events


def run_pipeline(
    video_source: str,
    camera_id: str,
    direction: Direction = "in",
    max_frames: int | None = None,
) -> Iterator[Event]:
    """Process a video source and yield events.

    Args:
        video_source: File path or RTSP URL.
        camera_id: Camera identifier for events.
        direction: Gate direction.
        max_frames: Stop after N frames (None = process all).

    Yields:
        Event objects for each plate detection.
    """
    pipe = Pipeline()
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video source: {video_source}")

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            events = pipe.process_frame(frame, camera_id, direction)
            yield from events

            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break
    finally:
        cap.release()


def run_single_image(
    image_path: str,
    camera_id: str,
    direction: Direction = "in",
) -> list[Event]:
    """Process a single image and return events.

    For single images, if no vehicles are detected (e.g. plate-only crops),
    falls back to direct plate detection + OCR without tracking.
    """
    frame = cv2.imread(image_path)
    if frame is None:
        raise ValueError(f"Cannot read image: {image_path}")

    pipe = Pipeline()
    events = pipe.process_frame(frame, camera_id, direction)

    # fallback: if no events (e.g. plate-only image), detect plates directly
    if not events:
        plates = pipe.plate_detector.detect(frame)
        for i, plate in enumerate(plates):
            text, conf = pipe.plate_ocr.read(plate.crop)
            events.append(Event(
                camera_id=camera_id,
                timestamp=datetime.now(UTC),
                direction=direction,
                vehicle_type="car",
                track_id=f"untracked_{i}",
                plate_text=text,
                confidence=conf,
                snapshot_path=None,
            ))

    return events
