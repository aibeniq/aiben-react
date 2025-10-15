# Knowledge Base Upload Streaming Refactoring Plan

## Problem Statement

The current knowledge base creation process is extremely memory-inefficient for large uploads:

1. **Full File Buffering**: All uploaded files are read entirely into memory as bytes in the main endpoint
2. **Double Storage**: Files are stored in memory as `file_data` list, then written to disk again in background processing
3. **Memory Scaling Issues**: For 1000 PDFs (potentially 1GB+), this requires loading everything into RAM simultaneously
4. **OOM Risk**: Large uploads can cause out-of-memory crashes before processing even begins

## Current Implementation Analysis

### Memory Usage Pattern

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

**File**: `backend/app/utils/streaming_file_handler.py`

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

**File**: `backend/app/services/file_validator.py`

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

**File**: `backend/app/api/routes/knowledgebases.py`

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

**File**: `backend/app/api/routes/knowledgebases.py`

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

```python
# Environment variable
STREAMING_UPLOAD_ENABLED = os.getenv("STREAMING_UPLOAD_ENABLED", "false").lower() == "true"

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
2. **Integration Tests**: Test full upload flow with streaming enabled
3. **Load Tests**: Test with large file sets (100+ files)
4. **Memory Profiling**: Compare memory usage between old and new approaches
5. **Error Handling**: Test cleanup on failures at various points

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
- Create `StreamingFileHandler` class
- Update `FileValidator` for streaming validation
- Add feature flag support

### Week 2: Endpoint Migration
- Refactor `create_knowledge_base` endpoint
- Update background task interface
- Add comprehensive error handling

### Week 3: Integration Testing
- Test with various file types and sizes
- Memory usage profiling
- Performance benchmarking

### Week 4: Production Rollout
- Gradual traffic migration
- Monitoring and alerting setup
- Cleanup of old code

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
<parameter name="filePath">/home/ec2-user/aiben-react/KNOWLEDGE_BASE_STREAMING_REFACTORING_PLAN.md