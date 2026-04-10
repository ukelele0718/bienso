# INTEGRATION MANUAL DASHBOARD SMOKE CHECKLIST

**Branch**: `feat/integration-seeded-pretrained`  
**Date**: 2026-04-10  
**Owner**: Integration QA pass  
**Scope**: Manual smoke checklist cho ca seeded + pretrained sections tren dashboard da merge.

---

## 1) Pre-conditions

- [ ] Backend start OK (`uvicorn app.main:app --port 8000`)
- [ ] Dashboard start OK (`npm run dev`)
- [ ] API base URL trỏ đúng backend integration branch
- [ ] DB migration da apply day du (`004_pretrained_jobs.sql` + seeded migrations)

---

## 2) Seeded section smoke

### 2.1 KPI + realtime
- [ ] The Total In / Total Out / OCR Success cards render
- [ ] Traffic summary render non-crash
- [ ] Refresh button update data khong error

### 2.2 Account list
- [ ] Filter by plate hoạt động
- [ ] Filter by registration status hoạt động
- [ ] Sort by `created_at` hoạt động
- [ ] Sort by `balance_vnd` hoạt động
- [ ] Sort by `plate_text` hoạt động
- [ ] Sort order `asc/desc` hoạt động
- [ ] Pagination Previous/Next hoạt động

### 2.3 Verify queue
- [ ] Queue render khi co item
- [ ] Empty state render khi khong co item
- [ ] Verify action khong crash UI

### 2.4 Import summary (seeded)
- [ ] Summary cards render
- [ ] Batches table render
- [ ] Refresh import data hoạt động

---

## 3) Pretrained section smoke

### 3.1 Pretrained import panel
- [ ] Form source/model/threshold render đúng
- [ ] `Create Infer Job` success path hoạt động
- [ ] `Create Import Job` success path hoạt động
- [ ] Jobs table update sau create

### 3.2 Pretrained detail drawer
- [ ] Click row mở drawer
- [ ] Drawer hiển thị job metadata
- [ ] Drawer hiển thị item list
- [ ] Close drawer hoạt động

### 3.3 Pretrained summary/API consistency
- [ ] `/api/v1/pretrained/jobs/summary` reflect UI counters
- [ ] Job detail API match drawer fields

---

## 4) Cross-section regression

- [ ] Seeded section vẫn hoạt động sau thao tác pretrained
- [ ] Pretrained section vẫn hoạt động sau thao tác seeded
- [ ] Không có JS runtime error ở console
- [ ] Không có API 500 trong network tab (happy path)

---

## 5) Result log

| Item | Status | Notes |
| --- | --- | --- |
| Seeded smoke | PENDING | Chua run manual trong session nay |
| Pretrained smoke | PENDING | Chua run manual trong session nay |
| Cross regression | PENDING | Chua run manual trong session nay |

---

## 6) Recommendation input for readiness v3

- Manual smoke completion status: **PENDING**  
- Blocking issues found: **NONE YET** (pending execution)  
- Require human/manual run confirmation before main-merge Go decision: **YES**
