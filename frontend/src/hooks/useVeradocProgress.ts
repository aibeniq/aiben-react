import { useEffect, useState, useRef } from "react"
import { VeradocService } from "@/client"

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

    const MAX_POLLS = 3600
    const MAX_TRANSIENT_ERRORS = 5

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
            setProgress(prev => ({
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
        pollCountRef.current = 0

        let consecutiveErrorCount = 0

        const processProgressResponse = async (response: any): Promise<string | undefined> => {
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
                            setProgress(prev => ({ ...prev, results }))
                            break
                        } catch (err) {
                            try {
                                const fallbackUrl = `${window.location.origin}/api/v1/veradoc/results/${taskId}`
                                const fr = await fetch(fallbackUrl, { credentials: 'same-origin' })
                                if (fr.ok) {
                                    const json = await fr.json()
                                    setProgress(prev => ({ ...prev, results: json }))
                                    break
                                }
                            } catch (ferr) {
                                // ignore
                            }

                            attempt += 1
                            const waitMs = Math.min(2000 * Math.pow(2, attempt), 15000)
                            await new Promise(r => setTimeout(r, waitMs))
                        }
                    }
                } catch (err) {
                    setProgress(prev => ({ ...prev, error: 'Failed to fetch results' }))
                }
            }

            return response?.status
        }

        const pollProgress = async () => {
            if (!isActiveRef.current) return

            try {
                let status: string | undefined

                try {
                    const response = await VeradocService.getVeradocProgress({ taskId })
                    status = await processProgressResponse(response)
                    consecutiveErrorCount = 0
                } catch (primaryErr) {
                    try {
                        const fallbackUrl = `${window.location.origin}/api/v1/veradoc/progress/${taskId}`
                        const fr = await fetch(fallbackUrl, { credentials: 'same-origin' })
                        if (fr.ok) {
                            const json = await fr.json()
                            status = await processProgressResponse(json)
                            consecutiveErrorCount = 0
                        } else {
                            consecutiveErrorCount += 1
                        }
                    } catch (ferr) {
                        consecutiveErrorCount += 1
                    }

                    if (consecutiveErrorCount >= MAX_TRANSIENT_ERRORS) {
                        setProgress(prev => ({ ...prev, error: 'Network/CORS error contacting progress endpoint', isActive: false }))
                        isActiveRef.current = false
                        if (intervalIdRef.current) {
                            window.clearInterval(intervalIdRef.current)
                            intervalIdRef.current = null
                        }
                        return
                    }
                }

                if (status === 'completed' || status === 'error' || pollCountRef.current >= MAX_POLLS) {
                    isActiveRef.current = false
                    if (intervalIdRef.current) {
                        window.clearInterval(intervalIdRef.current)
                        intervalIdRef.current = null
                    }
                }
            } catch (error) {
                setProgress(prev => ({ ...prev, error: error instanceof Error ? error.message : 'Failed to fetch progress' }))
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
