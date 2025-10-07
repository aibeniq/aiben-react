# CRITICAL FIX: Progress Hook Re-mounting Issue - October 7, 2025

## Problem Description

The progress bar for **Full Document Scan reviews** would stop updating after the first question, showing only:
```
"Answering question 1/2 for file 1/1: What is your name?"
```

Even though the backend logs showed:
- ✅ Question 2 completed
- ✅ Reviewing stage completed
- ✅ Finalizing stage completed
- ✅ Task marked as completed
- ✅ Results stored

The frontend never received these updates and the progress bar appeared stuck.

## Root Cause

The `useVeradocProgress` hook had `pollCount` in its `useEffect` dependency array:

```typescript
}, [taskId, pollCount])  // ❌ WRONG - causes re-mount on every poll!
```

### What This Caused

1. **Every second**, the `pollProgress` function would execute
2. This would increment `pollCount` via `setPollCount((prev) => prev + 1)`
3. Because `pollCount` was in the dependency array, **the entire effect re-ran**
4. This triggered the cleanup function:
   ```typescript
   return () => {
       isActive = false
       clearInterval(intervalId)
   }
   ```
5. A **new interval** was created, starting the cycle again

### Observable Symptoms

Browser console showed this pattern repeating:
```
🔍 VERADOC PROGRESS: Response received: {...}
🔍 VERADOC PROGRESS: Component unmounted, stopping  ← Effect cleanup
🔍 VERADOC PROGRESS: Response received: {...}
🔍 VERADOC PROGRESS: Component unmounted, stopping  ← Effect cleanup again
```

The hook was **constantly killing and restarting itself**, so it would:
- Poll once
- Receive response (e.g., "Answering question 1/2")
- Update state
- Trigger re-mount
- Kill the interval
- Start new interval
- Poll again
- Get the **same response** (because backend hasn't progressed yet)
- Repeat...

## The Fix

### Changed: Removed `pollCount` from Dependencies

**Before:**
```typescript
const [pollCount, setPollCount] = useState(0)

useEffect(() => {
    // ... polling logic ...
    setPollCount((prev) => prev + 1)  // Causes re-mount!
}, [taskId, pollCount])  // ❌ WRONG
```

**After:**
```typescript
const pollCountRef = useRef(0)  // Use ref instead of state

useEffect(() => {
    // ... polling logic ...
    pollCountRef.current += 1  // No state update, no re-mount!
}, [taskId])  // ✅ CORRECT - only re-run when taskId changes
```

### Why This Works

1. **Refs don't cause re-renders**: Changing `pollCountRef.current` doesn't trigger component updates
2. **Effect runs once per taskId**: The effect only re-runs when `taskId` changes, not on every poll
3. **Interval stays alive**: The interval continues polling without being killed and recreated
4. **Progress updates work**: The frontend receives all progress updates from backend

## Code Changes

**File: `/frontend/src/hooks/useVeradocProgress.ts`**

1. **Line 1**: Added `useRef` import
   ```typescript
   import { useEffect, useState, useRef } from "react"
   ```

2. **Line 27**: Changed from state to ref
   ```typescript
   const pollCountRef = useRef(0)  // Was: const [pollCount, setPollCount] = useState(0)
   ```

3. **Lines 43, 54, 62, 63, 94, 97, 110**: Replaced all `pollCount` with `pollCountRef.current`
   ```typescript
   pollCountRef.current += 1  // Was: setPollCount((prev) => prev + 1)
   willStopPolling: pollCountRef.current >= MAX_POLLS - 10
   currentPollCount: pollCountRef.current
   ```

4. **Line 127**: Removed `pollCount` from dependency array
   ```typescript
   }, [taskId])  // Was: }, [taskId, pollCount])
   ```

## Testing

### Before Fix
- Progress stuck at "Answering question 1/2"
- Console shows repeated "Component unmounted, stopping"
- Backend completes but frontend never sees it
- Users see frozen progress bar

### After Fix
- Progress updates smoothly through all stages
- No "Component unmounted" messages during polling
- Frontend receives all backend updates
- Users see:
  - "Answering question 1/2" 
  - "Completed question 1/2"
  - "Answering question 2/2"
  - "Completed question 2/2"
  - "Generating final evaluation"
  - "Review completed successfully"

## Why This Affected Full Document Scan More

**Vector Search** (5-10 chunks):
- Each question completes in ~5-15 seconds
- Progress might update before the re-mount cycle completes
- Issue less noticeable

**Full Document Scan** (100+ chunks):
- Each question takes 30-60+ seconds
- Multiple re-mount cycles happen before backend updates
- Issue very noticeable - appears completely stuck

## Related Files

- `/frontend/src/hooks/useVeradocProgress.ts` - Progress polling hook (FIXED)
- `/frontend/src/routes/_layout/review.tsx` - Review page using the hook
- `/backend/app/api/routes/veradoc.py` - Backend progress updates

## Key Learnings

### React useEffect Dependencies

**Rule**: Only include values that should **trigger a re-run** of the effect in the dependency array.

**State vs Ref**:
- **State**: Triggers re-render when changed → include in dependencies
- **Ref**: Doesn't trigger re-render → exclude from dependencies

**For Counters in Effects**:
- ✅ Use `useRef` if the counter is only used inside the effect
- ❌ Don't use `useState` for internal effect counters

### Debugging Effect Re-mounts

Look for these patterns:
1. Cleanup messages appearing frequently in console
2. Effects running more often than expected  
3. Intervals being cleared and recreated
4. Same API calls being made repeatedly with same results

### Full Document Scan Considerations

Full Document Scan is a **long-running operation** that requires:
- ✅ Stable polling intervals (no re-mounting)
- ✅ Frequent progress updates (backend)
- ✅ Adequate event loop yielding (backend)
- ✅ Patient polling (frontend)

## Verification

After applying this fix:

1. ✅ Frontend polling stays active for entire review duration
2. ✅ All backend progress updates are received by frontend
3. ✅ Progress bar shows smooth transitions
4. ✅ No premature "Component unmounted" messages
5. ✅ Full Document Scan reviews complete successfully
6. ✅ Vector Search reviews continue working normally

## Status

**RESOLVED** - Frontend now correctly polls for progress without self-destructing on every update.
