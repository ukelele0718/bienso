# TEST_PLAN.md - Seeded Mode Testing Plan

**Version**: 2.0  
**Ngày cập nhật**: 2026-03-29  
**Phạm vi**: Kiểm thử toàn diện cho VNLP Seeded Backend Dashboard  

---

## Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Unit Tests - Services](#2-unit-tests---services)
3. [Unit Tests - CRUD](#3-unit-tests---crud)
4. [Integration Tests - API Endpoints](#4-integration-tests---api-endpoints)
5. [Integration Tests - Import Scripts](#5-integration-tests---import-scripts)
6. [Database & Migration Tests](#6-database--migration-tests)
7. [End-to-End Tests - Business Flow](#7-end-to-end-tests---business-flow)
8. [Dashboard UI Tests](#8-dashboard-ui-tests)
9. [Performance Tests](#9-performance-tests)
10. [Security Tests](#10-security-tests)
11. [Typed Quality Gate Tests](#11-typed-quality-gate-tests)
12. [Test Data & Setup](#12-test-data--setup)
13. [Progress Tracking](#13-progress-tracking)

---

## 1. Tổng quan

### 1.1 Mục tiêu kiểm thử
- Đảm bảo logic nghiệp vụ barrier hoạt động đúng với tất cả scenarios
- Xác minh import seed data không tạo duplicate
- Kiểm tra các API endpoint trả về đúng format và data
- Đảm bảo dashboard hiển thị đúng dữ liệu
- Verify tính idempotent của import scripts

### 1.2 Môi trường kiểm thử
- Database: PostgreSQL 16 (Docker container: `vehicle_lpr_postgres`)
- Backend: Python 3.11 + FastAPI (port 8000)
- Mock Server: FastAPI serving images (port 8088)
- Dashboard: React + TypeScript + Vite (port 5173)
- Test Framework: pytest (backend), manual/Playwright (frontend)

### 1.3 Cách chạy tests

```bash
# Full stack start
docker-compose up -d

# Backend unit/integration tests
cd apps/backend
python -m pytest tests/ -v

# Seeded mode specific tests
python -m pytest tests/test_seeded_mode.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# API flow tests (requires running backend)
python scripts/test_seeded_flow.py --verbose

# Run specific flow test
python scripts/test_seeded_flow.py --only test_registered_in

# Dashboard type check
cd apps/dashboard
npm run typecheck
```

---

## 2. Unit Tests - Services

### 2.1 `decide_barrier()` - Barrier Decision Logic

**File**: `apps/backend/app/services.py`  
**Test file**: `apps/backend/tests/test_seeded_mode.py`

| ID | Test Case | Input | Expected Output | Status |
|----|-----------|-------|-----------------|--------|
| SVC-001 | Registered vehicle IN | `registration_status='registered'`, `direction='in'` | `barrier_action='open'`, `barrier_reason='registered_vehicle_in'`, `needs_verification=False` | [ ] |
| SVC-002 | Registered vehicle OUT | `registration_status='registered'`, `direction='out'` | `barrier_action='open'`, `barrier_reason='registered_vehicle_out'`, `needs_verification=False` | [ ] |
| SVC-003 | Temporary vehicle IN | `registration_status='temporary_registered'`, `direction='in'` | `barrier_action='open'`, `needs_verification=False` | [ ] |
| SVC-004 | Temporary vehicle OUT | `registration_status='temporary_registered'`, `direction='out'` | `barrier_action='hold'`, `needs_verification=True` | [ ] |
| SVC-005 | Unknown vehicle IN | `registration_status='unknown'`, `direction='in'` | `registration_status='temporary_registered'`, `barrier_action='open'` | [ ] |
| SVC-006 | Unknown vehicle OUT | `registration_status='unknown'`, `direction='out'` | `barrier_action='hold'` (default case) | [ ] |
| SVC-007 | Default fallback | Any unmatched combination | `barrier_action='hold'`, `needs_verification=True` | [ ] |

### 2.2 `BarrierDecision` Dataclass

| ID | Test Case | Expected | Status |
|----|-----------|----------|--------|
| SVC-010 | BarrierDecision is immutable | Cannot modify after creation (frozen=True) | [ ] |
| SVC-011 | All fields required | TypeError if missing any field | [ ] |

---

## 3. Unit Tests - CRUD

### 3.1 Account Operations

**File**: `apps/backend/app/crud.py`

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| CRUD-001 | `get_account()` - found | Existing plate_text | Returns Account object | [ ] |
| CRUD-002 | `get_account()` - not found | Non-existing plate_text | Raises `NotFoundError` | [ ] |
| CRUD-003 | `list_accounts()` - no filter | Empty params | Returns all accounts, paginated | [ ] |
| CRUD-004 | `list_accounts()` - filter by plate | `plate='29A'` | Returns accounts containing '29A' | [ ] |
| CRUD-005 | `list_accounts()` - filter by status | `registration_status='registered'` | Returns only registered accounts | [ ] |
| CRUD-006 | `list_accounts()` - pagination page 1 | `page=1, page_size=10` | Returns first 10 accounts | [ ] |
| CRUD-007 | `list_accounts()` - pagination page 2 | `page=2, page_size=10` | Returns accounts 11-20 | [ ] |
| CRUD-008 | `list_accounts()` - total count | DB has 100 accounts | Returns `total=100` | [ ] |
| CRUD-009 | `get_accounts_summary()` | DB has mixed statuses | Returns correct counts per status | [ ] |

### 3.2 Transaction Operations

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| CRUD-010 | `list_transactions()` - has txns | Valid account_id | Returns list sorted by created_at ASC | [ ] |
| CRUD-011 | `list_transactions()` - empty | New account | Returns empty list | [ ] |
| CRUD-012 | Transaction type='init' | After import | Transaction with amount=100000 | [ ] |
| CRUD-013 | Transaction type='event_charge' | After event | Transaction with amount=-2000 | [ ] |

### 3.3 Barrier Action Operations

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| CRUD-020 | `list_barrier_actions_by_plate()` | Plate with actions | Returns list of actions | [ ] |
| CRUD-021 | `verify_latest_hold()` - success | Plate has 'hold' action | Action updated to 'open', verified_by set | [ ] |
| CRUD-022 | `verify_latest_hold()` - not found | Plate has no actions | Raises `NotFoundError` | [ ] |
| CRUD-023 | `verify_latest_hold()` - already open | Plate's latest is 'open' | Returns action unchanged | [ ] |
| CRUD-024 | `verify_latest_hold()` - audit log | Verify success | AuditLog entry created | [ ] |

### 3.4 Event Creation

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| CRUD-030 | `create_event()` - new plate | Unknown plate_text | Creates new account with `temporary_registered` | [ ] |
| CRUD-031 | `create_event()` - new plate balance | Unknown plate_text | Account has `balance_vnd=100000` | [ ] |
| CRUD-032 | `create_event()` - new plate init txn | Unknown plate_text | Creates Transaction type='init' | [ ] |
| CRUD-033 | `create_event()` - existing plate | Known plate_text | Uses existing account, no new account | [ ] |
| CRUD-034 | `create_event()` - charge balance | Any valid event | `balance_vnd -= 2000` | [ ] |
| CRUD-035 | `create_event()` - event_charge txn | Any valid event | Creates Transaction type='event_charge' | [ ] |
| CRUD-036 | `create_event()` - creates vehicle_event | Valid payload | VehicleEvent record created | [ ] |
| CRUD-037 | `create_event()` - creates plate_read | Valid payload | PlateRead record created | [ ] |
| CRUD-038 | `create_event()` - creates barrier_action | Valid payload with plate | BarrierAction record created | [ ] |

---

## 4. Integration Tests - API Endpoints

### 4.1 Events API (`/api/v1/events`)

| ID | Test Case | Method | Endpoint | Request | Expected Response | Status |
|----|-----------|--------|----------|---------|-------------------|--------|
| API-001 | Create event - registered IN | POST | `/events` | `plate_text='29A12345', direction='in'` | 200, `barrier_action='open'` | [ ] |
| API-002 | Create event - registered OUT | POST | `/events` | `plate_text='29A12345', direction='out'` | 200, `barrier_action='open'` | [ ] |
| API-003 | Create event - unknown IN | POST | `/events` | `plate_text='99X99999', direction='in'` | 200, `registration_status='temporary_registered'` | [ ] |
| API-004 | Create event - temporary OUT | POST | `/events` | `plate_text='99X99999', direction='out'` | 200, `barrier_action='hold'` | [ ] |
| API-005 | Create event - missing camera_id | POST | `/events` | Missing required field | 422 Validation Error | [ ] |
| API-006 | Create event - invalid direction | POST | `/events` | `direction='invalid'` | 422 Validation Error | [ ] |
| API-007 | List events - no filter | GET | `/events` | - | 200, array of EventOut | [ ] |
| API-008 | List events - filter by plate | GET | `/events?plate=29A` | - | 200, filtered events | [ ] |
| API-009 | List events - filter by direction | GET | `/events?direction=in` | - | 200, only IN events | [ ] |
| API-010 | List events - filter by vehicle_type | GET | `/events?vehicle_type=motorbike` | - | 200, only motorbike events | [ ] |
| API-011 | List events - filter by time range | GET | `/events?from_time=...&to_time=...` | - | 200, events in range | [ ] |

### 4.2 Accounts API (`/api/v1/accounts`)

| ID | Test Case | Method | Endpoint | Request | Expected Response | Status |
|----|-----------|--------|----------|---------|-------------------|--------|
| API-020 | List accounts - default | GET | `/accounts` | - | 200, `{items, total, page, page_size}` | [ ] |
| API-021 | List accounts - search by plate | GET | `/accounts?plate=29A` | - | 200, filtered results | [ ] |
| API-022 | List accounts - filter registered | GET | `/accounts?registration_status=registered` | - | 200, only registered | [ ] |
| API-023 | List accounts - filter temporary | GET | `/accounts?registration_status=temporary_registered` | - | 200, only temporary | [ ] |
| API-024 | List accounts - pagination | GET | `/accounts?page=2&page_size=5` | - | 200, correct page | [ ] |
| API-025 | List accounts - page_size limit | GET | `/accounts?page_size=200` | - | 422 or capped to max | [ ] |
| API-026 | Get accounts summary | GET | `/accounts/summary` | - | 200, `{total, registered, temporary}` | [ ] |
| API-027 | Get single account - found | GET | `/accounts/{plate}` | Existing plate | 200, account details | [ ] |
| API-028 | Get single account - not found | GET | `/accounts/{plate}` | Non-existing plate | 404, `{detail: 'account_not_found'}` | [ ] |
| API-029 | Get account transactions | GET | `/accounts/{plate}/transactions` | Existing plate | 200, array of transactions | [ ] |
| API-030 | Get account transactions - not found | GET | `/accounts/{plate}/transactions` | Non-existing plate | 404 | [ ] |

### 4.3 Barrier Actions API (`/api/v1/barrier-actions`)

| ID | Test Case | Method | Endpoint | Request | Expected Response | Status |
|----|-----------|--------|----------|---------|-------------------|--------|
| API-040 | List barrier actions | GET | `/barrier-actions?plate=...` | Valid plate | 200, array of actions | [ ] |
| API-041 | List barrier actions - missing plate | GET | `/barrier-actions` | No plate param | 422 Validation Error | [ ] |
| API-042 | Verify barrier action - success | POST | `/barrier-actions/verify?plate=...&actor=...` | Plate with hold | 200, action with 'open' | [ ] |
| API-043 | Verify barrier action - not found | POST | `/barrier-actions/verify?plate=...&actor=...` | Plate with no actions | 404 | [ ] |
| API-044 | Verify barrier action - already open | POST | `/barrier-actions/verify?plate=...&actor=...` | Plate already open | 200, unchanged | [ ] |

### 4.4 Stats API (`/api/v1/stats`)

| ID | Test Case | Method | Endpoint | Expected Response | Status |
|----|-----------|--------|----------|-------------------|--------|
| API-050 | Realtime stats | GET | `/stats/realtime` | 200, `{total_in, total_out, ocr_success_rate}` | [ ] |
| API-051 | Traffic stats - hourly | GET | `/stats/traffic?group_by=hour` | 200, array with 'YYYY-MM-DD HH:00' buckets | [ ] |
| API-052 | Traffic stats - daily | GET | `/stats/traffic?group_by=day` | 200, array with 'YYYY-MM-DD' buckets | [ ] |
| API-053 | Traffic stats - invalid group_by | GET | `/stats/traffic?group_by=invalid` | 200, defaults to 'hour' | [ ] |
| API-054 | OCR success rate | GET | `/stats/ocr-success-rate` | 200, `{success_rate}` | [ ] |

### 4.5 Health & Misc

| ID | Test Case | Method | Endpoint | Expected Response | Status |
|----|-----------|--------|----------|-------------------|--------|
| API-060 | Health check | GET | `/health` | 200, `{status: 'ok', time: ...}` | [ ] |
| API-061 | Error sample | GET | `/api/v1/errors/sample` | 200, `{detail: 'not_implemented'}` | [ ] |
| API-062 | Invalid endpoint | GET | `/api/v1/invalid` | 404 Not Found | [ ] |

---

## 5. Integration Tests - Import Scripts

### 5.1 `generate_seed_plates.py`

**File**: `scripts/generate_seed_plates.py`

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| IMP-001 | Parse plate from VNLP filename | `6_2215_0_98n12408_470_70_592_168.jpg` | `98N12408` | [ ] |
| IMP-002 | Normalize - uppercase | `29a12345` | `29A12345` | [ ] |
| IMP-003 | Normalize - remove dashes | `29A-123-45` | `29A12345` | [ ] |
| IMP-004 | Normalize - remove dots | `29A.123.45` | `29A12345` | [ ] |
| IMP-005 | Normalize - remove spaces | `29A 123 45` | `29A12345` | [ ] |
| IMP-006 | Validate VN plate format | `29A12345` | Returns plate (valid) | [ ] |
| IMP-007 | Validate - too short | `ABC` | Returns None (invalid) | [ ] |
| IMP-008 | Validate - invalid format | `ABCDEFGH` | Returns None (invalid) | [ ] |
| IMP-009 | Deduplicate plates | 3 identical plates | Output contains 1 | [ ] |
| IMP-010 | CSV output format | Valid input | CSV with columns: plate_text, source, seed_group, vehicle_type | [ ] |
| IMP-011 | JSON summary output | Valid input | JSON with stats: total, unique, province distribution | [ ] |
| IMP-012 | Source file not found | Invalid path | Exits with error message | [ ] |

### 5.2 `import_seed_plates.py`

**File**: `scripts/import_seed_plates.py`

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| IMP-020 | Import new plate - creates account | New plate | Account with `registration_status='registered'` | [ ] |
| IMP-021 | Import new plate - initial balance | New plate | `balance_vnd=100000` | [ ] |
| IMP-022 | Import new plate - init transaction | New plate | Transaction `type='init'`, `amount=100000` | [ ] |
| IMP-023 | Import existing plate - skip | Existing plate | No duplicate, skipped count++ | [ ] |
| IMP-024 | Import - idempotent run 1 | Fresh DB | N accounts created | [ ] |
| IMP-025 | Import - idempotent run 2 | Same data | 0 new accounts, N skipped | [ ] |
| IMP-026 | Import - summary output | Complete run | Prints imported/skipped/invalid | [ ] |
| IMP-027 | Import - transaction rollback | Error during import | All changes rolled back | [ ] |
| IMP-028 | Import - invalid plate skip | Invalid plate in CSV | Skipped, invalid count++ | [ ] |
| IMP-029 | Import - database connection error | Wrong DATABASE_URL | Exits with error | [ ] |
| IMP-030 | Import - CSV not found | Invalid path | Exits with error | [ ] |

### 5.3 `import_vehicle_events.py`

**File**: `scripts/import_vehicle_events.py`

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| IMP-040 | Camera lookup - found | Existing camera name | Returns camera_id | [ ] |
| IMP-041 | Camera lookup - not found | Non-existing name | Script exits with error | [ ] |
| IMP-042 | Insert vehicle events | 10 records | 10 vehicle_events created | [ ] |
| IMP-043 | Insert plate reads | 10 records | 10 plate_reads created | [ ] |
| IMP-044 | HTTP URL format | Snapshot URL | Starts with `http://`, not `file://` | [ ] |
| IMP-045 | Alternating direction | 10 events | Index 0,2,4,6,8='in', 1,3,5,7,9='out' | [ ] |
| IMP-046 | Custom snapshot_base_url | `--snapshot-base-url http://custom:8088` | URLs use custom base | [ ] |
| IMP-047 | Custom camera name | `--camera-name "Custom Cam"` | Looks up that camera | [ ] |

---

## 6. Database & Migration Tests

### 6.1 Schema & Migrations

| ID | Test Case | Expected | Status |
|----|-----------|----------|--------|
| DB-001 | Tables created | cameras, vehicle_events, plate_reads, accounts, transactions, barrier_actions, audit_logs | [ ] |
| DB-002 | Constraint - direction | Only 'in' or 'out' allowed | [ ] |
| DB-003 | Constraint - vehicle_type | Only 'motorbike' or 'car' allowed | [ ] |
| DB-004 | Constraint - ocr_status | Only 'success', 'partial', 'failed' | [ ] |
| DB-005 | Constraint - registration_status | Only 'registered', 'temporary_registered', 'unknown' | [ ] |
| DB-006 | Constraint - barrier_action | Only 'open' or 'hold' | [ ] |
| DB-007 | Constraint - transaction type | Only 'init', 'event_charge', 'manual_adjust' | [ ] |
| DB-008 | Unique - accounts.plate_text | Duplicate plate_text rejected | [ ] |
| DB-009 | Indexes created | All expected indexes exist | [ ] |

### 6.2 Referential Integrity

| ID | Test Case | Expected | Status |
|----|-----------|----------|--------|
| DB-010 | FK - vehicle_events.camera_id | References cameras.id | [ ] |
| DB-011 | FK - plate_reads.event_id | References vehicle_events.id, CASCADE delete | [ ] |
| DB-012 | FK - transactions.account_id | References accounts.id, CASCADE delete | [ ] |
| DB-013 | FK - transactions.event_id | References vehicle_events.id, nullable | [ ] |
| DB-014 | FK - barrier_actions.event_id | References vehicle_events.id, CASCADE delete | [ ] |

---

## 7. End-to-End Tests - Business Flow

### 7.1 Registered Vehicle Flow

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| E2E-001 | Registered IN | 1. Import seed plate<br>2. POST event IN | barrier='open', balance-=2000 | [ ] |
| E2E-002 | Registered OUT | 1. Plate đã registered<br>2. POST event OUT | barrier='open', balance-=2000 | [ ] |
| E2E-003 | Registered IN+OUT sequence | 1. IN event<br>2. OUT event | Both 'open', balance-=4000 total | [ ] |
| E2E-004 | Multiple events same plate | 5 events | 5 transactions, balance=100000-10000=90000 | [ ] |

### 7.2 Unknown/Temporary Vehicle Flow

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| E2E-010 | Unknown IN creates temporary | POST event with new plate, direction='in' | New account `temporary_registered`, barrier='open' | [ ] |
| E2E-011 | Temporary OUT holds | 1. Plate is temporary<br>2. POST event OUT | barrier='hold', needs_verification=True | [ ] |
| E2E-012 | Verify hold opens barrier | 1. Barrier is hold<br>2. POST verify | barrier='open', verified_by set | [ ] |
| E2E-013 | Verify audit logged | After verify | AuditLog entry created | [ ] |

### 7.3 Balance & Transaction Flow

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| E2E-020 | Init transaction on import | Import new plate | Transaction type='init', amount=100000 | [ ] |
| E2E-021 | Event charge transaction | POST event | Transaction type='event_charge', amount=-2000 | [ ] |
| E2E-022 | Balance calculation | Init + 3 events | balance = 100000 - 6000 = 94000 | [ ] |
| E2E-023 | Negative balance allowed | 60 events | balance = 100000 - 120000 = -20000 | [ ] |
| E2E-024 | balance_after_vnd accurate | After each txn | balance_after_vnd matches account.balance_vnd | [ ] |

### 7.4 Full Demo Flow

**Script**: `scripts/test_seeded_flow.py`

| ID | Test Case | Command | Expected | Status |
|----|-----------|---------|----------|--------|
| E2E-030 | test_registered_in | `--only test_registered_in` | PASS | [ ] |
| E2E-031 | test_registered_out | `--only test_registered_out` | PASS | [ ] |
| E2E-032 | test_unknown_in | `--only test_unknown_in` | PASS | [ ] |
| E2E-033 | test_temporary_out | `--only test_temporary_out` | PASS | [ ] |
| E2E-034 | Full flow all tests | No args | All 4 tests PASS | [ ] |

---

## 8. Dashboard UI Tests

### 8.1 Page Load & Navigation

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-001 | Dashboard loads | Open http://localhost:5173 | Page loads without errors | [ ] |
| UI-002 | No console errors | Open DevTools | No JS errors in console | [ ] |
| UI-003 | Responsive layout | Resize browser | Layout adapts correctly | [ ] |

### 8.2 Stats Cards Section

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-010 | Total In card | Page loads | Shows correct count | [ ] |
| UI-011 | Total Out card | Page loads | Shows correct count | [ ] |
| UI-012 | OCR Success card | Page loads | Shows percentage | [ ] |
| UI-013 | Total Accounts card | Page loads | Blue card with count | [ ] |
| UI-014 | Registered card | Page loads | Green card with count | [ ] |
| UI-015 | Temporary card | Page loads | Yellow card with count | [ ] |
| UI-016 | Traffic summary | Page loads | Shows bucket data | [ ] |

### 8.3 Realtime Events Section

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-020 | Events table renders | Events in DB | Table with Time, Plate, Type, Dir, Barrier | [ ] |
| UI-021 | Empty state | No events | Shows "No events yet" | [ ] |
| UI-022 | Refresh button works | Click Refresh | Data reloads | [ ] |
| UI-023 | Time format | Events present | Shows localized time | [ ] |

### 8.4 Account Search Section

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-030 | Search input present | Page loads | Input placeholder "Plate number" | [ ] |
| UI-031 | Search by plate - found | Enter valid plate, Search | Shows Balance, Transaction count | [ ] |
| UI-032 | Search by plate - not found | Enter invalid plate, Search | Shows error message | [ ] |
| UI-033 | Date range filters | Set from/to dates | Filters events by time | [ ] |
| UI-034 | Search results table | Search success | Shows matching events | [ ] |
| UI-035 | Barrier decisions list | Search success | Shows barrier actions | [ ] |

### 8.5 Account List Section

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-040 | Account list table | Accounts in DB | Table with Plate, Balance, Status | [ ] |
| UI-041 | Search filter | Type in search input | List filters | [ ] |
| UI-042 | Status filter - All | Select "All" | Shows all accounts | [ ] |
| UI-043 | Status filter - Registered | Select "Registered" | Shows only registered | [ ] |
| UI-044 | Status filter - Temporary | Select "Temporary" | Shows only temporary | [ ] |
| UI-045 | Pagination - Next | Click Next | Shows next page | [ ] |
| UI-046 | Pagination - Previous | Click Previous | Shows previous page | [ ] |
| UI-047 | Page info display | Paginate | Shows "Page X of Y" | [ ] |
| UI-048 | Status badge - registered | Registered account | Green badge | [ ] |
| UI-049 | Status badge - temporary | Temporary account | Yellow badge | [ ] |

### 8.6 Verification Queue Section

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-050 | Queue displays holds | Actions need verify | Table with Plate, Reason, Time, Verify button | [ ] |
| UI-051 | Empty queue | No pending | Shows "No pending verifications" | [ ] |
| UI-052 | Verify button click | Click Verify | API called, row removed | [ ] |
| UI-053 | Verify button loading | During verify | Button shows loading state | [ ] |
| UI-054 | Refresh queue button | Click Refresh | Queue reloads | [ ] |
| UI-055 | Pending count badge | N pending | Badge shows N | [ ] |

### 8.7 Error Handling

| ID | Test Case | Steps | Expected | Status |
|----|-----------|-------|----------|--------|
| UI-060 | API error display | Backend returns error | Red error box appears | [ ] |
| UI-061 | Network error | Backend not running | Error message shown | [ ] |
| UI-062 | Error dismissable | After error | Can recover, try again | [ ] |

---

## 9. Performance Tests

### 9.1 API Response Time

| ID | Test Case | Threshold | Status |
|----|-----------|-----------|--------|
| PERF-001 | GET /events (100 records) | < 200ms | [ ] |
| PERF-002 | GET /events (1000 records) | < 500ms | [ ] |
| PERF-003 | GET /accounts (1000 records) | < 500ms | [ ] |
| PERF-004 | POST /events | < 100ms | [ ] |
| PERF-005 | GET /accounts/summary | < 100ms | [ ] |
| PERF-006 | POST /barrier-actions/verify | < 100ms | [ ] |

### 9.2 Import Script Performance

| ID | Test Case | Threshold | Status |
|----|-----------|-----------|--------|
| PERF-010 | Import 3000 plates | < 30 seconds | [ ] |
| PERF-011 | Import 3000 plates (second run) | < 10 seconds (all skipped) | [ ] |
| PERF-012 | Generate seed CSV (5000 lines) | < 5 seconds | [ ] |

### 9.3 Dashboard Performance

| ID | Test Case | Threshold | Status |
|----|-----------|-----------|--------|
| PERF-020 | Initial page load (cold) | < 3 seconds | [ ] |
| PERF-021 | Initial page load (warm) | < 1 second | [ ] |
| PERF-022 | Account list pagination | < 500ms per page | [ ] |
| PERF-023 | Search response | < 1 second | [ ] |

---

## 10. Security Tests

### 10.1 Input Validation

| ID | Test Case | Input | Expected | Status |
|----|-----------|-------|----------|--------|
| SEC-001 | SQL injection - plate search | `'; DROP TABLE accounts; --` | Query safe, no error | [ ] |
| SEC-002 | SQL injection - API param | `plate='; DELETE FROM accounts;` | 200 or 422, no damage | [ ] |
| SEC-003 | XSS - plate text display | `<script>alert('xss')</script>` | Text escaped in UI | [ ] |
| SEC-004 | Invalid UUID - camera_id | `camera_id='not-a-uuid'` | 422 Validation Error | [ ] |
| SEC-005 | Invalid direction enum | `direction='sideways'` | 422 Validation Error | [ ] |
| SEC-006 | Invalid vehicle_type | `vehicle_type='bicycle'` | 422 Validation Error | [ ] |
| SEC-007 | Negative page number | `page=-1` | 422 or default to 1 | [ ] |
| SEC-008 | Oversized page_size | `page_size=10000` | Capped or 422 | [ ] |

### 10.2 Error Handling

| ID | Test Case | Expected | Status |
|----|-----------|----------|--------|
| SEC-010 | No stack trace in production | 500 errors don't expose code | [ ] |
| SEC-011 | Consistent error format | All errors return `{detail: ...}` | [ ] |

---

## 11. Typed Quality Gate Tests

### 11.1 Python Type Checking

| ID | Test Case | Command | Expected | Status |
|----|-----------|---------|----------|--------|
| TYPE-001 | Backend type check | `mypy app/` | No errors | [ ] |
| TYPE-002 | Scripts type check | `mypy scripts/` | No errors or acceptable | [ ] |
| TYPE-003 | Tests type check | `mypy tests/` | No errors | [ ] |

### 11.2 TypeScript Type Checking

| ID | Test Case | Command | Expected | Status |
|----|-----------|---------|----------|--------|
| TYPE-010 | Dashboard type check | `npm run typecheck` | Exit 0, no errors | [ ] |
| TYPE-011 | No `any` in main code | Review main.tsx | No explicit `any` | [ ] |
| TYPE-012 | API types match backend | Compare schemas | Types aligned | [ ] |

---

## 12. Test Data & Setup

### 12.1 Prerequisites

| ID | Item | Command/Action | Status |
|----|------|----------------|--------|
| DATA-001 | Docker running | `docker ps` | [ ] |
| DATA-002 | Postgres container | `docker-compose up -d postgres` | [ ] |
| DATA-003 | Backend running | `docker-compose up -d backend` | [ ] |
| DATA-004 | Mock server running | `docker-compose up -d mock_server` | [ ] |
| DATA-005 | Sample camera created | `psql < scripts/setup_sample_camera.sql` | [ ] |
| DATA-006 | Seed CSV generated | `python scripts/generate_seed_plates.py` | [ ] |
| DATA-007 | Seed plates imported | `python scripts/import_seed_plates.py` | [ ] |
| DATA-008 | Sample events imported | `python scripts/import_vehicle_events.py` | [ ] |

### 12.2 Test Accounts

| Plate | Status | Purpose |
|-------|--------|---------|
| 29A12345 | registered | Test registered flow |
| 99X99999 | (new) | Test unknown → temporary flow |
| 30M86121 | registered (from seed) | Test seed import |

---

## 13. Progress Tracking

### 13.1 Summary by Category

| Category | Total | Passed | Failed | Pending |
|----------|-------|--------|--------|---------|
| Unit Tests - Services | 9 | | | |
| Unit Tests - CRUD | 23 | | | |
| Integration Tests - API | 30 | | | |
| Integration Tests - Import | 30 | | | |
| Database Tests | 14 | | | |
| End-to-End Tests | 16 | | | |
| Dashboard UI Tests | 35 | | | |
| Performance Tests | 12 | | | |
| Security Tests | 11 | | | |
| Typed Quality Gates | 6 | | | |
| **TOTAL** | **186** | | | |

### 13.2 Execution Status

- [ ] Phase 1: Unit Tests Complete
- [ ] Phase 2: API Tests Complete
- [ ] Phase 3: Import Tests Complete
- [ ] Phase 4: E2E Tests Complete
- [ ] Phase 5: UI Tests Complete
- [ ] Phase 6: Performance Tests Complete
- [ ] Phase 7: Security Tests Complete
- [ ] Phase 8: Final Regression Pass
- [ ] Phase 9: Sign-off

---

## Phụ lục: Quick Commands

```bash
# Full stack start
docker-compose up -d

# Run all backend tests
cd apps/backend && python -m pytest tests/ -v

# Run seeded mode tests only
python -m pytest tests/test_seeded_mode.py -v

# Run API flow tests
python scripts/test_seeded_flow.py --verbose

# Dashboard type check
cd apps/dashboard && npm run typecheck

# View test coverage
python -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

**Người tạo**: Copilot CLI  
**Ngày tạo**: 2026-03-29  
**Phiên bản**: 2.0

