# Vision Analysis Fix - Complete Summary

## Issue Description

When users enabled Vision Analysis through the UI override:

- **Upload endpoint**: Vision analysis worked correctly ✅
- **Knowledge base endpoint**: Vision analysis was NOT being performed ❌
- **Error in logs**: `KeyError: 'language_instruction'` - Vision analysis would fail when attempting to regenerate the answer

## Root Causes

### 1. Missing `vision_analysis_override` parameter in knowledge base query

**File**: `backend/app/api/routes/chatbot.py`
**Function**: `query_knowledge_base()`
**Line**: ~1329

**Problem**: The `vision_analysis_override` parameter was received by the endpoint but was NOT passed to `VisionService.is_vision_enabled()`, so it was always ignored.

```python
# BEFORE (BROKEN):
vision_enabled = VisionService.is_vision_enabled(llm, current_user)

# AFTER (FIXED):
vision_enabled = VisionService.is_vision_enabled(llm, current_user, vision_analysis_override)
```

### 2. Vision analysis only runs when text is insufficient

**File**: `backend/app/api/routes/chatbot.py`
**Functions**:

- `query_knowledge_base()` (~1399-1405)
- `query_documents()` (~2181-2189)
- `_handle_full_text_kb_query()` (~387-394)

**Problem**: Vision analysis was conditional on `text_answer_insufficient` being True. When users explicitly enable vision analysis via the override, they expect it to ALWAYS run regardless of text quality.

```python
# BEFORE (BROKEN):
if text_answer_insufficient and vision_enabled:
    # perform vision

# AFTER (FIXED):
should_perform_vision = vision_analysis_override is True or (text_answer_insufficient and vision_enabled)
if should_perform_vision:
    # perform vision
```

### 3. Missing `language_instruction` in LLM calls after vision analysis

**File**: `backend/app/api/routes/chatbot.py`
**Functions & Lines**:

- `query_knowledge_base()` at line 1509-1519 (regenerating answer with vision context)
- `_handle_full_text_kb_query()` at line 492-501 (regenerating answer with vision analysis)
- `_handle_full_text_document_query()` at line 752-776 (processing images with prompt)

**Problem**: When regenerating the LLM response after vision analysis, the `language_instruction` variable was not included in the variables dictionary, causing a `KeyError` exception.

```python
# BEFORE (BROKEN):
answer_content = invoke_llm(
    llm,
    qa_prompt_template,
    {
        "context": context,
        "question": rephrased_question,
        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
        # MISSING: "language_instruction": language_instruction,
    },
)

# AFTER (FIXED):
answer_content = invoke_llm(
    llm,
    qa_prompt_template,
    {
        "context": context,
        "question": rephrased_question,
        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
        "language_instruction": language_instruction,  # ✅ ADDED
    },
)
```

### 4. Missing parameters in full-text KB query function calls

**File**: `backend/app/api/routes/chatbot.py`
**Function**: `_handle_full_text_kb_query()`

**Problem**: The function didn't accept `vision_analysis_override` and `pdf_parsing_override` parameters, and the caller wasn't passing them.

**Fixes Applied**:

1. Added parameters to function signature (line 128-137)
2. Updated function caller to pass parameters (line 983-993)
3. Updated `is_vision_enabled()` call to use the override (line 150-152)

## All Fixed Locations

| File         | Location                                              | Fix                                                        |
| ------------ | ----------------------------------------------------- | ---------------------------------------------------------- |
| `chatbot.py` | Line ~150 (\_handle_full_text_kb_query)               | Pass `vision_analysis_override` to `is_vision_enabled()`   |
| `chatbot.py` | Line ~387-394 (\_handle_full_text_kb_query)           | Update `should_attempt_vision` logic                       |
| `chatbot.py` | Line ~492-501 (\_handle_full_text_kb_query)           | Add `language_instruction` to vision-enhanced answer regen |
| `chatbot.py` | Line ~128-137 (\_handle_full_text_kb_query signature) | Add parameters to function signature                       |
| `chatbot.py` | Line ~752-776 (\_handle_full_text_document_query)     | Add `language_instruction` to process_images_with_prompt   |
| `chatbot.py` | Line ~983-993 (query_knowledge_base)                  | Pass parameters to \_handle_full_text_kb_query             |
| `chatbot.py` | Line ~1329 (query_knowledge_base)                     | Pass `vision_analysis_override` to `is_vision_enabled()`   |
| `chatbot.py` | Line ~1399-1405 (query_knowledge_base)                | Update `should_perform_vision` logic                       |
| `chatbot.py` | Line ~1509-1519 (query_knowledge_base)                | Add `language_instruction` to vision-enhanced answer regen |
| `chatbot.py` | Line ~2181-2189 (query_documents)                     | Update `should_perform_vision` logic                       |

## Expected Behavior After Fix

### Scenario 1: Upload with Vision Analysis Override

1. User uploads document(s) and enables "Vision Analysis"
2. System performs text analysis
3. System performs vision analysis REGARDLESS of text quality ✅
4. Vision results regenerate answer with language instruction ✅
5. User receives vision-enhanced answer ✅

### Scenario 2: Knowledge Base Query with Vision Analysis Override

1. User selects knowledge base and enables "Vision Analysis"
2. System performs vector search and text analysis
3. System performs vision analysis REGARDLESS of text quality ✅
4. Vision results regenerate answer with language instruction ✅
5. User receives vision-enhanced answer ✅

### Scenario 3: Full-Text Scan with Vision Analysis Override

1. User selects full-text scan mode and enables "Vision Analysis"
2. System chunks documents and analyzes chunks
3. System performs vision analysis REGARDLESS of chunk quality ✅
4. Vision results regenerate answer with language instruction ✅
5. User receives vision-enhanced answer ✅

## Testing Checklist

- [ ] Test upload endpoint with vision override enabled
- [ ] Test upload endpoint with full-text scan + vision override
- [ ] Test knowledge base query with vector search + vision override
- [ ] Test knowledge base query with full-text scan + vision override
- [ ] Verify language instruction is correct in responses
- [ ] Test with multiple images in documents
- [ ] Verify no `KeyError: 'language_instruction'` in logs
- [ ] Test without vision override (cost optimization should still work)

## Error That Should Now Be Fixed

```
backend-1  | 2025-11-06 17:00:02 |    ERROR | app.services.retry_utils | 💥 TENACITY: OpenAI API call failed: _invoke_langchain_model - KeyError: 'language_instruction'
backend-1  | Vision analysis failed: 'language_instruction'
```

This error should NO LONGER APPEAR in the logs.
