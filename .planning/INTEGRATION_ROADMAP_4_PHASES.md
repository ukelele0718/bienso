# INTEGRATION ROADMAP 4 PHASES

**Project**: VNLP Seeded Backend Dashboard + Pretrained Import Flow  
**Scope**: Ke hoach dai hoi de dua 3 nhanh ve trang thai on dinh, tich hop co kiem soat, va san sang merge/release.  
**Ngay tao**: 2026-04-10

---

## 0) Nguyen tac van hanh

1. **Khong merge som**: on dinh tung nhanh truoc, roi moi hop nhat.
2. **Contract-first**: backend/frontend types va error schema phai dong bo.
3. **Runtime-light truoc**: uu tien code/test/docs nhanh, de script/docker/train nang cho khung gio du.
4. **Evidence-driven**: moi gate deu co file minh chung (test logs, checklist, report).

---

## PHASE 1 - Branch Stabilization (Week 1)

### Muc tieu
- Khoa chat luong rieng cho tung nhanh.
- Khong thay doi lon tren `main`.

### 1.1 `feat/pretrained-lpr-import-flow`

#### Cong viec
- [ ] Bo sung test persistence cho:
  - `pretrained_jobs`
  - `pretrained_detections`
  - summary counts
- [ ] Bo sung API contract tests:
  - infer/import/list/summary/detail
- [ ] Bo sung dashboard smoke checklist cho drawer + item list.
- [ ] Chuan hoa runbook pretrained (commands + expected output).

#### Done criteria
- [ ] Test nhanh pass on dinh (>= 2 lan lien tiep).
- [ ] Contract docs + DB schema docs cap nhat day du.
- [ ] Co `PROGRESS_EVIDENCE.md` ban cap nhat moi nhat.

### 1.2 `feat/vnlp-seeded-backend-dashboard`

#### Cong viec
- [ ] Xu ly warning timezone (`datetime.utcnow` -> aware datetime).
- [ ] Tang them 1-2 contract tests endpoint seeded quan trong.
- [ ] Chot TEST_PLAN voi ket qua run moi nhat.
- [ ] Bo sung runbook seeded cho sort/filter + verify queue + import summary.

#### Done criteria
- [ ] Quick suite pass on dinh.
- [ ] Khong con mismatch backend/frontend contract.
- [ ] Plan Priority 2 duoc tick hoan tat.

### 1.3 `main`

#### Cong viec
- [ ] Chi nhan thay doi safe (utilities/docs/conventions).
- [ ] Khong dua business flow lon vao `main` o phase nay.

#### Done criteria
- [ ] Main clean, de rebase/merge.

---

## PHASE 2 - Controlled Integration Branch (Week 2-3)

### Muc tieu
- Tich hop seeded + pretrained trong 1 nhanh kiem soat.

### Cong viec
- [ ] Tao nhanh: `feat/integration-seeded-pretrained`.
- [ ] Merge lan 1: seeded baseline.
- [ ] Merge lan 2: pretrained flow.
- [ ] Giai quyet conflicts theo checklist:
  - routes ordering
  - schemas/types naming
  - CRUD/model compatibility
  - dashboard sections ownership
- [ ] Chay test matrix v1.

### Test matrix v1
- [ ] Backend unit tests
- [ ] API contract tests
- [ ] Dashboard smoke test
- [ ] Regression script lightweight

### Done criteria
- [ ] Integration branch build/test pass.
- [ ] Co `INTEGRATION_CONFLICT_LOG.md`.
- [ ] Co danh sach risky points + rollback points.

---

## PHASE 3 - Ops Hardening & Reporting (Week 3-4)

### Muc tieu
- Chuan hoa van hanh de demo/bao cao/ban giao.

### Cong viec
- [ ] One-command runbooks:
  - backend quick run
  - dashboard quick run
  - quick test run
- [ ] Chuan hoa bo tai lieu bao cao:
  - executive summary 1 trang
  - slide-ready bullets
  - plan alignment report
  - progress evidence
- [ ] Tao report tong hop readiness:
  - `INTEGRATION_READINESS_REPORT.md`

### Done criteria
- [ ] Moi command demo co expected output.
- [ ] Bo tai lieu du de trinh bay voi GV/PM.
- [ ] Team co the tai lap trong 1 may moi voi setup toi thieu.

---

## PHASE 4 - Merge to Main with Quality Gates (Week 5+)

### Muc tieu
- Dua ket qua tich hop ve `main` an toan.

### Merge gates (bat buoc)
- [ ] Test matrix pass 2-3 lan lien tiep.
- [ ] Lint/typecheck pass.
- [ ] Contract backend/frontend khong lech.
- [ ] Runbook/docs cap nhat day du.
- [ ] Rollback plan ro rang (commit range co the revert).

### Quy trinh
- [ ] Mo PR integration -> main voi summary ro rang.
- [ ] Review checklist truoc merge.
- [ ] Merge khong force, khong bo qua hooks.
- [ ] Post-merge sanity check ngay.

### Done criteria
- [ ] Main o trang thai release-ready.
- [ ] Co changelog + ket qua test kem theo.

---

## Timeline de xuat

- **Week 1**: Phase 1 (stabilize tung nhanh)
- **Week 2-3**: Phase 2 (integration branch)
- **Week 3-4**: Phase 3 (ops hardening + reporting)
- **Week 5+**: Phase 4 (merge gates + release)

---

## RACI goi y (co the dieu chinh)

- **Owner ky thuat**: ban (chinh)
- **Support code/test**: agent workflow
- **Reviewer**: GV/PM hoac peer
- **Gate keeper merge**: owner + reviewer

---

## Risk register ngan

1. **Schema drift** giua 2 nhanh  
   -> Giam thieu: contract tests + typed aliases.

2. **Route conflicts** (static vs dynamic routes)  
   -> Giam thieu: checklist route ordering + test endpoint matrix.

3. **Regression UI** khi tach component  
   -> Giam thieu: smoke tests + deterministic fixtures.

4. **False completion claim**  
   -> Giam thieu: evidence files + explicit gate checklist.

---

## Next action ngay lap tuc (48h)

- [ ] Tao `feat/integration-seeded-pretrained`.
- [ ] Run test matrix v1 tren tung nhanh truoc merge.
- [ ] Tao `INTEGRATION_CONFLICT_LOG.md` template.
- [ ] Cap nhat `INTEGRATION_READINESS_REPORT.md` lan 1.
