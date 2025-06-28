import React, { useRef } from "react"
import { Button, Textarea, HStack, Icon, Box } from "@chakra-ui/react"
import { FiSend } from "react-icons/fi"
import SourcePopover from "@/components/Chatbot/SourcePopover"
import useCustomToast from "@/hooks/useCustomToast"

interface InputAreaProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  onSendClick: () => void
  isLoading?: boolean
  isSendDisabled?: boolean
  placeholder?: string
  setShowKnowledgeBaseModal: (show: boolean) => void
  setUploadedFiles: (files: File[]) => void
}

const InputArea: React.FC<InputAreaProps> = ({
  value,
  onChange,
  onSendClick,
  isLoading = false,
  isSendDisabled = false,
  placeholder = "Ask a question...",
  setShowKnowledgeBaseModal,
  setUploadedFiles,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("handleFileSelect called")
    const files = Array.from(event.target.files || [])
    console.log("Selected files:", files)

    if (files.length === 0) return

    // Check file size limit (10MB per file)
    const maxSize = 10 * 1024 * 1024 // 10MB
    const oversizedFiles = files.filter((file) => file.size > maxSize)

    if (oversizedFiles.length > 0) {
      showErrorToast(`Some files are too large. Maximum size is 10MB per file.`)
      return
    }

    if (files.length > 0 && setUploadedFiles) {
      console.log(
        "Setting uploaded files:",
        files.map((f) => f.name),
      )
      setUploadedFiles(files)
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
        accept=".pdf,.txt,.docx,.doc,.rtf"
        multiple
      />
      <Textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        resize="none"
        rows={1}
        fontSize="sm"
        height="40px"
        pl="40px"
        pr="40px"
        borderRadius="md"
        border="1px solid"
        borderColor="gray.200"
        _focus={{
          borderColor: "blue.500",
          boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)",
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            onSendClick()
          }
        }}
      />
      <HStack
        className="input-buttons"
        position="absolute"
        top="0"
        left="0"
        right="0"
        height="40px"
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
