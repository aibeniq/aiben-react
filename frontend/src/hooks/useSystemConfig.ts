import { useQuery } from "@tanstack/react-query"

export interface SystemConfig {
  enable_model_selection: boolean
  force_default_llm?: string
  force_default_embedding?: string
}

export const useSystemConfig = () => {
  return useQuery<SystemConfig>({
    queryKey: ["systemConfig"],
    queryFn: async () => {
      console.log("🔍 useSystemConfig: Making API call to backend")
      // For development, use the direct backend port since we know it works
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:8000/api/v1/utils/system-config"
        : "/api/v1/utils/system-config"

      console.log("🔍 useSystemConfig: API URL:", apiUrl)
      const response = await fetch(apiUrl)
      if (!response.ok) {
        console.error(
          "🔍 useSystemConfig: API call failed with status:",
          response.status,
        )
        throw new Error(`Failed to fetch system config: ${response.status}`)
      }
      const data = await response.json()
      console.log("🔍 useSystemConfig: API response:", data)
      console.log(
        "🔍 useSystemConfig: enable_model_selection =",
        data.enable_model_selection,
      )
      return data
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    retry: 3,
    // Default to showing model selection while loading to prevent layout shifts
    placeholderData: { enable_model_selection: true } as SystemConfig,
  })
}
