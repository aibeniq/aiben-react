# Progress Bars — generalizable pattern

This document describes a pragmatic, reusable approach for wiring progress bars across the app (knowledge base creation, report generation, review flows, compare/optimize flows, etc.). It covers the contract between front-end and back-end, Redis persistence, polling strategy, UX considerations, common failure modes (race/CORS), and tests to validate correctness.

## 1) High-level contract (inputs / outputs / behavior)

- Inputs
  - A short-lived `task_id` created by a lightweight "create task" endpoint. The client keeps the `task_id` and passes it into the long-running processing API (or background worker) so that work updates the shared progress state.
- Outputs
  - A `GET /<feature>/progress/{task_id}` endpoint that returns progress JSON, e.g.:
    ```json
    {
      "percentage": 42,
      "message": "Fetching documents (12/30)",
      "status": "in_progress", // in_progress | completed | error
      "error": null
    }
    ```
  - A `GET /<feature>/results/{task_id}` endpoint to fetch final results/metadata after completion.
- Success criteria
  - Frontend polls the progress endpoint and displays a stable progress bar, then fetches results when `status === 'completed'`.
  - No duplicate polling intervals; polling stops after completion or after a configured max poll count.
- Error modes
  - Transient network/CORS failures (retryable)
  - Backend returns missing/expired task (404) — frontend should surface a clear error and optionally retry after a short delay
  - Permanent failures (task `status === 'error'`) — show error and stop polling

## 2) Backend responsibilities

1. Task creation endpoint (lightweight)
   - Example: `POST /veradoc/review/task` returns `{ "task_id": "abc-123" }` immediately.
   - Keep this handler small and fast (no heavy work).

2. Long-running processing endpoint or worker
   - Accepts the `task_id` (source of truth for progress updates).
   - Either perform work in a background thread/worker or return quickly and enqueue the job; update progress from the background worker.

3. Progress persistence (Redis recommended)
   - Use a small `progress_tracker` abstraction so multiple endpoints can share logic.
   - Keys: `progress:{task_id}` for current progress JSON, `progress:{task_id}:metadata` for final results.
   - Use `SETEX` with a reasonable TTL (e.g., 3600s) so leftover keys auto-expire. Update TTL on writes if appropriate.

4. Progress API
   - Implement `GET /progress/{task_id}` returning 200 + JSON when found.
   - If the task key is missing, return a lightweight placeholder (200 with `{ status: 'not_found' }`) or 404 depending on UX preference — frontends must tolerate both.
   - Implement `GET /results/{task_id}` for final details. If not finished, return a clear status (e.g., `{ status: 'pending' }`).

5. Robustness and logging
   - Log Host/Origin headers for incoming requests to aid in diagnosing CORS/gateway mismatches.
   - Ensure error-handling paths (internal errors, 404 HTML pages from upstream proxies) still return CORS headers in production — otherwise the browser will block the response and show only a network error.

6. Update patterns
   - Provide helper methods: `update_progress(task_id, percentage, message, status)` and `set_results(task_id, payload)` to centralize TTL management and schema.

## 3) Frontend responsibilities & recommended hook pattern

Create a reusable hook per feature (e.g., `useVeradocProgress`, `useReportGenieProgress`, `useCompareProgress`). Keep hooks small and focused.

Hook contract
- Inputs: `taskId: string | null`
- Outputs: `{ percentage, message, isActive, completed, error, results }`

Implementation checklist
- Delay the first poll slightly (e.g., 300–500ms) to avoid racing the task creation and backend attach.
- Start a single interval (useRef to store interval id). Avoid creating multiple intervals for the same task.
- Poll interval: 600–1500ms depending on UX needs (we used 1000ms in the app).
- Transient fault tolerance: track a consecutive transient error counter (e.g., MAX_TRANSIENT_ERRORS = 3–5). Use small backoffs where appropriate.
- Same-origin fallback: when the OpenAPI.BASE or configured API URL is cross-origin and you see a fetch failure, attempt `fetch(
  `${window.location.origin}/api/v1/<feature>/progress/${taskId}`, { credentials: 'same-origin' }
)` before counting it as a fatal error. This helps local dev when the API URL points to prod.
- Results fetch: upon `status === 'completed'`, try the typed generated client first. If it fails due to CORS/network, attempt a same-origin fetch fallback. Use exponential backoff for results fetch (max attempts 3–5).
- Cancellation and reset: when `taskId` becomes `null` or changes, clear interval and reset state.
- Safety caps: stop polling when `pollCount` exceeds a large cap (e.g., 3600) to avoid infinite polling.

