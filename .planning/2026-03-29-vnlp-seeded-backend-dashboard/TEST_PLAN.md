# TEST_PLAN
## Ke hoach kiem thu chi tiet cho seeded mode (Unit -> API -> Integration -> UI)

**Du an**: VNLP seeded backend dashboard  
**Ngay cap nhat**: 2026-03-29  
**Muc tieu**: liet ke day du test cases cho luong import bien so, nghiep vu tai chinh, barrier action, dashboard, va event gia lap.

---

## 1) Pham vi kiem thu
- Script import seed plates
- Backend API (FastAPI + database)
- Rule nghiep vu so du `100000` / `-2000` / cho phep am
- Rule `registered / temporary_registered / unknown`
- Rule barrier `open / hold / verify`
- Dashboard UI (search, account, verify queue, stats)
- Typed quality gates (Python type hints + TypeScript strict)

---

## 2) Unit Test Cases

## 2.1 Unit test - Seed import logic
- [ ] Parse plate tu filename VNLP dung format.
- [ ] Normalize bien so upper-case dung.
- [ ] Bo separator va space dung.
- [ ] Dedupe plate trong cung seed batch dung.
- [ ] Sinh `registered_plates_seed.csv` dung schema.
- [ ] Summary `imported/skipped/invalid` tinh dung.

## 2.2 Unit test - Business Rule (so du)
- [ ] Import account moi tao dung balance `100000`.
- [ ] Account moi sinh `init transaction`.
- [ ] Event dau tien bi tru dung `2000`.
- [ ] Nhieu event lien tiep tru dung moi luot `2000`.
- [ ] So du duoc phep am.
- [ ] `balance_after_vnd` trong transaction khop account that.

## 2.3 Unit test - Barrier decision logic
- [ ] `registered + in` => `open`.
- [ ] `registered + out` => `open`.
- [ ] `temporary_registered + in` => `open`.
- [ ] `temporary_registered + out` => `hold`.
- [ ] `unknown + in` => `temporary_registered` + `open`.
- [ ] `needs_verification=true` khi `hold`.
- [ ] Verify thanh cong cap nhat `hold -> open`.

## 2.4 Unit test - CRUD / Query logic
- [ ] `create_event` tao du `vehicle_events` + `plate_reads`.
- [ ] `get_account` tra dung account seeded.
- [ ] `list_transactions` tra dung lich su.
- [ ] `list_barrier_actions_by_plate` tra dung lich su barrier.
- [ ] `verify_latest_hold` mo dung event can verify.

---

## 3) API Test Cases (HTTP level)

## 3.1 API - Event endpoints
- [ ] `POST /api/v1/events` tra 200/201 voi payload hop le.
- [ ] `POST /api/v1/events` tra `registered + in -> open`.
- [ ] `POST /api/v1/events` tra `registered + out -> open`.
- [ ] `POST /api/v1/events` tra `unknown + in -> temporary_registered`.
- [ ] `POST /api/v1/events` tra `temporary_registered + out -> hold`.
- [ ] `GET /api/v1/events` tra dung schema.
- [ ] `GET /api/v1/events` filter theo plate hoat dong dung.

## 3.2 API - Account/Transaction endpoints
- [ ] `GET /api/v1/accounts` tra danh sach account.
- [ ] `GET /api/v1/accounts` filter `registration_status` dung.
- [ ] `GET /api/v1/accounts/summary` tra dung tong hop.
- [ ] `GET /api/v1/accounts/{plate}` tra dung so du.
- [ ] `GET /api/v1/accounts/{plate}` tra 404 voi plate khong ton tai.
- [ ] `GET /api/v1/accounts/{plate}/transactions` tra dung lich su.

## 3.3 API - Barrier endpoints
- [ ] `GET /api/v1/barrier-actions?plate=...` tra dung lich su.
- [ ] `POST /api/v1/barrier-actions/verify` mo duoc hold hop le.
- [ ] `POST /api/v1/barrier-actions/verify` tra 404 khi khong tim thay hold.

## 3.4 API - Stats endpoints
- [ ] `GET /api/v1/stats/realtime` tra du fields.
- [ ] `GET /api/v1/stats/traffic` tra dung schema.
- [ ] `GET /api/v1/stats/ocr-success-rate` khong vo UI seeded mode.
- [ ] `GET /health` tra `status=ok`.

---

## 4) Database & Migration Test Cases

## 4.1 Migration
- [ ] Tao du bang can cho seeded mode.
- [ ] Check constraint `registration_status` dung.
- [ ] Check constraint `barrier_action` dung.
- [ ] Unique `accounts.plate_text` dung.

