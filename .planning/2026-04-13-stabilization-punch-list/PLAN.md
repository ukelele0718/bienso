# STABILIZATION PUNCH LIST
## Ke hoach xu ly cac diem ton dong truoc khi merge

**Ngay tao**: 2026-04-13  
**Nhanh hien tai**: `feat/vnlp-seeded-backend-dashboard`  
**Muc tieu**: Dong tat ca gap truoc khi chuyen sang Phase 2-3 cua Integration Roadmap.

---

## TONG QUAN 6 HANG MUC

| # | Hang muc | Muc do | Uoc luong | Trang thai |
|---|----------|--------|-----------|------------|
| A | Fix datetime.utcnow -> aware datetime | Cao | 30-45 phut | DONE (c561e64) |
| B | Unit tests barrier_rules + normalize | Cao | 30-45 phut | DONE (723196b) — 51/51 pass, fix 9 pre-existing fails |
| C | Cau hinh mypy/pyright cho backend | Trung binh | 20-30 phut | DONE (edad636) — mypy clean, 0 errors |
| D | Bo sung tests cho pretrained branch | Cao | 45-60 phut |
| E | Integration branch — full test matrix | Cao | 60 phut |
| F | Don dep uncommitted changes + baseline eval | Thap | 15-20 phut |

---

## A) FIX DATETIME.UTCNOW -> AWARE DATETIME

**Van de**: 16 cho dung `datetime.utcnow()` (naive, khong co timezone).  
Python 3.12+ deprecated `utcnow()`. Can chuyen sang `datetime.now(UTC)`.

### A.1 Backend models (apps/backend/app/models.py)
- [x] Line 21: `Camera.created_at` default -> `datetime.now(UTC)`
- [x] Line 35: `Vehicle.created_at` default -> `datetime.now(UTC)`
- [x] Line 53: `PlateRead.created_at` default -> `datetime.now(UTC)`
- [x] Line 69: `Account.created_at` default -> `datetime.now(UTC)`
- [x] Line 70: `Account.updated_at` default -> `datetime.now(UTC)`
- [x] Line 89: `Transaction.created_at` default -> `datetime.now(UTC)`
- [x] Line 106: `PaymentRequest.created_at` default -> `datetime.now(UTC)`
- [x] Line 126: `ImportBatch.created_at` default -> `datetime.now(UTC)`
- [x] Line 136: `AuditLog.created_at` default -> `datetime.now(UTC)`

### A.2 Backend runtime (apps/backend/app/main.py)
- [x] Line 341: `/health` endpoint -> `datetime.now(UTC).isoformat()`

### A.3 Test files
- [x] `tests/test_barrier_api.py` line 18
- [x] `tests/test_balance_rule.py` lines 13, 43
- [x] `tests/test_seeded_mode.py` (~21 instances, lines 107-109, 217-218, 243-244, etc.)

### A.4 Kiem tra sau fix
- [x] Chay `pytest` — 26 pass, 9 fail (pre-existing session isolation bug, khong lien quan datetime)
- [x] Grep lai `datetime.utcnow` — 0 instances
- [x] Commit: `fix(backend): replace deprecated utcnow with timezone-aware datetime` (c561e64)

---

## B) UNIT TESTS CHO BARRIER RULES + NORMALIZE

**Van de**: `barrier_rules.py` co unit test (`test_barrier_unit.py`) nhung can review do phu.
Chua co unit test cho normalize helper.

### B.1 Review + bo sung test_barrier_unit.py
- [ ] Test case: `registered` + `in` => `open`
- [ ] Test case: `registered` + `out` => `open`
- [ ] Test case: `temporary_registered` + `in` => `open`
- [ ] Test case: `temporary_registered` + `out` => `hold` + `needs_verification=true`
- [ ] Test case: `unknown` + `in` => tu tao `temporary_registered` + `open`
- [ ] Test case: `unknown` + `out` => `hold`
- [ ] Test case: plate_text = None/empty => xu ly an toan
- [ ] Test case: `barrier_reason` dung cho moi nhanh logic

