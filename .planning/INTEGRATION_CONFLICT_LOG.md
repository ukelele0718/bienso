# INTEGRATION CONFLICT LOG

**Branch**: `feat/integration-seeded-pretrained`  
**Base date**: 2026-04-10  
**Owner**: integration track  
**Purpose**: Track all merge/rebase conflicts and resolution decisions between seeded and pretrained flows.

---

## 1) Usage Guide

Mỗi khi có conflict trong quá trình merge/rebase/cherry-pick:
1. Tạo 1 entry mới trong bảng bên dưới.
2. Ghi rõ file, loại conflict, root cause.
3. Mô tả quyết định resolve và lý do.
4. Link commit đã fix.
5. Đánh dấu trạng thái verify.

> Rule: không đóng conflict nếu chưa có verify evidence (test, lint, contract check).

---

## 2) Conflict Register

| ID | Date | Area | Files | Conflict Type | Root Cause | Resolution Decision | Commit | Verify Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CF-001 | 2026-04-10 | setup | _n/a_ | template-init | Create initial tracking template | Baseline document created | f58b532 | DONE | Initialized before merge rehearsal |
| CF-002 | 2026-04-10 | backend-core | `apps/backend/app/main.py`, `apps/backend/app/schemas.py` | content | Seeded error-contract + sort aliases overlapped with pretrained endpoints/schemas | Kept union model: retained seeded `ApiErrorOut` + account sort aliases and added pretrained contracts/routes in same module | `merge-rehearsal local` | DONE | Verified by quick matrix pass |
| CF-003 | 2026-04-10 | frontend-core | `apps/dashboard/src/api-types.ts`, `apps/dashboard/src/api.ts`, `apps/dashboard/src/main.tsx` | content | Seeded dashboard enhancements and pretrained drawer/apis edited same regions | Merged both feature sets: seeded account/import/verify UX + pretrained job APIs/types/drawer support | `merge-rehearsal local` | DONE | No conflict markers left, tests green |
| CF-004 | 2026-04-10 | planning-docs | `.planning/2026-03-29-vnlp-seeded-backend-dashboard/*`, `.planning/branch-plan-*/PLAN.md` | add/add | Parallel planning files introduced in both branches | Resolved using integration-branch versions to avoid doc churn during rehearsal | `merge-rehearsal local` | DONE | Can revisit final doc harmonization later |
| CF-005 | 2026-04-10 | test-matrix | `apps/backend/tests/test_pretrained_contract.py` | coverage-gap | Integration checklist lacked explicit pretrained contract assertion | Added integration contract test for `/api/v1/pretrained/jobs/summary` | `14ea664` | DONE | Included in 11-pass quick matrix |
| CF-006 | 2026-04-10 | backend-db-compat | `apps/backend/app/crud.py` | runtime/test failure | SQLite test DB does not support PostgreSQL `to_char` used in traffic aggregation | Added dialect-aware bucket expression: `strftime` for SQLite, `to_char` for PostgreSQL | pending commit | DONE | Expanded smoke matrix now passes 12/12 |

---

## 3) Frequent Conflict Patterns (to update)

| Pattern | Symptom | Prevention | Owner |
| --- | --- | --- | --- |
| Route overlap | static route bi dynamic route nuot (`/summary` vs `/{id}`) | Dat static route truoc dynamic route | backend |
| Schema drift | frontend type khong match Pydantic | Bat buoc contract test + typed sync checklist | backend+frontend |
| Model/migration mismatch | code dung table/column chua migrate | verify migration order + schema docs | backend |

---

## 4) Resolution Checklist (per conflict)

- [ ] Conflict reproduced and understood
- [ ] Root cause documented
- [ ] Resolution implemented with minimal scope
- [ ] Lint/typecheck pass
- [ ] Relevant tests pass
- [ ] Contract compatibility verified
- [ ] Log updated with commit hash

---

## 5) Sign-off

| Date | Reviewer | Decision | Evidence |
| --- | --- | --- | --- |
| _pending_ | _pending_ | _pending_ | _pending_ |
