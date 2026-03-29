# MACHINE TRAINING PROFILE
## Cau hinh train toi uu cho may GTX 1650 / RAM 16 GB / i5-10300H

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Pham vi**: detector train, OCR baseline, runtime train hygiene cho may local  

---

## 0) Cau hinh phan cung muc tieu
- GPU: NVIDIA GTX 1650
- VRAM: 4 GB
- RAM: 16 GB
- CPU: Intel Core i5-10300H
- Luu tru con trong uoc tinh: ~128 GB

---

## 1) Danh gia tong quan
May nay du de:
- train detector nho (`yolov8n`, `yolo11n`)
- fine-tune detector `640` tren quy mo ~37k anh
- smoke train OCR baseline
- chay runtime prototype 1 camera

May nay khong hop de:
- train model lon trong thoi gian ngan
- vua train full detector vua train OCR song song
- cache dataset vao RAM
- chay batch lon, imgsz lon, workers qua cao

---

## 2) Muc tieu toi uu
Uu tien theo thu tu:
1. On dinh, khong OOM
2. Co artifact train that
3. Metric tang deu
4. Toc do chap nhan duoc
5. Moi toi uu them do chinh xac

---

## 3) Detector profile de xuat

## 3.1 Plate detector - profile uu tien
- Model uu tien: `yolov8n.pt`
- Fallback thay the: `yolo11n.pt`
- Khong uu tien ngay tu dau: `yolov8s.pt`

### Cau hinh smoke train de xuat
- `imgsz=640`
- `batch=8`
- fallback neu OOM: `batch=4`
- `workers=2`
- `epochs=10` hoac `15`
- `cache=disk`
- `device=0`
- `amp=True`
- `patience=10`
- `plots=True`
- `save=True`
- `save_period=5`

### Cau hinh full train de xuat
- `imgsz=640`
- `batch=8` neu on, neu khong thi `4`
- `workers=2` hoac `4`
- `epochs=50`
- `close_mosaic=10`
- `cache=disk`
- `cos_lr=True`
- `amp=True`
- `optimizer=auto`

### Lenh uu tien ve mat chien luoc
- Chay `yolov8n` truoc
- Chi thu `yolov8s` khi:
  - labels da QA tot
  - `yolov8n` da train on
  - ban can metric cao hon va chap nhan train lau hon

---

## 3.2 Vehicle detector - profile de xuat
Neu pretrained da du cho runtime:
- khong fine-tune ngay

Neu can fine-tune:
- model: `yolov8n.pt`
- `imgsz=640`
- `batch=8` hoac `4`
- `workers=2`
- `epochs=30-50`

Ly do:
- phan kho cua du an nay khong nam o vehicle detector
- plate + OCR moi la diem gia tri cao nhat

---

## 4) OCR profile de xuat

## 4.1 Muc tieu thuc te
May nay hop de:
- fine-tune OCR model nho
- train OCR baseline tren crop da sach

May nay khong hop de:
- train tu dau mot OCR model lon
- dat sequence dai + batch lon

## 4.2 Chien luoc OCR
Uu tien theo thu tu:
1. plate crop sach
2. post-process regex
3. char normalization
4. baseline OCR model nho
5. moi toi finetune sau

## 4.3 Cau hinh OCR baseline de xuat
- batch: `16` neu crop nho va model rat nho
- fallback: `8`
- mixed precision neu framework ho tro
- early stopping bat
- image height/co width co dinh de giam RAM
- chia train theo run ngan 2-5 gio thay vi 1 run qua dai ngay tu dau

---

## 5) Bang cau hinh an toan

| Bai toan | Model | imgsz | batch uu tien | batch fallback | workers | Epoch smoke | Epoch full |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Plate detector | `yolov8n` | 640 | 8 | 4 | 2 | 10-15 | 50 |
| Vehicle detector | `yolov8n` | 640 | 8 | 4 | 2 | 10-15 | 30-50 |
| Plate detector an toan hon nua | `yolov8n` | 512 | 8 | 4 | 2 | 10-15 | 50 |
| Plate detector thu nghiem | `yolov8s` | 640 | 4 | 2 | 2 | 10 | 50 |
| OCR baseline | model nho | tuy framework | 16 | 8 | 2 | 5-10 | 20-40 |

