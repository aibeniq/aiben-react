# KeyError: 'chunk_analyses' Fix

## Problem Diagnosed ✅

The KeyError: 'chunk_analyses' was occurring because the **vector search** code path was using the wrong prompt template.

### Root Cause:

- **Line 323** in `reportgenie.py` was using `settings.REPORT_GENIE_SYNTHESIS_PROMPT_TEMPLATE`
- This template expects variables: `{chunk_analyses}` and `{question}`
- But the vector search code was providing: `{"context": context, "question": section_description}`
- The template was looking for `chunk_analyses` but getting `context` instead → **KeyError**

### Template Usage Analysis:

1. **Full Text Scan** (✅ Correct):

   - Uses `CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE`
   - Provides: `chunk_analyses` and `question`
   - Template expects: `{chunk_analyses}` and `{question}`

2. **Vector Search** (❌ Was Wrong → ✅ Now Fixed):
   - **Before**: Used `REPORT_GENIE_SYNTHESIS_PROMPT_TEMPLATE`
   - **After**: Uses `REPORT_GENIE_PROMPT_TEMPLATE`
   - Provides: `report_draft`, `context`, `question`, `custom_instructions`
   - Template expects: `{report_draft}`, `{context}`, `{question}`, `{custom_instructions}`

## Fix Applied ✅

Changed the vector search template from:

```python
settings.REPORT_GENIE_SYNTHESIS_PROMPT_TEMPLATE
```

To:

```python
settings.REPORT_GENIE_PROMPT_TEMPLATE
```

And updated the variables to include all required parameters:

```python
{
    "report_draft": draft_report,
    "context": context,
    "question": section_description,
    "custom_instructions": ""
}
```

## Verification ✅

- ✅ No syntax errors in Python file
- ✅ Template variables now match between code and template
- ✅ Full text scan continues to work with correct template
- ✅ Vector search now uses appropriate template for its data structure

## Result

The KeyError: 'chunk_analyses' should no longer occur when using **Full Document Scan** mode. Both search modes now use their appropriate templates with correct variable mappings.
