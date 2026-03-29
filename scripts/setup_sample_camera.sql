-- Create sample camera for VNLP import
-- Run this AFTER migrations are applied

-- Insert sample camera for VNLP data import
INSERT INTO cameras (id, name, gate_type, location, stream_url, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'VNLP Sample Camera',
    'student',
    'offline-import',
    NULL,
    TRUE
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    gate_type = EXCLUDED.gate_type,
    location = EXCLUDED.location;

-- Verify camera was created
SELECT id, name, gate_type, location, is_active FROM cameras;
