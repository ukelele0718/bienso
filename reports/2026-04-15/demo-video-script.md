# Demo Video Script — Hệ thống nhận diện biển số xe

**Duration**: 90 giây  
**Resolution**: 1920×1080 @ 30fps  
**Voice-over**: Tiếng Việt, giọng bình thường, pace rõ ràng  
**Recording tool**: OBS Studio

---

## Pre-recording Checklist

- [ ] **Reset DB**: `rm apps/backend/*.db`
- [ ] **Pre-seed 1 biển đã đăng ký** (để demo barrier OPEN):
  ```bash
  cd apps/backend
  PYTHONIOENCODING=utf-8 python -c "
  from app.database import SessionLocal
  from app import crud, schemas
  db = SessionLocal()
  crud.create_account(db, schemas.AccountCreate(plate_text='36H82613', balance=50000, vehicle_type='motorbike'))
  db.close()
  print('Seeded OK')
  "
  ```
- [ ] **Khởi động backend**: `cd apps/backend && uvicorn app.main:app --port 8000`
- [ ] **Khởi động dashboard**: `cd apps/dashboard && npm run dev`
- [ ] **Mở Chrome**: http://localhost:5173 — xác nhận dashboard load, events table trống
- [ ] **Test AI engine trước**: chạy `--max-frames 30` để xác nhận OpenCV window hiện và detect được biển
- [ ] **OBS setup**:
  - Scene 1 — "Intro": window capture → file `slides/bao-ve-do-an.pptx` slide 1
  - Scene 2 — "Architecture": window capture → slide kiến trúc (hoặc ảnh `reports/2026-04-13/images/hinh-01-architecture.png` mở trong Photos)
  - Scene 3 — "Split Terminal": Display capture crop → 3 terminals + Chrome (dùng Virtual Desktop hoặc layout tay)
  - Scene 4 — "AI Engine": window capture → terminal T3 + OpenCV window side-by-side
  - Scene 5 — "Dashboard": window capture → Chrome full
  - Scene 6 — "Features Tour": window capture → Chrome full
  - Scene 7 — "Outro": text/image source
- [ ] **Microphone test**: record 5s, replay, xác nhận không có noise
- [ ] **Font size terminal**: tăng lên 16–18pt để dễ đọc khi export 1080p
- [ ] **Clear terminal history**: `clear` mỗi terminal trước khi quay

---

## Shot-by-Shot Script

