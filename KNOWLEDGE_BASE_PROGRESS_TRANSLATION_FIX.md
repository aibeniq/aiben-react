# Knowledge Base Progress Translation Fix

## Issue Summary
When creating a knowledge base with Spanish as the selected language, the progress bar label only displayed "Procesando..." without providing translations for different stages (e.g., processing, embedding, chunking, storing). Additionally, the upload middleware wasn't properly tracking megabytes being uploaded.

## Root Causes Identified

### 1. Translation Key Bug in Frontend Hook
**Location:** `frontend/src/hooks/useKnowledgeBaseProgress.ts`

**Problem:** The hook was using `progress.message_key` (from the old state) instead of `(data as any).message_key` (from the API response). This meant the translation keys sent from the backend were never being applied.

**Code Issue (lines 104-106):**
```typescript
const message = progress.message_key
  ? t(progress.message_key, progress.message_params)
  : progress.message
```

**Fix:** Changed to use the API response data:
```typescript
const message = (data as any).message_key
  ? t((data as any).message_key, (data as any).message_params || {})
  : (data as any).message
```

### 2. Missing Translation Keys
**Locations:** 
- `frontend/src/locales/en/common.json`
- `frontend/src/locales/es/common.json`

**Problem:** Both English and Spanish locale files were missing translation keys for:
- `knowledgeBases.progress.chunking`
- `knowledgeBases.progress.embedding`
- `knowledgeBases.progress.storing`
- `knowledgeBases.progress.finalizing`

**Fix:** Added all missing keys to both files.

### 3. Upload Middleware Not Using Translation Keys
**Location:** `backend/app/middleware/upload_middleware.py`

**Problem:** The upload middleware was tracking progress but not using `message_key` and `message_params` for i18n support.

**Fix:** Updated `update_stage_progress` and `complete_stage` calls to include:
```python
message_key="knowledgeBases.progress.uploading",
message_params={"current": received_mb, "total": total_mb}
```

### 4. Progress Tracker Missing message_params Support
**Location:** `backend/app/services/progress_tracker.py`

**Problem:** The `ProgressStage` and `ProgressData` dataclasses didn't have a `message_params` field, and `complete_stage` method didn't accept it.

**Fix:** 
- Added `message_params: Optional[dict] = None` to both dataclasses
- Updated `complete_stage` method signature to accept `message_params`

## Files Modified

### Frontend
1. **frontend/src/hooks/useKnowledgeBaseProgress.ts**
   - Fixed translation key retrieval to use API response instead of old state
   - Added message_key and message_params to ProgressData state

2. **frontend/src/locales/en/common.json**
   - Added missing progress translation keys:
     - `chunking`: "Chunking document {{current}}/{{total}}..."
     - `embedding`: "Creating embeddings {{current}}/{{total}}..."
     - `storing`: "Storing data {{current}}/{{total}}..."
     - `finalizing`: "Finalizing creation {{current}}/{{total}}..."

3. **frontend/src/locales/es/common.json**
   - Added Spanish translations:
     - `chunking`: "Dividiendo el documento {{current}}/{{total}}..."
     - `embedding`: "Creando incrustaciones {{current}}/{{total}}..."
     - `storing`: "Almacenando datos {{current}}/{{total}}..."
     - `finalizing`: "Finalizando creación {{current}}/{{total}}..."

### Backend
1. **backend/app/middleware/upload_middleware.py**
   - Updated progress tracking to use `message_key` and `message_params`
   - Now properly supports i18n for upload progress messages

2. **backend/app/services/progress_tracker.py**
   - Added `message_params` field to `ProgressStage` dataclass
   - Added `message_params` field to `ProgressData` dataclass
   - Updated `complete_stage` method to accept and handle `message_params`

## Testing Recommendations

1. **Spanish Language Test:**
   - Set language to Spanish in the UI
   - Create a new knowledge base with file uploads
   - Verify all progress stages show proper Spanish translations:
     - Upload stage: "Preparando para la carga de archivos..."
     - Processing stage: "Procesando archivo X/Y: filename"
     - Chunking stage: "Dividiendo el documento X/Y..."
     - Embedding stage: "Creando incrustaciones X/Y..."
     - Storing stage: "Almacenando datos X/Y..."
     - Finalizing stage: "Finalizando creación X/Y..."

2. **Upload Progress Test:**
   - Upload large files (>1MB) to trigger upload middleware
   - Check backend logs for "📊 UPLOAD PROGRESS" messages
   - Verify progress bar shows upload percentage

3. **Multi-language Test:**
   - Test with other languages to ensure fallback to English works
   - Switch language mid-upload to verify dynamic translation

## Benefits

1. ✅ **Proper i18n Support:** All progress stages now properly translate based on user's selected language
2. ✅ **Upload Tracking:** Upload middleware now properly tracks and displays file upload progress
3. ✅ **Consistent UX:** Users see meaningful progress messages at each stage in their language
4. ✅ **Debugging:** Enhanced logging in middleware and progress tracker for troubleshooting

## Backend Progress Flow

The knowledge base creation process now properly tracks these stages:

1. **Upload (10% weight)** - File upload via middleware
2. **Processing (30% weight)** - Extract text from files
3. **Chunking (20% weight)** - Split documents into chunks
4. **Embedding (30% weight)** - Create vector embeddings
5. **Storing (10% weight)** - Save to database

Each stage reports progress with i18n keys that get translated on the frontend based on the user's language preference.

## Date
October 12, 2025
