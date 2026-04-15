# Plan: Xử lý tất cả tồn đọng ĐATN

**Ngày tạo**: 14/04/2026
**Nguồn**: Phân tích báo cáo `BÁO CÁO ĐỊNH KỲ TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP 20260414.docx` + codebase
**Mục tiêu**: Hoàn thành tất cả items còn tồn đọng để chuẩn bị bảo vệ ĐATN

---

## Tổng quan hiện trạng

| Hạng mục | Trạng thái | Chi tiết |
|----------|-----------|---------|
| AI Engine pipeline | ⚠ 80% | detect + track + OCR hoạt động, thiếu snapshot + post-processing |
| Backend API | ✅ 100% | 18 endpoints, 56/56 tests pass |
| Dashboard | ⚠ 60% | Events list OK, các tính năng khác chưa test browser |
| E2E flow | ⚠ 70% | Demo hoạt động, thiếu snapshot, FPS thấp |
| Báo cáo | ⚠ 50% | .md + .docx có, chưa viết lý thuyết, thiếu phân công |
| Slide bảo vệ | ❌ 0% | Chưa bắt đầu |

---

## Phases

| Phase | Tên | Ưu tiên | Trạng thái | File |
|-------|-----|---------|-----------|------|
| 01 | OCR Post-processing (regex + char mapping) | 🔴 Cao | ⬜ Pending | [phase-01](phase-01-ocr-post-processing.md) |
| 02 | Lưu snapshot crop biển số | 🔴 Cao | ⬜ Pending | [phase-02](phase-02-snapshot-saving.md) |
| 03 | Full OCR Evaluation (3,731+ ảnh) | 🔴 Cao | ⬜ Pending | [phase-03](phase-03-full-ocr-eval.md) |
| 04 | Dashboard browser testing + fix | 🟡 Cao | ⬜ Pending | [phase-04](phase-04-dashboard-testing.md) |
| 05 | Screenshot dashboard cho báo cáo | 🟡 TB | ⬜ Pending | [phase-05](phase-05-dashboard-screenshots.md) |
| 06 | Viết phần lý thuyết (Ch.1) | 🟡 TB | ⬜ Pending | [phase-06](phase-06-chapter1-theory.md) |
| 07 | Hoàn thiện báo cáo chính thức | 🟡 TB | ⬜ Pending | [phase-07](phase-07-finalize-report.md) |
| 08 | Slide bảo vệ | 🟠 TB | ⬜ Pending | [phase-08](phase-08-defense-slides.md) |
| 09 | Nice-to-have improvements | 🟢 Thấp | ⬜ Pending | [phase-09](phase-09-nice-to-have.md) |

---

## Dependency Graph

```
Phase 01 (OCR post-process) ──┐
                               ├──→ Phase 03 (Full OCR eval) ──→ Phase 07 (Báo cáo)
Phase 02 (Snapshot saving) ───┘                                        │
                                                                       ↓
Phase 04 (Dashboard test) ──→ Phase 05 (Screenshots) ──────────→ Phase 07
                                                                       │
Phase 06 (Lý thuyết Ch.1) ────────────────────────────────────→ Phase 07
                                                                       │
                                                                       ↓
                                                                Phase 08 (Slide)
Phase 09 (Nice-to-have) ── độc lập, làm nếu còn thời gian
```

---

## Ước tính thời gian tổng

| Phase | Ước tính |
|-------|---------|
| 01 - OCR post-processing | ~2 giờ |
| 02 - Snapshot saving | ~2 giờ |
| 03 - Full OCR eval | ~1 giờ |
| 04 - Dashboard test + fix | ~3 giờ |
| 05 - Dashboard screenshots | ~30 phút |
| 06 - Lý thuyết Ch.1 | ~5 giờ |
| 07 - Hoàn thiện báo cáo | ~3 giờ |
| 08 - Slide bảo vệ | ~4 giờ |
| 09 - Nice-to-have | ~5 giờ |
| **Tổng** | **~25.5 giờ** |
