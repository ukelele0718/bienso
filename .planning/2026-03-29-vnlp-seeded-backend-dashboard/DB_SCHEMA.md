# DB SCHEMA - PRETRAINED JOBS & DETECTIONS

Tai lieu schema bo sung cho branch `feat/pretrained-lpr-import-flow`.

---

## 1) Table: `pretrained_jobs`

### Columns

- `id` UUID/STRING PK
- `job_type` TEXT NOT NULL (`infer|import`)
- `status` TEXT NOT NULL (`queued|running|success|failed`)
- `model_version` TEXT NOT NULL
- `source` TEXT NOT NULL
- `threshold` FLOAT NULL
- `total_items` INTEGER NOT NULL DEFAULT 0
- `processed_items` INTEGER NOT NULL DEFAULT 0
- `error_message` TEXT NULL
- `result_preview_json` JSON NULL
- `created_at` TIMESTAMPTZ NOT NULL
- `updated_at` TIMESTAMPTZ NOT NULL

### Constraints

- `ck_pretrained_jobs_job_type`
- `ck_pretrained_jobs_status`

### Indexes

- `idx_pretrained_jobs_created_at`
- `idx_pretrained_jobs_status`
- `idx_pretrained_jobs_job_type`

---

## 2) Table: `pretrained_detections`

### Columns

- `id` UUID/STRING PK
- `job_id` UUID/STRING FK -> `pretrained_jobs.id` (ON DELETE CASCADE)
- `plate_text` TEXT NULL
- `confidence` FLOAT NULL
- `vehicle_type` TEXT NULL (`motorbike|car`)
- `event_time` TIMESTAMPTZ NULL
- `metadata_json` JSON NULL
- `created_at` TIMESTAMPTZ NOT NULL

### Constraints

- `ck_pretrained_detections_vehicle_type`

### Indexes

- `idx_pretrained_detections_job_id`
- `idx_pretrained_detections_plate_text`

---

## 3) Relationship

- `pretrained_jobs (1) -> (N) pretrained_detections`
- Detail endpoint load items theo `job_id`

---

## 4) Migration file

- `apps/backend/migrations/004_pretrained_jobs.sql`

Migration nay tao du 2 bang + indexes + constraints de phuc vu API:
- list jobs,
- job detail,
- summary status counts.

---

## 5) Note implementation

- Backend ORM models:
  - `PretrainedJob`
  - `PretrainedDetection`
- CRUD layer:
  - `create_job`
  - `create_detections`
  - `list_jobs`
  - `get_job`
  - `list_detections_by_job`
  - `get_jobs_summary`
