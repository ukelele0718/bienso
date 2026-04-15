# Phase 05: Screenshot Dashboard cho Báo cáo

**Ưu tiên**: 🟡 Trung bình — hình ảnh minh họa cho Ch.3.3 và Ch.4
**Trạng thái**: ⬜ Pending
**Phụ thuộc**: Phase 04 (Dashboard đã test + fix xong)
**Ước tính**: ~30 phút

---

## Bối cảnh

Báo cáo hiện có 11 hình. Hình 9, 10 là screenshot dashboard nhưng có thể cần chụp lại sau khi fix bugs ở Phase 04.

Hình cần chụp/cập nhật:
- Hình 9: Screenshot dashboard — trang tổng quan (stats + events)
- Hình 10: Screenshot dashboard — accounts list + verify queue

Hình mới có thể cần thêm:
- Account detail + transactions
- Traffic stats
- Snapshot biển số hiển thị trên dashboard (sau Phase 02)

---

## Yêu cầu

### 1. Chuẩn bị dữ liệu đẹp
- Chạy E2E demo để có ≥5 events, ≥3 accounts
- Đảm bảo có mix: registered + temporary, IN + OUT
- Có ít nhất 1 barrier HOLD để verify queue không trống

### 2. Chụp screenshots

| Hình | Nội dung | Tên file |
|------|---------|---------|
| Hình 9 | Trang tổng quan: stats cards + events table | `hinh-09-dashboard-overview.png` |
| Hình 10 | Accounts list + verify queue | `hinh-10-dashboard-accounts-verify.png` |
| (Mới) | Account detail + transactions | `hinh-12-dashboard-account-detail.png` |
| (Mới) | Snapshot biển số trên event | `hinh-13-dashboard-snapshot.png` |

### 3. Tiêu chuẩn ảnh
- Độ phân giải: ≥1920x1080
- Browser: Chrome, full window (không crop quá nhỏ)
- Dữ liệu thật (từ E2E demo), không mock
- Highlight vùng quan trọng nếu cần (bbox đỏ)

### 4. Lưu vào reports
- Path: `reports/2026-04-13/images/hinh-XX-*.png`
- Update file báo cáo .md với hình mới

---

## Files cần sửa

| File | Hành động |
|------|----------|
| `reports/2026-04-13/images/` | Thêm/cập nhật screenshots |
| `reports/2026-04-13/bao-cao-dinh-ky-tien-do.md` | Update references hình mới |

---

## Tiêu chí hoàn thành

- [ ] Hình 9, 10 chụp lại với data thực tế
- [ ] Ảnh rõ nét, ≥1920x1080
- [ ] Dữ liệu trên dashboard khớp với kết quả test
- [ ] File .md references đúng tên file hình
