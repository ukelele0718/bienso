# API CONTRACT - PRETRAINED IMPORT FLOW

Tai lieu contract cho branch `feat/pretrained-lpr-import-flow` (phase code-first, runtime-light).

---

## 1) Pretrained Endpoints

## 1.1 Create infer job (mocked)

- **Method**: `POST`
- **Path**: `/api/v1/pretrained/infer`

### Request

```json
{
  "model_version": "mock-v1",
  "source": "demo://frame-001.jpg",
  "threshold": 0.5
}
```

### Response `200`

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
  "created_at": "2026-04-06T22:00:00Z",
  "updated_at": "2026-04-06T22:00:00Z",
  "error_message": null,
  "result_preview": {
    "plate_text": "MOCK12345",
    "confidence": 0.92,
    "vehicle_type": "motorbike"
  },
  "items": null
}
```

---

## 1.2 Create import job

- **Method**: `POST`
- **Path**: `/api/v1/pretrained/import`

### Request

```json
{
  "model_version": "mock-v1",
  "source": "demo://batch-001",
  "items": [
    {
      "plate_text": "51G12345",
      "confidence": 0.9,
      "vehicle_type": "motorbike"
    },
    {
      "plate_text": "99X99999",
      "confidence": 0.78,
      "vehicle_type": "car"
    }
  ]
}
```

### Response `200`

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
  "created_at": "2026-04-06T22:00:00Z",
  "updated_at": "2026-04-06T22:00:00Z",
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
      "confidence": 0.9,
      "vehicle_type": "motorbike",
      "event_time": null,
      "metadata_json": null,
      "created_at": "2026-04-06T22:00:00Z"
    }
  ]
}
```

---

## 1.3 List jobs (pagination)

- **Method**: `GET`
- **Path**: `/api/v1/pretrained/jobs?page=1&page_size=20`

### Response `200`

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
      "created_at": "2026-04-06T22:00:00Z",
      "updated_at": "2026-04-06T22:00:00Z",
      "error_message": null,
      "result_preview": {"imported": 2},
      "items": null
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

---

## 1.4 Get job detail

- **Method**: `GET`
- **Path**: `/api/v1/pretrained/jobs/{job_id}`

### Response `200`

- Tra ve `PretrainedJobOut` + `items` day du.

### Response `404`

```json
{
  "detail": "pretrained_job_not_found"
}
```

---

## 1.5 Get jobs summary counts

- **Method**: `GET`
- **Path**: `/api/v1/pretrained/jobs/summary`

### Response `200`

```json
{
  "total": 10,
  "queued": 1,
  "running": 2,
  "success": 6,
  "failed": 1
}
```

---

## 2) Shared contracts

### 2.1 Job status lifecycle

- `queued`
- `running`
- `success`
- `failed`

### 2.2 Job types

- `infer`
- `import`

### 2.3 Validation rules

- `threshold`: `0.0 <= threshold <= 1.0` (optional)
- `vehicle_type` in detection item: `motorbike | car` (optional)
- `model_version`, `source`: required string

---

## 3) Dashboard mapping

Frontend su dung:
- `fetchPretrainedJobs` -> bang jobs
- `fetchPretrainedJob` -> detail drawer
- `fetchPretrainedJobsSummary` -> cards summary
- `createPretrainedInferJob` / `createPretrainedImportJob` -> tao job nhanh
