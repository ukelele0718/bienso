from __future__ import annotations

import json
from pathlib import Path


def _write_empty_labels_for_images(image_root: Path, label_root: Path) -> int:
    count = 0
    for image_path in image_root.rglob("*"):
        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        rel = image_path.relative_to(image_root)
        label_path = (label_root / rel).with_suffix(".txt")
        label_path.parent.mkdir(parents=True, exist_ok=True)
        if not label_path.exists():
            label_path.write_text("", encoding="utf-8")
            count += 1
    return count


def main() -> None:
    external = Path("data/external")
    processed = Path("data/processed")
    yolo_labels = processed / "labels"
    yolo_labels.mkdir(parents=True, exist_ok=True)

    # This script provides a normalization scaffold:
    # - keep source image paths from manifest
    # - create YOLO label files if missing
    # Real bbox conversion should be added when source annotation schema is confirmed.
    manifest_path = processed / "dataset_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("dataset_manifest.json not found. Run prepare_dataset.py first.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    image_counts: dict[str, int] = {}
    for source in ("vnlp", "kaggle", "roboflow"):
        source_dir = external / source
        if not source_dir.exists():
            image_counts[source] = 0
            continue
        image_counts[source] = sum(1 for p in source_dir.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"})

    placeholder_labels_created = 0
    for source in ("vnlp", "kaggle", "roboflow"):
        source_dir = external / source
        if source_dir.exists():
            placeholder_labels_created += _write_empty_labels_for_images(source_dir, yolo_labels / source)

    report = {
        "status": "annotation_normalization_scaffold_ready",
        "notes": [
            "YOLO label files were scaffolded for detected images.",
            "Empty labels indicate no bbox parsed yet from source annotations.",
            "Next step: implement parser per source annotation format (JSON/XML/TXT).",
        ],
        "image_counts": image_counts,
        "placeholder_labels_created": placeholder_labels_created,
        "manifest_count": manifest.get("count", 0),
    }

    (processed / "annotation_normalization_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
