# Knowledge Base Creation and Progress Tracking

## Overview

This document provides a comprehensive guide to the Knowledge Base creation process, including real-time progress tracking, frontend-backend integration, and troubleshooting common issues.

## Process Flow

### High-Level Architecture

1. **Task Creation**: Frontend calls `POST /api/v1/knowledge-bases/create-task` to get a `task_id`
2. **File Upload**: Frontend calls `POST /api/v1/knowledge-bases/` with files and `task_id`
3. **Background Processing**: Backend processes files asynchronously with progress updates
4. **Progress Polling**: Frontend polls `GET /api/v1/knowledge-bases/progress/{task_id}` for updates
5. **Completion**: Frontend detects completion and fetches results

### Two-Step Upload Process

The system uses a two-step process to handle large file uploads efficiently:

1. **Step 1: File Reading into Memory**
   - Files are read entirely into memory as bytes
   - This allows passing data to background tasks (UploadFile objects can't be serialized)
   - Enables upfront validation and size calculation

2. **Step 2: Saving to Disk in Background**
   - Background task saves files to temporary storage
   - Processes documents and creates embeddings
   - Updates progress throughout the operation

## Progress Tracking Stages

### Weighted Progress Stages

The creation process is divided into 6 stages with the following weights:

- **Upload (20%)**: File upload and validation
- **Processing (20%)**: Text extraction from files
- **Chunking (20%)**: Document splitting into chunks
- **Embedding (20%)**: Creating vector embeddings
- **Storing (17%)**: Saving to database
- **Finalizing (3%)**: Creating source entries and cleanup

### Progress Messages

#### Upload Stage (0-20%)
- "Reading file 1/8: document.pdf"
- "All 8 files uploaded successfully"

#### Processing Stage (20-40%)
- "Processing file 1/8: document.pdf"
- "Processed 15 documents from 1/8 files"
- "Processed 108 documents from 8 files successfully"

#### Chunking Stage (40-60%)
- "Starting document splitting and chunking for 108 documents..."
- "Split 108 documents into 596 chunks"

#### Embedding Stage (60-80%)
- "Creating embeddings: 1/596"
- "Creating embeddings: 596/596"

#### Storing Stage (80-97%)
- "Compressing and storing data..."
- "Data stored successfully"

#### Finalizing Stage (97-100%)
- "Creating source entries..."
- "Knowledge base created successfully"

## Frontend Implementation

### Hook Pattern: `useKnowledgeBaseProgress`

```typescript
const progress = useKnowledgeBaseProgress(taskId)

// Returns:
{
  percentage: 42,
  message: "Processing file 2/5: document.pdf",
  isActive: true,
  completed: false,
  error: null,
  results: null
}
```

### Key Features

- **Polling Strategy**: Polls every 1000ms with transient error handling
- **Completion Detection**: Handles completion when `status === 'completed'` and `percentage > 80`
- **Error Handling**: Supports retry logic and same-origin fallbacks
- **State Management**: Prevents race conditions and duplicate toasts

### Modal Implementation

The creation modal (`AddKnowledgeBase.tsx`) handles:

1. **Task Creation**: Calls `createKnowledgeBaseTask()` first
2. **File Upload**: Uploads files with the `task_id`
3. **Progress Display**: Shows progress bar with real-time updates
4. **Completion Handling**: Closes modal and shows success toast
5. **Error Handling**: Shows error messages and allows retry

## Backend Implementation

### Core Components

1. **Progress Tracker** (`progress_tracker.py`): Redis-based progress persistence
2. **Upload Middleware** (`upload_middleware.py`): Real-time upload progress tracking
3. **Knowledge Base Service** (`knowledgebases.py`): Main processing logic

### Key Endpoints

- `POST /api/v1/knowledge-bases/create-task`: Creates task and returns `task_id`
- `POST /api/v1/knowledge-bases/`: Main upload endpoint with background processing
- `GET /api/v1/knowledge-bases/progress/{task_id}`: Progress polling endpoint

### Background Processing Flow

```python
async def process_knowledge_base_creation(
    task_id: str,
    knowledge_base_id: uuid.UUID,
    file_paths: List[dict],
    temp_dir: str,
    user_id: uuid.UUID,
    embedding_model_id: uuid.UUID,
    user_language: str = "en",
):
    # 1. Load and process documents
    # 2. Create chunks
    # 3. Generate embeddings
    # 4. Store in database
    # 5. Update progress throughout
    # 6. Handle errors gracefully
```

### Memory Management

- **Streaming ZIP Creation**: Avoids loading entire ZIP files into memory
- **Memory Monitoring**: Automatic cleanup when usage >75%
- **Chunked Processing**: Processes documents in batches to prevent OOM

## Common Issues and Fixes

### 1. Progress Stuck at 0%

**Symptoms**: UI shows "Ladataan 0 MB/0 MB" indefinitely

**Root Cause**: File reading and validation takes too long for large uploads

**Fix**: 
- Optimize file reading loop
- Add progress updates during reading
- Consider streaming approach for very large files

### 2. Progress Stuck at 80%

**Symptoms**: Processing completes but progress shows 80%

**Root Cause**: Upload stage never marked as completed

**Fix**:
- Ensure `progress_tracker.complete_stage(task_id, "upload")` is called
- Verify all stages complete properly

### 3. 404 Errors on Progress Endpoint

**Symptoms**: Progress polling returns 404

**Root Cause**: FastAPI route ordering issue

**Fix**:
- Move specific routes before generic `/{id}` routes
- Ensure `/progress/{task_id}` comes before `/{id}`

### 4. Background Processing Not Starting

**Symptoms**: Progress stuck at 20%, no further updates

**Root Cause**: ThreadPoolExecutor termination or FastAPI BackgroundTasks not used

**Fix**:
- Use `background_tasks.add_task()` instead of ThreadPoolExecutor
- Ensure async functions are properly awaited

### 5. Race Conditions in Frontend

**Symptoms**: Success toast shown immediately on second KB creation

**Root Cause**: Progress state not reset properly between tasks

**Fix**:
- Reset completion handler before setting new task_id
- Use refs instead of state for internal counters

### 6. CORS Errors

**Symptoms**: "Network Error" during progress polling

**Root Cause**: Missing CORS headers or caching

**Fix**:
- Add `expose_headers=["*"]` and `max_age=3600` to CORS middleware
- Ensure all error responses include CORS headers

### 7. Memory Issues

**Symptoms**: OOM crashes during large KB creation

**Root Cause**: Inefficient memory usage in ZIP compression

**Fix**:
- Use streaming ZIP creation
- Monitor memory usage and trigger GC
- Process in smaller batches

## Testing

### Unit Tests

```python
# Test progress tracker
def test_progress_tracking():
    task_id = progress_tracker.create_task("Test task", 100)
    progress_tracker.update_stage_progress(task_id, "upload", 50, 100, "Uploading...")
    progress = progress_tracker.get_progress(task_id)
    assert progress["percentage"] == 50

# Test frontend hook
const { result } = renderHook(() => useKnowledgeBaseProgress("test-task"))
expect(result.current.isActive).toBe(true)
```

### Integration Tests

1. **Create Knowledge Base**: Upload files and verify progress updates
2. **Progress Polling**: Ensure frontend receives all backend updates
3. **Completion Handling**: Verify modal closes and success toast appears
4. **Error Handling**: Test with invalid files and network failures

### Load Testing

- Test with 1000+ PDFs
- Verify memory usage stays within limits
- Check progress accuracy with large datasets

## Deployment Notes

### Environment Variables

```bash
# Redis for progress tracking
REDIS_URL=redis://localhost:6379

# File upload limits
MAX_UPLOAD_SIZE=1073741824  # 1GB

# Memory thresholds
MEMORY_WARNING_THRESHOLD=75
MEMORY_CRITICAL_THRESHOLD=90
```

### Docker Configuration

```yaml
# Traefik for load balancing
- traefik.http.middlewares.backend-timeout.buffering.maxRequestBodyBytes=1073741824

# CORS headers
expose_headers: ["*"]
max_age: 3600
```

### Monitoring

- **Redis Keys**: Monitor progress key TTL and cleanup
- **Memory Usage**: Track peak usage during KB creation
- **Progress Accuracy**: Ensure percentage calculations match actual progress

## Performance Optimizations

### For Large Knowledge Bases

1. **Batch Processing**: Process documents in chunks
2. **Memory Management**: Use streaming for large files
3. **Progress Updates**: Balance update frequency with performance
4. **Database Optimization**: Use bulk inserts for embeddings

### Scaling Considerations

- **Horizontal Scaling**: Multiple backend instances with shared Redis
- **Queue System**: Use Celery for very large processing jobs
- **Caching**: Cache embeddings and document chunks

## Troubleshooting Checklist

### When Progress Gets Stuck

1. Check backend logs for processing activity
2. Verify Redis keys exist: `progress:{task_id}`
3. Check route ordering in FastAPI
4. Ensure background tasks are properly scheduled
5. Verify CORS configuration

### When Memory Issues Occur

1. Monitor memory usage during processing
2. Check for memory leaks in background tasks
3. Verify streaming ZIP creation is working
4. Adjust batch sizes for processing

### When Frontend Doesn't Update

1. Check network tab for failed requests
2. Verify task_id is correctly passed
3. Check for race conditions in state management
4. Ensure polling interval is active

## Future Enhancements

1. **WebSocket Support**: Real-time progress updates without polling
2. **Partial Results**: Show results as they become available
3. **Cancellation**: Allow users to cancel long-running operations
4. **Resume**: Support resuming interrupted uploads
5. **Progress Persistence**: Store progress across browser sessions

---

This document consolidates all knowledge base creation and progress tracking functionality. For specific implementation details, refer to the individual component documentation.

---

# Knowledge Base Upload Streaming Refactoring Plan

## Problem Statement

The current knowledge base creation process is extremely memory-inefficient for large uploads:

1. **Full File Buffering**: All uploaded files are read entirely into memory as bytes in the main endpoint
2. **Double Storage**: Files are stored in memory as `file_data` list, then written to disk again in background processing
3. **Memory Scaling Issues**: For 1000 PDFs (potentially 1GB+), this requires loading everything into RAM simultaneously
4. **OOM Risk**: Large uploads can cause out-of-memory crashes before processing even begins

## Current Implementation Analysis

### Memory Usage Pattern

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1075-1095)

