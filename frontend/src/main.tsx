import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { RouterProvider, createRouter } from "@tanstack/react-router"
import React, { StrictMode, Suspense } from "react"
import ReactDOM from "react-dom/client"
import { routeTree } from "./routeTree.gen"

// Import global axios configuration FIRST to ensure 30-minute timeouts
import "./client/axiosGlobalConfig"

import { ApiError, OpenAPI } from "./client"
import { CustomProvider } from "./components/ui/provider"
import { ResultsProvider } from "./contexts/ResultsContext"
import "./i18n" // Initialize i18n

const envApiUrl = import.meta.env.VITE_API_URL
console.log("API URL (env):", envApiUrl)

// If the env API URL points to a production host while the app is running on localhost
// or a different origin, prefer same-origin API base to avoid CORS blocking during local/dev testing.
let computedBase = envApiUrl || ""
try {
  if (typeof window !== "undefined" && envApiUrl) {
    const envUrl = new URL(envApiUrl)
    const envHost = envUrl.hostname
    const currentHost = window.location.hostname
    // If env points at production API but we're on localhost (or a different host), use same origin
    if (
      envHost !== currentHost &&
      (currentHost === "localhost" || currentHost === "127.0.0.1")
    ) {
      computedBase = window.location.origin
      console.log(
        `API URL override: running on ${currentHost}, overriding API base to ${computedBase}`,
      )
    }
  }
} catch (e) {
  console.warn("Could not parse VITE_API_URL, using as-is", e)
}

OpenAPI.BASE = computedBase
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    localStorage.removeItem("access_token")
    window.location.href = "/login"
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <CustomProvider>
    <QueryClientProvider client={queryClient}>
      <ResultsProvider>
        <Suspense fallback={<div>Loading translations...</div>}>
          <RouterProvider router={router} />
        </Suspense>
      </ResultsProvider>
    </QueryClientProvider>
  </CustomProvider>,
)
