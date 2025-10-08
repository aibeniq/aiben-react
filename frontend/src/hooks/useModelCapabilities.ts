import { LlmModelsService } from "@/client"

export interface ModelCapabilities {
  vision: boolean
  model_name?: string
}

const VISION_ENABLED_MODELS = [
  "gpt-4-vision-preview",
  "gpt-4o",
  "gpt-4o-mini",
  "claude-3-opus",
  "claude-3-sonnet",
  "claude-3-haiku",
  "claude-3-5-sonnet",
]

export function checkModelVisionCapability(modelName: string): boolean {
  if (!modelName) return false

  return VISION_ENABLED_MODELS.some((visionModel) =>
    modelName.toLowerCase().includes(visionModel.toLowerCase()),
  )
}

export function useModelCapabilities() {
  const checkCapabilities = async (): Promise<ModelCapabilities> => {
    try {
      const response = await LlmModelsService.getDefaultLlmModel()
      const modelName = response.model_id || ""

      return {
        vision: checkModelVisionCapability(modelName),
        model_name: modelName,
      }
    } catch (error) {
      console.error("Error checking model capabilities:", error)
      return {
        vision: false,
      }
    }
  }

  return { checkCapabilities }
}
