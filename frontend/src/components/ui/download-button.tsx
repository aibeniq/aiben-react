import { Button } from "@chakra-ui/react"
import type React from "react"
import { FiDownload } from "react-icons/fi"

interface DownloadButtonProps {
  onClick: () => void
  loading?: boolean
  disabled?: boolean
  size?: "xs" | "sm" | "md" | "lg"
  children?: React.ReactNode
}

const DownloadButton: React.FC<DownloadButtonProps> = ({
  onClick,
  loading = false,
  disabled = false,
  size = "sm",
  children = "Download DOCX",
}) => {
  return (
    <Button
      size={size}
      variant="outline"
      onClick={onClick}
      loading={loading}
      disabled={disabled}
      colorPalette="rgba(0, 65, 72, 0.9)"
      border="1px solid"
      borderColor="rgba(0, 65, 72, 0.3)"
      _hover={{ bg: "rgba(0, 65, 72, 0.1)" }}
    >
      <FiDownload />
      {children}
    </Button>
  )
}

export default DownloadButton
