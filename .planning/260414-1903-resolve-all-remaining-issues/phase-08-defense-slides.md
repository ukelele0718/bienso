# Phase 08: Slide Bảo vệ Đồ án — Plan Chi tiết

**Ưu tiên**: 🟠 Trung bình — bắt buộc cho buổi bảo vệ
**Trạng thái**: ⬜ Pending
**Phụ thuộc**: Phase 07 (Báo cáo hoàn thiện) — nhưng có thể bắt đầu song song
**Ước tính**: ~4 giờ

---

## Thông tin đồ án

- **Đề tài**: Thiết kế hệ thống quản lý phương tiện ra/vào cơ sở giáo dục đào tạo thông qua nhận diện biển số xe
- **Sinh viên**: Hà Văn Quang (20210718), Nguyễn Hữu Cần (20223882)
- **GVHD**: Nguyễn Tiến Dũng
- **Trường**: Đại học Bách khoa Hà Nội
- **Thời lượng thuyết trình**: ~15-20 phút + 5-10 phút Q&A

---

## Cấu trúc Slide chi tiết (27 slides)

### PHẦN 1: MỞ ĐẦU (4 slides) — ~2 phút

#### Slide 1: Trang bìa
- Logo ĐHBK Hà Nội
- Tên đề tài (tiếng Việt)
- Sinh viên: Hà Văn Quang — 20210718, Nguyễn Hữu Cần — 20223882
- GVHD: Nguyễn Tiến Dũng
- Ngày bảo vệ: ___/___/2026
- **Layout**: Center-aligned, formal, trắng/xanh dương

#### Slide 2: Đặt vấn đề
- Nhu cầu: Quản lý xe ra/vào tại cơ sở giáo dục quy mô lớn
- Vấn đề: Thủ công, chậm, dễ sai sót, khó thống kê
- Giải pháp: Hệ thống tự động nhận diện biển số xe + quản lý online
- **Hình minh họa**: Ảnh cổng trường hoặc icon xe + camera
- **Ghi chú cho người trình bày**: Nêu bối cảnh ĐHBK — nhiều cổng, lưu lượng cao

#### Slide 3: Mục tiêu & Phạm vi
- Mục tiêu:
  - Xây dựng prototype E2E: camera → AI → backend → dashboard
  - Nhận diện biển số xe Việt Nam (1 hàng + 2 hàng)
  - Quản lý tài khoản, giao dịch, thống kê realtime
- Phạm vi prototype:
  - 1-2 camera (IN/OUT)
  - Xe máy + ô tô
  - SQLite dev / PostgreSQL production
- **Layout**: 2 cột (Mục tiêu | Phạm vi)

#### Slide 4: Nội dung trình bày
- 1. Tổng quan kiến trúc
- 2. Thiết kế hệ thống
- 3. Xây dựng các module
- 4. Thực nghiệm & đánh giá
- 5. Kết luận & hướng phát triển
- **Layout**: Numbered list, mỗi mục có icon

---

### PHẦN 2: TỔNG QUAN KIẾN TRÚC (3 slides) — ~3 phút

#### Slide 5: Kiến trúc tổng thể 4 lớp
- **Hình**: `hinh-01-architecture.png` (full slide, caption bên dưới)
- Lớp 1: Đầu vào (Video file / Camera IP)
- Lớp 2: AI Engine (YOLOv8n → SORT → LP_detector → LP_ocr)
- Lớp 3: Backend (FastAPI + PostgreSQL, 18 API endpoints)
- Lớp 4: Dashboard (React + TypeScript, realtime monitoring)
- **Ghi chú**: Highlight luồng data flow bằng mũi tên

#### Slide 6: Công nghệ sử dụng
- Bảng 2 cột:

