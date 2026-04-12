# TEST PLAN - Priority 2 (Seeded Hardening/Refactor)

## 1) Unit tests

- [x] test_barrier_unit.py:
  - registered in/out -> open
  - temporary out -> hold + verify
  - unknown in -> auto temporary + open
- [ ] mapper tests:
  - Event mapper tra dung structure
  - Barrier mapper tra dung fields
  - Account mapper tra dung fields

## 2) Contract tests

- [x] Error contract test:
  - 404 account -> `ApiErrorOut`
- [x] Account list contract test:
  - response co `sort_by`, `sort_order`
  - sort/filter params duoc nhan dung

## 3) Dashboard behavior checks

- [ ] Account list filter by status
- [ ] Account list sort by created_at/balance/plate
- [ ] Sort asc/desc update list
- [ ] Import Summary section render empty/non-empty
- [ ] Verify Queue section render empty/non-empty

## 4) Integration sanity

- [x] API `/api/v1/accounts` voi sort/filter khong loi
- [x] API error schema thong nhat tren endpoint chinh

## 5) Regression

- [x] pytest pass local
- [ ] seeded flow script pass (optional when time allows)

---

## Test results (fill during execution)

| Test case | Status | Notes |
| --- | --- | --- |
| Error contract | PASS | `test_api_error_contract.py` |
| Account sort/filter contract | PASS | `test_accounts_contract.py` validates `sort_by/sort_order` and ordering |
| Barrier rules quick unit | PASS | `test_barrier_unit.py` |
| Quick suite (seeded + contract) | PASS | `7 passed, 6 warnings` via `python -m pytest ...` |
| Dashboard sort/filter UX | PENDING | Manual check |
