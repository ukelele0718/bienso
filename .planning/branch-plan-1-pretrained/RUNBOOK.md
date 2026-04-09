# RUNBOOK - feat/pretrained-lpr-import-flow

Runbook nay danh cho nhanh `feat/pretrained-lpr-import-flow` voi muc tieu code-heavy + runtime-light.

---

## 1) Muc tieu runbook

- Kiem tra duoc API pretrained flow ma khong can train model that.
- Verify duoc:
  - create infer job
  - create import job
  - list jobs
  - jobs summary
  - job detail + detection items

---

## 2) Dieu kien

- Backend app khoi dong duoc (`uvicorn` hoac docker backend)
- DB da migrate den `004_pretrained_jobs.sql`

---

## 3) Chay migration

```powershell
cd G:/TTMT/datn
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
python "G:/TTMT/datn/apps/backend/scripts/run_migrations.py"
```

---

## 4) Start backend (option docker)

```powershell
cd G:/TTMT/datn
docker compose up -d --build backend
```

Check health:

```powershell
curl http://localhost:8000/health
```

---

## 5) API smoke test pretrained flow

### 5.1 Create infer job

```powershell
curl -X POST "http://localhost:8000/api/v1/pretrained/infer" -H "Content-Type: application/json" -d "{\"model_version\":\"mock-v1\",\"source\":\"demo://frame-001.jpg\",\"threshold\":0.5}"
```

### 5.2 Create import job

```powershell
curl -X POST "http://localhost:8000/api/v1/pretrained/import" -H "Content-Type: application/json" -d "{\"model_version\":\"mock-v1\",\"source\":\"demo://batch-001\",\"items\":[{\"plate_text\":\"51G12345\",\"confidence\":0.91,\"vehicle_type\":\"motorbike\"},{\"plate_text\":\"99X99999\",\"confidence\":0.77,\"vehicle_type\":\"car\"}]}"
```

### 5.3 List jobs

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs?page=1&page_size=20"
```

### 5.4 Jobs summary

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs/summary"
```

### 5.5 Job detail (replace JOB_ID)

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs/JOB_ID"
```

---

## 6) Dashboard check

- Mo dashboard (`apps/dashboard`, `npm run dev`)
- Section `Pretrained Import`:
  - tao infer/import job
  - list jobs hien thi status
  - click row de xem drawer detail + items

---

## 7) Unit tests (mock service)

```powershell
cd G:/TTMT/datn/apps/backend
pytest -q tests/test_pretrained_unit.py
```

---

## 8) Done criteria

- API endpoints pretrained tra response typed dung contract
- DB luu duoc jobs + detections
- Dashboard hien thi list + drawer detail
- Unit tests mock service pass
