-- 001_init.sql
-- Core schema for events, plates, accounts, transactions, audit logs

CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    gate_type TEXT NOT NULL CHECK (gate_type IN ('student', 'staff')),
    location TEXT,
    stream_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_events (
    id UUID PRIMARY KEY,
    camera_id UUID NOT NULL REFERENCES cameras(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('in', 'out')),
    vehicle_type TEXT NOT NULL CHECK (vehicle_type IN ('motorbike', 'car')),
    track_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS plate_reads (
    id UUID PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES vehicle_events(id) ON DELETE CASCADE,
    plate_text TEXT,
    confidence DOUBLE PRECISION,
    snapshot_url TEXT,
    crop_url TEXT,
    ocr_status TEXT NOT NULL CHECK (ocr_status IN ('success', 'partial', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY,
    plate_text TEXT UNIQUE NOT NULL,
    balance_vnd INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    event_id UUID REFERENCES vehicle_events(id),
    amount_vnd INTEGER NOT NULL,
    balance_after_vnd INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('init', 'event_charge', 'manual_adjust')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID,
    action TEXT NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_events_timestamp ON vehicle_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_vehicle_events_camera ON vehicle_events(camera_id);
CREATE INDEX IF NOT EXISTS idx_plate_reads_plate_text ON plate_reads(plate_text);
CREATE INDEX IF NOT EXISTS idx_plate_reads_confidence ON plate_reads(confidence);
CREATE INDEX IF NOT EXISTS idx_accounts_plate_text ON accounts(plate_text);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_event_id ON transactions(event_id);
