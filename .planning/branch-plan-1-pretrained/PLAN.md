# PLAN - feat/pretrained-lpr-import-flow (PRIORITY 1)

**Uu tien**: Cao nhat (lam truoc)  
**Muc tieu**: Tao khung pretrained/import flow hoan chinh (mockable), chinh sua nhieu file, KHONG can train hay chay runtime dai.

---

## 1) Muc tieu ky thuat

- Co API contract day du cho pretrained inference/import.
- Co service layer mockable + stub.
- Co CRUD/DB schema cho import job & detection batch (chua can model that).
- Co dashboard view de quan ly import job + status.
- Co test nhanh (unit/mocked) de validate contract.

---

## 2) Pham vi (in-scope)

- API endpoints:
  - `POST /api/v1/pretrained/infer`
  - `POST /api/v1/pretrained/import`
  - `GET /api/v1/pretrained/jobs`
  - `GET /api/v1/pretrained/jobs/{id}`
- Schema Pydantic + TypeScript types.
- Job status lifecycle: `queued -> running -> success|failed`.
- Database tables (migration):
  - `pretrained_jobs`
  - `pretrained_detections` (hoac `pretrained_import_items`)
- Dashboard page: list job + detail + retry button (UI only).

---

## 3) Out-of-scope (de sau)

- Train model that.
- Chay inference thuc te bang GPU.
- Upload file lon / multi-part storage.

---

## 4) Work Breakdown (code-heavy)

### 4.1 Backend schema + models
- [ ] Them model `PretrainedJob`.
- [ ] Them model `PretrainedDetection`.
- [ ] Them enums status/type.
- [ ] Cap nhat `schemas.py` + `api-types.ts` tuong ung.

### 4.2 Backend services (mockable)
- [ ] `services/pretrained_inference.py` (stub)
- [ ] `services/pretrained_import.py` (adapter stub)
- [ ] unit tests cho services (mock)

### 4.3 CRUD layer
- [ ] Them CRUD create/list/get job
- [ ] Them CRUD insert detections (batch)
- [ ] Them summary endpoint (job counts)

### 4.4 API routes
- [ ] `POST /pretrained/infer` (return job + mock result)
- [ ] `POST /pretrained/import` (create job + items)
- [ ] `GET /pretrained/jobs` (pagination)
- [ ] `GET /pretrained/jobs/{id}`

### 4.5 Dashboard
- [ ] Page/Section “Pretrained Import”
- [ ] Form submit mock job
- [ ] Table job history + badge status
- [ ] Detail drawer (job meta + items)

### 4.6 Docs + Planning
- [ ] Update `API_CONTRACT.md`
- [ ] Update `DB_SCHEMA.md`
- [ ] Update branch runbook

---

## 5) Tieu chi hoan thanh

- [ ] Mo rong 25+ file (backend + dashboard + docs).
- [ ] Lint/typecheck pass.
- [ ] API contract & types dong bo.
- [ ] UI co the demo (mock) khong can backend long-running.

---

## 6) Thu tu uu tien task

1. Schema + migration
2. CRUD + services (stub)
3. API routes
4. Dashboard UI
5. Docs + test
