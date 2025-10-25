import { defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  client: "legacy/axios",
  input: "./openapi.json",
  output: "./src/client",
  // exportSchemas: true,
  plugins: [
    {
      name: "@hey-api/sdk",
      // NOTE: this doesn't allow tree-shaking
      asClass: true,
      operationId: true,
      methodNameBuilder: (operation) => {
        // @ts-ignore
        const summary: string = operation.summary || ''
        // @ts-ignore
        const operationId: string = operation.operationId || operation.name || ''

        if (summary) {
          // Convert summary to camelCase
          // Examples:
          // "Get Token Usage" -> "getTokenUsage"
          // "Read User Me" -> "readUserMe"
          // "Recover Password" -> "recoverPassword"
          // "Get Available Providers" -> "getAvailableProviders"

          const words = summary.toLowerCase().split(/\s+/)
          if (words.length > 0) {
            let methodName = words[0]
            for (let i = 1; i < words.length; i++) {
              const word = words[i]
              if (word) {
                methodName += word.charAt(0).toUpperCase() + word.slice(1)
              }
            }
            return methodName
          }
        }

        // Fallback to operationId parsing if summary is not available
        if (operationId) {
          // Simple fallback: remove common suffixes and convert to camelCase
          let cleanId = operationId
            .replace(/_api_v1_.*$/, '') // Remove _api_v1_... suffix
            .replace(/^get_/, '') // Remove get_ prefix
            .replace(/^post_/, '') // Remove post_ prefix
            .replace(/^put_/, '') // Remove put_ prefix
            .replace(/^delete_/, '') // Remove delete_ prefix
            .replace(/^patch_/, '') // Remove patch_ prefix

          const parts = cleanId.split('_')
          if (parts.length > 0) {
            let methodName = parts[0]
            for (let i = 1; i < parts.length; i++) {
              const part = parts[i]
              if (part) {
                methodName += part.charAt(0).toUpperCase() + part.slice(1)
              }
            }
            return methodName
          }
        }

        return 'unknownMethod'
      },
    },
  ],
})
