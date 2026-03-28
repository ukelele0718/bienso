# API Contract (Draft v1)
## Vehicle LPR System - Typed API

Base URL (dev): `http://localhost:8000/api/v1`

---

## 1) POST `/events`
AI Engine gửi event đã xử lý (detect/track/count/OCR) và nhận quyết định điều khiển thanh chắn.

### Request Body
```json
{
  "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
  "timestamp": "2026-03-27T08:15:30Z",
  "direction": "in",
  "vehicle_type": "motorbike",
  "track_id": "track_219",
  "plate_text": "29A-12345",
  "confidence": 0.94,
  "snapshot_url": "https://storage/events/evt_001.jpg",
  "crop_url": "https://storage/plates/evt_001_crop.jpg"
}
```

### Response 201
```json
{
  "id": "401f3b5e-c3fd-4cc2-a1cb-a2ad9ebf4f18",
  "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
  "timestamp": "2026-03-27T08:15:30Z",
  "direction": "in",
  "vehicle_type": "motorbike",
  "track_id": "track_219",
  "plate_text": "29A-12345",
  "confidence": 0.94,
  "snapshot_url": "https://storage/events/evt_001.jpg",
  "registration_status": "temporary_registered",
  "barrier_action": "open",
  "barrier_reason": "unknown_vehicle_auto_temporary_register"
}
```

### Side effects
- Tạo `vehicle_event` + `plate_read`.
- Nếu có `plate_text` hợp lệ:
  - tạo account mới với 100,000 VND nếu chưa tồn tại.
  - nếu plate chưa có trong hệ thống: gán `registration_status=temporary_registered`.
  - trừ 2,000 VND và tạo transaction.
- Tạo `barrier_action` theo rule:
  - `registered` + direction=`in` => `open`
  - `temporary_registered` + direction=`in` => `open`
  - `temporary_registered` + direction=`out` => `hold` + `needs_verification=true`
  - sau khi verify mới phát lệnh `open`.

---

## 2) GET `/events`
Tra cứu sự kiện theo biển số và khoảng thời gian.

### Query Params
- `plate` (optional)
- `from` (optional, ISO datetime)
- `to` (optional, ISO datetime)
- `direction` (optional: `in` | `out`)
- `vehicle_type` (optional: `motorbike` | `car`)
- `page` (optional, default 1)
- `page_size` (optional, default 20)

### Response 200
```json
{
  "items": [
    {
      "id": "401f3b5e-c3fd-4cc2-a1cb-a2ad9ebf4f18",
      "camera_id": "6ec51d17-2ea4-4db7-b2f5-bf8a0f6748c4",
      "timestamp": "2026-03-27T08:15:30Z",
      "direction": "in",
      "vehicle_type": "motorbike",
      "track_id": "track_219",
      "plate_text": "29A-12345",
      "confidence": 0.94,
      "snapshot_url": "https://storage/events/evt_001.jpg"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

## 3) GET `/stats/realtime`
### Response 200
```json
{
  "total_in": 132,
  "total_out": 127,
  "ocr_success_rate": 91.3
}
```

---

## 4) GET `/stats/traffic`
Thống kê lưu lượng theo giờ/ngày.

### Query Params
- `group_by` = `hour` | `day`
- `from` (optional)
- `to` (optional)

### Response 200
```json
{
  "group_by": "hour",
  "series": [
    {"bucket": "2026-03-27T08:00:00Z", "total_in": 25, "total_out": 21},
    {"bucket": "2026-03-27T09:00:00Z", "total_in": 31, "total_out": 28}
  ]
}
```

---

## 5) GET `/stats/ocr-success-rate`
### Response 200
```json
{
  "ocr_success_rate": 91.3,
  "total_events": 500,
  "ocr_success_events": 456
}
```

---

## 6) GET `/accounts/{plate_text}`
Truy vấn số dư hiện tại theo biển số.

### Response 200
```json
{
  "plate_text": "29A-12345",
  "balance_vnd": 86000
}
```

---

## 7) GET `/accounts/{plate_text}/transactions`
Lịch sử giao dịch của biển số.

### Query Params
- `from` (optional)
- `to` (optional)
- `page` (optional)
- `page_size` (optional)

### Response 200
```json
{
  "items": [
    {
      "id": "6dd7f34f-bc17-4696-b89e-64f33e8c09ec",
      "tx_type": "event_charge",
      "amount_vnd": -2000,
      "balance_before_vnd": 88000,
      "balance_after_vnd": 86000,
      "created_at": "2026-03-27T08:15:31Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20
}
```

---

## 8) Lỗi chuẩn
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid timestamp format",
  "details": {"field": "timestamp"}
}
```

Mã lỗi đề xuất:
- `VALIDATION_ERROR`
- `NOT_FOUND`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `CONFLICT`
- `INTERNAL_ERROR`

---

## 9) Type definitions gợi ý
- Python: Pydantic models (strict validation)
- Frontend: TypeScript interfaces generated từ OpenAPI

---

## 10) OpenAPI YAML skeleton
```yaml
openapi: 3.1.0
info:
  title: Vehicle LPR API
  version: 0.1.0
paths:
  /api/v1/events:
    post:
      summary: Create event
  /api/v1/events:
    get:
      summary: Search events
  /api/v1/stats/realtime:
    get:
      summary: Get realtime counters
  /api/v1/stats/traffic:
    get:
      summary: Get traffic stats
  /api/v1/accounts/{plate_text}:
    get:
      summary: Get account balance
  /api/v1/accounts/{plate_text}/transactions:
    get:
      summary: Get account transactions
```
