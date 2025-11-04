/**
 * Temporary type augmentation for new User fields
 * This file extends the auto-generated UserPublic type until the OpenAPI schema is regenerated
 * TODO: Remove this file after regenerating the client SDK with backend running
 */

import { UserPublic as GeneratedUserPublic } from "./types.gen"

declare module "./types.gen" {
  export interface UserPublic extends GeneratedUserPublic {
    default_processing_mode: string
  }
}

declare module "./sdk.gen" {
  export namespace UsersService {
    export function updateProcessingDefaults(data: {
      requestBody: {
        default_processing_mode: string
        vision_analysis_enabled: boolean
        pdf_parsing_preference: string
      }
    }): Promise<any>
  }
}