| Lĩnh vực | Công nghệ |
|-----------|-----------|
| Vehicle Detection | YOLOv8n (COCO, 6.3MB) |
| Tracking | SORT (Kalman Filter + Hungarian) |
| Plate Detection | LP_detector.pt (YOLOv5, 41MB) |
| OCR | LP_ocr.pt (YOLOv5 char-level) |
| Backend | FastAPI + SQLAlchemy |
| Database | PostgreSQL / SQLite |
| Frontend | React + TypeScript (Vite) |
| Deployment | Docker Compose (3 services) |

- **Layout**: Bảng clean, header xanh dương

#### Slide 7: Kịch bản vận hành
- **2 flow diagrams đơn giản**:
- Xe VÀO: Camera → AI detect → OCR → Server tra cứu → Barrier OPEN → Dashboard
- Xe RA: Camera → AI detect → Server kiểm tra → Registered: OPEN / Tạm: HOLD+Verify
- **Highlight**: 6 nhánh barrier rules
- **Ghi chú**: Dùng arrows + icons, không quá nhiều text

---

### PHẦN 3: THIẾT KẾ & XÂY DỰNG (10 slides) — ~8 phút

#### Slide 8: Thiết kế CSDL
- **Hình**: `hinh-02-erd.png` (ER Diagram)
- Tóm tắt: 10 bảng, quan hệ chính
- Highlight: cameras → vehicle_events → plate_reads → accounts → transactions → barrier_actions
- **Ghi chú**: Chỉ ra 3-4 bảng quan trọng nhất, không giải thích từng bảng

#### Slide 9: Luồng xử lý create_event (7 bước)
- **Hình**: `hinh-03-sequence.png` (Sequence Diagram)
- 7 bước atomic:
  1. Auto-create camera
  2. Tạo VehicleEvent
  3. Normalize plate text
  4. Tạo PlateRead
  5. Auto-create Account (100k VND)
  6. decide_barrier() — 6 nhánh
  7. Tạo BarrierAction + Transaction
- **Ghi chú**: Nhấn mạnh "atomic" — nếu 1 bước fail → rollback

#### Slide 10: Module phát hiện phương tiện
- **Hình**: `hinh-04-detection.png` (bbox xanh quanh xe)
- Model: YOLOv8 Nano (3.2M params, 6.3MB)
- Lọc 4 class COCO: car, motorcycle, bus, truck
- Confidence threshold: 0.5
- File: `vehicle_detector.py` (61 dòng)
- **Stats**: 100% detection rate trên video test

#### Slide 11: Module theo dõi đối tượng (SORT)
- **Hình**: `hinh-05-tracking.png` (track ID trên bbox)
- Thuật toán: Kalman Filter 7 chiều + Hungarian matching (IoU)
- Params: max_age=1, min_hits=3, iou_threshold=0.3
- Kết quả: Track ID ổn định, xe được gán ID duy nhất
- File: `sort_tracker.py` (244 dòng)
- **Nguồn**: Refactor từ abewley/sort (GPL-3.0)

#### Slide 12: Module phát hiện biển số
- **Hình**: `hinh-06-plate.png` (bbox đỏ quanh biển số)
- Benchmark 2 model:

| Model | Detection Rate | Tốc độ | Kích thước |
|-------|---------------|--------|-----------|
| LP_detector.pt (YOLOv5) ← CHỌN | 100% | 32ms | 41MB |
| number_plate.pt (YOLOv8) | 100% | 48ms | 50MB |

- LP_detector nhanh hơn 33%, nhẹ hơn 18%

#### Slide 13: Module OCR biển số Việt Nam
- **Hình**: `hinh-07-ocr.png` (text vàng trên biển số)
- Phương pháp: Detect từng ký tự → Gap-based 2-row clustering
- **Diagram nhỏ** mô tả thuật toán:
  1. Detect chars → sort by Y
  2. Tìm gap lớn nhất
  3. Gap > 30% avg height → tách 2 hàng
  4. Mỗi hàng sort L→R → nối
- Post-processing (MỚI): Char mapping (0↔O, 1↔I) + Regex validate

