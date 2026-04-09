# RUNBOOK - Branch `feat/pretrained-lpr-import-flow`

Runbook nay danh cho luong pretrained import (uu tien code-heavy, runtime-light).

---

## 1) Muc tieu runbook

- Verify API pretrained da hoat dong:
  - create infer job
  - create import job
  - list jobs
  - jobs summary
  - job detail (co items)
- Verify dashboard section `Pretrained Import` co:
  - tao job
  - list jobs
  - mo detail drawer

---

## 2) Prerequisite

- Backend da cai dependencies va migration da chay.
- Co DB local/Postgres docker.

Goi y env (PowerShell):

```powershell
$env:PYTHONPATH="G:/TTMT/datn/apps/backend"
$env:APP_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
```

---

## 3) Chay migration

```powershell
python "G:/TTMT/datn/apps/backend/scripts/run_migrations.py"
```

Dam bao migration `004_pretrained_jobs.sql` da apply.

---

## 4) Start backend

```powershell
cd G:/TTMT/datn/apps/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```powershell
curl http://localhost:8000/health
```

---

## 5) API smoke test (pretrained)

### 5.1 Create infer job

```powershell
curl -X POST "http://localhost:8000/api/v1/pretrained/infer" -H "Content-Type: application/json" -d "{\"model_version\":\"mock-v1\",\"source\":\"demo://frame-001.jpg\",\"threshold\":0.5}"
```

### 5.2 Create import job

```powershell
curl -X POST "http://localhost:8000/api/v1/pretrained/import" -H "Content-Type: application/json" -d "{\"model_version\":\"mock-v1\",\"source\":\"demo://batch-001\",\"items\":[{\"plate_text\":\"51G12345\",\"confidence\":0.9,\"vehicle_type\":\"motorbike\"},{\"plate_text\":\"99X99999\",\"confidence\":0.8,\"vehicle_type\":\"car\"}]}"
```

### 5.3 List jobs

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs?page=1&page_size=10"
```

### 5.4 Jobs summary

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs/summary"
```

### 5.5 Job detail

Lay `job_id` tu list, roi goi:

```powershell
curl "http://localhost:8000/api/v1/pretrained/jobs/<job_id>"
```

Ky vong: response co `items`.

---

## 6) Dashboard smoke

```powershell
cd G:/TTMT/datn/apps/dashboard
npm install
npm run dev
```

Tren UI:
1. Vao section `Pretrained Import (Mocked)`
2. Bam `Create Infer Job` / `Create Import Job`
3. Xac nhan table jobs update
4. Click row job -> mo detail drawer
5. Xac nhan drawer co job meta + item list

---

## 7) Troubleshooting nhanh

### 7.1 `/pretrained/jobs/summary` bi 404
- Kiem tra route order trong `app/main.py`:
  - route static `/pretrained/jobs/summary` phai dat TRUOC `/pretrained/jobs/{job_id}`.

### 7.2 Job detail khong co items
- Kiem tra `crud_pretrained.create_detections` co duoc goi trong import endpoint.
- Kiem tra migration 004 da apply.

### 7.3 Dashboard click row khong mo drawer
- Kiem tra `fetchPretrainedJob` va state `showPretrainedDrawer` trong `src/main.tsx`.

---

## 8) Done criteria cho branch runbook

- API pretrained smoke test pass.
- Jobs summary endpoint tra ve count dung format.
- Drawer hien job meta + items tren dashboard.
- Plan checklist Priority 1 gan hoan tat.
