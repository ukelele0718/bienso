"""License plate detection — supports YOLOv5 (torch.hub) and YOLOv8 (ultralytics)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import torch

from . import config


@dataclass
class PlateDetection:
    bbox: np.ndarray   # [x1, y1, x2, y2]
    score: float
    crop: np.ndarray   # cropped plate image (H, W, 3)


class PlateDetector:
    """Detect license plates in a frame or vehicle crop."""

    def __init__(
        self,
        model_path: str | None = None,
        model_type: Literal["yolov5", "yolov8"] | None = None,
        confidence: float | None = None,
    ) -> None:
        path = model_path or str(config.PLATE_MODEL)
        self.confidence = confidence or config.PLATE_CONFIDENCE

        # auto-detect model type from filename if not specified
        if model_type is None:
            model_type = "yolov5" if "LP_detector" in path else "yolov8"

        self.model_type = model_type
        if model_type == "yolov5":
            self.model = torch.hub.load(
                "ultralytics/yolov5", "custom", path=path, trust_repo=True,
            )
            self.model.conf = self.confidence
        else:
            from ultralytics import YOLO
            self.model = YOLO(path)

    def detect(self, frame: np.ndarray) -> list[PlateDetection]:
        """Detect plates in a frame. Returns list of PlateDetection."""
        if self.model_type == "yolov5":
            return self._detect_v5(frame)
        return self._detect_v8(frame)

    def _detect_v5(self, frame: np.ndarray) -> list[PlateDetection]:
        results = self.model(frame)
        detections: list[PlateDetection] = []
        for *xyxy, conf, _cls in results.xyxy[0].tolist():
            x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            detections.append(PlateDetection(
                bbox=np.array([x1, y1, x2, y2]),
                score=conf,
                crop=crop,
            ))
        return detections

    def _detect_v8(self, frame: np.ndarray) -> list[PlateDetection]:
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        detections: list[PlateDetection] = []
        for box in results.boxes.data.tolist():
            x1, y1, x2, y2, score, _cls = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                continue
            detections.append(PlateDetection(
                bbox=np.array([x1, y1, x2, y2]),
                score=score,
                crop=crop,
            ))
        return detections
