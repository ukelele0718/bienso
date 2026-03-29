from __future__ import annotations

import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class SplitConfig:
    train: float = 0.8
    val: float = 0.1
    test: float = 0.1


def _collect_images(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES]


def _ensure_dirs(root: Path) -> None:
    for name in ("train", "val", "test"):
        (root / name).mkdir(parents=True, exist_ok=True)


def _split_paths(paths: list[Path], cfg: SplitConfig) -> tuple[list[Path], list[Path], list[Path]]:
    if not paths:
        return [], [], []

    rng = random.Random(42)
    rng.shuffle(paths)
    total = len(paths)
    n_train = int(total * cfg.train)
    n_val = int(total * cfg.val)
    n_test = total - n_train - n_val

    train = paths[:n_train]
    val = paths[n_train : n_train + n_val]
    test = paths[n_train + n_val : n_train + n_val + n_test]
    return train, val, test


def _copy_with_unique_name(src: Path, dst_dir: Path) -> str:
    dst_name = f"{src.parent.name}_{src.name}"
    dst = dst_dir / dst_name
    if dst.exists():
        dst = dst_dir / f"{src.parent.name}_{src.stem}_{abs(hash(str(src))) % 999999}{src.suffix}"
    shutil.copy2(src, dst)
    return dst.name


def build_artifacts(external_root: Path, processed_root: Path) -> dict:
    _ensure_dirs(processed_root)

    images = _collect_images(external_root)
    train, val, test = _split_paths(images, SplitConfig())

    entries: list[dict] = []
    split_map = {"train": train, "val": val, "test": test}

    for split_name, paths in split_map.items():
        split_dir = processed_root / split_name
        for src in paths:
            copied_name = _copy_with_unique_name(src, split_dir)
            entries.append(
                {
                    "file_name": f"{split_name}/{copied_name}",
                    "split": split_name,
                    "source_path": str(src),
                }
            )

    manifest = {
        "dataset_name": "vnlp-public",
        "source_root": str(external_root),
        "processed_root": str(processed_root),
        "total_images": len(images),
        "split_counts": {
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
        "entries": entries,
    }
    return manifest


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    external_root = project_root / "data" / "external"
    processed_root = project_root / "data" / "processed"
    manifest_path = processed_root / "dataset_manifest.json"

    manifest = build_artifacts(external_root=external_root, processed_root=processed_root)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote manifest to {manifest_path}")
    print(f"Total images: {manifest['total_images']}")


if __name__ == "__main__":
    main()
