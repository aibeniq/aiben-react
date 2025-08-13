const fs = require("fs")

// --- Patch sdk.gen.ts ---
const sdkPath = "./frontend/src/client/sdk.gen.ts"
let sdkContent = fs.readFileSync(sdkPath, "utf8")

// Define endpoints that need blob response
const blobEndpoints = [
  "/api/v1/reportgenie/generate/docx",
  "/api/v1/reportgenie/generate/csv", 
  "/api/v1/twincheck/generate/docx",
  "/api/v1/veradoc/generate/docx",
  "/api/v1/veradoc/generate/csv",
  "/api/v1/veradoc/optimization/csv",
  "/api/v1/reportgenie/optimize-outline/csv"
]

// For each endpoint, find and patch it
blobEndpoints.forEach(endpoint => {
  const escapedEndpoint = endpoint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  
  // Find the function containing this URL and add responseType if not present
  const pattern = new RegExp(
    `(url: '${escapedEndpoint}',\\s*\\n\\s*body:[\\s\\S]*?mediaType: 'application/json',\\s*\\n)(\\s*)(errors: \\{)`,
    'g'
  )
  
  sdkContent = sdkContent.replace(pattern, (match, beforeErrors, whitespace, errorsStart) => {
    if (match.includes("responseType:")) {
      return match // Already patched
    }
    return beforeErrors + whitespace + "responseType: 'blob',\n" + whitespace + errorsStart
  })
  
  // Also try pattern with double quotes
  const patternDoubleQuotes = new RegExp(
    `(url: "${escapedEndpoint}",\\s*\\n\\s*body:[\\s\\S]*?mediaType: 'application/json',\\s*\\n)(\\s*)(errors: \\{)`,
    'g'
  )
  
  sdkContent = sdkContent.replace(patternDoubleQuotes, (match, beforeErrors, whitespace, errorsStart) => {
    if (match.includes("responseType:")) {
      return match // Already patched
    }
    return beforeErrors + whitespace + "responseType: 'blob',\n" + whitespace + errorsStart
  })
})

fs.writeFileSync(sdkPath, sdkContent)

// --- Patch ApiRequestOptions.ts ---
const apiRequestOptionsPath = "./frontend/src/client/core/ApiRequestOptions.ts"
let apiRequestOptionsContent = fs.readFileSync(apiRequestOptionsPath, "utf8")

if (!apiRequestOptionsContent.includes('readonly responseType?:')) {
  apiRequestOptionsContent = apiRequestOptionsContent.replace(
    /(readonly responseHeader\?: string;)/,
    '$1\n\treadonly responseType?: "json" | "blob" | "text" | "arraybuffer";',
  )
}

fs.writeFileSync(apiRequestOptionsPath, apiRequestOptionsContent)

// --- Patch request.ts ---
const requestPath = "./frontend/src/client/core/request.ts"
let requestContent = fs.readFileSync(requestPath, "utf8")

if (!requestContent.includes('responseType: options.responseType')) {
  requestContent = requestContent.replace(
    /(let requestConfig: AxiosRequestConfig = \{\n)([\s\S]*?)(headers,)/,
    (match, p1, p2, p3) => {
      return `${p1}${p2}responseType: options.responseType || "json",\n\t\t${p3}`
    },
  )
}

fs.writeFileSync(requestPath, requestContent)

console.log("✅ Successfully patched SDK files for blob responses")