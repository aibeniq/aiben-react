import ChatMessages from "@/components/Chatbot/ChatMessages"
import InputArea from "@/components/Chatbot/InputArea"
import KnowledgeBaseSelectionModal from "@/components/Common/KnowledgeBaseSelectionModal"
import { useKnowledgeBases } from "@/hooks/useKnowledgeBases"
import { Box, Button, HStack, Icon, Show, Text } from "@chakra-ui/react"
import { useRouter } from "@tanstack/react-router"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { FiTrash } from "react-icons/fi"
import { Radio, RadioGroup } from "../ui/radio"
import { Tooltip } from "../ui/tooltip"
import { Checkbox } from "../ui/checkbox"
import { useAssistantStore } from "../../stores/assistantStore"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
  rephrasedQuestion?: string
  sessionId?: string
}

interface ChatbotPanelProps {
  isOpen: boolean
  messages: ChatMessage[]
  question: string
  setQuestion: (question: string) => void
  isLoading: boolean
  messagesEndRef: React.RefObject<HTMLDivElement>
  selectedKbId: string | null
  setSelectedKbId: (id: string | null) => void
  uploadedFiles: File[]
  setUploadedFiles: (files: File[]) => void
  setCurrentKbId: (id: string | null) => void
  setCurrentFileNames: (names: string[]) => void
  showKnowledgeBaseModal: boolean
  setShowKnowledgeBaseModal: (show: boolean) => void
  clearChat: () => void
  handleSendMessage: () => Promise<void>
  searchMode: "vector" | "full_text"
  setSearchMode: (mode: "vector" | "full_text") => void
  assistantMode: boolean
  setAssistantMode: (mode: boolean) => void
}

// Helper function to truncate text with ellipsis
const truncateText = (text: string, maxLength = 40): string => {
  if (text.length <= maxLength) return text
  return `${text.substring(0, maxLength)}...`
}

