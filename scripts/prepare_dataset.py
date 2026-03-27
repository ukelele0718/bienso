from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Split = Literal["train", "val", "test"]


@dataclass
class DatasetEntry:
    path: str
    split: Split
    source: str


def build_manifest(dataset_root: Path, output_path: Path) -> None:
    """Create a minimal dataset manifest placeholder.

    Expected directory layout:
      dataset_root/
        train/
        val/
        test/
    """
    entries: list[DatasetEntry] = []
    for split in ("train", "val", "test"):
        split_dir = dataset_root / split
        if not split_dir.exists():
            continue
        for image_path in split_dir.rglob("*.jpg"):
            entries.append(
                DatasetEntry(
                    path=str(image_path.relative_to(dataset_root)),
                    split=split,
                    source=str(dataset_root),
                )
            )

    manifest = {
        "dataset_root": str(dataset_root),
        "count": len(entries),
        "entries": [entry.__dict__ for entry in entries],
    }
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    root = Path("data/processed")
    out = Path("data/processed/dataset_manifest.json")
    build_manifest(root, out)
