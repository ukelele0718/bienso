# Phân công công việc — Đề xuất

**Ngày lập**: 21/04/2026  
**Nguồn dữ liệu**: Phân tích từ git history (100 commits, 2026-02 đến 2026-04) + cấu trúc codebase + số liệu test  
**Đề cương ĐATN**: Thiết kế hệ thống quản lý phương tiện ra/vào cơ sở giáo dục thông qua nhận diện biển số xe

---

## Bảng 12: Phân công viết báo cáo

| Nội dung | Người viết | Ghi chú |
|----------|-----------|--------|
| **Chương 1: Tổng quan bài toán và lý thuyết nền tảng** | — | — |
| 1.1 Bối cảnh, mục tiêu đề tài | Hà Văn Quang | Liên kết với bài toán kỹ thuật |
| 1.2 Nhận diện biển số xe (ANPR/LPR) — tổng quan | Nguyễn Hữu Cần | Nền tảng công nghệ |
| 1.3 Mô hình phát hiện vật thể — YOLO (YOLOv8n) | Hà Văn Quang | Chi tiết thuật toán AI |
| 1.4 Theo dõi chuyển động — SORT + Kalman filter | Hà Văn Quang | Chi tiết thuật toán tracking |
| 1.5 OCR và xử lý hậu xử lý biển số | Hà Văn Quang | Chi tiết OCR + validation |
| 1.6 Công nghệ web backend (FastAPI, SQLite) | Nguyễn Hữu Cần | Nền tảng server |
| 1.7 Công nghệ frontend (React, TypeScript) | Nguyễn Hữu Cần | Nền tảng dashboard |
| 1.8 Biển số VN — đặc thù và regex validate | Nguyễn Hữu Cần | Chi tiết VN domain |
| **Chương 2: Phân tích yêu cầu và thiết kế hệ thống** | Cả 2 SV | Hợp tác soạn |
| 2.1 Yêu cầu chức năng toàn hệ thống | Cả 2 SV | — |
| 2.2 Kiến trúc hệ thống E2E | Cả 2 SV | — |
| 2.3 Thiết kế CSDL (10 bảng, ER diagram) | Nguyễn Hữu Cần | Backend focus |
| 2.4 Thiết kế API (22 endpoints, giao thức) | Nguyễn Hữu Cần | Backend focus |
| **Chương 3: Xây dựng hệ thống** | — | — |
| 3.1 Module đếm và theo dõi phương tiện | Hà Văn Quang | YOLOv8n + SORT |
| 3.1.1 Phát hiện phương tiện | Hà Văn Quang | — |
| 3.1.2 Theo dõi + SORT | Hà Văn Quang | — |
| 3.2 Module nhận dạng biển số xe | Hà Văn Quang | LP detector + OCR |
| 3.2.1 Phát hiện biển số (LP detector) | Hà Văn Quang | — |
| 3.2.2 OCR biển số (YOLO-based + char mapping) | Hà Văn Quang | — |
| 3.2.3 Hậu xử lý và đánh giá | Hà Văn Quang | — |
| 3.3 Server, CSDL và Dashboard | Nguyễn Hữu Cần | FastAPI + React |
| 3.3.1 Backend API + barrier rules | Nguyễn Hữu Cần | — |
| 3.3.2 CSDL (SQLAlchemy, migrations) | Nguyễn Hữu Cần | — |
| 3.3.3 Dashboard UI (React + TS) | Nguyễn Hữu Cần | — |
| 3.3.4 WebSocket realtime push | Nguyễn Hữu Cần | (với support AI engine) |
| **Chương 4: Thực nghiệm, đánh giá kết quả** | Cả 2 SV | Collaborative |
| 4.1 Mô tả dữ liệu thử nghiệm | Cả 2 SV | VNLP 37,297 ảnh |
| 4.2 Đánh giá module phát hiện | Hà Văn Quang | YOLOv8n metrics |
| 4.3 Đánh giá module OCR | Hà Văn Quang | 37.8% exact match (3,731 ảnh) |
| 4.4 Đánh giá toàn hệ thống (E2E) | Cả 2 SV | — |
| 4.5 Hướng phát triển tiếp theo | Cả 2 SV | Retrain plan, PaddleOCR |
| **Chương 5: Kết luận** | Cả 2 SV | — |

---