const ChatbotPanel = ({
  isOpen: _isOpen,
  messages,
  question,
  setQuestion,
  isLoading,
  messagesEndRef,
  selectedKbId,
  setSelectedKbId,
  uploadedFiles,
  setUploadedFiles,
  setCurrentKbId,
  setCurrentFileNames,
  showKnowledgeBaseModal,
  setShowKnowledgeBaseModal,
  clearChat,
  handleSendMessage,
  searchMode,
  setSearchMode,
  assistantMode,
  setAssistantMode,
}: ChatbotPanelProps) => {
  const { t } = useTranslation()
  const { knowledgeBases, showAllUsers, toggleShowAllUsers } = useKnowledgeBases() // Respect All Users toggle state
  const router = useRouter()

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, messagesEndRef])

  const handleSendMessageWrapper = async () => {
    console.log("handleSendMessageWrapper called, assistantMode:", assistantMode)
    if (assistantMode) {
      console.log("Calling handleAssistantRequest")
      await handleAssistantRequest(question, uploadedFiles)
    } else {
      console.log("Calling regular handleSendMessage")
      await handleSendMessage()
    }
  }

  const detectIntent = async (
    message: string,
    files: File[],
  ): Promise<{
    type: string
    suggestionType?: string
    isMultistep?: boolean
    steps?: Array<{ action: string; description: string }>
    parameters?: { customInstructions?: string; searchMode?: string; consultDocs?: boolean }
    confidence?: number
    reasoning?: string
  }> => {
    console.log(
      "detectIntent called with message:",
      message,
      "files:",
      files.map((f) => f.name),
    )
    try {
      // Add file names for context (not the actual files since they're large)
      const fileNames = files.map((f) => f.name)

      // Get base URL for API calls
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"

      console.log("Making request to", `${baseUrl}/api/v1/chat/assistant/detect-intent`)
      const requestData = {
        message: message,
        file_names: fileNames,
      }

      const response = await fetch(`${baseUrl}/api/v1/chat/assistant/detect-intent`, {
        method: "POST",
        body: JSON.stringify(requestData),
        credentials: "include", // Include cookies for authentication
        headers: {
          "Content-Type": "application/json",
        },
      })

      console.log("Response status:", response.status)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const intentData = await response.json()
      console.log("Intent detection response:", intentData)

      return {
        type: intentData.primary_intent,
        suggestionType: intentData.suggestion_type,
        isMultistep: intentData.is_multistep,
        steps: intentData.steps,
        parameters: intentData.parameters,
        confidence: intentData.confidence,
        reasoning: intentData.reasoning,
      }
    } catch (error) {
      console.error("Intent detection failed:", error)
      // Fallback to simple keyword detection
      const lowerMessage = message.toLowerCase()

      if (lowerMessage.includes("review") || lowerMessage.includes("checklist")) {
        return { type: "review" }
      } else if (lowerMessage.includes("generate") || lowerMessage.includes("report")) {
        return { type: "generate" }
      } else if (lowerMessage.includes("compare")) {
        return { type: "compare" }
      } else if (lowerMessage.includes("match") || lowerMessage.includes("form")) {
        return { type: "match" }
      }

      return { type: "chatbot" }
    }
  }

  const { setAssistantData } = useAssistantStore()

  const handleAssistantRequest = async (message: string, files: File[]) => {
    console.log(
      "Assistant request triggered with message:",
      message,
      "and files:",
      files.map((f) => f.name),
    )

    // 1. Analyze message and files using LLM
    const intent = await detectIntent(message, files)
    console.log("Detected intent:", intent)

    // 2. Determine target route based on primary intent
    let targetRoute = ""
    if (intent.type === "review") {
      targetRoute = "/review"
    } else if (intent.type === "generate") {
      targetRoute = "/generate"
    } else if (intent.type === "compare") {
      targetRoute = "/compare"
    } else if (intent.type === "match") {
      targetRoute = "/match"
    } else {
      // For chatbot or unknown intents, stay on current page
      targetRoute = window.location.pathname
    }

    // 3. Store comprehensive data in global state
    setAssistantData({
      message,
      files,
      assistantMode: true,
      targetRoute,
      suggestionType: intent.suggestionType,
      isMultistep: intent.isMultistep,
      steps: intent.steps,
      parameters: intent.parameters,
      currentStepIndex: 0,
    })
    console.log("Stored comprehensive assistant data:", {
      targetRoute,
      suggestionType: intent.suggestionType,
      isMultistep: intent.isMultistep,
      steps: intent.steps,
      parameters: intent.parameters,
    })

    // 4. Clear the input fields
    setQuestion("")
    setUploadedFiles([])
    console.log("Cleared input fields")

    // 5. Navigate to appropriate page if different from current
    if (targetRoute !== window.location.pathname) {
      console.log("Navigating to:", targetRoute)
      await router.navigate({ to: targetRoute })
    } else {
      console.log("Staying on current page for chatbot interaction")
    }
  }

  return (
    <>
      <Box
        width="100%"
        height="100%"
        bg="bg"
        overflow="hidden"
        display="flex"
        flexDirection="column"
      >
        <Box
          py={4}
          bg="rgba(0, 65, 72, 0.9)"
          color="white"
          display="flex"
          flexShrink={0}
          alignItems="center"
        >
          <Box flex="1" />
          <Text fontWeight="bold" fontSize="lg" py={2}>
            {t("chatbot.title")}
          </Text>
          <HStack gap={2} flex="1" justifyContent="flex-end">
            <Show when={messages.length > 0}>
              <Button
                variant="ghost"
                color="white"
                display="flex"
                alignItems="center"
                justifyContent="center"
                onClick={clearChat}
                size="sm"
                mx={3}
                _hover={{ bg: "teal" }}
                title="Clear chat history"
              >
                <Icon as={FiTrash} boxSize="20px" />
              </Button>
            </Show>
          </HStack>
        </Box>

        {/* Search Mode Toggle */}
        <Box px={4} pt={2} pb={1} bg="bg" borderBottom="1px solid" borderColor="gray.100">
          <RadioGroup
            value={searchMode}
            onValueChange={(details) => setSearchMode(details.value as "vector" | "full_text")}
            size="sm"
            colorPalette="teal"
          >
            <HStack gap={4}>
              <Text fontSize="xs" color="gray.600" fontWeight="medium">
                {t("chatbot.searchMode")}
              </Text>
              <Radio value="vector">
                <Text fontSize="xs">{t("chatbot.vectorSearch")}</Text>
              </Radio>
              <Radio value="full_text">
                <Text fontSize="xs">{t("chatbot.fullTextScan")}</Text>
              </Radio>
            </HStack>
          </RadioGroup>
          <Text fontSize="xs" color="gray.500" mt={1}>
            {t("chatbot.searchModeDescription")}
          </Text>
        </Box>

        <Box p={4} overflowY="auto" flex="1" height="100%">
          <Box width="100%" height="100%" overflowY="auto">
            <ChatMessages
              messages={messages}
              isLoading={isLoading}
              selectedKbId={selectedKbId}
              uploadedFiles={uploadedFiles}
              messagesEndRef={messagesEndRef}
            />
          </Box>
        </Box>

        <Box
          width="100%"
          bg="bg"
          borderTop="1px solid"
          borderColor="gray.100"
          flexShrink={0}
          position="relative"
        >
          <Box position="relative" width="100%" px={4} pt={2}>
            <Checkbox checked={assistantMode} onCheckedChange={setAssistantMode} mb={2}>
              {t("chatbot.enableAssistantMode")}
            </Checkbox>
            <InputArea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onSendClick={handleSendMessageWrapper}
              isLoading={isLoading}
              isSendDisabled={!question.trim() || isLoading}
              setShowKnowledgeBaseModal={setShowKnowledgeBaseModal}
              setUploadedFiles={setUploadedFiles}
              setSelectedKbId={setSelectedKbId}
            />
          </Box>
          <HStack
            gap={2}
            fontSize="xs"
            color="gray.500"
            pl={5}
            pb={3}
            justify="space-between"
            align="center"
          >
            <Box flex="1" minW="0">
              {selectedKbId ? (
                (() => {
                  const kbTitle = knowledgeBases.find((kb) => kb.id === selectedKbId)?.title || ""
                  const truncatedTitle = truncateText(kbTitle)
                  const needsTooltip = kbTitle.length > 40

                  const content = (
                    <Text>
                      {t("chatbot.usingKnowledgeBase")} <b>{truncatedTitle}</b>
                    </Text>
                  )

                  return needsTooltip ? (
                    <Tooltip content={`${t("chatbot.usingKnowledgeBase")} ${kbTitle}`} showArrow>
                      {content}
                    </Tooltip>
                  ) : (
                    content
                  )
                })()
              ) : uploadedFiles.length > 0 ? (
                (() => {
                  const fileNames = uploadedFiles.map((f) => f.name).join(", ")
                  const truncatedFileNames = truncateText(fileNames)
                  const needsTooltip = fileNames.length > 40

                  const content = (
                    <Text>
                      {t("chatbot.usingFiles", {
                        count: uploadedFiles.length,
                        plural: uploadedFiles.length > 1 ? "s" : "",
                      })}{" "}
                      <b>{truncatedFileNames}</b>
                    </Text>
                  )

                  return needsTooltip ? (
                    <Tooltip
                      content={`${t("chatbot.usingFiles", {
                        count: uploadedFiles.length,
                        plural: uploadedFiles.length > 1 ? "s" : "",
                      })} ${fileNames}`}
                      showArrow
                    >
                      {content}
                    </Tooltip>
                  ) : (
                    content
                  )
                })()
              ) : (
                <Text>{t("chatbot.usingGeneralAI")}</Text>
              )}
            </Box>
            <Show when={selectedKbId || uploadedFiles.length > 0}>
              <Text
                as="span"
                color="blue.500"
                cursor="pointer"
                _hover={{ textDecoration: "underline" }}
                onClick={() => {
                  setSelectedKbId(null)
                  setCurrentKbId(null)
                  setUploadedFiles([])
                  setCurrentFileNames([])
                }}
                flexShrink={0}
              >
                {t("chatbot.remove")}
              </Text>
            </Show>
          </HStack>
        </Box>
      </Box>

      <KnowledgeBaseSelectionModal
        isOpen={showKnowledgeBaseModal}
        onClose={() => setShowKnowledgeBaseModal(false)}
        title={t("chatbot.selectKnowledgeBase")}
        knowledgeBases={knowledgeBases}
        selectedKnowledgeBase={
          selectedKbId ? knowledgeBases.find((kb) => kb.id === selectedKbId) || null : null
        }
        onSelectionChange={(kb) => {
          setSelectedKbId(kb?.id || null)
          setUploadedFiles([])
        }}
        showAllUsers={showAllUsers}
        toggleShowAllUsers={toggleShowAllUsers}
      />
    </>
  )
}

export default ChatbotPanel
