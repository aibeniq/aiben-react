# Assistant Mode Implementation Guide

## Overview

This guide outlines the implementation of an "Assistant Mode" feature for the application. When enabled, users can provide natural language requests along with file uploads to the chatbot, and the system will automatically determine the appropriate function (Review, Generate, Match, Compare), navigate to the correct page, and pre-fill inputs to execute the operation seamlessly.

## 1. UI Integration: Add Assistant Mode Toggle

Add a toggle switch in the chatbot panel to enable/disable Assistant Mode.

**File:** `frontend/src/components/Chatbot/ChatbotPanel.tsx`

```tsx
// ...existing code...
import { FormControl, FormLabel, Switch } from "@chakra-ui/react"

// Inside the component
const { assistantMode, setAssistantMode } = props // Passed from parent

// Add this JSX element in the appropriate location (e.g., after the chat input)
;<FormControl display="flex" alignItems="center" mt={2}>
  <FormLabel htmlFor="assistant-mode" mb="0">
    {t("chatbot.enableAssistantMode")}
  </FormLabel>
  <Switch
    id="assistant-mode"
    isChecked={assistantMode}
    onChange={(e) => setAssistantMode(e.target.checked)}
  />
</FormControl>
// ...existing code...
```

## 2. State Management

Manage the Assistant Mode state in the parent component.

**File:** `frontend/src/components/Chatbot/ChatbotMain.tsx`

```tsx
// ...existing code...
import { useState } from "react"

// Inside the component
const [assistantMode, setAssistantMode] = useState(false)

// Pass to ChatbotPanel
;<ChatbotPanel
  // ...existing props...
  assistantMode={assistantMode}
  setAssistantMode={setAssistantMode}
/>
// ...existing code...
```

## 3. Intercept Chat Submission

Modify the chat submission logic to route requests to the assistant handler when Assistant Mode is enabled.

**File:** `frontend/src/components/Chatbot/ChatbotPanel.tsx`

```tsx
// ...existing code...
const handleSubmit = async (message: string, files: File[]) => {
  if (assistantMode) {
    await handleAssistantRequest(message, files)
  } else {
    // Normal chat submission logic
    await handleNormalChat(message, files)
  }
}
// ...existing code...
```

## 4. Assistant Mode Handler

Create a function to analyze the request, determine intent, and navigate accordingly.

**File:** `frontend/src/components/Chatbot/ChatbotPanel.tsx` (or extract to a separate utility)

```tsx
// ...existing code...
import { useRouter } from "@tanstack/react-router"

const router = useRouter()

const handleAssistantRequest = async (message: string, files: File[]) => {
  // 1. Analyze message and files
  const intent = await detectIntent(message, files)

  // 2. Store data in global state
  setAssistantData({ message, files, assistantMode: true })

  // 3. Clear the input fields
  setQuestion("")
  setUploadedFiles([])

  // 4. Navigate to appropriate page using router (preserves React state)
  if (intent.type === "review") {
    await router.navigate({ to: "/review" })
  } else if (intent.type === "generate") {
    await router.navigate({ to: "/generate" })
  } else if (intent.type === "compare") {
    await router.navigate({ to: "/compare" })
  } else if (intent.type === "match") {
    await router.navigate({ to: "/match" })
  } else {
    // Fallback to normal chat
    await handleSendMessage()
  }
}
}

const detectIntent = async (message: string, files: File[]): Promise<{ type: string }> => {
  // Implement intent detection logic
  // This could use keyword matching or call an LLM API
  // For now, simple keyword-based detection
  const lowerMessage = message.toLowerCase()

  if (lowerMessage.includes("review") || lowerMessage.includes("checklist")) {
    return { type: "review" }
  } else if (lowerMessage.includes("generate") || lowerMessage.includes("report")) {
    return { type: "generate" }
  } else if (lowerMessage.includes("compare")) {
    return { type: "compare" }
  } else if (lowerMessage.includes("match") || lowerMessage.includes("form")) {
    return { type: "match" }
  }

  return { type: "chat" } // Default to normal chat
}
// ...existing code...
```

**⚠️ Critical Fix:** Use `router.navigate()` instead of `window.location.href` to preserve React state across navigation. The latter causes a full page reload that destroys all component state, including the uploaded files.

## 5. Routing and Prefilling Inputs

