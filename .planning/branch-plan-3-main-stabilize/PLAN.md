# PLAN - main stabilization (PRIORITY 3)

**Uu tien**: Thu 3 (lam sau cung)  
**Muc tieu**: Giu `main` on dinh, chi nhan thay doi an toan/co tinh tai su dung cao, han che runtime nang.

---

## 1) Muc tieu ky thuat

- Tao baseline on dinh cho cac branch feature rebase/merge sau nay.
- Dua utility/framework dung chung vao main mot cach co kiem soat.
- Tang chat luong docs/standards cho toan repo.

---

## 2) Pham vi (in-scope)

- Utility dung chung:
  - normalize helper,
  - typed error response model,
  - script/check tooling nhe.
- Docs chuan:
  - contributing mini guide,
  - coding/testing conventions,
  - branch policy.
- CI nhe:
  - lint/typecheck workflow co ban (khong chay job nang).

---

## 3) Out-of-scope (de sau)

- Merge toan bo seeded/pretrained flow vao main ngay.
- Chay training jobs / heavy docker suites.

---

## 4) Work Breakdown (code + governance)

### 4.1 Shared utilities
- [ ] Dua module normalize dung chung
- [ ] Dua error schema/model dung chung
- [ ] Them helper logging/co relation id

### 4.2 Minimal CI safeguards
- [ ] Workflow lint/typecheck nhanh
- [ ] Check formatting basic
- [ ] Fail-fast config

### 4.3 Project governance docs
- [ ] Add branch policy (when merge / when hold)
- [ ] Add definition of done per branch
- [ ] Add release checklist template

### 4.4 Optional safe cherry-picks
- [ ] Cherry-pick docs/tools an toan tu seeded branch
- [ ] Khong cherry-pick business flow lon

---

## 5) Tieu chi hoan thanh

- [ ] Chinh sua 8-15 file tren main (an toan, dung chung).
- [ ] Khong lam vo luong hien co.
- [ ] Main giu trang thai clean + de tich hop.

---

## 6) Thu tu uu tien task

1. Shared utilities
2. Minimal CI
3. Governance docs
4. Safe cherry-picks
