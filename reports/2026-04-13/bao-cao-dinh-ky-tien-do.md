
BÁO CÁO ĐỊNH KỲ TIẾN ĐỘ ĐỒ ÁN TỐT NGHIỆP

THIẾT KẾ HỆ THỐNG QUẢN LÝ PHƯƠNG TIỆN RA/VÀO
CƠ SỞ GIÁO DỤC ĐÀO TẠO THÔNG QUA NHẬN DIỆN BIỂN SỐ XE

Ngày lập báo cáo: 14/04/2026
Giai đoạn báo cáo: 27/03/2026 – 13/04/2026 (Tuần 1–3)

Sinh viên thực hiện:
- _________________________________ (MSSV: _____________)
- _________________________________ (MSSV: _____________)

Giáo viên hướng dẫn: _________________________________


MỤC LỤC

1. Tổng quan tiến độ
2. Chương 1+2 — Tổng quan về bài toán quản lý phương tiện thông qua nhận diện biển số xe
3. Chương 3 — Phân tích yêu cầu và thiết kế hệ thống
4. Chương 4 — Xây dựng hệ thống quản lý phương tiện ra/vào cơ sở giáo dục
   4.1. Module đếm và theo dõi phương tiện
   4.2. Module nhận dạng biển số xe
   4.3. Server, cơ sở dữ liệu và dashboard
5. Chương 5 — Thực nghiệm, đánh giá kết quả và hướng phát triển
6. Thống kê số liệu tổng hợp
7. Kế hoạch triển khai giai đoạn tiếp theo
8. Phân công công việc
9. Đề xuất và xin ý kiến thầy
10. Phụ lục: Plan chụp ảnh chèn vào báo cáo


═══════════════════════════════════════════════════════════════

1. TỔNG QUAN TIẾN ĐỘ

═══════════════════════════════════════════════════════════════

1.1. Tiến độ theo kế hoạch 16 tuần

┌──────────┬───────────────────────────────────────┬──────────┬─────────────┐
│ Tuần     │ Nội dung theo đề cương                │ Trạng thái│ Ghi chú    │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 1-2      │ Khảo sát, chốt hướng, phạm vi        │ ✅ Xong   │ Đề cương đã │
│          │                                       │          │ được duyệt  │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 3-4      │ Chuẩn bị dữ liệu, baseline detect    │ ✅ Xong   │ VNLP 37,297 │
│          │                                       │          │ ảnh + models │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 5-6      │ Tracking, luật đếm, đo sai số        │ ⚠ 70%    │ Tracking OK │
│          │                                       │          │ Đếm: chưa   │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 7-8      │ Biển số, OCR ban đầu                  │ ✅ Xong   │ OCR 2-row   │
│          │                                       │          │ VN hoạt động│
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 9-10     │ Hậu xử lý OCR, đánh giá lỗi          │ ⚠ 50%    │ Baseline có │
│          │                                       │          │ chưa full   │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 11-12    │ Backend, CSDL, API                    │ ✅ Xong   │ 18 endpoints│
│          │                                       │          │ 10 bảng DB  │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 13-14    │ Dashboard realtime/thống kê           │ ✅ Xong   │ React + TS  │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 15       │ Tích hợp, tối ưu, kiểm thử           │ ✅ Xong   │ E2E demo    │
│          │                                       │          │ hoạt động   │
├──────────┼───────────────────────────────────────┼──────────┼─────────────┤
│ 16       │ Viết báo cáo, slide, demo             │ 🔄 Đang  │ Báo cáo này │
└──────────┴───────────────────────────────────────┴──────────┴─────────────┘

Nhận xét: Backend, Dashboard và tích hợp E2E đã hoàn thành sớm hơn kế hoạch (tuần 3 thay vì tuần 11-15). Hai phần còn thiếu là luật đếm xe theo hướng và đánh giá OCR toàn diện.

1.2. Tổng quan kiến trúc hệ thống đã triển khai

[📷 HÌNH 1: Sơ đồ kiến trúc tổng thể 4 lớp — chụp/vẽ diagram]
Chú thích: Sơ đồ 4 lớp: Camera/Video → AI Engine → Backend API → Dashboard
Gợi ý: Vẽ bằng draw.io hoặc Mermaid, export PNG

Mô tả kiến trúc đã triển khai:

  Lớp 1 — Đầu vào: Video file / Camera IP (hiện hỗ trợ file mp4)
  Lớp 2 — AI Engine: Python pipeline xử lý video
           YOLOv8n (detect xe) → SORT tracker → LP_detector (biển số) → LP_ocr (OCR)
  Lớp 3 — Backend: FastAPI + PostgreSQL/SQLite, 18 REST API endpoints
           Nhận event, xử lý barrier logic, quản lý accounts, thống kê
  Lớp 4 — Dashboard: React + TypeScript, hiển thị realtime trên trình duyệt


═══════════════════════════════════════════════════════════════

2. CHƯƠNG 1+2 — TỔNG QUAN VỀ BÀI TOÁN QUẢN LÝ PHƯƠNG TIỆN
   THÔNG QUA NHẬN DIỆN BIỂN SỐ XE

═══════════════════════════════════════════════════════════════

Trạng thái: Đề cương đã có, cần viết thành văn bản chính thức.

Nội dung chương này gộp từ Chương 1 (Mở đầu) và Chương 2 (Tổng quan bài toán và công nghệ) trong đề cương ban đầu, bao gồm:

  ✅ Đã xác định: Bối cảnh bài toán tại ĐH Bách khoa Hà Nội
  ✅ Đã xác định: Đối tượng quản lý (cán bộ, sinh viên, khách)
  ✅ Đã xác định: Phạm vi prototype (1-2 camera, xe máy + ô tô)
  ✅ Đã chọn: Hướng ứng dụng "kiểm soát ra/vào khu vực" + "bãi đỗ xe thông minh"

Các công nghệ đã áp dụng thực tế (làm cơ sở viết phần tổng quan lý thuyết):

