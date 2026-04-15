# Phase 02: Lưu Snapshot Crop Biển Số

**Ưu tiên**: 🔴 Cao — báo cáo Ch.4 cần ảnh minh chứng, dashboard cần hiển thị
**Trạng thái**: ⬜ Pending
**Ước tính**: ~2 giờ

---

## Bối cảnh

Hiện tại `snapshot_path=None` được hardcode tại `apps/ai_engine/src/pipeline.py` (dòng 139, 217, 293).
Backend đã có field `snapshot_url` trong:
- Schema: `apps/backend/app/schemas.py:28` — `snapshot_url: str | None = None`
- Model: `apps/backend/app/models.py:50` — `snapshot_url` trong PlateRead
- API response: `apps/backend/app/response_mappers.py:21`
- Dashboard types: `apps/dashboard/src/api-types.ts:14,30`

Tức là toàn bộ stack đã sẵn sàng nhận snapshot, chỉ cần AI Engine tạo và gửi URL.

---

## Yêu cầu

### 1. Tạo snapshot trong pipeline

**File**: `apps/ai_engine/src/pipeline.py`

Khi detect được biển số + OCR thành công:
1. Crop vùng biển số từ frame gốc (dùng plate bbox + padding 15%)
2. Lưu file PNG vào thư mục `snapshots/` (configurable)
3. Đặt tên: `{timestamp}_{plate_text}_{track_id}.png`
4. Gán `snapshot_path` = đường dẫn file hoặc URL tương đối

### 2. Config

**File**: `apps/ai_engine/src/config.py`

```python
SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR", "snapshots")
SNAPSHOT_PADDING = float(os.environ.get("SNAPSHOT_PADDING", "0.15"))  # 15%
ENABLE_SNAPSHOT = os.environ.get("ENABLE_SNAPSHOT", "true").lower() == "true"
```

### 3. Serve snapshots từ backend (hoặc static)

**Option A** (đơn giản nhất): AI Engine lưu vào folder, backend serve static files
- Thêm `StaticFiles` mount trong `apps/backend/app/main.py`
- `snapshot_url` = `/static/snapshots/{filename}`

**Option B**: AI Engine gửi base64 kèm event payload → backend lưu
- Phức tạp hơn, không cần thiết cho prototype

→ **Chọn Option A**

### 4. Update event_sender

**File**: `apps/ai_engine/src/event_sender.py:38`

Hiện tại: `"snapshot_url": event.snapshot_path`
→ Khi `snapshot_path` không còn None, URL sẽ tự động được gửi.

### 5. Dashboard hiển thị snapshot

**File**: `apps/dashboard/src/main.tsx`

Trong bảng events, nếu `snapshot_url` tồn tại → hiển thị thumbnail ảnh biển số.

---

## Files cần sửa

| File | Hành động |
|------|----------|
| `apps/ai_engine/src/pipeline.py` | Thêm logic crop + save snapshot |
| `apps/ai_engine/src/config.py` | Thêm SNAPSHOT_DIR, SNAPSHOT_PADDING, ENABLE_SNAPSHOT |
| `apps/backend/app/main.py` | Mount StaticFiles cho `/static/snapshots/` |
| `apps/dashboard/src/main.tsx` | Hiển thị thumbnail snapshot trong events table |
| `scripts/run-e2e-demo.py` | Truyền snapshot config |

---

## Tiêu chí hoàn thành

- [ ] Chạy E2E demo → folder `snapshots/` có ảnh crop biển số
- [ ] Ảnh crop có padding 15%, đúng vùng biển số
- [ ] Backend trả `snapshot_url` trong API response (không còn null)
- [ ] Dashboard hiển thị thumbnail ảnh biển số bên cạnh event
- [ ] Tên file snapshot có timestamp + plate text (dễ trace)
