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
- [x] Chot contract `registered_plates_seed.csv`
- [x] Chot rule normalize bien so duy nhat
- [x] Chot rule `registered + out -> open`
- [x] Chot policy import lai seed batch

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
- [x] Chot cot bat buoc: `plate_text`, `source`, `seed_group`
- [x] Chot cot nen co: `vehicle_type`, `note`
- [x] Chot rule upper-case / bo separator / bo space
- [x] Chot policy duplicate plate trong cung seed

### Thoi gian uoc tinh
- `0.5 ngay`

---

## Phase 2 - Seed extraction artifact
### Deliverables
- `registered_plates_seed.csv`
- `registered_plates_seed_summary.json`
- report duplicate / invalid / normalized

### Checklist
- [x] Doc file list VNLP
- [x] Parse `plate_text` tu filename
- [x] Normalize bien so
- [x] Dedupe theo `plate_text`
- [x] Gan `source=vnlp_two_rows_xe_may`
- [x] Gan `seed_group`
- [x] Xuat file CSV seed
- [x] Xuat file summary de audit

### Thoi gian uoc tinh
- `0.5 ngay`

---

## Phase 3 - Import path vao database
### Deliverables
- script import local/CLI
- import summary ro rang
- du lieu `accounts` + `transactions` duoc seed

### Checklist
- [x] Tao script import local
- [x] Input: `registered_plates_seed.csv`
- [x] Upsert theo `plate_text`
- [x] Account moi:
  - [x] `registration_status=registered`
  - [x] `balance_vnd=100000`
  - [x] sinh `Transaction(type='init')`
- [x] Account da ton tai:
  - [x] skip hoac update theo policy da chot
- [x] In summary:
  - [x] imported
  - [x] skipped
  - [x] invalid
- [x] Dam bao import idempotent o muc MVP

### Thoi gian uoc tinh
- `0.5-1 ngay`

---

## Phase 4 - Backend business rule fix for seeded mode
### Deliverables
- rule nghiep vu khop seeded mode
- test case cho 4 nhanh chinh

### Checklist
- [x] Bo sung rule `registered + out -> open`
- [x] Review lai y nghia `unknown`
- [x] Dam bao seed plate khong bi tao lai thanh `temporary_registered`
- [x] Dam bao unknown plate `in` van tao `temporary_registered`
- [x] Dam bao `temporary_registered + out -> hold`
- [x] Dam bao verify hold van mo duoc barrier

### Test case bat buoc
- [x] registered plate + in
- [x] registered plate + out
- [x] unknown plate + in
- [x] temporary_registered plate + out

### Thoi gian uoc tinh
- `1 ngay`

---

## Phase 5 - Backend API expansion
### Deliverables
- API cho dashboard van hanh duoc
- API list/search/summary account

### Checklist
- [x] `GET /api/v1/accounts`
  - [x] search theo plate
  - [x] filter theo `registration_status`
  - [x] pagination
- [x] `GET /api/v1/accounts/summary`
- [x] `GET /api/v1/accounts/{plate}`
- [x] `GET /api/v1/accounts/{plate}/transactions`
- [x] `GET /api/v1/barrier-actions?plate=...`
- [x] `POST /api/v1/barrier-actions/verify`
- [x] Can nhac `POST /api/v1/accounts/{plate}/mark-registered`
- [x] Can nhac `POST /api/v1/accounts/{plate}/adjust-balance`

### Thoi gian uoc tinh
- `1-1.5 ngay`

---

## Phase 6 - Dashboard seeded mode
### Deliverables
- dashboard co the demo duoc ma khong can AI
- operator flow ro rang

### Checklist
- [x] danh sach account / bien so
- [x] o search bien so
- [x] filter `registered / temporary_registered`
- [x] trang chi tiet account
- [x] hien so du hien tai
- [x] hien lich su giao dich
- [x] hien lich su event
- [x] hien barrier action lien quan
- [x] verify queue cho barrier hold
- [x] tong quan so luong:
  - [x] total accounts
  - [x] registered
  - [x] temporary_registered
  - [x] event in/out

### Thoi gian uoc tinh
- `1-2 ngay`

---

## Phase 7 - Simulated event flow and QA
### Deliverables
- bo event payload gia lap
- end-to-end demo seeded mode
- checklist nghiem thu pass

### Checklist
- [x] tao payload event gia lap cho registered plate in
- [x] tao payload event gia lap cho registered plate out
- [x] tao payload event gia lap cho unknown plate in
- [x] tao payload event gia lap cho temporary plate out
- [x] verify balance thay doi dung
- [x] verify barrier action dung
- [x] verify dashboard hien thi dung
- [x] verify search + history + verify queue

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
- [x] Moi API moi deu co schema output ro rang
- [x] Moi script import moi deu co type annotations co ban
- [x] Khong merge neu API va dashboard lech contract

---

## 5) KPI nghiem thu cho seeded mode
- [x] Import duoc seed batch vao DB ma khong duplicate account
- [x] Account moi co `registration_status=registered`
- [x] Account moi co `balance_vnd=100000` va `init transaction`
- [x] Registered plate `in` -> barrier `open`
- [x] Registered plate `out` -> barrier `open`
- [x] Unknown plate `in` -> tao `temporary_registered` va `open`
- [x] Temporary plate `out` -> `hold` va verify duoc
- [x] Dashboard search theo bien so chay dung
- [x] Dashboard xem duoc balance va transactions
- [x] Dashboard xem duoc barrier verify queue
- [x] Demo duoc end-to-end ma khong can AI/OCR that

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

