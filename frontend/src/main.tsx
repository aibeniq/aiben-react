import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { RouterProvider, createRouter } from "@tanstack/react-router"
import React, { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { routeTree } from "./routeTree.gen"

import { ApiError, OpenAPI } from "./client"
import { API_BASE_URL } from "./config/api"
import { CustomProvider } from "./components/ui/provider"
import { ResultsProvider } from "./contexts/ResultsContext"

console.log("API URL:", API_BASE_URL)

OpenAPI.BASE = API_BASE_URL
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
        <RouterProvider router={router} />
      </ResultsProvider>
    </QueryClientProvider>
  </CustomProvider>,
)