---

## 6) Uoc tinh VRAM thuc te
Uoc tinh kinh nghiem tren GTX 1650 4 GB:

- `yolov8n`, `imgsz=640`, `batch=8`:
  - co kha nang vua
  - nhung de vo OOM neu dataset pipeline nang, augmentation nang, hoac co app khac dang mo
- `yolov8n`, `imgsz=640`, `batch=4`:
  - la profile an toan nhat
- `yolov8s`, `imgsz=640`, `batch=4`:
  - can than trong
  - de cham va nong may
- `imgsz=768` tro len:
  - khong khuyen nghi cho run full train dau tien

---

## 7) Uoc tinh thoi gian train

## 7.1 Plate detector
- `yolov8n`, ~37k anh, `epochs=50`:
  - **24-40 gio**
- `yolov8s`, ~37k anh, `epochs=50`:
  - **40-70 gio**

## 7.2 Vehicle detector
- `yolov8n`, `epochs=30-50`:
  - **20-36 gio**
- `yolov8s`, `epochs=30-50`:
  - **36-60 gio**

## 7.3 OCR baseline
- baseline / fine-tune nho:
  - **2-5 gio** cho smoke run
  - **6-14 gio** cho run day du hon

---

## 8) Cai dat he thong khi train
- Cam sac pin neu la laptop
- Chuyen power mode sang hieu nang cao
- Tat app nang khong can thiet:
  - browser nhieu tab
  - Docker khong dung
  - video playback
  - IDE mo qua nhieu workspace
- Giu trong o dia toi thieu:
  - `30-50 GB` truoc khi bat dau full train

---

## 9) Quy tac tranh OOM
Neu gap CUDA OOM, thu theo thu tu nay:
1. Giam `batch`
2. Giam `imgsz`
3. Giam `workers`
4. Tat cache RAM, giu `cache=disk`
5. Dong bot app nen
6. Thu lai voi smoke subset truoc

Khong nen:
- vua giam batch vua doi model vua doi imgsz trong cung mot lan debug
- nhay thang vao `yolov8s` khi `yolov8n` con chua on

---

## 10) Quy tac chay smoke train
Smoke train phai tra loi 4 cau hoi:
1. Co chay het ma khong OOM khong?
2. Loss co giam khong?
3. Prediction sample co hop ly khong?
4. Throughput co chap nhan duoc khong?

Neu 1 trong 4 cau tra loi la "khong":
- khong chay full train ngay
- quay lai data / config / augmentation

---

## 11) Quy tac chay full train
Chi chay full train khi:
- labels da QA
- smoke train dat
- artifact path da duoc chuan bi
- co cho trong o dia
- co ke hoach doc metrics sau moi dem

Moi run full train phai luu:
- file config
- command line
- best weights
- last weights
- metrics file
- sample predictions
- note run: data version, parser version, split version

---

## 12) Profile command de xuat

## 12.1 Plate detector smoke
```bash
yolo detect train model=yolov8n.pt data=plate.yaml imgsz=640 batch=8 epochs=10 workers=2 cache=disk device=0 amp=True plots=True
```

## 12.2 Plate detector full
```bash
yolo detect train model=yolov8n.pt data=plate.yaml imgsz=640 batch=4 epochs=50 workers=2 cache=disk device=0 amp=True cos_lr=True close_mosaic=10 plots=True
```

## 12.3 Vehicle detector smoke
```bash
yolo detect train model=yolov8n.pt data=vehicle.yaml imgsz=640 batch=8 epochs=10 workers=2 cache=disk device=0 amp=True plots=True
```

### Ghi chu
- `batch=8` la muc uu tien
- neu may nong hoac OOM, chuyen ngay xuong `batch=4`

---

## 13) Khuyen nghi cuoi cung
- Lua chon "de dat artifact that som" tot nhat tren may nay la:
  - `yolov8n`
  - `imgsz=640`
  - `batch=4-8`
  - `workers=2`
  - `cache=disk`
- Dung danh doi nhieu ngay train chi de theo model lon hon khi labels con chua chac
- Tren may nay, **chat luong data va QA label quan trong hon viec nang model**
