## AibenIQ OpenShift CORS Avoidance Guide & Checklist

Comprehensive, action‑oriented reference for preventing and resolving CORS issues between the React (Vite) frontend and FastAPI backend on Red Hat OpenShift.

---

### Core Principles

1. Vite `VITE_*` vars are build‑time; wrong value => must rebuild (or emergency patch built assets).
2. Backend must explicitly allow every browser origin (scheme + host, no trailing slash) via CORS middleware.
3. Frontend JS must call the API host exactly as whitelisted; mismatches (protocol / host / port) trigger CORS failures.
4. Route TLS termination (edge) means the browser origin is `https://<route-host>` even if the backend pod listens on HTTP.
5. Minimize origins: only production frontend, API (if needed), and localhost for dev.

### Touchpoints

| Layer                       | Concern                 | Artifact                                                            |
| --------------------------- | ----------------------- | ------------------------------------------------------------------- |
| Frontend build              | Inject correct API base | Dockerfile build arg `VITE_API_URL` / BuildConfig `buildArgs`       |
| Frontend runtime (fallback) | Emergency sed patch     | `frontend-patch.yaml` initContainer strategy                        |
| Backend config              | Allowed origins list    | `BACKEND_CORS_ORIGINS`, `FRONTEND_HOST` in `settings` (`config.py`) |
| OpenShift routing           | Public origins & TLS    | `Route` objects (frontend + backend)                                |
| Monitoring / Diagnostics    | Runtime confirmation    | `GET /api/v1/utils/cors-origins`                                    |

### Failure Modes & Symptoms

| Symptom                                         | Likely Cause                                          | Fix                                                 |
| ----------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------- |
| Browser CORS error (preflight failed)           | Origin not in backend list                            | Add origin, restart backend                         |
| Requests using old cluster host                 | Stale built JS                                        | Rebuild with correct `VITE_API_URL` or patch assets |
| Access-Control-Allow-Origin echoes wrong domain | Mismatched value order / placeholder fallback misused | Verify env + backend config; rebuild                |
| Works locally, fails prod                       | `BACKEND_CORS_ORIGINS` empty / using defaults         | Set production origins explicitly                   |
| OPTIONS 403 or no CORS headers                  | Middleware not mounted                                | Ensure list not empty so middleware added           |

---

## Preventative Checklist (Pre-Build)

- [ ] Confirm target frontend route host (e.g. `redhat.aiben.io`).
- [ ] Confirm backend API route host (e.g. `redhat-api.aiben.io`).
- [ ] Update BuildConfig: buildArg `VITE_API_URL=https://redhat-api.aiben.io`.
- [ ] Inspect frontend sources: no hardcoded legacy hosts (grep old domain strings).
- [ ] Dockerfile uses `ARG VITE_API_URL` then `ENV VITE_API_URL=${VITE_API_URL:-__API_BASE__}`.
- [ ] If domains changed, bump image tag (avoid stale `:latest`).

## Backend Configuration Checklist

- [ ] `BACKEND_CORS_ORIGINS` includes each required https origin (no trailing slash).
- [ ] `FRONTEND_HOST` set to primary frontend origin.
- [ ] No wildcard `*` when `allow_credentials=True` (cookies / auth headers).
- [ ] Local dev origin (`http://localhost:5173`) only present when needed.
- [ ] Runtime validation: `GET /api/v1/utils/cors-origins` returns expected list.

## OpenShift Deployment Checklist

- [ ] Frontend Route host matches `FRONTEND_HOST` / expected user URL.
- [ ] Backend Route host matches `VITE_API_URL` (the origin inside built JS minus path).
- [ ] TLS termination: using `edge` ⇒ origins must use `https://`.
- [ ] Frontend Deployment: `VITE_API_URL` env only if runtime placeholder replacement is implemented; otherwise keep minimal.
- [ ] Deploy (or restart) backend before switching frontend to new origin (avoid transient mismatch).

## Build & Deploy Order

1. Update backend allowed origins.
2. Rollout / restart backend.
3. Rebuild frontend with correct `VITE_API_URL`.
4. Deploy new frontend image.
5. Clear CDN / browser caches if applicable.

