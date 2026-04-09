# DB SCHEMA - Pretrained Import Flow (Branch Plan Priority 1)

Tai lieu nay mo ta schema bo sung cho pretrained import flow.

---

## 1) Table: `pretrained_jobs`

### Muc dich
Luu thong tin moi job infer/import.

### Columns
- `id` UUID/STRING PK
- `job_type` TEXT NOT NULL
  - check: `infer | import`
- `status` TEXT NOT NULL
  - check: `queued | running | success | failed`
- `model_version` TEXT NOT NULL
- `source` TEXT NOT NULL
- `threshold` FLOAT NULL
- `total_items` INT NOT NULL DEFAULT 0
- `processed_items` INT NOT NULL DEFAULT 0
- `error_message` TEXT NULL
- `result_preview_json` JSON NULL
- `created_at` TIMESTAMPTZ NOT NULL
- `updated_at` TIMESTAMPTZ NOT NULL

### Indexes
- `idx_pretrained_jobs_status`
- `idx_pretrained_jobs_created_at`

---

## 2) Table: `pretrained_detections`

### Muc dich
Luu item-level ket qua cho tung job import/infer.

### Columns
- `id` UUID/STRING PK
- `job_id` UUID/STRING FK -> `pretrained_jobs(id)` ON DELETE CASCADE
- `plate_text` TEXT NULL
- `confidence` FLOAT NULL
- `vehicle_type` TEXT NULL
  - check: `motorbike | car` (neu khong NULL)
- `event_time` TIMESTAMPTZ NULL
- `metadata_json` JSON NULL
- `created_at` TIMESTAMPTZ NOT NULL

### Indexes
- `idx_pretrained_detections_job_id`
- `idx_pretrained_detections_plate_text`

---

## 3) Migration lien quan

- `apps/backend/migrations/004_pretrained_jobs.sql`

Noi dung migration:
1. Tao `pretrained_jobs`
2. Tao `pretrained_detections`
3. Tao cac index phuc vu list/lookup nhanh

---

## 4) Quan he du lieu

- 1 `pretrained_job` co N `pretrained_detections`.
- Xoa job se xoa theo detections qua `ON DELETE CASCADE`.

---

## 5) Query patterns chinh

1. List jobs phan trang theo `created_at DESC`.
2. Summary jobs theo `status` (`queued/running/success/failed`).
3. Lay detail job + detections by `job_id`.
