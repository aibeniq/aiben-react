# Processing Settings Testing Guide

## Overview

This document describes the comprehensive testing procedure for the Processing Settings feature, which allows users to configure and override three key parameters for document processing:

1. **Search Mode** (`search_mode`): `vector` or `full_scan`
2. **Vision Analysis** (`vision_analysis_enabled`): `true` or `false`
3. **PDF Parsing** (`pdf_parsing_preference`): `enhanced` or `basic`

## Test Script

**Main Test File**: `test_all_processing_settings.py`

This script comprehensively tests all 8 possible combinations (2×2×2) of the three processing parameters.

### Prerequisites

1. **Backend must be running** via Docker Compose
2. **Knowledge Base with Swedish Fish PDF** must exist with chunks
   - KB ID: `7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e`
   - Title: "Test KB Swedish Fish 1762268987"
   - File: `test_files/swedish fish.pdf`
3. **User credentials** configured in the script:
   - Username: `david@aiben.io`
   - Password: `password123456`

### Running the Test

```powershell
# Ensure backend is running
docker-compose up -d

# Wait for services to be ready (10-15 seconds)
Start-Sleep -Seconds 15

# Run the comprehensive test
python test_all_processing_settings.py
```

### Test Execution Flow

The script performs the following:

1. **Login** - Authenticates using session-based auth (cookies)
2. **Test All Combinations** - Runs 8 tests covering all parameter combinations:

   - Test 1: `vector + vision_True + pdf_enhanced`
   - Test 2: `vector + vision_True + pdf_basic`
   - Test 3: `vector + vision_False + pdf_enhanced`
   - Test 4: `vector + vision_False + pdf_basic`
   - Test 5: `full_scan + vision_True + pdf_enhanced`
   - Test 6: `full_scan + vision_True + pdf_basic`
   - Test 7: `full_scan + vision_False + pdf_enhanced`
   - Test 8: `full_scan + vision_False + pdf_basic`

3. **Analysis** - Analyzes results to determine:
   - Which parameters produce different results
   - Overall uniqueness of outputs
   - Hash distribution

### Expected Results

✅ **All parameters should produce different results**:

- **Search Mode**: 4/4 combinations show difference
- **Vision Analysis**: 4/4 combinations show difference
- **PDF Parsing**: 4/4 combinations show difference

✅ **Overall Uniqueness**: 8/8 unique results (100% uniqueness ratio)

### Sample Output

```
================================================================================
COMPREHENSIVE PROCESSING SETTINGS TEST
Testing ALL combinations of settings
================================================================================
Test file: test_files/swedish fish.pdf
Using KB: 7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e

Parameter space:
  - Search Modes: ['vector', 'full_scan']
  - Vision Analysis: [True, False]
  - PDF Parsing: ['enhanced', 'basic']
  - Total combinations: 8

[Test 1/8]
================================================================================
TESTING: vector+vision_True+pdf_enhanced
================================================================================
Task ID: 16254e53-392a-44ca-8619-786ce62a15d1
Parameters:
  - Search Mode: vector
  - Vision Analysis: True
  - PDF Parsing: enhanced
✅ Completed in 61.57s
Evaluation length: 690 chars
Hash: d06358e7
Preview: Ei, asiakirja ei noudata sääntöjä/ohjeita...

... (7 more tests)

================================================================================
ANALYSIS: PARAMETER IMPACT
================================================================================

1. SEARCH MODE IMPACT (vector vs full_scan)
--------------------------------------------------------------------------------
  Vision=True, PDF=enhanced: DIFFERENT (vector=d06358e7, full_scan=5b3babd5)
  Vision=True, PDF=basic: DIFFERENT (vector=345e608c, full_scan=6c3e1fc7)
  Vision=False, PDF=enhanced: DIFFERENT (vector=28006c35, full_scan=35687a58)
  Vision=False, PDF=basic: DIFFERENT (vector=e42f9edd, full_scan=60b22ad2)

Result: 4/4 combinations show difference
✅ Search mode parameter IS working!

2. VISION ANALYSIS IMPACT (True vs False)
--------------------------------------------------------------------------------
  Search=vector, PDF=enhanced: DIFFERENT (on=d06358e7, off=28006c35)
  Search=vector, PDF=basic: DIFFERENT (on=345e608c, off=e42f9edd)
  Search=full_scan, PDF=enhanced: DIFFERENT (on=5b3babd5, off=35687a58)
  Search=full_scan, PDF=basic: DIFFERENT (on=6c3e1fc7, off=60b22ad2)

Result: 4/4 combinations show difference
✅ Vision analysis parameter IS working!

3. PDF PARSING IMPACT (enhanced vs basic)
--------------------------------------------------------------------------------
  Search=vector, Vision=True: DIFFERENT (enhanced=d06358e7, basic=345e608c)
  Search=vector, Vision=False: DIFFERENT (enhanced=28006c35, basic=e42f9edd)
  Search=full_scan, Vision=True: DIFFERENT (enhanced=5b3babd5, basic=6c3e1fc7)
  Search=full_scan, Vision=False: DIFFERENT (enhanced=35687a58, basic=60b22ad2)

Result: 4/4 combinations show difference
✅ PDF parsing parameter IS working!

4. OVERALL UNIQUENESS
--------------------------------------------------------------------------------
Total tests run: 8
Unique results: 8
Uniqueness ratio: 8/8 = 100.0%
✅ ALL RESULTS UNIQUE - All parameters working!

================================================================================
TEST SUMMARY
================================================================================
Total tests: 8
Total time: 437.64s
Average time: 54.71s
```

