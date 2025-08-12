import { IconButton } from "@chakra-ui/react"
import { FiMessageSquare } from "react-icons/fi"

interface FloatingChatButtonProps {
  onClick: () => void
}

const FloatingChatButton = ({ onClick }: FloatingChatButtonProps) => {
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
        console.log("🎯 FloatingChatButton clicked")
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
      // Add these properties to ensure it's always interactive
      pointerEvents="auto"
      isolation="isolate"
    />
  )
}

export default FloatingChatButton
