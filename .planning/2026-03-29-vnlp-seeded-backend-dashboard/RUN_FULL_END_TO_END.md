# RUNBOOK FULL E2E - VNLP Seeded Backend Dashboard

Tai lieu nay huong dan chay full he thong tu dau den cuoi cho mode seeded:

`seed CSV -> import DB -> backend API -> dashboard -> test seeded flow -> verify ket qua`

---

## 0) Muc tieu

Sau khi lam xong runbook nay, ban co the:
- tao/migrate DB day du (co `import_batches`)
- import seed plates vao bang `accounts`
- chay backend API
- chay dashboard frontend
- chay full test seeded flow
- doi chieu ket qua voi checklist trong `IMPLEMENTATION_PLAN.md`

---

## 1) Dieu kien tien quyet

## 1.1 Cong cu can co

- Python 3.11+ (khuyen nghi 3.11/3.12)
- Node.js 18+ va npm
- PostgreSQL 14+ (hoac Docker Desktop neu dung container)
- Git

Kiem tra nhanh:

```bash
python --version
node --version
npm --version
```

Neu dung Postgres local:

```bash
psql --version
```

Neu dung Docker:

```bash
docker --version
docker compose version
```

---

## 1.2 Cau truc thu muc (workspace)

Workspace goc:

`G:\TTMT\datn`

Thu muc lien quan:
- Backend: `apps/backend`
- Dashboard: `apps/dashboard`
- Scripts: `scripts`
- Planning docs: `.planning/2026-03-29-vnlp-seeded-backend-dashboard`

---

## 2) Chuan bi Database

Ban co 2 cach: **A (Docker)** hoac **B (Postgres local)**.

## 2.A Cach A - Dung Docker (de nhat)

Tai workspace root:

```bash
cd G:/TTMT/datn
docker compose up -d postgres
```

DB se o:
- host: `localhost`
- port: `5432`
- db: `vehicle_lpr`
- user: `postgres`
- pass: `postgres`

---

## 2.B Cach B - Dung Postgres local

Dang nhap psql va tao DB:

```sql
CREATE DATABASE vehicle_lpr;
```

Dam bao user/pass/host/port phu hop voi URL backend.

---

## 3) Tao virtualenv va cai dependency backend

```bash
cd G:/TTMT/datn/apps/backend
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Cai dependency:

```bash
pip install -U pip
pip install -r requirements.txt
pip install pytest httpx
```

---

## 4) Cau hinh bien moi truong backend

Backend doc DB URL tu bien:
- `APP_DATABASE_URL`

Gia tri mac dinh dang la:

`postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr`

Neu muon set ro rang trong PowerShell:

```powershell
$env:APP_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
```

---

## 5) Chay migration (bao gom migration 003)

Tu `apps/backend`:

```bash
python scripts/run_migrations.py
```

Ky vong thanh cong:
- khong bao loi ket noi
- khong bao loi schema
- tao/day du cac bang:
  - `accounts`, `transactions`, `vehicle_events`, `plate_reads`, `barrier_actions`
  - `import_batches`
- cot provenance trong `accounts`:
  - `source`, `seed_group`, `imported_at`, `import_batch_id`

---

## 6) Import seed CSV vao DB

Tu workspace root (`G:/TTMT/datn`) hoac bat ky, mien script truy cap duoc file:

```bash
python scripts/import_seed_plates.py
```

Script se:
- doc `data/processed/registered_plates_seed.csv`
- tao account moi `registration_status=registered`
- gan `balance_vnd=100000`
- tao `transaction(type='init')`
- ghi provenance (`source`, `seed_group`, `imported_at`, `import_batch_id`)
- tao/cap nhat `import_batches`

Output can xem:
- `Imported`
- `Skipped`
- `Invalid`
- `Import Batch`

Note: script idempotent muc MVP (import lai se skip plate da ton tai).

---

## 7) Chay backend API

Tu `apps/backend`:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Kiem tra health:

```bash
curl http://localhost:8000/health
```

Ky vong:

```json
{"status":"ok","time":"..."}
```

---

## 8) Chay dashboard frontend

Mo terminal moi:

```bash
cd G:/TTMT/datn/apps/dashboard
npm install
npm run dev
```

Neu can chi dinh API base URL:

- Tao file `.env` trong `apps/dashboard`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Mo URL local do Vite in ra (thuong la `http://localhost:5173`).

---

## 9) Chay full seeded flow test

Tu workspace root hoac `scripts`:

```bash
python scripts/test_seeded_flow.py --base-url http://localhost:8000
```

Verbose:

```bash
python scripts/test_seeded_flow.py --base-url http://localhost:8000 --verbose
```

Ky vong:
- tat ca test case pass
- gom cac nhanh:
  - registered + in -> open
  - registered + out -> open
  - unknown + in -> temporary_registered + open
  - temporary_registered + out -> hold
  - verify hold -> open

---

## 10) Smoke test API thu cong (khuyen nghi)

## 10.1 Summary accounts

```bash
curl http://localhost:8000/api/v1/accounts/summary
```

## 10.2 List accounts (search/filter/page)

```bash
curl "http://localhost:8000/api/v1/accounts?page=1&page_size=10"
curl "http://localhost:8000/api/v1/accounts?plate=29A"
curl "http://localhost:8000/api/v1/accounts?registration_status=registered"
```

## 10.3 Import batches

```bash
curl "http://localhost:8000/api/v1/import-batches?limit=10"
curl "http://localhost:8000/api/v1/import-batches/summary"
```

## 10.4 Barrier verify

```bash
curl "http://localhost:8000/api/v1/barrier-actions?plate=30B99999"
curl -X POST "http://localhost:8000/api/v1/barrier-actions/verify?plate=30B99999&actor=guard_01"
```