## Backend Implementation Details

### API Endpoint

The test hits the `/api/v1/veradoc/process-rag` endpoint with the following parameters:

```python
{
    "questions": "What are the ingredients?\nWhat is the nutritional information?\nAre there any allergens mentioned?",
    "knowledge_base_id": "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e",
    "search_mode": "vector",  # or "full_scan"
    "vision_analysis_enabled": "true",  # or "false"
    "pdf_parsing_preference": "enhanced",  # or "basic"
    "task_id": "<generated-task-id>"
}
```

### Backend Processing

1. **Search Mode**:

   - `vector`: Uses vector similarity search on knowledge base embeddings
   - `full_scan`: Processes entire document content directly

2. **Vision Analysis**:

   - `true`: Enables GPT-4 Vision for image analysis in documents
   - `false`: Disables vision analysis

3. **PDF Parsing**:
   - `enhanced`: Uses PyMuPDF4LLM for advanced table and structure extraction
   - `basic`: Uses basic PyPDF text extraction

### Parameter Priority

For each parameter, the backend follows this priority order:

1. **Override parameter** (passed in API request) - Highest priority
2. **User preference** (from user settings)
3. **Global setting** (system default) - Lowest priority

## Bugs Fixed During Testing

### 1. PDF Extraction Async/Coroutine Error

**Problem**: `'coroutine' object is not iterable` error when extracting PDF text

**Root Cause**: `extract_text_from_pdf_bytes()` was calling async functions (`load_pdf_with_pypdf`, `extract_pdf_with_pymupdf4llm`) without `await`

**Solution**:

- Created async version: `extract_text_from_pdf_bytes_async()`
- Made sync wrapper use `asyncio.run()` to execute async code
- Added `await` to all async function calls

**Files Modified**:

- `backend/app/services/pdf_utils.py`

### 2. Thread Pool Executor Parameter Passing

**Problem**: Parameters not being passed correctly to `extract_text_from_file()` in thread pool

**Root Cause**: `run_in_executor` was passing positional arguments instead of keyword arguments

**Solution**: Used `functools.partial` to properly pass keyword arguments

**Files Modified**:

- `backend/app/api/routes/veradoc.py`

## Test File Organization

### Active Test Files

- **`test_all_processing_settings.py`** - ✅ Main comprehensive test (KEEP)

  - Tests all 8 parameter combinations
  - Analyzes parameter impact
  - Provides detailed output

- **`test_files/swedish fish.pdf`** - ✅ Test data file (KEEP)
  - Used for all processing tests
  - Contains actual content for meaningful results

### Deprecated/Old Test Files

The following files are deprecated iterations and can be removed:

- **`test_processing_simple.py`** - ❌ DELETE

  - Only tests search_mode (subset of functionality)
  - Superseded by `test_all_processing_settings.py`

- **`test_all_combinations.py`** - ❌ DELETE

  - Early version with KB creation logic
  - Superseded by `test_all_processing_settings.py`

- **`test_processing_settings_combinations.py`** - ❌ DELETE

  - Incomplete version with commented-out parameters
  - Used token-based auth (wrong approach)
  - Superseded by `test_all_processing_settings.py`

- **`list_kbs.py`** - ❌ DELETE
  - Utility script for debugging KB issues
  - No longer needed

## Troubleshooting

### Test Fails with "KB has no chunks"

**Cause**: Knowledge base hasn't finished processing or got stuck

**Solution**:

1. Check KB status in the UI
2. If stuck, recreate the KB by uploading `test_files/swedish fish.pdf` through the UI
3. Update `KB_ID` constant in test script

### All Results Identical

**Cause**: Backend not accepting/processing override parameters

**Solution**:

1. Check backend logs: `docker logs aibeniq-react-backend-1`
2. Look for parameter logging (e.g., "Using PDF parsing preference override: basic")
3. Ensure backend code has parameter handling implemented

### Authentication Errors

**Cause**: Using wrong auth method or expired session

**Solution**:

1. Test uses session-based auth (cookies), not JWT tokens
2. Ensure `requests.Session()` is used
3. Check credentials are correct

### Slow Test Execution

**Expected**: ~55 seconds per test, ~440 seconds total

**Why**: Each test processes the full PDF with different parameters, including:

- Text extraction
- Vector/full-scan search
- Vision analysis (if enabled)
- LLM evaluation

## Success Criteria

✅ All tests complete without errors  
✅ All 8 combinations produce unique results  
✅ Search mode: 4/4 different  
✅ Vision analysis: 4/4 different  
✅ PDF parsing: 4/4 different  
✅ 100% uniqueness ratio

## Future Enhancements

1. **Add tests for other routes**:

   - `/api/v1/reportgenie/process-rag`
   - `/api/v1/formconnect/process-rag`
   - `/api/v1/twincheck/process-rag`
   - `/api/v1/chatbot/chat`

2. **Add performance benchmarks**:

   - Track execution time trends
   - Identify performance regressions

3. **Add content validation**:

   - Verify answers contain expected keywords
   - Check citation quality

4. **Add edge case tests**:
   - Empty KB
   - Invalid parameter values
   - Missing parameters

## Related Documentation

- **Implementation Guide**: `PROCESSING_SETTINGS_IMPLEMENTATION_GUIDE.md`
- **Refactoring Plan**: `PROCESSING_SETTINGS_REFACTORING.md`
- **Frontend Components**: `frontend/src/components/settings/ProcessingDefaultsSettings.tsx`
- **Backend Routes**: `backend/app/api/routes/veradoc.py`
