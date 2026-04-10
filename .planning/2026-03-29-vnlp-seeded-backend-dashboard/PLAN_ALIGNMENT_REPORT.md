# BAO CAO SO SANH DO KHÓP KẾ HOẠCH

**Doi tuong so sanh**:
- Ke hoach goc: `G:/TTMT/datn/.planning/2026-03-29` (sprint train nhanh 30 phut)
- Ke hoach hien tai: `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard` (seeded backend + dashboard)

**Ngay bao cao**: 2026-04-05

---

## 1) Tong quan khac biet muc tieu

### Ke hoach goc (2026-03-29)
- Trong tam: **train nhanh detector trong ~30 phut** (Kaggle)
- Deliverables chinh: `best.pt`, `results.csv`, sample predictions
- Pham vi: model/AI, quick baseline

### Ke hoach hien tai (seeded backend)
- Trong tam: **backend + dashboard seeded mode** (khong can OCR/model)
- Deliverables chinh: import seed -> API -> dashboard -> test seeded flow
- Pham vi: nghiep vu tai chinh + barrier + UI/ops

**Ket luan**: 2 ke hoach khac scope. Ke hoach hien tai la **nhanh hon ve he thong**, ke hoach goc la **nhanh hon ve model**. Chung song song, khong thay the nhau.

---

## 2) Muc do khop theo nhom yeu cau

| Nhom yeu cau | Ke hoach goc (train nhanh) | Ke hoach hien tai (seeded backend) | Do khop |
| --- | --- | --- | --- |
| AI/model training | Co (scope chinh) | Khong (out-of-scope) | Thap |
| Import seed plates | Khong | Co (scope chinh) | Thap |
| Backend API + business rules | Khong | Co (scope chinh) | Thap |
| Dashboard demo | Khong | Co (scope chinh) | Thap |
| Timebox 30 phut | Co | Khong ap dung | Thap |
| Integration readiness | Mot phan (sau khi co model) | Truc tiep (khong can model) | Trung binh |

---

## 3) So sanh cac tai lieu chinh

### 3.1 PRD
- PRD goc: tap trung **model detector baseline**
- PRD seeded: tap trung **seeded mode backend + dashboard**

=> Khong trung nhau ve scope. Hien tai dang thuc thi dung PRD seeded, **khong dung PRD goc**.

### 3.2 Implementation Plan
- Plan goc: 3 phase (subset -> train -> validate)
- Plan seeded: 8 phase (seed -> import -> backend -> dashboard -> QA -> provenance)

=> 2 plan khac nhau. Hien tai da hoan thanh 100% checklist trong plan seeded.

---

## 4) Tinh khop theo deliverables

### Ke hoach goc (train nhanh)
Deliverables mong muon:
- `best.pt`
- `results.csv`
- sample predictions
- run note

**Trang thai hien tai**: **chua thuc hien** (khong thuoc scope seeded).

### Ke hoach seeded backend
Deliverables mong muon:
- seed import pipeline
- backend API seeded mode
- dashboard ops
- seeded flow test pass
- runbook + CI regression

**Trang thai hien tai**: **da hoan thanh** (theo `IMPLEMENTATION_PLAN.md` seeded).

---

## 5) Danh gia do khop (summary)

- Do khop giua **ke hoach goc** va **ke hoach hien tai**: **Thap (~20–30%)**
- Ly do: 2 ke hoach tap trung vao 2 tranche khac nhau cua du an.
- Khong co mau thuan: seeded plan la nhanh de demo he thong, goc plan la nhanh de co model tam.

---

## 6) Gap dong/khuyen nghi

### Neu muon dong bo 2 ke hoach
- Tao 1 muc “Bridge” trong plan goc:
  - sau khi co `best.pt`, gan vao pipeline detect/crop va goi backend seeded events.
- Bo sung checklist “Integration test with model” trong seeded plan (Phase 9).

### De xuat thuc te
- Giu ke hoach seeded (da xong) la **baseline system**.
- Neu can model tạm, quay lai thuc thi ke hoach goc (train 30 phut), sau do chi can 1 buoc gan model vao pipeline va thu event.

---

## 7) Ket luan

- Hien tai **khong lech huong** so voi plan seeded mode.
- Nhung **khac scope** voi plan train nhanh 30 phut.
- De hop nhat, can mot “phase noi” nho de gan model tam vao he thong seeded (neu can).

---

## 8) Tai lieu tham chieu

- `G:/TTMT/datn/.planning/2026-03-29/PRD.md`
- `G:/TTMT/datn/.planning/2026-03-29/IMPLEMENTATION_PLAN.md`
- `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/PRD.md`
- `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/IMPLEMENTATION_PLAN.md`
- `G:/TTMT/datn/.planning/2026-03-29-vnlp-seeded-backend-dashboard/EXECUTION_DETAILED_REPORT.md`
