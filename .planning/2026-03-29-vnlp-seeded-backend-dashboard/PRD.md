# PRODUCT REQUIREMENTS DOCUMENT
## Seeded mode cho he thong quan ly bien so ra vao

**Version**: 1.0  
**Ngay cap nhat**: 2026-03-29  
**Trang thai**: Ready for implementation  

---

## 1) Muc tieu san pham
Xay dung mot che do van hanh prototype trong do:
- he thong khong can OCR that
- he thong khong can model detect that
- bien so da duoc coi nhu biet truoc o dau vao

Che do nay cho phep team:
- tiep tuc xay backend
- tiep tuc xay dashboard
- demo luong nghiep vu thanh chan
- test nghiep vu tai chinh theo bien so
- khong bi block boi bai toan AI/train

---

## 2) Pham vi trien khai

### 2.1 In-scope
- 1 nguon seed plate list duoc rut tu filename VNLP
- import seed batch vao database
- account va balance theo bien so
- transaction history theo bien so
- event in/out gia lap co `plate_text`
- barrier decision theo `registration_status`
- dashboard list/search/detail/verify queue
- summary so luong `registered / temporary_registered / total`

### 2.2 Out-of-scope
- plate detector that
- OCR that
- camera runtime production
- tracking/counting production
- hardware barrier integration that
- dong bo nhieu camera

---

## 3) Nguon du lieu seed
Can cu seed du lieu:
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\list_two_rows_label_xe_may.txt`
- `G:\TTMT\datn\data\external\vnlp\VNLP_detection\detection\VNLP_readme`

Gia dinh chot:
- `plate_text` duoc parse tu filename
- sau normalize upper-case, bo separator, bo space
- seed batch hien tai co the tao tu khoang `3227` bien so unique tu file list dang xet

Seed artifact muc tieu:
- `registered_plates_seed.csv`

---

## 4) Personas
- **Bao ve cong**: xem event, xem hold queue, verify xe tam ra cong
- **Van hanh he thong**: import seed batch, theo doi tong so tai khoan va event
- **Nguoi phat trien backend/dashboard**: co du lieu that de test API va UI ma khong can doi AI

---

## 5) Use cases chinh
- UC01: Import danh sach bien so da biet truoc vao he thong
- UC02: Tim kiem account theo bien so
- UC03: Xem so du va lich su giao dich cua mot bien so
- UC04: Nhan event `in` cho bien so da dang ky
- UC05: Nhan event `out` cho bien so da dang ky
- UC06: Nhan event `in` cho bien so chua dang ky va tao `temporary_registered`
- UC07: Nhan event `out` cho bien so tam va yeu cau verify
- UC08: Bao ve verify barrier action bi hold
- UC09: Dashboard xem duoc tong quan va danh sach xu ly

---

## 6) Functional requirements

### 6.1 Seed import
- FR-01: He thong phai nhan mot file seed CSV co toi thieu cot `plate_text`
- FR-02: He thong phai normalize bien so truoc khi import
- FR-03: He thong phai dedupe bien so trong cung seed batch
- FR-04: He thong phai co summary `imported / skipped / invalid`
- FR-05: He thong phai idempotent o muc MVP

### 6.2 Account va transaction
- FR-06: Moi bien so moi duoc tao thanh 1 account
- FR-07: Account moi seed vao co `registration_status=registered`
- FR-08: Account moi seed vao co `balance_vnd=100000`
- FR-09: Account moi phai co `init transaction`
- FR-10: Moi event in/out phai tru `2000 VND`
- FR-11: He thong phai cho phep so du am

### 6.3 Barrier rules
- FR-12: `registered + in` -> `open`
- FR-13: `registered + out` -> `open`
- FR-14: `unknown + in` -> tao `temporary_registered` va `open`
- FR-15: `temporary_registered + out` -> `hold`
- FR-16: Bao ve co the verify `hold` de mo barrier

### 6.4 Backend API
- FR-17: Co API lay account theo bien so
- FR-18: Co API list/search accounts
- FR-19: Co API list transactions theo bien so
- FR-20: Co API list barrier actions theo bien so
- FR-21: Co API verify barrier action
- FR-22: Co API summary accounts

### 6.5 Dashboard
- FR-23: Hien danh sach account / bien so
- FR-24: Search theo bien so
- FR-25: Filter theo `registration_status`
- FR-26: Hien chi tiet account
- FR-27: Hien so du va lich su giao dich
- FR-28: Hien lich su event va barrier action
- FR-29: Hien verify queue cho barrier hold
- FR-30: Hien tong quan `registered / temporary_registered / total`

---

## 7) Non-functional requirements
- NFR-01: Typed-first, backend schema va dashboard contract phai ro rang
- NFR-02: Import seed batch phai lap lai duoc
- NFR-03: Seeded mode phai demo duoc ma khong can AI runtime
- NFR-04: Rule nghiep vu phai co test case cho 4 nhanh co ban
- NFR-05: Dashboard phai tra cuu trong thoi gian chap nhan duoc tren quy mo seed prototype

---

## 8) Data model cot loi
- `accounts(id, plate_text, balance_vnd, registration_status, created_at, updated_at)`
- `transactions(id, account_id, event_id, amount_vnd, balance_after_vnd, type, created_at)`
- `vehicle_events(id, camera_id, timestamp, direction, vehicle_type, track_id, created_at)`
- `plate_reads(id, event_id, plate_text, confidence, snapshot_url, crop_url, ocr_status, created_at)`
- `barrier_actions(id, event_id, plate_text, registration_status, barrier_action, barrier_reason, needs_verification, verified_by, verified_at, created_at)`

MVP chua bat buoc:
- bang `import_batches`
- metadata provenance chi tiet trong schema

---

## 9) Gia tri kinh doanh / gia tri ky thuat
Gia tri cua seeded mode:
- backend va dashboard khong bi block boi AI
- co the test nghiep vu so du va barrier som
- co the demo cho stakeholder som hon
- giam rui ro "cho xong model moi bat dau xay he thong"

---

## 10) Rui ro va open questions
- RQ-01: Rule `registered + out` co duoc mo tu dong hay can mot policy khac?
- RQ-02: Import lai cung mot batch seed thi skip hay update?
- RQ-03: Co can luu provenance `source`, `seed_group`, `imported_at` ngay trong schema MVP khong?
- RQ-04: Co can import UI tren dashboard o phase 1, hay script local la du?

---

## 11) KPI nghiem thu
- KPI-01: Import thanh cong seed batch ma khong tao duplicate account
- KPI-02: Registered plate `in/out` deu di dung nhanh `open`
- KPI-03: Unknown plate `in` tao duoc `temporary_registered`
- KPI-04: Temporary plate `out` bi `hold` va verify duoc
- KPI-05: Dashboard tra cuu duoc bien so, so du, transactions, barrier history
- KPI-06: Demo duoc luong nghiep vu ma khong can OCR/detector that

