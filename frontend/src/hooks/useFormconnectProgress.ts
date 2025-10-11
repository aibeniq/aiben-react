import { OpenAPI } from "@/client/core/OpenAPI"
import { request as __request } from "@/client/core/request"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

interface ProgressData {
  status: "pending" | "in_progress" | "completed" | "failed"
  percentage: number
  message: string
  current_stage: string
  completed: boolean
  error?: string
  isActive: boolean
}

export function useFormconnectProgress(taskId: string | null) {
  const { t } = useTranslation()
  const [progress, setProgress] = useState<ProgressData>({
    status: "pending",
    percentage: 0,
    message: t("common.progress.initializing"),
    current_stage: "setup",
    completed: false,
    isActive: false,
  })

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const lastPercentageRef = useRef<number>(0)

  useEffect(() => {
    if (!taskId) {
      // Reset progress when taskId is cleared
      setProgress({
        status: "pending",
        percentage: 0,
        message: t("common.progress.initializing"),
        current_stage: "setup",
        completed: false,
        isActive: false,
      })
      return
    }

    console.log("🔄 Starting FormConnect progress polling for task:", taskId)

    const pollProgress = async () => {
      try {
        const data: any = await __request(OpenAPI, {
          method: "GET",
          url: `/api/v1/formconnect/progress/${taskId}`,
        })

        console.log("📊 FormConnect progress update:", data)

        // Determine the display message:
        // 1. If message_key exists, use it for translation
        // 2. Otherwise, fall back to the message field (for backwards compatibility)
        const displayMessage = data.message_key
          ? t(data.message_key)
          : data.message

        // Only update if percentage actually changed (prevents unnecessary re-renders)
        if (data.percentage !== lastPercentageRef.current) {
          lastPercentageRef.current = data.percentage
          setProgress({
            status: data.status,
            percentage: data.percentage,
            message: displayMessage,
            current_stage: data.current_stage,
            completed: data.status === "completed",
            isActive:
              data.status === "in_progress" || data.status === "started",
            error: data.error,
          })
        }

        // Stop polling if completed or failed
        if (data.status === "completed" || data.status === "failed") {
          console.log("✅ FormConnect task finished, stopping polling")
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      } catch (error) {
        console.error("Error polling FormConnect progress:", error)
        setProgress((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : "Unknown error",
        }))
      }
    }

    // Start polling immediately
    pollProgress()

    // Then poll every 500ms
    intervalRef.current = setInterval(pollProgress, 500)

    // Cleanup on unmount or taskId change
    return () => {
      if (intervalRef.current) {
        console.log("🛑 Stopping FormConnect progress polling")
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [taskId])

  return progress
}