| # | Timing | Scene | Layout / Zoom | Action | Voice-over (đọc chính xác) | Caption/Overlay | Technical Note |
|---|--------|-------|---------------|--------|----------------------------|-----------------|----------------|
| 1 | 0:00–0:08 | **Intro** | Slide title ĐHBK (full screen) | Không cần thao tác, giữ yên | *"Đây là hệ thống quản lý phương tiện ra vào qua nhận diện biển số xe — đồ án tốt nghiệp Đại học Bách khoa Hà Nội."* | Dòng 1: Tên sinh viên / MSSV | OBS Scene 1. Mở slide trước khi bấm record |
| 2 | 0:08–0:18 | **Architecture** | Ảnh `hinh-01-architecture.png` full screen (mở trong Photos, zoom fit) | Không cần thao tác | *"Hệ thống gồm bốn lớp: camera và video đầu vào, AI Engine xử lý nhận diện, backend FastAPI lưu trữ sự kiện, và dashboard React hiển thị realtime."* | Arrow highlight: Camera → AI → Backend → Dashboard (thêm trong post) | OBS Scene 2. Zoom ảnh 100% để text rõ |
| 3 | 0:18–0:28 | **Setup terminals** | Màn hình chia 4: T1 (top-left), T2 (top-right), T3 (bottom-left), Chrome (bottom-right) | T1 đang chạy uvicorn (output "Application startup complete"). T2 đang chạy npm (output "VITE ready"). T3: con trỏ nhấp nháy, lệnh đã gõ sẵn chưa Enter. Chrome mở http://localhost:5173 dashboard trống | *"Ba service đã khởi động: backend FastAPI cổng 8000, dashboard React cổng 5173, và AI Engine sẵn sàng."* | T1 label: "Backend :8000" / T2: "Dashboard :5173" / T3: "AI Engine" / T4: "Dashboard" | OBS Scene 3. Dùng Windows Snap hoặc PowerToys FancyZones chia 4 ô |
| 4 | 0:28–0:32 | **AI Engine start** | T3 full screen (hoặc 60% màn hình, OpenCV window chiếm 40% bên phải) | Nhấn **Enter** để chạy lệnh: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --visual --max-frames 200` | *"Khởi động AI Engine với video thực tế."* | Caption: "python run-e2e-demo.py --visual" | Lệnh đã gõ sẵn từ shot 3. OpenCV window tự mở sau ~3s |
| 5 | 0:32–0:50 | **OpenCV detection** | OpenCV window full screen (hoặc 70% left), terminal log nhỏ bên phải | Không cần thao tác — để video chạy tự nhiên. Đảm bảo frame có xe và biển hiển thị rõ (frame ~50–120 thường có xe rõ nhất) | *"AI Engine phát hiện xe và đọc biển số realtime. Khung xanh là vùng xe, khung đỏ là biển số, kết quả OCR hiển thị trực tiếp trên ảnh. Độ chính xác detection đạt 99,9%, OCR exact match 92%."* | Bottom bar: "Detection: 99.9% accuracy · OCR: 92% exact match · ~20 FPS GPU" | Nếu OpenCV window nhỏ → dùng OBS transform scale up. Dừng video tại frame đẹp nếu cần |
| 6 | 0:50–0:54 | **Switch to Dashboard** | Chrome full screen, tab http://localhost:5173 | Alt+Tab sang Chrome, không cần click gì thêm | *"Chuyển sang dashboard — sự kiện đã được đẩy realtime qua WebSocket."* | Không cần overlay | OBS Scene 5. Events table lúc này đã có 2–5 rows |
| 7 | 0:54–1:05 | **Events table** | Chrome full screen — Events section | Scroll nhẹ để thấy rows. Click vào 1 row có plate "36H82613" để mở detail | *"Mỗi sự kiện ghi nhận: biển số, loại xe, hướng vào ra, trạng thái barrier, và ảnh biển số đã crop. Không cần reload trang — WebSocket push tức thì."* | Highlight row thumbnail: "Ảnh biển số crop tự động" | Đảm bảo thumbnail hiển thị (static file server đã mount) |
| 8 | 1:05–1:12 | **Stats cards** | Chrome — phần trên dashboard (cards: Total In, Total Out, OCR Rate) | Scroll lên đầu trang để thấy stats cards | *"Các chỉ số tổng hợp cập nhật theo sự kiện: tổng xe vào, xe ra, và tỷ lệ nhận diện biển số."* | Arrow chỉ vào cards (post-production) | |
| 9 | 1:12–1:17 | **Verify queue** | Chrome — Verify Queue section | Scroll xuống hoặc click nav "Verify Queue" | *"Biển số xe lạ ra cổng sẽ vào hàng đợi xác minh — nhân viên xác nhận thủ công trước khi mở barrier."* | Label: "Xác minh barrier thủ công" | |
| 10 | 1:17–1:22 | **Traffic stats** | Chrome — Traffic Stats section | Click nav "Traffic Stats" hoặc scroll | *"Thống kê lưu lượng theo giờ giúp quản lý nắm bắt giờ cao điểm."* | Label: "Biểu đồ lưu lượng theo giờ" | |
| 11 | 1:22–1:27 | **Cameras section** | Chrome — Cameras section | Click nav "Cameras" | *"Quản lý danh sách camera: tên, stream URL, và trạng thái hoạt động."* | Label: "Quản lý camera" | |
| 12 | 1:27–1:30 | **Outro** | Màn hình tối / slide cuối | Không cần thao tác | *"Cảm ơn thầy cô và hội đồng đã lắng nghe."* | Dòng 1: Tên SV — MSSV / Dòng 2: GVHD / Dòng 3: "github.com/ukelele0718/bienso" | OBS Scene 7. Fade to black 0.5s |

---

## Voice-over Full Script (đọc liền mạch)

> Đọc tốc độ bình thường, rõ ràng, không cần đọc nhanh. Các đoạn ngắt theo shot.

```
[0:00] Đây là hệ thống quản lý phương tiện ra vào qua nhận diện biển số xe —
       đồ án tốt nghiệp Đại học Bách khoa Hà Nội.

