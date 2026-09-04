# Vision Analysis Fix - Testing Guide

## How to Verify the Fix

### Test 1: Knowledge Base Query with Vision Override Enabled

**Setup:**

1. Create or select a knowledge base that contains images
2. Ask a question that requires vision analysis to answer correctly

**Test Case 1a: With Vision Enabled Override**

```bash
POST /chat/query_knowledge_base
{
    "kb_id": "your-kb-id",
    "question": "What do you see in the images?",
    "vision_analysis_override": true
}
```

**Expected Result:** Vision analysis should run even if text answer seems sufficient

**Test Case 1b: Without Vision Override (Default Behavior)**

```bash
POST /chat/query_knowledge_base
{
    "kb_id": "your-kb-id",
    "question": "What do you see in the images?",
    "vision_analysis_override": null
}
```

**Expected Result:** Vision analysis only runs if text answer is insufficient

---

### Test 2: Document Upload with Vision Override Enabled

**Setup:**

1. Upload a PDF or DOCX with images
2. Ask a question in the same request

**Test Case 2a: With Vision Enabled Override**

```bash
POST /chat/query_documents?vision_analysis_override=true
Form Data:
  - question: "What do you see in the images?"
  - files: [document.pdf]
```

**Expected Result:** Vision analysis should run even if text answer seems sufficient

**Test Case 2b: Without Vision Override**

```bash
POST /chat/query_documents?vision_analysis_override=false
Form Data:
  - question: "What do you see in the images?"
  - files: [document.pdf]
```

**Expected Result:** Vision analysis should be skipped even if it would help

---

### Test 3: Full-Text Scan with Vision

**Test Case 3a: Knowledge Base Full-Text Scan with Vision**

```bash
POST /chat/query_knowledge_base?search_mode=full_text&vision_analysis_override=true
{
    "kb_id": "your-kb-id",
    "question": "What do you see in the images?"
}
```

**Expected Result:** After analyzing all chunks, if insufficient text found, vision analysis runs

**Test Case 3b: Document Full-Text Scan with Vision**

```bash
POST /chat/query_documents?search_mode=full_text&vision_analysis_override=true
Form Data:
  - question: "What do you see in the images?"
  - files: [document.pdf]
```

**Expected Result:** Vision analysis always runs (since override=true)

---

## Key Behavior Changes

### Before Fix

- **Knowledge Base Query:** Vision analysis only worked if it was a follow-up after text analysis failed
- **Upload Query:** Same behavior
- **Inconsistency:** No clear way to force vision analysis to run

### After Fix

- **Knowledge Base Query:** Vision analysis respects the `vision_analysis_override` parameter
- **Upload Query:** Consistent behavior now
- **Explicit Control:** When `vision_analysis_override=true`, vision runs ALWAYS (if images exist)

---

## Verification Checklist

- [ ] Test vector search knowledge base query with vision_analysis_override=true
- [ ] Test full-text scan knowledge base query with vision_analysis_override=true
- [ ] Test vector search document query with vision_analysis_override=true
- [ ] Test full-text scan document query with vision_analysis_override=true
- [ ] Verify that vision_analysis_override=false properly disables vision
- [ ] Verify that vision_analysis_override=null uses default behavior (insufficient text triggers vision)
- [ ] Check backend logs to confirm vision analysis is being attempted
- [ ] Verify no new syntax errors or import issues

---

## Debug Logging

Look for these log messages to confirm the fix is working:

```
Received vision_analysis_override: true
DEBUG: vision_enabled=True, has_vision_fallbacks=False, all_images_count=5
Text analysis insufficient: False
Attempting vision analysis from X image(s)
Vision analysis result: ...
```

The key indicator is:

- ✅ `vision_analysis_override: true` received
- ✅ Vision analysis attempted even when text analysis is sufficient
- ✅ Images are extracted and processed
