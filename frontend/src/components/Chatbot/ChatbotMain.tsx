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
    setSessionId("")
    setSelectedKbId(null)
    setUploadedFiles([])
  }

  const handleOpenChat = () => {
    console.log("🎯 FloatingChatButton clicked, opening chat")
    setIsOpen(true)
  }

  const handleCloseChat = () => {
    console.log("🔒 Closing chat drawer")
    setIsOpen(false)
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

        // Check for large files and adjust timeout
        const hasVeryLargeFile = uploadedFiles.some(file => file.size > 50 * 1024 * 1024) // > 50MB
        
        if (hasVeryLargeFile && searchMode === "vector") {
          console.log("Large file detected, recommending full text mode")
          setMessages((prev) => [
            ...prev,
            { 
              role: "assistant", 
              content: "⚠️ Large document detected. For better performance with files over 50MB, consider switching to 'Full Text Scan' mode using the toggle above."
            },
          ])
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
      
      // Better error handling for timeouts and large files
      let errorMessage = "Sorry, I couldn't process your request. Please try again."
      
      if (error && typeof error === 'object') {
        const errorObj = error as any
        if (errorObj.code === "ERR_NETWORK" || errorObj.message?.includes("timeout")) {
          const hasLargeFiles = uploadedFiles.some(file => file.size > 10 * 1024 * 1024)
          if (hasLargeFiles) {
            errorMessage = "The document is very large and processing timed out. Please try with a smaller document or switch to 'Full Text Scan' mode which is more efficient for large files."
          } else {
            errorMessage = "Request timed out. Please check your connection and try again."
          }
        } else if (errorObj.response?.status === 413) {
          errorMessage = "The uploaded file is too large. Please try with a smaller document."
        } else if (errorObj.response?.status >= 500) {
          errorMessage = "Server error occurred. The document might be too large or complex to process. Please try with a smaller file or contact support."
        }
      }
      
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMessage },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // Defensive: always neutralize any drawer backdrops so chat panel is never dimmed
  useEffect(() => {
    if (isOpen) {
      // Find the drawer content and ensure it's fully opaque
      const drawerContent = document.querySelector('[data-scope="drawer"][data-part="content"]')
      if (drawerContent) {
        const contentEl = drawerContent as HTMLElement
        contentEl.style.opacity = "1"
        contentEl.style.backgroundColor = "white"
        contentEl.style.position = "relative"
        contentEl.style.zIndex = "9001"
      }
    }
  }, [isOpen])

  return (
    <>
      {!isOpen && <FloatingChatButton onClick={handleOpenChat} />}
      {isOpen && (
        <Drawer.Root
          open={isOpen}
          onOpenChange={({ open }) => !open && handleCloseChat()}
          placement="end"
          size="md"
        >
          {/* Use the built-in Drawer.Backdrop but with custom styling */}
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
      )}
    </>
  )
}

export default ChatbotMain
