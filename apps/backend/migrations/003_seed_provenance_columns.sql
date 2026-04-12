-- 003_seed_provenance_columns.sql
-- Optional seeded-mode provenance columns for import audit

ALTER TABLE accounts
    ADD COLUMN IF NOT EXISTS source TEXT,
    ADD COLUMN IF NOT EXISTS seed_group TEXT,
    ADD COLUMN IF NOT EXISTS imported_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS import_batches (
    id UUID PRIMARY KEY,
    source TEXT NOT NULL,
    seed_group TEXT,
    imported_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    invalid_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

ALTER TABLE accounts
    ADD COLUMN IF NOT EXISTS import_batch_id UUID REFERENCES import_batches(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_accounts_source ON accounts(source);
CREATE INDEX IF NOT EXISTS idx_accounts_seed_group ON accounts(seed_group);
CREATE INDEX IF NOT EXISTS idx_accounts_import_batch_id ON accounts(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_import_batches_created_at ON import_batches(created_at DESC);
