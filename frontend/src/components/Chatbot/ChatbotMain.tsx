import { useState, useRef } from "react"
import { Drawer } from "@chakra-ui/react"
import FloatingChatButton from "@/components/Chatbot/FloatingChatButton"
import ChatbotPanel from "@/components/Chatbot/ChatbotPanel"
import { ChatService } from "@/client"

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

const ChatbotMain = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedKbId, setSelectedKbId] = useState<string | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [currentKbId, setCurrentKbId] = useState<string | null>(null)
  const [currentFileName, setCurrentFileName] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string>("")
  const [searchMode, setSearchMode] = useState<"vector" | "full_text">("vector")

  const clearChat = () => {
    setMessages([])
    setSessionId(Math.random().toString(36).substring(2, 15))
    setSelectedKbId(null)
    setUploadedFile(null)
  }

  const handleChatbotResponse = (response: any, userMessage: string) => {
    if (!response?.answer) return

    console.log("Sources from response:", response.sources)

    // Check if sources have source_data_id
    if (response.sources && response.sources.length > 0) {
      console.log("First source metadata:", response.sources[0].metadata)
      console.log("Source has ID:", !!response.sources[0].metadata?.source_data_id)
    }

    // You can show the rephrased question if you want
    const rephrasedInfo =
      response.rephrased_question && response.rephrased_question !== userMessage
        ? `(Interpreted as: "${response.rephrased_question}")`
        : ""

    // Store the session ID from the response
    if (response.session_id) {
      setSessionId(response.session_id)
      console.log("Received session ID from server:", response.session_id)
    }

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: response.answer + (rephrasedInfo ? `\n\n${rephrasedInfo}` : ""),
        sources: response.sources,
        rephrasedQuestion: response.rephrased_question,
        sessionId: response.session_id,
      },
    ])
  }

  const handleSendMessage = async () => {
    if (!question.trim()) return

    console.log("Current session ID:", sessionId)
    console.log("Current KB ID:", currentKbId)
    console.log("Selected KB ID:", selectedKbId)

    const userMessage = question

    // Add the new user message to chat history
    const newMessage: ChatMessage = { role: "user", content: userMessage }
    const updatedMessages = [...messages, newMessage]
    setMessages(updatedMessages)
    setQuestion("")
    setIsLoading(true)

    try {
      // Format chat history for API
      // Only send the last 10 messages to keep context manageable
      const recentHistory = updatedMessages.slice(-10)
      const formattedChatHistory = recentHistory
        .map((msg) => {
          const role = msg.role === "user" ? "User" : "Assistant"
          return `${role}: ${msg.content}`
        })
        .join("\n\n")

      // Check if this is a follow-up question with the same resources
      const isFollowUp =
        sessionId &&
        ((selectedKbId && selectedKbId === currentKbId) ||
          (uploadedFile && currentFileName === uploadedFile.name))
      console.log("Formatted chat history:", formattedChatHistory)
      console.log("Is follow-up:", isFollowUp)

      if (!selectedKbId && !uploadedFile) {
        // New case: No KB or file selected - use direct text query
        const response = await ChatService.queryText({
          question: userMessage,
          chatHistory: formattedChatHistory,
          sessionId: sessionId,
          isFollowUp: isFollowUp && sessionId ? true : false,
        })

        console.log("Response:", response)
        handleChatbotResponse(response as any, userMessage)
      } else if (selectedKbId) {
        // Set current KB ID if it's changed
        if (currentKbId !== selectedKbId) {
          setCurrentKbId(selectedKbId)
          // Generate new session ID when knowledge base changes
          setSessionId("") // Clear it and let the server generate a new one
          console.log("KB changed, clearing session ID")
        }

        const response = await ChatService.queryKnowledgeBase({
          kbId: selectedKbId,
          question: userMessage,
          chatHistory: formattedChatHistory,
          useDefaultModels: true,
          sessionId: sessionId, // Make sure this is being sent correctly
          isFollowUp: isFollowUp && sessionId ? true : false, // Only true if we have a session ID
          searchMode: searchMode, // Pass the search mode
        })

        console.log("Response:", response)
        handleChatbotResponse(response as any, userMessage)
      } else if (uploadedFile) {
        // Set current filename if it's changed
        if (currentFileName !== uploadedFile.name) {
          setCurrentFileName(uploadedFile.name)
          // Don't generate a new session ID here - let the server handle it
          setSessionId("") // Clear it and let the server generate a new one
          console.log("File changed, clearing session ID")
        }
        const formData = new FormData()
        // Only send the file if this is NOT a follow-up question
        if (!isFollowUp) {
          formData.append("file", uploadedFile)
        }

        const response = await ChatService.queryDocument({
          question: userMessage,
          chatHistory: formattedChatHistory,
          useDefaultModels: true,
          sessionId: sessionId,
          isFollowUp: isFollowUp === true,
          formData: isFollowUp ? undefined : { file: uploadedFile },
          searchMode: searchMode, // Pass the search mode
        })

        console.log("Response:", response)
        handleChatbotResponse(response as any, userMessage)
      }
    } catch (error) {
      console.error("Error querying:", error)
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't process your request. Please try again." },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <FloatingChatButton onClick={() => setIsOpen(true)} />
      <Drawer.Root
        open={isOpen}
        onOpenChange={(details) => setIsOpen(details.open)}
        placement="end"
        size="md"
      >
        <Drawer.Trigger asChild>
          <FloatingChatButton onClick={() => setIsOpen(true)} />
        </Drawer.Trigger>
        <Drawer.Backdrop />
        <Drawer.Positioner>
          <Drawer.Content>
            <ChatbotPanel
              isOpen={isOpen}
              messages={messages}
              question={question}
              setQuestion={setQuestion}
              isLoading={isLoading}
              messagesEndRef={messagesEndRef}
              selectedKbId={selectedKbId}
              setSelectedKbId={setSelectedKbId}
              uploadedFile={uploadedFile}
              setUploadedFile={setUploadedFile}
              setCurrentKbId={setCurrentKbId}
              setCurrentFileName={setCurrentFileName}
              showKnowledgeBaseModal={showKnowledgeBaseModal}
              setShowKnowledgeBaseModal={setShowKnowledgeBaseModal}
              clearChat={clearChat}
              handleSendMessage={handleSendMessage}
              searchMode={searchMode}
              setSearchMode={setSearchMode}
            />
          </Drawer.Content>
        </Drawer.Positioner>
      </Drawer.Root>
    </>
  )
}

export default ChatbotMain
