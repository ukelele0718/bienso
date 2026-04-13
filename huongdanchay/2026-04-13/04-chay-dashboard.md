# 04 — Chạy Dashboard

Dashboard là React + TypeScript (Vite), hiển thị dữ liệu từ Backend API.

## Yêu cầu

- Backend đang chạy trên `:8000` (xem [03-chay-backend.md](03-chay-backend.md))
- Node.js 18+ và npm đã cài

## Khởi động

```bash
cd apps/dashboard
npm install    # chỉ cần lần đầu
npm run dev
```

Kết quả mong đợi:
```
VITE v6.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

## Mở browser

Truy cập http://localhost:5173

### Dashboard hiển thị

- **Realtime Stats**: tổng xe vào, xe ra, tỉ lệ OCR thành công
- **Events list**: danh sách sự kiện (biển số, loại xe, thời gian, confidence)
- **Accounts**: biển số unique, số dư, trạng thái đăng ký
- **Barrier Actions**: quyết định barrier (open/hold), nút verify
- **Traffic Stats**: biểu đồ lưu lượng theo giờ

## Cấu hình API URL

Mặc định dashboard kết nối `http://localhost:8000`. Nếu backend chạy ở URL khác:

```bash
VITE_API_BASE_URL=http://192.168.1.100:8000 npm run dev
```

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|-----------|
| Dashboard trắng, console báo CORS | Backend chưa có CORS middleware | Đảm bảo dùng code mới nhất (đã thêm CORS) |
| "Network Error" khi fetch | Backend chưa chạy | Start backend trước (bước 03) |
| Dashboard hiện nhưng không có data | Chưa gửi event nào | Chạy AI Engine (bước 05) hoặc POST event thủ công |

## Build production (tùy chọn)

```bash
npm run build
# Output: apps/dashboard/dist/
# Serve bằng bất kỳ static server nào
```

Tiếp → [05-chay-ai-engine.md](05-chay-ai-engine.md)
