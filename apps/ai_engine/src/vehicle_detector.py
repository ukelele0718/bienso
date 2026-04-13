"""Vehicle detection using YOLOv8 on COCO classes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

from . import config


@dataclass
class VehicleDetection:
    bbox: np.ndarray  # [x1, y1, x2, y2]
    score: float
    class_name: str


class VehicleDetector:
    """Detect vehicles (car, motorcycle, bus, truck) in a frame."""

    def __init__(
        self,
        model_path: str | None = None,
        confidence: float | None = None,
    ) -> None:
        path = model_path or str(config.VEHICLE_MODEL)
        self.confidence = confidence or config.VEHICLE_CONFIDENCE
        self.model = YOLO(path)
        # build allowed class id set from COCO names
        self._vehicle_ids: set[int] = {
            k for k, v in self.model.names.items()
            if v in config.VEHICLE_CLASSES
        }

    def detect(self, frame: np.ndarray) -> list[VehicleDetection]:
        """Run detection on a single frame.

        Returns list of VehicleDetection with bbox, score, class_name.
        """
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        detections: list[VehicleDetection] = []

        for box in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = box
            if int(class_id) in self._vehicle_ids:
                detections.append(VehicleDetection(
                    bbox=np.array([x1, y1, x2, y2]),
                    score=score,
                    class_name=self.model.names[int(class_id)],
                ))

        return detections

    def detect_as_array(self, frame: np.ndarray) -> np.ndarray:
        """Return detections as (N, 5) array [x1, y1, x2, y2, score] for SORT."""
        dets = self.detect(frame)
        if not dets:
            return np.empty((0, 5))
        return np.array([[*d.bbox, d.score] for d in dets])