#### Slide 14: Backend API Server
- **Hình**: `hinh-08-api.png` (curl POST + JSON response)
- FastAPI + SQLAlchemy + PostgreSQL/SQLite
- 18 REST API endpoints (bảng tóm tắt 5-6 endpoint quan trọng):
  - POST /events — Tạo event + barrier
  - GET /events — Danh sách events
  - GET /accounts — Quản lý tài khoản
  - GET /stats/realtime — Thống kê realtime
  - POST /barrier-actions/verify — Xác minh barrier
- Barrier rules: 6 nhánh quyết định (bảng nhỏ)
- **Stats**: 56/56 unit tests pass, 1.48s

#### Slide 15: Dashboard giám sát
- **Hình**: `hinh-09-dashboard.png` + `hinh-10-accounts.png` (2 screenshots)
- Layout 2 ảnh: bên trái overview, bên phải accounts
- Tính năng: Realtime stats, Events list, Accounts, Verify queue, Traffic stats
- React + TypeScript, kết nối qua fetch API
- **Stats**: 1,205 dòng TypeScript, 6 source files

#### Slide 16: Tích hợp & Deployment
- Docker Compose: 3 services (postgres, backend, dashboard)
- E2E flow: Video → AI Engine → Backend :8000 → Dashboard :5173
- CORS middleware cho cross-origin
- SQLite auto-create tables on startup (dev mode)
- **Diagram đơn giản**: 3 container boxes với arrows

#### Slide 17: Snapshot biển số (MỚI)
- Khi detect biển số → crop + padding 15% → lưu PNG
- Backend serve static files tại `/static/snapshots/`
- Dashboard hiển thị thumbnail bên cạnh event
- **Hình**: Screenshot dashboard với thumbnail biển số (nếu có)

---

### PHẦN 4: THỰC NGHIỆM & ĐÁNH GIÁ (6 slides) — ~5 phút

#### Slide 18: Bộ dữ liệu
- VNLP Dataset: 37,297 ảnh biển số Việt Nam
  - one_row: 19,086 | two_rows: 12,618 | xe_may: 5,593
- Video test: trungdinh22-demo.mp4 (600×800, 10fps, 30s)
- **Hình**: Grid 4 ảnh mẫu biển số VN (1 hàng, 2 hàng, xe máy, ô tô)

#### Slide 19: Kết quả Plate Detection + OCR Baseline
- Plate Detection: 100% (20/20 ảnh)
- OCR Baseline (50 ảnh):

| Metric | Kết quả |
|--------|---------|
| Detection rate | 96.0% |
| Exact match | 33.3% |
| Char accuracy | 51.0% |
| Avg confidence | 0.82 |
| Tốc độ | 15.4 ảnh/s |

- Phân tích lỗi: thừa/thiếu ký tự, nhầm hình dáng (0↔O), biển mờ

#### Slide 20: Cải thiện OCR — Post-processing (MỚI)
- Char mapping position-aware: O→0, I→1, S→5, B→8 (tùy vị trí)
- Regex validation: 4 patterns biển VN
- **Bảng so sánh before/after** (điền sau khi chạy Phase 03):

| Metric | Baseline | Sau post-processing |
|--------|---------|-------------------|
| Exact match | 33.3% | ___ % |
| Char accuracy | 51.0% | ___ % |

- 33 unit tests pass

#### Slide 21: Kết quả E2E Video Test
- Lần 1 (300 frames): 2 biển unique, 2.1 FPS, 140s
- Lần 2 (101 frames): 1 biển unique (36H82613), 1.6 FPS, 62.1s
- **Hình**: `hinh-11-visual.png` (detection realtime)
- Known issues:
  - Duplicate events do SORT tạo track mới
  - Vehicle type mismatch (motorbike vs car) — đã cải thiện
  - FPS thấp trên CPU — cần GPU

