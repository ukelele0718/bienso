"""End-to-end demo: Video → AI Engine → Backend.

Usage:
    python scripts/run-e2e-demo.py \
        --video data/test-videos/trungdinh22-demo.mp4 \
        --camera cam_gate_1 \
        --backend http://localhost:8000 \
        --max-frames 60
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# add ai_engine to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "ai_engine"))

from src.pipeline import run_pipeline  # noqa: E402
from src.event_sender import send_event  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E demo: video → detect → backend")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--camera", default="cam_gate_1", help="Camera ID")
    parser.add_argument("--direction", default="in", choices=["in", "out"])
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit frames")
    args = parser.parse_args()

    print(f"[demo] Video: {args.video}")
    print(f"[demo] Camera: {args.camera}, Direction: {args.direction}")
    print(f"[demo] Backend: {args.backend}")
    print(f"[demo] Max frames: {args.max_frames or 'all'}")
    print()

    sent_plates: set[str] = set()  # deduplicate: plate_text already sent
    total_events = 0
    total_sent = 0
    t0 = time.time()

    for event in run_pipeline(args.video, args.camera, args.direction, args.max_frames):
        total_events += 1

        if not event.plate_text:
            continue

        # deduplicate: skip if same plate already sent
        key = f"{event.track_id}:{event.plate_text}"
        if key in sent_plates:
            continue
        sent_plates.add(key)

        # send to backend
        print(f"[detect] {event.vehicle_type:9s} track={event.track_id:10s} "
              f"plate={event.plate_text:14s} conf={event.confidence:.2f}")

        result = send_event(event, args.backend)
        total_sent += 1

        if result:
            status = result.get("registration_status", "?")
            action = result.get("barrier_action", "?")
            print(f"[sent]   → backend OK  status={status}  barrier={action}")
        else:
            print(f"[sent]   → backend FAILED")

    elapsed = time.time() - t0
    print()
    print(f"[done] {elapsed:.1f}s elapsed")
    print(f"[done] {total_events} raw events, {total_sent} sent to backend")
    print(f"[done] {len(sent_plates)} unique plate+track combos")


if __name__ == "__main__":
    main()
