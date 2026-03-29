# IMPLEMENTATION PLAN
## Luong gia lap "da co danh sach bien so" tu VNLP de day nhanh backend va dashboard

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Pham vi**: bo qua bai toan OCR/train trong giai doan nay, coi nhu da co danh sach bien so va chi tap trung vao import DB + backend + dashboard  

---

## 0) Can cu xuat phat
Tu 2 file:
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt`
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\VNLP_readme`

Co the suy ra:
- filename trong VNLP da chua chuoi bien so
- filename cung chua toa do bbox
- danh sach `list_two_rows_label_xe_may.txt` co the dung de rut ra bien so ma khong can OCR

Quan sat nhanh tren file list nay:
- tong so dong: `5593`
- so bien so parse duoc: `5593`
- so bien so unique sau khi upper-case: `3227`

Suy ra:
- chi rieng file nay da du de tao mot tap `registered plates` gia lap
- co the coi day la du lieu seed ban dau de phat trien backend/dashboard

---

## 1) Muc tieu cua plan nay
Muc tieu la khoa pham vi theo huong:

`VNLP filename list` -> `seed file bien so` -> `import vao database` -> `backend APIs` -> `dashboard van hanh`

Khong lam trong plan nay:
- OCR that
- plate detector that
- vehicle detector that
- train model that
- dong bo runtime vision that

Nghia la trong giai doan nay, he thong se hoat dong nhu mot ban mo phong:
- "nhan dien bien so" da co ket qua dau vao
- backend xu ly nghiep vu tu danh sach bien so nay
- dashboard co the quan sat, tra cuu, verify, va demo luong nghiep vu

---

## 2) Gia dinh khoa cung

### Gia dinh 1 - Danh sach bien so da san sang
Ta coi nhu da co mot file seed, vi du:
- `registered_plates_seed.csv`

No chua toi thieu:
- `plate_text`

Nen co them:
- `source`
- `seed_group`
- `vehicle_type`
- `note`

### Gia dinh 2 - Bien so seed la bien so "da dang ky"
Tat ca bien so import tu file seed se vao DB voi:
- `registration_status = registered`
- `balance_vnd = 100000`

### Gia dinh 3 - Chi can demo luong nghiep vu
Muc tieu la:
- tim kiem bien so
- xem so du
- xem lich su giao dich
- xem event in/out
- xem barrier action
- verify cac xe bi hold

---

## 3) Dinh nghia artifact seed can chot

### 3.1 Contract toi thieu
De backend import de dang, chot mot contract CSV rat don gian:

| Cot | Bat buoc | Vi du | Ghi chu |
| --- | --- | --- | --- |
| `plate_text` | co | `29A12345` | bien so da normalize |
| `source` | co | `vnlp_two_rows_xe_may` | nguon seed |
| `seed_group` | co | `2026_03_29_v1` | batch import |
| `vehicle_type` | nen co | `motorbike` | phuc vu UI/filter |
| `note` | tuy chon | `seed from VNLP filename` | provenance |

### 3.2 Rule normalize bien so
Truoc khi import, chot 1 rule normalize duy nhat:
- upper-case
- bo khoang trang
- bo ky tu phan cach neu co
- giu lai chu va so lien mach

Vi du:
- `29h119396` -> `29H119396`
- `29-AA-30124` -> `29AA30124`

### 3.3 Rule dedupe
Neu cung 1 bien so xuat hien nhieu lan trong seed:
- chi import `1` account
- luu lai so lan xuat hien o file bao cao neu can

---

## 4) Danh gia code hien tai

### Hien da co
Backend hien da co cac bang va API can ban:
- `accounts`
- `transactions`
- `vehicle_events`
- `plate_reads`
- `barrier_actions`

Co san cac API:
- tao event
- lay account theo bien so
- lay transactions
- lay barrier actions theo bien so
- verify barrier hold
- realtime stats

### Hien chua co hoac chua du
- chua co luong import bulk plates
- chua co API list/search accounts
- chua co API import preview / import summary
- chua co dashboard man hinh quan ly danh sach bien so seed
- chua co dashboard man hinh transaction/account list day du

