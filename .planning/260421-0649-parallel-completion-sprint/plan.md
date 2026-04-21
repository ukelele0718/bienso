# Plan: Parallel Completion Sprint

**Ngày tạo**: 21/04/2026
**Mục tiêu**: Triển khai nhiều việc tồn đọng nhất có thể, tiến tới sản phẩm hoàn chỉnh
**Chiến lược**: Spawn nhiều agent song song qua worktrees + branches; thử nghiệm rủi ro trên branch riêng để so sánh
**Deadline**: Còn nhiều thời gian → ưu tiên chất lượng + thử nghiệm, không rush

---

## Tổng quan 11 phases

| # | Phase | Loại | Branch strategy | Batch |
|---|-------|------|----------------|-------|
| 01 | OCR Debug — Root cause analysis | 🔴 Critical | `experiment/ocr-padding` | B1 |
| 02 | PaddleOCR Alternative | 🟠 Experiment | `experiment/paddle-ocr` + worktree | B1 |
| 03 | Vehicle Type Majority Voting | 🟡 Improvement | `experiment/vehicle-voting` + worktree | B1 |
| 04 | Deduplicate Events by plate_text | 🟡 Fix | `fix/dedup-events` | B2 |
| 05 | Dashboard Browser Testing + Runtime Fixes | 🔴 Critical | `fix/dashboard-runtime` + worktree | B1 |
| 06 | Backend Missing Endpoint Tests | 🟢 Coverage | `test/missing-endpoints` | B1 |
| 07 | WebSocket Realtime Push | 🟠 Feature | `feat/websocket-realtime` + worktree | B2 |
| 08 | Chapter 1 Theory Writing | 🟡 Doc | main (markdown only) | B1 |
| 09 | Camera Stream URL Display | 🟢 Feature | `feat/stream-url` | B2 |
| 10 | Screenshots + Demo Video Recording | 🟢 Polish | main | B3 |
| 11 | GPU Benchmark + Additional Test Videos | 🟢 Polish | main | B3 |

### Priority legend
- 🔴 Critical: ảnh hưởng đến tính đúng đắn của sản phẩm
- 🟠 Experiment: thay đổi lớn, cần so sánh A/B
- 🟡 Improvement: làm tốt hơn tính năng hiện có
- 🟢 Polish: hoàn thiện, không chặn tính năng

---

## Execution Batching

### Batch 1 (Parallel, 6 agents)
Các task độc lập file-wise, có thể chạy song song ngay:

| Phase | Subagent type | Worktree | Branch |
|-------|--------------|----------|--------|
| 01 - OCR Debug | fullstack-developer | Main WT | `experiment/ocr-padding` |
| 02 - PaddleOCR | fullstack-developer | WT-B | `experiment/paddle-ocr` |
| 03 - Vehicle Voting | fullstack-developer | WT-C | `experiment/vehicle-voting` |
| 05 - Dashboard Test | debugger | WT-D | `fix/dashboard-runtime` |
| 06 - Backend Tests | tester | Main WT | `test/missing-endpoints` |
| 08 - Ch.1 Writing | researcher + user | Main WT | main |

File conflict analysis:
- Phase 01, 02, 03 đều touch `pipeline.py` → cần worktree riêng
- Phase 05 touch `apps/dashboard/*` + `apps/backend/app/main.py` → worktree riêng
- Phase 06 chỉ thêm file `apps/backend/tests/` → main OK
- Phase 08 chỉ markdown → main OK

### Batch 2 (Sau Batch 1 merge, 3 agents)
Các task cần quyết định từ Batch 1:

| Phase | Depends on | Lý do |
|-------|-----------|-------|
| 04 - Deduplicate | 01 (OCR stable trước) | Cần OCR chuẩn mới dedup đúng |
| 07 - WebSocket | 05 (Dashboard OK) | Push đến UI đang hoạt động |
| 09 - Stream URL | 05 (Dashboard OK) | Thêm UI mới |