### B.2 Tao tests cho normalize (neu co module normalize)
- [ ] Tim module normalize hien tai (grep `normalize` trong backend)
- [ ] Test: chuan hoa ky tu nham lan (O/0, I/1, B/8, S/5)
- [ ] Test: bien so 1 dong format
- [ ] Test: bien so 2 dong format
- [ ] Test: input rong/None => xu ly an toan
- [ ] Test: input co khoang trang/ky tu dac biet => strip dung

### B.3 Kiem tra sau bo sung
- [ ] Chay `pytest tests/test_barrier_unit.py -v` — all pass
- [ ] Chay `pytest tests/test_normalize.py -v` — all pass (neu tao moi)
- [ ] Commit: `test(backend): expand barrier rules and normalize unit coverage`

---

## C) CAU HINH MYPY/PYRIGHT CHO BACKEND

**Van de**: Khong co file cau hinh type checker nao trong backend.  
IMPLEMENTATION_PLAN yeu cau `mypy/pyright pass` nhung chua thiet lap.

### C.1 Chon tool va tao config
- [ ] Quyet dinh dung mypy hay pyright (de xuat: mypy vi pho bien hon voi FastAPI)
- [ ] Tao `apps/backend/pyproject.toml` hoac `apps/backend/mypy.ini` voi cau hinh co ban:
  ```
  [mypy]
  python_version = 3.11
  strict = false
  warn_return_any = true
  warn_unused_configs = true
  disallow_untyped_defs = false   # bat dan khi san sang
  ignore_missing_imports = true
  ```

### C.2 Chay lan dau va xu ly loi
- [ ] Chay `mypy apps/backend/app/` — ghi nhan so loi
- [ ] Fix loi critical (missing return types tren public functions)
- [ ] Fix loi type mismatch ro rang
- [ ] Tam ignore cac loi phuc tap bang `# type: ignore` co comment ly do

### C.3 Tich hop
- [ ] Them script `scripts/typecheck.sh` hoac lenh trong README
- [ ] Dam bao chay khong fail tren trang thai hien tai
- [ ] Commit: `chore(backend): add mypy config and fix critical type errors`

---

## D) BO SUNG TESTS CHO PRETRAINED BRANCH

**Van de**: `feat/pretrained-lpr-import-flow` thieu persistence tests va contract tests.  
Can on dinh truoc khi merge vao integration.

### D.1 Persistence tests
- [ ] Test tao `pretrained_jobs` row — verify fields luu dung
- [ ] Test tao `pretrained_detections` batch — verify count + fields
- [ ] Test job status lifecycle: `queued -> running -> success`
- [ ] Test job status lifecycle: `queued -> running -> failed`
- [ ] Test summary counts endpoint tra dung so lieu

### D.2 API contract tests
- [ ] `POST /api/v1/pretrained/infer` — tra 200 voi payload hop le
- [ ] `POST /api/v1/pretrained/infer` — tra 422 voi payload sai
- [ ] `POST /api/v1/pretrained/import` — tao job thanh cong
- [ ] `GET /api/v1/pretrained/jobs` — tra list co pagination
- [ ] `GET /api/v1/pretrained/jobs/{id}` — tra 200 voi id hop le
- [ ] `GET /api/v1/pretrained/jobs/{id}` — tra 404 voi id khong ton tai

### D.3 Dashboard smoke checklist
- [ ] Trang Pretrained Import hien thi duoc (khong crash)
- [ ] Form submit mock job hoat dong
- [ ] Table job history hien thi badge status dung
- [ ] Detail drawer mo duoc va hien thi meta

### D.4 Kiem tra
- [ ] Chay full pytest tren pretrained branch — all pass
- [ ] TypeScript `tsc --noEmit` pass
- [ ] Commit: `test(pretrained): add persistence and contract test coverage`

---

## E) INTEGRATION BRANCH — FULL TEST MATRIX

**Van de**: `feat/integration-seeded-pretrained` da merge rehearsal nhung chua qua full test matrix.  
Roadmap Phase 2 yeu cau test matrix v1 pass truoc khi chuyen phase.