---

## 11) Checklist doi chieu voi Phase 8

Trong `IMPLEMENTATION_PLAN.md`, dam bao da tick:
- `[x] can nhac them source`
- `[x] can nhac them seed_group`
- `[x] can nhac them imported_at`
- `[x] can nhac bang import_batches`
- `[x] can nhac dashboard import summary`

---

## 12) Troubleshooting nhanh

## 12.0 Known pitfalls + fix (tu qua trinh chay that)

### Pitfall A - Backend container crash ngay khi start: `ModuleNotFoundError: No module named 'app'`
Nguyen nhan:
- command trong `docker-compose.yml` chay migration/uvicorn nhung chua set `PYTHONPATH=/app`.

Fix:
- dung command backend nhu sau:

```bash
/bin/sh -c "PYTHONPATH=/app python scripts/run_migrations.py && PYTHONPATH=/app uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### Pitfall B - Docker build fail do file cache pytest trong context
Trieu chung:
- loi kieu `Access is denied` voi file `pytest-cache-files-*`.

Fix:
- tao `apps/backend/.dockerignore` bo qua cache:
  - `.pytest_cache/`
  - `pytest-cache-files-*`
- xoa cache cu roi build lai:

```powershell
Remove-Item -Force "G:\TTMT\datn\apps\backend\pytest-cache-files-*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "G:\TTMT\datn\apps\backend\.pytest_cache" -ErrorAction SilentlyContinue
docker compose build --no-cache backend
```

### Pitfall C - Test script bi fail ket noi du backend da healthy
Trieu chung:
- `Server disconnected without sending a response` trong `httpx`.

Nguyen nhan thuong gap:
- `httpx` bi anh huong boi proxy env tren may local.

Fix:
- tao client voi `trust_env=False` trong `scripts/test_seeded_flow.py`.

### Pitfall D - Test `registered_in/out` fail do khong co account `registered`
Trieu chung:
- setup bao `No registered plate found in DB for registered-flow tests`.

Fix nhanh:
- mark 1 plate tam thanh `registered` qua API:

```powershell
$resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/accounts?registration_status=temporary_registered&page=1&page_size=1"
$plate = $resp.items[0].plate_text
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/accounts/$plate/mark-registered"
```

### Pitfall E - 500 khi tao event do UUID khong map voi schema response
Trieu chung:
- `EventOut` validation fail vi `id/camera_id` dang UUID, schema can string.

Fix:
- ep kieu `str()` cho `id`, `camera_id` khi map response `EventOut` trong `apps/backend/app/main.py`.

### Pitfall F - 1 test fail do collision state (`test_car_vehicle_type`)
Nguyen nhan:
- plate cua scenario bo sung trung voi plate da duoc mark `registered`.

Fix:
- trong test script, cho `test_car_vehicle_type` dung unknown plate random moi lan chay.

## 12.1 Loi "database vehicle_lpr does not exist"

- Tao DB `vehicle_lpr` truoc (neu Postgres local)
- hoac chay `docker compose up -d postgres`
- kiem tra lai `APP_DATABASE_URL`

## 12.2 Loi "docker is not recognized"

- cai Docker Desktop
- bat lai terminal sau khi cai
- neu khong dung Docker, chuyen sang Postgres local

## 12.3 Loi "pytest not found"

Trong venv backend:

```bash
pip install pytest
```

hoac:

```bash
python -m pytest
```

## 12.4 Dashboard khong goi duoc API

- check backend dang run cang `8000`
- check `VITE_API_BASE_URL`
- mo browser devtools > Network de xem request loi

---

## 13) Trinh tu chay nhanh de demo

Neu can demo nhanh trong 1 lan chay:

1. Start Postgres
2. Chay migration
3. Import seed CSV
4. Start backend
5. Start dashboard
6. Chay `test_seeded_flow.py`
7. Mo dashboard, verify cac man:
   - Summary cards
   - Account list/search/filter
   - Verification queue
   - Import summary

---

## 13.1) CI local quick run (giong regression pipeline)

Tu workspace root:

```bash
# 1) Bat postgres
cd G:/TTMT/datn
docker compose up -d postgres

# 2) Chay migration (backend env)
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
python "G:/TTMT/datn/apps/backend/scripts/run_migrations.py"

# 3) Reset deterministic fixture
python "G:/TTMT/datn/scripts/reset_seeded_test_state.py"

# 4) Chay backend
# Option A: docker
# docker compose up -d backend
# Option B: local
# cd apps/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5) Chay seeded regression
python "G:/TTMT/datn/scripts/test_seeded_flow.py" --base-url http://localhost:8000
```

Ky vong:
- [OK] Backend healthy
- [OK] All tests passed (6/6)

## 14) Lenh tong hop (copy nhanh)

## Terminal 1 - Postgres

```bash
cd G:/TTMT/datn
docker compose up -d postgres
```

## Terminal 2 - Backend setup + migrate + run

```bash
cd G:/TTMT/datn/apps/backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install pytest httpx
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
python scripts/run_migrations.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Terminal 3 - Import seed + test

```bash
cd G:/TTMT/datn
python scripts/import_seed_plates.py
python scripts/test_seeded_flow.py --base-url http://localhost:8000 --verbose
```

## Terminal 4 - Dashboard

```bash
cd G:/TTMT/datn/apps/dashboard
npm install
npm run dev
```

---

## 15) Ghi chu

- Runbook nay uu tien seeded mode MVP de backend/dashboard khong bi block boi AI runtime.
- Khi merge ve mode production, can ra soat lai API contract va luong OCR/detector.