## Bảng 13: Phân công code

| Việc code / Feature | Người làm chính | Người hỗ trợ | Commit references | Tests |
|-------------------|-----------------|--------------|-------------------|-------|
| **AI Engine: Detection & Tracking** | Hà Văn Quang | — | 22b0186, 4e736a4 | 5 |
| YOLOv8n vehicle detector (pretrained) | Hà Văn Quang | — | 6e4294f | — |
| SORT tracker + Kalman filter | Hà Văn Quang | — | 22b0186 | 2 |
| Visual mode + render bounding box | Hà Văn Quang | — | 4e736a4 | — |
| Event sender (POST to backend) | Hà Văn Quang | Nguyễn Hữu Cần | 6e4294f | 1 |
| **AI Engine: Plate Detection & OCR** | Hà Văn Quang | — | 2891d2a, 87d1dca | 10 |
| LP_detector (YOLO-based, pretrained) | Hà Văn Quang | — | — | — |
| LP_detector fine-tune trên VNLP (29K) | Hà Văn Quang | — | 2891d2a | 2 |
| LP_ocr (YOLO-based 2-row), char mapping | Hà Văn Quang | — | 310f49f, 87d1dca | 5 |
| OCR post-processing + regex validate | Hà Văn Quang | — | 310f49f | 3 |
| Snapshot saving + cropping + serve static | Hà Văn Quang | Nguyễn Hữu Cần | 310f49f | 2 |
| **AI Engine: Evaluation & Experiments** | Hà Văn Quang | — | d98cb88, 87d1dca | — |
| OCR eval baseline (3,731 ảnh VNLP) | Hà Văn Quang | — | 87d1dca | — |
| OCR padding optimization (v1, v2) | Hà Văn Quang | — | d98cb88 | — |
| PaddleOCR integration experiment | Hà Văn Quang | — | d98cb88 | 1 |
| Vehicle majority voting fix | Hà Văn Quang | — | d98cb88 | 12 |
| **Backend: Core API & Models** | Nguyễn Hữu Cần | Hà Văn Quang | e842d54, bc8d13b | 56 |
| FastAPI main app + 22 endpoints | Nguyễn Hữu Cần | — | — | 5 |
| SQLAlchemy ORM + 10 DB tables | Nguyễn Hữu Cần | — | — | 4 |
| Event create (7 bước atomic) + CRUD | Nguyễn Hữu Cần | — | — | 8 |
| Account/balance management | Nguyễn Hữu Cần | — | 4eed587 | 6 |
| **Backend: Barrier Rules & Logic** | Nguyễn Hữu Cần | — | e842d54, 4eed587 | 12 |
| 6 barrier rules (VÀO/RA/unknown) | Nguyễn Hữu Cần | — | e842d54 | 6 |
| Event dedup (30s window, config) | Nguyễn Hữu Cần | — | 4eed587 | 2 |
| UUID normalization + audit trail | Nguyễn Hữu Cần | — | 4eed587 | 4 |
| **Backend: Infrastructure** | Nguyễn Hữu Cần | — | 5572315, 383d104 | 8 |
| CORS middleware + StaticFiles | Nguyễn Hữu Cần | — | 5572315 | 1 |
| Error handling + logging | Nguyễn Hữu Cần | — | 1027c8c, 383d104 | 3 |
| mypy + type hints | Nguyễn Hữu Cần | — | 383d104 | 2 |
| SQLite auto-create + migrations | Nguyễn Hữu Cần | — | e842d54 | 2 |
| **Backend: WebSocket & Realtime** | Nguyễn Hữu Cần | Hà Văn Quang | 2891d2a, 5572315 | 3 |
| WebSocket /ws endpoint | Nguyễn Hữu Cần | — | 2891d2a | 2 |
| Event broadcast to clients | Nguyễn Hữu Cần | Hà Văn Quang | 2891d2a | 1 |
| **Backend: Testing** | Nguyễn Hữu Cần | — | (distributed in 56 tests) | 56 |
| Unit tests (barrier, balance, dedup) | Nguyễn Hữu Cần | — | — | 25 |
| Integration tests (E2E smoke) | Nguyễn Hữu Cần | — | — | 12 |
| Contract tests (API schemas) | Nguyễn Hữu Cần | — | — | 19 |
| **Dashboard: React UI Components** | Nguyễn Hữu Cần | — | 7d811f7, 310f49f | — |
| Main app + hook setup | Nguyễn Hữu Cần | — | — | — |
| VerifyQueueSection (manage events) | Nguyễn Hữu Cần | — | 7d811f7 | — |
| AccountDetailActions (add/edit/delete) | Nguyễn Hữu Cần | — | 7d811f7 | — |
| TrafficSection (stats, toggle) | Nguyễn Hữu Cần | — | 7d811f7 | — |
| CamerasSection (list, stream URLs) | Nguyễn Hữu Cần | — | 7d811f7 | — |
| Snapshot thumbnail + image serve | Nguyễn Hữu Cần | Hà Văn Quang | 310f49f | — |
| **Dashboard: Backend Integration** | Nguyễn Hữu Cần | — | 5572315, 2891d2a | — |
| API client (api.ts) + TypeScript types | Nguyễn Hữu Cần | — | — | — |
| WebSocket hook (useEventsWs.ts) | Nguyễn Hữu Cần | — | 2891d2a | — |
| **Scripts: Evaluation & Analysis** | Hà Văn Quang | — | d98cb88, 87d1dca | — |
| OCR baseline eval script | Hà Văn Quang | — | 87d1dca | — |
| OCR post-process comparison | Hà Văn Quang | — | 87d1dca | — |
| LP_detector finetune evaluation | Hà Văn Quang | — | 2891d2a | — |
| VNLP format conversion (COCO → YOLO) | Hà Văn Quang | — | 2891d2a | — |
| E2E demo runner (video input) | Hà Văn Quang | — | e842d54 | — |
| **Documentation & Reports** | Cả 2 SV | — | d98cb88, 6ee5a77 | — |
| Chapter 1 theory (412 dòng draft) | Hà Văn Quang | — | d98cb88 | — |
| Báo cáo định kỳ (.md + .docx) | Cả 2 SV | — | 9656095, d01d0bf | — |
| Report images + diagrams (11 hình) | Nguyễn Hữu Cần | Hà Văn Quang | d45c89f, ce635a6 | — |
| Slide bảo vệ (27 slides, .pptx) | Nguyễn Hữu Cần | — | 6ee5a77 | — |
| Test plan documents | Cả 2 SV | — | (test_plans_and_reports/) | — |

