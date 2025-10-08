import { VeradocService } from "@/client"
import { OpenAPI } from "@/client/core/OpenAPI"
import { useEffect, useRef, useState } from "react"

export interface ProgressData {
  percentage: number
  message: string
  isActive: boolean
  completed: boolean
  error: string | undefined
  willStopPolling: boolean
  currentPollCount: number
  results: any | undefined
}

export const useVeradocProgress = (taskId: string | null) => {
  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    message: "",
    isActive: false,
    completed: false,
    error: undefined,
    willStopPolling: false,
    currentPollCount: 0,
    results: undefined,
  })

  const pollCountRef = useRef(0)
  const intervalIdRef = useRef<number | null>(null)
  const isActiveRef = useRef(false)
  const currentTaskIdRef = useRef<string | null>(null)
  const isPollingRef = useRef(false)
  const consecutiveErrorCountRef = useRef(0)

  const MAX_POLLS = 3600
  const MAX_TRANSIENT_ERRORS = 15 // Increased from 5 to allow more resilience to CORS issues

  useEffect(() => {
    if (!taskId) {
      setProgress({
        percentage: 0,
        message: "",
        isActive: false,
        completed: false,
        error: undefined,
        willStopPolling: false,
        currentPollCount: 0,
        results: undefined,
      })
      return
    }

    const isNewTask = currentTaskIdRef.current !== taskId

    if (isNewTask) {
      setProgress((prev) => ({
        ...prev,
        percentage: 0,
        message: "",
        isActive: true,
        completed: false,
        error: undefined,
        willStopPolling: false,
        currentPollCount: 0,
        results: undefined,
      }))

      if (intervalIdRef.current) {
        window.clearInterval(intervalIdRef.current)
        intervalIdRef.current = null
      }

      currentTaskIdRef.current = taskId
    }

    if (!isNewTask && isActiveRef.current && intervalIdRef.current) {
      return
    }

    isActiveRef.current = true
    consecutiveErrorCountRef.current = 0

    let consecutiveErrorCount = 0

    const processProgressResponse = async (
      response: any,
    ): Promise<string | undefined> => {
      if (!isActiveRef.current) return
      pollCountRef.current += 1

      const newProgress: ProgressData = {
        percentage: response?.percentage || 0,
        message: response?.message || "",
        isActive: response?.status === "in_progress",
        completed: response?.status === "completed",
        error: response?.error,
        willStopPolling: pollCountRef.current >= MAX_POLLS - 10,
        currentPollCount: pollCountRef.current,
        results: undefined,
      }

      setProgress(newProgress)

      if (response?.status === "completed") {
        try {
          let attempt = 0
          const maxAttempts = 5
          while (attempt < maxAttempts) {
            try {
              const results = await VeradocService.getVeradocResults({ taskId })
              setProgress((prev) => ({ ...prev, results }))
              break
            } catch (err) {
              try {
                const fallbackUrl = `${OpenAPI.BASE}/api/v1/veradoc/results/${taskId}`
                const fr = await fetch(fallbackUrl, {
                  credentials: "same-origin",
                })
                if (fr.ok) {
                  const json = await fr.json()
                  setProgress((prev) => ({ ...prev, results: json }))
                  break
                }
              } catch (ferr) {
                // ignore
              }

              attempt += 1
              const waitMs = Math.min(2000 * 2 ** attempt, 15000)
              await new Promise((r) => setTimeout(r, waitMs))
            }
          }
        } catch (err) {
          setProgress((prev) => ({ ...prev, error: "Failed to fetch results" }))
        }
      }

      return response?.status
    }

    const pollProgress = async () => {
      if (!isActiveRef.current) return
      if (isPollingRef.current) return
      isPollingRef.current = true

      try {
        let status: string | undefined

        try {
          const response = await VeradocService.getVeradocProgress({ taskId })
          status = await processProgressResponse(response)
          consecutiveErrorCount = 0

          // Reset to normal polling interval on success
          consecutiveErrorCountRef.current = 0
          if (intervalIdRef.current) {
            window.clearInterval(intervalIdRef.current)
            intervalIdRef.current = window.setInterval(pollProgress, 1000)
          }
        } catch (primaryErr) {
          try {
            // Use the configured API base URL for fallback instead of window.location.origin
            const fallbackUrl = `${OpenAPI.BASE}/api/v1/veradoc/progress/${taskId}`
            const fr = await fetch(fallbackUrl, { credentials: "same-origin" })
            if (fr.ok) {
              const json = await fr.json()
              status = await processProgressResponse(json)
              consecutiveErrorCount = 0

              // Reset to normal polling interval on success
              consecutiveErrorCountRef.current = 0
              if (intervalIdRef.current) {
                window.clearInterval(intervalIdRef.current)
                intervalIdRef.current = window.setInterval(pollProgress, 1000)
              }
            } else {
              consecutiveErrorCount += 1
            }
          } catch (ferr) {
            consecutiveErrorCount += 1
          }

          if (consecutiveErrorCount >= MAX_TRANSIENT_ERRORS) {
            setProgress((prev) => ({
              ...prev,
              error: "Network/CORS error contacting progress endpoint",
              isActive: false,
            }))
            isActiveRef.current = false
            if (intervalIdRef.current) {
              window.clearInterval(intervalIdRef.current)
              intervalIdRef.current = null
            }
            return
          }

          // Store the consecutive error count for dynamic interval calculation
          consecutiveErrorCountRef.current = consecutiveErrorCount

          // Adjust polling interval based on error count - slow down when errors occur
          const currentInterval = intervalIdRef.current
          if (currentInterval) {
            window.clearInterval(currentInterval)
            intervalIdRef.current = null
          }

          // Exponential backoff: base 1000ms, double for each consecutive error, max 30000ms
          const newInterval = Math.min(1000 * Math.pow(2, consecutiveErrorCount), 30000)
          intervalIdRef.current = window.setInterval(pollProgress, newInterval)
        }

        if (
          status === "completed" ||
          status === "error" ||
          pollCountRef.current >= MAX_POLLS
        ) {
          isActiveRef.current = false
          if (intervalIdRef.current) {
            window.clearInterval(intervalIdRef.current)
            intervalIdRef.current = null
          }
        }
      } catch (error) {
        setProgress((prev) => ({
          ...prev,
          error:
            error instanceof Error ? error.message : "Failed to fetch progress",
        }))
      } finally {
        isPollingRef.current = false
      }
    }

    intervalIdRef.current = window.setInterval(pollProgress, 1000)

    const initTimer = window.setTimeout(() => {
      if (isActiveRef.current) pollProgress()
    }, 500)

    return () => {
      isActiveRef.current = false
      if (intervalIdRef.current) {
        window.clearInterval(intervalIdRef.current)
        intervalIdRef.current = null
      }
      window.clearTimeout(initTimer)
    }
  }, [taskId])

  return progress
}
