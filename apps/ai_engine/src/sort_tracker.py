"""SORT: Simple Online and Realtime Tracker.

Based on https://github.com/abewley/sort (GPL-3.0, Alex Bewley).
Refactored from Cannguyen123/Detect_redlight for integration into AI Engine.
Removed CLI/display dependencies — only core tracking logic retained.
"""

from __future__ import annotations

import numpy as np
from filterpy.kalman import KalmanFilter


def _iou_batch(bb_test: np.ndarray, bb_gt: np.ndarray) -> np.ndarray:
    """Compute IoU between two sets of bboxes [x1, y1, x2, y2]."""
    bb_gt = np.expand_dims(bb_gt, 0)
    bb_test = np.expand_dims(bb_test, 1)

    xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
    yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
    xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
    yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])

    w = np.maximum(0.0, xx2 - xx1)
    h = np.maximum(0.0, yy2 - yy1)
    intersection = w * h

    area_test = (bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])
    area_gt = (bb_gt[..., 2] - bb_gt[..., 0]) * (bb_gt[..., 3] - bb_gt[..., 1])

    return intersection / (area_test + area_gt - intersection)


def _linear_assignment(cost_matrix: np.ndarray) -> np.ndarray:
    """Hungarian algorithm assignment."""
    try:
        import lap
        _, x, y = lap.lapjv(cost_matrix, extend_cost=True)
        return np.array([[y[i], i] for i in x if i >= 0])
    except ImportError:
        from scipy.optimize import linear_sum_assignment
        x, y = linear_sum_assignment(cost_matrix)
        return np.array(list(zip(x, y)))


def _bbox_to_z(bbox: np.ndarray) -> np.ndarray:
    """Convert [x1, y1, x2, y2] to [cx, cy, area, aspect_ratio]."""
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    return np.array([
        bbox[0] + w / 2.0,
        bbox[1] + h / 2.0,
        w * h,
        w / float(h),
    ]).reshape((4, 1))


def _z_to_bbox(x: np.ndarray, score: float | None = None) -> np.ndarray:
    """Convert [cx, cy, area, aspect_ratio] back to [x1, y1, x2, y2]."""
    w = np.sqrt(x[2] * x[3])
    h = x[2] / w
    box = [x[0] - w / 2.0, x[1] - h / 2.0, x[0] + w / 2.0, x[1] + h / 2.0]
    if score is not None:
        box.append(score)
    return np.array(box).reshape((1, -1))


class _KalmanBoxTracker:
    """Internal state for a single tracked object."""

    _count = 0

    def __init__(self, bbox: np.ndarray) -> None:
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ])
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ])
        self.kf.R[2:, 2:] *= 10.0
        self.kf.P[4:, 4:] *= 1000.0
        self.kf.P *= 10.0
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = _bbox_to_z(bbox)
        self.time_since_update = 0
        self.id = _KalmanBoxTracker._count
        _KalmanBoxTracker._count += 1
        self.hits = 0
        self.hit_streak = 0
        self.age = 0

    def update(self, bbox: np.ndarray) -> None:
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(_bbox_to_z(bbox))

    def predict(self) -> np.ndarray:
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0
        self.kf.predict()
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        return _z_to_bbox(self.kf.x)[0]

    def get_state(self) -> np.ndarray:
        return _z_to_bbox(self.kf.x)[0]


def _associate(
    detections: np.ndarray,
    trackers: np.ndarray,
    iou_threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Assign detections to trackers via IoU + Hungarian."""
    if len(trackers) == 0:
        return (
            np.empty((0, 2), dtype=int),
            np.arange(len(detections)),
            np.empty((0, 5), dtype=int),
        )

    iou_matrix = _iou_batch(detections, trackers)

    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = _linear_assignment(-iou_matrix)
    else:
        matched_indices = np.empty(shape=(0, 2))

    unmatched_dets = [d for d in range(len(detections)) if d not in matched_indices[:, 0]]
    unmatched_trks = [t for t in range(len(trackers)) if t not in matched_indices[:, 1]]

    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_dets.append(m[0])
            unmatched_trks.append(m[1])
        else:
            matches.append(m.reshape(1, 2))

    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches, np.array(unmatched_dets), np.array(unmatched_trks)


class Sort:
    """SORT multi-object tracker.

    Usage::

        tracker = Sort()
        for frame_detections in video_frames:
            # detections: np.ndarray of shape (N, 5) — [x1, y1, x2, y2, score]
            tracks = tracker.update(frame_detections)
            # tracks: np.ndarray of shape (M, 5) — [x1, y1, x2, y2, track_id]
    """

    def __init__(
        self,
        max_age: int = 1,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
    ) -> None:
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: list[_KalmanBoxTracker] = []
        self.frame_count = 0

    def update(self, dets: np.ndarray | None = None) -> np.ndarray:
        """Update tracker with detections for one frame.

        Args:
            dets: (N, 5) array of [x1, y1, x2, y2, score]. Empty array for no detections.

        Returns:
            (M, 5) array of [x1, y1, x2, y2, track_id].
        """
        if dets is None:
            dets = np.empty((0, 5))

        self.frame_count += 1

        # predict existing trackers
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            trks[t, :] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(t)
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        for t in reversed(to_del):
            self.trackers.pop(t)

        matched, unmatched_dets, unmatched_trks = _associate(
            dets, trks, self.iou_threshold,
        )

        # update matched
        for m in matched:
            self.trackers[m[1]].update(dets[m[0], :])

        # init new trackers
        for i in unmatched_dets:
            self.trackers.append(_KalmanBoxTracker(dets[i, :]))

        # collect results, prune dead
        ret = []
        i = len(self.trackers)
        for trk in reversed(self.trackers):
            d = trk.get_state()
            if (trk.time_since_update < 1) and (
                trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits
            ):
                ret.append(np.concatenate((d, [trk.id + 1])).reshape(1, -1))
            i -= 1
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)

        if len(ret) > 0:
            return np.concatenate(ret)
        return np.empty((0, 5))