### Batch 3 (Final polish, serial)
| Phase | Depends on | Lý do |
|-------|-----------|-------|
| 10 - Screenshots + Demo | 01-09 all done | Cần sản phẩm final |
| 11 - GPU Benchmark | 01 + 02 done | Cần OCR finalized |

---

## Branch Strategy

```
main
├── experiment/ocr-padding       # Phase 01 — merge nếu accuracy ↑
├── experiment/paddle-ocr        # Phase 02 — merge nếu beat YOLO baseline
├── experiment/vehicle-voting    # Phase 03 — merge nếu giảm mismatch
├── fix/dashboard-runtime        # Phase 05 — merge sau test thành công
├── test/missing-endpoints       # Phase 06 — merge ngay nếu tests pass
├── fix/dedup-events            # Phase 04 — tạo sau Batch 1
├── feat/websocket-realtime      # Phase 07 — tạo sau Batch 1
└── feat/stream-url              # Phase 09 — tạo sau Batch 1
```

### Quyết định merge
- Mỗi branch thử nghiệm có kết quả benchmark riêng
- Chỉ merge vào main nếu KẾT QUẢ TỐT HƠN baseline hiện tại
- Nếu kết quả TỆ HƠN: giữ branch để reference, ghi lessons learned, rollback

---

## Dependency Graph

```
Batch 1 (parallel):
  Phase 01 ──┐
  Phase 02 ──┼── merge decisions ──┐
  Phase 03 ──┘                     │
  Phase 05 ───────────────────────┼── Phase 04 ──┐
  Phase 06 ───────────────────────┤               ├── Phase 10 ── Phase 11
  Phase 08 ───────────────────────┘               │
                                   └── Phase 07 ──┤
                                   └── Phase 09 ──┘
```

---

## Success Criteria (Product-level)

Sau khi tất cả phases hoàn thành, sản phẩm nên:

- [ ] OCR accuracy ≥ 70% exact match (hiện 37.8%) HOẶC chuyển sang PaddleOCR đạt ≥80%
- [ ] Vehicle type classification có test + accuracy ≥ 80% trên video thật
- [ ] Dashboard: tất cả 7 tính năng đều hoạt động trên browser (đã verify thủ công)
- [ ] Không còn duplicate events cho cùng biển số trong 30s
- [ ] Realtime push qua WebSocket (hoặc giữ polling nếu không lợi)
- [ ] Stream URL camera hiển thị trên dashboard
- [ ] Backend coverage ≥ 85% (hiện ~75%)
- [ ] Có screenshots mới + video demo chính thức
- [ ] Chương 1 lý thuyết viết xong (≥15 trang A4)
- [ ] GPU benchmark có kết quả trên ≥2 video VN

---

## Risks & Mitigation

| Rủi ro | Xác suất | Mitigation |
|--------|---------|-----------|
| PaddleOCR không tốt hơn | TB | Giữ branch để reference, không merge |
| Dashboard có bug runtime nặng | Cao | Phase 05 ưu tiên fix trước |
| WebSocket tốn effort không tương xứng | TB | Có thể skip, giữ polling |
| Ch.1 theory viết không xong kịp | Thấp | User tự viết, AI chỉ hỗ trợ research (đã có) |
| Git worktree conflict khi merge | TB | Merge tuần tự, rebase thay vì merge commit |
| Token usage cao do nhiều agent | Cao | Spawn 2-3 agent cùng lúc, không phải tất cả |

---

## Files

```
.planning/260421-0649-parallel-completion-sprint/
├── plan.md                                    # File này
├── phase-01-ocr-debug-padding.md
├── phase-02-paddle-ocr-experiment.md
├── phase-03-vehicle-majority-voting.md
├── phase-04-deduplicate-events.md
├── phase-05-dashboard-browser-test.md
├── phase-06-backend-missing-tests.md
├── phase-07-websocket-realtime.md
├── phase-08-chapter1-theory-writing.md
├── phase-09-camera-stream-url.md
├── phase-10-screenshots-demo-video.md
├── phase-11-gpu-benchmark.md
└── execution-log.md                           # Track progress realtime
```

---

## Next Step

Review plan với user → confirm thứ tự → spawn Batch 1 (6 agents parallel).