```python
# Current: Load all files into memory
file_data = []
for file in files:
    content = await file.read()  # ❌ Loads entire file into RAM
    file_data.append({
        "filename": file.filename,
        "content": content,  # ❌ Stores bytes in memory
        "content_type": file.content_type,
        "size": len(content)
    })

# Later in background task:
for file_info in file_data:
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(file_info['content'])  # ❌ Writes from memory to disk
```

**Memory Peak**: `sum(file_sizes) + overhead` - all files loaded simultaneously

## Proposed Streaming Refactoring

### Core Concept

**Stream files directly to temporary storage during upload validation, then pass file paths to background processing.**

### Benefits

1. **Memory Efficiency**: Files never fully loaded into memory simultaneously
2. **Streaming Processing**: Handle files as they arrive without buffering
3. **Scalability**: Support arbitrarily large uploads limited only by disk space
4. **Error Recovery**: Failed validations don't waste memory on invalid files
5. **Progress Tracking**: Real-time upload progress without memory pressure

### Architecture Changes

#### 1. New Streaming File Handler

Create a new utility class for streaming file operations:

**File**: `backend/app/utils/streaming_file_handler.py` (NEW)

```python
class StreamingFileHandler:
    @staticmethod
    async def stream_to_temp_storage(
        upload_file: UploadFile,
        temp_dir: str,
        validator: FileValidator = None
    ) -> dict:
        """Stream file directly to temp storage with validation."""
        # Implementation below
```

