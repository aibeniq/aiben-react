# Progress Bar Translation Status

**Date:** October 11, 2025  
**Issue:** Progress bars showing English even when Finnish is selected  

## Current Status

### ✅ COMPLETED (Frontend)
1. **Success toast messages** - Now use `t()` function:
   - `compare.tsx`: "Documents compared successfully!" → `t("compare.compareSuccess")`
   
2. **All translation keys added** to JSON files:
   - `common.progress.starting`, `initializing`, `processing`, `extracting`
   - `generate.progress.starting`, `initializing`
   - `compare.progress.starting`, `initializing`, `comparing`
   - `compare.compareSuccess`
   - `match.progress.starting`, `initializing`, `formatting`, `matching`
   - `match.matchSuccess`

3. **Finnish translations complete** for all new keys

### ⚠️ BACKEND ISSUE DISCOVERED

The progress bar messages are **coming from the backend** Python code. Looking at the Docker logs, I can see:

```
MESSAGE: Comparing and formatting results... Verrataan ja muotoillaan tulokset...
```

The backend is **already trying to send Finnish translations**, but it's sending BOTH English and Finnish in the same message string! This needs to be fixed on the **backend side**.

## What's Happening

### Progress Message Flow:
1. **Backend** sends progress updates via `/api/v1/{service}/progress/{task_id}`
2. **Frontend** receives these in progress hooks:
   - `useReportGenieProgress.ts` (Generate)
   - `useTwincheckProgress.ts` (Compare)  
   - `useFormconnectProgress.ts` (Match)
3. **Frontend displays** the `message` field directly from backend

### The Problem:
The backend Python code is sending hardcoded English messages OR mixed English/Finnish messages like:
- "Starting..."
- "Please wait while we generate your report"
- "Comparing and formatting results... Verrataan ja muotoillaan tulokset..."
- "Initializing"

## Solution Required

The **backend** needs to be updated to send translation keys instead of translated text, OR the backend needs to detect the user's language preference and send only the appropriate language.

### Option 1: Backend sends translation keys (RECOMMENDED)
Backend sends:
```json
{
  "message_key": "match.progress.formatting",
  "percentage": 85
}
```

Frontend translates:
```typescript
message: t(data.message_key)
```

### Option 2: Backend detects user language
- Backend reads user's language preference from session/JWT
- Backend sends pre-translated message in correct language
- Frontend displays as-is

### Option 3: Frontend message mapping (WORKAROUND)
Create a mapping of English messages to translation keys:
```typescript
const messageMap = {
  "Comparing and formatting results...": "match.progress.formatting",
  "Starting...": "common.progress.starting",
  // etc.
}
```

This is fragile and should be avoided.

## Files Modified (Frontend Only)

### Translation Files
- `/frontend/src/locales/en/common.json` - Added all progress keys
- `/frontend/src/locales/fi/common.json` - Added Finnish translations

### React Components  
- `/frontend/src/routes/_layout/compare.tsx` - Line 428: `t("compare.compareSuccess")`

## What Still Shows English

These messages come FROM THE BACKEND and cannot be fixed on frontend alone:

1. **GENERATE Progress Bar**:
   - "Starting..." ← Backend message
   - "Please wait while we generate your report" ← Already uses `t("generate.pleaseWait")` on frontend, but this may also come from backend

2. **COMPARE Progress Bar**:
   - "Starting..." ← Backend message  
   - "Please wait while we compare your documents" ← Backend message

3. **MATCH Progress Bar**:
   - "Initializing" ← Backend message
   - "Comparing and formatting results..." ← Backend message (shows mixed EN/FI)

## Backend Files to Investigate

Based on the services, these Python files likely need updates:

1. **ReportGenie (Generate)**:
   - `/backend/app/api/routes/reportgenie.py`
   - Look for progress update calls with hardcoded messages

2. **TwinCheck (Compare)**:
   - `/backend/app/api/routes/twincheck.py`
   - Look for progress update calls

3. **FormConnect (Match)**:
   - `/backend/app/api/routes/formconnect.py`
   - Look for progress update calls  
   - The log shows: "Comparing and formatting results... Verrataan ja muotoillaan tulokset..." - this is the issue!

## Recommendation

**BACKEND TEAM**: Update all progress message calls to send translation keys instead of hardcoded text. The frontend already has all the necessary translations ready.

Example backend change needed:
```python
# BEFORE
await save_progress(task_id, {
    "message": "Comparing and formatting results...",
    "percentage": 85
})

# AFTER
await save_progress(task_id, {
    "message_key": "match.progress.formatting",
    "percentage": 85
})
```

Frontend will handle the translation automatically.
