import { useState, useRef, useEffect } from "react"
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
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [currentKbId, setCurrentKbId] = useState<string | null>(null)
  const [currentFileNames, setCurrentFileNames] = useState<string[]>([])
  const [sessionId, setSessionId] = useState<string>("")
  const [searchMode, setSearchMode] = useState<"vector" | "full_text">("vector")

  const clearChat = () => {
    setMessages([])
    setSessionId(Math.random().toString(36).substring(2, 15))
    setSelectedKbId(null)
    setUploadedFiles([])
  }

  const handleOpenChat = () => {
    console.log("🎯 FloatingChatButton clicked, opening chat")
    setIsOpen(true)
  }

  const handleDrawerOpenChange = (details: { open: boolean }) => {
    console.log("🎯 Drawer state changed:", details.open)
    setIsOpen(details.open)
  }

  // Add escape key handler as emergency fallback
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        console.log("🚨 Emergency escape - closing chat drawer")
        setIsOpen(false)
      }
    }

    document.addEventListener("keydown", handleEscapeKey)
    return () => document.removeEventListener("keydown", handleEscapeKey)
  }, [isOpen])

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
      const currentFileNamesStr = uploadedFiles
        .map((f) => f.name)
        .sort()
        .join(",")
      const isFollowUp =
        sessionId &&
        ((selectedKbId && selectedKbId === currentKbId) ||
          (uploadedFiles.length > 0 && currentFileNames.sort().join(",") === currentFileNamesStr))
      console.log("Formatted chat history:", formattedChatHistory)
      console.log("Is follow-up:", isFollowUp)

      if (!selectedKbId && uploadedFiles.length === 0) {
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
      } else if (uploadedFiles.length > 0) {
        // Set current filenames if they've changed
        const newFileNamesStr = uploadedFiles
          .map((f) => f.name)
          .sort()
          .join(",")
        if (currentFileNames.sort().join(",") !== newFileNamesStr) {
          setCurrentFileNames(uploadedFiles.map((f) => f.name))
          // Don't generate a new session ID here - let the server handle it
          setSessionId("") // Clear it and let the server generate a new one
          console.log("Files changed, clearing session ID")
        }

        const formData = new FormData()
        // For full-text mode, always send the files since they're needed for each query
        // For vector mode, only send the files if this is NOT a follow-up question
        if (searchMode === "full_text" || !isFollowUp) {
          uploadedFiles.forEach((file) => {
            formData.append("files", file)
          })
        }

        const response = await ChatService.queryDocument({
          question: userMessage,
          chatHistory: formattedChatHistory,
          useDefaultModels: true,
          sessionId: sessionId,
          isFollowUp: isFollowUp === true,
          formData:
            searchMode === "full_text" || !isFollowUp ? { files: uploadedFiles } : undefined,
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
      {/* Only show floating button when drawer is closed */}
      {!isOpen && <FloatingChatButton onClick={handleOpenChat} />}

      <Drawer.Root open={isOpen} onOpenChange={handleDrawerOpenChange} placement="end" size="md">
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
              uploadedFiles={uploadedFiles}
              setUploadedFiles={setUploadedFiles}
              setCurrentKbId={setCurrentKbId}
              setCurrentFileNames={setCurrentFileNames}
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
