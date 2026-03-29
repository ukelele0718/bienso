# IMPLEMENTATION PLAN
## Ke hoach trien khai rieng cho luong VNLP seeded backend dashboard

**Version**: 1.1  
**Ngay cap nhat**: 2026-03-29  
**Pham vi**: bo qua OCR/train trong giai doan nay, coi nhu da co `plate_text` va tap trung vao import database, backend nghiep vu, dashboard, va demo luong thanh chan  

---

## 0) Muc tieu trien khai
Trien khai nhanh mot prototype theo luong bat buoc:

`VNLP filename list` -> `seed file bien so` -> `import vao DB` -> `event gia lap co plate_text` -> `backend nghiep vu` -> `dashboard van hanh`

He thong can bao phu duoc:
- import danh sach bien so da normalize vao `accounts`
- khoi tao so du mac dinh `100000 VND`
- tru `2000 VND` cho moi event in/out
- cho phep so du am
- mo phong luong thanh chan:
  - bien so da dang ky vao: mo
  - bien so da dang ky ra: mo
  - bien so la vao: tao `temporary_registered` va mo
  - bien so tam ra: hold va yeu cau verify

---

## 0.1) Can cu du lieu dau vao
Tu:
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt`
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\VNLP_readme`

Co the suy ra:
- filename da chua `plate_text`
- filename da chua thong tin bbox
- khong can OCR de rut bien so cho phase nay

Thong ke hien tai tren file list:
- tong so dong: `5593`
- tong so plate parse duoc: `5593`
- tong so plate unique sau normalize upper-case: `3227`

Suy ra:
- file nay du de tao mot seed batch `registered plates`
- luong seeded mode co the duoc xay song song voi nhom AI/train

---

## 1) Scope lock checklist
- [x] Dau vao cua he thong trong phase nay la `plate_text` da co san
- [x] Chi tap trung vao backend + dashboard + import + event gia lap
- [x] Khong phu thuoc OCR that
- [x] Khong phu thuoc detector that
- [x] Khong phu thuoc runtime camera that
- [ ] Chot contract `registered_plates_seed.csv`
- [ ] Chot rule normalize bien so duy nhat
- [ ] Chot rule `registered + out -> open`
- [ ] Chot policy import lai seed batch

---

## 2) Work Breakdown Structure (WBS)

## Phase 1 - Finalize seeded-mode PRD + data contract
### Deliverables
- `PRD.md` cho luong seeded mode
- contract `registered_plates_seed.csv`
- rule normalize va dedupe duoc chot

### Checklist
- [x] Chot pham vi "khong AI that"
- [x] Chot nguon seed tu VNLP filename list
- [ ] Chot cot bat buoc: `plate_text`, `source`, `seed_group`
- [ ] Chot cot nen co: `vehicle_type`, `note`
- [ ] Chot rule upper-case / bo separator / bo space
- [ ] Chot policy duplicate plate trong cung seed

### Thoi gian uoc tinh
- `0.5 ngay`

---

## Phase 2 - Seed extraction artifact
### Deliverables
- `registered_plates_seed.csv`
- `registered_plates_seed_summary.json`
- report duplicate / invalid / normalized

### Checklist
- [ ] Doc file list VNLP
- [ ] Parse `plate_text` tu filename
- [ ] Normalize bien so
- [ ] Dedupe theo `plate_text`
- [ ] Gan `source=vnlp_two_rows_xe_may`
- [ ] Gan `seed_group`
- [ ] Xuat file CSV seed
- [ ] Xuat file summary de audit

### Thoi gian uoc tinh
- `0.5 ngay`

---

## Phase 3 - Import path vao database
### Deliverables
- script import local/CLI
- import summary ro rang
- du lieu `accounts` + `transactions` duoc seed

### Checklist
- [ ] Tao script import local
- [ ] Input: `registered_plates_seed.csv`
- [ ] Upsert theo `plate_text`
- [ ] Account moi:
  - [ ] `registration_status=registered`
  - [ ] `balance_vnd=100000`
  - [ ] sinh `Transaction(type='init')`
- [ ] Account da ton tai:
  - [ ] skip hoac update theo policy da chot
- [ ] In summary:
  - [ ] imported
  - [ ] skipped
  - [ ] invalid
- [ ] Dam bao import idempotent o muc MVP

### Thoi gian uoc tinh
- `0.5-1 ngay`

---

## Phase 4 - Backend business rule fix for seeded mode
### Deliverables
- rule nghiep vu khop seeded mode
- test case cho 4 nhanh chinh

### Checklist
- [ ] Bo sung rule `registered + out -> open`
- [ ] Review lai y nghia `unknown`
- [ ] Dam bao seed plate khong bi tao lai thanh `temporary_registered`
- [ ] Dam bao unknown plate `in` van tao `temporary_registered`
- [ ] Dam bao `temporary_registered + out -> hold`
- [ ] Dam bao verify hold van mo duoc barrier

### Test case bat buoc
- [ ] registered plate + in
- [ ] registered plate + out
- [ ] unknown plate + in
- [ ] temporary_registered plate + out

### Thoi gian uoc tinh
- `1 ngay`

---

## Phase 5 - Backend API expansion
### Deliverables
- API cho dashboard van hanh duoc
- API list/search/summary account

