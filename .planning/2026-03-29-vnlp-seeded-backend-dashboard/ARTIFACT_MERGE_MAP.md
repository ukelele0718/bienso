# ARTIFACT MERGE MAP
## Ban do merge tu planning folder nay ve `.artifacts`

**Muc tieu**: de sau nay co the merge `G:\TTMT\datn\.planning\2026-03-29-vnlp-seeded-backend-dashboard` vao `G:\TTMT\datn\.artifacts` ma khong phai viet lai tu dau.

---

## 1) Nguyen tac thiet ke
- Giu cung ten file voi `.artifacts` neu file do la tai lieu cot loi.
- Giu ket cau section gan voi `.artifacts`.
- Giu nguyen domain model:
  - events
  - accounts
  - transactions
  - barrier_actions
- Ghi ro phan nao la seeded-mode override.
- Khong dua path `.planning/...` vao logic cot loi neu khong can.

---

## 2) Map file 1:1

| Planning file | Target trong `.artifacts` | Chien luoc merge |
| --- | --- | --- |
| `PRD.md` | `.artifacts/PRD.md` | Merge section-level, giu seeded mode nhu mot implementation profile |
| `IMPLEMENTATION_PLAN.md` | `.artifacts/IMPLEMENTATION_PLAN.md` | Merge theo phase, bo sung backend-first path song song voi AI-first path |
| `API_CONTRACT.md` | `.artifacts/API_CONTRACT.md` | Merge endpoint-level, them account list/summary/barrier verify |
| `DB_SCHEMA.md` | `.artifacts/DB_SCHEMA.md` | Merge schema-level, uu tien schema khop codebase thuc te |
| `DASHBOARD_WIREFRAME.md` | `.artifacts/DASHBOARD_WIREFRAME.md` | Merge UX-level, them verify queue va account-first view |
| `TEST_PLAN.md` | `.artifacts/TEST_PLAN.md` | Merge test-suite-level, them seeded-mode tests thanh track rieng |
| `BASELINE_EVALUATION_REPORT.md` | `.artifacts/BASELINE_EVALUATION_REPORT.md` | Merge report-level, tach `AI baseline` va `seeded baseline` |

---

## 3) File khong can merge truc tiep 1:1

| Planning file | Ly do |
| --- | --- |
| `task.md` | Dung cho theo doi execution, khong phai artifact canonical |
| `ARTIFACT_MERGE_MAP.md` | Chi dung de huong dan merge, khong can dua vao `.artifacts` |

---

## 4) Chien luoc merge de xuat

### Cach 1 - Merge tung file
Dung khi:
- muon giu `.artifacts` gon
- muon xem tung thay doi ro rang

Thu tu merge:
1. `PRD.md`
2. `IMPLEMENTATION_PLAN.md`
3. `API_CONTRACT.md`
4. `DB_SCHEMA.md`
5. `TEST_PLAN.md`
6. `DASHBOARD_WIREFRAME.md`
7. `BASELINE_EVALUATION_REPORT.md`

### Cach 2 - Merge theo concept
Dung khi:
- muon giu AI-first va seeded-first cung ton tai trong `.artifacts`

Thu tu merge:
1. merge `seeded mode` vao PRD
2. merge backend-first path vao implementation plan
3. merge account/barrier APIs vao API contract
4. merge verify queue vao dashboard wireframe
5. merge seeded tests vao test plan

---

## 5) Nguyen tac conflict resolution
- Neu `.artifacts` va planning folder khac nhau, uu tien:
  1. su that cua codebase hien tai
  2. seeded mode la execution path de giam block
  3. giu architecture tong de sau nay quay lai AI mode duoc

- Khong merge seeded mode theo cach xoa bo AI mode.
- Nen merge theo cach:
  - "AI mode" = long-term target
  - "Seeded mode" = short-term backend-first MVP path

---

## 6) Dau hieu da san sang merge
- [ ] Rule `registered + out` da chot va da test
- [ ] Seed CSV contract da chot
- [ ] Import script da chay that
- [ ] API list/search/summary account da on
- [ ] Dashboard verify queue da co
- [ ] Test plan da du testcase seeded mode

---

## 7) Ket luan
Folder planning nay da duoc thiet ke de:
- giong `.artifacts` ve ten file
- giong `.artifacts` ve ket cau
- de merge lai ve sau ma it conflict nhat

No khong nham thay the `.artifacts` ngay lap tuc.
No nham bo sung mot execution path moi:
- `backend-first seeded mode`
- song song voi `AI-first original mode`

