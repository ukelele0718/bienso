# RUNBOOK - feat/pretrained-lpr-import-flow

Runbook nhanh cho nhanh pretrained (uu tien code-heavy, runtime-light).

---

## 1) Muc tieu runbook

Kiem tra nhanh cac API/dashboard phan pretrained ma khong can train model that.

Bao gom:
- tao infer job mocked,
- tao import job mocked + items,
- list jobs,
- xem detail job,
- xem summary counts.

---

## 2) Setup moi truong nhanh

Tu workspace root:

```powershell
cd G:/TTMT/datn
docker compose up -d postgres backend
```

Neu backend local:

```powershell
cd G:/TTMT/datn/apps/backend
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
python scripts/run_migrations.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 3) API smoke test pretrained

## 3.1 Create infer job

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/pretrained/infer" -ContentType "application/json" -Body '{"model_version":"mock-v1","source":"demo://frame-001.jpg","threshold":0.5}'
```

## 3.2 Create import job

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/pretrained/import" -ContentType "application/json" -Body '{"model_version":"mock-v1","source":"demo://batch-001","items":[{"plate_text":"51G12345","confidence":0.9,"vehicle_type":"motorbike"},{"plate_text":"99X99999","confidence":0.78,"vehicle_type":"car"}]}'
```

## 3.3 List jobs

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pretrained/jobs?page=1&page_size=20"
```

## 3.4 Summary counts

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pretrained/jobs/summary"
```

## 3.5 Detail by job id

```powershell
$jobs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pretrained/jobs?page=1&page_size=1"
$id = $jobs.items[0].id
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/pretrained/jobs/$id"
```

---

## 4) Dashboard check

```powershell
cd G:/TTMT/datn/apps/dashboard
npm install
npm run dev
```

Mo dashboard, kiem tra section `Pretrained Import`:
- tao infer/import job bang button,
- bang job history cap nhat,
- click row mo detail drawer,
- drawer hien items.

---

## 5) Test nhanh unit

```powershell
cd G:/TTMT/datn/apps/backend
python -m pytest tests/test_pretrained_unit.py -q
```

---

## 6) Troubleshooting nhanh

- 404 `pretrained_job_not_found`:
  - kiem tra `job_id` co ton tai.
- migration chua co bang pretrained:
  - chay lai `run_migrations.py` (bao gom `004_pretrained_jobs.sql`).
- dashboard khong thay data:
  - refresh section,
  - check `VITE_API_BASE_URL`.
