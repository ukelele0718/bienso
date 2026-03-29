# KAGGLE 30 MIN TRAIN PLAN
## Ke hoach train nhanh 30 phut de lay model tam

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Muc tieu**: co mot `best.pt` dung tam trong khoang `30 phut` tong thoi gian  
**Nguon du lieu**: `G:\TTMT\datn\data\external\kaggle\archive`  
**Hardware target**: GTX 1650 4 GB VRAM, RAM 16 GB, i5-10300H  

---

## 0) Muc tieu that su
Day khong phai ke hoach train "tot nhat".

Day la ke hoach:
- ra model nhanh
- dung mot tap du lieu nho
- tranh OOM
- co artifact de test runtime tam thoi

Model dau ra du kien:
- `plate detector` tam thoi
- do chinh xac vua phai
- du de test pipeline, chua du de ket luan chat luong cuoi

---

## 1) Tai sao chon bo Kaggle
Bo Kaggle hien co la bo nhanh nhat de bat dau:
- da o format YOLOv8
- da co `train/valid/test`
- anh va label khop `1:1`
- chi co `1` class: `Licence-Plate`

So luong day du:
- `train`: `1618`
- `valid`: `551`
- `test`: `42`

Cho muc tieu `30 phut`, khong can dung het.

---

## 2) Profile nhanh de xuat

### Model
- `yolov8n.pt`

### Cau hinh train
- `imgsz=512`
- `batch=8`
- fallback khi OOM: `batch=4`
- `workers=2`
- `epochs=12`
- `device=0`
- `cache=False`
- `plots=False`

### Ly do chon profile nay
- `yolov8n` la model nhe nhat, phu hop GTX 1650 4 GB
- `imgsz=512` nhanh hon `640`, du de lay model tam
- `12 epoch` du de model hoc box co ban tren subset nho
- `batch=8` la muc nen thu truoc

---

## 3) Kich thuoc subset de xuat

### Lua chon chinh
- `train`: `320` anh
- `valid`: `96` anh
- `test`: bo qua trong dot nay

Tong anh dua vao run:
- `416`

### Tai sao chon muc nay
- du nho de train nhanh
- du lon de model thay duoc nhieu vi du hon mot smoke run qua nho
- thich hop de ra model tam trong `20-30 phut`

### Lua chon fallback neu muon nhanh hon nua
- `train`: `192`
- `valid`: `64`
- `epochs=8`
- `imgsz=512`

Lua chon fallback nay huong toi:
- `10-18 phut` train
- doi lai metric se yeu hon

---

## 4) Uoc tinh thoi gian thuc te

### Phuong an chinh 30 phut
- Chon va copy subset: `3-5 phut`
- QA nhanh 15-20 anh: `3-5 phut`
- Train `12 epoch`: `15-20 phut`
- Val nhanh + luu artifact: `2-4 phut`

Tong:
- `23-34 phut`

### Phuong an fallback sieu nhanh
- Chon subset nho hon: `2-4 phut`
- QA nhanh: `2-3 phut`
- Train `8 epoch`: `8-12 phut`
- Val nhanh: `2-3 phut`

Tong:
- `14-22 phut`

Suy ra:
- Neu ban muon "co model tam that nhanh", dung phuong an fallback
- Neu ban muon van con chut gia tri su dung, dung phuong an chinh

---

## 5) Ke hoach thao tac

### Buoc 1 - Tao subset nho
Muc tieu:
- tao mot tap train rieng, khong dung full dataset

De xuat:
- random lay `320` anh tu `train/images`
- copy label tuong ung tu `train/labels`
- random lay `96` anh tu `valid/images`
- copy label tuong ung tu `valid/labels`

Khuyen nghi:
- giu ten file goc
- khong doi format
- tao rieng mot folder subset de de lap lai

---

### Buoc 2 - QA rat nhanh
Kiem:
- 15-20 anh train
- 5-10 anh valid

Chi can tra loi 3 cau:
- bbox co o dung bien so khong
- co nhieu label rong hay sai khong
- anh co bi meo qua muc khong

Neu tra loi "on" cho 3 cau tren, di tiep ngay.

---

### Buoc 3 - Train tam
Dung profile:
- `yolov8n`
- `imgsz=512`
- `batch=8`
- `epochs=12`

Fallback:
- neu OOM, ha `batch=4`
- neu van cham, ha `epochs=8`

---

### Buoc 4 - Validate nhanh
Can lay:
- `best.pt`
- `results.csv`
- 10 anh prediction dai dien

Chi can check:
- model co ve box dung bien so o nhieu mau hay khong
- loss co xu huong giam hay khong

---

## 6) Tieu chi dung
Co the dung run ngay khi dat 3 dieu kien:
- [ ] sinh ra `best.pt`
- [ ] box nhin bang mat la chap nhan duoc tren sample
- [ ] khong OOM

Khong can co metric dep o dot nay.

---

## 7) Tieu chi thanh cong
- [ ] Tong thoi gian trong khoang `30 phut` hoac xap xi
- [ ] Co model tam de goi thu trong runtime
- [ ] Co 1 run folder de luu log va artifact
- [ ] Khong phai sua parser, convert, hay data contract

---

## 8) De xuat cau hinh chot
Neu chi duoc chon 1 cau hinh, dung cau hinh nay:

- Dataset:
  - `320 train`
  - `96 valid`
- Model:
  - `yolov8n.pt`
- Train:
  - `imgsz=512`
  - `batch=8`
  - `workers=2`
  - `epochs=12`
  - `device=0`

Day la diem can bang tot nhat giua:
- toc do
- kha nang chay on tren GTX 1650
- chat luong du de co model tam

---

## 9) Khuyen nghi su dung model tam
Model nay nen duoc dung cho:
- test pipeline detect
- test crop bien so
- test runtime end-to-end
- test dashboard/event flow neu can

Khong nen dung no de:
- danh gia KPI cuoi
- so sanh chinh thuc giua cac mo hinh
- dua ra ket luan nghiem thu

---

## 10) Buoc tiep theo sau khi co model tam
Thu tu hop ly sau run 30 phut:
1. Goi model tam vao pipeline
2. Xem prediction that tren video/anh thuc te
3. Neu model dung duoc, moi chuyen sang full train bo Kaggle
4. Sau do moi tinh den bo lon hon hoac hop nhat nhieu nguon

