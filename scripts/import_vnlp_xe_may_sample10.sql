-- Import 10 VNLP motorbike samples into backend DB
-- Usage (psql):
--   psql "<YOUR_DB_URL>" -f scripts/import_vnlp_xe_may_sample10.sql

BEGIN;

-- Ensure a camera exists
INSERT INTO cameras (id, name, gate_type, location, stream_url, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'VNLP Sample Camera',
    'student',
    'offline-import',
    NULL,
    TRUE
)
ON CONFLICT (id) DO NOTHING;

-- Vehicle events
INSERT INTO vehicle_events (id, camera_id, timestamp, direction, vehicle_type, track_id)
VALUES
    ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 minute',  'in', 'motorbike', '4_1198_0_18u19495_469_149_615_264'),
    ('22222222-2222-2222-2222-222222222222', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '2 minutes', 'in', 'motorbike', '8_2925_0_30m86121_231_57_389_178'),
    ('33333333-3333-3333-3333-333333333333', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '3 minutes', 'in', 'motorbike', '5_820_0_29V73283_413_1_574_118'),
    ('44444444-4444-4444-4444-444444444444', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '4 minutes', 'in', 'motorbike', '7_2815_0_29t164988_406_172_529_278'),
    ('55555555-5555-5555-5555-555555555555', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '5 minutes', 'in', 'motorbike', '9_3392_0_29m119166_268_199_399_317'),
    ('66666666-6666-6666-6666-666666666666', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '6 minutes', 'in', 'motorbike', '8_3083_0_29l501163_223_127_377_268'),
    ('77777777-7777-7777-7777-777777777777', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '7 minutes', 'in', 'motorbike', '6_1181_0_29E111033_482_29_626_161'),
    ('88888888-8888-8888-8888-888888888888', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '8 minutes', 'in', 'motorbike', '9_3676_0_29g148508_343_97_453_184'),
    ('99999999-9999-9999-9999-999999999999', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '9 minutes', 'in', 'motorbike', '2_720_0_29m126840_233_124_361_232'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '00000000-0000-0000-0000-000000000001', NOW() - INTERVAL '10 minutes','in', 'motorbike', '8_2992_0_29g174621_312_90_448_207');

-- Plate reads (OCR)
INSERT INTO plate_reads (id, event_id, plate_text, confidence, snapshot_url, crop_url, ocr_status)
VALUES
    ('b1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', '18U19495', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/4_1198_0_18u19495_469_149_615_264.jpg', NULL, 'success'),
    ('b2222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', '30M86121', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/8_2925_0_30m86121_231_57_389_178.jpg', NULL, 'success'),
    ('b3333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', '29V73283', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/5_820_0_29V73283_413_1_574_118.jpg', NULL, 'success'),
    ('b4444444-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444444', '29T164988', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/7_2815_0_29t164988_406_172_529_278.jpg', NULL, 'success'),
    ('b5555555-5555-5555-5555-555555555555', '55555555-5555-5555-5555-555555555555', '29M119166', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/9_3392_0_29m119166_268_199_399_317.jpg', NULL, 'success'),
    ('b6666666-6666-6666-6666-666666666666', '66666666-6666-6666-6666-666666666666', '29L501163', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/8_3083_0_29l501163_223_127_377_268.jpg', NULL, 'success'),
    ('b7777777-7777-7777-7777-777777777777', '77777777-7777-7777-7777-777777777777', '29E111033', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/6_1181_0_29E111033_482_29_626_161.jpg', NULL, 'success'),
    ('b8888888-8888-8888-8888-888888888888', '88888888-8888-8888-8888-888888888888', '29G148508', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/9_3676_0_29g148508_343_97_453_184.jpg', NULL, 'success'),
    ('b9999999-9999-9999-9999-999999999999', '99999999-9999-9999-9999-999999999999', '29M126840', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/2_720_0_29m126840_233_124_361_232.jpg', NULL, 'success'),
    ('baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '29G174621', 0.85, 'file:///G:/TTMT/datn/data/processed/vnlp_xe_may_sample10/images/8_2992_0_29g174621_312_90_448_207.jpg', NULL, 'success');

COMMIT;
