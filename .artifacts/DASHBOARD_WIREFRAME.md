# Dashboard Wireframe (v1)
## Scope: realtime + tra cứu + số dư

---

## 1) Màn hình tổng quan (Realtime)

### Layout
- Header: tên hệ thống, trạng thái camera, thời gian hiện tại.
- Row KPI cards:
  - Tổng lượt vào hôm nay
  - Tổng lượt ra hôm nay
  - OCR success rate
  - Số event chưa đọc biển
- Main content chia 2 cột:
  - Cột trái (70%): Bảng sự kiện realtime
  - Cột phải (30%): Live summary + cảnh báo OCR low confidence

### Bảng sự kiện realtime
Cột đề xuất:
- Thời gian
- Ảnh snapshot
- Biển số
- Loại xe
- Hướng (in/out)
- Confidence
- Số dư sau giao dịch
- Action (xem chi tiết)

---

## 2) Màn hình tra cứu sự kiện

### Bộ lọc
- Biển số (text)
- Khoảng thời gian (from/to)
- Hướng (in/out)
- Loại xe (motorbike/car)
- OCR status (success/failed/partial)

### Kết quả
- Table phân trang + export CSV.
- Nhấn vào dòng để mở panel chi tiết:
  - ảnh full frame
  - ảnh crop biển số
  - raw OCR text
  - normalized text
  - metadata event

---

## 3) Màn hình tài khoản biển số (số dư)

### Tìm kiếm
- Input biển số + nút tra cứu

### Thông tin chính
- Biển số
- Số dư hiện tại (có thể âm)
- Số lượt in/out trong ngày

### Lịch sử giao dịch
Cột:
- Thời gian
- Loại giao dịch (`init`, `event_charge`, `manual_adjust`)
- Số tiền (+/-)
- Số dư trước
- Số dư sau
- Liên kết đến event liên quan

---

## 4) Màn hình thống kê lưu lượng

### Biểu đồ
- Lưu lượng theo giờ (line/bar)
- Lưu lượng theo ngày
- Tỉ lệ xe máy/ô tô
- Tỉ lệ OCR success theo khung giờ

### Bộ lọc
- Range thời gian
- Kịch bản cổng (sinh viên/giảng viên)

---

## 5) UX states bắt buộc
- Loading state cho mọi API call.
- Empty state khi không có dữ liệu.
- Error state kèm nút retry.
- Badge cảnh báo cho confidence thấp.

---

## 6) Wireframe ASCII (màn realtime)

```text
+--------------------------------------------------------------------------------+
| Vehicle LPR Dashboard         Camera: ONLINE          Time: 2026-03-27 10:30  |
+--------------------------------------------------------------------------------+
| [In Today: 132] [Out Today: 127] [OCR Success: 91.3%] [Unreadable: 17]        |
+-------------------------------------------+------------------------------------+
| Realtime Events                           | Live Summary / Alerts              |
|-------------------------------------------|------------------------------------|
| time  | plate     | type | dir | conf |bal| - Low confidence events            |
| 10:29 | 29A-12345 | MB   | IN  |0.94 |86k| - OCR failed last 5 minutes        |
| 10:29 | 30F-88888 | CAR  | OUT |0.88 |-2k| - System health: OK                |
| ...                                       |                                    |
+-------------------------------------------+------------------------------------+
```

---

## 7) Mapping với API
- Realtime cards: `GET /stats/realtime`
- Realtime table: `GET /events`
- Search page: `GET /events` với query filters
- Balance card: `GET /accounts/{plate_text}`
- Transaction table: `GET /accounts/{plate_text}/transactions`
- Traffic charts: `GET /stats/traffic`

---

## 8) Yêu cầu typed frontend
- Toàn bộ response map vào TypeScript interfaces.
- Không dùng `any` trong modules chính.
- Tách `types.ts`, `api.ts`, `features/*` rõ ràng.
