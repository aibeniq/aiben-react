import axios from "axios"
import "./axiosGlobalConfig" // Ensure global timeout configuration is applied
import { OpenAPI } from "./core/OpenAPI"
import type { KnowledgeBasesCreateKnowledgeBaseData } from "./types.gen"

// Temporary interface for the new response format until types are regenerated
interface KnowledgeBaseCreateResponse {
  knowledge_base: any
  task_id: string
}

// Extended interface that includes timeout option and task_id
interface KnowledgeBasesCreateKnowledgeBaseDataWithTimeout
  extends KnowledgeBasesCreateKnowledgeBaseData {
  timeout?: number // Optional timeout in milliseconds
  taskId?: string // Optional task_id for existing progress tracking
}

// Override global axios defaults to prevent interference (reasonable timeout)
axios.defaults.timeout = 5 * 60 * 1000 // 5 minutes globally (async processing should return immediately)

// Create a custom axios client for knowledge base operations with appropriate timeout
export const knowledgeBaseAxiosClient = axios.create({
  timeout: 5 * 60 * 1000, // 5 minutes for initial request (should return immediately with task_id)
  // Explicitly override any global defaults
  maxContentLength: Number.POSITIVE_INFINITY,
  maxBodyLength: Number.POSITIVE_INFINITY,
})

// Add request interceptor to include auth headers
knowledgeBaseAxiosClient.interceptors.request.use(async (config) => {
  // Copy relevant config from the main OpenAPI client
  config.baseURL = OpenAPI.BASE
  config.withCredentials = OpenAPI.WITH_CREDENTIALS

  // DON'T override timeout if it's already set - preserve the dynamic timeout!
  if (!config.timeout) {
    config.timeout = 5 * 60 * 1000 // Only set default if not already set
  }

  // Get token directly from localStorage (same way the main client does)
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  console.log(
    "🕐 Request interceptor: Set timeout to",
    config.timeout / 1000 / 60,
    "minutes",
  )

  return config
})

// Add response interceptor for error handling
knowledgeBaseAxiosClient.interceptors.response.use(
  (response) => {
    console.log("✅ Response received successfully")
    return response
  },
  (error) => {
    // Enhanced timeout error logging
    if (error.code === "ECONNABORTED") {
      console.error("❌ Request was aborted (likely timeout)")
      console.error("⏰ Error after:", error.config?.timeout || "unknown", "ms")
    } else if (error.message?.includes("timeout")) {
      console.error("❌ Timeout error:", error.message)
    } else if (error.message?.includes("Network Error")) {
      console.error("❌ Network error:", error.message)
    }

    return Promise.reject(error)
  },
)

/**
 * Extended timeout version of createKnowledgeBase for handling large uploads
 */
export const createKnowledgeBaseWithTimeout = async (
  data: KnowledgeBasesCreateKnowledgeBaseDataWithTimeout,
): Promise<KnowledgeBaseCreateResponse> => {
  try {
    console.log("🚀 Starting knowledge base upload with timeout client")
    console.log("📊 Files to upload:", data.formData?.files?.length || 0)

    // Extract timeout from data, default to 1 hour for large uploads
    const requestTimeout = data.timeout || 60 * 60 * 1000 // 1 hour default
    console.log("⏰ Using timeout:", requestTimeout / 1000 / 60, "minutes")

    const formData = new FormData()

    // Add files to form data
    if (data.formData?.files) {
      for (const file of data.formData.files) {
        formData.append("files", file)
        const fileName = file instanceof File ? file.name : "blob"
        const fileSize = (file.size / 1024 / 1024).toFixed(2)
        console.log(`📁 Added file: ${fileName} (${fileSize}MB)`)
      }
    }

    // Add metadata to form data
    formData.append("title", data.title || "")
    formData.append("description", data.description || "")
    if (data.embeddingModelId) {
      formData.append("embedding_model_id", data.embeddingModelId)
    }

    // Log the exact timeout being used
    console.log(
      "🔧 Using dynamic timeout:",
      requestTimeout / 1000 / 60,
      "minutes",
    )

    // Make the request with our custom axios client
    const requestStartTime = Date.now()
    console.log("🌐 MAKING HTTP REQUEST to /api/v1/knowledge-bases/ with task_id:", data.taskId)

    const response = await knowledgeBaseAxiosClient.post(
      "/api/v1/knowledge-bases/",
      formData,
      {
        params: {
          task_id: data.taskId, // Only task_id as query parameter
        },
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: requestTimeout, // Use the dynamic timeout
        maxContentLength: Number.POSITIVE_INFINITY,
        maxBodyLength: Number.POSITIVE_INFINITY,
      },
    )

    const requestDuration = Date.now() - requestStartTime
    console.log("✅ HTTP REQUEST COMPLETED in", requestDuration, "ms")

    console.log("✅ Knowledge base upload completed successfully")
    return response.data
  } catch (error: any) {
    console.error("❌ Knowledge base creation error:", error)

    // Enhanced error logging for debugging
    if (error.code === "ECONNABORTED") {
      console.error("🕐 Request timed out")
      console.error(
        "⏱️  Timeout was set to:",
        error.config?.timeout || "unknown",
        "ms",
      )
      console.error(
        "⏱️  That's",
        (error.config?.timeout || 0) / 1000 / 60,
        "minutes",
      )
    } else if (error.message?.includes("timeout")) {
      console.error("🕐 Timeout error:", error.message)
    } else if (error.message?.includes("Network Error")) {
      console.error("🌐 Network error:", error.message)
    } else {
      console.error("🔍 Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        code: error.code,
      })
    }

    throw error
  }
}