[0:08] Hệ thống gồm bốn lớp: camera và video đầu vào, AI Engine xử lý nhận diện,
       backend FastAPI lưu trữ sự kiện, và dashboard React hiển thị realtime.

[0:18] Ba service đã khởi động: backend FastAPI cổng 8000,
       dashboard React cổng 5173, và AI Engine sẵn sàng.

[0:28] Khởi động AI Engine với video thực tế.

[0:32] AI Engine phát hiện xe và đọc biển số realtime.
       Khung xanh là vùng xe, khung đỏ là biển số,
       kết quả OCR hiển thị trực tiếp trên ảnh.
       Độ chính xác detection đạt 99,9 phần trăm, OCR exact match 92 phần trăm.

[0:50] Chuyển sang dashboard — sự kiện đã được đẩy realtime qua WebSocket.

[0:54] Mỗi sự kiện ghi nhận: biển số, loại xe, hướng vào ra,
       trạng thái barrier, và ảnh biển số đã crop.
       Không cần reload trang — WebSocket push tức thì.

[1:05] Các chỉ số tổng hợp cập nhật theo sự kiện:
       tổng xe vào, xe ra, và tỷ lệ nhận diện biển số.

[1:12] Biển số xe lạ ra cổng sẽ vào hàng đợi xác minh —
       nhân viên xác nhận thủ công trước khi mở barrier.

[1:17] Thống kê lưu lượng theo giờ giúp quản lý nắm bắt giờ cao điểm.

[1:22] Quản lý danh sách camera: tên, stream URL, và trạng thái hoạt động.

[1:27] Cảm ơn thầy cô và hội đồng đã lắng nghe.
```

---

## OBS Settings

```
Output resolution : 1920×1080
FPS               : 30
Encoder           : x264 (hoặc NVENC nếu có GPU)
Rate control      : CRF 18 (chất lượng cao, file ~200MB/90s)
Audio             : Mono, 48kHz, AAC 192kbps
File format       : MKV (ghi), sau đó Remux sang MP4 trong OBS
```

### OBS Scene List

| Scene | Source | Ghi chú |
|-------|--------|---------|
| 01-Intro | Window Capture (PowerPoint/Photos) | Slide 1 |
| 02-Architecture | Window Capture (Photos/image viewer) | `hinh-01-architecture.png` |
| 03-SplitTerminal | Display Capture + crop | 4-ô layout |
| 04-AIEngine | Window Capture (OpenCV) + terminal | Side-by-side |
| 05-Dashboard | Window Capture (Chrome) | Full screen |
| 06-Outro | Image source + Text GDI+ | Text overlay |

---

## Post-production Notes (Kdenlive / DaVinci Resolve)

- **Transitions**: Cut cứng giữa các shot (không cần dissolve, trông professional hơn cho đồ án)
- **Arrows trên Architecture**: Dùng Kdenlive Title Clip vẽ 4 arrow đơn giản màu đỏ
- **Bottom bar shot 5**: Text clip "Detection: 99.9% · OCR: 92% · ~20 FPS GPU" — font Roboto 28pt, nền đen 60% opacity
- **Thumbnail highlight shot 7**: Zoom in crop 2× vào thumbnail cell trong 1s, rồi zoom out
- **Fade in/out**: 0.3s fade in đầu video, 0.5s fade to black cuối
- **Subtitles**: Export SRT từ voice-over script nếu cần embed cho YouTube

---

## Fallback — Nếu OpenCV window không mở kịp

Trường hợp AI Engine chậm start (CPU mode ~5–8s):
- Tại shot 4, sau khi Enter, đếm nhẩm 5 giây trước khi nói voice-over shot 5
- Nếu quay trước và edit sau: pause tại điểm OpenCV window hiện, cắt phần chờ trong post

## Fallback — Nếu WebSocket không push kịp trong shot 6–7

- Chạy AI Engine `--max-frames 50` trước khi bắt đầu quay (để có sẵn vài events trong DB)
- Khi quay shot 6, refresh Chrome một lần → events hiện ngay từ REST API load
- WebSocket realtime sẽ thấy ở events mới xuất hiện trong lúc quay shot 5
