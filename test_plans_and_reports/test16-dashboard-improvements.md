# Test 16 — Dashboard Improvements (TC-04, TC-06, Phase 09)

Date: 2026-04-21

## Summary

Three improvements implemented to complete partial TCs from Phase 05 and deliver Phase 09 camera stream section.

---

## Part 1: Account Detail Actions (TC-04)

Added two action buttons to the "Search account" panel:

- **Mark as Registered** — shown only when account status is `temporary_registered`. Calls `POST /api/v1/accounts/{plate}/mark-registered`. On success refreshes account detail.
- **Adjust Balance** — always visible. Opens inline number input + Confirm/Cancel. Calls `POST /api/v1/accounts/{plate}/adjust-balance` with `{amount_vnd, reason}`. Supports negative amounts (deduction). On success shows new balance and refreshes detail.

Both buttons show loading state and display error/success messages inline (no alert()).

Account detail panel now also shows current registration status label and uses `.toLocaleString()` for balance formatting.

---

## Part 2: Traffic Stats Hour/Day Toggle (TC-06)

Replaced static "Traffic summary" text card with a new `TrafficSection` component featuring:

- Toggle buttons: **By Hour** / **By Day** — active tab highlighted in blue
- Full HTML table with columns: Time bucket | In | Out | Total
- Summary totals row in footer
- In column shown in green, Out in amber (matches existing badge palette)
- Fetches fresh data on toggle change

Traffic data is no longer fetched in the main `loadRealtime()` call — `TrafficSection` self-manages its state.

---

## Part 3: Cameras Section (Phase 09)

### Backend

Added `GET /api/v1/cameras` endpoint returning list of configured cameras ordered by `created_at DESC`.

Added `CameraOut` Pydantic schema to `schemas.py`:
- Fields: id, name, gate_type, location, stream_url, is_active, created_at

### Frontend

New component `CamerasSection.tsx`:
- Shows count in heading
- Table: Name | Gate | Location | Stream | Active
- Stream URL renders as clickable `<a target="_blank">` link when present, else `—`
- Active field shown as green "Yes" / red "No"
- Refresh button to re-fetch

Embedded at bottom of main dashboard (after VerifyQueueSection).

---

## Files Changed

### Backend
- `apps/backend/app/schemas.py` — added `CameraOut` class
- `apps/backend/app/main.py` — added `Camera` import, `CameraOut` import, `GET /api/v1/cameras` endpoint

### Frontend
- `apps/dashboard/src/api-types.ts` — added `CameraOut` interface
- `apps/dashboard/src/api.ts` — added `markRegistered`, `adjustBalance`, `fetchCameras` functions; added `CameraOut` import
- `apps/dashboard/src/components/AccountDetailActions.tsx` — new component (148 lines)
- `apps/dashboard/src/components/TrafficSection.tsx` — new component (110 lines)
- `apps/dashboard/src/components/CamerasSection.tsx` — new component (90 lines)
- `apps/dashboard/src/main.tsx` — updated imports, removed `useMemo`+`traffic` state, added `accountDetail` state, added `refreshAccountDetail`, wired 3 new components

### Tests
- `apps/backend/tests/test_cameras_api.py` — 4 new tests for cameras endpoint

---

## Test Results

### TypeScript
```
npx tsc --noEmit → 0 errors (clean)
```

### Backend Tests
```
95 passed, 0 failed (was 91 before this task)
New tests: test_cameras_list_empty, test_cameras_list_returns_seeded_camera,
           test_cameras_list_schema_shape, test_cameras_list_with_extra_camera
```

---

## Screenshots

Not captured (GPU busy, browser verification skipped per constraints).

---

## Definition of Done

- [x] TC-04: Mark as registered + Adjust balance buttons in Account Detail
- [x] TC-06: Hour/day toggle in Traffic Stats + table display
- [x] Phase 09: Cameras section with stream URL links
- [x] Backend endpoint for cameras list (`GET /api/v1/cameras`)
- [x] TypeScript compiles clean
- [x] Backend tests pass (95 total, all pass)
- [x] Report at test16

---

## Known Limitations

- `AccountDetailActions` shows only when a plate has been searched — no standalone account detail view
- Camera section auto-loads on mount; no auto-refresh interval
- Traffic section does not persist selected groupBy across page refreshes (defaults to 'hour')