### Diem nghiep vu can sua som
Logic barrier hien tai dang co lo hong quan trong:
- `registered + in` -> `open`
- `temporary_registered + in` -> `open`
- `temporary_registered + out` -> `hold`
- nhung `registered + out` hien se roi vao `default_hold`

Neu muon dung seed plates de demo nghiep vu hop ly, can quyet dinh som:
- xe `registered` khi `out` se `open` hay `hold`

Khuyen nghi:
- dat `registered + out -> open`

Neu khong sua diem nay, luong demo voi bien so seed se bi vo.

---

## 5) Luong kien truc de xuat

### Phase A - Seed extraction artifact
Day la phase "ngoai he thong train":
- doc file list VNLP
- parse plate tu filename
- normalize
- dedupe
- xuat ra `registered_plates_seed.csv`

Output cua phase nay:
- `registered_plates_seed.csv`
- `registered_plates_seed_summary.json`

### Phase B - Import vao DB
He thong import doc seed CSV va:
- upsert vao `accounts`
- tao `init transaction` cho account moi
- bo qua account da ton tai, hoac update theo policy

Output:
- `N imported`
- `N skipped duplicate`
- `N invalid`

### Phase C - Backend nghiep vu
Sau khi co seed accounts:
- event moi co `plate_text` trung seed se di theo nhanh `registered`
- event moi co `plate_text` khong co trong seed se tao `temporary_registered`
- barrier actions va transactions se sinh theo rule nghiep vu

### Phase D - Dashboard
Dashboard se co cac man hinh:
- danh sach tai khoan/bien so
- chi tiet tai khoan
- lich su giao dich
- lich su event
- hang doi verify barrier
- tong quan imported plates / registered / temporary

---

## 6) Work Breakdown Structure

## Phase 1 - Chot contract seed va fake data boundary
**Muc tieu**: ngan du an roi nguoc tro lai bai toan OCR/train

Cong viec:
- chot rang dau vao he thong la `plate_text` da co san
- chot format `registered_plates_seed.csv`
- chot rule normalize bien so
- chot policy dedupe
- chot policy account da ton tai thi xu ly the nao

Dau ra:
- 1 tai lieu contract seed
- 1 file mau seed

Thoi gian uoc tinh:
- `0.5 ngay`

---

## Phase 2 - Thiet ke import path vao database
**Muc tieu**: co duong nhap du lieu bien so vao DB an toan, lap lai duoc

Cong viec:
- quyet dinh import bang script hay API admin
- uu tien giai doan 1: script local/CLI
- them idempotency:
  - import lai khong tao duplicate account
- them summary report:
  - imported
  - skipped
  - invalid

Khuyen nghi MVP:
- lam `seed_accounts.py` chay local
- chua can upload file qua dashboard

Dau ra:
- script import
- log ket qua import
- du lieu `accounts` va `transactions` duoc seed

Thoi gian uoc tinh:
- `0.5-1 ngay`

---

## Phase 3 - Sua nghiep vu backend de ho tro luong seed
**Muc tieu**: event flow phai dung khi diem bat dau la account da ton tai

Cong viec:
- bo sung rule cho `registered + out`
- review logic `unknown` / `temporary_registered`
- dam bao event voi bien so seed khong bi tao lai account sai
- dam bao transaction init chi tao 1 lan cho account moi
- dam bao verify hold van chay duoc cho xe tam

Can test ro:
- bien so trong seed, `in`
- bien so trong seed, `out`
- bien so khong trong seed, `in`
- bien so khong trong seed, `out`

Dau ra:
- backend business rule on dinh hon
- test case moi cho cac nhanh tren

Thoi gian uoc tinh:
- `1 ngay`

---

## Phase 4 - Mo rong backend API cho dashboard van hanh
**Muc tieu**: dashboard co du du lieu de xai duoc that

API can uu tien them:
- `GET /api/v1/accounts`
  - tim kiem theo plate
  - filter theo `registration_status`
  - pagination
- `GET /api/v1/accounts/summary`
  - tong `registered`
  - tong `temporary_registered`
  - tong tai khoan
