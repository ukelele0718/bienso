# KAGGLE QUICK PLAN
## Ke hoach nhanh de dua bo Kaggle vao baseline train detector

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Muc tieu**: di tu dataset Kaggle hien co den `best.pt` plate detector baseline nhanh nhat co the  
**Hardware target**: GTX 1650 4 GB VRAM, RAM 16 GB, i5-10300H  

---

## 0) Tom tat rat nhanh
Bo `kaggle` hien co la mot bo detection da kha san sang de train:
- Path: `G:\TTMT\datn\data\external\kaggle\archive`
- Format: YOLOv8
- So lop: `1`
- Ten lop: `Licence-Plate`
- Split:
  - `train`: `1618` anh, `1618` label
  - `valid`: `551` anh, `551` label
  - `test`: `42` anh, `42` label

Suy ra:
- Day la bo nhanh nhat de len baseline
- Khong can viet parser annotation moi
- Chi can QA nhanh, train smoke, train full, danh gia va dong goi artifact

---

## 1) Muc tieu pham vi
Plan nay chi nham toi:
- tao baseline `plate detector`
- train nhanh tren bo Kaggle co san
- lay duoc artifact `best.pt`
- co metric val/test co the bao cao

Plan nay chua bao gom:
- OCR
- vehicle detector
- hop nhat voi `data/processed`
- retrain tren bo lon 37k anh
- integration runtime/backend/dashboard

Neu muc tieu la demo nhanh mo hinh nhan bien so, day la duong ngan nhat.

---

## 2) Danh gia phu hop voi may hien tai
Voi cau hinh may cua ban:
- `yolov8n` la lua chon uu tien
- `imgsz=640` la muc an toan
- `batch=8` nen thu truoc
- fallback khi OOM: `batch=4`
- `workers=2` an toan hon `4`
- khong nen cache vao RAM

Danh gia tong quan:
- Bo Kaggle nho hon nhieu so voi processed set 37k anh
- Thoi gian train tren GTX 1650 co the chap nhan duoc trong 1 buoi hoac 1 dem
- Rui ro lon nhat khong phai toc do, ma la chat luong nhan va do hop ly cua split

---

## 3) Ke hoach nhanh theo tung buoc

### Phase 1 - Data readiness check
**Muc tieu**: xac nhan bo Kaggle dung train duoc ngay

Cong viec:
- Mo `data.yaml` va xac nhan duong dan split
- Random check bang mat 30-50 anh
- Kiem 1 vai label file xem bbox co hop ly khong
- Xac nhan anh/label khop 1:1 tren `train/valid/test`

Thoi gian uoc tinh:
- `20-40 phut`

Dau ra bat buoc:
- Xac nhan dataset train duoc ngay
- Note neu co loi split, label rong, bbox sai

Quyet dinh:
- Neu QA dat: di tiep ngay sang smoke train
- Neu QA xau: dung, khong full train

---

### Phase 2 - Smoke train
**Muc tieu**: xac nhan dataloader, VRAM, loss va metric co chay on

Cau hinh de xuat:
- model: `yolov8n.pt`
- `imgsz=640`
- `batch=8`
- fallback: `batch=4`
- `workers=2`
- `epochs=10` hoac `15`
- `cache=disk`
- `device=0`

Thoi gian uoc tinh tren may cua ban:
- `30-60 phut` neu `batch=8`
- `45-90 phut` neu phai ha xuong `batch=4`

Dau ra bat buoc:
- Run train khong OOM
- Co `results.csv`
- Co `best.pt` tam thoi
- Co sample prediction images

Tieu chi dat:
- loss giam
- val khong bi vo
- prediction box nhin bang mat la hop ly

---

### Phase 3 - Full train baseline
**Muc tieu**: lay model baseline that su dung duoc

Cau hinh de xuat:
- model: `yolov8n.pt`
- `imgsz=640`
- `batch=8` neu on, neu khong `4`
- `workers=2`
- `epochs=50`
- `close_mosaic=10`
- `patience=15`
- `cache=disk`
- `plots=True`

Thoi gian uoc tinh tren may cua ban:
- `2.5-4.5 gio` neu on voi `batch=8`
- `4-7 gio` neu phai chay `batch=4`

Khuyen nghi:
- Neu smoke train on, co the chay full train qua dem
- Khong nen vua train vua lam viec nang khac tren may