┌──────────────────┬────────────────────────┬───────────────────────────┐
│ Lĩnh vực         │ Công nghệ              │ File code tham chiếu      │
├──────────────────┼────────────────────────┼───────────────────────────┤
│ Detect phương tiện│ YOLOv8n (COCO)        │ vehicle_detector.py       │
│ Tracking         │ SORT (Kalman Filter)   │ sort_tracker.py           │
│ Detect biển số   │ YOLOv5 custom          │ plate_detector.py         │
│ OCR              │ YOLOv5 char-level      │ plate_ocr.py              │
│ Backend          │ FastAPI + SQLAlchemy   │ apps/backend/app/         │
│ Frontend         │ React + TypeScript     │ apps/dashboard/src/       │
│ Database         │ PostgreSQL / SQLite    │ models.py, db.py          │
│ Container        │ Docker Compose         │ docker-compose.yml        │
└──────────────────┴────────────────────────┴───────────────────────────┘

Việc còn lại: Viết phần lý thuyết tổng quan (tìm paper/tài liệu tham khảo cho YOLO, SORT, ANPR/LPR).


═══════════════════════════════════════════════════════════════

3. CHƯƠNG 3 — PHÂN TÍCH YÊU CẦU VÀ THIẾT KẾ HỆ THỐNG

═══════════════════════════════════════════════════════════════

Trạng thái: ✅ Thiết kế hoàn chỉnh, đã implement và kiểm thử.

3.1. Kịch bản vận hành đã thiết kế

  Xe VÀO cổng:
  Camera ghi nhận → AI detect xe + biển số → OCR → Gửi event về server
  → Server tra cứu account:
     • Biển đã đăng ký → barrier OPEN, trừ 2,000 VND
     • Biển lạ → tự tạo account tạm, cấp 100,000 VND, barrier OPEN
  → Dashboard hiển thị realtime

  Xe RA cổng:
  Camera ghi nhận → AI detect → Gửi event
  → Server kiểm tra:
     • Biển đã đăng ký → barrier OPEN
     • Biển tạm → barrier HOLD, cần xác minh thủ công trên Dashboard
  → Nhân viên verify trên Dashboard → barrier OPEN/CLOSE

3.2. Thiết kế cơ sở dữ liệu

Hệ thống sử dụng 10 bảng, quan hệ chính:

[📷 HÌNH 2: ER Diagram cơ sở dữ liệu — vẽ từ models.py]
Chú thích: 10 bảng: cameras, vehicle_events, plate_reads, accounts,
transactions, barrier_actions, import_batches, audit_logs,
pretrained_jobs, pretrained_detections
Gợi ý: Dùng dbdiagram.io hoặc draw.io, paste schema từ models.py

Các bảng chính và vai trò:

  cameras          — Quản lý camera tại các cổng (student/staff)
  vehicle_events   — Ghi nhận sự kiện xe vào/ra (direction, vehicle_type)
  plate_reads      — Kết quả OCR (plate_text, confidence, ocr_status)
  accounts         — Tài khoản theo biển số (balance, registration_status)
  transactions     — Lịch sử giao dịch (init/event_charge/manual_adjust)
  barrier_actions  — Quyết định barrier (open/hold + lý do)

3.3. Thiết kế API

Backend cung cấp 18 REST API endpoints:

┌────────┬──────────────────────────────────────┬────────────────────────┐
│ Method │ Endpoint                             │ Chức năng              │
├────────┼──────────────────────────────────────┼────────────────────────┤
│ POST   │ /api/v1/events                       │ Tạo event + barrier    │
│ GET    │ /api/v1/events                       │ Danh sách events       │
│ GET    │ /api/v1/accounts                     │ Danh sách accounts     │
│ GET    │ /api/v1/accounts/{plate}             │ Chi tiết account       │
│ GET    │ /api/v1/accounts/summary             │ Thống kê accounts     │
│ POST   │ /api/v1/accounts/{plate}/mark-registered │ Đánh dấu đã ĐK   │
│ POST   │ /api/v1/accounts/{plate}/adjust-balance  │ Điều chỉnh số dư  │
│ GET    │ /api/v1/accounts/{plate}/transactions│ Lịch sử giao dịch     │
│ GET    │ /api/v1/barrier-actions              │ Danh sách barrier      │
│ POST   │ /api/v1/barrier-actions/verify       │ Xác minh barrier       │
│ GET    │ /api/v1/stats/realtime               │ Stats realtime         │
│ GET    │ /api/v1/stats/traffic                │ Thống kê lưu lượng    │
│ GET    │ /api/v1/stats/ocr-success-rate       │ Tỉ lệ OCR thành công  │
│ POST   │ /api/v1/pretrained/infer             │ Tạo job suy luận      │
│ POST   │ /api/v1/pretrained/import            │ Import detections      │
│ GET    │ /api/v1/pretrained/jobs              │ Danh sách jobs         │
│ GET    │ /api/v1/pretrained/jobs/{id}         │ Chi tiết job           │
│ GET    │ /api/v1/pretrained/jobs/summary      │ Thống kê jobs          │
└────────┴──────────────────────────────────────┴────────────────────────┘

Tài liệu thiết kế tham chiếu:
  .planning/2026-03-29-vnlp-seeded-backend-dashboard/API_CONTRACT.md
  .planning/2026-03-29-vnlp-seeded-backend-dashboard/DB_SCHEMA.md
  .planning/2026-03-29-vnlp-seeded-backend-dashboard/DASHBOARD_WIREFRAME.md

3.4. Luồng xử lý event (create_event — 7 bước atomic)

[📷 HÌNH 3: Sequence diagram luồng create_event — vẽ diagram]
Chú thích: 7 bước: (1) auto-create camera → (2) tạo VehicleEvent →
(3) normalize plate → (4) tạo PlateRead → (5) auto-create Account →
(6) decide_barrier → (7) tạo BarrierAction + Transaction
Gợi ý: Vẽ sequence diagram bằng Mermaid hoặc draw.io