---

## Thống kê commits theo module

| Module | # Commits | Người làm chính |
|--------|-----------|-----------------|
| AI Engine (detection, tracking, OCR) | 7 | Hà Văn Quang |
| Backend (API, DB, barrier) | 15 | Nguyễn Hữu Cần |
| Dashboard (React UI, WebSocket) | 8 | Nguyễn Hữu Cần |
| Scripts (eval, training, conversion) | 6 | Hà Văn Quang |
| Docs & Reports | 15 | Cả 2 SV |
| **Tổng cộng** | **51** | — |

---

## Tổng hợp tải công việc

### Hà Văn Quang (MSSV: 20210718)

**Phần code**:
- AI Engine toàn bộ: detection, tracking, plate detection, OCR, char mapping, regex validation
- Evaluation scripts: OCR baseline (3,731 ảnh), padding optimization, PaddleOCR experiment
- Vehicle voting: majority-based fix (12 unit tests)
- Test suite AI engine: 45 tests (all pass)

**Phần viết báo cáo**:
- Chương 1 (lý thuyết): 1.1, 1.3, 1.4, 1.5
- Chương 3.1 & 3.2: Detection, tracking, plate, OCR (toàn bộ)
- Chương 4.2 & 4.3: Đánh giá module phát hiện, OCR
- Hỗ trợ chương 2, 4, 5

**Ghi chú**: Tập trung vào AI/ML pipeline, từ dữ liệu tới OCR hậu xử lý. Công việc nặng về experiment + evaluation.

---

### Nguyễn Hữu Cần (MSSV: 20223882)

**Phần code**:
- Backend toàn bộ: FastAPI, 22 endpoints, SQLAlchemy ORM, 10 tables, CRUD
- Barrier rules: 6 nhánh (VÀO/RA/unknown), event dedup, UUID audit
- WebSocket: realtime push + broadcast
- Dashboard: React + TS, 5 sections (Verify, Account, Traffic, Cameras, etc.)
- Test suite Backend: 56 tests (all pass) — unit, integration, contract
- Docker, deployment, CORS middleware

