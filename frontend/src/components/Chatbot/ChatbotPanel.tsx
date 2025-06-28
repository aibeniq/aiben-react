import { Box, Button, HStack, Text, Icon, Show } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { FiTrash } from "react-icons/fi"
import { KnowledgeBasesService } from "@/client"
import SelectionModal from "@/components/Common/SelectionModal"
import KnowledgeBaseTable from "@/components/Common/KnowledgeBaseTable"
import ChatMessages from "@/components/Chatbot/ChatMessages"
import InputArea from "@/components/Chatbot/InputArea"
import { useEffect } from "react"
import { Radio, RadioGroup } from "../ui/radio"

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
  isOpen,
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
                Search Mode:
              </Text>
              <Radio value="vector">
                <Text fontSize="xs">Vector Search</Text>
              </Radio>
              <Radio value="full_text">
                <Text fontSize="xs">Full Text Scan</Text>
              </Radio>
            </HStack>
          </RadioGroup>
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
            />
          </Box>
          <HStack gap={2} fontSize="xs" color="gray.500" pl={5} pb={3}>
            {selectedKbId ? (
              <Text>
                Using knowledge base:{" "}
                <b>{knowledgeBases.find((kb) => kb.id === selectedKbId)?.title}</b>
              </Text>
            ) : uploadedFiles.length > 0 ? (
              <Text>
                Using {uploadedFiles.length} document{uploadedFiles.length > 1 ? "s" : ""}:{" "}
                <b>{uploadedFiles.map((f) => f.name).join(", ")}</b>
              </Text>
            ) : (
              <Text>Using general AI assistant</Text>
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
            setUploadedFiles([])
          }}
        />
      </SelectionModal>
    </>
  )
}

export default ChatbotPanel
