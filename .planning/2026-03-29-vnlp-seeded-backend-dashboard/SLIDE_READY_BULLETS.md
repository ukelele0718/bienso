# SLIDE-READY BULLETS (COPY VAO PPT)

## Slide 1 - Project Snapshot
- **Project**: VNLP Seeded Backend Dashboard
- **Goal**: Demo full flow khong phu thuoc OCR/AI runtime
- **Status**: MVP hoan thanh, regression pass
- **Date**: 2026-04-05

## Slide 2 - Problem & Objective
- Can demo nghiep vu barrier nhanh, on dinh
- Dau vao: plate_text da co san tu VNLP filename list
- Muc tieu: import -> backend rules -> dashboard -> test E2E
- Uu tien: reliability, reproducibility, fast demo

## Slide 3 - Scope Delivered
- Seed import pipeline (CSV -> DB)
- Backend business rules cho seeded mode
- Dashboard operational views + import summary
- Full seeded regression test flow
- Runbook + setup + one-command runner

## Slide 4 - Key Backend Deliverables
- Normalize plate text nhat quan
- Rule seeded mode da chot:
  - registered in/out -> open
  - unknown in -> temporary + open
  - temporary out -> hold + verify
- Import provenance:
  - source, seed_group, imported_at
  - import_batch_id + import_batches
- APIs import audit:
  - GET /import-batches
  - GET /import-batches/summary

## Slide 5 - Key Dashboard Deliverables
- Accounts summary + list/search/filter
- Verify queue cho barrier hold
- Import Summary section
- Recent import batches table
- Refresh import data actions

## Slide 6 - Testing & Quality Gates
- Seeded flow integration test: **PASS 6/6**
- Deterministic reset script cho local/CI
- Dynamic test payloads tranh state collision
- Docker readiness + health checks
- CI seeded regression workflow

## Slide 7 - Major Issues Resolved
- FK camera 500 -> auto-create camera fallback
- Docker build context fail -> backend .dockerignore
- Module import crash in container -> PYTHONPATH fix
- Windows console Unicode issue -> ASCII markers
- Proxy env connection issue -> trust_env=False
- UUID schema mismatch -> cast string in responses

## Slide 8 - Operational Assets Delivered
- RUN_FULL_END_TO_END.md
- SETUP_STEP_BY_STEP.md
- EXECUTION_DETAILED_REPORT.md
- EXECUTIVE_SUMMARY_ONE_PAGE.md
- DEMO_5_MIN_10_COMMANDS.md
- scripts/run_seeded_regression.ps1

## Slide 9 - Demo Script (5 minutes)
- Start postgres
- Run migration
- Reset deterministic fixture
- Start backend
- Run seeded flow test
- Show pass 6/6 + import summary API

## Slide 10 - Business/Academic Value
- Co the demo ngay khong can AI runtime
- Testable, reproducible, audit-friendly
- Giam rui ro demo fail do env/data drift
- Tang toc do handover cho team/giang vien

## Slide 11 - Current Status
- Backend: stable
- Dashboard: usable for ops demo
- Tests: green
- Docs: synced
- Plan checkboxes: completed

## Slide 12 - Next Steps
- Split commits by domain (backend/scripts/dashboard/docs)
- Run CI regression 2-3 rounds on target branch
- Add extra smoke checks for import summary API
- Prepare final presentation + live demo backup plan
