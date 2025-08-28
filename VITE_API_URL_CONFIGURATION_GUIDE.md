# VITE_API_URL Configuration Guide

This document explains how to properly configure `VITE_API_URL` to prevent CORS errors in the AibenIQ React frontend deployment.

## Table of Contents
- [Problem Overview](#problem-overview)
- [Root Cause](#root-cause)
- [Solution Components](#solution-components)
- [Configuration Files](#configuration-files)
- [Deployment Steps](#deployment-steps)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Problem Overview

**Symptom**: Frontend shows CORS errors when trying to communicate with the backend:
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at https://api-aibeniq-prod.apps.your-cluster.com/api/v1/login/access-token. (Reason: CORS request did not succeed). Status code: (null).
```

**Root Issue**: Frontend is hardcoded with incorrect API URL instead of using the dynamically configured `VITE_API_URL`.

## Root Cause

Vite environment variables (`VITE_*`) are **build-time** variables that get baked into the JavaScript bundle during the build process. Unlike regular environment variables, they cannot be changed at runtime without rebuilding or patching the assets.

The issue occurs when:
1. Frontend is built with incorrect or placeholder API URL
2. Runtime environment variables don't affect already-built JavaScript
3. Frontend makes requests to wrong backend URL, causing CORS failures

## Solution Components

### 1. Dockerfile Configuration

**File**: `frontend/Dockerfile`

Key changes to ensure proper build-time variable handling:

```dockerfile
ARG VITE_API_URL
# Use the build arg if provided, otherwise use placeholder for runtime replacement
ENV VITE_API_URL=${VITE_API_URL:-__API_BASE__}

RUN echo "Building with VITE_API_URL=$VITE_API_URL" && npm run build
```

**Important**: The `ENV` instruction should use `${VITE_API_URL:-__API_BASE__}` syntax to:
- Use the build argument if provided
- Fall back to a replaceable placeholder if not provided

### 2. OpenShift BuildConfig

**File**: Referenced in OpenShift build configuration

Ensure the BuildConfig includes the correct build argument:

```yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: frontend-build
spec:
  strategy:
    dockerStrategy:
      buildArgs:
      - name: VITE_API_URL
        value: https://redhat-api.aiben.io  # Your actual API URL
```

### 3. Runtime Patching (Fallback Solution)

**File**: `frontend-patch.yaml`

If builds fail or for immediate fixes, use an init container to patch the JavaScript at runtime:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      initContainers:
        - name: copy-and-patch
          image: [frontend-image]
          command:
            - sh
            - -c
            - |
              echo "Copying original frontend assets..."
              cp -r /usr/share/nginx/html/* /app-assets/
              echo "Patching API URL in frontend assets..."
              find /app-assets -name "*.js" -exec sed -i 's|https://api-aibeniq-prod\.apps\.your-cluster\.com|https://redhat-api.aiben.io|g' {} \;
              echo "API URL patching complete"
          volumeMounts:
            - mountPath: /app-assets
              name: app-assets
      containers:
        - name: frontend
          volumeMounts:
            - mountPath: /usr/share/nginx/html
              name: app-assets
      volumes:
        - name: app-assets
          emptyDir: {}
```

## Configuration Files

### 1. Frontend Environment Files

**File**: `frontend/.env.production`
```env
VITE_API_URL=https://redhat-api.aiben.io
```

### 2. Frontend API Configuration

**File**: `frontend/src/config/api.ts`

The smart fallback configuration:

```typescript
// Centralized API base URL configuration
// Priority:
// 1. Explicit env variable (runtime injected via placeholder replacement)
// 2. Production fallback to known public host
// 3. Development fallback to localhost

const PUBLIC_HOST = "https://redhat-api.aiben.io";

// Vite exposes variables on import.meta.env; during docker runtime we replace placeholder
const envUrl = (import.meta as any).env?.VITE_API_URL as string | undefined;

// Derive a safe default
let base = envUrl?.trim();
if (!base) {
  if (typeof window !== "undefined" && window.location.hostname.includes("redhat")) {
    base = PUBLIC_HOST; // running in deployed redhat domain but env missing
  } else {
    base = "http://localhost:8000"; // local dev
  }
}

// Normalize (strip trailing slash)
export const API_BASE_URL = base.replace(/\/$/, "");
```

### 3. Backend CORS Configuration

**File**: `backend/app/core/config.py`

Ensure backend allows the frontend domain:

```python
BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = [
    "https://redhat.aiben.io",        # Frontend domain
    "https://redhat-api.aiben.io",    # API domain (for testing)
    "http://redhat.aiben.io",         # HTTP fallback
    "http://localhost:5173"           # Local development
]
```

## Deployment Steps

### For New Deployments

1. **Set BuildConfig correctly**:
   ```bash
   oc patch buildconfig frontend-build --type='merge' -p='{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"VITE_API_URL","value":"https://redhat-api.aiben.io"}]}}}}'
   ```

2. **Trigger new build**:
   ```bash
   oc start-build frontend-build
   ```

3. **Wait for build completion**:
   ```bash
   oc get builds | grep frontend
   ```

4. **Deploy new image**:
   ```bash
   oc rollout latest frontend
   ```

### For Emergency Fixes (Runtime Patching)

1. **Apply runtime patch**:
   ```bash
   oc patch deployment frontend --patch-file frontend-patch.yaml
   ```

2. **Wait for rollout**:
   ```bash
   oc rollout status deployment/frontend
   ```

## Verification

### 1. Check Built JavaScript

Verify the API URL is correctly set in the frontend assets:

```bash
# Get current frontend pod
FRONTEND_POD=$(oc get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}')

# Check for correct API URL
oc exec $FRONTEND_POD -- grep -r "redhat-api.aiben.io" /usr/share/nginx/html/

# Verify old URL is gone
oc exec $FRONTEND_POD -- grep -r "api-aibeniq-prod.apps.your-cluster.com" /usr/share/nginx/html/ || echo "Old URL successfully removed"
```

### 2. Test CORS

Test CORS preflight request:

```bash
curl -k -X OPTIONS \
  -H "Origin: https://redhat.aiben.io" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type,authorization" \
  https://redhat-api.aiben.io/api/v1/login/access-token -v
```

Should return:
```
< HTTP/1.1 200 OK
< access-control-allow-origin: https://redhat.aiben.io
< access-control-allow-credentials: true
< access-control-allow-headers: content-type,authorization
```

### 3. Browser Testing

1. **Clear browser cache**: Ctrl+Shift+Delete (Chrome) or equivalent
2. **Hard refresh**: Ctrl+F5 or Cmd+Shift+R
3. **Check Network tab**: Verify requests go to `https://redhat-api.aiben.io`
4. **Check Console**: No CORS errors should appear

## Troubleshooting

### Build Issues

**Problem**: BuildConfig fails to fetch source
```bash
# Check build logs
oc logs build/frontend-build-[number]

# Update branch reference if needed
oc patch buildconfig frontend-build --type='merge' -p='{"spec":{"source":{"git":{"ref":"[your-branch]"}}}}'
```

**Problem**: Build fails with context directory errors
```bash
# Use binary build instead
oc start-build frontend-build --from-dir=. --follow
```

### Runtime Issues

**Problem**: Frontend still shows old API URL
```bash
# Apply runtime patch immediately
oc patch deployment frontend --patch-file frontend-patch.yaml

# Force restart
oc rollout restart deployment/frontend
```

**Problem**: CORS still failing after fix
```bash
# Check backend environment
oc exec [backend-pod] -- printenv | grep CORS

# Verify route configuration
oc describe route backend-api
```

### Verification Commands

```bash
# Check current API configuration in browser console
console.log("Current API Base:", window.OpenAPI?.BASE || "Not set")

# Check environment variables in frontend pod
oc exec [frontend-pod] -- printenv | grep VITE

# Test backend accessibility
curl -k https://redhat-api.aiben.io/api/v1/utils/health-check/
```

## Best Practices

1. **Always use build arguments** for `VITE_API_URL` in production builds
2. **Test CORS configuration** before deploying
3. **Keep fallback logic** in `api.ts` for resilience
4. **Document environment-specific URLs** clearly
5. **Use runtime patching** only as emergency measure
6. **Verify builds complete successfully** before promoting to production

## Environment URLs Reference

| Environment | Frontend URL | Backend URL |
|-------------|-------------|-------------|
| Production | https://redhat.aiben.io | https://redhat-api.aiben.io |
| Local Development | http://localhost:5173 | http://localhost:8000 |

---

**Last Updated**: August 28, 2025  
**Applies to**: AibenIQ React Frontend v1.0+  
**Validated on**: OpenShift 4.x