- `POST /api/v1/accounts/import-preview` hoac script-only summary
- `POST /api/v1/accounts/{plate}/mark-registered`
- `POST /api/v1/accounts/{plate}/adjust-balance`

Neu muon giu MVP gon:
- bat buoc nhat la `GET /api/v1/accounts`
- sau do moi them `summary`

Dau ra:
- dashboard co du endpoint de hien thi va thao tac

Thoi gian uoc tinh:
- `1-1.5 ngay`

---

## Phase 5 - Dashboard cho luong seed plates
**Muc tieu**: demo duoc he thong quan ly bien so ma khong can AI

UI can co:
- trang danh sach bien so da import
- o tim kiem bien so
- filter `registered / temporary_registered`
- trang chi tiet account:
  - so du
  - registration_status
  - lich su giao dich
  - barrier action lien quan
- trang event history
- trang verify hold queue

Widget tong quan nen co:
- tong so bien so da seed
- tong so tai khoan registered
- tong so tai khoan temporary
- tong so event in/out

Dau ra:
- operator co the demo duoc luong quan tri

Thoi gian uoc tinh:
- `1-2 ngay`

---

## Phase 6 - Demo data va end-to-end mo phong
**Muc tieu**: co kich ban demo khong phu thuoc model that

Can chuan bi:
- 1 tap plates da seed
- 1 tap payload event gia lap:
  - bien so da seed vao cong
  - bien so da seed ra cong
  - bien so la vao cong
  - bien so tam ra cong

Can quan sat:
- transaction co sinh dung khong
- barrier action co dung rule khong
- dashboard co hien dung khong
- verify hold co cap nhat duoc khong

Dau ra:
- kich ban demo hoan chinh khong can OCR

Thoi gian uoc tinh:
- `0.5-1 ngay`

---

## 7) Lo trinh uu tien rat thuc dung

### MVP nhanh nhat
Neu muon co demo som, di theo thu tu nay:
1. chot CSV seed contract
2. viet script import local
3. seed `accounts` + `init transactions`
4. sua rule `registered + out`
5. them `GET /api/v1/accounts`
6. dashboard list/search account
7. tao event gia lap de demo

### Nen de sau
- upload file import qua dashboard
- provenance chi tiet cho moi plate
- import batch history day du
- OCR/runtime that

---

## 8) Thiet ke du lieu de xuat cho seed import

### Cach di toi thieu, it sua schema
Dung bang hien tai:
- `accounts`
- `transactions`

Policy:
- moi plate moi -> tao `Account`
- tao `Transaction(type='init')`
- `registration_status='registered'`
- `balance_vnd=100000`

Uu diem:
- nhanh
- dung duoc ngay

Nhuoc diem:
- chua theo doi duoc provenance import tot

### Cach di tot hon, nhung ton cong hon
Them metadata import, vi du:
- `account_source`
- `seed_group`
- `imported_at`

Uu diem:
- audit tot hon
- dashboard bao cao seed tot hon

Nhuoc diem:
- phai sua schema va API

Khuyen nghi:
- MVP di theo cach toi thieu
- provenance de phase 2

---

## 9) Checklist nghiem thu
- [ ] Da co file seed bien so duoc normalize va dedupe
- [ ] Import lai khong tao duplicate account
- [ ] Account moi duoc cong `init transaction`
- [ ] Bien so seed khi vao cong duoc xu ly theo nhanh `registered`
- [ ] Bien so seed khi ra cong khong bi hold sai logic
- [ ] Bien so la van di vao nhanh `temporary_registered`
- [ ] Dashboard tim kiem duoc bien so
- [ ] Dashboard xem duoc so du va lich su giao dich
- [ ] Dashboard xem duoc barrier actions va verify hold

---

## 10) Ket qua mong doi sau plan nay
Sau khi lam xong plan nay, du an se co:
- 1 luong demo khong phu thuoc AI that
- 1 tap bien so seed gia lap tu VNLP
- backend co du nghiep vu tai khoan/giao dich/barrier co the test that
- dashboard co gia tri van hanh som

Va quan trong nhat:
- team co the tiep tuc xay backend/dashboard trong luc nhom AI lam model that

