#!/usr/bin/env python3
"""
Import vehicle events with HTTP URLs for snapshot images.

Usage:
    python scripts/import_vehicle_events.py [--camera-name NAME] [--snapshot-base-url URL]

Environment:
    DATABASE_URL: PostgreSQL connection string (default: postgresql://postgres:postgres@localhost:5432/vehicle_lpr)

Examples:
    # Use defaults
    python scripts/import_vehicle_events.py

    # Custom camera and URL
    python scripts/import_vehicle_events.py --camera-name "Gate A Camera" --snapshot-base-url "http://192.168.1.100:8088/static/images"
"""

import argparse
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import execute_values

# Sample data: (plate_text, image_filename)
SAMPLE_PLATES = [
    ("18U19495", "4_1198_0_18u19495_469_149_615_264.jpg"),
    ("30M86121", "8_2925_0_30m86121_231_57_389_178.jpg"),
    ("29V73283", "5_820_0_29V73283_413_1_574_118.jpg"),
    ("29T164988", "7_2815_0_29t164988_406_172_529_278.jpg"),
    ("29M119166", "9_3392_0_29m119166_268_199_399_317.jpg"),
    ("29L501163", "8_3083_0_29l501163_223_127_377_268.jpg"),
    ("29E111033", "6_1181_0_29E111033_482_29_626_161.jpg"),
    ("29G148508", "9_3676_0_29g148508_343_97_453_184.jpg"),
    ("29M126840", "2_720_0_29m126840_233_124_361_232.jpg"),
    ("29G174621", "8_2992_0_29g174621_312_90_448_207.jpg"),
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import vehicle events with HTTP URLs for snapshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--camera-name",
        default="VNLP Sample Camera",
        help="Camera name to look up in database (default: 'VNLP Sample Camera')",
    )
    parser.add_argument(
        "--snapshot-base-url",
        default="http://localhost:8088/static/vnlp_xe_may_sample10/images",
        help="Base URL for snapshot images (default: http://localhost:8088/static/vnlp_xe_may_sample10/images)",
    )
    return parser.parse_args()


def get_camera_id(conn, camera_name: str) -> str:
    """Look up camera ID by name. Fails if camera not found."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM cameras WHERE name = %s", (camera_name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(
                f"Camera '{camera_name}' not found in database.\n"
                f"Please create the camera first or use --camera-name to specify an existing camera."
            )
        return row[0]


def insert_vehicle_events(conn, camera_id: str) -> list[tuple[str, str]]:
    """Insert vehicle events and return list of (event_id, track_id)."""
    now = datetime.now(timezone.utc)
    events = []

    for idx, (plate_text, filename) in enumerate(SAMPLE_PLATES):
        event_id = str(uuid.uuid4())
        # Extract track_id from filename (remove .jpg extension)
        track_id = filename.rsplit(".", 1)[0]
        # Alternate direction: even index = 'in', odd index = 'out'
        direction = "in" if idx % 2 == 0 else "out"
        timestamp = now - timedelta(minutes=idx + 1)

        events.append((event_id, camera_id, timestamp, direction, "motorbike", track_id, now))

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO vehicle_events (id, camera_id, timestamp, direction, vehicle_type, track_id, created_at)
            VALUES %s
            """,
            events,
        )

    # Return event_id and index for plate_reads
    return [(events[i][0], i) for i in range(len(events))]


def insert_plate_reads(conn, event_indices: list[tuple[str, int]], snapshot_base_url: str):
    """Insert plate reads with HTTP URLs."""
    now = datetime.now(timezone.utc)
    # Ensure base URL doesn't have trailing slash
    base_url = snapshot_base_url.rstrip("/")

    plate_reads = []
    for event_id, idx in event_indices:
        plate_text, filename = SAMPLE_PLATES[idx]
        plate_read_id = str(uuid.uuid4())
        snapshot_url = f"{base_url}/{filename}"

        plate_reads.append((plate_read_id, event_id, plate_text, 0.85, snapshot_url, None, "success", now))

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO plate_reads (id, event_id, plate_text, confidence, snapshot_url, crop_url, ocr_status, created_at)
            VALUES %s
            """,
            plate_reads,
        )


def verify_inserts(conn) -> dict:
    """Verify records were inserted and return counts."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vehicle_events")
        event_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM plate_reads")
        plate_count = cur.fetchone()[0]

        # Get sample of inserted records
        cur.execute(
            """
            SELECT ve.direction, pr.plate_text, pr.snapshot_url
            FROM vehicle_events ve
            JOIN plate_reads pr ON pr.event_id = ve.id
            ORDER BY ve.timestamp DESC
            LIMIT 3
            """
        )
        samples = cur.fetchall()

    return {"event_count": event_count, "plate_count": plate_count, "samples": samples}


def main():
    args = parse_args()

    # Get database URL from environment or use default
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vehicle_lpr")

    print(f"🔌 Connecting to database...")
    print(f"   Camera name: {args.camera_name}")
    print(f"   Snapshot base URL: {args.snapshot_base_url}")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
    except psycopg2.Error as e:
        print(f"❌ Failed to connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Step 1: Look up camera
        print(f"\n📷 Looking up camera '{args.camera_name}'...")
        camera_id = get_camera_id(conn, args.camera_name)
        print(f"   Found camera ID: {camera_id}")

        # Step 2: Insert vehicle events
        print(f"\n🚗 Inserting {len(SAMPLE_PLATES)} vehicle events...")
        event_indices = insert_vehicle_events(conn, camera_id)
        print(f"   Inserted with alternating directions (in/out)")

        # Step 3: Insert plate reads
        print(f"\n📝 Inserting {len(SAMPLE_PLATES)} plate reads with HTTP URLs...")
        insert_plate_reads(conn, event_indices, args.snapshot_base_url)

        # Commit transaction
        conn.commit()
        print("\n✅ Transaction committed successfully!")

        # Step 4: Verify inserts
        print("\n📊 Verification:")
        stats = verify_inserts(conn)
        print(f"   Total vehicle_events: {stats['event_count']}")
        print(f"   Total plate_reads: {stats['plate_count']}")
        print("\n   Sample records:")
        for direction, plate, url in stats["samples"]:
            print(f"   - [{direction:3}] {plate}: {url}")

        print("\n🎉 Import completed successfully!")

    except ValueError as e:
        conn.rollback()
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\n❌ Database error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
