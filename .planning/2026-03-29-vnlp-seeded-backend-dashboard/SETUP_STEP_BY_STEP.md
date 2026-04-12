# HUONG DAN SETUP TUNG BUOC (FROM ZERO TO RUN)

Tai lieu nay huong dan chi tiet tu dau den cuoi:
- cai Docker Desktop
- khoi dong database
- cai backend dependencies
- chay migration
- lay data VNLP va tao file test 50 xe
- import seed vao DB
- chay backend + dashboard
- chay full test seeded flow

Ap dung cho workspace:
`G:/TTMT/datn`

---

## 0) Tong quan nhanh

Sau khi lam xong, ban se co:
- PostgreSQL chay bang Docker
- Backend API chay o `http://localhost:8000`
- Dashboard chay o `http://localhost:5173` (hoac cong Vite in ra)
- Seeded flow test pass

---

## 1) Dieu kien tien quyet

Can co:
- Windows 10/11
- Python 3.11+
- Node.js 18+ + npm
- Docker Desktop

Kiem tra nhanh trong PowerShell:

```powershell
python --version
node --version
npm --version
docker --version
docker compose version
```

Neu lenh `docker` chua nhan:
1. Mo Docker Desktop
2. Cho Docker startup xong
3. Dong/mo lai PowerShell

---

## 2) Cai Docker Desktop (neu chua co)

1. Tai Docker Desktop:
   - https://www.docker.com/products/docker-desktop/
2. Cai dat theo wizard mac dinh
3. Restart may neu duoc yeu cau
4. Mo Docker Desktop va cho trang thai `Engine running`

Kiem tra lai:

```powershell
docker --version
docker compose version
```

---

## 3) Di chuyen vao project

```powershell
cd G:/TTMT/datn
```

---

## 4) Khoi dong PostgreSQL bang Docker

Project da co `docker-compose.yml`.

Chay:

```powershell
docker compose up -d postgres
```

Kiem tra container:

```powershell
docker compose ps
```

Ky vong service `postgres` o trang thai `running`.

Thong tin DB mac dinh:
- host: `localhost`
- port: `5432`
- db: `vehicle_lpr`
- user: `postgres`
- pass: `postgres`

---

## 5) Cai backend dependencies

```powershell
cd G:/TTMT/datn/apps/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
pip install pytest httpx
```

---

## 6) Set bien moi truong backend

Trong terminal backend (sau khi active venv):

```powershell
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
```

---

## 7) Chay migration

```powershell
python G:/TTMT/datn/apps/backend/scripts/run_migrations.py
```

Ky vong co dong nhu:
- `Applied 001_init.sql`
- `Applied 002_barrier_and_registration.sql`
- `Applied 003_seed_provenance_columns.sql`

---

## 8) Lay data VNLP o dau + dung vao viec gi

Nguon data ban dau:
- Danh sach VNLP hai dong xe may:
  - `G:/TTMT/datn/data/external/vnlp/VNLP_detection/detection/list_two_rows_label_xe_may.txt`
- Huong dan format ten file:
  - `G:/TTMT/datn/data/external/vnlp/VNLP_detection/detection/VNLP_readme`

Theo readme, ten file co dang:
`x_x_x_<PLATE>_<left>_<top>_<width>_<height>.jpg`

Plate nam o thanh phan thu 4 (`<PLATE>`).

---

## 9) Tao file test 50 xe tu VNLP

Chay lenh nay o workspace root:

```powershell
python -c "from pathlib import Path; import csv,re; src=Path(r'G:/TTMT/datn/data/external/vnlp/VNLP_detection/detection/list_two_rows_label_xe_may.txt'); out=Path(r'G:/TTMT/datn/data/processed/seed_test_50_plates.csv'); lines=[l.strip() for l in src.read_text(encoding='utf-8',errors='ignore').splitlines() if l.strip()]; seen=set(); rows=[]; \
for line in lines:\
 name=Path(line).name; stem=name.rsplit('.',1)[0]; parts=stem.split('_');\
 if len(parts)<8: continue;\
 plate_raw=parts[3]; plate_norm=re.sub(r'[^A-Za-z0-9]','',plate_raw).upper();\
 if len(plate_norm)<6 or plate_norm in seen: continue;\
 seen.add(plate_norm); rows.append({'plate_text':plate_norm,'source':'vnlp_two_rows_xe_may','seed_group':'test_50_from_list_two_rows','vehicle_type':'motorbike','note':f'sample_from:{name}'});\
 if len(rows)>=50: break;\
out.parent.mkdir(parents=True, exist_ok=True);\
with out.open('w', newline='', encoding='utf-8') as f:\
 w=csv.DictWriter(f, fieldnames=['plate_text','source','seed_group','vehicle_type','note']); w.writeheader(); w.writerows(rows);\
print(f'Wrote {len(rows)} rows to {out}')"
```

