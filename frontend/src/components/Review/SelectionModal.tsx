import React from "react"
import { Button, Card, Heading, HStack, IconButton } from "@chakra-ui/react"
import { FiX } from "react-icons/fi"

interface SelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

const SelectionModal = ({ isOpen, onClose, title, children }: SelectionModalProps) => {
  if (!isOpen) return null

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
      onClick={onClose}
    >
      <Card.Root maxW="4xl" maxH="80vh" w="90%" onClick={(e) => e.stopPropagation()}>
        <Card.Header>
          <HStack justify="space-between" align="center">
            <Heading size="lg">{title}</Heading>
            <IconButton size="sm" variant="ghost" onClick={onClose} aria-label="Close modal">
              <FiX />
            </IconButton>
          </HStack>
        </Card.Header>
        <Card.Body>{children}</Card.Body>
        <Card.Footer>
          <Button onClick={onClose}>Done</Button>
        </Card.Footer>
      </Card.Root>
    </div>
  )
}

export default SelectionModal