═══════════════════════════════════════════════════════════════

4. CHƯƠNG 4 — XÂY DỰNG HỆ THỐNG QUẢN LÝ PHƯƠNG TIỆN RA/VÀO
   CƠ SỞ GIÁO DỤC ĐÀO TẠO

═══════════════════════════════════════════════════════════════

───────────────────────────────────────────────────────────────
4.1. Module đếm và theo dõi phương tiện
───────────────────────────────────────────────────────────────

4.1.1. Phát hiện phương tiện (Vehicle Detection)

Trạng thái: ✅ Hoàn thành

Model: YOLOv8 Nano (yolov8n.pt, 6.3MB)
Framework: Ultralytics YOLOv8
Đầu vào: Frame video (numpy array)
Đầu ra: Danh sách bounding box [x1, y1, x2, y2] + score + class

Các loại phương tiện phát hiện (lọc từ 80 class COCO):
  • car (ô tô)
  • motorcycle (xe máy)
  • bus (xe buýt)
  • truck (xe tải)

File code: apps/ai_engine/src/vehicle_detector.py (61 dòng)

[📷 HÌNH 4: Ảnh demo detection — bounding box xanh quanh xe]
Chú thích: Frame từ video trungdinh22-demo.mp4, bbox xanh = xe được detect
Gợi ý: Chạy --visual, chụp frame có nhiều xe

4.1.2. Theo dõi đối tượng (Object Tracking)

Trạng thái: ✅ Hoàn thành

Thuật toán: SORT (Simple Online and Realtime Tracker)
  • Kalman Filter 7 chiều: [x, y, area, ratio, vx, vy, va]
  • Hungarian matching bằng IoU
  • Tham số: max_age=1, min_hits=3, iou_threshold=0.3

Kết quả: Track ID ổn định qua nhiều frame, xe được gán ID duy nhất.

File code: apps/ai_engine/src/sort_tracker.py (244 dòng)
Nguồn gốc: Refactor từ abewley/sort (GPL-3.0) + Cannguyen123/Detect_redlight

[📷 HÌNH 5: Ảnh demo tracking — ID xe hiển thị trên bbox]
Chú thích: Cùng xe được gán ID không đổi qua nhiều frame
Gợi ý: Chụp 2-3 frame liên tiếp thấy cùng ID

4.1.3. Đếm phương tiện theo hướng

Trạng thái: ❌ Chưa triển khai

Kế hoạch: Thiết kế luật đếm theo line-crossing (vẽ đường ảo trên frame,
đếm khi centroid xe cắt qua đường theo hướng vào/ra).

Hiện tại hệ thống ghi nhận hướng (in/out) dựa trên tham số đầu vào
của camera, chưa tự phát hiện hướng từ video.

───────────────────────────────────────────────────────────────
4.2. Module nhận dạng biển số xe
───────────────────────────────────────────────────────────────

4.2.1. Phát hiện vùng biển số (Plate Detection)

Trạng thái: ✅ Hoàn thành

Đã benchmark 2 model:

┌─────────────────────┬──────────────┬──────────┬──────────┐
│ Model               │ Detection    │ Tốc độ   │ Kích     │
│                     │ Rate         │ (ms/ảnh) │ thước    │
├─────────────────────┼──────────────┼──────────┼──────────┤
│ LP_detector.pt ← ĐÃ│ 100%         │ 32 ms    │ 41 MB    │
│ CHỌN (YOLOv5)      │ (20/20 ảnh)  │          │          │
├─────────────────────┼──────────────┼──────────┼──────────┤
│ number_plate.pt     │ 100%         │ 48 ms    │ 50 MB    │
│ (YOLOv8)            │ (20/20 ảnh)  │          │          │
└─────────────────────┴──────────────┴──────────┴──────────┘

Kết luận: LP_detector.pt (YOLOv5) được chọn — cùng accuracy nhưng nhanh hơn 33%, nhẹ hơn 18%.

File code: apps/ai_engine/src/plate_detector.py (82 dòng)

[📷 HÌNH 6: Ảnh demo plate detection — bbox đỏ quanh biển số]
Chú thích: Biển số VN được detect với bbox đỏ
Gợi ý: Chụp từ --visual mode, frame có biển rõ

4.2.2. Nhận dạng ký tự (OCR)

Trạng thái: ✅ Hoàn thành (cần cải thiện accuracy)

Model: LP_ocr.pt (YOLOv5 char-level, 41MB)
Phương pháp: Detect từng ký tự → Gap-based 2-row clustering

Thuật toán 2-row clustering cho biển VN:
  1. Detect tất cả ký tự, ghi nhận tọa độ tâm (x_center, y_center)
  2. Sắp xếp theo y_center (trên → dưới)
  3. Tính gap lớn nhất giữa các ký tự liên tiếp
  4. Nếu gap > 30% chiều cao trung bình ký tự → tách 2 hàng
  5. Mỗi hàng sắp xếp left → right
  6. Nối: hàng trên + hàng dưới → chuỗi biển số

Kết quả baseline (50 ảnh VNLP):

┌────────────────────────┬──────────────┐
│ Chỉ số                 │ Kết quả      │
├────────────────────────┼──────────────┤
│ Detection rate (biển)  │ 96.0%        │
│ Exact match rate (OCR) │ 33.3%        │
│ Char accuracy          │ 51.0%        │
│ Avg confidence         │ 0.82         │
│ Tốc độ                 │ 15.4 ảnh/s   │
└────────────────────────┴──────────────┘

File code: apps/ai_engine/src/plate_ocr.py (104 dòng)
Script eval: scripts/eval-ocr-baseline.py (263 dòng)
Kết quả JSON: reports/2026-04-13/baseline-eval-results.json

[📷 HÌNH 7: Ảnh demo OCR — text vàng hiển thị kết quả đọc biển]
Chú thích: Kết quả OCR hiển thị phía trên biển số (vàng trên nền đen)
Gợi ý: Chụp từ --visual, frame có text OCR rõ