### Checklist
- [ ] `GET /api/v1/accounts`
  - [ ] search theo plate
  - [ ] filter theo `registration_status`
  - [ ] pagination
- [ ] `GET /api/v1/accounts/summary`
- [ ] `GET /api/v1/accounts/{plate}`
- [ ] `GET /api/v1/accounts/{plate}/transactions`
- [ ] `GET /api/v1/barrier-actions?plate=...`
- [ ] `POST /api/v1/barrier-actions/verify`
- [ ] Can nhac `POST /api/v1/accounts/{plate}/mark-registered`
- [ ] Can nhac `POST /api/v1/accounts/{plate}/adjust-balance`

### Thoi gian uoc tinh
- `1-1.5 ngay`

---

## Phase 6 - Dashboard seeded mode
### Deliverables
- dashboard co the demo duoc ma khong can AI
- operator flow ro rang

### Checklist
- [ ] danh sach account / bien so
- [ ] o search bien so
- [ ] filter `registered / temporary_registered`
- [ ] trang chi tiet account
- [ ] hien so du hien tai
- [ ] hien lich su giao dich
- [ ] hien lich su event
- [ ] hien barrier action lien quan
- [ ] verify queue cho barrier hold
- [ ] tong quan so luong:
  - [ ] total accounts
  - [ ] registered
  - [ ] temporary_registered
  - [ ] event in/out

### Thoi gian uoc tinh
- `1-2 ngay`

---

## Phase 7 - Simulated event flow and QA
### Deliverables
- bo event payload gia lap
- end-to-end demo seeded mode
- checklist nghiem thu pass

### Checklist
- [ ] tao payload event gia lap cho registered plate in
- [ ] tao payload event gia lap cho registered plate out
- [ ] tao payload event gia lap cho unknown plate in
- [ ] tao payload event gia lap cho temporary plate out
- [ ] verify balance thay doi dung
- [ ] verify barrier action dung
- [ ] verify dashboard hien thi dung
- [ ] verify search + history + verify queue

### Thoi gian uoc tinh
- `0.5-1 ngay`

---

## Phase 8 - Optional provenance and import audit
### Deliverables
- import metadata ro rang hon
- co kha nang audit batch import

### Checklist
- [ ] can nhac them `source`
- [ ] can nhac them `seed_group`
- [ ] can nhac them `imported_at`
- [ ] can nhac bang `import_batches`
- [ ] can nhac dashboard import summary

### Thoi gian uoc tinh
- `de sau MVP`

---

## 3) Thach thuc va huong giai quyet

### Thach thuc 1 - Seed data khong phai du lieu van hanh that
Rui ro:
- plate list lay tu VNLP co the trung lap, khong dai dien user that

Huong giai quyet:
- seed chi dung cho backend/dashboard prototype
- luon luu `source` va `seed_group`
- tach ro seeded mode voi production mode

### Thach thuc 2 - Rule backend hien tai chua khop seeded mode
Rui ro:
- `registered + out` hien roi vao `default_hold`

Huong giai quyet:
- sua som trong `services.py`
- bo sung test de khoa rule

### Thach thuc 3 - Import bi duplicate hoac tao lai account
Rui ro:
- balance va transaction history sai

Huong giai quyet:
- import idempotent
- unique theo `plate_text`
- init transaction chi tao cho account moi

### Thach thuc 4 - Dashboard hien chua co man hinh quan tri account day du
Rui ro:
- du lieu da seed nhung operator khong xem duoc luong nghiep vu

Huong giai quyet:
- uu tien list/search/detail/verify queue truoc

---

## 4) Typed Quality Gate
- [x] API contracts typed bang Pydantic
- [x] Dashboard typed bang TypeScript
- [ ] Moi API moi deu co schema output ro rang
- [ ] Moi script import moi deu co type annotations co ban
- [ ] Khong merge neu API va dashboard lech contract

---

## 5) KPI nghiem thu cho seeded mode
- [ ] Import duoc seed batch vao DB ma khong duplicate account
- [ ] Account moi co `registration_status=registered`
- [ ] Account moi co `balance_vnd=100000` va `init transaction`
- [ ] Registered plate `in` -> barrier `open`
- [ ] Registered plate `out` -> barrier `open`
- [ ] Unknown plate `in` -> tao `temporary_registered` va `open`
- [ ] Temporary plate `out` -> `hold` va verify duoc
- [ ] Dashboard search theo bien so chay dung
- [ ] Dashboard xem duoc balance va transactions
- [ ] Dashboard xem duoc barrier verify queue
- [ ] Demo duoc end-to-end ma khong can AI/OCR that

---

## 6) Thu tu uu tien de ra ket qua nhanh
Thu tu khuyen nghi:
1. Chot PRD seeded mode
2. Chot contract `registered_plates_seed.csv`
3. Tao seed CSV tu file list VNLP
4. Viet script import DB
5. Sua rule `registered + out`
6. Them API list/search/summary account
7. Lam dashboard list/detail/verify queue
8. Tao event payload gia lap
9. Chay end-to-end demo

Neu can rut ngan hon nua:
- bo qua provenance phase
- bo qua import-preview UI
- uu tien script import local thay vi upload file tren dashboard