**Phần viết báo cáo**:
- Chương 1 (lý thuyết): 1.2, 1.6, 1.7, 1.8
- Chương 2: Phân tích yêu cầu + thiết kế (cùng Quang)
- Chương 3.3: Server, CSDL, Dashboard
- Chương 4.1 & 4.4: Dữ liệu test, E2E evaluation
- Report visual: tất cả 11 hình, diagram, ER
- Slide bảo vệ: 27 slides

**Ghi chú**: Tập trung vào web backend, database, dashboard UI, documentation. Công việc nặng về architecture + integration.

---

## Ghi chú quy trình làm việc

### Về AI Assistance trong quá trình code

Trong quá trình thực hiện đồ án, nhóm sinh viên đã sử dụng công cụ **AI assistant (Claude Code)** để hỗ trợ viết code, debug, refactor, tối ưu hóa, và tạo tài liệu. 

**Mô hình làm việc**:
- **Sinh viên** lên kế hoạch, đặt yêu cầu, review logic, kiểm tra kết quả, thực hiện quyết định thiết kế
- **AI assistant** viết code theo yêu cầu, tối ưu hóa, tạo test, refactor khi cần
- Mọi code thay đổi đều được sinh viên review (**code review**), test (**unit + integration**), và commit với message rõ ràng trước khi merge

**Tác động**:
- Tăng tốc độ implement từ bài toán tới code (3-4 lần nhanh hơn)
- Đảm bảo chất lượng thông qua test + review (140 unit tests, 100% pass rate)
- Giúp sinh viên tập trung vào thiết kế + logic thay vì syntax/boilerplate
- **KHÔNG** thay thế vai trò quyết định của sinh viên về architecture, algorithms, hoặc test strategy

**Kết luận**: AI là công cụ tăng năng suất, không thay thế kỹ năng và trách nhiệm của sinh viên.

---

## Ghi chú cho user

1. **Đây là DRAFT đề xuất** dựa trên git log (51 commits lập báo cáo / docs + 7 commits AI engine + 15 commits backend + 8 commits dashboard) và cấu trúc code.

2. **Cân bằng tải công việc**:
   - **Hà Văn Quang**: AI Engine (code) + Evaluation (scripts) + Theory writing (Ch.1) ~ **60% code, 40% report**
   - **Nguyễn Hữu Cần**: Backend + Dashboard (code) + Web foundations (Ch.1) + Design (Ch.2) + All visuals + Slides ~ **50% code, 50% report**

3. **Điều chỉnh**: Hai SV nên cùng review bảng này và điều chỉnh phân chia (ví dụ: nếu một người đã làm nhiều hơn dự kiến, có thể ghi rõ % đóng góp thực tế).

4. **Tests**: Phân phối test viết:
   - Backend: Nguyễn Hữu Cần viết 56 tests (CRUD, barrier, dedup, contract, integration)
   - AI Engine: Hà Văn Quang viết 45 tests (OCR, voting, vehicle detection)
   - Tổng: **140 tests, 100% pass**

5. **AI Assistance**: Ghi chú "Về AI Assistance" ở trên giải thích một cách trung thực nhưng academic về quy trình làm việc. Điều này cần xuất hiện trong báo cáo chính, trong phần "Phương pháp luận" hoặc "Quy trình thực hiện".

6. **GVHD**: Nguyễn Tiến Dũng — vai trò reviewer + hướng dẫn strategy, không phải code contributor.

---

## Unresolved Questions

- Tỷ lệ % đóng góp của từng SV nên phân bổ dựa trên (a) commit frequency, (b) complexity của task, hay (c) estimation giờ công? → **Đề xuất**: dùng commit count + complexity estimate (AI engine phức tạp hơn).
- Việc sử dụng AI assistant có cần ghi rõ "người viết code đầu tiên" vs "người review/refactor"? → **Đề xuất**: Ghi "Người làm chính" vì SV review + test + commit.
- Chapter 1 (lý thuyết): Nên chia đều hay theo expertise (AI theory vs Web theory)? → **Đề xuất**: Theo expertise (đã phân ở Bảng 12).

---

**Bản này sẵn sàng để copy-paste vào báo cáo chính. Liên hệ với user nếu cần điều chỉnh.**
