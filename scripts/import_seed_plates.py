#!/usr/bin/env python3
"""
Import seed plates into the Vehicle LPR PostgreSQL database.

Reads the seed CSV and creates Account + Transaction records for each plate.
Idempotent: existing plates are skipped.

Usage:
    python scripts/import_seed_plates.py

Environment:
    DATABASE_URL: PostgreSQL connection string
                  Default: postgresql://postgres:postgres@localhost:5432/vehicle_lpr

Input:
    data/processed/registered_plates_seed.csv
"""

import argparse
import csv
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple
from uuid import uuid4

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SEED_CSV = Path(r"G:\TTMT\datn\data\processed\registered_plates_seed.csv")
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/vehicle_lpr"

# Seed account defaults
DEFAULT_BALANCE_VND = 100_000
DEFAULT_REGISTRATION_STATUS = "registered"
INIT_TRANSACTION_TYPE = "init"


# ─────────────────────────────────────────────────────────────────────────────
# Data Types
# ─────────────────────────────────────────────────────────────────────────────

class SeedPlate(NamedTuple):
    """A seed plate record from CSV."""
    plate_text: str
    source: str
    seed_group: str
    vehicle_type: str | None = None
    note: str | None = None


class ImportStats(NamedTuple):
    """Import operation statistics."""
    total: int
    imported: int
    promoted_existing: int
    skipped: int
    invalid: int
    errors: list[str]
    import_batch_id: str | None


# ─────────────────────────────────────────────────────────────────────────────
# Database Operations
# ─────────────────────────────────────────────────────────────────────────────

def get_connection():
    """Get database connection from DATABASE_URL env var."""
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    print(f"Connecting to: {database_url.split('@')[-1]}")  # Hide credentials
    return psycopg2.connect(database_url)


def get_existing_plates(conn) -> set[str]:
    """Get all existing plate_text values from accounts table."""
    with conn.cursor() as cur:
        cur.execute("SELECT plate_text FROM accounts")
        return {row[0] for row in cur.fetchall()}