File ket qua:
- `G:/TTMT/datn/data/processed/seed_test_50_plates.csv`

---

## 10) Import seed vao DB

Script da ho tro `--csv`.

```powershell
cd G:/TTMT/datn
python scripts/import_seed_plates.py --csv "G:/TTMT/datn/data/processed/seed_test_50_plates.csv"
```

Theo doi output:
- `Imported new`
- `Promoted reg`
- `Skipped`
- `Invalid`
- `Import Batch`

---

## 11) Khoi dong backend

### Cach A (khuyen nghi): dung Docker

```powershell
cd G:/TTMT/datn
docker compose up -d --build backend
```

Kiem tra log:

```powershell
docker compose logs backend --tail=100
```

Ky vong co:
- `Application startup complete`
- `Uvicorn running on http://0.0.0.0:8000`

Kiem tra health:

```powershell
curl http://localhost:8000/health
```

---

## 12) Khoi dong dashboard

Mo terminal moi:

```powershell
cd G:/TTMT/datn/apps/dashboard
npm install
npm run dev
```

Mo URL Vite in ra (thuong `http://localhost:5173`).

Neu can set API base URL:
- tao `apps/dashboard/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 13) Chay full seeded flow test

```powershell
cd G:/TTMT/datn
python scripts/test_seeded_flow.py --base-url http://localhost:8000
```

Ky vong cuoi:
- `[OK] All tests passed!`

---

## 14) Cach chay nhanh 1 lenh (da dong goi)

Da co script one-command:
`G:/TTMT/datn/scripts/run_seeded_regression.ps1`

Chay:

```powershell
cd G:/TTMT/datn
powershell -ExecutionPolicy Bypass -File "G:/TTMT/datn/scripts/run_seeded_regression.ps1" -UseDockerBackend
```

Script se tu dong:
1. Start postgres
2. Chay migration
3. Reset deterministic test fixture
4. Start backend
5. Cho health ready
6. Chay seeded flow regression

---

## 15) Kiem tra Import Summary tren dashboard

Sau khi import xong:
1. Mo dashboard
2. Tim section `Import Summary`
3. Bam `Refresh Import Data`
4. Kiem tra:
   - cards: total/imported/skipped/invalid
   - bang recent batches co batch moi nhat

Co the doi chieu bang API:

```powershell
curl "http://localhost:8000/api/v1/import-batches?limit=10"
curl "http://localhost:8000/api/v1/import-batches/summary"
```

---

## 16) Troubleshooting nhanh

## 16.1 Loi `Cannot connect to localhost:8000`

- Kiem tra backend log:

```powershell
docker compose logs backend --tail=200
```

- Kiem tra health:

```powershell
curl http://localhost:8000/health
```

## 16.2 Loi `ModuleNotFoundError: No module named 'app'` trong container

- Dam bao backend command co `PYTHONPATH=/app` (da co trong compose hien tai)
- Rebuild lai backend:

```powershell
docker compose up -d --build backend
```

## 16.3 Loi build context do file cache pytest

- Da co `.dockerignore` chan cache, neu van gap thi xoa tay:

```powershell
Remove-Item -Force "G:/TTMT/datn/apps/backend/pytest-cache-files-*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "G:/TTMT/datn/apps/backend/.pytest_cache" -ErrorAction SilentlyContinue
```

## 16.4 Test fail do khong co plate registered

- Reset deterministic state:

```powershell
python G:/TTMT/datn/scripts/reset_seeded_test_state.py
```

- Hoac mark thu cong qua API:

```powershell
$resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/accounts?registration_status=temporary_registered&page=1&page_size=1"
$plate = $resp.items[0].plate_text
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/accounts/$plate/mark-registered"
```

---

## 17) Lenh shutdown

Dung he thong:

```powershell
cd G:/TTMT/datn
docker compose down
```

Neu muon xoa volume DB (can than, se mat data):

```powershell
docker compose down -v
```

---

## 18) Tai lieu lien quan

- Plan: `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/IMPLEMENTATION_PLAN.md`
- PRD: `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/PRD.md`
- Runbook E2E: `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/RUN_FULL_END_TO_END.md`
- Bao cao chi tiet: `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/EXECUTION_DETAILED_REPORT.md`
