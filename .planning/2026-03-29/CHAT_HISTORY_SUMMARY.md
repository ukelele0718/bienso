# Chat History Summary — 2026-03-29

## 1) Mục tiêu đã chốt
Dự án được thu hẹp để ưu tiên prototype chạy được end-to-end với phạm vi rõ ràng:
- Chỉ xử lý **1 luồng camera**.
- 2 kịch bản cổng:
  - Cổng sinh viên: xe máy.
  - Cổng giảng viên: xe máy + ô tô.
- Luồng bắt buộc:
  - `video -> detect vehicle -> track -> count -> detect plate -> OCR -> post-process -> send event -> dashboard`.
- Rule tài chính:
  - khởi tạo 100,000 VND/biển số,
  - mỗi lượt vào/ra trừ 2,000 VND,
  - cho phép số dư âm.
- Rule thanh chắn:
  - xe đã đăng ký vào: mở tự động,
  - xe lạ vào: mở và tự tạo đăng ký tạm,
  - xe đăng ký tạm ra: giữ chặn, xác thực xong mới mở.

---

## 2) Tài liệu `.artifacts` đã được cập nhật
Đã chỉnh sửa/khởi tạo các tài liệu để đồng bộ scope và khả năng maintain:
- `PRD.md`
- `IMPLEMENTATION_PLAN.md`
- `DB_SCHEMA.md`
- `API_CONTRACT.md`
- `DASHBOARD_WIREFRAME.md`
- `TEST_PLAN.md`
- `BASELINE_EVALUATION_REPORT.md`

Các tài liệu đã phản ánh:
- phạm vi single-stream,
- typed-first,
- rule tài chính + barrier,
- test planning đầy đủ từ unit tới UI/E2E,
- nguồn tham khảo/citation.

---

## 3) Trạng thái code hiện tại (thực tế đã làm)

### Backend
- Đã kết nối DB thực bằng SQLAlchemy (không dùng in-memory store).
- Đã có migration SQL:
  - `001_init.sql`
  - `002_barrier_and_registration.sql`
- Đã có modules chính:
  - `app/models.py`
  - `app/schemas.py`
  - `app/crud.py`
  - `app/services.py` (barrier decision)
  - `app/main.py` (API endpoints)
- Đã có audit log cho barrier decision/verify.

### API chính đã có
- `POST /api/v1/events`
- `GET /api/v1/events` (filter theo plate/time/direction/vehicle)
- `GET /api/v1/accounts/{plate}`
- `GET /api/v1/accounts/{plate}/transactions`
- `GET /api/v1/barrier-actions?plate=...`
- `POST /api/v1/barrier-actions/verify?plate=...&actor=...`
- `GET /api/v1/stats/realtime`
- `GET /api/v1/stats/traffic`
- `GET /api/v1/stats/ocr-success-rate`
- `GET /health`

### Dashboard (TypeScript)
- Đã có skeleton UI dùng data thật từ API:
  - realtime cards,
  - bảng sự kiện gần nhất,
  - tra cứu theo biển số + khoảng thời gian,
  - account balance + transaction count,
  - barrier logs,
  - traffic summary.
- TypeScript typecheck đã pass (`tsc --noEmit`).

### Test backend
- Đã có test files:
  - `test_balance_rule.py`
  - `test_barrier_unit.py`
  - `test_barrier_api.py`
  - `conftest.py` (fixture DB + seed camera + cleanup)
- Test environment hiện đã chuyển về SQLite local cho tính tự chạy (không phụ thuộc DB test có sẵn).

---

## 4) Docker/Runbook hiện có
- Có `docker-compose.yml` cho Postgres + Backend.
- Có `apps/backend/Dockerfile`.
- Có migration runner: `apps/backend/scripts/run_migrations.py`.

Run nhanh:
```bash
docker compose up --build
```

---

## 5) Dữ liệu (Phase 2) — trạng thái đã xác minh
Nguồn ở `data/external` đã được kiểm tra theo thống kê nhẹ (không load toàn bộ ảnh):
- `vnlp`: 37,304 files
- `kaggle`: 1 file
- `roboflow`: 7 files

