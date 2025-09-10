import ChatMessages from "@/components/Chatbot/ChatMessages"
import InputArea from "@/components/Chatbot/InputArea"
import KnowledgeBaseTable from "@/components/Common/KnowledgeBaseTable"
import SelectionModal from "@/components/Common/SelectionModal"
import { Box, Button, HStack, Icon, Show, Text } from "@chakra-ui/react"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { FiTrash } from "react-icons/fi"
import { Radio, RadioGroup } from "../ui/radio"
import { useKnowledgeBases } from "@/hooks/useKnowledgeBases"

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
}: ChatbotPanelProps) => {
  const { t } = useTranslation()
  const { knowledgeBases } = useKnowledgeBases()

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, messagesEndRef])

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
            <InputArea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onSendClick={handleSendMessage}
              isLoading={isLoading}
              isSendDisabled={!question.trim() || isLoading}
              setShowKnowledgeBaseModal={setShowKnowledgeBaseModal}
              setUploadedFiles={setUploadedFiles}
              setSelectedKbId={setSelectedKbId}
            />
          </Box>
          <HStack gap={2} fontSize="xs" color="gray.500" pl={5} pb={3}>
            {selectedKbId ? (
              <Text>
                {t("chatbot.usingKnowledgeBase")}{" "}
                <b>{knowledgeBases.find((kb) => kb.id === selectedKbId)?.title}</b>
              </Text>
            ) : uploadedFiles.length > 0 ? (
              <Text>
                {t("chatbot.usingFiles", {
                  count: uploadedFiles.length,
                  plural: uploadedFiles.length > 1 ? "s" : "",
                })}{" "}
                <b>{uploadedFiles.map((f) => f.name).join(", ")}</b>
              </Text>
            ) : (
              <Text>{t("chatbot.usingGeneralAI")}</Text>
            )}
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
              >
                {t("chatbot.remove")}
              </Text>
            </Show>
          </HStack>
        </Box>
      </Box>

      <SelectionModal
        isOpen={showKnowledgeBaseModal}
        onClose={() => setShowKnowledgeBaseModal(false)}
        title={t("chatbot.selectKnowledgeBase")}
      >
        <KnowledgeBaseTable
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={
            selectedKbId ? knowledgeBases.find((kb) => kb.id === selectedKbId) || null : null
          }
          onSelectionChange={(kb) => {
            setSelectedKbId(kb?.id || null)
            setUploadedFiles([])
          }}
        />
      </SelectionModal>
    </>
  )
}

export default ChatbotPanel