UI mapping
- Use `percentage` to render the progress bar width.
- Show `message` as the helper text and include the status (e.g., "Uploading files", "Processing doc 2/6").
- Provide a final results area that appears when `completed` and `results` are available.

## 4) Common pitfalls and mitigations

- Duplicate intervals / memory leaks
  - Always use refs and clear intervals on cleanup; guard re-creation when `taskId` unchanged.

- Race where frontend polls before backend has written any progress
  - Add a 300–500ms initial delay and make the backend return a clear `not_started` or `pending` state rather than a raw 404.

- CORS / gateway errors
  - The worst failure mode is an upstream gateway returning an HTML error page without Access-Control-Allow-Origin. The browser will show a generic network error and drop headers. Fixes:
    - Adjust gateway/proxy to include CORS headers for error pages.
    - On the client, use a same-origin fallback for local/dev situations.
    - Log Host and Origin server-side to spot origin mismatches.

- Missing TTL or too-short TTL
  - Persisted progress may expire while the frontend is still polling. Use a TTL that reasonably covers job execution time (e.g., 1 hour) and refresh TTL on progress updates.

## 5) Tests and quality gates

- Unit tests (frontend)
  - Hook tests: mock the generated client and `fetch` to assert polling behavior, retry/backoff, and cleanup.
  - Happy path test: ensure the hook sets `completed` and fetches results.
  - Transient failure test: simulate a few network errors then a success.

- Integration / E2E
  - Start backend+frontend, create a task, simulate background update (or invoke a small worker job) and assert the UI transitions from 0→progress→completed and displays results.

- Backend tests
  - Test `progress_tracker` functions: write/read/update TTL, store metadata, and ensure atomic updates.
  - Test `GET /progress/{task_id}` returns expected shapes for found/missing/expired keys.

Quality gates to run before merging
- Lint and type checks (TS/py)
- Unit tests for hooks and progress-tracker
- A quick manual smoke test: create a task, visit the UI, and confirm the progress bar advances and results populate.

## 6) Example minimal flow (pseudocode)

Backend
```py
# create task
@router.post('/some-feature/task')
async def create_task():
    task_id = str(uuid4())
    progress_tracker.set_progress(task_id, { 'percentage': 0, 'message': 'queued', 'status': 'pending' })
    return { 'task_id': task_id }

# long running call (or worker): accepts the same task_id and updates progress
# progress_tracker.update_progress(task_id, percentage=30, message='fetching docs', status='in_progress')
# when done: progress_tracker.set_results(task_id, results)
```

Frontend (React hook sketch)
```ts
const progress = useSomeFeatureProgress(taskId)
// hook will poll /api/v1/some-feature/progress/{taskId}
// when progress.completed -> fetch results
```

## 7) Deployment & infra notes

- Ensure CORS middleware is applied in the path that might return errors (including upstream proxy/gateway error handlers). If the gateway strips/changes headers for 50x pages, browsers will hide the response.
- For production, prefer same-site cookies or authorization headers and keep the API and web UI origins aligned when possible to reduce CORS complexity.

## 8) Implementation checklist for adding a new progress bar

1. Add `POST /<feature>/task` returning a `task_id`.
2. Accept `task_id` in the long-running action and update `progress:{task_id}` as work advances.
3. Add `GET /<feature>/progress/{task_id}` and `GET /<feature>/results/{task_id}`.
4. Implement `use<Feature>Progress` hook using the recommended polling pattern.
5. Add unit tests for the hook and backend progress-tracker helpers.
6. Add a small smoke/integration test to validate the end-to-end flow.

## 9) Troubleshooting checklist (when you see "Task not found or expired" or generic network errors)

- Check backend logs for Host and Origin headers for the failing request.
- Confirm Redis keys exist for `progress:{task_id}` and `progress:{task_id}:metadata`.
- Verify TTL on keys to ensure they didn't expire.
- If the browser shows a generic network error, open DevTools → Network and inspect the failing request; if response is HTML, it's likely a gateway error page without CORS — fix infra.
- Ensure the frontend isn't using a different base URL (OpenAPI.BASE) that causes cross-origin calls in dev; use same-origin fallback in hooks for local dev.

---

Created as a general, copyable guide to apply the same pattern across features. If you want, I can:
- Create a tiny code template (backend `task` + `progress` endpoints + a sample `progress_tracker` helper) under `backend/app/utils`.
- Add a test fixture and a unit test for the frontend hook.

Which of those should I do next?