#### Slide 22: Backend & Dashboard Tests
- Unit tests: 56/56 pass (100%), 1.48s
- API smoke test: 5/5 pass
- Dashboard API: 7/7 pass
- Barrier logic: 8 test cases, 6 nhánh — all pass
- Dashboard code review: 2 bugs found + fixed
- **Layout**: Checklist ✅ format

#### Slide 23: Tổng hợp kết quả

| Hạng mục | Pass | Fail | Chưa test |
|----------|------|------|-----------|
| AI Engine → Backend | 1/1 | 0 | 0 |
| Backend API | 5/5 | 0 | 0 |
| Dashboard API | 7/7 | 0 | 0 |
| OCR Post-processing | 33/33 | 0 | 0 |
| Backend Unit Tests | 56/56 | 0 | 0 |
| Known issues | 1/3 | 1 (dup) | 1 (FPS) |

---

### PHẦN 5: KẾT LUẬN (4 slides) — ~2 phút

#### Slide 24: Kết quả đạt được
- ✅ Pipeline E2E hoạt động: Video → AI → Backend → Dashboard
- ✅ Nhận diện biển số VN (1 hàng + 2 hàng)
- ✅ Backend 18 API + barrier rules (6 nhánh)
- ✅ Dashboard realtime monitoring
- ✅ Docker deployment (3 services)
- ✅ OCR post-processing (char mapping + regex)
- ✅ Snapshot crop biển số
- **Thống kê**: 5,799 dòng code, 89 unit tests, 11 hình, 33 tài liệu tham khảo

#### Slide 25: Hạn chế
- OCR accuracy thấp (33.3% exact match) — cần cải thiện model
- FPS chậm trên CPU (1.6-2.1) — cần GPU
- Chỉ test trên 1 video biển VN
- Chưa full eval trên toàn bộ 37,297 ảnh
- Dashboard chưa test toàn diện trên browser
- Chưa lưu ảnh minh chứng (snapshot) khi chạy demo cũ

#### Slide 26: Hướng phát triển
- **Ngắn hạn**:
  - Full OCR evaluation trên 3,731+ ảnh
  - Regex post-processing nâng accuracy
  - Test dashboard đầy đủ trên browser
- **Trung hạn**:
  - GPU acceleration (kỳ vọng 10-15 FPS)
  - Nhiều camera đồng thời, xử lý song song
  - WebSocket realtime push (thay polling)
- **Dài hạn**:
  - Edge deployment (Jetson Nano)
  - Cải thiện OCR: deblur, perspective correction
  - Tích hợp quản lý đăng ký phương tiện nhà trường

#### Slide 27: Q&A
- "Cảm ơn thầy/cô đã lắng nghe"
- Thông tin liên hệ (optional)
- Mã nguồn: https://github.com/ukelele0718/bienso
- **Layout**: Clean, professional, centered

---

## Tài nguyên có sẵn

### Hình ảnh (11 files tại `reports/2026-04-13/images/`)

| File | Nội dung | Dùng cho slide |
|------|---------|---------------|
| `hinh-01-architecture.png` | Kiến trúc 4 lớp | Slide 5 |
| `hinh-02-erd.png` | ER Diagram 10 bảng | Slide 8 |
| `hinh-03-sequence.png` | Sequence create_event | Slide 9 |
| `hinh-04-detection.png` | Vehicle detection bbox | Slide 10 |
| `hinh-05-tracking.png` | SORT tracking ID | Slide 11 |
| `hinh-06-plate.png` | Plate detection bbox | Slide 12 |
| `hinh-07-ocr.png` | OCR text trên biển | Slide 13 |
| `hinh-08-api.png` | API curl + response | Slide 14 |
| `hinh-09-dashboard.png` | Dashboard overview | Slide 15 |
| `hinh-10-accounts.png` | Accounts + verify | Slide 15 |
| `hinh-11-visual.png` | Visual mode detection | Slide 21 |

