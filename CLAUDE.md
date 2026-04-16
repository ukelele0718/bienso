# Project Context for Claude Code

> File này tự động load mỗi session. Giữ ngắn gọn, tập trung vào RULES + GOTCHAS.

---

## 1. Mục tiêu

Đồ án tốt nghiệp (ĐATN) tại ĐH Bách khoa Hà Nội:
**Thiết kế hệ thống quản lý phương tiện ra/vào cơ sở giáo dục đào tạo thông qua nhận diện biển số xe.**

- **Pipeline**: Camera/Video → AI Engine → Backend → Dashboard
- **Phạm vi**: Prototype E2E với 1-2 camera, xe máy + ô tô

---

## 2. Trạng thái hiện tại (cập nhật: 15/04/2026)

### Đã xong ✅

| Module | Chi tiết |
|--------|---------|
| AI Engine | YOLOv8n + SORT + LP_detector + LP_ocr (gap-based 2-row clustering) |
| Backend | FastAPI + 18 API + 6 barrier rules + SQLAlchemy + 10 DB tables |
| Dashboard | React + TypeScript, events + accounts + verify queue |
| E2E flow | Video → AI → Backend → Dashboard hoạt động |
| OCR post-processing | Char mapping + regex validate (đã tắt char mapping mặc định) |
| Snapshot saving | Crop biển số + serve static + dashboard thumbnail |
| Full OCR eval | 3,731 ảnh VNLP: 37.8% exact match, 53.8% char accuracy |
| Slide bảo vệ | 27 slides tại `slides/bao-ve-do-an.pptx` |
| Báo cáo định kỳ | `.md` + `.docx` tại `reports/2026-04-13/` và `reports/2026-04-15/` |

### Còn lại ⚠

- Viết văn bản lý thuyết Ch.1 (đã có research 19 references, chưa viết thành văn)
- Test dashboard thủ công trên browser (code review OK, chưa verify UI)
- Chụp screenshot dashboard mới (sau fix bugs + snapshot thumbnail)
- Deduplicate events by plate_text (fix known issue)
- Viết báo cáo chính thức (điền phân công, tên sinh viên)

---

## 3. RULES & GOTCHAS (QUAN TRỌNG)

### Platform & Environment

- **OS**: Windows 11, shell = Git Bash (không phải PowerShell)
- **Python**: dùng `.venv/Scripts/python.exe` — **KHÔNG dùng Python 3.14 global** (không compat với PyTorch)
- **Encoding**: luôn set `PYTHONIOENCODING=utf-8` cho lệnh Python có tiếng Việt (Windows cp1252 sẽ crash)
- **Path**: dùng forward slash `/` hoặc escape backslash — `path.join()` tạo `\` làm glob Windows fail
- **curl trên Windows**: dùng `curl.exe` không dùng `curl` (PowerShell alias Invoke-WebRequest)

### AI Engine

- **OCR char mapping**: ĐÃ TẮT mặc định (`ENABLE_CHAR_MAPPING=false`). Lý do: giảm exact match 37.8% → 32.7% trên 3,731 ảnh. Heuristic 2-letter series nhầm biển 9 ký tự. Xem `test_plans_and_reports/test6-full-ocr-eval-3731.md`.
- **OCR regex validate**: Bật (`ENABLE_PLATE_VALIDATION=true`) — chỉ kiểm tra, không sửa.
- **Snapshot saving**: Bật mặc định. Folder `snapshots/`, padding 15%.
- **Backend tests**: 56/56 pass. OCR tests: 33/33 pass. Tổng **89 unit tests**.
- **FPS**: 1.6-2.1 FPS trên CPU, 14.7 img/s trên GPU GTX 1650.

### Backend / Dashboard

- **Barrier rules**: 6 nhánh tại `apps/backend/app/barrier_rules.py`. Biển lạ VÀO → tự tạo account tạm 100k VND + OPEN. Biển tạm RA → HOLD + verify.
- **Dashboard state**: React hooks — lưu ý `setAccountsPage(1)` là **async**, không dùng page state ngay sau `set`. Đã có bug này, đã fix.
- **CORS**: đã enable, dashboard :5173 gọi backend :8000 được.
- **SQLite auto-create tables**: on startup (dev mode). Production dùng PostgreSQL.

### Camera direction

- **Config-based**, KHÔNG phải line-crossing. Mỗi camera cấu hình `gate_type` + direction cố định (IN hoặc OUT). Đây là thiết kế cố ý, không phải thiếu sót.

### User feedback patterns (để không lặp lại)

- **Không tự động commit**: User sẽ yêu cầu "commit và push" khi muốn.
- **Trung thực với trạng thái**: Không đánh ✅ khi thực tế ⚠. Ghi rõ "chưa test browser" thay vì giả định OK.
- **Không nói quá**: Nếu chỉ code review thì ghi "code review OK", không ghi "verified working".
- **Báo cáo honest**: Ghi rõ known issues + limitations. User thấy mâu thuẫn → sẽ yêu cầu fix.
- **Tiếng Việt academic tone** cho báo cáo; tiếng Anh technical terms OK.
- **Long-running commands**: Nếu >30s (eval script, training) → thông báo thời gian trước khi chạy.

---

## 4. Key Commands

```bash
# Start backend (dev)
cd apps/backend && PYTHONIOENCODING=utf-8 uvicorn app.main:app --port 8000 --reload

