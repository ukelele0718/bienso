# RUNBOOK — 30-Minute Kaggle Plate Detector (quick baseline)

**Mục tiêu**: có `best.pt` trong ~30 phút để tích hợp tạm.

---

## 0) Checklist trước khi chạy
- [ ] Đảm bảo `G:/TTMT/datn/.venv` đã có `ultralytics`.
- [ ] Dataset Kaggle tồn tại tại `G:/TTMT/datn/data/external/kaggle/archive`.
- [ ] Dung lượng trống tối thiểu ~5–10 GB.
- [ ] Đóng app nặng (tránh OOM).

---

## 1) Tạo subset + data.yaml
**PowerShell** (chạy tại `G:\TTMT\datn`):

```powershell
.\.venv\Scripts\python.exe -c "import os, random, shutil, pathlib, textwrap
base=r'G:/TTMT/datn/data/external/kaggle/archive'
out=r'G:/TTMT/datn/data/processed/kaggle_30min'
train_n=320
val_n=96
random.seed(1337)

def prep(split, n):
    img_dir=pathlib.Path(base)/split/'images'
    lbl_dir=pathlib.Path(base)/split/'labels'
    out_img=pathlib.Path(out)/split/'images'
    out_lbl=pathlib.Path(out)/split/'labels'
    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)
    imgs=sorted([p for p in img_dir.iterdir() if p.suffix.lower() in ['.jpg','.jpeg','.png']])
    picks=random.sample(imgs, min(n, len(imgs)))
    for p in picks:
        shutil.copy2(p, out_img/p.name)
        lbl=lbl_dir/(p.stem+'.txt')
        if lbl.exists():
            shutil.copy2(lbl, out_lbl/lbl.name)
    return picks

train_picks=prep('train', train_n)
val_picks=prep('valid', val_n)

# sample pred set
sample_dir=pathlib.Path(out)/'sample_pred'
sample_dir.mkdir(parents=True, exist_ok=True)
for p in val_picks[:10]:
    shutil.copy2(p, sample_dir/p.name)

# data.yaml
yaml=textwrap.dedent('''
path: G:/TTMT/datn/data/processed/kaggle_30min
train: train/images
val: valid/images
names:
  0: Licence-Plate
''').strip()+"\n"
(pathlib.Path(out)/'data.yaml').write_text(yaml, encoding='utf-8')
print('subset ready:', out)
" 
```

Checklist nhanh:
- [ ] `data/processed/kaggle_30min/train/images` có ~320 ảnh
- [ ] `data/processed/kaggle_30min/valid/images` có ~96 ảnh
- [ ] `data/processed/kaggle_30min/data.yaml` tồn tại

---

## 2) Train nhanh (30 phút)
**PowerShell**:

```powershell
.\.venv\Scripts\python.exe -m ultralytics detect train model=yolov8n.pt data=G:/TTMT/datn/data/processed/kaggle_30min/data.yaml imgsz=512 epochs=12 batch=8 workers=2 device=0 cache=False plots=False project=G:/TTMT/datn/runs name=plate_kaggle_30min exist_ok=True
```

Fallback nếu OOM:
- đổi `batch=4`
- nếu vẫn chậm quá, giảm `epochs=8`

---

## 3) Prediction sample nhanh
Sau khi train xong:

```powershell
.\.venv\Scripts\python.exe -m ultralytics detect predict model=G:/TTMT/datn/runs/plate_kaggle_30min/weights/best.pt source=G:/TTMT/datn/data/processed/kaggle_30min/sample_pred imgsz=512 save=True project=G:/TTMT/datn/runs name=plate_kaggle_30min_pred exist_ok=True
```

---

## 4) Checklist nghiệm thu sprint
- [ ] Có `G:/TTMT/datn/runs/plate_kaggle_30min/weights/best.pt`
- [ ] Có `results.csv` trong thư mục run
- [ ] Prediction sample hiển thị box hợp lý
- [ ] Thời gian tổng ~30 phút (±5 phút)

---

## 5) Ghi chú bắt buộc cho demo
- “quick baseline 30-minute run”
- Không dùng để chốt KPI cuối
- Cần full-train/benchmark lại sau