### Số liệu từ test reports

| Metric | Giá trị | Nguồn |
|--------|---------|-------|
| Detection rate (plate) | 100% (20/20) | benchmark |
| OCR exact match | 33.3% (16/48) | baseline eval |
| OCR char accuracy | 51.0% | baseline eval |
| E2E FPS (CPU) | 1.6-2.1 | test 1+2 |
| Backend tests | 56/56 pass | pytest |
| OCR post-process tests | 33/33 pass | pytest |
| API endpoints | 18 | main.py |
| DB tables | 10 | models.py |
| Total code | 5,799 dòng | stats |
| Git commits | 74+ | git log |

---

## Yêu cầu kỹ thuật

### Format
- **Tool**: PowerPoint (.pptx) — tạo bằng python-pptx hoặc thủ công
- **Template**: Minimalist, trắng + xanh dương ĐHBK (#003366)
- **Font**: Calibri (heading) + Calibri Light (body), hoặc Arial
- **Font size**: Title 28-32pt, Body 18-22pt, Caption 14pt
- **Aspect ratio**: 16:9

### Quy tắc slide
- Mỗi slide: ≤6 bullet points
- Mỗi bullet: ≤25 từ
- Hình ảnh chiếm ≥40% diện tích slide (khi có)
- Không đọc nguyên văn slide — slide chỉ là gợi ý
- Background: trắng hoặc gradient nhạt, không pattern rối

### Speaker notes
- Mỗi slide kèm speaker notes 3-5 câu
- Ghi thời gian ước tính (tổng ~17 phút)
- Ghi câu hỏi thầy có thể hỏi + gợi ý trả lời

---

## Chuẩn bị Demo (2 phương án)

### Phương án A: Video demo (khuyến nghị — an toàn)
1. Quay screen recording toàn bộ E2E flow
2. Nội dung:
   - Terminal 1: `uvicorn app.main:app` (backend start)
   - Terminal 2: `npm run dev` (dashboard start)
   - Terminal 3: `python scripts/run-e2e-demo.py --visual` (AI engine + video)
   - Browser: Dashboard hiển thị events realtime
3. Thời lượng: 60-90 giây
4. Resolution: 1080p, chèn vào Slide 2 hoặc trước Slide 18
5. **Tool**: OBS Studio hoặc Windows Game Bar

### Phương án B: Demo live (rủi ro nhưng ấn tượng hơn)
1. Chuẩn bị laptop chạy sẵn Docker / local services
2. Đảm bảo WiFi ổn định tại phòng bảo vệ
3. Backup: có video demo sẵn nếu live fail
4. Script chạy demo:
   ```bash
   # Terminal 1
   cd apps/backend && uvicorn app.main:app --port 8000
   # Terminal 2
   cd apps/dashboard && npm run dev
   # Terminal 3
   cd . && python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --visual --max-frames 100
   ```

---

## Câu hỏi thầy có thể hỏi + Gợi ý trả lời

### Câu hỏi kỹ thuật

**Q1: Tại sao chọn YOLOv8 Nano thay vì model lớn hơn?**
> Trả lời: YOLOv8n nhẹ (6.3MB, 3.2M params), phù hợp edge deployment (Jetson Nano). Trong prototype, detect xe không cần model lớn vì đối tượng rõ ràng. Nếu cần accuracy cao hơn → upgrade YOLOv8s/m.

**Q2: OCR accuracy 33.3% có thấp không? Làm sao cải thiện?**
> Trả lời: 33.3% là baseline chưa post-processing. Với char mapping + regex → kỳ vọng 50-60%. Hướng cải thiện: padding crop, perspective correction, augmented training, ensemble model.

**Q3: Tại sao dùng SORT thay vì DeepSORT?**
> Trả lời: SORT đủ cho bài toán (xe di chuyển chậm, ít occlusion). SORT nhanh 260Hz vs DeepSORT 30-40Hz. Trong hệ thống giám sát cổng, xe đi thẳng không cần re-ID.

**Q4: Hệ thống xử lý thế nào khi camera mất kết nối?**
> Trả lời: Hiện prototype chưa xử lý case này. Hướng phát triển: health check camera định kỳ, cảnh báo trên dashboard, retry connection.

**Q5: Barrier rule "temp_out_requires_verify" hoạt động thế nào?**
> Trả lời: Xe tạm (lần đầu vào) khi ra cổng → barrier HOLD. Nhân viên verify trên dashboard → chọn OPEN/CLOSE. Mục đích: ngăn xe lạ ra vào tự do.

### Câu hỏi chung

**Q6: Phân công công việc thế nào?**
> Trả lời: (Điền theo thực tế phân công giữa Quang và Cần)

**Q7: Nếu có thêm thời gian, sẽ ưu tiên cải thiện gì?**
> Trả lời: (1) Full OCR eval 3,731 ảnh, (2) GPU benchmark, (3) Multi-camera support, (4) WebSocket realtime.

---

## Phân công thực hiện slide

| Slide | Nội dung | Người làm | Ghi chú |
|-------|---------|-----------|---------|
| 1-4 | Mở đầu | ___ | Logo trường, layout chuẩn |
| 5-7 | Tổng quan kiến trúc | ___ | Dùng hinh-01 |
| 8-9 | Thiết kế DB + Sequence | ___ | Dùng hinh-02, hinh-03 |
| 10-13 | AI modules (detect, track, OCR) | ___ | Dùng hinh-04~07 |
| 14-17 | Backend, Dashboard, Docker | ___ | Dùng hinh-08~10 |
| 18-23 | Thực nghiệm + đánh giá | ___ | Bảng số liệu |
| 24-27 | Kết luận + Q&A | ___ | Cùng review |
| Demo | Video demo E2E | ___ | Quay bằng OBS |

---

## Timeline thực hiện

| Bước | Công việc | Ước tính | Phụ thuộc |
|------|----------|---------|-----------|
| 1 | Tạo template .pptx (bìa, color scheme, fonts) | 30 phút | - |
| 2 | Slides 1-7: Mở đầu + Kiến trúc | 45 phút | Bước 1 |
| 3 | Slides 8-17: Thiết kế + Xây dựng | 1.5 giờ | Bước 1, hình ảnh |
| 4 | Slides 18-23: Thực nghiệm | 45 phút | Phase 03 eval data |
| 5 | Slides 24-27: Kết luận + Q&A | 15 phút | - |
| 6 | Quay video demo | 30 phút | Backend+Dashboard chạy |
| 7 | Review + dry-run thuyết trình | 30 phút | Tất cả slides |
| **Tổng** | | **~4.5 giờ** | |

---

## Tiêu chí hoàn thành

- [ ] 27 slides hoàn chỉnh (.pptx)
- [ ] 11 hình ảnh đã nhúng đúng slide
- [ ] Speaker notes cho mỗi slide (3-5 câu)
- [ ] Demo video 60-90s (hoặc script demo live)
- [ ] Dry-run thuyết trình ≤20 phút
- [ ] Review bởi cả 2 thành viên
- [ ] Câu hỏi Q&A chuẩn bị 7+ câu

---

## Rủi ro

| Rủi ro | Xác suất | Ảnh hưởng | Giải pháp |
|--------|----------|----------|-----------|
| Số liệu OCR eval chưa có (Phase 03) | Cao | Slide 20 trống | Dùng số baseline, ghi "đang đánh giá" |
| Demo live fail tại buổi bảo vệ | TB | Mất điểm trình bày | Luôn có video backup |
| Slide quá nhiều text | TB | Khó theo dõi | Review: mỗi bullet ≤25 từ |
| Thời gian trình bày > 20 phút | Thấp | Bị cắt ngang | Dry-run + timing trước |
