import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"

interface ProgressData {
  percentage: number
  message: string
  isActive: boolean
  completed?: boolean
  error?: string
  message_key?: string
  message_params?: Record<string, any>
}

export const useKnowledgeBaseProgress = (taskId: string | null) => {
  const { t } = useTranslation()

  // Force console logs with timestamp to ensure they appear
  console.warn("🔄 HOOK CALLED:", new Date().toISOString(), "taskId:", taskId)

  // Log when task ID is received
  if (taskId) {
    console.warn("🎯 TASK ID RECEIVED:", taskId)
  }

  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    message: "",
    isActive: false,
  })

  useEffect(() => {
    const timestamp = new Date().toISOString()
    console.log(
      `🚀 FRONTEND HOOK EFFECT TRIGGERED at ${timestamp} with taskId:`,
      taskId,
    )

    if (!taskId) {
      // Reset progress state when no task is active
      setProgress({
        percentage: 0,
        message: "",
        isActive: false,
        completed: false,
        error: undefined,
      })
      console.log("🔄 No taskId - resetting progress state to initial")
      return
    }

    // CRITICAL FIX: Force immediate reset of all state to prevent cached completion
    // This ensures a completely fresh start for each new task
    console.log(
      "🔄 New task started, FORCE resetting ALL progress state for:",
      taskId,
    )
    setProgress({
      percentage: 0,
      message: "Starting knowledge base creation...",
      isActive: true,
      completed: false,
      error: undefined,
    })

    console.log(
      `🔄 Starting progress polling for task: ${taskId} at ${timestamp}`,
    )

    let intervalId: NodeJS.Timeout
    let isPolling = true
    let pollCount = 0
    let lastProgressUpdate = Date.now()
    let stuckCount = 0

    const pollProgress = async () => {
      if (!isPolling) {
        console.log("🛑 POLLING STOPPED: isPolling is false for task:", taskId)
        return
      }

      pollCount++
      const timestamp = new Date().toISOString()
      console.log(`📡 POLL #${pollCount} at ${timestamp} for task:`, taskId)

      try {
        console.log(
          "🔐 Making authenticated request to progress API for task:",
          taskId,
        )

        const data = await __request(OpenAPI, {
          method: "GET",
          url: `/api/v1/knowledge-bases/progress/${taskId}`,
        })

        // Enhanced debug logging
        console.log("📊 FRONTEND RECEIVED PROGRESS:", {
          percentage: (data as any).percentage,
          message: (data as any).message,
          message_key: (data as any).message_key,
          message_params: (data as any).message_params,
          status: (data as any).status,
          current_stage: (data as any).current_stage,
          taskId: taskId,
          pollCount: pollCount,
        })

        // Translate message using message_key if available, fallback to backend message
        let message: string
        if ((data as any).message_key) {
          // Use translation key with parameters
          message = t(
            (data as any).message_key,
            (data as any).message_params || {},
          ) as string
        } else {
          // Fallback to backend message (for backwards compatibility)
          message = (data as any).message || "Processing..."
        }

        const newProgress: ProgressData = {
          percentage: Math.round((data as any).percentage || 0),
          message,
          message_key: (data as any).message_key,
          message_params: (data as any).message_params,
          isActive:
            (data as any).status === "in_progress" ||
            (data as any).status === "started",
          completed: (data as any).status === "completed",
          error:
            (data as any).status === "failed"
              ? (data as any).error_message || message
              : undefined,
        }

        console.log("📊 FRONTEND SETTING PROGRESS STATE:", {
          ...newProgress,
          willStopPolling:
            (data as any).status === "completed" ||
            (data as any).status === "failed",
          receivedStatus: (data as any).status,
        })

        setProgress(newProgress)

        // Check for stuck progress
        const currentTime = Date.now()
        if (
          newProgress.percentage > 0 ||
          newProgress.message !== "Starting knowledge base creation..."
        ) {
          lastProgressUpdate = currentTime
          stuckCount = 0
        } else if (currentTime - lastProgressUpdate > 30000) {
          // 30 seconds of no progress
          stuckCount++
          if (stuckCount >= 3) {
            // 3 consecutive checks with no progress
            console.warn(
              "⚠️ PROGRESS STUCK: No progress updates for 90+ seconds, stopping polling",
            )
            isPolling = false
            if (intervalId) {
              clearInterval(intervalId)
            }
            setProgress((prev) => ({
              ...prev,
              error: "Upload appears to be stuck. Please try again.",
              isActive: false,
            }))
            return
          }
        }

        // Stop polling if completed or errored
        if (
          (data as any).status === "completed" ||
          (data as any).status === "failed"
        ) {
          console.log(
            "🛑 FRONTEND STOPPING POLLING:",
            (data as any).status === "completed" ? "success" : "error",
          )
          isPolling = false
          clearInterval(intervalId)
        } else {
          console.log(
            "✅ FRONTEND CONTINUING POLLING: status =",
            (data as any).status,
            "poll count =",
            pollCount,
          )
        }
      } catch (error) {
        console.error(
          "❌ Error polling progress for task",
          taskId,
          `poll #${pollCount}:`,
          error,
        )

        // Check if this is a 404 (task not found) which indicates completion or task cleanup
        if (error instanceof Error && error.message.includes("404")) {
          console.log(
            "🔍 Task not found (404) - may have been cleaned up after completion",
          )
          // Don't stop polling immediately on 404 - it might be temporary
          // Only stop if we've had multiple 404s in a row
        } else {
          console.log("🔄 Network error, continuing to poll...")
        }

        // Continue polling on errors in case they're temporary
      }
    }

    // Start polling immediately, then every 2 seconds
    console.log("🚀 STARTING INITIAL POLL for task:", taskId)
    pollProgress()

    // CRITICAL FIX: Add a small delay before starting the interval to ensure
    // component re-renders don't interfere with the polling setup
    const startInterval = () => {
      intervalId = setInterval(() => {
        console.log(
          "⏰ INTERVAL TICK - polling for task:",
          taskId,
          "isPolling:",
          isPolling,
        )
        pollProgress()
      }, 5000) // Increased from 2000 to 5000 milliseconds
    }

    // Start interval immediately if no task is being processed,
    // or with small delay to avoid interference from component re-renders
    setTimeout(startInterval, 50)

    // CRITICAL DEBUG: Log any external factors that might disrupt polling
    console.log(
      "🎯 Progress polling setup complete for task:",
      taskId,
      "- polling should continue until 100%",
    )

    // Cleanup function
    return () => {
      const timestamp = new Date().toISOString()
      console.log(
        `🛑 CLEANUP at ${timestamp}: Stopping progress polling for task:`,
        taskId,
        "isPolling was:",
        isPolling,
        "pollCount was:",
        pollCount,
      )
      isPolling = false
      if (intervalId) {
        clearInterval(intervalId)
        console.log("🧹 CLEANUP: Interval cleared for task:", taskId)
      }
    }
  }, [taskId])

  return progress
}
