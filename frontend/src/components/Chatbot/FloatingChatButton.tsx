import { IconButton } from "@chakra-ui/react"
import { FiMessageSquare } from "react-icons/fi"
import { useEffect } from "react"

interface FloatingChatButtonProps {
  onClick: () => void
}

const FloatingChatButton = ({ onClick }: FloatingChatButtonProps) => {
  // Simplified responsiveness check - less frequent, less aggressive
  useEffect(() => {
    const ensureButtonResponsive = () => {
      const buttonEl = document.querySelector('[aria-label="Get help"]') as HTMLElement
      if (buttonEl) {
        // Only update if styles are missing/wrong
        if (buttonEl.style.pointerEvents !== "auto") {
          buttonEl.style.pointerEvents = "auto"
        }
        if (buttonEl.style.zIndex !== "9999") {
          buttonEl.style.zIndex = "9999"
        }
      }
    }

    // Run immediately and set up less frequent checks
    ensureButtonResponsive()
    const interval = setInterval(ensureButtonResponsive, 5000) // Every 5 seconds instead of 1

    return () => clearInterval(interval)
  }, [])

  return (
    <IconButton
      position="fixed"
      bottom="4"
      right="4"
      size="lg"
      bg="rgba(0, 65, 72, 0.9)"
      color="white"
      boxShadow="lg"
      zIndex={9999} // Use explicit high z-index instead of "overlay"
      onClick={(e) => {
        e.stopPropagation() // Prevent event bubbling
        e.preventDefault() // Prevent default behavior
        console.log("🎯 FloatingChatButton clicked")

        // Simple safety check - only clean up obvious blocking overlays
        const blockingOverlays = document.querySelectorAll(
          '[data-scope="drawer"][data-part="backdrop"]:not([data-state="open"])',
        )
        if (blockingOverlays.length > 0) {
          console.log("🔧 Cleaning up stuck overlays before opening chat")
          blockingOverlays.forEach((overlay) => {
            const overlayEl = overlay as HTMLElement
            overlayEl.style.display = "none"
            overlayEl.style.pointerEvents = "none"
          })
        }

        onClick()
      }}
      _hover={{ bg: "rgba(0, 65, 72, 0.7)" }}
      transition="all 0.2s"
      aria-label="Get help"
      as={FiMessageSquare}
      rounded="full"
      width="56px"
      height="56px"
      p={3}
      // Simplified properties to ensure it's always interactive
      pointerEvents="auto"
      isolation="isolate"
      style={{
        // Minimal inline styles to ensure responsiveness
        pointerEvents: "auto",
        zIndex: 9999,
        isolation: "isolate",
      }}
    />
  )
}

export default FloatingChatButton