#### 2. Modified Upload Endpoint

Replace memory buffering with streaming:

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1075-1095)

```python
# BEFORE: Memory-intensive
file_data = []
for file in files:
    content = await file.read()  # ❌
    file_data.append({"content": content, ...})

# AFTER: Streaming
temp_dir = tempfile.mkdtemp(prefix="kb_upload_")
file_paths = []
for file in files:
    file_info = await StreamingFileHandler.stream_to_temp_storage(
        file, temp_dir, FileValidator()
    )
    file_paths.append(file_info)
```

#### 3. Background Task Interface Change

Pass file paths instead of file contents:

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1115-1125)

```python
# BEFORE: Memory-heavy
background_tasks.add_task(
    process_knowledge_base_background,
    file_data=file_data,  # ❌ Contains all file bytes
    ...
)

# AFTER: Path-based
background_tasks.add_task(
    process_knowledge_base_background,
    file_paths=file_paths,  # ✅ Just file paths and metadata
    temp_dir=temp_dir,
    ...
)
```

## Implementation Plan

### Phase 1: Core Streaming Infrastructure

#### 1.1 Create StreamingFileHandler Class

**File**: `backend/app/utils/streaming_file_handler.py` (NEW)

```python
import tempfile
import os
from typing import Dict, Optional
from fastapi import UploadFile
from app.services.file_validator import FileValidator

class StreamingFileHandler:
    
    @staticmethod
    async def stream_to_temp_storage(
        upload_file: UploadFile,
        temp_dir: str,
        validator: Optional[FileValidator] = None,
        chunk_size: int = 8192
    ) -> Dict:
        """
        Stream upload file directly to temporary storage.
        
        Args:
            upload_file: FastAPI UploadFile object
            temp_dir: Directory to store temp files
            validator: Optional file validator
            chunk_size: Size of chunks to read/write
            
        Returns:
            Dict with file metadata and temp path
        """
        # Validate file first (headers only, no content read)
        if validator:
            is_valid, reason = await validator.validate_upload_headers(upload_file)
            if not is_valid:
                raise ValueError(f"File validation failed: {reason}")
        
        # Create safe filename
        safe_filename = sanitize_filename(upload_file.filename)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{safe_filename}")
        
        file_size = 0
        try:
            with open(temp_path, "wb") as temp_file:
                while chunk := await upload_file.read(chunk_size):
                    temp_file.write(chunk)
                    file_size += len(chunk)
                    
                    # Optional: Progress callback here
                    # await progress_callback(file_size)
            
            # Final validation if needed
            if validator:
                is_valid, reason = validator.validate_temp_file(temp_path, upload_file.filename)
                if not is_valid:
                    os.unlink(temp_path)
                    raise ValueError(f"Post-upload validation failed: {reason}")
            
            return {
                "original_filename": upload_file.filename,
                "safe_filename": safe_filename,
                "temp_path": temp_path,
                "content_type": upload_file.content_type,
                "size": file_size,
                "temp_dir": temp_dir
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
```

