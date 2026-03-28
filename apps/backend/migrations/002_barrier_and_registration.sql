-- 002_barrier_and_registration.sql
-- Add registration_status and barrier action log

ALTER TABLE accounts
    ADD COLUMN IF NOT EXISTS registration_status VARCHAR(30) NOT NULL DEFAULT 'temporary_registered',
    ADD CONSTRAINT ck_accounts_registration_status CHECK (registration_status IN ('registered','temporary_registered','unknown'));

CREATE TABLE IF NOT EXISTS barrier_actions (
    id UUID PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES vehicle_events(id) ON DELETE CASCADE,
    plate_text TEXT,
    registration_status VARCHAR(30) NOT NULL CHECK (registration_status IN ('registered','temporary_registered','unknown')),
    barrier_action VARCHAR(10) NOT NULL CHECK (barrier_action IN ('open','hold')),
    barrier_reason TEXT NOT NULL,
    needs_verification BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_barrier_actions_event_id ON barrier_actions(event_id);
CREATE INDEX IF NOT EXISTS idx_barrier_actions_plate_text ON barrier_actions(plate_text);
