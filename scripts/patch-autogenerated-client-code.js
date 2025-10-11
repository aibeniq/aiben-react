const fs = require("fs")
const path = require("path")

// --- Patch sdk.gen.ts ---
const sdkPath = path.join(__dirname, "../frontend/src/client/sdk.gen.ts")
let sdkContent = fs.readFileSync(sdkPath, "utf8")

// Define endpoints that need blob response
const blobEndpoints = [
  "/api/v1/reportgenie/generate/docx",
  "/api/v1/reportgenie/generate/csv", 
  "/api/v1/twincheck/generate/docx",
  "/api/v1/twincheck/generate/csv",
  "/api/v1/veradoc/generate/docx",
  "/api/v1/veradoc/generate/csv",
  "/api/v1/veradoc/optimization/csv",
  "/api/v1/reportgenie/optimize-outline/csv",
  "/api/v1/formconnect/generate/docx",
  "/api/v1/formconnect/generate/csv",
  "/api/v1/files/source/{source_id}/pdf",
  "/api/v1/files/source/by-filename/{filename}/pdf",
  "/api/v1/files/source/{source_id}/rtf-pdf",
  "/api/v1/files/source/by-filename/{filename}/rtf-pdf"
]// For each endpoint, find and patch it
blobEndpoints.forEach(endpoint => {
  const escapedEndpoint = endpoint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  
  // Find the function containing this URL and add responseType if not present
  // Pattern 1: Standard pattern with body parameter
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
  
  // Pattern 2: Alternative pattern with simple body reference
  const pattern2 = new RegExp(
    `(url: "${escapedEndpoint}",\\s*\\n\\s*body: data\\.requestBody,\\s*\\n\\s*mediaType: "application/json",\\s*\\n)(\\s*)(errors: \\{)`,
    'g'
  )
  
  sdkContent = sdkContent.replace(pattern2, (match, beforeErrors, whitespace, errorsStart) => {
    if (match.includes("responseType:")) {
      return match // Already patched
    }
    return beforeErrors + whitespace + "responseType: 'blob',\n" + whitespace + errorsStart
  })
  
  // Also try pattern with double quotes for URL
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
const apiRequestOptionsPath = path.join(__dirname, "../frontend/src/client/core/ApiRequestOptions.ts")
let apiRequestOptionsContent = fs.readFileSync(apiRequestOptionsPath, "utf8")

if (!apiRequestOptionsContent.includes('readonly responseType?:')) {
  apiRequestOptionsContent = apiRequestOptionsContent.replace(
    /(readonly responseHeader\?: string;)/,
    '$1\n\treadonly responseType?: "json" | "blob" | "text" | "arraybuffer";',
  )
}

fs.writeFileSync(apiRequestOptionsPath, apiRequestOptionsContent)

// --- Patch request.ts ---
const requestPath = path.join(__dirname, "../frontend/src/client/core/request.ts")
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