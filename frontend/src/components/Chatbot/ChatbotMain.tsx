import { ChatService } from "@/client"
import ChatbotPanel from "@/components/Chatbot/ChatbotPanel"
import FloatingChatButton from "@/components/Chatbot/FloatingChatButton"
import type { ProcessingSettings } from "@/components/Common/ProcessingSettingsPopup"
import useAuth from "@/hooks/useAuth"
import { Drawer } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

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
  const { t } = useTranslation()
  const { user } = useAuth()
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

  // Processing settings state - initialized from user defaults
  const [processingSettings, setProcessingSettings] = useState<ProcessingSettings>({
    searchMode: (user?.default_processing_mode as "vector" | "full_scan") || "vector",
    visionAnalysis: user?.vision_analysis_enabled || false,
    pdfParsing: (user?.pdf_parsing_preference as "enhanced" | "basic") || "basic",
  })

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

  // Simplified overlay management - less aggressive than before
  useEffect(() => {
    const handleGlobalClick = (event: MouseEvent) => {
      // Only intervene if there's a clear sign of overlay problems
      // and the chat is not open (to avoid conflicts)
      if (!isOpen) {
        const target = event.target as HTMLElement

        // Check if the click target is obviously blocked
        if (target && !target.click) {
          console.warn("🚨 Detected unresponsive element, cleaning overlays")

          // Only clean up clearly problematic overlays
          const stuckOverlays = document.querySelectorAll(
            '[data-scope="drawer"][data-part="backdrop"]:not([data-state="open"])',
          )

          stuckOverlays.forEach((overlay) => {
            const overlayEl = overlay as HTMLElement
            overlayEl.style.display = "none"
            overlayEl.style.pointerEvents = "none"
          })
        }
      }
    }

    // Use a less intrusive event listener
    document.addEventListener("click", handleGlobalClick, false)
    return () => document.removeEventListener("click", handleGlobalClick, false)
  }, [isOpen])

  const handleChatbotResponse = (response: any, userMessage: string) => {
    if (!response) return

    console.log("Sources from response:", response.sources)

    // Check if sources have source_data_id
    if (response.sources && response.sources.length > 0) {
      console.log("First source metadata:", response.sources[0].metadata)
      console.log("Source has ID:", !!response.sources[0].metadata?.source_data_id)
    }

    // Handle error_key - translate it to the user's language
    let displayContent = response.answer
    if (response.error_key) {
      displayContent = t(response.error_key)
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
        content: displayContent + (rephrasedInfo ? `\n\n${rephrasedInfo}` : ""),
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
          isFollowUp: !!(isFollowUp && sessionId),
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
          isFollowUp: !!(isFollowUp && sessionId), // Only true if we have a session ID
          searchMode: processingSettings.searchMode === "full_scan" ? "full_text" : "vector", // Map full_scan to full_text for chatbot
          visionAnalysisOverride: processingSettings.visionAnalysis,
          pdfParsingOverride: processingSettings.pdfParsing,
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
        const hasVeryLargeFile = uploadedFiles.some((file) => file.size > 50 * 1024 * 1024) // > 50MB

        if (hasVeryLargeFile && processingSettings.searchMode === "vector") {
          console.log("Large file detected, recommending full text mode")
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content:
                "⚠️ Large document detected. For better performance with files over 50MB, consider switching to 'Deep Search' mode using the gear icon above.",
            },
          ])
        }

        const formData = new FormData()
        // For full-text mode, always send the files since they're needed for each query
        // For vector mode, only send the files if this is NOT a follow-up question
        if (processingSettings.searchMode === "full_scan" || !isFollowUp) {
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
            processingSettings.searchMode === "full_scan" || !isFollowUp
              ? { files: uploadedFiles }
              : undefined,
          searchMode: processingSettings.searchMode === "full_scan" ? "full_text" : "vector", // Map full_scan to full_text for chatbot
          visionAnalysisOverride: processingSettings.visionAnalysis,
          pdfParsingOverride: processingSettings.pdfParsing,
        })

        console.log("Response:", response)
        handleChatbotResponse(response as any, userMessage)
      }
    } catch (error) {
      console.error("Error querying:", error)

      // Better error handling for timeouts and large files
      let errorMessage = t("chatbot.errors.generic")

      if (error && typeof error === "object") {
        const errorObj = error as any

        // Check for session expiration errors
        if (
          errorObj.response?.data?.detail?.includes("Session expired") ||
          errorObj.response?.data?.detail?.includes("session expired")
        ) {
          errorMessage = "Session expired. Please upload your documents again."
        } else if (errorObj.code === "ERR_NETWORK" || errorObj.message?.includes("timeout")) {
          const hasLargeFiles = uploadedFiles.some((file) => file.size > 10 * 1024 * 1024)
          if (hasLargeFiles) {
            errorMessage = t("chatbot.errors.largeFileTimeout")
          } else {
            errorMessage = t("chatbot.errors.timeout")
          }
        } else if (errorObj.response?.status === 413) {
          errorMessage = t("chatbot.errors.fileSize")
        } else if (errorObj.response?.status >= 500) {
          errorMessage = t("chatbot.errors.serverError")
        } else if (errorObj.response?.data?.detail) {
          // Use the specific error message from the backend if available
          errorMessage = errorObj.response.data.detail
        }
      }

      setMessages((prev) => [...prev, { role: "assistant", content: errorMessage }])
    } finally {
      setIsLoading(false)
    }
  }

  // Simplified overlay management to prevent UI responsiveness issues
  useEffect(() => {
    console.log("Chat drawer state changed:", { isOpen })

    if (isOpen) {
      // Ensure drawer content is properly visible
      const drawerContent = document.querySelector('[data-scope="drawer"][data-part="content"]')
      if (drawerContent) {
        const contentEl = drawerContent as HTMLElement
        contentEl.style.opacity = "1"
        contentEl.style.backgroundColor = "white"
        contentEl.style.position = "relative"
        contentEl.style.zIndex = "9001"
      }
    } else {
      // When chat is closed, clean up only chat-related overlays
      setTimeout(() => {
        console.log("Chat closed - cleaning up chat overlays")

        // Only clean up chat overlays (placement="end")
        const chatOverlays = document.querySelectorAll(
          '[data-placement="end"] [data-scope="drawer"][data-part="backdrop"]',
        )
        chatOverlays.forEach((overlay) => {
          const overlayEl = overlay as HTMLElement
          overlayEl.style.display = "none"
          overlayEl.style.pointerEvents = "none"
        })
      }, 10) // Small delay to allow animation to complete
    }
  }, [isOpen])

  return (
    <>
      {!isOpen && <FloatingChatButton onClick={handleOpenChat} />}
      {isOpen && (
        <Drawer.Root
          open={isOpen}
          onOpenChange={({ open }) => {
            console.log("Drawer onOpenChange called with:", { open })
            if (!open) {
              handleCloseChat()
            }
          }}
          placement="end"
          size="md"
        >
          {/* Enhanced Drawer.Backdrop with explicit cleanup */}
          <Drawer.Backdrop
            onClick={() => {
              console.log("Backdrop clicked - closing chat")
              handleCloseChat()
            }}
            style={{
              pointerEvents: "auto",
              zIndex: 8999, // Lower than floating chat button
            }}
          />
          <Drawer.Positioner
            style={{
              pointerEvents: "none", // Allow clicks to pass through positioner
              zIndex: 9000,
            }}
          >
            <Drawer.Content
              style={{
                pointerEvents: "auto", // Re-enable for content
                zIndex: 9001,
              }}
            >
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
                processingSettings={processingSettings}
                setProcessingSettings={setProcessingSettings}
              />
            </Drawer.Content>
          </Drawer.Positioner>
        </Drawer.Root>
      )}
    </>
  )
}

export default ChatbotMain
