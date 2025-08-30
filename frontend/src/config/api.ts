// Centralized API base URL configuration
// Priority:
// 1. Explicit env variable (runtime injected via placeholder replacement)
// 2. Production fallback to known public host
// 3. Development fallback to localhost

const PUBLIC_HOST = "https://redhat-api.aiben.io";

// Vite exposes variables on import.meta.env; during docker runtime we replace placeholder
const envUrl = (import.meta as any).env?.VITE_API_URL as string | undefined;

// Derive a safe default
let base = envUrl?.trim();
if (!base) {
  if (typeof window !== "undefined" && window.location.hostname.includes("redhat")) {
    base = PUBLIC_HOST; // running in deployed redhat domain but env missing
  } else {
    base = "http://localhost:8000"; // local dev
  }
}

// Normalize (strip trailing slash)
export const API_BASE_URL = base.replace(/\/$/, "");
