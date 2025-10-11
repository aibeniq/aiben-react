import { useTranslation } from "react-i18next"
import { useEffect, useState } from "react"
import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"

interface ProgressData {
  percentage: number
  message: string
  isActive: boolean
  completed?: boolean
  error?: string
}

export const useReportGenieProgress = (taskId: string | null) => {
  const { t } = useTranslation()
  console.warn(
    "🔄 REPORTGENIE PROGRESS HOOK CALLED:",
    new Date().toISOString(),
    "taskId:",
    taskId,
  )

  if (taskId) {
    console.warn("🎯 REPORTGENIE TASK ID RECEIVED:", taskId)
  }

  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    message: "",
    isActive: false,
  })

  useEffect(() => {
    const timestamp = new Date().toISOString()
    console.log(
      `🚀 REPORTGENIE HOOK EFFECT TRIGGERED at ${timestamp} with taskId:`,
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
      console.log(
        "🔄 No taskId - resetting ReportGenie progress state to initial",
      )
      return
    }

    // Force immediate reset of all state to prevent cached completion
    console.log(
      "🔄 New ReportGenie task started, FORCE resetting ALL progress state for:",
      taskId,
    )
    setProgress({
      percentage: 0,
      message: t("common.progress.starting"),
      isActive: true,
      completed: false,
      error: undefined,
    })

    console.log(
      `🔄 Starting ReportGenie progress polling for task: ${taskId} at ${timestamp}`,
    )

    let intervalId: NodeJS.Timeout
    let isPolling = true
    let pollCount = 0

    const pollProgress = async () => {
      if (!isPolling) {
        console.log("🛑 POLLING STOPPED: isPolling is false for task:", taskId)
        return
      }

      pollCount++
      const timestamp = new Date().toISOString()
      console.log(
        `📡 REPORTGENIE POLL #${pollCount} at ${timestamp} for task:`,
        taskId,
      )

      try {
        console.log(
          "🔐 Making authenticated request to ReportGenie progress API for task:",
          taskId,
        )

        const data = await __request(OpenAPI, {
          method: "GET",
          url: `/api/v1/reportgenie/progress/${taskId}`,
        })

        // Enhanced debug logging
        console.log("📊 REPORTGENIE FRONTEND RECEIVED PROGRESS:", {
          percentage: (data as any).percentage,
          message: (data as any).message,
          message_key: (data as any).message_key,
          status: (data as any).status,
          current_stage: (data as any).current_stage,
          taskId: taskId,
          pollCount: pollCount,
        })

        // Determine the display message:
        // 1. If message_key exists, use it for translation
        // 2. Otherwise, fall back to the message field (for backwards compatibility)
        const displayMessage = (data as any).message_key
          ? t((data as any).message_key)
          : (data as any).message || "Processing..."

        const newProgress: ProgressData = {
          percentage: Math.round((data as any).percentage || 0),
          message: displayMessage,
          isActive:
            (data as any).status === "in_progress" ||
            (data as any).status === "started",
          completed: (data as any).status === "completed",
          error:
            (data as any).status === "failed"
              ? (data as any).error_message || (data as any).message
              : undefined,
        }

        console.log("📊 REPORTGENIE FRONTEND SETTING PROGRESS STATE:", {
          ...newProgress,
          willStopPolling:
            (data as any).status === "completed" ||
            (data as any).status === "failed",
          currentPollCount: pollCount,
        })

        setProgress(newProgress)

        // Stop polling if the task is completed or failed
        if (
          (data as any).status === "completed" ||
          (data as any).status === "failed"
        ) {
          console.log(
            `🏁 REPORTGENIE TASK ${(data as any).status.toUpperCase()}. Stopping polling at poll #${pollCount}`,
          )
          isPolling = false
          clearInterval(intervalId)
        }
      } catch (error) {
        console.error("❌ Error polling ReportGenie progress:", error)
        // Don't stop polling on error - the task might still be running
        // Only log the error and continue polling
        console.warn(`⚠️ REPORTGENIE POLL ERROR at #${pollCount}, will retry...`)
      }
    }

    // Start polling immediately, then every 1 second
    pollProgress()
    intervalId = setInterval(pollProgress, 1000)

    console.log("⏱️ REPORTGENIE POLLING INTERVAL STARTED for task:", taskId)

    // Cleanup function
    return () => {
      console.log(
        `🧹 REPORTGENIE CLEANUP: Stopping polling for task ${taskId} after ${pollCount} polls`,
      )
      isPolling = false
      clearInterval(intervalId)
    }
  }, [taskId])

  return progress
}
