import { Box, Flex, IconButton, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { useState, useEffect } from "react"
import { FaBars } from "react-icons/fa"
import { FiLogOut } from "react-icons/fi"
import { useTranslation } from "react-i18next"

import type { UserPublic } from "@/client"
import useAuth from "@/hooks/useAuth"
import {
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
  DrawerTrigger,
} from "../ui/drawer"
import SidebarItems from "./SidebarItems"

const Sidebar = () => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const { logout } = useAuth()
  const [open, setOpen] = useState(false)
  const { t } = useTranslation()

  // Enhanced sidebar drawer management to prevent overlay conflicts
  useEffect(() => {
    const cleanupSidebarOverlays = () => {
      // More aggressive cleanup of sidebar-related overlays
      const allOverlays = document.querySelectorAll(
        '[data-scope="drawer"][data-part="backdrop"], [data-placement="start"] [data-scope="drawer"][data-part="backdrop"]',
      )

      allOverlays.forEach((overlay) => {
        const overlayEl = overlay as HTMLElement
        const drawerRoot = overlay.closest('[data-placement="start"]')

        // If this is a sidebar overlay and drawer is closed, force cleanup
        if (drawerRoot && !open) {
          overlayEl.style.display = "none !important"
          overlayEl.style.pointerEvents = "none !important"
          overlayEl.style.opacity = "0 !important"
          overlayEl.style.visibility = "hidden !important"

          console.log("🔧 Cleaned up sidebar overlay")
        }
      })

      // Also ensure sidebar trigger button remains responsive
      const sidebarTrigger = document.querySelector('[aria-label="Open Menu"]') as HTMLElement
      if (sidebarTrigger) {
        sidebarTrigger.style.pointerEvents = "auto !important"
        sidebarTrigger.style.zIndex = "1001 !important"
        sidebarTrigger.style.isolation = "isolate"
      }
    }

    // Clean up immediately when state changes
    cleanupSidebarOverlays()

    // Set up responsive breakpoint monitoring
    const handleResize = () => {
      const windowWidth = window.innerWidth
      const isDesktop = windowWidth >= 768 // md breakpoint

      console.log(
        `📏 Window resized to ${windowWidth}px, isDesktop: ${isDesktop}, sidebar open: ${open}`,
      )

      // Force close sidebar on desktop to prevent stuck states
      if (isDesktop && open) {
        console.log("🖥️ Desktop detected, closing sidebar drawer")
        handleSidebarToggle(false)
      }

      // Ensure button is responsive at all screen sizes
      setTimeout(() => {
        const sidebarTrigger = document.querySelector('[aria-label="Open Menu"]') as HTMLElement
        if (sidebarTrigger) {
          // Force button to be interactive, especially at half-size
          sidebarTrigger.style.pointerEvents = "auto"
          sidebarTrigger.style.zIndex = "1001"
          sidebarTrigger.style.isolation = "isolate"
          sidebarTrigger.style.cursor = "pointer"

          console.log(`🔧 Ensured sidebar button is responsive at ${windowWidth}px`)
        }
      }, 50)

      // Clean up any lingering overlays after resize
      setTimeout(cleanupSidebarOverlays, 100)
    }

    window.addEventListener("resize", handleResize)

    // Set up periodic cleanup to prevent accumulation of stuck overlays
    const cleanupInterval = setInterval(cleanupSidebarOverlays, 2000)

    return () => {
      window.removeEventListener("resize", handleResize)
      clearInterval(cleanupInterval)
    }
  }, [open])

  // Emergency cleanup when component unmounts
  useEffect(() => {
    return () => {
      console.log("🚨 Sidebar unmounting - emergency overlay cleanup")
      const allSidebarOverlays = document.querySelectorAll(
        '[data-placement="start"] [data-scope="drawer"][data-part="backdrop"]',
      )

      allSidebarOverlays.forEach((overlay) => {
        const overlayEl = overlay as HTMLElement
        overlayEl.style.display = "none !important"
        overlayEl.style.pointerEvents = "none !important"
      })
    }
  }, [])

  const handleSidebarToggle = (isOpen: boolean) => {
    console.log("🔄 Sidebar state changing:", {
      from: open,
      to: isOpen,
      windowWidth: window.innerWidth,
    })

    if (!isOpen) {
      // When closing, immediately clean up overlays
      setTimeout(() => {
        const sidebarOverlays = document.querySelectorAll(
          '[data-placement="start"] [data-scope="drawer"][data-part="backdrop"]',
        )

        sidebarOverlays.forEach((overlay) => {
          const overlayEl = overlay as HTMLElement
          overlayEl.style.display = "none !important"
          overlayEl.style.pointerEvents = "none !important"
          console.log("🔧 Force cleaned sidebar overlay on close")
        })
      }, 10)
    }

    setOpen(isOpen)
  }

  return (
    <>
      {/* Mobile */}
      <DrawerRoot placement="start" open={open} onOpenChange={(e) => handleSidebarToggle(e.open)}>
        <DrawerBackdrop
          onClick={() => {
            console.log("🎯 Sidebar backdrop clicked - force closing")
            handleSidebarToggle(false)
          }}
          style={{
            zIndex: 999, // Lower than chat overlay
            pointerEvents: "auto",
          }}
        />
        <DrawerTrigger asChild>
          <IconButton
            variant="ghost"
            color="inherit"
            display={{ base: "flex", md: "none" }}
            aria-label="Open Menu"
            position="absolute"
            zIndex="1001" // Higher than backdrop
            m={4}
            onClick={(e) => {
              e.stopPropagation()
              console.log(
                "🎯 Sidebar menu button clicked, current state:",
                open,
                "window width:",
                window.innerWidth,
              )

              // Emergency cleanup before state change
              const problematicOverlays = document.querySelectorAll(
                '[data-scope="drawer"][data-part="backdrop"]',
              )
              problematicOverlays.forEach((overlay) => {
                const overlayEl = overlay as HTMLElement
                const isFromChat = overlay.closest('[data-placement="end"]')
                if (!isFromChat) {
                  // Only clean non-chat overlays
                  overlayEl.style.display = "none"
                  overlayEl.style.pointerEvents = "none"
                }
              })

              // Manually toggle the drawer state since we're using asChild
              const newState = !open
              console.log(`🔄 Manually toggling sidebar: ${open} → ${newState}`)
              handleSidebarToggle(newState)

              // Fallback: Force trigger after short delay if state didn't change
              setTimeout(() => {
                if (open === !newState) {
                  console.log("🚨 Sidebar state didn't change, forcing update")
                  setOpen(newState)
                }
              }, 100)
            }}
            style={{
              pointerEvents: "auto",
              zIndex: 1001,
              isolation: "isolate",
            }}
          >
            <FaBars />
          </IconButton>
        </DrawerTrigger>
        <DrawerContent
          maxW="xs"
          style={{
            zIndex: 1000, // Lower than chat but higher than backdrop
            pointerEvents: "auto",
          }}
        >
          <DrawerCloseTrigger
            onClick={() => {
              console.log("🔒 Sidebar close button clicked")
              handleSidebarToggle(false)
            }}
          />
          <DrawerBody>
            <Flex flexDir="column" justify="space-between">
              <Box>
                <SidebarItems onClose={() => handleSidebarToggle(false)} />
                <Flex
                  as="button"
                  onClick={() => {
                    logout()
                  }}
                  alignItems="center"
                  gap={4}
                  px={4}
                  py={2}
                >
                  <FiLogOut />
                  <Text>{t("navigation.logout")}</Text>
                </Flex>
              </Box>
              {currentUser?.email && (
                <Text fontSize="sm" p={2} truncate maxW="sm">
                  {t("navigation.loggedInAs", { email: currentUser.email })}
                </Text>
              )}
            </Flex>
          </DrawerBody>
          <DrawerCloseTrigger
            onClick={() => {
              console.log("🔒 Sidebar bottom close button clicked")
              handleSidebarToggle(false)
            }}
          />
        </DrawerContent>
      </DrawerRoot>

      {/* Desktop */}

      <Box
        display={{ base: "none", md: "flex" }}
        position="sticky"
        bg="bg.subtle"
        top={0}
        minW="xs"
        h="100vh"
        p={4}
        style={{
          pointerEvents: "auto",
          isolation: "isolate",
          zIndex: 1, // Lower than any overlays
        }}
      >
        <Box w="100%">
          <SidebarItems />
        </Box>
      </Box>
    </>
  )
}

export default Sidebar