### E.1 Backend unit tests
- [ ] Chay `pytest` tren integration branch — ghi nhan ket qua
- [ ] Fix bat ky test fail nao do merge conflict
- [ ] Xac nhan khong co import loi / module missing

### E.2 API contract tests
- [ ] Tat ca endpoint seeded: events, accounts, transactions, stats
- [ ] Tat ca endpoint pretrained: infer, import, jobs, summary
- [ ] Khong co response schema mismatch giua 2 flow

### E.3 Dashboard smoke
- [ ] Seeded section: KPI cards, account list, verify queue
- [ ] Pretrained section: job list, detail drawer
- [ ] Khong co TypeScript compile error
- [ ] Khong co runtime crash khi chuyen giua sections

### E.4 Regression nhanh
- [ ] Tao event seeded -> barrier decision dung
- [ ] Tao event seeded -> balance tru dung
- [ ] Tao job pretrained -> status lifecycle dung
- [ ] Search events theo plate + time range dung

### E.5 Ghi nhan ket qua
- [ ] Tao/cap nhat `INTEGRATION_TEST_MATRIX_RESULTS.md` trong planning
- [ ] Ghi ro: pass/fail, so luong, thoi gian chay
- [ ] Neu co fail: ghi root cause + fix plan
- [ ] Commit: `test(integration): complete test matrix v1 and record results`

---

## F) DON DEP + BASELINE EVALUATION

### F.1 Xu ly uncommitted changes
- [ ] Review `apps/backend/app/main.py` — thay doi gi? commit hay discard?
- [ ] Review `apps/dashboard/src/api.ts` — thay doi gi? commit hay discard?
- [ ] Review cac file untracked:
  - [ ] `.planning/RUNBOOK_VNLP_50_PLATES.md` — commit vao planning
  - [ ] `BUG_REPORT.md` — commit hoac chuyen vao planning
  - [ ] `apps/dashboard/vite.config.ts` — can thiet? commit neu co
  - [ ] `thayhoi.md` — xac dinh noi dung, commit hoac xoa
- [ ] Commit gon: `chore: commit pending work-in-progress files`

### F.2 Baseline evaluation report
- [ ] Xac dinh: co du thoi gian chay benchmark model that khong?
  - Neu CO: chay detector + OCR tren test split, ghi metrics vao report v0.2
  - Neu CHUA: cap nhat report v0.1 voi timeline cu the khi nao chay
- [ ] Cap nhat `.artifacts/BASELINE_EVALUATION_REPORT.md` voi trang thai moi nhat
- [ ] Commit: `docs: update baseline evaluation status`

---

## THU TU THUC HIEN DE XUAT

```
Buoc 1 (lam truoc):  F.1  — Don dep uncommitted (15 phut)
Buoc 2:              A    — Fix datetime.utcnow (30-45 phut)
Buoc 3:              B    — Unit tests barrier + normalize (30-45 phut)
Buoc 4:              C    — Cau hinh mypy (20-30 phut)
  --- seeded branch on dinh ---
Buoc 5:              D    — Tests pretrained branch (45-60 phut)
  --- pretrained branch on dinh ---
Buoc 6:              E    — Integration test matrix (60 phut)
Buoc 7 (lam cuoi):   F.2  — Baseline eval update (15-20 phut)
```

**Tong uoc luong**: 4-5 gio lam viec tap trung.

---

## TIEU CHI HOAN TAT TOAN BO

- [ ] `datetime.utcnow` = 0 instances trong toan repo backend
- [ ] `pytest` pass 100% tren ca 3 nhanh (seeded, pretrained, integration)
- [ ] `mypy` hoac `pyright` chay duoc va khong co loi critical
- [ ] `tsc --noEmit` pass tren dashboard
- [ ] Khong con uncommitted changes tren nhanh hien tai
- [ ] Integration test matrix v1 co ket qua ghi nhan day du
- [ ] Baseline evaluation report duoc cap nhat (du la ghi nhan "chua chay")
- [ ] San sang chuyen sang Phase 3 (Ops Hardening) cua Integration Roadmap
