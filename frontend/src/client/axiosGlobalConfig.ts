import axios from "axios"

/**
 * Global axios configuration to prevent any 10-minute timeout issues
 * This file ensures ALL axios requests use 60-minute timeouts by default
 */

// Set global axios defaults to 60 minutes
axios.defaults.timeout = 60 * 60 * 1000 // 60 minutes globally
axios.defaults.maxContentLength = Infinity
axios.defaults.maxBodyLength = Infinity

console.log("✅ Global axios timeout set to 60 minutes")

// Add a global request interceptor to ensure ALL axios requests have 30-minute timeout
axios.interceptors.request.use(
    (config) => {
        // Force 30-minute timeout on ALL requests unless explicitly overridden
        if (!config.timeout || config.timeout < 60 * 60 * 1000) {
            config.timeout = 60 * 60 * 1000
            console.log("🔧 Global interceptor: Enhanced timeout to 60 minutes for:", config.url)
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Add a global response interceptor for enhanced error logging
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.code === "ECONNABORTED") {
            console.error("❌ Global timeout interceptor: Request aborted")
            console.error("⏰ Request URL:", error.config?.url)
            console.error("⏰ Timeout was:", error.config?.timeout, "ms")
            console.error("⏰ That's", (error.config?.timeout || 0) / 1000 / 60, "minutes")
        }
        return Promise.reject(error)
    }
)

export default axios