Đã chạy script chuẩn bị data artifact và sinh:
- `data/processed/dataset_manifest.json`

Thống kê từ manifest:
- tổng ảnh hợp lệ: 37,297
- source: vnlp
- split:
  - train: 29,837
  - val: 3,729
  - test: 3,731

---

## 6) Các điểm đã tick trong IMPLEMENTATION_PLAN
- Phase 1: done.
- Phase 5: done.
- Phase 6: done.
- Phase 7: phần lớn integration đã tick.
- Phase 2: đã làm phần ingest/split/manifest; cần rà soát mục chuẩn hóa annotation (YOLO/COCO) để đóng hoàn toàn.

---

## 7) Các vấn đề/ghi chú kỹ thuật quan trọng
1. Có sự lệch giữa DB schema tài liệu và code ở một số naming/chi tiết, cần chuẩn hóa lại trước release.
2. Một số command test trước đó thất bại do môi trường DB test PostgreSQL chưa có database `vehicle_lpr_test`; đã chuyển hướng dùng fixture SQLite để giảm phụ thuộc.
3. Cần tách rõ "pass local" vs "pass CI" để tránh hiểu nhầm trạng thái chất lượng.
4. Một số warning `datetime.utcnow()` còn tồn tại; nên chuyển dần sang timezone-aware datetime.

---

## 8) Việc cần làm tiếp theo (ưu tiên maintain)

### P0 (ngay)
- Chuẩn hóa annotation về YOLO/COCO và hoàn tất mục còn lại của Phase 2.
- Chốt thống nhất schema tài liệu ↔ models ↔ migrations (single source of truth).
- Chạy lại full backend tests sau khi chốt DB path/fixtures.

### P1
- Setup Python type-check đầy đủ (`mypy` hoặc `pyright`) và thêm vào pipeline runbook.
- Tạo baseline evaluation thực tế cho counting/OCR (report v0.2 có số đo thật).
- Hoàn thiện dashboard transaction history chi tiết (không chỉ count).

### P2
- Tăng độ tin cậy E2E test với dữ liệu video mẫu.
- Bổ sung monitoring/logging chuẩn cho production prototype.

---

## 9) Đề xuất cấu trúc vận hành để maintain lâu dài
- Giữ `.artifacts` là nguồn tài liệu sản phẩm/chấp thuận.
- Giữ `.planning` là nhật ký điều phối theo ngày (như file này).
- Mỗi thay đổi lớn nên cập nhật cả 3 lớp:
  1) PRD/Plan,
  2) API/DB contract,
  3) test plan + test implementation.
- Khi tick `[x]` trong plan, luôn gắn bằng chứng:
  - file thay đổi,
  - command đã chạy,
  - kết quả test/typecheck.

---

## 10) Snapshot file quan trọng để người mới tiếp quản
- Product/plan:
  - `.artifacts/PRD.md`
  - `.artifacts/IMPLEMENTATION_PLAN.md`
  - `.artifacts/TEST_PLAN.md`
- Contracts:
  - `.artifacts/API_CONTRACT.md`
  - `.artifacts/DB_SCHEMA.md`
- Backend:
  - `apps/backend/app/main.py`
  - `apps/backend/app/crud.py`
  - `apps/backend/app/models.py`
  - `apps/backend/migrations/*.sql`
  - `apps/backend/tests/*`
- Dashboard:
  - `apps/dashboard/src/main.tsx`
  - `apps/dashboard/src/api.ts`
  - `apps/dashboard/src/api-types.ts`
- Data artifacts:
  - `scripts/prepare_dataset.py`
  - `data/processed/dataset_manifest.json`
  - `.artifacts/BASELINE_EVALUATION_REPORT.md`

---

## 11) Kết luận
Dự án đã đi qua giai đoạn chốt scope + dựng nền tảng backend/dashboard + test skeleton và bắt đầu bước data artifact cho baseline.  
Khả năng maintain hiện tốt hơn đáng kể nhờ hệ tài liệu `.artifacts` và checklist có trạng thái.  
Để tiến tới mốc demo tin cậy, cần khóa nốt chuẩn annotation + typed QA Python + baseline metrics thực tế.
