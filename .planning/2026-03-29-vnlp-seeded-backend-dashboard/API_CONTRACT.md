# API Contract (Seeded Mode Draft v1)
## Vehicle LPR System - Typed API cho luong VNLP seeded backend dashboard

Base URL (dev): `http://localhost:8000/api/v1`

---

## 1) POST `/events`
Nguon event trong phase nay co the la:
- script gia lap
- cong cu import event mau
- runtime seeded mode

He thong nhan event da co `plate_text` va tra ve quyet dinh nghiep vu / barrier.

### Request Body
```json
{
  "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
  "timestamp": "2026-03-29T08:15:30Z",
  "direction": "in",
  "vehicle_type": "motorbike",
  "track_id": "seeded_track_001",
  "plate_text": "29A12345",
  "confidence": 1.0,
  "snapshot_url": "https://storage/events/evt_seed_001.jpg"
}
```

### Response 201
```json
{
  "id": "401f3b5e-c3fd-4cc2-a1cb-a2ad9ebf4f18",
  "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
  "timestamp": "2026-03-29T08:15:30Z",
  "direction": "in",
  "vehicle_type": "motorbike",
  "track_id": "seeded_track_001",
  "plate_text": "29A12345",
  "confidence": 1.0,
  "snapshot_url": "https://storage/events/evt_seed_001.jpg",
  "registration_status": "registered",
  "barrier_action": "open",
  "barrier_reason": "registered_vehicle_in",
  "needs_verification": false
}
```

### Side effects
- Tao `vehicle_event` + `plate_read`.
- Neu `plate_text` da ton tai trong `accounts`:
  - dung `registration_status` hien co.
  - tru `2000 VND`.
  - tao `event_charge transaction`.
- Neu `plate_text` chua ton tai:
  - tao account moi `temporary_registered`.
  - khoi tao `100000 VND`.
  - tao `init transaction`.
  - tru `2000 VND`.
- Tao `barrier_action` theo rule seeded mode:
  - `registered` + `in` => `open`
  - `registered` + `out` => `open`
  - `temporary_registered` + `in` => `open`
  - `temporary_registered` + `out` => `hold`

---

## 2) GET `/events`
Tra cuu su kien theo bien so va khoang thoi gian.

### Query Params
- `plate` (optional)
- `from_time` (optional, ISO datetime)
- `to_time` (optional, ISO datetime)
- `direction` (optional: `in` | `out`)
- `vehicle_type` (optional: `motorbike` | `car`)

### Response 200
```json
[
  {
    "id": "401f3b5e-c3fd-4cc2-a1cb-a2ad9ebf4f18",
    "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
    "timestamp": "2026-03-29T08:15:30Z",
    "direction": "in",
    "vehicle_type": "motorbike",
    "track_id": "seeded_track_001",
    "plate_text": "29A12345",
    "confidence": 1.0,
    "snapshot_url": "https://storage/events/evt_seed_001.jpg",
    "registration_status": "registered",
    "barrier_action": "open",
    "barrier_reason": "registered_vehicle_in",
    "needs_verification": false
  }
]
```

---

## 3) GET `/stats/realtime`
### Response 200
```json
{
  "total_in": 132,
  "total_out": 127,
  "ocr_success_rate": 100.0
}
```

Luu y:
- Trong seeded mode, `ocr_success_rate` co the gan nhu `100%` neu moi event deu co `plate_text`.
- Metric nay van duoc giu de tranh vo UI va de merge lai ve AI mode sau nay.

---

## 4) GET `/stats/traffic`
Thong ke luu luong theo gio/ngay.

### Query Params
- `group_by` = `hour` | `day`

### Response 200
```json
[
  {"bucket": "2026-03-29 08:00", "total_in": 25, "total_out": 21},
  {"bucket": "2026-03-29 09:00", "total_in": 31, "total_out": 28}
]
```

---

## 5) GET `/stats/ocr-success-rate`
### Response 200
```json
{
  "success_rate": 100.0
}
```

---

## 6) GET `/accounts`
Danh sach account seeded / temporary.

### Query Params
- `plate` (optional)
- `registration_status` (optional: `registered` | `temporary_registered` | `unknown`)
- `page` (optional)
- `page_size` (optional)

### Response 200
```json
{
  "items": [
    {
      "plate_text": "29A12345",
      "balance_vnd": 86000,
      "registration_status": "registered"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

## 7) GET `/accounts/summary`
### Response 200
```json
{
  "total_accounts": 3227,
  "registered_accounts": 3200,
  "temporary_registered_accounts": 27
}
```

---

## 8) GET `/accounts/{plate_text}`
Truy van so du hien tai theo bien so.

### Response 200
```json
{
  "plate_text": "29A12345",
  "balance_vnd": 86000,
  "registration_status": "registered"
}
```

---

## 9) GET `/accounts/{plate_text}/transactions`
Lich su giao dich cua bien so.

### Response 200
```json
[
  {
    "id": "6dd7f34f-bc17-4696-b89e-64f33e8c09ec",
    "account_id": "acc_001",
    "event_id": "evt_001",
    "amount_vnd": -2000,
    "balance_after_vnd": 86000,
    "type": "event_charge",
    "created_at": "2026-03-29T08:15:31Z"
  }
]
```

---

## 10) GET `/barrier-actions`
Tra cuu lich su barrier theo bien so.

### Query Params
- `plate` (required)

### Response 200
```json
[
  {
    "id": "bar_001",
    "event_id": "evt_001",
    "plate_text": "29A12345",
    "registration_status": "registered",
    "barrier_action": "open",
    "barrier_reason": "registered_vehicle_in",
    "needs_verification": false,
    "verified_by": null,
    "verified_at": null,
    "created_at": "2026-03-29T08:15:31Z"
  }
]
```

---

## 11) POST `/barrier-actions/verify`
Mo barrier cho event dang `hold`.

### Query Params
- `plate` (required)
- `actor` (required)

### Response 200
```json
{
  "id": "bar_002",
  "event_id": "evt_002",
  "plate_text": "30B99999",
  "registration_status": "temporary_registered",
  "barrier_action": "open",
  "barrier_reason": "manual_verify_open",
  "needs_verification": false,
  "verified_by": "guard_01",
  "verified_at": "2026-03-29T08:20:00Z",
  "created_at": "2026-03-29T08:19:10Z"
}
```

---

## 12) Loi chuan
```json
{
  "detail": "account_not_found"
}
```

Ma loi de xuat:
- `account_not_found`
- `barrier_action_not_found`
- `validation_error`
- `internal_error`

---

## 13) Type definitions goi y
- Python: Pydantic models + typed CRUD return shapes
- Frontend: TypeScript interfaces generated hoac viet tay tu OpenAPI

---

## 14) Merge note
File nay co chu dich giu ten va thu tu section gan voi `.artifacts/API_CONTRACT.md`.

Khi merge ve `.artifacts`, uu tien:
- giu cac endpoint chung da on dinh
- them nho cac endpoint seeded-mode bo sung:
  - `GET /accounts`
  - `GET /accounts/summary`
  - `GET /barrier-actions`
  - `POST /barrier-actions/verify`
- sau nay co the de `seeded mode` lam mot execution profile cua cung mot API contract tong