Use TanStack Router to handle navigation with search parameters. For file handling, consider using global state (e.g., Zustand) or local storage since files can't be passed via URL.

**Global State Example (using Zustand):**

Create a store for assistant mode data:

**File:** `frontend/src/stores/assistantStore.ts`

```typescript
import { create } from "zustand"

interface AssistantState {
  assistantMode: boolean
  targetRoute: string // Add target route to prevent cross-page activation
  message: string
  files: File[]
  setAssistantData: (data: Partial<AssistantState>) => void
}

export const useAssistantStore = create<AssistantState>((set) => ({
  assistantMode: false,
  targetRoute: "",
  message: "",
  files: [],
  setAssistantData: (data) => set(data),
}))
```

**File:** `frontend/src/components/Chatbot/ChatbotPanel.tsx`

```tsx
const handleAssistantRequest = async (message: string, files: File[]) => {
  // 1. Analyze message and files
  const intent = await detectIntent(message, files)

  // 2. Determine target route
  let targetRoute = ""
  if (intent.type === "review") {
    targetRoute = "/review"
  } else if (intent.type === "generate") {
    targetRoute = "/generate"
  } else if (intent.type === "compare") {
    targetRoute = "/compare"
  } else if (intent.type === "match") {
    targetRoute = "/match"
  }

  // 3. Store data in global state with target route
  setAssistantData({ message, files, assistantMode: true, targetRoute })

  // 4. Clear the input fields
  setQuestion("")
  setUploadedFiles([])

  // 5. Navigate to appropriate page
  // ... navigation code ...
}
```

**Critical Fix:** Each target page now checks `targetRoute === '/current-page'` before processing assistant mode, preventing unintended activation on other pages.

Update the handler to use the store:

**File:** `frontend/src/components/Chatbot/ChatbotPanel.tsx`

```tsx
// ...existing code...
import { useAssistantStore } from "../../stores/assistantStore"

const { setAssistantData } = useAssistantStore()

const handleAssistantRequest = async (message: string, files: File[]) => {
  const intent = await detectIntent(message, files)

  setAssistantData({ message, files, assistantMode: true })

  switch (intent.type) {
    case "review":
      router.navigate({ to: "/review" })
      break
    // ... other cases
  }
}
// ...existing code...
```

## 6. LLM-Based Intent Detection

For more sophisticated intent detection, create a backend endpoint that uses your LLM to analyze the message.

**Backend Endpoint:** `backend/app/api/routes/assistant.py`

```python
from fastapi import APIRouter, UploadFile, File
from typing import List

router = APIRouter()

@router.post("/detect-intent")
async def detect_intent(message: str, files: List[UploadFile] = File(...)):
    # Use your LLM to analyze the message and files
    # Return structured intent data
    intent = await analyze_with_llm(message, files)
    return {"intent": intent}
```

**Frontend Call:**

```tsx
const detectIntent = async (message: string, files: File[]): Promise<{ type: string }> => {
  const formData = new FormData()
  formData.append("message", message)
  files.forEach((file) => formData.append("files", file))

  const response = await fetch("/api/assistant/detect-intent", {
    method: "POST",
    body: formData,
  })

  const data = await response.json()
  return data.intent
}
```

## 7. Prefill Logic in Target Pages

Each target page should check for assistant mode data and prefill inputs accordingly.

**Example for Review Page:** `frontend/src/routes/_layout/review.tsx`

```tsx
// ...existing code...
import { useAssistantStore } from "../../stores/assistantStore"
import { useEffect } from "react"

const ReviewPage = () => {
  const { message, files, assistantMode, setAssistantData } = useAssistantStore()

  useEffect(() => {
    if (assistantMode) {
      // Prefill the form
      setSelectedFiles(files)
      setCustomInstructions(message)
      // Trigger the review process
      handleReview()
      // Reset assistant mode
      setAssistantData({ assistantMode: false, message: "", files: [] })
    }
  }, [assistantMode, message, files])

  // ...existing code...
}
// ...existing code...
```

**Example for Compare Page:** `frontend/src/routes/_layout/compare.tsx`