# Start dashboard (dev)
cd apps/dashboard && npm run dev

# Run E2E demo (AI Engine → Backend)
PYTHONIOENCODING=utf-8 python scripts/run-e2e-demo.py --video data/test-videos/trungdinh22-demo.mp4 --visual --max-frames 100

# Backend tests (56 tests, ~1.5s)
cd apps/backend && PYTHONIOENCODING=utf-8 python -m pytest tests/ -v

# OCR post-processing tests (33 tests, ~2.5s)
cd . && PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m pytest apps/ai_engine/tests/ -v

# Full OCR eval on 3,731 images (~4 min GPU)
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/eval-ocr-baseline.py --limit 3731

# Rebuild .docx report
node reports/2026-04-13/docx/build-report.js

# Rebuild slides
PYTHONIOENCODING=utf-8 python slides/build-slides.py
```

---

## 5. File Map

### Code chính

```
apps/
├── ai_engine/src/
│   ├── pipeline.py          # Main orchestration (~350 dòng)
│   ├── vehicle_detector.py  # YOLOv8n
│   ├── sort_tracker.py      # SORT (244 dòng)
│   ├── plate_detector.py    # LP_detector.pt
│   ├── plate_ocr.py         # LP_ocr.pt + char mapping + regex (179 dòng)
│   ├── event_sender.py      # POST to backend
│   └── config.py            # ENV vars (snapshot, post-process flags)
├── backend/app/
│   ├── main.py              # 18 API endpoints + StaticFiles mount
│   ├── crud.py              # create_event 7 bước atomic
│   ├── barrier_rules.py     # 6 barrier nhánh
│   ├── models.py            # 10 DB tables (SQLAlchemy)
│   └── schemas.py           # Pydantic schemas
├── backend/tests/           # 56 tests (pytest)
├── ai_engine/tests/         # 33 tests OCR post-processing
└── dashboard/src/
    ├── main.tsx             # React app (598 dòng)
    ├── api.ts               # Backend API client
    ├── api-types.ts         # TypeScript types
    └── components/          # VerifyQueueSection, ImportSummarySection
