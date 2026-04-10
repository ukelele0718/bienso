# PLAN - feat/vnlp-seeded-backend-dashboard (PRIORITY 2)

**Uu tien**: Thu 2 (lam sau nhanh pretrained skeleton)  
**Muc tieu**: Hardening + refactor + UX polish cho seeded flow, uu tien sua nhieu code/file nhung tranh runtime dai.

---

## 1) Muc tieu ky thuat

- Tang do ben vung seeded backend va dashboard.
- Chuan hoa contracts/errors/types de de bao tri.
- Tinh gon code va tach module nghiep vu ro rang.
- Tang chat luong test nhanh (unit/contract), han che phu thuoc e2e nang.

---

## 2) Pham vi (in-scope)

- Refactor backend domain logic:
  - barrier decision,
  - account state transitions,
  - import batch summary.
- Chuan hoa API errors + response contracts.
- Dashboard componentization:
  - import summary,
  - verify queue,
  - account list filters.
- Test nhanh:
  - unit + contract snapshots.

---

## 3) Out-of-scope (de sau)

- Chay soak/load test dai.
- Chay docker integration day du lien tuc.
- Chuyen sang production deploy.

---

## 4) Work Breakdown (code-heavy)

### 4.1 Backend refactor
- [x] Tach module `barrier_rules.py` / `account_state.py`
- [x] Tach response mappers cho Event/Barrier/Account
- [x] Chuan hoa naming va typed aliases
- [x] Giam duplicate logic trong CRUD

### 4.2 API contracts
- [x] Them error schema thong nhat (`code`, `message`, `details`)
- [x] Dong bo Pydantic models voi frontend types
- [x] Add examples cho endpoint chinh

### 4.3 Dashboard polishing
- [x] Tach component cho Import Summary section
- [x] Tach component cho Verify Queue section
- [x] Bo sung empty/loading/error states
- [x] Bo sung filter + sort UX cho account list

### 4.4 Test & docs
- [ ] Unit tests cho normalize + barrier rules
- [x] Contract tests cho API responses chinh
- [x] Cap nhat docs runbook + test plan seeded

---

## 5) Tieu chi hoan thanh

- [x] Chinh sua 20+ file (backend + dashboard + test + docs).
- [x] Lint/typecheck pass.
- [x] Contract backend/frontend khong lech.
- [x] Seeded flow van pass sau refactor.

---

## 6) Thu tu uu tien task

1. Backend refactor core
2. API contract/error standard
3. Dashboard componentization + UX polish
4. Tests/docs
