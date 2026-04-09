# API CONTRACT - Pretrained Import Flow (Branch Plan Priority 1)

## Base URL
- Local: `http://localhost:8000`

---

## 1) Create infer job

### Endpoint
`POST /api/v1/pretrained/infer`

### Request
```json
{
  "model_version": "mock-v1",
  "source": "demo://frame-001.jpg",
  "threshold": 0.5
}
```

### Response 200
```json
{
  "id": "uuid",
  "job_type": "infer",
  "status": "success",
  "model_version": "mock-v1",
  "source": "demo://frame-001.jpg",
  "threshold": 0.5,
  "total_items": 1,
  "processed_items": 1,
  "created_at": "2026-04-06T15:00:00Z",
  "updated_at": "2026-04-06T15:00:00Z",
  "error_message": null,
  "result_preview": {
    "plate_text": "MOCK12345",
    "confidence": 0.92,
    "vehicle_type": "motorbike"
  },
  "items": []
}
```

---

## 2) Create import job

### Endpoint
`POST /api/v1/pretrained/import`

### Request
```json
{
  "model_version": "mock-v1",
  "source": "demo://batch-001",
  "items": [
    {
      "plate_text": "51G12345",
      "confidence": 0.91,
      "vehicle_type": "motorbike"
    },
    {
      "plate_text": "99X99999",
      "confidence": 0.77,
      "vehicle_type": "car"
    }
  ]
}
```

### Response 200
```json
{
  "id": "uuid",
  "job_type": "import",
  "status": "success",
  "model_version": "mock-v1",
  "source": "demo://batch-001",
  "threshold": null,
  "total_items": 2,
  "processed_items": 2,
  "created_at": "2026-04-06T15:00:00Z",
  "updated_at": "2026-04-06T15:00:00Z",
  "error_message": null,
  "result_preview": {
    "imported": 2,
    "skipped": 0,
    "invalid": 0
  },
  "items": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "plate_text": "51G12345",
      "confidence": 0.91,
      "vehicle_type": "motorbike",
      "event_time": null,
      "metadata_json": null,
      "created_at": "2026-04-06T15:00:00Z"
    }
  ]
}
```

---

## 3) List jobs

### Endpoint
`GET /api/v1/pretrained/jobs?page=1&page_size=20`

### Response 200
```json
{
  "items": [
    {
      "id": "uuid",
      "job_type": "import",
      "status": "success",
      "model_version": "mock-v1",
      "source": "demo://batch-001",
      "threshold": null,
      "total_items": 2,
      "processed_items": 2,
      "created_at": "2026-04-06T15:00:00Z",
      "updated_at": "2026-04-06T15:00:00Z",
      "error_message": null,
      "result_preview": {"imported": 2},
      "items": []
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 4
}
```

---

## 4) Jobs summary

### Endpoint
`GET /api/v1/pretrained/jobs/summary`

### Response 200
```json
{
  "total": 4,
  "queued": 0,
  "running": 0,
  "success": 4,
  "failed": 0
}
```

---

## 5) Job detail

### Endpoint
`GET /api/v1/pretrained/jobs/{job_id}`

### Response 200
```json
{
  "id": "uuid",
  "job_type": "import",
  "status": "success",
  "model_version": "mock-v1",
  "source": "demo://batch-001",
  "threshold": null,
  "total_items": 2,
  "processed_items": 2,
  "created_at": "2026-04-06T15:00:00Z",
  "updated_at": "2026-04-06T15:00:00Z",
  "error_message": null,
  "result_preview": {"imported": 2},
  "items": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "plate_text": "51G12345",
      "confidence": 0.91,
      "vehicle_type": "motorbike",
      "event_time": null,
      "metadata_json": null,
      "created_at": "2026-04-06T15:00:00Z"
    }
  ]
}
```

### Response 404
```json
{
  "detail": "pretrained_job_not_found"
}
```

---

## Notes
- Flow nay duoc thiet ke runtime-light, co the test nhanh khong can train model that.
- Kieu `status` hop le: `queued | running | success | failed`.
- Kieu `job_type` hop le: `infer | import`.
