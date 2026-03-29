from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

Split = Literal["train", "val", "test"]


@dataclass
class DatasetEntry:
    path: str
    split: Split
    source: str


def collect_images(source_dir: Path, extensions: tuple[str, ...]) -> list[Path]:
    return [p for p in source_dir.rglob("*") if p.suffix.lower() in extensions]


def split_list(items: list[Path], train_ratio: float, val_ratio: float) -> dict[Split, list[Path]]:
    random.shuffle(items)
    total = len(items)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    return {
        "train": items[:train_end],
        "val": items[train_end:val_end],
        "test": items[val_end:],
    }


def build_manifest(entries: list[DatasetEntry], output_path: Path, metadata: dict) -> None:
    manifest = {
        "generated_at": datetime.utcnow().isoformat(),
        "count": len(entries),
        "entries": [entry.__dict__ for entry in entries],
        "metadata": metadata,
    }
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    random.seed(42)

    external_root = Path("data/external")
    processed_root = Path("data/processed")
    processed_root.mkdir(parents=True, exist_ok=True)

    sources = {
        "vnlp": external_root / "vnlp",
        "kaggle": external_root / "kaggle",
        "roboflow": external_root / "roboflow",
    }
    extensions = (".jpg", ".jpeg", ".png")

    all_entries: list[DatasetEntry] = []
    metadata = {
        "sources": {},
        "split": {"train": 0.8, "val": 0.1, "test": 0.1},
        "extensions": list(extensions),
    }

    for name, path in sources.items():
        if not path.exists():
            continue
        images = collect_images(path, extensions)
        if not images:
            metadata["sources"][name] = {"path": str(path), "count": 0}
            continue

        splits = split_list(images, 0.8, 0.1)
        for split_name, split_items in splits.items():
            for image_path in split_items:
                relative_path = image_path.relative_to(path)
                all_entries.append(
                    DatasetEntry(
                        path=str(Path(name) / relative_path),
                        split=split_name,
                        source=name,
                    )
                )
        metadata["sources"][name] = {"path": str(path), "count": len(images)}

    manifest_path = processed_root / "dataset_manifest.json"
    build_manifest(all_entries, manifest_path, metadata)


if __name__ == "__main__":
    main()
