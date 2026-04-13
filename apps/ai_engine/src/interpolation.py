"""Bounding box interpolation for frames with missing detections.

Adapted from Cannguyen123/Detect_redlight/src/add_missing_data.py.
Refactored: works on dicts directly, no CSV I/O.
"""

from __future__ import annotations

import numpy as np


def interpolate_tracks(
    results: dict[int, dict[int, dict]],
) -> dict[int, dict[int, dict]]:
    """Fill gaps in per-frame tracking results via linear interpolation.

    Args:
        results: ``{frame_id: {track_id: {car_bbox, plate_bbox, plate_text, ...}}}``

    Returns:
        Same structure with missing frames filled in. Only bboxes are interpolated;
        ``plate_text`` carries forward from the nearest frame with highest confidence.
    """
    # collect all (frame, track_id) entries
    track_data: dict[int, list[tuple[int, dict]]] = {}
    for frame_id, tracks in results.items():
        for track_id, data in tracks.items():
            track_data.setdefault(track_id, []).append((frame_id, data))

    output: dict[int, dict[int, dict]] = {}

    for track_id, entries in track_data.items():
        entries.sort(key=lambda e: e[0])

        # best plate text across all frames for this track
        best_text = None
        best_conf = 0.0
        for _, data in entries:
            conf = data.get("plate_confidence", 0.0)
            if data.get("plate_text") and conf > best_conf:
                best_text = data["plate_text"]
                best_conf = conf

        # interpolate consecutive pairs
        for i in range(len(entries)):
            frame_id, data = entries[i]
            output.setdefault(frame_id, {})[track_id] = data

            if i + 1 >= len(entries):
                continue

            next_frame, next_data = entries[i + 1]
            gap = next_frame - frame_id
            if gap <= 1:
                continue

            # linear interpolation for bboxes
            car_bbox = np.array(data.get("car_bbox", [0, 0, 0, 0]), dtype=float)
            next_car_bbox = np.array(next_data.get("car_bbox", [0, 0, 0, 0]), dtype=float)
            plate_bbox = np.array(data.get("plate_bbox", [0, 0, 0, 0]), dtype=float)
            next_plate_bbox = np.array(next_data.get("plate_bbox", [0, 0, 0, 0]), dtype=float)

            for step in range(1, gap):
                alpha = step / gap
                interp_car = car_bbox + alpha * (next_car_bbox - car_bbox)
                interp_plate = plate_bbox + alpha * (next_plate_bbox - plate_bbox)
                fid = frame_id + step

                output.setdefault(fid, {})[track_id] = {
                    "car_bbox": interp_car.tolist(),
                    "plate_bbox": interp_plate.tolist(),
                    "plate_text": best_text,
                    "plate_confidence": 0.0,  # interpolated, not real
                    "interpolated": True,
                }

    return output