4.2.3. Hậu xử lý chuỗi biển số

Trạng thái: ⚠ Cơ bản (cần bổ sung)

Đã có:
  • Strip ký tự không phải chữ/số: re.sub(r"[^A-Za-z0-9]", "", text)
  • Uppercase toàn bộ
  • Hàm normalize_plate_text() trong backend (13 unit tests pass)

Chưa có:
  • Regex match format biển VN: XX[A-Z]-XXXXX (1 hàng) hoặc XXX-XXXXX (2 hàng)
  • Bảng chuyển đổi ký tự dễ nhầm (0↔O, 1↔I, 5↔S, 8↔B)

───────────────────────────────────────────────────────────────
4.3. Server, cơ sở dữ liệu và dashboard
───────────────────────────────────────────────────────────────

4.3.1. Backend API Server

Trạng thái: ✅ Hoàn thành

Framework: FastAPI (Python)
Database: PostgreSQL (production) / SQLite (dev/demo)
ORM: SQLAlchemy
CORS: Enabled cho cross-origin dashboard
Docker: docker-compose.yml với 3 services

Quy tắc nghiệp vụ barrier:

┌──────────────────────┬────────┬──────────┬─────────────────────────┬─────────┐
│ Registration status  │ Hướng  │ Barrier  │ Lý do                   │ Verify? │
├──────────────────────┼────────┼──────────┼─────────────────────────┼─────────┤
│ registered           │ IN     │ OPEN     │ registered_vehicle_in   │ Không   │
│ registered           │ OUT    │ OPEN     │ registered_vehicle_out  │ Không   │
│ temporary_registered │ IN     │ OPEN     │ temp_vehicle_in         │ Không   │
│ temporary_registered │ OUT    │ HOLD     │ temp_out_requires_verify│ Có      │
│ unknown (xe mới)     │ IN     │ OPEN     │ auto_temporary_register │ Không   │
│ (mặc định)          │ (any)  │ HOLD     │ default_hold            │ Có      │
└──────────────────────┴────────┴──────────┴─────────────────────────┴─────────┘

File code: apps/backend/app/ — 11 files, 1,644 dòng
  barrier_rules.py (55) — Logic barrier
  crud.py (441) — Nghiệp vụ chính (20+ hàm)
  main.py (478) — 18 API endpoints
  models.py (175) — 10 bảng ORM
  schemas.py (226) — Pydantic schemas

[📷 HÌNH 8: Ảnh API response — curl POST event + JSON response]
Chú thích: Response JSON thể hiện barrier_action, registration_status
Gợi ý: Chụp terminal chạy curl POST /api/v1/events

4.3.2. Dashboard giám sát

Trạng thái: ✅ Hoàn thành

Framework: React + TypeScript (Vite)
File code: apps/dashboard/src/ — 964 dòng

Các tính năng đã triển khai:
  ✅ Realtime stats: tổng xe vào/ra, tỉ lệ OCR thành công
  ✅ Events list: thời gian, biển số, loại xe, hướng, barrier action
  ✅ Accounts list: phân trang, tìm kiếm, sắp xếp
  ✅ Account detail: lịch sử giao dịch, điều chỉnh số dư
  ✅ Verify queue: danh sách barrier cần xác minh, nút verify
  ✅ Traffic stats: thống kê lưu lượng theo giờ
  ✅ Import summary: tổng hợp import batches

[📷 HÌNH 9: Screenshot dashboard — trang tổng quan]
Chú thích: Giao diện dashboard hiển thị realtime stats, events list
Gợi ý: Mở localhost:5173 sau khi chạy demo, chụp full page

[📷 HÌNH 10: Screenshot dashboard — accounts list + verify queue]
Chú thích: Danh sách accounts và barrier cần verify
Gợi ý: Chụp phần accounts table + verify section


═══════════════════════════════════════════════════════════════

5. CHƯƠNG 5 — THỰC NGHIỆM, ĐÁNH GIÁ KẾT QUẢ
   VÀ HƯỚNG PHÁT TRIỂN

═══════════════════════════════════════════════════════════════

5.1. Bộ dữ liệu

┌────────────────────────┬──────────┬──────────────────────────┐
│ Dataset                │ Số lượng │ Mô tả                    │
├────────────────────────┼──────────┼──────────────────────────┤
│ VNLP one_row           │ 19,086   │ Biển số VN 1 hàng        │
│ VNLP two_rows          │ 12,618   │ Biển số VN 2 hàng (ô tô) │
│ VNLP two_rows_xe_may   │ 5,593    │ Biển số VN 2 hàng (xe máy)│
│ VNLP tổng              │ 37,297   │                          │
├────────────────────────┼──────────┼──────────────────────────┤
│ Kaggle (Roboflow)      │ (có)     │ Dữ liệu bổ sung         │
├────────────────────────┼──────────┼──────────────────────────┤
│ Video test (VN plates) │ 1 video  │ trungdinh22-demo.mp4     │
│                        │ 300 frame│ 600×800, 10fps, 30s      │
├────────────────────────┼──────────┼──────────────────────────┤
│ Video test (traffic)   │ 2 video  │ demo-redlight, vehicle-  │
│                        │          │ count (biển nước ngoài)  │
└────────────────────────┴──────────┴──────────────────────────┘

5.2. Kết quả thực nghiệm

5.2.1. Plate Detection Benchmark (20 ảnh VNLP)

  LP_detector.pt (YOLOv5): 100% (20/20), 32ms/ảnh ← ĐÃ CHỌN
  number_plate.pt (YOLOv8): 100% (20/20), 48ms/ảnh

