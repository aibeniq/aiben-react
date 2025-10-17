import SourcePopover from "@/components/Chatbot/SourcePopover"
import useCustomToast from "@/hooks/useCustomToast"
import { Box, Button, HStack, Icon, Textarea } from "@chakra-ui/react"
import type React from "react"
import { useRef } from "react"
import { useTranslation } from "react-i18next"
import { FiSend } from "react-icons/fi"

interface InputAreaProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  onSendClick: () => void
  isLoading?: boolean
  isSendDisabled?: boolean
  placeholder?: string
  setShowKnowledgeBaseModal: (show: boolean) => void
  setUploadedFiles: (files: File[]) => void
  setSelectedKbId: (id: string | null) => void
}

const InputArea: React.FC<InputAreaProps> = ({
  value,
  onChange,
  onSendClick,
  isLoading = false,
  isSendDisabled = false,
  placeholder,
  setShowKnowledgeBaseModal,
  setUploadedFiles,
  setSelectedKbId,
}) => {
  const { t } = useTranslation()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Use translation if no placeholder provided
  const displayPlaceholder = placeholder || t("chatbot.placeholder")

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("handleFileSelect called")
    const files = Array.from(event.target.files || [])
    console.log("Selected files:", files)

    if (files.length === 0) return

    // Check file size limit (10MB per file)
    const maxSize = 100 * 1024 * 1024 // 100MB... upped from 10
    const oversizedFiles = files.filter((file) => file.size > maxSize)

    if (oversizedFiles.length > 0) {
      showErrorToast(t("toast.filesTooLarge"))
      return
    }

    if (files.length > 0 && setUploadedFiles) {
      console.log(
        "Setting uploaded files:",
        files.map((f) => f.name),
      )
      setUploadedFiles(files)
      // Clear knowledge base selection when files are uploaded
      setSelectedKbId(null)
      showSuccessToast(`${files.length} file${files.length > 1 ? "s" : ""} selected successfully.`)
    }
  }

  const triggerFileInput = () => {
    console.log("triggerFileInput called")
    if (fileInputRef.current) {
      console.log("Clicking file input")
      fileInputRef.current.click()
    } else {
      console.log("File input ref is null")
    }
  }

  return (
    <Box
      position="relative"
      width="100%"
      _hover={{
        "& .input-buttons": {
          opacity: 1,
        },
      }}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        style={{ display: "none" }}
        accept=".pdf,.txt,.docx,.doc,.rtf,.csv,.xlsx,.xls"
        multiple
      />
      <Textarea
        value={value}
        onChange={onChange}
        placeholder={displayPlaceholder}
        resize="vertical"
        minHeight="40px"
        maxHeight="200px"
        bg="white"
        border="1px solid #d0d7de"
        pl="50px" // Add left padding to make room for the plus icon
        pr="50px" // Add right padding to make room for the send button
        _hover={{
          borderColor: "#0969da",
        }}
        _focus={{
          borderColor: "#0969da",
          boxShadow: "0 0 0 1px #0969da",
        }}
      />
      <HStack
        className="input-buttons"
        position="absolute"
        top="2px" // Slightly inset from the top
        left="2px" // Slightly inset from the left
        right="2px" // Slightly inset from the right
        height="36px" // Slightly smaller than textarea min height
        pointerEvents="none"
        transition="opacity 0.2s"
      >
        <Box pointerEvents="auto">
          <SourcePopover
            onSelectKnowledgeBase={() => setShowKnowledgeBaseModal(true)}
            onSelectFile={triggerFileInput}
          />
        </Box>
        <Box flex={1} />
        <Box pointerEvents="auto">
          <Button
            onClick={onSendClick}
            disabled={isSendDisabled || isLoading}
            loading={isLoading}
            size="sm"
            height="40px"
            minW="40px"
            bg="transparent"
            color="rgba(0, 65, 72, 1.0)"
            _hover={{ bg: "transparent", color: "rgba(0, 65, 72, 0.8)" }}
          >
            <Icon as={FiSend} />
          </Button>
        </Box>
      </HStack>
    </Box>
  )
}

export default InputArea
