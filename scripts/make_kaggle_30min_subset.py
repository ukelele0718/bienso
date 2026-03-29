import random
import shutil
import pathlib
import textwrap


BASE = pathlib.Path(r"G:/TTMT/datn/data/external/kaggle/archive")
OUT = pathlib.Path(r"G:/TTMT/datn/data/processed/kaggle_30min")
TRAIN_N = 320
VAL_N = 96
SEED = 1337


def prep(split: str, n: int) -> list[pathlib.Path]:
    img_dir = BASE / split / "images"
    lbl_dir = BASE / split / "labels"
    out_img = OUT / split / "images"
    out_lbl = OUT / split / "labels"

    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)

    imgs = sorted([p for p in img_dir.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])
    picks = random.sample(imgs, min(n, len(imgs)))

    for p in picks:
        shutil.copy2(p, out_img / p.name)
        lbl = lbl_dir / f"{p.stem}.txt"
        if lbl.exists():
            shutil.copy2(lbl, out_lbl / lbl.name)

    return picks


def main() -> None:
    random.seed(SEED)

    train_picks = prep("train", TRAIN_N)
    val_picks = prep("valid", VAL_N)

    sample_dir = OUT / "sample_pred"
    sample_dir.mkdir(parents=True, exist_ok=True)
    for p in val_picks[:10]:
        shutil.copy2(p, sample_dir / p.name)

    yaml_content = textwrap.dedent(
        """
        path: G:/TTMT/datn/data/processed/kaggle_30min
        train: train/images
        val: valid/images
        names:
          0: Licence-Plate
        """
    ).strip() + "\n"

    (OUT / "data.yaml").write_text(yaml_content, encoding="utf-8")

    print(f"subset ready: {OUT}")
    print(f"train picks: {len(train_picks)}")
    print(f"valid picks: {len(val_picks)}")


if __name__ == "__main__":
    main()
