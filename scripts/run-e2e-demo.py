"""End-to-end demo: Video → AI Engine → Backend.

Usage:
    python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --camera cam_gate_1
    python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --visual
    python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --visual --no-backend
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

# add ai_engine to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "ai_engine"))

from src.pipeline import Pipeline  # noqa: E402
from src.event_sender import send_event  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E demo: video → detect → backend")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--camera", default="cam_gate_1", help="Camera ID")
    parser.add_argument("--direction", default="in", choices=["in", "out"])
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit frames")
    parser.add_argument("--visual", action="store_true", help="Show detection window")
    parser.add_argument("--no-backend", action="store_true", help="Skip sending to backend")
    args = parser.parse_args()

    print(f"[demo] Video: {args.video}")
    print(f"[demo] Camera: {args.camera}, Direction: {args.direction}")
    print(f"[demo] Visual: {args.visual}, Backend: {'off' if args.no_backend else args.backend}")
    print(f"[demo] Max frames: {args.max_frames or 'all'}")
    print()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"[error] Cannot open video: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 10
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[info] Video: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
          f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {fps:.0f}fps, {total_frames} frames")
    print(f"[info] Loading models...")

    pipe = Pipeline()
    print(f"[info] Models loaded. Processing...\n")

    sent_plates: set[str] = set()
    total_events = 0
    total_sent = 0
    frame_count = 0
    t0 = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if args.max_frames and frame_count > args.max_frames:
                break

            # process frame
            if args.visual:
                annotated, events = pipe.process_frame_visual(
                    frame, args.camera, args.direction,
                )

                # add frame counter + FPS overlay
                elapsed = time.time() - t0
                current_fps = frame_count / elapsed if elapsed > 0 else 0
                info = f"Frame {frame_count}/{total_frames}  FPS: {current_fps:.1f}"
                cv2.putText(annotated, info, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # resize for display if too large or too small
                h, w = annotated.shape[:2]
                if w < 640:
                    scale = 640 / w
                    annotated = cv2.resize(annotated, (int(w * scale), int(h * scale)))
                elif w > 1280:
                    scale = 1280 / w
                    annotated = cv2.resize(annotated, (int(w * scale), int(h * scale)))

                cv2.imshow("E2E Demo — press Q/ESC to quit", annotated)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):  # Q or ESC
                    print("\n[demo] Stopped by user")
                    break
            else:
                events = pipe.process_frame(frame, args.camera, args.direction)

            # send events to backend
            for event in events:
                total_events += 1

                if not event.plate_text:
                    continue

                key = f"{event.track_id}:{event.plate_text}"
                if key in sent_plates:
                    continue
                sent_plates.add(key)

                print(f"[detect] {event.vehicle_type:9s} track={event.track_id:10s} "
                      f"plate={event.plate_text:14s} conf={event.confidence:.2f}")

                if not args.no_backend:
                    result = send_event(event, args.backend)
                    total_sent += 1
                    if result:
                        status = result.get("registration_status", "?")
                        action = result.get("barrier_action", "?")
                        print(f"[sent]   → backend OK  status={status}  barrier={action}")
                    else:
                        print(f"[sent]   → backend FAILED")
                else:
                    total_sent += 1

    finally:
        cap.release()
        if args.visual:
            cv2.destroyAllWindows()

    elapsed = time.time() - t0
    print()
    print(f"[done] {elapsed:.1f}s, {frame_count} frames processed ({frame_count/elapsed:.1f} FPS)")
    print(f"[done] {total_events} raw events, {total_sent} unique sent")
    print(f"[done] {len(sent_plates)} unique plate+track combos")


if __name__ == "__main__":
    main()
