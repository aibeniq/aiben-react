import React from "react"
import { Button } from "@chakra-ui/react"

interface ConfirmButtonProps {
  onClick: () => void
  loading?: boolean
  disabled?: boolean
  size?: "xs" | "sm" | "md" | "lg"
  children?: React.ReactNode
}

const ConfirmButton: React.FC<ConfirmButtonProps> = ({
  onClick,
  loading = false,
  disabled = false,
  size = "sm",
  children = "Confirm",
}) => {
  return (
    <Button
      size={size}
      onClick={onClick}
      loading={loading}
      disabled={disabled}
      bg="rgba(0, 65, 72, 0.9)"
      color="white"
      _hover={{ bg: "rgba(0, 65, 72, 0.8)" }}
    >
      {children}
    </Button>
  )
}

export default ConfirmButton
