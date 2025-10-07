# Context Pre-fetch Debug Investigation

## Issue
The progress bar is immediately skipping to "Answering question..." stage instead of showing "Retrieving policy context..." because the pre-fetched context is not being found.

## Symptom
Backend logs show:
```
⚠️ No pre-fetched context found for question: Does each character have a cle..., using fallback
```

This means:
1. Context pre-fetching IS running (fetching_context stage)
2. BUT the context is not being retrieved when answering questions
3. System falls back to fetching context again during question answering

## Root Cause Investigation

The issue is in the key matching between storing and retrieving context.

**Storing context** (line 357):
```python
question_contexts[question_text] = {
    "context": question_context,
    "source_citations": source_citations,
    "consult_documents": consult_documents
}
```

**Retrieving context** (line 1086):
```python
if question_text in question_contexts:
    # Use cached context
```

The problem could be:
1. **Different question text formats** - Questions might be parsed differently in pre-fetch vs processing
2. **Whitespace differences** - Extra spaces, newlines, or trimming inconsistencies
3. **Question list recreation** - Question list might be parsed twice with slight differences

## Debug Logging Added

Added debug output to show:
- What question key is being looked up
- What keys are available in the context cache

**Location:** Line 1082 in `/backend/app/api/routes/veradoc.py`

```python
print(f"🔍 DEBUG: Looking for question key: '{question_text[:50]}'")
print(f"🔍 DEBUG: Available keys in question_contexts: {[key[:50] for key in question_contexts.keys()]}")
```

## Testing Instructions

1. Run a Review with a few questions
2. Check backend logs for debug output
3. Look for lines starting with `🔍 DEBUG:`
4. Compare the "Looking for" key with "Available keys"
5. Identify any differences (case, whitespace, punctuation, etc.)

## Expected Behavior

**If working correctly:**
```
🔍 DEBUG: Looking for question key: 'Does each character have a clear and distinct moti'
🔍 DEBUG: Available keys in question_contexts: ['Does each character have a clear and distinct moti']
✅ Using pre-fetched context for question: Does each character have a cle...
```

**If broken (current state):**
```
🔍 DEBUG: Looking for question key: 'Does each character have a clear and distinct moti'
🔍 DEBUG: Available keys in question_contexts: []
⚠️ No pre-fetched context found for question: Does each character have a cle..., using fallback
```

OR:
```
🔍 DEBUG: Looking for question key: 'Does each character have a clear and distinct moti'
🔍 DEBUG: Available keys in question_contexts: ['Does each character have a clear and distinct motivation']
⚠️ No pre-fetched context found for question: Does each character have a cle..., using fallback
```
(Note the subtle difference - one is truncated, one has full text)

## Possible Fixes

Once we identify the mismatch:

1. **If whitespace issue:** Normalize both keys with `.strip()` and potentially regex to collapse multiple spaces
2. **If case issue:** Convert both to lowercase for comparison
3. **If parsing issue:** Ensure question list is parsed the same way in both locations
4. **If length issue:** Don't truncate question text when using as key

## Next Steps

1. Test the Review function
2. Share the debug output from backend logs
3. I'll provide the appropriate fix based on what we see
4. Remove debug logging once fixed

## Files Modified

- `/backend/app/api/routes/veradoc.py` - Added debug logging at line 1082

Status: ⏳ Waiting for test results to identify the exact mismatch
