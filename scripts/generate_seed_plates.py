#!/usr/bin/env python3
"""
Generate seed plate data from VNLP detection dataset.

Reads the VNLP list file, extracts plate text from filenames,
normalizes them, and outputs CSV + JSON summary for seeding the LPR database.

Usage:
    python scripts/generate_seed_plates.py

Output:
    - data/processed/registered_plates_seed.csv
    - data/processed/registered_plates_seed_summary.json
"""

import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_FILE = Path(r"G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt")
OUTPUT_DIR = Path(r"G:\TTMT\datn\data\processed")
OUTPUT_CSV = OUTPUT_DIR / "registered_plates_seed.csv"
OUTPUT_JSON = OUTPUT_DIR / "registered_plates_seed_summary.json"

# Metadata for this seed batch
SOURCE_NAME = "vnlp_two_rows_xe_may"
SEED_GROUP = "vnlp_motorbike_2026"
VEHICLE_TYPE = "motorbike"

# Vietnamese plate validation pattern
# Format: 2 digits (province) + 1-2 letters (series) + 5-6 digits (number)
# Examples: 29A12345, 29AA12345, 30H35471, 98N12408
PLATE_PATTERN = re.compile(r'^(\d{2})([A-Z]{1,2})(\d{4,6})$')


# ─────────────────────────────────────────────────────────────────────────────
# Core Functions
# ─────────────────────────────────────────────────────────────────────────────

def extract_plate_from_filename(filename: str) -> str | None:
    """
    Extract plate text from VNLP filename format.
    
    Filename format: /detection/two_rows_label_xe_may/{idx}_{num}_0_{plate}_{coords}.jpg
    Example: 6_2215_0_98n12408_470_70_592_168.jpg -> 98n12408
    
    Args:
        filename: Full path or filename from VNLP list
        
    Returns:
        Extracted plate text or None if not found
    """
    # Get just the filename part (after last /)
    basename = filename.strip().split('/')[-1]
    
    # Remove .jpg extension
    if basename.endswith('.jpg'):
        basename = basename[:-4]
    
    # Split by underscore: idx_num_0_plate_x1_y1_x2_y2
    parts = basename.split('_')
    
    # Plate is the 4th field (index 3)
    if len(parts) >= 4:
        return parts[3]
    
    return None


def normalize_plate(plate: str) -> str | None:
    """
    Normalize a Vietnamese license plate.
    
    - Convert to uppercase
    - Remove spaces and special characters
    - Validate format
    
    Args:
        plate: Raw plate text
        
    Returns:
        Normalized plate or None if invalid
    """
    if not plate:
        return None
    
    # Uppercase and remove non-alphanumeric
    normalized = re.sub(r'[^A-Za-z0-9]', '', plate.upper())
    
    # Must have content
    if not normalized or len(normalized) < 6:
        return None
    
    # Validate Vietnamese plate format
    if PLATE_PATTERN.match(normalized):
        return normalized
    
    return None


def process_vnlp_file(source_path: Path) -> tuple[list[dict], dict]:
    """
    Process VNLP list file and extract unique plates.
    
    Args:
        source_path: Path to the VNLP list file
        
    Returns:
        Tuple of (plate_records, stats_dict)
    """
    stats = {
        "source_file": str(source_path),
        "processed_at": datetime.now().isoformat(),
        "total_lines": 0,
        "extracted": 0,
        "normalized": 0,
        "invalid": 0,
        "duplicates_removed": 0,
        "unique_plates": 0,
        "province_distribution": {},
        "series_distribution": {},
    }
    
    raw_plates = []
    invalid_examples = []
    
    # Read and extract plates
    with open(source_path, 'r', encoding='utf-8') as f:
        for line in f:
            stats["total_lines"] += 1
            line = line.strip()
            
            if not line:
                continue
            
            # Extract plate from filename
            raw_plate = extract_plate_from_filename(line)
            if raw_plate:
                stats["extracted"] += 1
                
                # Normalize
                normalized = normalize_plate(raw_plate)
                if normalized:
                    stats["normalized"] += 1
                    raw_plates.append(normalized)
                else:
                    stats["invalid"] += 1
                    if len(invalid_examples) < 10:
                        invalid_examples.append(raw_plate)
            else:
                stats["invalid"] += 1
    
    # Deduplicate
    plate_counts = Counter(raw_plates)
    unique_plates = sorted(plate_counts.keys())
    
    stats["duplicates_removed"] = len(raw_plates) - len(unique_plates)
    stats["unique_plates"] = len(unique_plates)
    stats["invalid_examples"] = invalid_examples
    
    # Analyze distribution
    province_counter = Counter()
    series_counter = Counter()
    
    for plate in unique_plates:
        match = PLATE_PATTERN.match(plate)
        if match:
            province, series, _ = match.groups()
            province_counter[province] += 1
            series_counter[series] += 1
    
    stats["province_distribution"] = dict(province_counter.most_common(20))
    stats["series_distribution"] = dict(series_counter.most_common(20))
    
    # Build records
    records = [
        {
            "plate_text": plate,
            "source": SOURCE_NAME,
            "seed_group": SEED_GROUP,
            "vehicle_type": VEHICLE_TYPE,
        }
        for plate in unique_plates
    ]
    
    return records, stats


def write_csv(records: list[dict], output_path: Path) -> None:
    """Write plate records to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ["plate_text", "source", "seed_group", "vehicle_type"]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Wrote {len(records)} records to {output_path}")


def write_summary(stats: dict, output_path: Path) -> None:
    """Write summary statistics to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Wrote summary to {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Main entry point."""
    print("=" * 60)
    print("VNLP Seed Plate Generator")
    print("=" * 60)
    
    # Validate source
    if not SOURCE_FILE.exists():
        print(f"✗ Source file not found: {SOURCE_FILE}")
        return 1
    
    print(f"\nSource: {SOURCE_FILE}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Output JSON: {OUTPUT_JSON}")
    print()
    
    # Process
    print("Processing VNLP file...")
    records, stats = process_vnlp_file(SOURCE_FILE)
    
    # Output
    write_csv(records, OUTPUT_CSV)
    write_summary(stats, OUTPUT_JSON)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Total lines:        {stats['total_lines']:,}")
    print(f"  Extracted:          {stats['extracted']:,}")
    print(f"  Normalized:         {stats['normalized']:,}")
    print(f"  Invalid/skipped:    {stats['invalid']:,}")
    print(f"  Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"  Unique plates:      {stats['unique_plates']:,}")
    
    if stats.get('invalid_examples'):
        print(f"\n  Invalid examples: {stats['invalid_examples'][:5]}")
    
    print("\n  Top provinces:")
    for province, count in list(stats['province_distribution'].items())[:10]:
        print(f"    {province}: {count}")
    
    print("\n✓ Done!")
    return 0


if __name__ == "__main__":
    exit(main())