```tsx
// ...existing code...
import { useAssistantStore } from "../../stores/assistantStore"

// Inside the component
const { message: assistantMessage, files: assistantFiles, assistantMode } = useAssistantStore()

// Initialize state with assistant data if available
const [document1, setDocument1] = useState<File | null>(
  assistantMode && assistantFiles.length >= 1
    ? assistantFiles[0]
    : compareInputs?.document1 || null,
)
const [document2, setDocument2] = useState<File | null>(
  assistantMode && assistantFiles.length >= 2
    ? assistantFiles[1]
    : compareInputs?.document2 || null,
)
const [topics, setTopics] = useState(
  assistantMode && assistantMessage ? assistantMessage : compareInputs?.topics || "",
)

// Assistant mode execution
useEffect(() => {
  const runAssistantMode = async () => {
    if (assistantMode && assistantFiles.length >= 2) {
      // Files and topics are already initialized above

      // Generate topics automatically using the suggest topics feature
      try {
        const topicsResponse = await TwincheckService.generateTopics({
          formData: {
            description: assistantMessage || "Compare these two documents",
            files: [assistantFiles[0], assistantFiles[1]],
          },
          searchMode: "vector",
        })

        if (topicsResponse.topics && Array.isArray(topicsResponse.topics)) {
          setTopics(topicsResponse.topics.join("\n"))
        }

        // Trigger the comparison automatically after a short delay
        setTimeout(() => {
          handleCompare()
          // Reset assistant mode after operation completes
          setTimeout(() => {
            setAssistantData({ assistantMode: false, message: "", files: [] })
          }, 1000)
        }, 500)
      } catch (error) {
        console.error("Failed to generate topics:", error)
        // Fallback: keep the message as topics and proceed
        setTimeout(() => {
          handleCompare()
          setTimeout(() => {
            setAssistantData({ assistantMode: false, message: "", files: [] })
          }, 1000)
        }, 500)
      }
    }
  }

  runAssistantMode()
}, [assistantMode, assistantMessage, assistantFiles])
// ...existing code...
```

Apply similar logic to other pages (Generate, Match).

## 8. User Experience Enhancements

- Show a loading indicator during intent detection and navigation.
- Display a toast notification: "Assistant Mode: Processing your request..."
- After navigation, automatically start the operation if all required inputs are available.

## 9. Localization

Add the necessary translation keys.

**File:** `frontend/src/locales/en/common.json`

```json
{
  "chatbot": {
    // ...existing code...
    "enableAssistantMode": "Enable Assistant Mode"
  }
}
```

Add similar keys for other languages.

## 10. Error Handling and Edge Cases

- Handle cases where intent detection fails or returns ambiguous results.
- Provide fallback to normal chat if intent cannot be determined.
- Validate that required inputs (e.g., files for certain operations) are present.
- Handle file size limits and unsupported formats.

## 11. Testing

- Test the toggle functionality.
- Test intent detection with various message types.
- Test navigation and prefilling for each operation type.
- Test error scenarios (no files, ambiguous intent, etc.).

## Summary

Implementing Assistant Mode involves:

1. ✅ Adding a UI toggle for enabling the mode.
2. ✅ Managing state across components.
3. ✅ Intercepting chat submissions when enabled.
4. ✅ Creating an intent detection system (simple or LLM-based).
5. ✅ Navigating to appropriate pages with prefilled data.
6. ✅ **Automatically triggering operations on the target pages**.

This creates a seamless experience where users can interact naturally with the application, and the system intelligently routes their requests to the appropriate functionality AND executes them automatically.

### **Key Enhancement: Automatic Execution**

The Assistant Mode now goes beyond just prefilling forms - it automatically executes the requested operations:

- **Review**: Automatically runs document review against selected knowledge base
- **Generate**: Automatically generates documents based on the provided outline/sections
- **Compare**: Automatically generates comparison topics and runs document comparison
- **Match**: Automatically processes forms and matches against uploaded documents

### **Smart Features:**

- **Compare Page**: Uses the `generateTopics` API to automatically suggest comparison topics based on the documents and user message
- **Fallback Handling**: If topic generation fails, uses the user's message as topics
- **Timing**: Operations are triggered after a 500ms delay to ensure form state is properly updated
- **Error Resilience**: Continues with fallback approaches if automatic features fail

## Next Steps

1. Implement the UI toggle.
2. Set up global state management.
3. Create the assistant request handler.
4. Implement intent detection (start with keyword-based, upgrade to LLM later).
5. Add prefilling logic to each target page.
6. Test thoroughly and iterate based on user feedback.