5.2.2. OCR Baseline (50 ảnh VNLP random)

  Detection rate:    96.0% (48/50 ảnh detect được biển)
  Exact match rate:  33.3% (16/48 biển đọc đúng hoàn toàn)
  Char accuracy:     51.0% (mức ký tự)
  Avg confidence:    0.82
  Tốc độ xử lý:     15.4 ảnh/giây

  Phân tích lỗi OCR:
  • Thừa/thiếu ký tự do detect nhầm hoặc miss char
  • Nhầm ký tự tương tự hình dáng (0↔O, 1↔I)
  • Biển mờ, nghiêng, che khuất một phần

5.2.3. End-to-End Video Test (trungdinh22-demo.mp4)

  Tổng frame:        300 (30 giây)
  Biển số phát hiện:  2 biển unique (36H82613, 14K117970)
  Events gửi backend: 23 raw events, 2 unique sau deduplicate
  FPS trên CPU:       2.1 (chậm, cần GPU)
  Thời gian xử lý:   140 giây cho 30 giây video

[📷 HÌNH 11: Ảnh demo visual mode — detection realtime trên video]
Chú thích: Cửa sổ visual: bbox xanh (xe), đỏ (biển), vàng (OCR text)
Gợi ý: Chạy --visual, chụp screenshot cửa sổ OpenCV

5.2.4. Backend & Tests

  Unit tests:        56/56 pass (100%)
  Thời gian test:    1.62 giây
  API smoke test:    Health, POST event, GET accounts — all pass
  Barrier logic:     8 test cases covering 6 nhánh — all pass

5.3. Hạn chế hiện tại

  1. OCR accuracy thấp (33.3% exact match) — cần hậu xử lý regex + char mapping
  2. Chưa có đếm xe theo hướng (line-crossing)
  3. FPS chậm trên CPU (2.1) — cần GPU hoặc tối ưu model
  4. Chưa lưu ảnh minh chứng (snapshot) biển số
  5. Chưa full eval trên toàn bộ 37,297 ảnh VNLP
  6. Chỉ có 1 video test biển VN — cần thêm video đa dạng

5.4. Hướng phát triển

  • Mở rộng nhiều camera đồng thời, xử lý song song
  • Edge deployment trên thiết bị nhúng (Jetson Nano)
  • Cảnh báo thông minh: xe lạ, biển số confidence thấp, lưu lượng bất thường
  • Tích hợp quản lý đăng ký phương tiện của nhà trường
  • Cải thiện OCR: deblur, perspective correction, augmented training


═══════════════════════════════════════════════════════════════

6. THỐNG KÊ SỐ LIỆU TỔNG HỢP

═══════════════════════════════════════════════════════════════

┌───────────────────────────────┬─────────────┐
│ Hạng mục                     │ Số liệu     │
├───────────────────────────────┼─────────────┤
│ Tổng dòng code Python        │ 4,835       │
│   AI Engine                  │ 954         │
│   Backend                    │ 1,644       │
│   Tests                      │ 1,036       │
│   Scripts                    │ 2,237       │ (note: includes utilities)
│ Tổng dòng code TypeScript    │ 964         │
│ Tổng dòng code (Python+TS)   │ 5,799       │ (note: không tính scripts)
├───────────────────────────────┼─────────────┤
│ Git commits (main)           │ 67          │
│ Git branches                 │ 5           │
│ Planning documents           │ 14 folders  │
├───────────────────────────────┼─────────────┤
│ API endpoints                │ 18          │
│ Database tables              │ 10          │
│ Dashboard components         │ 3           │
│ Unit tests                   │ 56 (100% pass)│
├───────────────────────────────┼─────────────┤
│ AI models                    │ 4 files     │
│ Tổng kích thước model        │ 138.3 MB    │
│ Dataset VNLP                 │ 37,297 ảnh  │
│ Video test                   │ 3 files     │
├───────────────────────────────┼─────────────┤
│ Plate detection rate         │ 100%        │
│ OCR exact match (baseline)   │ 33.3%       │
│ OCR char accuracy (baseline) │ 51.0%       │
│ E2E video FPS (CPU)          │ 2.1         │
│ Backend test time            │ 1.62s       │
├───────────────────────────────┼─────────────┤
│ Docker services              │ 3           │
│ Hướng dẫn chạy              │ 7 files     │
└───────────────────────────────┴─────────────┘


═══════════════════════════════════════════════════════════════

7. KẾ HOẠCH TRIỂN KHAI GIAI ĐOẠN TIẾP THEO

═══════════════════════════════════════════════════════════════

7.1. Ưu tiên cao (ảnh hưởng trực tiếp nội dung báo cáo)

┌───┬──────────────────────────────────────┬──────────────┬──────────┐
│ # │ Việc                                 │ Chương       │ Ước tính │
├───┼──────────────────────────────────────┼──────────────┼──────────┤
│ 1 │ Full OCR evaluation (3,731+ ảnh)     │ Ch.4.2, Ch.5 │ ~5 phút  │
│ 2 │ Regex hậu xử lý biển VN             │ Ch.4.2       │ ~1 giờ   │
│ 3 │ Char mapping (0↔O, 1↔I, 5↔S)       │ Ch.4.2       │ ~1 giờ   │
│ 4 │ Đếm xe line-crossing                │ Ch.4.1       │ ~3 giờ   │
│ 5 │ Screenshot dashboard cho báo cáo    │ Ch.4.3, Ch.5 │ ~30 phút │
│ 6 │ Vẽ diagram (kiến trúc, ERD, seq)    │ Ch.3         │ ~2 giờ   │
└───┴──────────────────────────────────────┴──────────────┴──────────┘

7.2. Ưu tiên trung bình

┌───┬──────────────────────────────────────┬──────────────┬──────────┐
│ # │ Việc                                 │ Chương       │ Ước tính │
├───┼──────────────────────────────────────┼──────────────┼──────────┤
│ 7 │ Lưu snapshot crop biển số           │ Ch.4.3       │ ~2 giờ   │
│ 8 │ Benchmark FPS: GPU vs CPU           │ Ch.5         │ ~30 phút │
│ 9 │ Thêm video test đa dạng            │ Ch.5         │ ~1 giờ   │
│10 │ Viết phần lý thuyết (tìm paper)    │ Ch.1+2       │ ~5 giờ   │
└───┴──────────────────────────────────────┴──────────────┴──────────┘

