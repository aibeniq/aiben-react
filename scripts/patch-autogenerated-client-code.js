const fs = require("fs")

// --- Patch sdk.gen.ts ---
const sdkPath = "./src/client/sdk.gen.ts"
let sdkContent = fs.readFileSync(sdkPath, "utf8")

// Patch for ReportGenie
sdkContent = sdkContent.replace(
  /(url: "\/api\/v1\/reportgenie\/generate\/docx",[\s\S]*?body: data\.requestBody,)/,
  '$1\n      responseType: "blob",',
)

// Patch for TwinCheck
sdkContent = sdkContent.replace(
  /(url: "\/api\/v1\/twincheck\/generate\/docx",[\s\S]*?body: data\.requestBody,)/,
  '$1\n      responseType: "blob",',
)

// Patch for VeraDoc
sdkContent = sdkContent.replace(
  /(url: "\/api\/v1\/veradoc\/generate\/docx",[\s\S]*?body: data\.requestBody,)/,
  '$1\n      responseType: "blob",',
)

fs.writeFileSync(sdkPath, sdkContent)

// --- Patch ApiRequestOptions.ts ---
const apiRequestOptionsPath = "./src/client/core/ApiRequestOptions.ts"
let apiRequestOptionsContent = fs.readFileSync(apiRequestOptionsPath, "utf8")

// Add the missing responseType field to ApiRequestOptions
apiRequestOptionsContent = apiRequestOptionsContent.replace(
  /(readonly responseHeader\?: string)/,
  '$1\n  readonly responseType?: "json" | "blob" | "text" | "arraybuffer"',
)

fs.writeFileSync(apiRequestOptionsPath, apiRequestOptionsContent)

// --- Patch request.ts ---
const requestPath = "./src/client/core/request.ts"
let requestContent = fs.readFileSync(requestPath, "utf8")

// Regex to find the start of the AxiosRequestConfig object
requestContent = requestContent.replace(
  /(let requestConfig: AxiosRequestConfig = \{\n)([\s\S]*?)(headers,)/,
  (match, p1, p2, p3) => {
    // Insert responseType after data/body/formData and before headers
    return `${p1}${p2}responseType: options.responseType || "json",\n  ${p3}`
  },
)

fs.writeFileSync(requestPath, requestContent)
