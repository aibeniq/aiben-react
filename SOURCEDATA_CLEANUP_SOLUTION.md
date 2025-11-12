# SourceData Cleanup Solution

## Problem
The `source_data` SQL table accumulates orphaned entries when knowledge bases or sources are deleted. This happens because:

1. Your system uses **file hash deduplication** - multiple `Source` entries can reference the same `SourceData`
2. When a knowledge base is deleted, `Source` entries are cascade-deleted
3. However, the referenced `SourceData` entries are NOT automatically deleted
4. Over time, orphaned `SourceData` entries accumulate and bloat the database

## Solution Implemented

### 1. Application-Level Cleanup (Automatic)
Modified `delete_knowledge_base()` in `backend/app/api/routes/knowledgebases.py`:

- Before deleting the knowledge base, collect all `source_data_id` references
- Delete the knowledge base (cascades to `Source` entries)
- For each `source_data_id`, check if any `Source` entries still reference it
- If reference count = 0, delete the orphaned `SourceData` entry

This ensures **future deletions are clean** and don't leave orphans.

### 2. One-Time Cleanup Script
Created `cleanup_orphaned_source_data.py` to clean up **existing orphaned data**:

```bash
# Run from the project root
python cleanup_orphaned_source_data.py
```

This script:
- Identifies all `SourceData` entries not referenced by any `Source`
- Deletes them and reports storage freed
- Should be run once to clean up historical orphans

## Why This Approach?

### ❌ Why NOT Database CASCADE DELETE?
Adding `ON DELETE CASCADE` from `Source` → `SourceData` would break your deduplication system:

```
KB1 has Source1 → SourceData1 (file.pdf)
KB2 has Source2 → SourceData1 (same file.pdf, deduplicated)

If we delete KB2:
- Source2 deleted → SourceData1 CASCADE DELETED
- KB1 loses access to its file! ❌
```

### ✅ Why Application-Level Reference Counting?
- Preserves the many-to-one relationship (multiple Sources → one SourceData)
- Only deletes SourceData when reference count reaches zero
- Matches your existing pattern in `update_knowledge_base()` and `delete_source()`

## Verification

After running the cleanup script, you can verify:

```sql
-- Check for orphaned SourceData entries
SELECT sd.id 
FROM "source-data" sd
LEFT JOIN sources s ON s.source_data_id = sd.id
WHERE s.id IS NULL;

-- Should return 0 rows after cleanup
```

## Files Modified

1. `backend/app/api/routes/knowledgebases.py` - Added cleanup logic to `delete_knowledge_base()`
2. `cleanup_orphaned_source_data.py` - One-time cleanup script

## Next Steps

1. **Run the cleanup script** to remove existing orphaned data:
   ```bash
   python cleanup_orphaned_source_data.py
   ```

2. **Test the fix** by:
   - Creating a knowledge base with files
   - Deleting the knowledge base
   - Verifying no orphaned `SourceData` entries remain

3. **Monitor** database size over time to confirm the issue is resolved

## Additional Notes

The same cleanup pattern is already used in:
- `update_knowledge_base()` when removing files
- `delete_source()` when deleting individual sources

This fix extends that pattern to knowledge base deletion for consistency.