7.3. Ưu tiên thấp (nice-to-have)

  11. Deploy lên server thật (VPS/cloud)
  12. Edge deployment (Jetson Nano)
  13. WebSocket realtime push (thay vì polling)


═══════════════════════════════════════════════════════════════

8. PHÂN CÔNG CÔNG VIỆC

═══════════════════════════════════════════════════════════════

8.1. Phân công viết báo cáo

┌────────────────────────────────────────────────────┬────────────┐
│ Nội dung                                           │ Người viết │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 1+2: Tổng quan bài toán + lý thuyết        │            │
│   • Bối cảnh, mục tiêu, phạm vi                   │            │
│   • Lý thuyết YOLO, SORT, ANPR, OCR               │            │
│   • Tổng quan công nghệ web (FastAPI, React, PG)   │            │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 3: Phân tích yêu cầu + thiết kế            │            │
│   • Kịch bản vận hành, yêu cầu chức năng/phi CN   │            │
│   • Kiến trúc tổng thể, diagram                   │            │
│   • Thiết kế DB schema, API contract               │            │
│   • Thiết kế luồng dữ liệu E2E                    │            │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 4.1: Module đếm + tracking                  │            │
│   • Vehicle detection (YOLOv8)                     │            │
│   • SORT tracker                                   │            │
│   • Luật đếm (khi implement xong)                  │            │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 4.2: Module nhận dạng biển số               │            │
│   • Plate detection (LP_detector.pt)               │            │
│   • OCR char-level + 2-row clustering              │            │
│   • Hậu xử lý + đánh giá                          │            │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 4.3: Server, CSDL, Dashboard               │            │
│   • Backend API + barrier logic                    │            │
│   • Database schema + migrations                   │            │
│   • Dashboard UI + tính năng                       │            │
├────────────────────────────────────────────────────┼────────────┤
│ Chương 5: Thực nghiệm + đánh giá + hướng PT      │            │
│   • Dataset mô tả, kịch bản test                  │            │
│   • Kết quả detection, OCR, E2E                    │            │
│   • Phân tích hạn chế + hướng mở rộng             │            │
└────────────────────────────────────────────────────┴────────────┘

8.2. Phân công code bổ sung

┌────────────────────────────────────────────────────┬────────────┐
│ Việc code                                          │ Người làm  │
├────────────────────────────────────────────────────┼────────────┤
│ Full OCR evaluation (chạy eval script)             │            │
│ Regex hậu xử lý biển VN + char mapping            │            │
│ Đếm xe line-crossing                              │            │
│ Lưu snapshot crop biển số                          │            │
│ Benchmark GPU vs CPU                               │            │
│ Vẽ diagram (kiến trúc, ERD, sequence)              │            │
│ Chụp screenshot dashboard                          │            │
│ Quay video demo E2E                                │            │
└────────────────────────────────────────────────────┴────────────┘


═══════════════════════════════════════════════════════════════

9. ĐỀ XUẤT VÀ XIN Ý KIẾN THẦY

═══════════════════════════════════════════════════════════════

9.1. Xin ý kiến về cấu trúc báo cáo

Chúng em đề xuất gộp chương so với đề cương ban đầu (8 chương → 5 chương):

  Đề cương gốc (8 chương)          →    Báo cáo đề xuất (5 chương)
  ─────────────────────────              ─────────────────────────
  Ch.1 Mở đầu                      ┐
  Ch.2 Tổng quan + công nghệ       ┘→   Ch.1+2 Tổng quan bài toán

  Ch.3 Phân tích + thiết kế        →    Ch.3 Phân tích + thiết kế (giữ nguyên)

  Ch.4 Module đếm phương tiện      ┐
  Ch.5 Module nhận dạng biển số    ├→   Ch.4 Xây dựng hệ thống
  Ch.6 Server + CSDL + Dashboard   ┘    (3 tiểu mục: 4.1, 4.2, 4.3)

  Ch.7 Thực nghiệm + đánh giá     ┐
  Ch.8 Kết luận + hướng PT         ┘→   Ch.5 Đánh giá + hướng phát triển

Lý do: Giảm trùng lặp, tập trung vào prototype E2E thay vì chia nhỏ từng module.

Thầy đồng ý cấu trúc này không, hay nên giữ 8 chương riêng?

9.2. Xin ý kiến về OCR accuracy

OCR exact match hiện tại: 33.3%. Chúng em dự kiến cải thiện bằng:
  • Regex post-processing (match format biển VN)
  • Bảng char mapping (0↔O, 1↔I)
  • Padding crop biển số trước OCR

Thầy có đề xuất thêm phương pháp nào khác không?

9.3. Xin ý kiến về đếm xe

Hiện tại hệ thống detect + track xe nhưng chưa đếm theo hướng.
Chúng em đề xuất dùng line-crossing (vẽ đường ảo, đếm khi centroid cắt qua).

Thầy nghĩ nên dùng line-crossing hay zone-based counting?

9.4. Đề xuất bổ sung chức năng

Nếu còn thời gian, chúng em muốn bổ sung:
  • Lưu ảnh minh chứng (snapshot) khi detect biển số
  • WebSocket push events thay vì polling trên dashboard
  • Trang quản trị camera (thêm/sửa/xóa camera, stream URL)

Thầy thấy cần thiết bổ sung chức năng nào khác không?


═══════════════════════════════════════════════════════════════

10. PHỤ LỤC: PLAN CHỤP ẢNH CHÈN VÀO BÁO CÁO

═══════════════════════════════════════════════════════════════

Danh sách ảnh cần chụp/vẽ và vị trí chèn:

