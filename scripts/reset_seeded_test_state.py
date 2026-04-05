#!/usr/bin/env python3
"""
Reset deterministic seeded test state for local/CI runs.

This script ensures a stable baseline for seeded-flow integration tests:
- Keeps schema intact (does not drop tables)
- Truncates runtime event data
- Seeds deterministic accounts for test scenarios
- Inserts required test camera

Usage:
  python scripts/reset_seeded_test_state.py

Environment:
  DATABASE_URL (optional)
  Default: postgresql://postgres:postgres@localhost:5432/vehicle_lpr
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from uuid import uuid4

try:
    import psycopg2
except ImportError:
    print("[ERROR] psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/vehicle_lpr"
TEST_CAMERA_ID = "11111111-1111-1111-1111-111111111111"


def get_connection():
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    print(f"Connecting to: {database_url.split('@')[-1]}")
    return psycopg2.connect(database_url)


def run_reset(conn) -> None:
    now = datetime.now(UTC)

    with conn.cursor() as cur:
        # Keep schema, clear runtime data first (order matters due to FK).
        cur.execute("TRUNCATE TABLE barrier_actions CASCADE")
        cur.execute("TRUNCATE TABLE plate_reads CASCADE")
        cur.execute("TRUNCATE TABLE transactions CASCADE")
        cur.execute("TRUNCATE TABLE vehicle_events CASCADE")
        cur.execute("TRUNCATE TABLE audit_logs CASCADE")

        # Keep import_batches for auditing history.

        # Keep accounts but normalize deterministic fixture state.
        cur.execute("DELETE FROM accounts")

        # Ensure deterministic camera exists.
        cur.execute(
            """
            INSERT INTO cameras (id, name, gate_type, location, stream_url, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                gate_type = EXCLUDED.gate_type,
                location = EXCLUDED.location,
                stream_url = EXCLUDED.stream_url,
                is_active = EXCLUDED.is_active
            """,
            (
                TEST_CAMERA_ID,
                "Seeded Test Camera",
                "student",
                "seeded_test_gate",
                None,
                True,
                now,
            ),
        )

        fixture_accounts = [
            ("51G12345", "registered", 100000),
            ("99X99999", "temporary_registered", 100000),
            ("30F56789", "temporary_registered", 100000),
            ("29A12345", "registered", 100000),
        ]

        for plate_text, reg_status, balance in fixture_accounts:
            account_id = str(uuid4())
            tx_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO accounts (
                    id, plate_text, registration_status, balance_vnd,
                    source, seed_group, imported_at, import_batch_id,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    account_id,
                    plate_text,
                    reg_status,
                    balance,
                    "seeded_fixture",
                    "deterministic_test",
                    now,
                    None,
                    now,
                    now,
                ),
            )
            cur.execute(
                """
                INSERT INTO transactions (
                    id, account_id, event_id, amount_vnd,
                    balance_after_vnd, type, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (tx_id, account_id, None, balance, balance, "init", now),
            )

    conn.commit()


def main() -> int:
    print("=" * 60)
    print("Reset Seeded Test State")
    print("=" * 60)

    try:
        conn = get_connection()
    except Exception as e:
        print(f"[ERROR] DB connect failed: {e}")
        return 1

    try:
        run_reset(conn)
        print("[OK] Deterministic seeded test state prepared.")
        print("[OK] Camera: 11111111-1111-1111-1111-111111111111")
        print("[OK] Accounts seeded: 4")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Reset failed (rolled back): {e}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
