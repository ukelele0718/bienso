# Bug Report

## Status
INVESTIGATING

## Bug Title
Dashboard still shows "Failed to fetch" when calling backend APIs.

## Bug Description
Dashboard frontend cannot complete API requests and surfaces generic `Failed to fetch` error. User confirmed backend + dashboard are running, but UI still fails.

## Steps to Reproduce
1. Start backend.
2. Start dashboard.
3. Open dashboard page.
4. Observe API-dependent sections.

## Actual Result
Dashboard shows `Failed to fetch`.

## Expected Result
Dashboard should fetch data from backend and render KPI/account/import/verify sections.

## Context
- **Error Message**: `Failed to fetch`
- **Environment**: Windows + local dev (`localhost:5173` -> `localhost:8000`)

---

## Root Cause Analysis
Current frontend API layer throws generic message on network failure and does not log useful diagnostics.

- `apps/dashboard/src/api.ts:15` sets base URL from env fallback to `http://localhost:8000`.
- `apps/dashboard/src/api.ts:17` `parseJson()` only checks `res.ok`; for network/CORS/connection errors there is no structured log context.
- API calls are direct `fetch(...)` and any thrown network error bubbles up as a generic UI error.

Backend already has CORS middleware in current branch (`apps/backend/app/main.py`), but we still need request-level observability to prove whether requests are arriving and what status is returned.

Call flow currently:

frontend component -> `api.ts` fetch -> exception -> UI `setError('Failed to fetch')`

Missing observability points:
- frontend: base URL, endpoint, request method, status, raw response body on error
- backend: per-request method/path/status + latency + exception logging

## Proposed Fixes
### Fix Option 1 (Recommended)
Add focused debug logging in both frontend and backend.

- Frontend (`apps/dashboard/src/api.ts`):
  - wrap all fetches via `apiFetch()` helper
  - log request start/end, status, and fetch exceptions (network/CORS)
  - enrich thrown error with endpoint + status text
- Backend (`apps/backend/app/main.py`):
  - add HTTP middleware for request/response logging (method, path, status, duration)
  - add exception log line for unexpected errors

**Pros**: Fastest way to isolate whether issue is browser/network/CORS/backend route.
**Risk**: Extra log noise (acceptable for debug session).

### Fix Option 2 (Alternative)
Only frontend logging in `api.ts`.

**Pros**: Minimal code changes.
**Cons**: If request never reaches backend or backend crashes before response, root cause may still be unclear.

## Verification Plan
1. Reload dashboard and inspect console logs for each API call.
2. Inspect backend logs to confirm request arrival and response status.
3. Confirm error message includes endpoint and status details (not only "Failed to fetch").
4. Re-test key APIs from dashboard flow (`realtime`, `accounts`, `import summary`).
