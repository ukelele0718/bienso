-- 004_pretrained_jobs.sql
-- Persistence layer for pretrained infer/import jobs and detections

CREATE TABLE IF NOT EXISTS pretrained_jobs (
    id UUID PRIMARY KEY,
    job_type TEXT NOT NULL CHECK (job_type IN ('infer', 'import')),
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'success', 'failed')),
    model_version TEXT NOT NULL,
    source TEXT NOT NULL,
    threshold DOUBLE PRECISION,
    total_items INTEGER NOT NULL DEFAULT 0,
    processed_items INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    result_preview_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pretrained_detections (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES pretrained_jobs(id) ON DELETE CASCADE,
    plate_text TEXT,
    confidence DOUBLE PRECISION,
    vehicle_type TEXT CHECK (vehicle_type IN ('motorbike', 'car')),
    event_time TIMESTAMP WITH TIME ZONE,
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pretrained_jobs_created_at ON pretrained_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_pretrained_jobs_status ON pretrained_jobs(status);
CREATE INDEX IF NOT EXISTS idx_pretrained_detections_job_id ON pretrained_detections(job_id);
CREATE INDEX IF NOT EXISTS idx_pretrained_detections_plate_text ON pretrained_detections(plate_text);
