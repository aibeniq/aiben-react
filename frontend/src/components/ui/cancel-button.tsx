import React from "react"
import { Button } from "@chakra-ui/react"

interface CancelButtonProps {
  onClick: () => void
  loading?: boolean
  disabled?: boolean
  size?: "xs" | "sm" | "md" | "lg"
  children?: React.ReactNode
}

const CancelButton = React.forwardRef<HTMLButtonElement, CancelButtonProps>(
  ({ onClick, loading = false, disabled = false, size = "sm", children = "Cancel" }, ref) => {
    return (
      <Button
        ref={ref}
        size={size}
        variant="outline"
        onClick={onClick}
        loading={loading}
        disabled={disabled}
        colorPalette="gray"
        border="1px solid"
        borderColor="gray.300"
        _hover={{ bg: "gray.50" }}
      >
        {children}
      </Button>
    )
  },
)

CancelButton.displayName = "CancelButton"

export default CancelButton
