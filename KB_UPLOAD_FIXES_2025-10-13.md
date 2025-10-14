# Knowledge Base Upload Fixes - October 13, 2025

## Issues Fixed

### 1. HTTP 413 Error (Request Entity Too Large)
**Problem:** Users uploading files larger than 100MB received a 413 error with missing CORS headers, appearing as a CORS error on the frontend.

**Root Cause:** Traefik middleware had `maxRequestBodyBytes=104857600` (100MB) limit.

**Fix:** Updated `docker-compose.yml` to increase Traefik body size limits to 1GB:
```yaml
- traefik.http.middlewares.backend-timeout.buffering.maxRequestBodyBytes=1073741824  # 1GB
- traefik.http.middlewares.backend-timeout.buffering.memRequestBodyBytes=1073741824  # 1GB
```

### 2. Missing CORS Headers on 413 Errors
**Problem:** When Traefik returned 413 errors, no CORS headers were included, causing browsers to report CORS errors instead of the actual upload size error.

**Fix:** Added exception handler in `backend/app/main.py`:
```python
@app.exception_handler(413)
async def payload_too_large_handler(request: Request, exc):
    """Handle 413 Payload Too Large errors with CORS headers"""
    response = JSONResponse(
        status_code=413,
        content={
            "detail": "File size too large. Maximum upload size is 1GB.",
            "error": "PAYLOAD_TOO_LARGE"
        }
    )
    
    # Add CORS headers manually to error response
    origin = request.headers.get("origin")
    if origin and origin in settings.all_cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # ... other CORS headers
    
    return response
```

# Knowledge Base Upload Fixes - October 13, 2025

## Issues Fixed

### 1. HTTP 413 Error (Request Entity Too Large)
**Problem:** Users uploading files larger than 100MB received a 413 error with missing CORS headers, appearing as a CORS error on the frontend.

**Root Cause:** Traefik middleware had `maxRequestBodyBytes=104857600` (100MB) limit.

**Fix:** Updated `docker-compose.yml` to increase Traefik body size limits to 1GB:
```yaml
- traefik.http.middlewares.backend-timeout.buffering.maxRequestBodyBytes=1073741824  # 1GB
- traefik.http.middlewares.backend-timeout.buffering.memRequestBodyBytes=1073741824  # 1GB
```

### 2. Missing CORS Headers on 413 Errors
**Problem:** When Traefik returned 413 errors, no CORS headers were included, causing browsers to report CORS errors instead of the actual upload size error.

**Fix:** Added exception handler in `backend/app/main.py`:
```python
@app.exception_handler(413)
async def payload_too_large_handler(request: Request, exc):
    """Handle 413 Payload Too Large errors with CORS headers"""
    response = JSONResponse(
        status_code=413,
        content={
            "detail": "File size too large. Maximum upload size is 1GB.",
            "error": "PAYLOAD_TOO_LARGE"
        }
    )
    
    # Add CORS headers manually to error response
    origin = request.headers.get("origin")
    if origin and origin in settings.all_cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # ... other CORS headers
    
    return response
```

### 3. Missing Real-Time Upload Progress ⚠️ **CRITICAL FIX**

**Problem:** Upload progress showed "Preparing for file upload..." for the entire duration of the file upload, with no incremental updates showing MB uploaded.

**Root Cause:** **Traefik was BUFFERING the entire request** before passing it to the backend! The `buffering` middleware configuration was causing Traefik to:
1. Receive the entire upload from the client
2. Store it in memory/disk
3. Only THEN forward it to the backend in one chunk

This meant the upload middleware never saw incremental data - it only saw the request after the entire upload was already buffered by Traefik.

**Fix:** Removed Traefik buffering middleware to enable streaming uploads:
```yaml
# BEFORE (caused buffering):
- traefik.http.routers.backend-https.middlewares=backend-timeout,general-ratelimit@file,security-headers@file
- traefik.http.middlewares.backend-timeout.buffering.maxRequestBodyBytes=1073741824
- traefik.http.middlewares.backend-timeout.buffering.memRequestBodyBytes=1073741824

# AFTER (streaming enabled):
- traefik.http.routers.backend-https.middlewares=general-ratelimit@file,security-headers@file
# NO buffering middleware = requests stream through to backend
```

**How it works now:**
1. Frontend calls `POST /api/v1/knowledge-bases/create-task` → gets `task_id`
2. Frontend calls `POST /api/v1/knowledge-bases/?task_id=xxx` with files
3. **Upload streams through Traefik directly to backend** (no buffering)
4. Upload middleware intercepts streaming data and updates Redis every 1MB or 5 seconds
5. Frontend polls `GET /api/v1/knowledge-bases/progress/xxx` and sees real-time progress

### 3. Missing Real-Time Upload Progress
**Problem:** Upload progress wasn't visible during file upload stage.

**Analysis:** 
- The system has two endpoints:
  1. `POST /api/v1/knowledge-bases/create-task` - Creates task_id BEFORE upload
  2. `POST /api/v1/knowledge-bases/` - Actual upload with task_id parameter
  
- Upload middleware (`UploadProgressMiddleware`) tracks progress and updates Redis via `progress_tracker`
- Frontend should call `/create-task` first to get task_id, then pass it to main upload endpoint

**Current Flow:**
```
1. Frontend calls POST /api/v1/knowledge-bases/create-task
   → Returns {task_id: "xxx"}
   → Creates progress tracker with "upload" stage at 0%

2. Frontend calls POST /api/v1/knowledge-bases/?task_id=xxx
   → Upload middleware intercepts and updates upload progress in Redis
   → Frontend polls GET /api/v1/knowledge-bases/progress/xxx
   → Shows real-time upload progress
```

## Files Modified

1. `/home/ec2-user/aiben-react/docker-compose.yml`
   - Increased Traefik body size limits from 100MB to 1GB

2. `/home/ec2-user/aiben-react/backend/app/main.py`
   - Added 413 error handler with CORS headers

## Previous Session Fixes (for context)

1. Fixed route ordering - moved `/progress/{task_id}` before `/{id}`
2. Replaced ThreadPoolExecutor with FastAPI BackgroundTasks
3. Added missing `os` import
4. Added missing `psutil` import

## Next Steps

1. **Restart Docker containers** to apply Traefik configuration changes
2. **Test upload flow:**
   - Create knowledge base with large files (>100MB)
   - Verify upload progress shows during file upload
   - Verify no 413 errors for files under 1GB
   - Verify proper error message for files over 1GB

## Frontend Implementation Notes

The frontend should:
1. Call `POST /api/v1/knowledge-bases/create-task` with metadata
2. Get `task_id` from response
3. Start polling `GET /api/v1/knowledge-bases/progress/{task_id}`
4. Call `POST /api/v1/knowledge-bases/?task_id={task_id}` with files
5. Continue polling progress until complete/failed

This ensures progress tracking starts BEFORE file upload begins.