#### 1.2 Update FileValidator for Streaming

**File**: `backend/app/services/file_validator.py` (MODIFY)

Add streaming-compatible validation methods:

```python
class FileValidator:
    @staticmethod
    async def validate_upload_headers(upload_file: UploadFile) -> tuple[bool, str]:
        """Validate file without reading content."""
        # Check filename, content-type, etc.
        pass
    
    @staticmethod
    def validate_temp_file(temp_path: str, original_filename: str) -> tuple[bool, str]:
        """Validate file that has been streamed to temp storage."""
        # Check file size, content, etc.
        pass
```

### Phase 2: Endpoint Refactoring

#### 2.1 Modify create_knowledge_base Endpoint

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1075-1125)

Replace the file reading loop:

```python
# OLD: Memory-intensive approach
file_data = []
total_size = 0
for i, file in enumerate(files):
    is_valid, reason = FileValidator.validate_upload(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' rejected: {reason}")

    content = await file.read()  # ❌ Loads entire file into memory
    safe_filename = sanitize_filename(file.filename)
    file_info = {
        "filename": safe_filename,
        "content": content,  # ❌ Stores bytes in memory
        "content_type": file.content_type,
        "size": len(content)
    }
    file_data.append(file_info)
    total_size += len(content)
    await file.seek(0)  # Reset file pointer

# NEW: Streaming approach
from app.utils.streaming_file_handler import StreamingFileHandler

temp_dir = tempfile.mkdtemp(prefix=f"kb_upload_{task_id}_")
file_paths = []
total_size = 0

try:
    for i, file in enumerate(files):
        # Update progress during streaming
        progress_tracker.update_stage_progress(
            task_id, "upload", i, len(files),
            f"Streaming file {i + 1}/{len(files)}: {file.filename}"
        )
        
        # Stream file directly to temp storage
        file_info = await StreamingFileHandler.stream_to_temp_storage(
            file, temp_dir, FileValidator()
        )
        file_paths.append(file_info)
        total_size += file_info["size"]
        
        # Yield control to prevent blocking
        await asyncio.sleep(0.01)
    
    # Complete upload stage
    progress_tracker.complete_stage(task_id, "upload", 
        f"Successfully streamed {len(files)} files ({total_size / (1024*1024):.1f}MB)")

except Exception as e:
    # Clean up temp directory on error
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    progress_tracker.fail_task(task_id, f"Upload failed: {str(e)}")
    raise
```

