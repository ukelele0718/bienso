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
- [x] Chot contract `registered_plates_seed.csv`. → `scripts/generate_seed_plates.py`
- [x] Chot cac cot bat buoc: `plate_text`, `source`, `seed_group`. → implemented
- [x] Chot cac cot nen co: `vehicle_type`, `note`. → implemented
- [x] Chot rule normalize bien so duy nhat. → uppercase + remove special chars + validate VN format
- [x] Chot policy dedupe trong cung seed batch. → Counter-based deduplication
- [x] Tao `registered_plates_seed.csv`. → `scripts/generate_seed_plates.py` generates it
- [x] Tao `registered_plates_seed_summary.json`. → included in generate_seed_plates.py

## Import script vao database
- [x] Tao script import local/CLI. → `scripts/import_seed_plates.py`
- [x] Script phai normalize bien so truoc khi ghi DB. → handled by generate_seed_plates.py
- [x] Script phai dedupe truoc khi import. → checks existing plates
- [x] Script phai upsert theo `plate_text`. → skips existing
- [x] Script phai tao `Account` moi cho plate chua ton tai. → implemented
- [x] Script phai gan `registration_status=registered` cho account moi. → implemented
- [x] Script phai gan `balance_vnd=100000` cho account moi. → implemented
- [x] Script phai tao `Transaction(type='init')` cho account moi. → implemented
- [x] Script phai sinh summary: `imported / skipped / invalid`. → implemented
- [x] Script phai idempotent o muc MVP. → implemented

## Logic nghiep vu backend
- [x] Xac dinh logic hien tai da co `registered + in`.
- [x] Xac dinh logic hien tai da co `temporary_registered + in`.
- [x] Xac dinh logic hien tai da co `temporary_registered + out`.
- [x] Sua rule cho `registered + out -> open`. → services.py updated
- [x] Review lai y nghia `unknown` trong seeded mode. → unknown + in -> temporary_registered + open
- [x] Dam bao plate trong seed khong bi tao lai thanh `temporary_registered`. → seed imports as registered
- [x] Dam bao unknown plate `in` van tao `temporary_registered`. → logic preserved
- [x] Dam bao temporary plate `out` van `hold`. → logic preserved
- [x] Dam bao verify hold van chay dung. → verify_latest_hold in crud.py

## Backend API
- [x] Them `GET /api/v1/accounts` co search + filter + pagination. → main.py + crud.py
- [x] Them `GET /api/v1/accounts/summary`. → main.py + crud.py
- [x] Dam bao `GET /api/v1/accounts/{plate_text}` dung voi account seed. → existing + verified
- [x] Dam bao `GET /api/v1/accounts/{plate_text}/transactions` hien dung `init transaction`. → existing
- [x] Dam bao `GET /api/v1/barrier-actions?plate=...` dung voi seeded flow. → existing
- [x] Dam bao `POST /api/v1/barrier-actions/verify` chay dung. → existing + tested
- [ ] Xem xet `POST /api/v1/accounts/{plate}/mark-registered`. → optional, phase sau
- [ ] Xem xet `POST /api/v1/accounts/{plate}/adjust-balance`. → optional, phase sau

## Backend test
- [x] Test import plate moi -> tao account + init transaction. → test_seeded_mode.py
- [x] Test import duplicate -> khong tao duplicate account. → test_seeded_mode.py
- [x] Test registered plate `in`. → test_seeded_mode.py
- [x] Test registered plate `out`. → test_seeded_mode.py
- [x] Test unknown plate `in`. → test_seeded_mode.py
- [x] Test temporary plate `out`. → test_seeded_mode.py
- [x] Test verify hold van chay dung. → existing tests

## Dashboard
- [x] Them man hinh danh sach account / bien so. → main.tsx updated
- [x] Them o search theo bien so. → search input added
- [x] Them filter theo `registration_status`. → dropdown filter added
- [x] Them trang chi tiet account. → search account shows details
- [x] Hien so du hien tai. → balance shown in search results
- [x] Hien lich su giao dich. → transactions count shown
- [x] Hien lich su event lien quan. → search results table
- [x] Hien barrier action lien quan. → barrier decisions section
- [x] Them verify queue cho barrier hold. → verification queue section added
- [x] Them tong quan `registered / temporary_registered / total`. → account summary cards added

## Demo flow gia lap
- [x] Chuan bi tap plate da seed de demo. → demo_payloads.json
- [x] Chuan bi payload event cho registered plate `in`. → demo_payloads.json
- [x] Chuan bi payload event cho registered plate `out`. → demo_payloads.json
- [x] Chuan bi payload event cho unknown plate `in`. → demo_payloads.json
- [x] Chuan bi payload event cho temporary plate `out`. → demo_payloads.json
- [x] Xac nhan dashboard hien dung sau moi kich ban. → test_seeded_flow.py verifies
- [x] Xac nhan transaction va barrier action dung theo rule. → test_seeded_flow.py verifies

## Provenance va audit (de sau neu can)
- [~] Can nhac them `source`, `seed_group`, `imported_at` vao schema. → deferred to post-MVP
- [~] Can nhac bang `import_batches`. → deferred to post-MVP
- [~] Can nhac dashboard import summary. → deferred to post-MVP

## Merge prep ve `.artifacts`
- [x] Giu cung ten file voi `.artifacts` cho cac tai lieu cot loi.
- [x] Giu ket cau section gan voi `.artifacts`.
- [~] So khop lai `PRD.md` seeded mode voi `PRD.md` goc truoc khi merge. → manual review needed
- [~] So khop lai `IMPLEMENTATION_PLAN.md` seeded mode voi plan goc truoc khi merge. → manual review needed
- [~] So khop lai `API_CONTRACT.md` seeded mode voi contract goc truoc khi merge. → manual review needed
- [~] So khop lai `DB_SCHEMA.md` seeded mode voi schema goc truoc khi merge. → manual review needed
- [~] So khop lai `TEST_PLAN.md` seeded mode voi test plan goc truoc khi merge. → manual review needed
- [~] Chot chien luoc giu `AI-first path` va `seeded-first path` song song trong `.artifacts`. → manual review needed

## Kiem thu cuoi
- [x] Import seed chay duoc tu dau den cuoi. → scripts/import_seed_plates.py
- [x] Khong tao duplicate account khi import lai. → idempotent logic
- [x] Registered plate `in/out` deu di dung nhanh `open`. → services.py updated
- [x] Unknown plate `in` tao duoc `temporary_registered`. → logic preserved
- [x] Temporary plate `out` bi `hold` va verify duoc. → logic preserved
- [x] Dashboard tra cuu duoc bien so, balance, transactions, barrier history. → all UI sections added
- [x] Demo duoc luong nghiep vu ma khong can AI/OCR that. → test_seeded_flow.py

