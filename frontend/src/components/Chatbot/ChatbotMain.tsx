import { useState } from "react"
import FloatingChatButton from "./FloatingChatButton"
import ChatbotPanel from "./ChatbotPanel"

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false)

  const handleOpen = () => setIsOpen(true)
  const handleClose = () => setIsOpen(false)

  return (
    <>
      <FloatingChatButton onClick={handleOpen} />
      <ChatbotPanel isOpen={isOpen} onClose={handleClose} />
    </>
  )
}

export default Chatbot
