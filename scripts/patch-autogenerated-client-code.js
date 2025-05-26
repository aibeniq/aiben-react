const fs = require('fs');

// --- Patch sdk.gen.ts ---
const sdkPath = './src/client/sdk.gen.ts';
let sdkContent = fs.readFileSync(sdkPath, 'utf8');
sdkContent = sdkContent.replace(
  /(url: "\/api\/v1\/reportgenie\/generate\/docx",[\s\S]*?body: data\.requestBody,)/,
  '$1\n      responseType: \'blob\','
);
fs.writeFileSync(sdkPath, sdkContent);

// --- Patch request.ts ---
const requestPath = './src/client/core/request.ts';
let requestContent = fs.readFileSync(requestPath, 'utf8');

// Regex to find the start of the AxiosRequestConfig object
requestContent = requestContent.replace(
  /(let requestConfig: AxiosRequestConfig = \{\n)([\s\S]*?)(headers,)/,
  (match, p1, p2, p3) => {
    // Insert responseType after data/body/formData and before headers
    return `${p1}${p2}responseType: options.responseType || "json",\n  ${p3}`;
  }
);

fs.writeFileSync(requestPath, requestContent);