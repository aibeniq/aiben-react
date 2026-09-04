# Progress Bar State Update Investigation - October 7, 2025

## Current Status: INVESTIGATING

### Problem Description

The progress bar for **Full Document Scan reviews** shows outdated progress messages even though the frontend console logs confirm that newer progress updates ARE being received.

**Observed Behavior:**
- **Progress Bar Shows**: "Beginning document review with policy context"
- **Console Logs Show**: "Answering question 1/2 for file 1/1: What is your name?"
- **Backend Logs Show**: All questions completed, task finished successfully

This means:
1. ✅ Backend is sending progress updates correctly
2. ✅ Frontend progress hook is RECEIVING updates correctly
3. ❌ Frontend UI is NOT displaying the latest progress

### Console Log Evidence

```
🔍 VERADOC PROGRESS: Response received: {
  message: "Answering question 1/2 for file 1/1: What is your name?",
  percentage: 65,
  status: "in_progress"
}
🔍 VERADOC PROGRESS: Component unmounted, stopping
🧹 Operation removed from tracking (0 remaining)
🚀 Review backend processing complete
```

###Key Observations

1. **Component is unmounting prematurely**: "Component unmounted, stopping" appears while processing is still active
2. **State updates may not be rendering**: `setProgress(newProgress)` is called but UI doesn't reflect the change
3. **Operation removed from tracking**: Happens when backend request completes, possibly triggering component re-render

## Potential Root Causes

### 1. Component Re-rendering Issue

The Review component might be re-rendering when the backend request completes (`onSuccess` callback), potentially causing:
- State to be reset
- Progress hook to re-initialize
- Old progress state to be displayed

### 2. React Batching/State Staleness

React might be batching state updates, causing the UI to display a stale value from `progress.message` even though the hook has updated its internal state.

### 3. Memoization or Caching Issue

The `progress` object returned from `useVeradocProgress` might be memoized or cached incorrectly, preventing React from detecting changes.

### 4. Component Unmounting Before Final Updates

The cleanup in `useOperationCancellation` (line 91-99) runs when the component unmounts, which might be happening when the backend request completes but BEFORE the final progress updates are received.

## Debugging Steps Added

### 1. Enhanced Progress Hook Logging

Added to `/frontend/src/hooks/useVeradocProgress.ts`:
```typescript
console.log("📊 Previous progress state:", progress)
setProgress(newProgress)
console.log("✅ setProgress() called with message:", newProgress.message)
```

This will show:
- The previous state before update
- The new state being set
- Confirmation that setProgress was called

### 2. Progress State Change Logging

Added to `/frontend/src/routes/_layout/review.tsx`:
```typescript
useEffect(() => {
  console.log("📊 REVIEW PAGE: Progress object updated:", {
    message: progress.message,
    percentage: progress.percentage,
    isActive: progress.isActive,
    completed: progress.completed
  })
}, [progress])
```

This will show when the Review component receives new progress values from the hook.

## Investigation Plan

1. **Test with new logging**: Run a Full Document Scan review and check console for:
   - Is `setProgress()` being called with the correct message?
   - Is the Review component's `useEffect` seeing the updated progress?
   - Is there a delay or missing update between these two?

2. **Check for re-renders**: Look for signs of component unmounting/remounting:
   - Multiple "🔍 VERADOC PROGRESS: Starting polling" messages
   - Component unmount messages before completion

3. **Verify state persistence**: Confirm that the `progress` object reference is stable across renders

## Hypotheses to Test

### Hypothesis A: State Not Propagating to UI
- **Test**: Check if `setProgress()` is called but Review component doesn't see the update
- **If True**: Issue with hook's state management or React rendering
- **Fix**: Force re-render or investigate hook dependencies

### Hypothesis B: Component Unmounting Too Early
- **Test**: Look for unmount message before all progress updates received
- **If True**: `onSuccess` callback is causing component to unmount
- **Fix**: Delay unmount until progress polling completes

### Hypothesis C: Progress Hook Re-initializing
- **Test**: Check if effect restarts (new "Starting polling" message) mid-process
- **If True**: `taskId` or other dependency is changing
- **Fix**: Stabilize dependencies or use refs

## Expected Debug Output

### Normal Flow (Working)
```
🔍 VERADOC PROGRESS: Starting polling for task_id: xxx
🔍 VERADOC PROGRESS: Polling attempt 1
🔍 VERADOC PROGRESS: Response received: {message: "Beginning document review..."}
📊 Previous progress state: {message: "", percentage: 0}
✅ setProgress() called with message: "Beginning document review..."
📊 REVIEW PAGE: Progress object updated: {message: "Beginning document review...", percentage: 5}
... (more polls) ...
🔍 VERADOC PROGRESS: Response received: {message: "Answering question 1/2..."}
📊 Previous progress state: {message: "Beginning document review...", percentage: 5}
✅ setProgress() called with message: "Answering question 1/2..."
📊 REVIEW PAGE: Progress object updated: {message: "Answering question 1/2...", percentage: 65}
```

### Broken Flow (If State Not Propagating)
```
🔍 VERADOC PROGRESS: Response received: {message: "Answering question 1/2..."}
📊 Previous progress state: {message: "Beginning document review...", percentage: 5}
✅ setProgress() called with message: "Answering question 1/2..."
📊 REVIEW PAGE: Progress object updated: {message: "Beginning document review...", percentage: 5}  ← WRONG!
```

### Broken Flow (If Component Unmounting)
```
🔍 VERADOC PROGRESS: Response received: {message: "Answering question 1/2..."}
🔍 VERADOC PROGRESS: Component unmounted, stopping  ← TOO EARLY!
🚀 Review backend processing complete
```

## Next Steps

1. Wait for frontend restart to complete
2. Run Full Document Scan test review
3. Analyze debug logs to identify which hypothesis is correct
4. Apply appropriate fix based on findings

## Related Files

- `/frontend/src/hooks/useVeradocProgress.ts` - Progress polling hook
- `/frontend/src/routes/_layout/review.tsx` - Review page component
- `/frontend/src/hooks/useOperationCancellation.ts` - Operation cleanup hook

## Status

**PENDING TESTING** - Frontend restarting with enhanced debug logging
