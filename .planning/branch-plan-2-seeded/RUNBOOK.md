# RUNBOOK - Branch `feat/vnlp-seeded-backend-dashboard` (Priority 2)

Muc tieu runbook nay: verify nhanh cac thay doi hardening/refactor/UX o Priority 2 ma khong can chay workflow nang.

---

## 1) Scope verify

- Backend refactor:
  - barrier rules tach module
  - response mappers
- API contract:
  - error schema thong nhat (`code`, `message`, `details`)
  - account list sort/filter contract
- Dashboard UX:
  - account list sort + filter
  - import summary component
  - verify queue component
  - empty/loading/error states

---

## 2) Quick local run

```powershell
cd G:/TTMT/datn
docker compose up -d postgres backend
cd apps/dashboard
npm run dev
```

---

## 3) API smoke checks

### 3.1 Error contract

```powershell
curl "http://localhost:8000/api/v1/accounts/NOT_FOUND_PLATE"
```

Ky vong:
```json
{
  "code": "account_not_found",
  "message": "account not found",
  "details": null
}
```

### 3.2 Account list sort/filter contract

```powershell
curl "http://localhost:8000/api/v1/accounts?page=1&page_size=10&registration_status=registered&sort_by=balance_vnd&sort_order=desc"
```

Ky vong co field:
- `items`
- `total`
- `page`
- `page_size`
- `sort_by`
- `sort_order`

---

## 4) Dashboard smoke checks

1. Vao section Account List
2. Filter theo status
3. Sort by = Balance / Plate / Created
4. Sort order = Asc/Desc
5. Verify list update dung
6. Kiem tra Import Summary section render dung
7. Kiem tra Verification Queue section render dung

---

## 5) Regression checks

```powershell
cd G:/TTMT/datn/apps/backend
pytest -q
```

Neu can check seeded flow full (dai hon):

```powershell
cd G:/TTMT/datn
python scripts/test_seeded_flow.py --base-url http://localhost:8000
```

---

## 6) Done criteria for Priority 2 batch

- API contract khong lech backend/frontend.
- Error response thong nhat.
- Account list UX co sort/filter ro rang.
- Dashboard components Import/Verify tach rieng va reuse duoc.