## Post-Deploy Verification

- [ ] Inspect frontend pod assets: `grep -r "redhat-api.aiben.io" /usr/share/nginx/html` (present).
- [ ] Old host string NOT present.
- [ ] Preflight OPTIONS to auth endpoint returns 200 and correct `Access-Control-Allow-Origin`.
- [ ] Browser Network tab: API calls target expected host.
- [ ] Console: No CORS errors after hard refresh (Ctrl+F5) & cache clear.
- [ ] `/api/v1/utils/cors-origins` output aligns with expected list.

## Emergency Runtime Patch Procedure

Use only when an incorrect `VITE_API_URL` was baked:

1. Apply `frontend-patch.yaml` (initContainer copies + sed replaces old host with new).
2. Wait for rollout.
3. Verify patched assets.
4. Schedule proper image rebuild; remove patch after confirmation.

## Decision Tree (Troubleshooting)

1. CORS error? → Check Network request URL vs intended API base.
2. URL wrong? → Rebuild or patch frontend assets.
3. URL right but blocked? → Curl preflight → Missing/incorrect header? → Check backend `/utils/cors-origins`.
4. Origin absent? → Fix `BACKEND_CORS_ORIGINS` / `FRONTEND_HOST`, restart backend.
5. Credentials failing? → Ensure `allow_credentials=True` and no `*`; confirm origin exact match.
6. Mixed http/https? → Standardize on `https://` for production and list that exact scheme.

## Curl / PowerShell Test Snippets

Preflight:

```powershell
curl -Method Options `
  -Uri https://redhat-api.aiben.io/api/v1/login/access-token `
  -Headers @{ Origin='https://redhat.aiben.io'; 'Access-Control-Request-Method'='POST'; 'Access-Control-Request-Headers'='content-type,authorization' } -Verbose
```

Runtime CORS config:

```powershell
curl https://redhat-api.aiben.io/api/v1/utils/cors-origins -H "Origin: https://redhat.aiben.io"
```

## Automation Opportunities

- CI grep to fail build if legacy domains appear outside allowlist.
- CI asserts `BACKEND_CORS_ORIGINS` non-empty for production image builds.
- Nightly preflight probe script; alert on missing headers / non-200.
- Sentry breadcrumb or log marker on CORS failures for early detection.

## Edge Cases

- Trailing slash confusion (normalized in settings by `rstrip('/')`).
- Domain migration: stage backend origin list BEFORE switching DNS / frontend build.
- Concurrent dev + prod usage: ensure distinct images with distinct `VITE_API_URL` build args.
- Removing emergency patch: validate new bundle first, then delete initContainer patch.

## Fast Sanity Checklist (Print This)

Build:

- [ ] Correct build arg set
- [ ] No stale host strings

Backend:

- [ ] Origins list accurate
- [ ] Middleware active

Routes:

- [ ] Hosts final & https

Deploy:

- [ ] Backend updated first
- [ ] Frontend rebuilt & rolled out

Verify:

- [ ] Bundle API host correct
- [ ] Preflight 200 + expected AC-Allow-Origin
- [ ] No console CORS errors

Fallback:

- [ ] Patch plan ready (initContainer) if needed

Monitor:

- [ ] Automated preflight
- [ ] Log scan for CORS failures

## Removal of Emergency Patch (If Used)

1. Rebuild with correct API URL.
2. Rollout new image (ensure patch removed from Deployment spec).
3. Confirm assets contain ONLY new host string.
4. Document closure in ops log / ticket.

## Quick Grep Commands (Linux container context)

```bash
grep -r "redhat-api.aiben.io" /usr/share/nginx/html/ | head
grep -r "api-aibeniq-prod.apps" /usr/share/nginx/html/ || echo "Old host removed"
```

## Summary

Following this checklist prevents almost all CORS incidents by enforcing correct build-time API embedding, explicit backend origin whitelisting, and verifiable runtime diagnostics. Keep origins tight, rebuild on change, patch only in emergencies, and automate verification.

---

Last Updated: 2025-08-28
Owner: Platform / DevOps
