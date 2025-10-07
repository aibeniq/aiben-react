# ReportGenie Full Document Scan - Citation Content Fix

**Date:** October 7, 2025  
**Issue:** Citations showed generic filenames instead of actual relevant text snippets

## Problem Description

After implementing LLM-based citation filtering for ReportGenie Full Document Scan, the citations were being created incorrectly. Instead of showing the actual relevant text snippets from the knowledge base (like the chatbot does), they only showed generic messages like:

```
"Full document scan from 10.1001%2Farchpsyc.1980.01780220027002.pdf"
```

This made the citations useless - users couldn't see **what** was relevant, only **which file** it came from.

## Root Cause

The citation creation code was iterating over the `sources` (files) instead of the `relevant_chunk_indices` (filtered text chunks):

### Before (WRONG):
```python
# Create source citations from all sources used in full text scan
source_citations = []
for source in sources:  # ❌ Iterating over SOURCE FILES
    source_citations.append({
        "content": f"Full document scan from {source.name}",  # ❌ Generic message
        "metadata": {
            "source": source.name,
            "source_data_id": str(source.source_data_id),
            "scan_type": "full_text",
        },
    })
```

**Problems:**
1. Iterates over `sources` (the uploaded files) instead of `text_chunks` (the actual content)
2. Creates generic "Full document scan from..." messages
3. Doesn't show the actual relevant text
4. One citation per file, not per relevant chunk

## Solution Implemented

Changed the citation creation to use the **filtered text chunks** that were identified as relevant:

### After (CORRECT):
```python
# Create source citations from relevant chunks only
source_citations = []
for idx in relevant_chunk_indices:  # ✅ Iterating over RELEVANT CHUNKS
    chunk_content = text_chunks[idx]
    # Truncate to 500 chars for display
    display_content = chunk_content[:500] + ("..." if len(chunk_content) > 500 else "")
    
    source_citations.append({
        "content": display_content,  # ✅ Actual chunk text
        "metadata": {
            "source": "Full Document Scan",
            "chunk_index": idx,
            "scan_type": "full_text",
        },
    })
```

**Improvements:**
1. Uses `relevant_chunk_indices` from the filtering loop
2. Extracts actual `chunk_content` from `text_chunks`
3. Shows real text snippets (truncated to 500 chars for UI)
4. One citation per relevant chunk
5. Matches chatbot behavior

## How It Works Now

### Complete Flow

1. **Extract text** from all documents in knowledge base
2. **Chunk text** into manageable pieces (~1000 tokens each)
3. **For each chunk:**
   - Send to LLM: "Is this chunk relevant to the question?"
   - If LLM says "No relevant information found" → SKIP
   - If LLM provides analysis → INCLUDE in `chunk_analyses` and track index in `relevant_chunk_indices`
4. **Synthesize** the relevant chunk analyses into final answer
5. **Create citations** from the actual relevant chunks (using `relevant_chunk_indices`)
6. **Display** citations with real text snippets

### Example Output

**Before (Generic):**
```json
{
  "content": "Full document scan from 10.1001%2Farchpsyc.1980.01780220027002.pdf",
  "metadata": {
    "source": "10.1001%2Farchpsyc.1980.01780220027002.pdf",
    "source_data_id": "abc123",
    "scan_type": "full_text"
  }
}
```

**After (Specific):**
```json
{
  "content": "Social Status.—In the stable and behaviorally manipulated multimale groups, the behaviors described in Table 2 were recorded. Social status was assessed by noting the subject's success in dyadic intermale aggression. Subject A was regarded as successful in a dyadic agonistic encounter with subject B if B submitted to or avoided A when A threatened B, displayed to B, or engaged in contact aggression with B. In each group the male with the highest percenta...",
  "metadata": {
    "source": "Full Document Scan",
    "chunk_index": 6,
    "scan_type": "full_text"
  }
}
```

## Comparison with Chatbot

The implementation now **exactly matches** the chatbot's Full Document Scan behavior:

| Aspect | Chatbot Full Scan | ReportGenie Full Scan (Now) |
|--------|------------------|------------------------------|
| **Filtering** | LLM-based relevance check | LLM-based relevance check ✅ |
| **Prompt** | VERADOC_RELEVANCE_FILTER_PROMPT | VERADOC_RELEVANCE_FILTER_PROMPT ✅ |
| **Detection** | "No relevant information found" | "No relevant information found" ✅ |
| **Citations** | Actual chunk text snippets | Actual chunk text snippets ✅ |
| **Truncation** | 500 chars | 500 chars ✅ |
| **Metadata** | chunk_index, scan_type | chunk_index, scan_type ✅ |

