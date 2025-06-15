import React, { useRef } from "react"
import { Button, Textarea, HStack, Icon, Box } from "@chakra-ui/react"
import { FiSend } from "react-icons/fi"
import SourcePopover from "@/components/Chatbot/SourcePopover"

interface InputAreaProps {
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  onSendClick: () => void
  isLoading?: boolean
  isSendDisabled?: boolean
  placeholder?: string
  setShowKnowledgeBaseModal: (show: boolean) => void
  setUploadedFile: (file: File | null) => void
}

const InputArea: React.FC<InputAreaProps> = ({
  value,
  onChange,
  onSendClick,
  isLoading = false,
  isSendDisabled = false,
  placeholder = "Ask a question...",
  setShowKnowledgeBaseModal,
  setUploadedFile,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("handleFileSelect called")
    const file = event.target.files?.[0]
    console.log("Selected file:", file)
    if (file && setUploadedFile) {
      console.log("Setting uploaded file:", file.name)
      setUploadedFile(file)
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
        accept="*/*"
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
