# Feedback UI Implementation Debug Guide

## Current Status

The feedback UI elements have been implemented for both Generate and Match tabs with the following components:

### ✅ What's Implemented

1. **Generate Tab (`/generate`)**:

   - ✅ FeedbackButtons component imported
   - ✅ interactionId state variable
   - ✅ handleFeedbackSubmitted function
   - ✅ Mutation captures interaction_id from backend response
   - ✅ Feedback buttons rendered conditionally in results area
   - ✅ Debug logging added

2. **Match Tab (`/match`)**:

   - ✅ FeedbackButtons component imported
   - ✅ interactionId state variable
   - ✅ handleFeedbackSubmitted function
   - ✅ Mutation captures interaction_id from backend response
   - ✅ Feedback buttons rendered conditionally in results area
   - ✅ Debug logging added

3. **Backend APIs**:
   - ✅ ReportGenie API returns interaction_id
   - ✅ FormConnect API returns interaction_id

## How to Test & Debug

### Step 1: Open Browser Developer Tools

1. Navigate to the application at `http://localhost:5174/`
2. Open browser Developer Tools (F12)
3. Go to the Console tab

### Step 2: Test Generate Tab

1. Go to the Generate tab
2. Select a knowledge base
3. Enter some section content
4. Click "Generate"
5. Watch the console for these debug messages:
   ```
   Generate Response data: {results: {...}}
   Generate interaction_id: [should show an ID or null]
   Generate interactionId for feedback: [should show an ID or null]
   ```

**Expected Behavior:**

- If interaction_id is received: You should see feedback buttons with red background
- If no interaction_id: You should see yellow box with "Debug: No interaction ID found"

### Step 3: Test Match Tab

1. Go to the Match tab
2. Upload some files
3. Enter field names
4. Click "Run"
5. Watch the console for these debug messages:
   ```
   Match Response data: {results: {...}}
   Match interaction_id: [should show an ID or null]
   Match interactionId for feedback: [should show an ID or null]
   ```

**Expected Behavior:**

- If interaction_id is received: You should see feedback buttons with red background
- If no interaction_id: You should see yellow box with "Debug: No interaction ID found"

## Troubleshooting

### Issue 1: No Debug Box Appears

**Cause**: Results aren't being generated
**Solution**: Make sure the operation completes successfully and produces results

### Issue 2: Yellow Debug Box Appears

**Cause**: Backend isn't returning interaction_id
**Solutions**:

1. Check that backend is running and updated with latest code
2. Check Network tab in browser dev tools for API response structure
3. Verify backend database connections are working

### Issue 3: Red Box with Feedback Buttons Appears

**Status**: ✅ This means everything is working correctly!

### Issue 4: Feedback Buttons Don't Respond

**Cause**: Component or handler issues
**Solutions**:

1. Check console for JavaScript errors
2. Verify FeedbackButtons component is properly imported
3. Check that handleFeedbackSubmitted function is defined

## Debug Output Analysis

When testing, you should see console output like this:

**Successful Generate:**

```
Generate Response data: {
  results: {
    full_report: "...",
    sections: [...],
    interaction_id: "uuid-string-here"
  }
}
Generate interaction_id: uuid-string-here
Generate interactionId for feedback: uuid-string-here
```

**Successful Match:**

```
Match Response data: {
  results: {
    comparison: "...",
    interaction_id: "uuid-string-here"
  }
}
Match interaction_id: uuid-string-here
Match interactionId for feedback: uuid-string-here
```

## Removing Debug Code

Once testing is complete and feedback buttons are working, remove the debug elements:

1. Remove the debug console.log statements
2. Remove the yellow debug boxes
3. Remove the red background from feedback button containers
4. Change conditional rendering back to only show when interactionId exists

## Final Implementation

The final code should look like this:

```tsx
{
  /* Generate Tab - Final Version */
}
{
  interactionId && (
    <Box
      position="sticky"
      bottom={4}
      right={4}
      display="flex"
      justifyContent="flex-end"
      pointerEvents="auto"
      zIndex={10}
      mt={4}
    >
      <FeedbackButtons
        interactionId={interactionId}
        onFeedbackSubmitted={handleFeedbackSubmitted}
      />
    </Box>
  )
}

{
  /* Match Tab - Final Version */
}
{
  interactionId && (
    <Box
      position="sticky"
      bottom={4}
      right={4}
      display="flex"
      justifyContent="flex-end"
      pointerEvents="auto"
      zIndex={10}
      mt={4}
    >
      <FeedbackButtons
        interactionId={interactionId}
        onFeedbackSubmitted={handleFeedbackSubmitted}
      />
    </Box>
  )
}
```
