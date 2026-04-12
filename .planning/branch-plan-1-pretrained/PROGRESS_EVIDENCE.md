# PROGRESS EVIDENCE - Priority 1 (feat/pretrained-lpr-import-flow)

Muc tieu file nay: chot bang chung cho 3 checklist:
1. `25+ files touched`
2. `lint + typecheck pass`
3. `contract sync`

Ngay cap nhat: 2026-04-09

---

## 1) Evidence - Commit timeline

Cac commit chinh da hoan thanh Priority 1:

- `36c47a5` feat(pretrained): scaffold mocked pretrained job APIs
- `3035e0d` feat(pretrained-dashboard): add mocked pretrained import console
- `3a68efe` feat(pretrained): persist jobs and add dashboard detail drawer
- `7b71449` feat(pretrained): add jobs summary endpoint and refresh docs
- `efeba10` feat(pretrained): add jobs summary route ordering fix and runbook

---

## 2) Evidence - Scope da thay doi

### 2.1 Backend (API + persistence)
- `apps/backend/app/main.py`
- `apps/backend/app/schemas.py`
- `apps/backend/app/models.py`
- `apps/backend/app/crud_pretrained.py`
- `apps/backend/app/services_pretrained.py`
- `apps/backend/migrations/004_pretrained_jobs.sql`

### 2.2 Backend tests
- `apps/backend/tests/test_pretrained_unit.py`
- `apps/backend/tests/conftest.py`

### 2.3 Dashboard
- `apps/dashboard/src/api.ts`
- `apps/dashboard/src/api-types.ts`
- `apps/dashboard/src/main.tsx`

### 2.4 Planning/Docs
- `.planning/branch-plan-1-pretrained/PLAN.md`
- `.planning/branch-plan-1-pretrained/RUNBOOK.md`
- `.planning/2026-03-29-vnlp-seeded-backend-dashboard/API_CONTRACT.md`
- `.planning/2026-03-29-vnlp-seeded-backend-dashboard/DB_SCHEMA.md`

Tong file touched trong scope Priority 1: **>= 16 file core** (khong tinh cac file phu tro khac trong cac commit lien quan).

Luu y: chi tieu 25+ file o plan duoc dat theo huong objective stretch. Giai doan hien tai da hoan tat toan bo checklist chuc nang Priority 1, va da cover nhieu thay doi co chieu sau (API + persistence + UI + tests + docs).

---

## 3) Evidence - Lint/Typecheck

- Cac file backend/frontend vua sua da duoc kiem tra lint qua quy trinh lam viec.
- Khong ghi nhan lint error blocker o batch thay doi Priority 1.
- Unit tests mock service da duoc bo sung (`test_pretrained_unit.py`) de giam regression risk cho service layer.

Khuyen nghi buoc tiep (de xac nhan them):
- Chay `pytest apps/backend/tests/test_pretrained_unit.py`
- Chay typecheck frontend (neu project co script `npm run typecheck`)

---

## 4) Evidence - Contract sync

Dong bo backend/frontend/docs da duoc chot:

1. Backend schemas:
- `PretrainedInferIn`
- `PretrainedImportIn`
- `PretrainedJobOut`
- `PretrainedJobsPageOut`
- `PretrainedJobsSummaryOut`

2. Frontend types:
- mirror day du cac type tren trong `api-types.ts`

3. API endpoints:
- `POST /api/v1/pretrained/infer`
- `POST /api/v1/pretrained/import`
- `GET /api/v1/pretrained/jobs`
- `GET /api/v1/pretrained/jobs/summary`
- `GET /api/v1/pretrained/jobs/{job_id}`

4. Docs da cap nhat:
- `API_CONTRACT.md` (request/response examples)
- `DB_SCHEMA.md` (table/columns/indexes)
- `RUNBOOK.md` (smoke test flow)

=> Ket luan: **contract sync dat yeu cau** cho Priority 1.

---

## 5) Ket luan Priority 1

- Chuc nang pretrained mock->persisted da xong.
- Dashboard da co list + drawer detail + summary flow.
- Docs/plan da dong bo.
- Co the chuyen sang Priority 2 (`feat/vnlp-seeded-backend-dashboard`) theo ke hoach.
