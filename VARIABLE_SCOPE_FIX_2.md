# Variable Scope Fix #2 Applied

## Problem Fixed

**UnboundLocalError**: `local variable 'minimal_text_pages' referenced before assignment` on line 1137

## Root Cause

The `minimal_text_pages` variable was being used in condition checking logic before it was defined:

```python
# ❌ BEFORE: Used before definition
if not table_pages and not minimal_text_pages:  # Line ~1130
    # ... condition checking ...

minimal_text_pages = []  # Line ~1190 - defined after use
```

## Solution Applied

Moved the `minimal_text_pages` detection and `all_vision_candidate_pages` calculation to occur before the condition checks:

```python
# ✅ AFTER: Define before use
# Check for minimal text pages (moved earlier)
minimal_text_pages = []
for i, doc in enumerate(documents):
    # ... detection logic ...

# Calculate all vision candidate pages
all_vision_candidate_pages = list(set(table_pages + minimal_text_pages))

# Now can safely use variables in condition checks
if not table_pages and not minimal_text_pages:
    # ... condition checking ...
```

## Changes Made

1. **Moved minimal text detection** from after condition checks to before them
2. **Moved all_vision_candidate_pages calculation** to follow minimal text detection
3. **Removed duplicate code** that was created during the move

## Impact

- ✅ **Fixed**: UnboundLocalError eliminated for `minimal_text_pages`
- ✅ **Fixed**: `all_vision_candidate_pages` now available when needed
- ✅ **Preserved**: All enhanced image-heavy detection functionality maintained
- ✅ **Improved**: Better logical flow - detect first, then check conditions

The enhanced image-heavy table processing should now work without variable scope errors and properly detect APA sample tables and other web-based PDFs.
