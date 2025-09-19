import { useEffect, useState } from "react"
import { OpenAPI } from "@/client/core/OpenAPI"

interface ProgressData {
    percentage: number
    message: string
    isActive: boolean
    completed?: boolean
    error?: string
}

export const useKnowledgeBaseProgress = (taskId: string | null) => {
    const [progress, setProgress] = useState<ProgressData>({
        percentage: 0,
        message: "",
        isActive: false
    })

    useEffect(() => {
        if (!taskId) {
            return
        }

        console.log("🔄 Starting progress polling for task:", taskId)

        let intervalId: NodeJS.Timeout
        let isPolling = true

        const pollProgress = async () => {
            if (!isPolling) return

            try {
                const token = localStorage.getItem("access_token")
                const response = await fetch(
                    `${OpenAPI.BASE}/api/v1/knowledge-bases/progress/${taskId}`,
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                )

                if (!response.ok) {
                    console.warn("Progress endpoint returned error:", response.status)
                    return
                }

                const data = await response.json()
                console.log("📊 Progress update:", data)

                const newProgress: ProgressData = {
                    percentage: Math.round(data.percentage || 0),
                    message: data.message || "Processing...",
                    isActive: data.status === "in_progress" || data.status === "started",
                    completed: data.status === "completed",
                    error: data.status === "failed" ? (data.error_message || data.message) : undefined
                }

                setProgress(newProgress)

                // Stop polling if completed or errored
                if (data.status === "completed" || data.status === "failed") {
                    console.log("✅ Progress polling completed:", data.status === "completed" ? "success" : "error")
                    isPolling = false
                    clearInterval(intervalId)
                }

            } catch (error) {
                console.error("❌ Error polling progress:", error)
                // Continue polling on network errors in case it's temporary
            }
        }

        // Start polling immediately, then every 2 seconds
        pollProgress()
        intervalId = setInterval(pollProgress, 2000)

        // Cleanup function
        return () => {
            console.log("🛑 Stopping progress polling for task:", taskId)
            isPolling = false
            clearInterval(intervalId)
        }
    }, [taskId])

    return progress
}