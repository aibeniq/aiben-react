# NEXT STEPS - Frontend Progress Bar Implementation

## ✅ Completed
1. ✅ Created `useReportGenieProgress` hook for progress polling
2. ✅ Updated all 4 ReportGenie frontend pages:
   - ✅ Review (VeraDoc) - `/frontend/src/routes/_layout/review.tsx`
   - ✅ Generate (ReportGenie) - `/frontend/src/routes/_layout/generate.tsx`
   - ✅ Match (FormConnect) - `/frontend/src/routes/_layout/match.tsx`
   - ✅ Compare (TwinCheck) - `/frontend/src/routes/_layout/compare.tsx`
3. ✅ Replaced loading spinners with progress bar overlays
4. ✅ Added task creation and completion handling logic
5. ✅ Backend progress tracking endpoints already implemented

## ⚠️ REQUIRED: Regenerate OpenAPI Client SDK

The frontend TypeScript client SDK needs to be regenerated to include the new task creation endpoints that the frontend is now calling.

### Commands to Run:

```bash
# 1. Start Docker containers (if not running)
cd /home/ec2-user/aiben-react
docker-compose up -d

# 2. Generate OpenAPI spec from inside the backend container
docker-compose exec backend python generate_openapi.py

# 3. In the frontend directory, regenerate the TypeScript client
cd frontend
npm run generate-client
```

### New Methods That Will Be Added:

The client SDK will include these new methods from the backend:

**ReportgenieService**:
- `createGenerateTask()` - Create task for report generation
- `createGenerateOutlineTask()` - Create task for outline generation  
- `createOptimizeOutlineTask()` - Create task for outline optimization
- `getProgress(task_id)` - Get progress for any reportgenie task

**VeradocService**:
- `createGenerateTask()` - Create task for review/veradoc

**FormconnectService**:
- `createOptimizeOutlineTask()` - Create task for form matching

**TwincheckService**:
- `createOptimizeOutlineTask()` - Create task for document comparison

### Why This Is Needed:

All 4 frontend pages are currently calling these methods:
```typescript
// Example from generate.tsx
const taskResponse = await ReportgenieService.createGenerateTask({ ... })
const newTaskId = taskResponse.task_id
```

Without regenerating the client SDK, these method calls will fail with TypeScript errors and runtime errors.

## Testing After SDK Regeneration

Once the SDK is regenerated, test each workflow:

### 1. Test Generate Workflow
1. Go to Generate page
2. Select a Knowledge Base
3. Enter some sections  
4. Click "Generate Document"
5. **VERIFY**: Progress bar appears with:
   - "Setting up report generation..." (10%)
   - "Generating report content..." (80%)
   - "Finalizing report..." (10%)
6. **VERIFY**: Progress bar disappears and results appear

### 2. Test Review Workflow
1. Go to Review page
2. Upload a file
3. Select Knowledge Base
4. Enter questions
5. Click "Run"
6. **VERIFY**: Progress bar appears with:
   - "Setting up document review..." (10%)
   - "Generating review responses..." (80%)
   - "Finalizing review..." (10%)
7. **VERIFY**: Progress bar disappears and results appear

### 3. Test Match Workflow
1. Go to Match page
2. Upload a file
3. Select a form template
4. Click "Run"
5. **VERIFY**: Progress bar appears with multiple stages
6. **VERIFY**: Progress bar disappears and results appear

### 4. Test Compare Workflow
1. Go to Compare page
2. Upload two documents
3. Enter comparison topics
4. Click "Compare"
5. **VERIFY**: Progress bar appears with multiple stages
6. **VERIFY**: Progress bar disappears and results appear

## Implementation Summary

### Progress Bar Pattern (Same as Knowledge Base Creation)

1. **Task Creation**: Frontend creates task to get `task_id`
2. **Polling Starts**: `useReportGenieProgress(taskId)` polls every 1 second
3. **Operation Executes**: Backend operation runs with `task_id`
4. **Progress Updates**: Backend updates Redis progress using `task_id`
5. **Frontend Display**: Progress bar shows percentage and message
6. **Completion**: Progress completes, bar disappears after 1.5s delay

### Visual Design

- **Dark Overlay**: `blackAlpha.800` background (same as Knowledge Base)
- **Progress Message**: Large white text showing current stage
- **Progress Bar**: Blue Chakra UI Progress component
- **Percentage**: Displayed below progress bar
- **Instructions**: "Please wait..." message

### Error Handling

- Progress errors are displayed via toast notifications
- Failed tasks clear taskId and show error message
- Completion handler prevents multiple success notifications
- Clean state reset on new task or error

## Files Modified

1. `/frontend/src/hooks/useReportGenieProgress.ts` - NEW
2. `/frontend/src/routes/_layout/review.tsx` - MODIFIED
3. `/frontend/src/routes/_layout/generate.tsx` - MODIFIED
4. `/frontend/src/routes/_layout/match.tsx` - MODIFIED
5. `/frontend/src/routes/_layout/compare.tsx` - MODIFIED

## Documentation Created

1. `REPORTGENIE_FRONTEND_PROGRESS_IMPLEMENTATION.md` - Complete implementation details
2. This file - Next steps and testing guide

## Status

✅ **Frontend Implementation**: COMPLETE
⚠️ **SDK Regeneration**: REQUIRED (run commands above)
⏳ **Testing**: PENDING (after SDK regeneration)
⏳ **Deployment**: PENDING (after testing)