Dau ra bat buoc:
- `best.pt`
- `last.pt`
- `results.csv`
- `args.yaml`
- prediction samples

---

### Phase 4 - Danh gia test set
**Muc tieu**: co so lieu de bao cao

Cong viec:
- Chay val/test bang `best.pt`
- Doc `precision`, `recall`, `mAP50`, `mAP50-95`
- Mo sample prediction tren `test`
- Note cac truong hop fail ro nhat

Thoi gian uoc tinh:
- `15-30 phut`

Luu y:
- `test` chi co `42` anh, nen metric co tinh tham khao, chua du manh de ket luan lon

---

### Phase 5 - Dong goi artifact
**Muc tieu**: de lai duoc mot baseline co the mo lai va dung tiep

Can giu:
- `best.pt`
- file config train
- `results.csv`
- 10-20 prediction anh dai dien
- note metric ngan
- note han che cua dataset

Thoi gian uoc tinh:
- `10-20 phut`

---

## 4) Tong thoi gian uoc tinh

### Kich ban nhanh nhat
- Data readiness check: `20-40 phut`
- Smoke train: `30-60 phut`
- Full train: `2.5-4.5 gio`
- Danh gia + dong goi: `25-50 phut`

Tong:
- `3.5-6.5 gio`

### Kich ban than trong hon
- QA ky hon: `45-60 phut`
- Smoke train `batch=4`: `45-90 phut`
- Full train `batch=4`: `4-7 gio`
- Danh gia + dong goi: `30-60 phut`

Tong:
- `6-9.5 gio`

Suy ra:
- Neu muon co ket qua trong ngay: kha thi
- Neu muon chac an toan: chay smoke ban ngay, full train qua dem

---

## 5) Lenh va profile uu tien

### Smoke train profile
- model: `yolov8n.pt`
- data: `G:\TTMT\datn\data\external\kaggle\archive\data.yaml`
- epochs: `10`
- imgsz: `640`
- batch: `8`
- workers: `2`

### Full train profile
- model: `yolov8n.pt`
- data: `G:\TTMT\datn\data\external\kaggle\archive\data.yaml`
- epochs: `50`
- imgsz: `640`
- batch: `8` hoac `4`
- workers: `2`

Neu ket qua baseline yeu:
- tang len `epochs=80`
- giu `imgsz=640`
- chi can nhac `yolov8s` sau khi `yolov8n` da on va may khong OOM

---

## 6) Rui ro va cach giam rui ro

### Rui ro 1 - Dataset nho
Tac dong:
- Mo hinh co the hoc duoc box co ban, nhung do phu tinh huong khong cao

Giam rui ro:
- Dung no lam baseline nhanh
- Khong xem day la bo cuoi cung

### Rui ro 2 - Ten class va metadata hoi "web-export"
Tac dong:
- Co the bo nay duoc thu thap tu nguon tong hop, can xem lai tinh dai dien voi bai toan VN

Giam rui ro:
- QA bang mat
- So sanh prediction voi anh VN thuc te sau khi train

### Rui ro 3 - Test set qua nho
Tac dong:
- Metric dao dong, kho ket luan chac

Giam rui ro:
- Dung test nay cho tham khao
- Bao cao ro test chi co `42` anh

### Rui ro 4 - OOM tren GTX 1650
Tac dong:
- Vo run, mat thoi gian

Giam rui ro:
- fallback `batch=4`
- giu `imgsz=640`
- tat app nang trong luc train

---

## 7) Tieu chi thanh cong
- [ ] QA nhanh dat, khong thay loi label nghiem trong
- [ ] Smoke train chay het, khong OOM
- [ ] Full train tao duoc `best.pt`
- [ ] Co metric val/test de bao cao
- [ ] Co 10-20 prediction mau nhin hop ly

Neu dat du 5 muc tren, plan Kaggle duoc xem la hoan thanh.

---

## 8) De xuat cach dung plan nay
Thu tu chay nhanh nhat:
1. QA nhanh 30-50 mau
2. Smoke train `10 epoch`
3. Neu on, full train `50 epoch`
4. Validate tren `test`
5. Dong goi `best.pt` va metric

Plan nay phu hop nhat khi ban can:
- co baseline som
- co artifact train that
- tranh sa vao cong doan parser/convert phuc tap qua som

