import { Box, Button, HStack, Text, Icon, Show } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { FiTrash } from "react-icons/fi"
import { KnowledgeBasesService } from "@/client"
import SelectionModal from "@/components/Common/SelectionModal"
import KnowledgeBaseTable from "@/components/Common/KnowledgeBaseTable"
import ChatMessages from "@/components/Chatbot/ChatMessages"
import InputArea from "@/components/Chatbot/InputArea"
import { useEffect } from "react"

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
  uploadedFile: File | null
  setUploadedFile: (file: File | null) => void
  setCurrentKbId: (id: string | null) => void
  setCurrentFileName: (name: string | null) => void
  showKnowledgeBaseModal: boolean
  setShowKnowledgeBaseModal: (show: boolean) => void
  clearChat: () => void
  handleSendMessage: () => Promise<void>
}

const ChatbotPanel = ({
  isOpen,
  messages,
  question,
  setQuestion,
  isLoading,
  messagesEndRef,
  selectedKbId,
  setSelectedKbId,
  uploadedFile,
  setUploadedFile,
  setCurrentKbId,
  setCurrentFileName,
  showKnowledgeBaseModal,
  setShowKnowledgeBaseModal,
  clearChat,
  handleSendMessage,
}: ChatbotPanelProps) => {
  // Get knowledge bases
  const { data: knowledgeBases = [] } = useQuery({
    queryKey: ["knowledge-bases"],
    queryFn: async () => {
      const response = await KnowledgeBasesService.readKnowledgeBases({
        skip: 0,
        limit: 100,
      })
      return response.data || []
    },
    enabled: isOpen,
  })

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
            Chat
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

        <Box p={4} overflowY="auto" flex="1" height="100%">
          <Box width="100%" height="100%" overflowY="auto">
            <ChatMessages
              messages={messages}
              isLoading={isLoading}
              selectedKbId={selectedKbId}
              uploadedFile={uploadedFile}
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
              setUploadedFile={setUploadedFile}
            />
          </Box>
          <HStack gap={2} fontSize="xs" color="gray.500" pl={5} pb={3}>
            {selectedKbId ? (
              <Text>
                Using knowledge base:{" "}
                <b>{knowledgeBases.find((kb) => kb.id === selectedKbId)?.title}</b>
              </Text>
            ) : uploadedFile ? (
              <Text>
                Using document: <b>{uploadedFile.name}</b>
              </Text>
            ) : (
              <Text>Using general AI assistant</Text>
            )}
            <Show when={selectedKbId || uploadedFile}>
              <Text
                as="span"
                color="blue.500"
                cursor="pointer"
                _hover={{ textDecoration: "underline" }}
                onClick={() => {
                  setSelectedKbId(null)
                  setCurrentKbId(null)
                  setUploadedFile(null)
                  setCurrentFileName(null)
                }}
              >
                Remove
              </Text>
            </Show>
          </HStack>
        </Box>
      </Box>

      <SelectionModal
        isOpen={showKnowledgeBaseModal}
        onClose={() => setShowKnowledgeBaseModal(false)}
        title="Select Knowledge Base"
      >
        <KnowledgeBaseTable
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={
            selectedKbId ? knowledgeBases.find((kb) => kb.id === selectedKbId) || null : null
          }
          onSelectionChange={(kb) => {
            setSelectedKbId(kb?.id || null)
            setUploadedFile(null)
          }}
        />
      </SelectionModal>
    </>
  )
}

export default ChatbotPanel