#### 2.2 Update Background Task Interface

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1115-1125)

Modify the background task call:

```python
# OLD: Pass file data
background_tasks.add_task(
    process_knowledge_base_background,
    knowledge_base_id=knowledge_base.id,
    task_id=task_id,
    file_data=file_data,  # ❌ Contains all bytes
    current_user_id=current_user.id,
    user_language=user_language,
)

# NEW: Pass file paths
background_tasks.add_task(
    process_knowledge_base_background,
    knowledge_base_id=knowledge_base.id,
    task_id=task_id,
    file_paths=file_paths,  # ✅ Just metadata and paths
    temp_dir=temp_dir,      # ✅ Temp directory for cleanup
    current_user_id=current_user.id,
    user_language=user_language,
)
```

### Phase 3: Background Processing Updates

#### 3.1 Update process_knowledge_base_background

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1130-1200)

Remove the file saving loop since files are already on disk:

```python
async def process_knowledge_base_background(
    knowledge_base_id: uuid.UUID,
    task_id: str,
    file_paths: List[dict],  # ✅ Now contains temp paths instead of content
    temp_dir: str,           # ✅ Temp directory for cleanup
    current_user_id: uuid.UUID,
    user_language: str = "en",
) -> None:
    """Background processing for knowledge base creation with streaming files."""
    try:
        with Session(engine) as session:
            knowledge_base = session.get(KnowledgeBase, knowledge_base_id)
            if not knowledge_base:
                progress_tracker.fail_task(task_id, "Knowledge base not found")
                return
            
            print(f"📊 Processing {len(file_paths)} streamed files in background")
            
            # Files are already saved to temp storage - no need to save again
            # Just proceed with existing processing logic
            await process_knowledge_base_creation(
                task_id=task_id,
                knowledge_base_id=knowledge_base_id,
                file_paths=file_paths,  # ✅ Already contain temp_path
                temp_dir=temp_dir,
                user_id=current_user_id,
                embedding_model_id=knowledge_base.embedding_model_id,
                user_language=user_language,
            )
            
    except Exception as e:
        # Clean up temp directory on error
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        progress_tracker.fail_task(task_id, f"Background processing failed: {str(e)}")
    finally:
        # Ensure temp directory cleanup
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to clean up temp directory {temp_dir}: {cleanup_error}")
```

### Phase 4: Integration with Existing Streaming Patterns

#### 4.1 Leverage Existing document_utils.py Streaming

**File**: `backend/app/services/document_utils.py` (lines 350-500)

The `extract_documents_from_file_unified` function already streams files properly:

```python
def extract_documents_from_file_unified(
    file_path: str,  # ✅ Takes file path instead of content
    filename: str
) -> List[Document]:
    """Extract documents from file path (already streaming-compatible)."""
    # Implementation uses temp files for processing
```

Update the processing loop to use file paths:

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1400-1450)

```python
# In process_knowledge_base_creation
for file_info in file_paths:
    # Use existing streaming function
    documents = extract_documents_from_file_unified(
        file_info["temp_path"],  # ✅ File path instead of content
        file_info["original_filename"]
    )
```

#### 4.2 Use Existing MemoryManager Streaming

**File**: `backend/app/utils/memory_manager.py` (lines 69-84)

The `MemoryManager.create_streaming_zip_from_directory` is already implemented and used.

## Memory Usage Comparison

### Current Implementation
- **Peak Memory**: `sum(all_file_sizes) + processing_overhead`
- **Example**: 1000 PDFs × 1MB each = 1GB+ RAM usage
- **Failure Point**: File reading loop in main endpoint

### Streaming Implementation
- **Peak Memory**: `max_file_size + processing_overhead`
- **Example**: Single largest PDF + processing = ~50MB RAM usage
- **Failure Point**: Individual file processing (much more manageable)

## Migration Strategy

### Gradual Rollout

