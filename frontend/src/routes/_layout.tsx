import { Flex } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"
import { Suspense, useEffect } from "react"

import Navbar from "@/components/Common/Navbar"
import Sidebar from "@/components/Common/Sidebar"
import { UsersService } from "@/client"
import { addEmergencyEscapeHandlers } from "../utils/overlay-debugger"

import Chatbot from "@/components/Chatbot/ChatbotMain"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    // Check authentication by making an API call with HTTP-only cookies
    try {
      await UsersService.readUserMe()
      // If the call succeeds, user is authenticated
    } catch (error) {
      // If the call fails, redirect to login
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  // Simplified emergency handlers - only enable in development
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("🔧 Setting up development overlay debugging utilities")
      const cleanup = addEmergencyEscapeHandlers()

      console.log("📋 Development shortcuts available:")
      console.log("  Ctrl+Shift+F12: Emergency overlay cleanup")
      console.log("  Ctrl+Shift+F11: Debug overlay information")

      return cleanup
    }
  }, [])

  return (
    <Flex direction="column" h="100vh">
      <Navbar />
      <Flex flex="1" overflow="hidden">
        <Sidebar />
        <Flex
          flex="1"
          direction="column"
          p={4}
          overflowY="auto"
          // Ensure main content area has explicit pointer events
          style={{
            pointerEvents: "auto",
            isolation: "isolate",
          }}
        >
          <Suspense fallback={<div>Loading...</div>}>
            <Outlet />
          </Suspense>
          <Chatbot />
        </Flex>
      </Flex>
    </Flex>
  )
}

export default Layout
