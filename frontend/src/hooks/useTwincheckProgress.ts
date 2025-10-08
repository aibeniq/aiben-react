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

export const useTwincheckProgress = (taskId: string | null) => {
    console.warn("🔄 TWINCHECK PROGRESS HOOK CALLED:", new Date().toISOString(), "taskId:", taskId)

    const [progress, setProgress] = useState<ProgressData>({
        percentage: 0,
        message: "",
        isActive: false,
        completed: false,
        error: undefined,
    })

    useEffect(() => {
        if (!taskId) {
            setProgress({ percentage: 0, message: "", isActive: false, completed: false, error: undefined })
            return
        }

        setProgress({ percentage: 0, message: "Starting...", isActive: true, completed: false, error: undefined })

        let intervalId: NodeJS.Timeout
        let isPolling = true
        let pollCount = 0

        const pollProgress = async () => {
            if (!isPolling) return
            pollCount += 1

            try {
                // Poll Twincheck-specific progress endpoint only
                const data: any = await __request(OpenAPI, {
                    method: 'GET',
                    url: `/api/v1/twincheck/progress/${taskId}`,
                })

                const newProgress: ProgressData = {
                    percentage: Math.round((data as any).percentage || 0),
                    message: (data as any).message || "Processing...",
                    isActive: (data as any).status === "in_progress" || (data as any).status === "started",
                    completed: (data as any).status === "completed",
                    error: (data as any).status === "failed" ? ((data as any).error_message || (data as any).message) : undefined,
                }

                setProgress(newProgress)

                if ((data as any).status === "completed" || (data as any).status === "failed") {
                    isPolling = false
                    clearInterval(intervalId)
                }
            } catch (error) {
                console.warn("❌ Error polling TwinCheck/ReportGenie progress:", error)
                // continue polling - tolerate transient errors
            }
        }

        pollProgress()
        intervalId = setInterval(pollProgress, 1000)

        return () => {
            isPolling = false
            clearInterval(intervalId)
        }
    }, [taskId])

    return progress
}