1. **Phase 1**: Implement `StreamingFileHandler` alongside existing code
2. **Phase 2**: Add feature flag to enable streaming for testing
3. **Phase 3**: Migrate production traffic gradually
4. **Phase 4**: Remove old memory-intensive code

### Feature Flag Implementation

**File**: `backend/app/core/config.py` (ADD)

```python
# Environment variable
STREAMING_UPLOAD_ENABLED = os.getenv("STREAMING_UPLOAD_ENABLED", "false").lower() == "true"
```

**File**: `backend/app/api/routes/knowledgebases.py` (lines 1075-1125)

```python
# In endpoint
if STREAMING_UPLOAD_ENABLED:
    # Use new streaming approach
    file_paths = await stream_files_to_temp(files, temp_dir)
else:
    # Use old memory approach
    file_data = await load_files_to_memory(files)
```

### Testing Strategy

1. **Unit Tests**: Test `StreamingFileHandler` with mock files
   - **File**: `backend/tests/test_streaming_file_handler.py` (NEW)
   
2. **Integration Tests**: Test full upload flow with streaming enabled
   - **File**: `backend/tests/test_kb_streaming_upload.py` (NEW)
   
3. **Load Tests**: Test with large file sets (100+ files)
   - **File**: `backend/tests/test_kb_large_upload.py` (MODIFY)
   
4. **Memory Profiling**: Compare memory usage between old and new approaches
   - **File**: `backend/tests/test_memory_profiling.py` (MODIFY)
   
5. **Error Handling**: Test cleanup on failures at various points
   - **File**: `backend/tests/test_streaming_error_handling.py` (NEW)

## Benefits Summary

### Performance Improvements
- **90%+ Memory Reduction**: Files never fully loaded into memory simultaneously
- **Scalability**: Handle arbitrarily large uploads
- **Responsiveness**: No long pauses during file reading
- **Reliability**: Reduced OOM crash risk

### Operational Benefits
- **Resource Efficiency**: Lower memory requirements allow smaller instances
- **Cost Reduction**: Potentially reduce EC2 instance sizes
- **User Experience**: Faster apparent upload times (streaming vs buffering)
- **Monitoring**: Better visibility into upload progress

### Code Quality
- **Separation of Concerns**: Upload streaming separate from processing
- **Error Recovery**: Better cleanup on failures
- **Testability**: Easier to test streaming logic independently
- **Maintainability**: Clearer separation between upload and processing phases

## Implementation Timeline

### Week 1: Infrastructure
- **File**: `backend/app/utils/streaming_file_handler.py` - Create `StreamingFileHandler` class
- **File**: `backend/app/services/file_validator.py` - Update `FileValidator` for streaming validation
- **File**: `backend/app/core/config.py` - Add feature flag support

### Week 2: Endpoint Migration
- **File**: `backend/app/api/routes/knowledgebases.py` - Refactor `create_knowledge_base` endpoint
- **File**: `backend/app/api/routes/knowledgebases.py` - Update background task interface
- **File**: `backend/app/api/routes/knowledgebases.py` - Add comprehensive error handling

### Week 3: Integration Testing
- **Files**: `backend/tests/test_*.py` - Test with various file types and sizes
- **File**: `backend/tests/test_memory_profiling.py` - Memory usage profiling
- **File**: `backend/tests/test_performance.py` - Performance benchmarking

### Week 4: Production Rollout
- **File**: `docker-compose.yml` - Gradual traffic migration
- **File**: `backend/app/core/config.py` - Monitoring and alerting setup
- **File**: `backend/app/api/routes/knowledgebases.py` - Cleanup of old code

## Risk Mitigation

### Rollback Plan
- Feature flag allows instant rollback to old implementation
- Database schema unchanged (no migration needed)
- Temp file cleanup ensures no disk space leaks

### Monitoring
- Add memory usage metrics to track improvement
- Monitor temp directory usage and cleanup
- Track upload success/failure rates

### Compatibility
- No changes to frontend API contract
- Progress tracking remains identical
- File validation logic preserved

This refactoring transforms the knowledge base upload from a memory-bound operation to a streaming, disk-based approach that can scale to handle very large document collections efficiently.</content>
<parameter name="filePath">/home/ec2-user/aiben-react/KNOWLEDGE_BASE_CREATION_MASTER.md