def import_plates_batch(conn, plates: list[SeedPlate], existing: set[str]) -> ImportStats:
    """
    Import plates in a single transaction.

    For each plate not in existing set:
    - Create Account with registration_status='registered', balance_vnd=100000
    - Create Transaction with type='init', amount_vnd=100000
    - Attach account to a single import batch for auditing

    Args:
        conn: Database connection
        plates: List of SeedPlate records to import
        existing: Set of existing plate_text values

    Returns:
        ImportStats with counts
    """
    imported = 0
    promoted_existing = 0
    skipped = 0
    invalid = 0
    errors = []

    now = datetime.now(UTC)
    import_batch_id = str(uuid4())
    default_source = plates[0].source if plates else "seed_import"
    default_seed_group = plates[0].seed_group if plates else None

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO import_batches (
                id,
                source,
                seed_group,
                imported_count,
                skipped_count,
                invalid_count,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                import_batch_id,
                default_source,
                default_seed_group,
                0,
                0,
                0,
                now,
            ),
        )

        for plate in plates:
            # Validate
            if not plate.plate_text or len(plate.plate_text) < 6:
                invalid += 1
                continue
            
            # Check if exists
            if plate.plate_text in existing:
                try:
                    cur.execute(
                        """
                        UPDATE accounts
                        SET registration_status = %s,
                            source = COALESCE(source, %s),
                            seed_group = COALESCE(seed_group, %s),
                            imported_at = COALESCE(imported_at, %s),
                            import_batch_id = COALESCE(import_batch_id, %s),
                            updated_at = %s
                        WHERE plate_text = %s
                          AND registration_status <> %s
                        """,
                        (
                            DEFAULT_REGISTRATION_STATUS,
                            plate.source,
                            plate.seed_group,
                            now,
                            import_batch_id,
                            now,
                            plate.plate_text,
                            DEFAULT_REGISTRATION_STATUS,
                        ),
                    )
                    if cur.rowcount > 0:
                        promoted_existing += 1
                    else:
                        skipped += 1
                except Exception as e:
                    error_msg = f"Error updating existing {plate.plate_text}: {e}"
                    errors.append(error_msg)
                continue
            
            try:
                # Generate UUIDs
                account_id = str(uuid4())
                transaction_id = str(uuid4())
                
                # Insert Account (matches DB schema from migrations)
                cur.execute(
                    """
                    INSERT INTO accounts (
                        id,
                        plate_text,
                        registration_status,
                        balance_vnd,
                        source,
                        seed_group,
                        imported_at,
                        import_batch_id,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        account_id,
                        plate.plate_text,
                        DEFAULT_REGISTRATION_STATUS,
                        DEFAULT_BALANCE_VND,
                        plate.source,
                        plate.seed_group,
                        now,
                        import_batch_id,
                        now,
                        now,
                    )
                )
                
                # Insert initial Transaction (matches DB schema: type, not transaction_type)
                cur.execute(
                    """
                    INSERT INTO transactions (
                        id,
                        account_id,
                        event_id,
                        amount_vnd,
                        balance_after_vnd,
                        type,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        transaction_id,
                        account_id,
                        None,  # event_id is NULL for init transactions
                        DEFAULT_BALANCE_VND,
                        DEFAULT_BALANCE_VND,  # balance_after_vnd same as initial
                        INIT_TRANSACTION_TYPE,
                        now,
                    )
                )
                
                imported += 1
                existing.add(plate.plate_text)  # Prevent duplicates within batch
                
            except Exception as e:
                error_msg = f"Error importing {plate.plate_text}: {e}"
                errors.append(error_msg)
                # Continue with next plate
    
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE import_batches
            SET imported_count = %s,
                skipped_count = %s,
                invalid_count = %s
            WHERE id = %s
            """,
            (imported + promoted_existing, skipped, invalid, import_batch_id),
        )

    return ImportStats(
        total=len(plates),
        imported=imported,
        promoted_existing=promoted_existing,
        skipped=skipped,
        invalid=invalid,
        errors=errors,
        import_batch_id=import_batch_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CSV Reader
# ─────────────────────────────────────────────────────────────────────────────

def read_seed_csv(csv_path: Path) -> list[SeedPlate]:
    """Read seed plates from CSV file."""
    plates = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            plates.append(SeedPlate(
                plate_text=row.get('plate_text', '').strip().upper(),
                source=row.get('source', ''),
                seed_group=row.get('seed_group', ''),
                vehicle_type=row.get('vehicle_type') or None,
                note=row.get('note') or None,
            ))
    
    return plates


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import seed plates into the Vehicle LPR database")
    parser.add_argument(
        "--csv",
        type=Path,
        default=SEED_CSV,
        help=f"Path to seed CSV (default: {SEED_CSV})",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    csv_path: Path = args.csv

    print("=" * 60)
    print("Seed Plate Importer")
    print("=" * 60)

    # Validate input
    if not csv_path.exists():
        print(f"[ERROR] Seed CSV not found: {csv_path}")
        print("  Run generate_seed_plates.py first or pass --csv.")
        return 1

    print(f"\nInput: {csv_path}")

    # Read CSV
    print("Reading seed CSV...")
    plates = read_seed_csv(csv_path)
    print(f"  Found {len(plates):,} plates in CSV")
    
    if not plates:
        print("[ERROR] No plates to import")
        return 1
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return 1
    
    try:
        # Get existing plates
        print("Checking existing plates...")
        existing = get_existing_plates(conn)
        print(f"  Found {len(existing):,} existing plates")
        
        # Import
        print("\nImporting plates...")
        stats = import_plates_batch(conn, plates, existing)
        
        # Commit transaction
        conn.commit()
        print("[OK] Transaction committed")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Import failed, rolled back: {e}")
        return 1
    finally:
        conn.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"  Total in CSV:  {stats.total:,}")
    print(f"  Imported new:  {stats.imported:,}")
    print(f"  Promoted reg:  {stats.promoted_existing:,} (existing -> registered)")
    print(f"  Skipped:       {stats.skipped:,} (already registered/exist)")
    print(f"  Invalid:       {stats.invalid:,}")
    print(f"  Import Batch:  {stats.import_batch_id or '--'}")
    
    if stats.errors:
        print(f"\n  Errors ({len(stats.errors)}):")
        for err in stats.errors[:5]:
            print(f"    - {err}")
        if len(stats.errors) > 5:
            print(f"    ... and {len(stats.errors) - 5} more")
    
    print("\n[OK] Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
