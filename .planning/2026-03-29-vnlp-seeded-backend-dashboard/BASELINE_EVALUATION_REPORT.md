# BASELINE EVALUATION REPORT (Seeded Mode Draft v0.1)
## Backend + dashboard baseline theo seeded plate flow

**Ngay**: 2026-03-29  
**Trang thai**: Draft khoi tao tu seeded-mode design, cho implementation va benchmark nghiep vu

---

## 1) Muc tieu
- Thiet lap baseline report de theo doi chat luong cua seeded mode.
- Danh gia nhanh:
  - import seed
  - account creation
  - transaction correctness
  - barrier correctness
  - dashboard usability

Khong nam trong report nay:
- counting benchmark that
- OCR benchmark that

---

## 2) Du lieu dau vao hien co
Nguon seed hien tai:
- `list_two_rows_label_xe_may.txt`
- `VNLP_readme`

Thong ke:
- Tong dong trong file list: **5593**
- Plate parse duoc: **5593**
- Plate unique sau normalize upper-case: **3227**

Seed artifact muc tieu:
- `registered_plates_seed.csv`

---

## 3) Baseline metrics can bao cao

### 3.1 Import metrics
- So dong dau vao
- So plate unique sau normalize
- So account moi duoc tao
- So duplicate bi skip
- So dong invalid

### 3.2 Business rule metrics
- Ty le pass cho:
  - `registered + in`
  - `registered + out`
  - `unknown + in`
  - `temporary_registered + out`
- So verify thanh cong / that bai

### 3.3 Finance metrics
- Ty le dung cua `init transaction`
- Ty le dung cua `event_charge`
- So account balance am sau test scenario

### 3.4 Dashboard metrics
- Search account co hoat dong khong
- Verify queue co hien dung khong
- Summary cards co khop DB khong

### 3.5 AI metrics (tam hoan)
- Counting
- OCR

---

## 4) Bo test scenario de xuat
- Scenario 1: import seed batch
- Scenario 2: registered plate vao cong
- Scenario 3: registered plate ra cong
- Scenario 4: unknown plate vao cong
- Scenario 5: temporary plate ra cong
- Scenario 6: verify hold queue
- Scenario 7: search va truy van lich su

---

## 5) Ket qua baseline hien tai
- **Import**: Chua chay benchmark that.
- **Barrier rules**: Chua chay benchmark that.
- **Dashboard**: Chua chay benchmark that.
- **Counting/OCR**: Khong nam trong seeded mode baseline nay.

Ly do:
- phase hien tai moi o muc thiet ke PRD/API/schema/test-plan.
- can implementation xong import script + backend API + dashboard moi co so lieu do.

---

## 6) Ke hoach cap nhat report vong tiep theo
- Chay seed import tren 1 batch mau.
- Ghi ket qua:
  - imported / skipped / invalid
- Chay 4 scenario nghiep vu chinh.
- Ghi ket qua:
  - barrier action
  - registration_status
  - so du sau event
- Chay dashboard smoke check.
- Cap nhat report v0.2.

---

## 7) Ket luan tam thoi
- Seeded mode hien da co du can cu de tro thanh mot luong trien khai rieng.
- Day la duong ngan nhat de tiep tuc xay backend/dashboard trong khi AI mode chua san sang.
- Sau khi seeded mode on dinh, co the merge lai vao bo `.artifacts` nhu mot MVP execution path song song voi AI-first path.

---

## 8) Merge note
File nay giu cung ten voi `.artifacts/BASELINE_EVALUATION_REPORT.md`, nhung doi trong tam tu AI metrics sang seeded-mode metrics.

Khi merge ve `.artifacts`, nen:
- giu report nay nhu mot phan `backend/dashboard baseline`
- tach ro voi `AI baseline`
- ve sau co the gom thanh 2 chuong trong mot report tong

