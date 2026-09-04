# Import Scoping Fixes for Review Functionality

## Problems Encountered

### Issue 1: UnboundLocalError with `traceback`
**Error:**
```
UnboundLocalError: local variable 'traceback' referenced before assignment
```

**Location:** Line 1319 in `/backend/app/api/routes/veradoc.py`

**Root Cause:** 
- `traceback` was imported at the top of the file (line 3)
- There was also a local `import traceback` inside a nested exception handler (line 795)
- Python's scoping rules caused the local import to shadow the global one
- When the exception handler at line 1319 tried to use `traceback`, Python saw it as a local variable that hadn't been assigned yet

**Solution:**
Added `import traceback` at the beginning of the exception handler where it's used:
```python
except Exception as e:
    import traceback  # Added this line
    print("Error processing RAG checklist:")
    print(str(e))
    traceback.print_exc()
    raise HTTPException(...)
```

### Issue 2: UnboundLocalError with `asyncio`
**Error:**
```
UnboundLocalError: local variable 'asyncio' referenced before assignment
```

**Location:** Line 582 in `/backend/app/api/routes/veradoc.py`

**Root Cause:**
- `asyncio` was imported at the top of the file (line 50)
- There was a local `import asyncio` inside a question processing loop (line 1001)
- Since Python detected a local `import asyncio` anywhere in the function, it treated `asyncio` as a local variable for the entire function scope
- When line 582 tried to use `asyncio.sleep()` before reaching line 1001, Python raised an error because the local variable hadn't been assigned yet

**Solution:**
Removed the redundant local import at line 1001 since `asyncio` is already imported globally:
```python
# BEFORE (line 1001):
if i > 0 and settings.VERADOC_ENABLE_PROCESSING_DELAYS:
    import asyncio  # This was causing the problem
    await asyncio.sleep(settings.PROCESSING_DELAY_BETWEEN_REQUESTS)

# AFTER:
if i > 0 and settings.VERADOC_ENABLE_PROCESSING_DELAYS:
    await asyncio.sleep(settings.PROCESSING_DELAY_BETWEEN_REQUESTS)
```

## Python Scoping Rule Explanation

In Python, if a variable is assigned anywhere in a function (including via `import`), Python treats it as a local variable for the **entire function scope**, not just from that point onward. This is why:

1. Even though `asyncio` was imported globally at line 50
2. And used at line 582
3. Python saw `import asyncio` at line 1001
4. It treated `asyncio` as local for the entire function
5. Which caused an error when trying to use it at line 582 (before it was "assigned")

## Best Practices

1. **Import at the top of the file** - Keep all imports at module level unless there's a specific reason not to (e.g., avoiding circular imports, lazy loading)

2. **Avoid local imports** - Don't use `import` statements inside functions unless absolutely necessary

3. **If you must use local imports** - Make sure they happen before any usage of that module in the function

4. **Use globals consistently** - If a module is imported globally, don't re-import it locally

## Files Modified

1. `/backend/app/api/routes/veradoc.py`:
   - Line 1316: Added `import traceback` in exception handler
   - Line 1001: Removed redundant `import asyncio`

## Deployment

1. Backend rebuilt: `docker-compose build backend`
2. Backend restarted: `docker-compose up -d backend`
3. Status: ✅ Fixed and deployed

## Testing

The Review functionality should now work without these import scoping errors when:
- Processing documents with progress tracking
- Handling exceptions during review
- Adding delays between question processing
