## Summary
- merge seeded hardening and pretrained job flow into integration branch with documented conflict resolution.
- unify backend/frontend contracts (error schema, account sort/filter, pretrained jobs summary/detail), and keep both dashboard feature sets functional.
- add integration validation artifacts: conflict log, manual smoke checklist, readiness reports (v1->v4), and expanded backend smoke/contract tests.

## Test plan
- [x] `python -m pytest apps/backend/tests/test_barrier_unit.py apps/backend/tests/test_api_error_contract.py apps/backend/tests/test_accounts_contract.py apps/backend/tests/test_pretrained_unit.py apps/backend/tests/test_pretrained_contract.py -q`
- [x] `python -m pytest apps/backend/tests/test_integration_smoke.py apps/backend/tests/test_barrier_unit.py apps/backend/tests/test_api_error_contract.py apps/backend/tests/test_accounts_contract.py apps/backend/tests/test_pretrained_unit.py apps/backend/tests/test_pretrained_contract.py -q`
- [x] Manual smoke checklist executed and tracked in `.planning/INTEGRATION_MANUAL_SMOKE_CHECKLIST.md`

## Notes
- readiness decision in `.planning/INTEGRATION_READINESS_REPORT.md` is **GO** for merge to `main`.
- known non-blocking warning debt: `datetime.utcnow` deprecation (documented for follow-up hardening).