## 4.2 Integrity
- [ ] FK `plate_reads.event_id -> vehicle_events.id` dung.
- [ ] FK `transactions.account_id -> accounts.id` dung.
- [ ] FK `barrier_actions.event_id -> vehicle_events.id` dung.
- [ ] Event moi khong tao duplicate account cho same plate.

---

## 5) Integration Test Cases

## 5.1 Import + DB Integration
- [ ] Import seed CSV tao du accounts.
- [ ] Import lai khong tao duplicate accounts.
- [ ] Import lai khong tao duplicate `init transaction`.
- [ ] Summary import khop ket qua DB.

## 5.2 Event + Account Integration
- [ ] Plate da seed di `in` di dung nhanh `registered`.
- [ ] Plate da seed di `out` di dung nhanh `registered`.
- [ ] Plate chua seed di `in` tao `temporary_registered`.
- [ ] Plate tam di `out` tao `hold`.
- [ ] Verify xong mo barrier dung.

---

## 6) UI Test Cases (Dashboard)

## 6.1 UI - Tong quan
- [ ] Hien duoc KPI `total / registered / temporary / hold`.
- [ ] Bang activity hien dung cot nghiep vu.
- [ ] Loading / empty / error state dung.

## 6.2 UI - Search / Account page
- [ ] Search theo bien so hoat dong dung.
- [ ] Chi tiet account hien dung so du va registration status.
- [ ] Hien dung lich su transactions.
- [ ] Hien dung lich su events va barrier actions.

## 6.3 UI - Verify queue
- [ ] Danh sach hold queue hien dung.
- [ ] Nhan verify thi trang thai doi dung.
- [ ] Sau verify, barrier action cap nhat tren UI.

## 6.4 UI - Stats page
- [ ] Bieu do traffic hien dung du lieu.
- [ ] Filter thoi gian cap nhat dung.
- [ ] Metric OCR khong lam vo layout du khong phai KPI chinh.

---

## 7) End-to-End (E2E) Test Cases
- [ ] Import seed batch -> xem duoc tren dashboard.
- [ ] Registered plate `in` -> event / transaction / open barrier.
- [ ] Registered plate `out` -> event / transaction / open barrier.
- [ ] Unknown plate `in` -> tao temporary account / transaction / open barrier.
- [ ] Temporary plate `out` -> hold / verify queue / verify thanh cong.
- [ ] Search bien so va xem duoc full lich su sau cac kich ban tren.

---

## 8) Non-functional Test Cases

## 8.1 Reliability
- [ ] Import lon khong crash backend.
- [ ] Restart backend khong mat schema/data.

## 8.2 Security co ban
- [ ] Validate input CSV va API an toan.
- [ ] Khong lo stacktrace noi bo ra response production mode.

## 8.3 Performance
- [ ] Search account tren quy mo seed prototype van chap nhan duoc.
- [ ] Verify queue mo nhanh tren quy mo seed prototype.

---

## 9) Typed Quality Gate Test Cases

## 9.1 Python
- [ ] Script import moi co type annotations co ban.
- [ ] Backend type-check pass.

## 9.2 TypeScript
- [ ] `tsc --noEmit` pass.
- [ ] Khong dung `any` trong feature chinh.

---

## 10) Regression Checklist
- [ ] Re-run import tests.
- [ ] Re-run barrier rule tests.
- [ ] Re-run account API tests.
- [ ] Re-run dashboard smoke tests.
- [ ] Re-run typed checks.

---

## 11) Test Data Checklist
- [ ] Co seed CSV hop le.
- [ ] Co camera seed hop le cho FK.
- [ ] Co tap event gia lap cho 4 nhanh nghiep vu.
- [ ] Co plate khong ton tai de test unknown flow.
- [ ] Co du event de test balance am.

---

## 12) Tien do thuc thi test (Tracking)
- [ ] Hoan thanh Unit tests
- [ ] Hoan thanh API tests
- [ ] Hoan thanh Integration tests
- [ ] Hoan thanh UI tests
- [ ] Hoan thanh E2E tests
- [ ] Hoan thanh Non-functional tests
- [ ] Hoan thanh Typed quality gates

---

## 13) Merge note
File nay co chu dich giu ten va bo muc gan voi `.artifacts/TEST_PLAN.md`.

Khi merge ve `.artifacts`, giu:
- khung unit/API/integration/UI/E2E/non-functional
- bo sung seed import tests va seeded rule tests thanh mot execution track song song voi AI mode

