# Plan chụp ảnh cho báo cáo

Lưu ảnh vào: reports/2026-04-13/images/

## Ảnh cần vẽ (diagram)

| Hình | Mô tả | Cách tạo |
|------|-------|----------|
| 1 | Sơ đồ kiến trúc tổng thể 4 lớp | Vẽ draw.io hoặc Mermaid |
| 2 | ER Diagram cơ sở dữ liệu (10 bảng) | Vẽ dbdiagram.io, tham khảo apps/backend/app/models.py |
| 3 | Sequence diagram luồng create_event 7 bước | Vẽ Mermaid hoặc draw.io |

## Ảnh chụp demo AI Engine

Activate venv trước mỗi lệnh:
```powershell
& .venv\Scripts\Activate.ps1
```

### Hình 4: Detection — bbox xanh quanh xe
```powershell
# Chạy backend trước
$env:APP_DATABASE_URL = "sqlite+pysqlite:///./demo.db"
$env:PYTHONPATH = "apps/backend"
python -m uvicorn app.main:app --port 8000

# Rồi chạy demo visual (terminal khác)
python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --camera cam_gate_1 --visual
```
Chụp frame có nhiều xe với bbox xanh.

### Hình 5: Tracking — ID xe hiển thị trên bbox
Cùng lệnh trên, chụp frame thấy ID (ví dụ "ID3 car") trên bbox xanh.

### Hình 6: Plate detection — bbox đỏ quanh biển số
Cùng lệnh trên, chụp frame có bbox đỏ quanh vùng biển số.

### Hình 7: OCR — text vàng kết quả đọc biển
Cùng lệnh trên, chụp frame có text vàng trên nền đen (ví dụ "36H82613 90%").

## Ảnh chụp API

### Hình 8: API response — curl POST event
```powershell
curl -X POST http://localhost:8000/api/v1/events -H "Content-Type: application/json" -d '{"camera_id":"cam_gate_1","timestamp":"2026-04-14T08:00:00Z","direction":"in","vehicle_type":"motorbike","track_id":"track_1","plate_text":"29A12345","confidence":0.85}'
```
Chụp terminal hiển thị JSON response.

## Ảnh chụp Dashboard

### Hình 9: Dashboard — trang tổng quan
Mở http://localhost:5173 (sau khi chạy backend + demo), chụp full page.

### Hình 10: Dashboard — accounts + verify queue
Cuộn xuống phần accounts table và verify section, chụp.

### Hình 11: Demo visual — cửa sổ OpenCV hiển thị realtime
Chụp cửa sổ "E2E Demo" khi đang chạy visual mode.
