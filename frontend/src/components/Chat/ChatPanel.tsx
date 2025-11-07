import { Box, Button, HStack, IconButton, Input, VStack, useDisclosure } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FaBrain } from "react-icons/fa"
import { FiFileText, FiPaperclip, FiSearch, FiSend, FiX } from "react-icons/fi"
import {
  ChatService,
  type KnowledgeBasePublic,
  type Message as MessageModel,
  type Source,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import KnowledgeBaseTable from "../KnowledgeBase/KnowledgeBaseTable"
import { CloseButton } from "../ui/CloseButton"
import { Drawer } from "../ui/Drawer"
import { Portal } from "../ui/Portal"
import { Radio, RadioGroup } from "../ui/radio"
import SelectionModal from "../ui/selection-modal"
import ChatMessage from "./ChatMessage"

interface Message {
  role: "user" | "assistant"
  content: string
}

interface ChatPanelProps {
  isOpen: boolean
  onClose: () => void
  knowledgeBase?: KnowledgeBasePublic | null
}

interface ChatInputProps {
  onSendMessage: (input: string) => void
  attachments: File[]
  setAttachments: (attachments: File[]) => void
  sources: Source[]
  setSources: (sources: Source[]) => void
  searchMode: "vector" | "full_text"
  setSearchMode: (mode: "vector" | "full_text") => void
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [input, setInput] = useState("")
  const [attachments, setAttachments] = useState<File[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [searchMode, setSearchMode] = useState<"vector" | "full_text">("vector")

  const handleSend = () => {
    onSendMessage(input)
    setInput("")
    setAttachments([])
    setSources([])
  }

  return (
    <HStack spacing={4}>
      <IconButton icon={<FiPaperclip />} aria-label="Attach file" onClick={() => {}} />
      <Input
        placeholder="Type your message here..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <Button colorScheme="blue" onClick={handleSend} leftIcon={<FiSend />}>
        Send
      </Button>
      <RadioGroup
        onValueChange={(details) => setSearchMode(details.value as "vector" | "full_text")}
        value={searchMode}
      >
        <HStack gap={4}>
          <Radio value="vector">Vector</Radio>
          <Radio value="full_text">Full Text</Radio>
        </HStack>
      </RadioGroup>
    </HStack>
  )
}

const ChatPanel: React.FC<ChatPanelProps> = ({
  isOpen,
  onClose,
  knowledgeBase: propKnowledgeBase,
}) => {
  const { showToast } = useCustomToast()
  const [messages, setMessages] = useState<Message[]>([])
  const [attachments, setAttachments] = useState<File[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [searchMode, setSearchMode] = useState<"vector" | "full_text">("vector")
  const [searchType, setSearchType] = useState<"vector" | "full_text">("vector") // New state for search type
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    propKnowledgeBase || null,
  )
  const endOfMessagesRef = useRef<HTMLDivElement>(null)

  const handleSendMessage = async (input: string) => {
    if (!input.trim()) return

    const userMessage: MessageModel = {
      role: "user",
      content: input,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await ChatService.chat({
        requestBody: {
          prompt: input,
          knowledge_base_id: selectedKnowledgeBase?.id,
          search_type: searchType,
        },
      })

      const assistantMessage: MessageModel = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      showToast({ title: "Error sending message", status: "error" })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (propKnowledgeBase) {
      setSelectedKnowledgeBase(propKnowledgeBase)
    }
  }, [propKnowledgeBase])

  return (
    <Portal>
      <Drawer.Root isOpen={isOpen} onClose={onClose}>
        <Drawer.Overlay />
        <Drawer.Positioner>
          <Drawer.Content>
            <Drawer.Header>
              <Drawer.Title>AI Assistant</Drawer.Title>
              <Drawer.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Drawer.CloseTrigger>
            </Drawer.Header>
            <Drawer.Body>
              <VStack h="full" align="stretch">
                <Box flex={1} overflowY="auto" p={4}>
                  {messages.map((msg, index) => (
                    <ChatMessage key={index} message={msg} />
                  ))}
                  <div ref={endOfMessagesRef} />
                </Box>
                <Box p={4} borderTopWidth="1px">
                  <VStack align="stretch" gap={2}>
                    <HStack>
                      <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        onKeyDown={(e) =>
                          e.key === "Enter" && !isLoading && handleSendMessage(input)
                        }
                        disabled={isLoading}
                      />
                      <IconButton
                        aria-label="Send message"
                        icon={<FiSend />}
                        onClick={() => handleSendMessage(input)}
                        isLoading={isLoading}
                        colorScheme="blue"
                      />
                    </HStack>
                    <RadioGroup
                      onValueChange={(details) =>
                        setSearchType(details.value as "vector" | "full_text")
                      }
                      value={searchType}
                    >
                      <HStack gap={4}>
                        <Radio value="vector">Fast Search</Radio>
                        <Radio value="full_text">Full Text Scan</Radio>
                      </HStack>
                    </RadioGroup>
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      Fast search provides fast, targeted results. Full text scan reviews all
                      content in the knowledge base.
                    </Text>
                  </VStack>
                </Box>
              </VStack>
            </Drawer.Body>
          </Drawer.Content>
        </Drawer.Positioner>
      </Drawer.Root>
    </Portal>
  )
}

export default ChatPanel
