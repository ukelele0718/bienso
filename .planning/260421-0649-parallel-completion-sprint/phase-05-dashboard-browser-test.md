# Phase 05: Dashboard Browser Testing + Runtime Fixes

**Ưu tiên**: 🔴 Critical
**Branch**: `fix/dashboard-runtime`
**Worktree**: WT-D (isolation)
**Ước tính**: 3-4 giờ

---

## Bối cảnh

Báo cáo đánh dấu 6/7 tính năng dashboard là "⚠ code review OK, chưa test browser". User nghi ngờ nhiều tính năng không chạy thực sự.

Code review trước đó (test5) đã fix 2 bugs:
- Pagination "1 - 0 of 0"
- Double-fetch stale page state

Nhưng **runtime bugs** chỉ phát hiện qua browser — cần test thủ công.

---

## Test Plan

### Chuẩn bị

1. Reset DB: `rm *.db` (giữ backup nếu cần)
2. Start backend: `cd apps/backend && PYTHONIOENCODING=utf-8 uvicorn app.main:app --port 8000 --reload`
3. Start dashboard: `cd apps/dashboard && npm run dev`
4. Seed data: chạy E2E demo 100 frames để có events
5. Mở browser: http://localhost:5173
6. Dev tools mở: Console + Network tabs

### Test Cases (7 features)

#### TC-01: Realtime Stats (cards trên đầu)
- [ ] 6 metric cards hiển thị: total_in, total_out, ocr_rate, accounts
- [ ] Số liệu khớp với `/api/v1/stats/realtime` (check Network tab)
- [ ] Refresh page → số liệu cập nhật
- [ ] Error states: backend down → có error message, không crash

#### TC-02: Events List
- [ ] Bảng hiển thị events với timestamp, plate, direction, vehicle_type
- [ ] **Snapshot thumbnail** hiển thị bên cạnh plate (feature mới từ Phase 02 cũ)
- [ ] Search by plate → filter đúng
- [ ] Filter by date range → filter đúng
- [ ] Filter by direction (in/out) → filter đúng
- [ ] Empty state (không có events) → không crash, hiển thị message

#### TC-03: Accounts List
- [ ] Bảng hiển thị accounts: plate, balance, status, created_at
- [ ] Pagination: Previous/Next hoạt động
- [ ] Search by plate → filter đúng
- [ ] Sort by balance/created_at → sort đúng
- [ ] Click account → navigate sang detail page

#### TC-04: Account Detail
- [ ] Hiển thị: plate, balance, status, transactions list
- [ ] Transactions: init, event_charge hiển thị đúng amount
- [ ] "Mark as registered" button → status thay đổi, verify queue cập nhật
- [ ] "Adjust balance" button → balance thay đổi

#### TC-05: Verify Queue
- [ ] Nếu có barrier HOLD → hiển thị trong queue với plate + reason
- [ ] Click "Verify" → barrier chuyển OPEN
- [ ] Queue refresh sau verify
- [ ] Empty state: không có barrier → "No items pending"

#### TC-06: Traffic Stats
- [ ] Hiển thị thống kê theo giờ/ngày (chart hoặc table)
- [ ] Switch group_by hour ↔ day → data thay đổi
- [ ] Empty data → không crash

#### TC-07: Import Summary
- [ ] Hiển thị batch import stats: total, imported, skipped, invalid
- [ ] Bảng batches history (nếu có)
- [ ] Empty state: "No imports yet"

---

## Fix Protocol

Với mỗi bug phát hiện:

1. **Ghi log**: `test_plans_and_reports/test11-dashboard-browser-bugs.md`
   - Vấn đề: gì
   - Reproduce: bước
   - Console error: paste
   - Network request: request/response
   - Expected vs Actual

2. **Fix trực tiếp** trong worktree
3. **Verify** lại sau fix
4. **Commit**: 1 bug = 1 commit, message rõ ràng

---

## Files có thể cần sửa

- `apps/dashboard/src/main.tsx` (most likely)
- `apps/dashboard/src/api.ts` (fetch logic)
- `apps/dashboard/src/api-types.ts` (type mismatch)
- `apps/dashboard/src/components/VerifyQueueSection.tsx`
- `apps/dashboard/src/components/ImportSummarySection.tsx`
- `apps/backend/app/main.py` (nếu API response sai format)
- `apps/backend/app/schemas.py` (nếu schema mismatch)

---

## Known Potential Issues (dự đoán trước)

Dựa trên code review (chưa verified):

1. **Snapshot URL 404**: backend mount `/static/snapshots` chỉ khi folder tồn tại. Nếu chạy tests mà chưa có ảnh → dashboard src broken image
2. **Empty array vs null**: Backend có thể trả `[]` hay `null` tùy endpoint → frontend phải handle cả 2
3. **Date format**: Python datetime ISO 8601 có thể có `Z` hoặc `+00:00` → JS Date parse khác nhau
4. **CORS preflight**: OPTIONS request có thể bị reject nếu endpoint mới thêm

---

## Tiêu chí thành công

- [ ] 7/7 test cases PASS
- [ ] 0 console errors trên tất cả pages
- [ ] 0 network errors (422, 500) khi click các buttons
- [ ] Report log đầy đủ tại `test_plans_and_reports/test11-dashboard-browser-bugs.md`

---

## Output

- Branch `fix/dashboard-runtime` với các bug fixes
- Test report chi tiết (liệt kê tất cả bugs phát hiện + fix)
- Nếu pass hết → merge về main
- Update báo cáo 2026-04-15 mục 3.3.2 với trạng thái ✅ cho từng tính năng