┌─────┬───────────────────────────────────────┬─────────────────────────────┐
│ Hình│ Mô tả                                 │ Cách tạo                    │
├─────┼───────────────────────────────────────┼─────────────────────────────┤
│ 1   │ Sơ đồ kiến trúc tổng thể 4 lớp       │ Vẽ draw.io hoặc Mermaid    │
│ 2   │ ER Diagram cơ sở dữ liệu             │ Vẽ dbdiagram.io / draw.io  │
│ 3   │ Sequence diagram luồng create_event   │ Vẽ Mermaid / draw.io       │
├─────┼───────────────────────────────────────┼─────────────────────────────┤
│ 4   │ Demo detection — bbox xanh quanh xe   │ Chạy --visual, chụp frame  │
│ 5   │ Demo tracking — ID xe trên bbox       │ Chạy --visual, 2-3 frame   │
│ 6   │ Demo plate detect — bbox đỏ biển số   │ Chạy --visual, chụp frame  │
│ 7   │ Demo OCR — text vàng kết quả đọc      │ Chạy --visual, chụp frame  │
├─────┼───────────────────────────────────────┼─────────────────────────────┤
│ 8   │ API response — curl POST event        │ Chụp terminal              │
│ 9   │ Dashboard — trang tổng quan           │ Chụp browser localhost:5173│
│ 10  │ Dashboard — accounts + verify queue   │ Chụp browser               │
│ 11  │ Demo visual mode — cửa sổ OpenCV      │ Chụp khi chạy --visual     │
└─────┴───────────────────────────────────────┴─────────────────────────────┘

Lệnh chạy visual mode để chụp ảnh:

  # Activate venv trước (dùng Python 3.11, không phải 3.14)
  .venv\Scripts\Activate.ps1

  # Chạy visual mode
  python scripts/run-e2e-demo.py ^
    --video data/test-videos/trungdinh22-demo.mp4 ^
    --camera cam_gate_1 --visual --no-backend

  # Nhấn Q hoặc ESC để thoát

Lưu ảnh vào: reports/2026-04-13/images/hinh-XX.png


═══════════════════════════════════════════════════════════════

11. TÀI LIỆU THAM KHẢO

═══════════════════════════════════════════════════════════════

--- Bài báo khoa học (Papers) ---

[1]  J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, "You Only Look
     Once: Unified, Real-Time Object Detection," in Proc. IEEE Conf.
     Computer Vision and Pattern Recognition (CVPR), 2016, pp. 779-788.
     DOI: 10.1109/CVPR.2016.91
     → Nền tảng lý thuyết YOLO cho phát hiện đối tượng (Chương 1+2)

[2]  J. Redmon and A. Farhadi, "YOLOv3: An Incremental Improvement,"
     arXiv preprint arXiv:1804.02767, 2018.
     → Kiến trúc multi-scale detection, cơ sở cho các phiên bản sau (Chương 1+2)

[3]  G. Jocher, A. Chaurasia, and J. Qiu, "Ultralytics YOLOv8," 2023.
     [Online]. Available: https://github.com/ultralytics/ultralytics
     → Model YOLOv8n dùng cho phát hiện phương tiện trong hệ thống (Chương 4.1)

[4]  G. Jocher, "YOLOv5 by Ultralytics," 2020.
     [Online]. Available: https://github.com/ultralytics/yolov5
     DOI: 10.5281/zenodo.3908559
     → Model YOLOv5 dùng cho phát hiện biển số và OCR ký tự (Chương 4.2)

[5]  A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, "Simple Online
     and Realtime Tracking," in Proc. IEEE Int. Conf. Image Processing
     (ICIP), 2016, pp. 3464-3468. DOI: 10.1109/ICIP.2016.7533003
     → Thuật toán SORT tracking dùng trong hệ thống (Chương 4.1)

[6]  R. E. Kalman, "A New Approach to Linear Filtering and Prediction
     Problems," Journal of Basic Engineering, vol. 82, no. 1, pp. 35-45,
     1960. DOI: 10.1115/1.3662552
     → Cơ sở lý thuyết Kalman Filter cho SORT tracker (Chương 1+2, 4.1)

[7]  H. W. Kuhn, "The Hungarian Method for the Assignment Problem,"
     Naval Research Logistics Quarterly, vol. 2, no. 1-2, pp. 83-97, 1955.
     DOI: 10.1002/nav.3800020109
     → Thuật toán Hungarian matching dùng trong SORT (Chương 4.1)

[8]  S. Du, M. Ibrahim, M. Shehata, and W. Badawy, "Automatic License
     Plate Recognition (ALPR): A State-of-the-Art Review," IEEE Trans.
     Circuits and Systems for Video Technology, vol. 23, no. 2,
     pp. 311-325, 2013. DOI: 10.1109/TCSVT.2012.2203741
     → Tổng quan hệ thống nhận dạng biển số tự động (Chương 1+2)

[9]  N. Omar, A. Sengur, and S. G. S. Al-Ani, "Cascaded deep learning-
     based efficient approach for license plate detection and recognition,"
     Expert Systems with Applications, vol. 149, 2020.
     DOI: 10.1016/j.eswa.2020.113280
     → Phương pháp cascade deep learning cho LPR (Chương 1+2)

[10] C.-N. E. Anagnostopoulos, I. E. Anagnostopoulos, I. D. Psoroulas,
     V. Loumos, and E. Kayafas, "License Plate Recognition From Still
     Images and Video Sequences: A Survey," IEEE Trans. Intelligent
     Transportation Systems, vol. 9, no. 3, pp. 377-391, 2008.
     DOI: 10.1109/TITS.2008.922938
     → Survey nhận dạng biển số từ ảnh và video (Chương 1+2)


--- Framework và thư viện phần mềm ---

[11] Ultralytics, "Ultralytics YOLOv8 Documentation," 2024.
     [Online]. Available: https://docs.ultralytics.com/
     → Framework chính cho vehicle detection (Chương 4.1)

[12] A. Bewley, "SORT: Simple Online and Realtime Tracking — Source Code,"
     2016. [Online]. Available: https://github.com/abewley/sort
     License: GPL-3.0
     → Mã nguồn gốc SORT tracker, refactor trong hệ thống (Chương 4.1)

