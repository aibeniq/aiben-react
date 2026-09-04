# Vision Analysis Fix - Knowledge Base vs Upload

## Problem

When a user enables Vision Analysis:

- **Upload endpoint**: Vision analysis works correctly when uploading a file directly
- **Knowledge Base endpoint**: Vision analysis does NOT work when querying a knowledge base

This inconsistency occurred because the knowledge base query endpoints were not respecting the `vision_analysis_override` parameter.

## Root Cause

There were two related issues:

### Issue 1: Missing Parameter Pass-Through

The `vision_analysis_override` parameter was received by the API endpoints but **not passed** to the internal functions or to `VisionService.is_vision_enabled()`.

**Affected locations:**

1. `query_knowledge_base()` - vector search path (line ~1329)
2. `_handle_full_text_kb_query()` - full-text scan path for knowledge bases
3. `_handle_full_text_document_query()` - full-text scan path for uploaded documents

### Issue 2: Conditional Vision Analysis Logic

Vision analysis was only performed when **BOTH**:

1. Text analysis appeared insufficient (contained the `LLM_INSUFFICIENT_INFO_PHRASE`)
2. Vision was generally enabled

This meant that even if a user explicitly enabled Vision Analysis, it wouldn't run if the text answer seemed "sufficient" to the LLM.

**Affected locations:**

1. `query_knowledge_base()` - line ~1362
2. `query_documents()` - line ~2138
3. `_handle_full_text_kb_query()` - line ~381
4. `_handle_full_text_document_query()` - line ~734

## Solution

### Fix 1: Pass `vision_analysis_override` to All Vision Decisions

Updated all calls to `VisionService.is_vision_enabled()` to include the override parameter:

```python
# Before
vision_enabled = VisionService.is_vision_enabled(llm, current_user)

# After
vision_enabled = VisionService.is_vision_enabled(llm, current_user, vision_analysis_override)
```

**Updated functions:**

1. `_handle_full_text_kb_query()` - line 151
2. `query_knowledge_base()` - line 1329
3. `_handle_full_text_document_query()` - line 576
4. `query_documents()` - already had this (line 2088)

Also passed parameters to internal function calls:

- `query_knowledge_base()` now passes `vision_analysis_override` and `pdf_parsing_override` to `_handle_full_text_kb_query()`
- `query_documents()` now passes `vision_analysis_override` and `pdf_parsing_override` to `_handle_full_text_document_query()`

### Fix 2: Always Perform Vision When Explicitly Enabled

Changed the vision analysis condition from:

```python
if text_answer_insufficient and vision_enabled and all_images:
```

To:

```python
should_perform_vision = vision_analysis_override is True or (text_answer_insufficient and vision_enabled)
if should_perform_vision and all_images:
```

This means vision analysis now runs when:

- **OR** `vision_analysis_override is True` (user explicitly enabled it)
- **OR** Text analysis was insufficient AND vision is generally enabled

**Updated locations:**

1. `_handle_full_text_kb_query()` - lines 381-387
2. `query_knowledge_base()` - lines 1362-1368
3. `_handle_full_text_document_query()` - lines 734-740
4. `query_documents()` - lines 2138-2144

## Files Modified

- `/backend/app/api/routes/chatbot.py`

## Testing

The fix ensures that:

1. ✅ When `vision_analysis_override=true` is sent, vision analysis ALWAYS runs (if images exist)
2. ✅ When `vision_analysis_override=false` is sent, vision analysis is disabled
3. ✅ When `vision_analysis_override=null` (not set), the old behavior applies (vision only if text insufficient)
4. ✅ Works consistently across:
   - Vector search for knowledge bases
   - Full-text scan for knowledge bases
   - Vector search for uploaded documents
   - Full-text scan for uploaded documents

## Endpoints Affected

All chatbot query endpoints now properly respect the vision analysis toggle:

- `POST /chat/query_knowledge_base` with `vision_analysis_override`
- `POST /chat/query_documents` with `vision_analysis_override`