```

### Scripts

- `scripts/run-e2e-demo.py` — AI Engine + send events + visual mode
- `scripts/eval-ocr-baseline.py` — OCR eval trên VNLP dataset
- `scripts/eval-with-postprocess.py` — so sánh baseline vs char mapping

### Reports & Docs

- `reports/2026-04-13/` — báo cáo định kỳ lần 1 (.md + .docx + 11 images)
- `reports/2026-04-15/` — báo cáo định kỳ lần 2 (mới nhất)
- `test_plans_and_reports/` — logs test (test1-test6)
- `plans/reports/` — subagent reports (research Ch.1, etc.)
- `.planning/260414-1903-resolve-all-remaining-issues/` — plan 9 phases
- `slides/bao-ve-do-an.pptx` — 27 slides bảo vệ
- `cauhoi/` — câu hỏi của thầy (gitignored, private)

### Data & Models

- `data/external/vnlp/VNLP_detection/` — dataset 37,297 ảnh (train 29,837 / val 3,729 / test 3,731)
- `data/processed/dataset_manifest.json` — split manifest
- `data/test-videos/trungdinh22-demo.mp4` — video biển VN 30s
- `models/` — LP_detector.pt, LP_ocr.pt, yolov8n.pt (gitignored, 138MB)

---

## 6. Links đến docs chi tiết

- **Báo cáo mới nhất**: [reports/2026-04-15/bao-cao-dinh-ky-tien-do.md](reports/2026-04-15/bao-cao-dinh-ky-tien-do.md)
- **Plan tồn đọng**: [.planning/260414-1903-resolve-all-remaining-issues/plan.md](.planning/260414-1903-resolve-all-remaining-issues/plan.md)
- **OCR eval report**: [test_plans_and_reports/test6-full-ocr-eval-3731.md](test_plans_and_reports/test6-full-ocr-eval-3731.md)
- **Research Ch.1**: [plans/reports/researcher-260414-chapter1-theory-references.md](plans/reports/researcher-260414-chapter1-theory-references.md)

---

## 7. Khi bắt đầu session mới

**Claude nên:**
1. Đọc file này (tự động)
2. Hỏi user muốn làm gì cụ thể — KHÔNG tự khởi động task
3. Nếu cần context thêm: đọc báo cáo mới nhất + plan tồn đọng
4. Tôn trọng RULES + GOTCHAS ở mục 3

**Thư mục KHÔNG liên quan đến đồ án (bỏ qua khi tìm context):**
- `docs/` — skill/marketing content (brand-guidelines, marketing-dashboard-*, video-script-*). KHÔNG phải project docs.
- `plans/` — subagent reports từ các project khác. Project plans nằm ở `.planning/`.
- `assets/`, `runs/`, `project_review/`, `.agents/`, `.claude/`, `.cursor/` — tooling/skill files.
- **Project docs thật ở**: `reports/`, `.planning/`, `test_plans_and_reports/`, `CLAUDE.md`.

**Claude KHÔNG nên:**
- Chạy eval/demo/test mà không được yêu cầu (tốn GPU/CPU)
- Tự commit/push
- Bật lại char mapping (đã tắt có lý do)
- Sửa barrier rules (đã test 8 cases, 6 nhánh)
- Viết lại báo cáo .md từ đầu (đã có 984 dòng, chỉ cần update)

---

## 8. Quy tắc cập nhật file này

Khi codebase/project thay đổi, Claude (hoặc user) cần update các mục:

- **Mục 2 (trạng thái)** — khi hoàn thành phase mới, thêm tính năng, hoặc thay đổi tiến độ
- **Mục 3 (rules & gotchas)** — khi có quyết định quan trọng mới (vd: tắt/bật feature, phát hiện bug pattern, rút ra best practice từ feedback)
- **Mục 5 (file map)** — khi thêm module mới, di chuyển file, xóa thư mục

Các mục **1, 4, 6, 7 ít thay đổi** — chỉ update khi mục tiêu đồ án thay đổi hoặc quy trình làm việc khác hẳn.

**Nguyên tắc**: giữ file dưới 300 dòng. Nếu quá dài → trích ra file riêng và link vào mục 6.
