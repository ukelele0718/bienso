# Plan test luồng thực tế + chụp ảnh cho báo cáo

⚠ GHI NHỚ: Sau khi test xong, CẬP NHẬT TIẾN ĐỘ ở đầu file bao-cao-dinh-ky-tien-do.md
(bảng 16 tuần và trạng thái tổng quan) cho đúng thực tế.

## Chuẩn bị

```powershell
# Terminal 1: Backend (với logging)
$env:APP_DATABASE_URL = "sqlite+pysqlite:///./test-flow.db"
$env:PYTHONPATH = "apps/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

# Terminal 2: Dashboard
cd apps/dashboard
npm run dev

# Terminal 3: AI Engine (activate venv 3.11 trước)
& .venv\Scripts\Activate.ps1
```

Xóa DB cũ trước mỗi lần test: `del test-flow.db`

## Test 1: AI Engine → Backend (có logging)

```powershell
python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --camera cam_gate_1 --visual --max-frames 100
```

Quan sát:
- [ ] Cửa sổ visual hiện bbox xanh (xe), đỏ (biển), vàng (OCR)
- [ ] Terminal 3 in [detect] và [sent] cho mỗi biển số
- [ ] Terminal 1 (backend) in log POST /api/v1/events 201
- [ ] Ghi lại: bao nhiêu plate detect, bao nhiêu đúng/sai loại xe

Chụp: Hình 4 (detection), 5 (tracking), 6 (plate), 7 (OCR), 11 (visual)

## Test 2: Backend API thủ công

```powershell
# Health
curl http://localhost:8000/health

# POST event
curl -X POST http://localhost:8000/api/v1/events -H "Content-Type: application/json" -d '{"camera_id":"cam_gate_1","timestamp":"2026-04-14T08:00:00Z","direction":"in","vehicle_type":"motorbike","track_id":"track_test","plate_text":"29A12345","confidence":0.85}'

# GET events
curl http://localhost:8000/api/v1/events

# GET accounts
curl http://localhost:8000/api/v1/accounts

# GET realtime stats
curl http://localhost:8000/api/v1/stats/realtime
```

Quan sát:
- [ ] Health trả {"status":"ok"}
- [ ] POST event trả JSON với barrier_action, registration_status
- [ ] GET events liệt kê events vừa tạo
- [ ] GET accounts có account cho biển vừa POST

Chụp: Hình 8 (API response)

## Test 3: Dashboard từng chức năng

Mở http://localhost:5173 sau khi chạy Test 1 + Test 2.

- [ ] Realtime events: hiện danh sách events — GHI KẾT QUẢ: ___
- [ ] Realtime stats (tổng in/out, OCR rate) — GHI KẾT QUẢ: ___
- [ ] Accounts list (phân trang, tìm kiếm) — GHI KẾT QUẢ: ___
- [ ] Account detail (click 1 account, xem transactions) — GHI KẾT QUẢ: ___
- [ ] Verify queue (xem barrier holds, thử verify) — GHI KẾT QUẢ: ___
- [ ] Traffic stats (biểu đồ) — GHI KẾT QUẢ: ___
- [ ] Import summary — GHI KẾT QUẢ: ___

Với mỗi mục:
- OK → ghi "OK, hoạt động đúng"
- Sai → ghi cụ thể sai gì
- Chưa test được → ghi "chưa test, lý do: ..."

Chụp: Hình 9 (tổng quan), 10 (accounts + verify)

## Test 4: Kiểm tra vấn đề đã biết

- [ ] Sai loại xe (motorbike vs car cho cùng biển) — xảy ra không?
- [ ] Duplicate events (cùng biển nhiều lần) — deduplicate hoạt động?
- [ ] FPS thực tế trên máy hiện tại — ghi số: ___

## Sau khi test

1. Điền kết quả vào các ô GHI KẾT QUẢ ở trên
2. Cập nhật bao-cao-dinh-ky-tien-do.md:
   - Bảng tiến độ 16 tuần ở mục 1.1
   - Trạng thái dashboard ở mục 3.3.2
   - Số liệu thực nghiệm ở chương 4
3. Commit + push
