# Phase 04: Dashboard Browser Testing + Fix

**Ưu tiên**: 🟡 Cao — nhiều tính năng đánh dấu ❓ trong báo cáo, cần verify thực tế
**Trạng thái**: ⬜ Pending
**Ước tính**: ~3 giờ

---

## Bối cảnh

Báo cáo mục 3.3.2 liệt kê trạng thái từng tính năng dashboard:
- ✅ Realtime events list — đã verify
- ⚠ Realtime stats — hiển thị được, chưa test kỹ số liệu
- ❓ Accounts list — chưa test kỹ
- ❓ Account detail + giao dịch — chưa test kỹ
- ❓ Verify queue — chưa test kỹ
- ❓ Traffic stats — chưa test kỹ
- ❓ Import summary — chưa test kỹ

Dashboard source: `apps/dashboard/src/` — 6 files, 1,205 dòng TypeScript/React.

---

## Test Plan

### Chuẩn bị
1. Start backend: `cd apps/backend && uvicorn app.main:app --port 8000`
2. Start dashboard: `cd apps/dashboard && npm run dev`
3. Seed data: chạy E2E demo trước để có events trong DB

### Test Cases

#### TC-01: Realtime Stats Cards
- [ ] Mở dashboard → 6 metric cards hiển thị đúng
- [ ] Total In, Total Out, OCR Rate khớp với `/api/v1/stats/realtime`
- [ ] Accounts count khớp với `/api/v1/accounts/summary`
- [ ] Refresh → số liệu update

#### TC-02: Events List
- [ ] Bảng events hiển thị ≥1 event
- [ ] Mỗi event có: plate, direction, vehicle_type, timestamp
- [ ] Search by plate hoạt động
- [ ] Filter by time range hoạt động
- [ ] Filter by direction (in/out) hoạt động

#### TC-03: Accounts List
- [ ] Danh sách accounts hiển thị đúng
- [ ] Pagination hoạt động (Previous/Next)
- [ ] Search by plate hoạt động
- [ ] Sort by balance/created_at hoạt động
- [ ] Hiển thị đúng: plate, balance, registration_status, created_at

#### TC-04: Account Detail
- [ ] Click vào account → hiển thị chi tiết
- [ ] Lịch sử giao dịch (transactions) hiển thị
- [ ] Balance đúng = init - charges
- [ ] Transaction types: init_balance, event_charge

#### TC-05: Verify Queue
- [ ] Nếu có barrier HOLD → hiển thị trong queue
- [ ] Click Verify → barrier chuyển OPEN
- [ ] Queue cập nhật sau verify
- [ ] Nếu không có barrier HOLD → queue trống, hiển thị "No items"

#### TC-06: Traffic Stats
- [ ] Hiển thị thống kê theo giờ/ngày
- [ ] Số liệu khớp với `/api/v1/stats/traffic`
- [ ] Group by hour vs day hoạt động

#### TC-07: Import Summary
- [ ] Hiển thị batch import statistics (nếu có data)
- [ ] Summary: total, imported, skipped, invalid
- [ ] Refresh hoạt động

---

## Fix Protocol

Với mỗi bug phát hiện:
1. Ghi log: vấn đề + screenshot (nếu có)
2. Fix trực tiếp trong code
3. Verify lại sau fix
4. Ghi kết quả vào `test_plans_and_reports/test5-dashboard-browser-log.txt`

---

## Files có thể cần sửa

| File | Lý do |
|------|-------|
| `apps/dashboard/src/main.tsx` | Fix UI bugs, data display issues |
| `apps/dashboard/src/api.ts` | Fix API call params, error handling |
| `apps/dashboard/src/components/VerifyQueueSection.tsx` | Fix verify flow |
| `apps/dashboard/src/components/ImportSummarySection.tsx` | Fix import display |
| `apps/backend/app/main.py` | Fix API response nếu frontend nhận sai |

---

## Tiêu chí hoàn thành

- [ ] Tất cả 7 test cases đều PASS
- [ ] Không còn tính năng đánh dấu ❓ trong báo cáo
- [ ] Kết quả test ghi vào `test_plans_and_reports/test5-dashboard-browser-log.txt`
- [ ] Báo cáo mục 3.3.2 update trạng thái ✅ hoặc ⚠ (kèm lý do cụ thể)
