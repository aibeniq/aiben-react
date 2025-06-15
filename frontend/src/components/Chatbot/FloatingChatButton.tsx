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
      zIndex="overlay"
      onClick={onClick}
      _hover={{ bg: "rgba(0, 65, 72, 0.7)" }}
      transition="all 0.2s"
      aria-label="Get help"
      as={FiMessageSquare}
      rounded="full"
      width="56px"
      height="56px"
      p={3}
    />
  )
}

export default FloatingChatButton
