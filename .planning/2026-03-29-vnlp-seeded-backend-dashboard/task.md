# Task checklist - VNLP seeded backend dashboard

Ngay: 2026-03-29

## Tai lieu va pham vi
- [x] Tao `PRD.md` rieng cho seeded mode.
- [x] Tao `IMPLEMENTATION_PLAN.md` rieng cho seeded mode.
- [x] Tao `API_CONTRACT.md` tuong ung `.artifacts`.
- [x] Tao `DB_SCHEMA.md` tuong ung `.artifacts`.
- [x] Tao `DASHBOARD_WIREFRAME.md` tuong ung `.artifacts`.
- [x] Tao `TEST_PLAN.md` tuong ung `.artifacts`.
- [x] Tao `BASELINE_EVALUATION_REPORT.md` tuong ung `.artifacts`.
- [x] Tao `ARTIFACT_MERGE_MAP.md` de huong dan merge nguoc ve `.artifacts`.
- [x] Xac dinh ro phase nay khong phu thuoc OCR/train/model that.
- [x] Xac dinh ro dau vao la `plate_text` da co san.

## Chuan bi du lieu seed
- [x] Xac dinh filename VNLP chua chuoi bien so.
- [x] Xac dinh `list_two_rows_label_xe_may.txt` co the dung de rut bien so ma khong can OCR.
- [x] Thong ke nhanh file list: `5593` dong, `3227` bien so unique sau normalize upper-case.
- [ ] Chot contract `registered_plates_seed.csv`.
- [ ] Chot cac cot bat buoc: `plate_text`, `source`, `seed_group`.
- [ ] Chot cac cot nen co: `vehicle_type`, `note`.
- [ ] Chot rule normalize bien so duy nhat.
- [ ] Chot policy dedupe trong cung seed batch.
- [ ] Tao `registered_plates_seed.csv`.
- [ ] Tao `registered_plates_seed_summary.json`.

## Import script vao database
- [ ] Tao script import local/CLI.
- [ ] Script phai normalize bien so truoc khi ghi DB.
- [ ] Script phai dedupe truoc khi import.
- [ ] Script phai upsert theo `plate_text`.
- [ ] Script phai tao `Account` moi cho plate chua ton tai.
- [ ] Script phai gan `registration_status=registered` cho account moi.
- [ ] Script phai gan `balance_vnd=100000` cho account moi.
- [ ] Script phai tao `Transaction(type='init')` cho account moi.
- [ ] Script phai sinh summary: `imported / skipped / invalid`.
- [ ] Script phai idempotent o muc MVP.

## Logic nghiep vu backend
- [x] Xac dinh logic hien tai da co `registered + in`.
- [x] Xac dinh logic hien tai da co `temporary_registered + in`.
- [x] Xac dinh logic hien tai da co `temporary_registered + out`.
- [ ] Sua rule cho `registered + out -> open`.
- [ ] Review lai y nghia `unknown` trong seeded mode.
- [ ] Dam bao plate trong seed khong bi tao lai thanh `temporary_registered`.
- [ ] Dam bao unknown plate `in` van tao `temporary_registered`.
- [ ] Dam bao temporary plate `out` van `hold`.
- [ ] Dam bao verify hold van chay dung.

## Backend API
- [ ] Them `GET /api/v1/accounts` co search + filter + pagination.
- [ ] Them `GET /api/v1/accounts/summary`.
- [ ] Dam bao `GET /api/v1/accounts/{plate_text}` dung voi account seed.
- [ ] Dam bao `GET /api/v1/accounts/{plate_text}/transactions` hien dung `init transaction`.
- [ ] Dam bao `GET /api/v1/barrier-actions?plate=...` dung voi seeded flow.
- [ ] Dam bao `POST /api/v1/barrier-actions/verify` chay dung.
- [ ] Xem xet `POST /api/v1/accounts/{plate}/mark-registered`.
- [ ] Xem xet `POST /api/v1/accounts/{plate}/adjust-balance`.

## Backend test
- [ ] Test import plate moi -> tao account + init transaction.
- [ ] Test import duplicate -> khong tao duplicate account.
- [ ] Test registered plate `in`.
- [ ] Test registered plate `out`.
- [ ] Test unknown plate `in`.
- [ ] Test temporary plate `out`.
- [ ] Test verify hold van chay dung.

## Dashboard
- [ ] Them man hinh danh sach account / bien so.
- [ ] Them o search theo bien so.
- [ ] Them filter theo `registration_status`.
- [ ] Them trang chi tiet account.
- [ ] Hien so du hien tai.
- [ ] Hien lich su giao dich.
- [ ] Hien lich su event lien quan.
- [ ] Hien barrier action lien quan.
- [ ] Them verify queue cho barrier hold.
- [ ] Them tong quan `registered / temporary_registered / total`.

## Demo flow gia lap
- [ ] Chuan bi tap plate da seed de demo.
- [ ] Chuan bi payload event cho registered plate `in`.
- [ ] Chuan bi payload event cho registered plate `out`.
- [ ] Chuan bi payload event cho unknown plate `in`.
- [ ] Chuan bi payload event cho temporary plate `out`.
- [ ] Xac nhan dashboard hien dung sau moi kich ban.
- [ ] Xac nhan transaction va barrier action dung theo rule.

## Provenance va audit (de sau neu can)
- [ ] Can nhac them `source`, `seed_group`, `imported_at` vao schema.
- [ ] Can nhac bang `import_batches`.
- [ ] Can nhac dashboard import summary.

## Merge prep ve `.artifacts`
- [x] Giu cung ten file voi `.artifacts` cho cac tai lieu cot loi.
- [x] Giu ket cau section gan voi `.artifacts`.
- [ ] So khop lai `PRD.md` seeded mode voi `PRD.md` goc truoc khi merge.
- [ ] So khop lai `IMPLEMENTATION_PLAN.md` seeded mode voi plan goc truoc khi merge.
- [ ] So khop lai `API_CONTRACT.md` seeded mode voi contract goc truoc khi merge.
- [ ] So khop lai `DB_SCHEMA.md` seeded mode voi schema goc truoc khi merge.
- [ ] So khop lai `TEST_PLAN.md` seeded mode voi test plan goc truoc khi merge.
- [ ] Chot chien luoc giu `AI-first path` va `seeded-first path` song song trong `.artifacts`.

## Kiem thu cuoi
- [ ] Import seed chay duoc tu dau den cuoi.
- [ ] Khong tao duplicate account khi import lai.
- [ ] Registered plate `in/out` deu di dung nhanh `open`.
- [ ] Unknown plate `in` tao duoc `temporary_registered`.
- [ ] Temporary plate `out` bi `hold` va verify duoc.
- [ ] Dashboard tra cuu duoc bien so, balance, transactions, barrier history.
- [ ] Demo duoc luong nghiep vu ma khong can AI/OCR that.