[13] R. Labbe, "FilterPy — Kalman filters and other optimal and non-
     optimal estimation filters in Python," 2024.
     [Online]. Available: https://github.com/rlabbe/filterpy
     → Thư viện Kalman Filter dùng trong SORT (Chương 4.1)

[14] A. Paszke, S. Gross, F. Massa, et al., "PyTorch: An Imperative Style,
     High-Performance Deep Learning Library," in Advances in Neural
     Information Processing Systems 32 (NeurIPS), 2019, pp. 8024-8035.
     → Framework deep learning chính (Chương 1+2, 4.1, 4.2)

[15] OpenCV Team, "OpenCV (Open Source Computer Vision Library)," 2024.
     [Online]. Available: https://opencv.org/
     → Thư viện xử lý ảnh/video (Chương 4.1, 4.2)

[16] S. Ramírez, "FastAPI — Modern, fast web framework for building APIs
     with Python," 2024.
     [Online]. Available: https://fastapi.tiangolo.com/
     → Framework backend API (Chương 4.3)

[17] M. Bayer, "SQLAlchemy — The Database Toolkit for Python," 2024.
     [Online]. Available: https://www.sqlalchemy.org/
     → ORM cho cơ sở dữ liệu (Chương 4.3)

[18] S. Pydantic, "Pydantic — Data validation using Python type
     annotations," 2024.
     [Online]. Available: https://docs.pydantic.dev/
     → Validation và schema cho API request/response (Chương 4.3)

[19] PostgreSQL Global Development Group, "PostgreSQL: The World's Most
     Advanced Open Source Relational Database," 2024.
     [Online]. Available: https://www.postgresql.org/
     → Hệ quản trị CSDL chính (Chương 4.3)

[20] Meta Platforms, "React — A JavaScript library for building user
     interfaces," 2024.
     [Online]. Available: https://react.dev/
     → Framework frontend dashboard (Chương 4.3)

[21] TypeScript Team, "TypeScript: JavaScript With Syntax For Types," 2024.
     [Online]. Available: https://www.typescriptlang.org/
     → Ngôn ngữ lập trình frontend (Chương 4.3)

[22] Vite Team, "Vite — Next Generation Frontend Tooling," 2024.
     [Online]. Available: https://vitejs.dev/
     → Build tool cho dashboard (Chương 4.3)

[23] Docker Inc., "Docker: Accelerated Container Application Development,"
     2024. [Online]. Available: https://www.docker.com/
     → Containerization cho deployment (Chương 4.3)


--- Dataset và mã nguồn tham khảo ---

[24] VNLP Dataset, "Vietnamese License Plate Detection Dataset," 2024.
     37,297 ảnh biển số Việt Nam (one_row: 19,086; two_rows: 12,618;
     two_rows_xe_may: 5,593).
     → Dataset chính dùng cho training model và đánh giá (Chương 5)

[25] Cannguyen123, "Detect_redlight — Vehicle and License Plate Detection,"
     2025. [Online]. Available:
     https://github.com/Cannguyen123/Detect_redlight
     → Mã nguồn tham khảo: SORT tracker integration, number_plate.pt model,
       visualize pipeline (Chương 4.1, 4.2)

[26] trungdinh22, "License-Plate-Recognition — Vietnamese license plate
     recognition," 2024. [Online]. Available:
     https://github.com/trungdinh22/License-Plate-Recognition
     → Mã nguồn tham khảo: LP_detector.pt và LP_ocr.pt models,
       video demo biển số VN (Chương 4.2, 5)

[27] winter2897, "Real-time Auto License Plate Recognition with Jetson
     Nano," 2023. [Online]. Available:
     https://github.com/winter2897/Real-time-Auto-License-Plate-Recognition-with-Jetson-Nano
     → Tham khảo kiến trúc LPR pipeline và dataset (Chương 1+2)

[28] mrzaizai2k, "License Plate Recognition YOLOv7 and CNN," 2024.
     [Online]. Available:
     https://github.com/mrzaizai2k/License-Plate-Recognition-YOLOv7-and-CNN
     → Tham khảo phương pháp nhận dạng biển số VN (Chương 1+2)


--- Tài liệu kỹ thuật và tiêu chuẩn ---

[29] Bộ Công an, "Quy chuẩn kỹ thuật quốc gia về biển số xe cơ giới —
     QCVN 40:2019/BGTVT," 2019.
     → Quy tắc format biển số xe Việt Nam (Chương 4.2)

[30] Uvicorn, "Uvicorn — An ASGI web server for Python," 2024.
     [Online]. Available: https://www.uvicorn.org/
     → ASGI server cho FastAPI backend (Chương 4.3)

[31] SciPy Community, "SciPy — Fundamental algorithms for scientific
     computing in Python," 2024.
     [Online]. Available: https://scipy.org/
     → Thuật toán linear_sum_assignment cho Hungarian matching (Chương 4.1)

[32] NumPy Community, "NumPy — The fundamental package for scientific
     computing with Python," 2024.
     [Online]. Available: https://numpy.org/
     → Xử lý mảng số cho AI pipeline (Chương 4.1, 4.2)


--- Mã nguồn dự án ---

[33] ukelele0718, "bienso — Hệ thống quản lý phương tiện ra/vào cơ sở
     giáo dục đào tạo thông qua nhận diện biển số xe," 2026.
     [Online]. Available: https://github.com/ukelele0718/bienso
     → Toàn bộ mã nguồn dự án đồ án tốt nghiệp (AI Engine, Backend,
       Dashboard, Scripts, Tests, Docker)


Ghi chú:
- Các tài liệu [Online] truy cập lần cuối: 13/04/2026
- Số thứ tự [1]-[10]: papers; [11]-[23]: frameworks; [24]-[28]: datasets/repos; [29]-[32]: khác
- Khi viết báo cáo chính thức, format theo chuẩn IEEE hoặc APA tùy yêu cầu của trường
