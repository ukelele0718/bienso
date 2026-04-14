# Test Summary — 2026-04-14

## Test 1: AI Engine → Backend (100 frames)

| Metric | Kết quả |
|--------|---------|
| Video | trungdinh22-demo.mp4 (600x800, 10fps) |
| Frames processed | 101 |
| Thời gian | 62.1s |
| FPS | 1.6 (CPU) |
| Raw events | 6 |
| Unique sent | 2 |
| Plates detected | 36H82613 (car) |
| Deduplicate | Hoạt động: 2 track combos → 2 events sent |

Kết quả: OK — pipeline detect + send event hoạt động.
Vấn đề: FPS thấp (1.6) trên CPU.

## Test 2: Backend API thủ công

| Test | Kết quả | Chi tiết |
|------|---------|---------|
| 2.1 Health | OK | {"status":"ok"} |
| 2.2 POST event | OK | barrier=open, status=temporary_registered |
| 2.3 GET events | OK | 1 event (trước AI), sau đó 3 events |
| 2.4 GET accounts | OK | 29A12345 balance=98,000 |
| 2.5 Realtime stats | OK | total_in=1, ocr_rate=100% |

Kết quả: All 5/5 pass.

## Test 3: Dashboard API endpoints

| Endpoint | Kết quả | Chi tiết |
|----------|---------|---------|
| 3.1 Events list | OK | 3 events hiển thị |
| 3.2 Realtime stats | OK | in=3, out=0, ocr=100% |
| 3.3 Accounts list | OK | 2 accounts (36H82613, 29A12345) |
| 3.4 Account detail + txns | OK | 3 transactions (init + 2 charges) |
| 3.5 Barrier actions | OK | 3 actions, all open, no verify needed |
| 3.6 Traffic stats | OK | 2 time buckets |
| 3.7 OCR success rate | OK | 100% |

Kết quả: All 7/7 pass.
Lưu ý: Đây là test API trả data đúng. Dashboard UI chưa test thủ công (cần mở browser).

## Test 4: Known Issues

| Issue | Kết quả |
|-------|---------|
| Vehicle type mismatch | OK — không xảy ra lần này (cả 2 plate consistent) |
| Duplicate events | WARNING — 36H82613 có 2 events (2 track IDs khác nhau) |
| FPS | 1.6 FPS (CPU only) |

## Tổng hợp

| Hạng mục | Pass | Fail | Chưa test |
|----------|------|------|-----------|
| AI Engine → Backend | 1/1 | 0 | 0 |
| Backend API | 5/5 | 0 | 0 |
| Dashboard API | 7/7 | 0 | 0 |
| Known issues | 1/3 | 1 (dup) | 1 (FPS cần GPU) |
| **Tổng** | **14/16** | **1** | **1** |

## Files tạo ra

- test1-ai-engine-log.txt
- test2-api-manual-log.txt
- test3-dashboard-api-log.txt
- test4-known-issues-log.txt
- reports/2026-04-13/images/hinh-01-architecture.png (45KB)
- reports/2026-04-13/images/hinh-02-erd.png (122KB)
- reports/2026-04-13/images/hinh-03-sequence.png (42KB)
