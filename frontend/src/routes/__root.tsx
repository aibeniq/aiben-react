import { Outlet, createRootRoute } from "@tanstack/react-router"
import React, { Suspense } from "react"

import NotFound from "@/components/Common/NotFound"

const loadDevtools = () =>
  Promise.all([import("@tanstack/router-devtools"), import("@tanstack/react-query-devtools")]).then(
    ([routerDevtools, _]) => {
      return {
        default: () => (
          <>
            <routerDevtools.TanStackRouterDevtools />
            {/* <reactQueryDevtools.ReactQueryDevtools /> */}
          </>
        ),
      }
    },
  )

//const TanStackDevtools =
//  process.env.NODE_ENV === "production" || import.meta.env.VITE_DISABLE_DEVTOOLS === "true"
//    ? () => null
//    : React.lazy(loadDevtools)

//tried hiding the TanStack icon with a flag but it didn't take somehow due to .env issue... just disabling for now
const TanStackDevtools = () => null

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <Suspense>
        <TanStackDevtools />
      </Suspense>
    </>
  ),
  notFoundComponent: () => <NotFound />,
})
