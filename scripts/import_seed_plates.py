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

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple
from uuid import uuid4

try:
    import psycopg2
    from psycopg2.extras import execute_values
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
    skipped: int
    invalid: int
    errors: list[str]


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
    
    Args:
        conn: Database connection
        plates: List of SeedPlate records to import
        existing: Set of existing plate_text values
        
    Returns:
        ImportStats with counts
    """
    imported = 0
    skipped = 0
    invalid = 0
    errors = []
    
    now = datetime.utcnow()
    
    with conn.cursor() as cur:
        for plate in plates:
            # Validate
            if not plate.plate_text or len(plate.plate_text) < 6:
                invalid += 1
                continue
            
            # Check if exists
            if plate.plate_text in existing:
                skipped += 1
                continue
            
            try:
                # Generate UUIDs
                account_id = str(uuid4())
                transaction_id = str(uuid4())
                
                # Insert Account (matches DB schema from migrations/001_init.sql)
                cur.execute(
                    """
                    INSERT INTO accounts (
                        id,
                        plate_text,
                        registration_status,
                        balance_vnd,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        account_id,
                        plate.plate_text,
                        DEFAULT_REGISTRATION_STATUS,
                        DEFAULT_BALANCE_VND,
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
    
    return ImportStats(
        total=len(plates),
        imported=imported,
        skipped=skipped,
        invalid=invalid,
        errors=errors,
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

def main():
    """Main entry point."""
    print("=" * 60)
    print("Seed Plate Importer")
    print("=" * 60)
    
    # Validate input
    if not SEED_CSV.exists():
        print(f"✗ Seed CSV not found: {SEED_CSV}")
        print("  Run generate_seed_plates.py first.")
        return 1
    
    print(f"\nInput: {SEED_CSV}")
    
    # Read CSV
    print("Reading seed CSV...")
    plates = read_seed_csv(SEED_CSV)
    print(f"  Found {len(plates):,} plates in CSV")
    
    if not plates:
        print("✗ No plates to import")
        return 1
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = get_connection()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
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
        print("✓ Transaction committed")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Import failed, rolled back: {e}")
        return 1
    finally:
        conn.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"  Total in CSV:  {stats.total:,}")
    print(f"  Imported:      {stats.imported:,}")
    print(f"  Skipped:       {stats.skipped:,} (already exist)")
    print(f"  Invalid:       {stats.invalid:,}")
    
    if stats.errors:
        print(f"\n  Errors ({len(stats.errors)}):")
        for err in stats.errors[:5]:
            print(f"    - {err}")
        if len(stats.errors) > 5:
            print(f"    ... and {len(stats.errors) - 5} more")
    
    print("\n✓ Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
