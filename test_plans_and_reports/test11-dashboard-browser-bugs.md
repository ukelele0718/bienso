# Test 11: Dashboard Browser Test — Partial (Backend Bug Fixes)

**Date**: 21/04/2026
**Status**: ⚠ Partial — agent exited before full test completion; backend bugs fixed

---

## What was done

Phase 05 agent started dashboard browser testing with chrome-devtools skill. Before completing all 7 test cases, discovered and fixed 4 backend serialization bugs that were breaking dashboard API responses.

### Bugs found + fixed

#### Bug 1: UUID → str auto-coercion in schemas

**File**: `apps/backend/app/schemas.py`

**Issue**: PostgreSQL UUID columns return Python UUID objects from SQLAlchemy, but Pydantic schemas declared `str`. FastAPI validation failed → 500 errors on list endpoints.

**Fix**: Added `_Str = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, UUID) else v)]` and used on all ID fields in:
- `EventOut.id`
- `PlateReadOut.id`, `.event_id`
- `TransactionOut.id`, `.account_id`, `.event_id`
- `BarrierActionOut.id`

#### Bug 2: Non-UUID camera_id crash on event create

**File**: `apps/backend/app/crud.py`

**Issue**: AI Engine sends `camera_id` like `"cam-001"` (not a UUID). Backend crashed trying to insert non-UUID into PostgreSQL UUID column.

**Fix**: Added `_coerce_camera_id()` function — valid UUID passes through; non-UUID string gets deterministic UUID5 (namespace-based). Original string preserved as camera name.

```python
def _coerce_camera_id(raw: str) -> str:
    try:
        UUID(raw)
        return raw
    except ValueError:
        return str(uuid5(_CAMERA_NS, raw))
```

#### Bug 3: ImportBatchOut id type mismatch

**File**: `apps/backend/app/main.py:185`

**Issue**: DB returned UUID object, Pydantic expected str → 500 error on `/api/v1/import-batches`.

**Fix**: Wrapped id in `str()` before ImportBatchOut constructor.

#### Bug 4: TransactionOut id type mismatch

**File**: `apps/backend/app/main.py:221`

**Issue**: Same as Bug 3 but for transactions endpoint.

**Fix**: Wrapped `id`, `account_id`, `event_id` in `str()`.

---

## Verification

- Backend tests: **86/86 pass** (no regression)
- All schema changes are backward-compatible with SQLite (tests use SQLite)

---

## What remains (not done)

Phase 05 did NOT complete the full 7-test UI matrix. Still needed:

- [ ] TC-01: Realtime Stats cards rendering
- [ ] TC-02: Events List + snapshot thumbnails
- [ ] TC-03: Accounts List pagination + search
- [ ] TC-04: Account Detail + transactions
- [ ] TC-05: Verify Queue flow
- [ ] TC-06: Traffic Stats
- [ ] TC-07: Import Summary

These require manual browser testing by the student or a follow-up agent run.

---

## Recommendation

**Merge the backend fixes immediately** — they're necessary regardless of remaining dashboard test scope. Without them, any dashboard query on list/detail endpoints would fail with 500 errors on PostgreSQL.

Follow-up task: Schedule another agent (or manual session) to complete the 7 test cases on a working browser.

---

## Files changed

```
apps/backend/app/crud.py             | 18 +++++++++++++++---
apps/backend/app/main.py             |  8 ++++----
apps/backend/app/response_mappers.py |  4 ++--
apps/backend/app/schemas.py          | 36 +++++++++++++++++++++---------------
4 files changed, 42 insertions(+), 24 deletions(-)
```
