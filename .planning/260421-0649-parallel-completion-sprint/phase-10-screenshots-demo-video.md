# Phase 10: Screenshots + Demo Video Recording

**Ưu tiên**: 🟢 Polish
**Branch**: main
**Worktree**: Main (user thực hiện thủ công)
**Phụ thuộc**: Tất cả Batch 1 + 2 done
**Ước tính**: 1-2 giờ

---

## Bối cảnh

Sau khi các phases khác done, cần:
1. Chụp lại screenshots dashboard (feature mới: cameras, snapshot thumbnails, WebSocket realtime)
2. Quay video demo E2E để dùng cho slide bảo vệ + báo cáo chính thức

---

## Screenshots cần chụp

| # | Tên file | Nội dung | Độ phân giải |
|---|---------|---------|--------------|
| 1 | `hinh-09-dashboard-overview-new.png` | Trang overview: 6 stats cards + events list (có thumbnail) | 1920×1080 |
| 2 | `hinh-10-accounts-verify-new.png` | Accounts list + Verify queue | 1920×1080 |
| 3 | `hinh-12-account-detail.png` | Account detail + transactions history | 1920×1080 |
| 4 | `hinh-13-cameras-section.png` | Cameras section với stream URLs | 1920×1080 |
| 5 | `hinh-14-traffic-stats.png` | Traffic stats theo giờ | 1920×1080 |
| 6 | `hinh-15-snapshot-thumbnail.png` | Close-up event row với thumbnail biển số | 800×600 |
| 7 | `hinh-16-realtime-ws.png` | Dashboard nhận event realtime qua WS (đếm giây) | 1920×1080 |

### Chuẩn bị data

Trước khi chụp:
1. Reset DB: `rm *.db`
2. Seed cameras: `INSERT INTO cameras ...` (2 cameras: 1 IN, 1 OUT, có stream_url)
3. Chạy E2E demo: ≥5 events với mix registered/temporary
4. Tạo ít nhất 1 barrier HOLD để verify queue không trống
5. Chụp bằng Chrome DevTools (F12 → Cmd+Shift+P → "screenshot full size")

---

## Demo Video

### Scenario

**Đoạn 1 (15s): Giới thiệu kiến trúc**
- Terminal split 3 phần: backend, dashboard, AI engine
- Hiển thị cmd starting services

**Đoạn 2 (30s): E2E flow**
- Start AI engine với `--visual`
- Cửa sổ OpenCV: video + detection boxes
- Chuyển qua browser: dashboard hiển thị events realtime
- Thumbnail biển số hiện bên cạnh plate

**Đoạn 3 (20s): Dashboard tương tác**
- Click account → detail page
- Click verify → barrier change
- Filter events by plate/date

**Đoạn 4 (10s): Kết luận**
- Logo trường, tên đề tài, nhóm thực hiện

**Total: ~75s (1 phút 15s)**

### Tools

- **OBS Studio** (recommend): free, quality cao, multi-source recording
- **Windows Game Bar** (Win+G): dễ hơn, chỉ 1 cửa sổ
- **Kdenlive** hoặc **DaVinci Resolve** (free): để edit/cắt ghép

### Output

- `reports/2026-04-15/demo-video-e2e.mp4` (hoặc save sang cloud nếu >100MB)
- Upload lên YouTube (unlisted) → embed link vào slide bảo vệ

---

## Files ownership

- `reports/2026-04-15/images/*.png` (screenshots mới)
- `reports/2026-04-15/demo-video-e2e.mp4` (gitignored nếu lớn)
- Update `.gitignore`: `reports/2026-04-15/demo-video-e2e.mp4`
- Update báo cáo 2026-04-15 với hình mới (rebuild .docx)

---

## Tiêu chí thành công

- [ ] 7 screenshots mới, rõ nét, đủ dữ liệu thực tế
- [ ] Video ≥60s, ≤2 phút, 1080p
- [ ] Demo đầy đủ: AI engine + backend + dashboard liên kết
- [ ] Slides bảo vệ cập nhật với link video (Slide 3 hoặc 18)

---

## Rủi ro

- Thấp — việc thủ công
- Nếu không đủ thiết bị quay: dùng Loom.com (free 5 min video)

---

## Output

- Ảnh + video
- Update slide + báo cáo references
