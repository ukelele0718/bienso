-- Verify import results
-- Run this after import_vehicle_events.py

-- Count records
SELECT 'vehicle_events' AS table_name, COUNT(*) AS count FROM vehicle_events
UNION ALL
SELECT 'plate_reads', COUNT(*) FROM plate_reads
UNION ALL
SELECT 'cameras', COUNT(*) FROM cameras;

-- Show sample data with snapshot URLs
SELECT 
    ve.id AS event_id,
    ve.direction,
    ve.vehicle_type,
    ve.timestamp,
    pr.plate_text,
    pr.confidence,
    pr.snapshot_url,
    pr.ocr_status
FROM vehicle_events ve
JOIN plate_reads pr ON pr.event_id = ve.id
ORDER BY ve.timestamp DESC
LIMIT 5;

-- Check if URLs are HTTP (not file://)
SELECT 
    CASE 
        WHEN snapshot_url LIKE 'http://%' THEN 'HTTP URL ✓'
        WHEN snapshot_url LIKE 'file://%' THEN 'FILE URL (needs fix)'
        ELSE 'Unknown format'
    END AS url_type,
    COUNT(*) as count
FROM plate_reads
GROUP BY url_type;