## Changes Made

### File Modified
`backend/app/api/routes/reportgenie.py` (lines ~312-420)

### Key Changes

**1. Filtering Loop** (lines ~312-350)
```python
# Track relevant chunk indices
relevant_chunk_indices = []

for i, chunk in enumerate(text_chunks):
    # Use relevance filter
    analysis = invoke_llm(
        llm,
        settings.VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE,  # ✅ Changed from CHATBOT_FULL_TEXT_CHUNK
        {"chunk": chunk, "question": section_description},
    )
    
    # Only include relevant chunks
    if "No relevant information found" not in analysis:
        chunk_analyses.append(analysis)
        relevant_chunk_indices.append(i)  # ✅ Track index
```

**2. Logging Update** (line ~355)
```python
print(
    f"📊 Relevance filtering: {len(chunk_analyses)} relevant chunks from {len(text_chunks)} total chunks"
)
```

**3. Citation Creation** (lines ~395-410)
```python
# Create source citations from relevant chunks only
source_citations = []
for idx in relevant_chunk_indices:  # ✅ Use filtered indices
    chunk_content = text_chunks[idx]  # ✅ Get actual content
    display_content = chunk_content[:500] + ("..." if len(chunk_content) > 500 else "")
    
    source_citations.append({
        "content": display_content,  # ✅ Real text, not filename
        "metadata": {
            "source": "Full Document Scan",
            "chunk_index": idx,
            "scan_type": "full_text",
        },
    })
```

## Benefits

### For Users
- ✅ **See actual quotes** from knowledge base documents
- ✅ **Verify relevance** - can read the exact text that informed the answer
- ✅ **Better transparency** - understand what the LLM found relevant
- ✅ **Consistent UX** - matches chatbot citation display

### For Quality
- ✅ **Verifiable** - citations can be traced to actual content
- ✅ **Actionable** - users can assess if citations truly support the answer
- ✅ **Professional** - shows real evidence, not just file names

## Testing

### How to Verify

1. **Run ReportGenie with Full Document Scan:**
   - Select a knowledge base
   - Create an outline with a section
   - Toggle "Full Document Scan" ON
   - Generate report

2. **Check Citations:**
   - Open the generated report
   - Expand a section to view citations
   - **Verify:** Citations show actual text snippets
   - **Verify:** NOT showing "Full document scan from filename.pdf"

3. **Check Backend Logs:**
   ```
   📊 Relevance filtering: 15 relevant chunks from 150 total chunks
   ```

### Expected Results

**Citations should look like:**
```
"Social Status.—In the stable and behaviorally manipulated
multimale groups, the behaviors described in Table 2 were re¬
corded. Social status was assessed by noting the subject's success
in dyadic intermale aggression. Subject A was regarded as suc¬
cessful in a dyadic agonistic encounter with subject  if  
submitted to or avoided A when A threatened B, displayed to B, or
engaged in contact aggression with B. In each group the male with
the highest percenta..."
```

**NOT like:**
```
"Full document scan from 10.1001%2Farchpsyc.1984.01790150095013.pdf"
```

## Related Issues Fixed

This fix completes the Full Document Scan implementation:

1. ✅ **Bug #1:** Full Document Scan mode never worked (always used vector search)
   - **Fixed:** Use `search_mode` parameter instead of `search_type`
   
2. ✅ **Bug #2:** No citation filtering (would include ALL chunks)
   - **Fixed:** LLM-based relevance filtering with `VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE`
   
3. ✅ **Bug #3:** Citations showed filenames instead of content (THIS FIX)
   - **Fixed:** Use `relevant_chunk_indices` to extract actual chunk text

## Summary

**The Problem:** Citations displayed generic filenames instead of relevant text snippets

**Root Cause:** Code iterated over `sources` (files) instead of `text_chunks` (content)

**The Fix:** Use `relevant_chunk_indices` to create citations from actual filtered chunk content

**Result:** ReportGenie Full Document Scan now shows real text citations, matching chatbot behavior ✅

---

**Status:** ✅ Fixed and Deployed  
**Deployed:** October 7, 2025  
**Testing:** Ready for user validation
