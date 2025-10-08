import {
  Card,
  CloseButton,
  HStack,
  Heading,
  Switch,
  Text,
} from "@chakra-ui/react"
import type React from "react"
import ConfirmButton from "../ui/confirm-button"
import HelpTooltip from "../ui/help-tooltip"
import { Tooltip } from "../ui/tooltip"

interface SelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  // Optional toggle props
  showToggle?: boolean
  toggleLabel?: string
  toggleValue?: boolean
  onToggleChange?: () => void
  toggleTooltipContent?: string
}

const SelectionModal = ({
  isOpen,
  onClose,
  title,
  children,
  showToggle = false,
  toggleLabel = "",
  toggleValue = false,
  onToggleChange,
  toggleTooltipContent = "",
}: SelectionModalProps) => {
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
      <Card.Root
        maxW="4xl"
        maxH="80vh"
        w="90%"
        onClick={(e) => e.stopPropagation()}
      >
        <Card.Header>
          <HStack justify="space-between" align="center">
            <Heading size="lg">{title}</Heading>
            <CloseButton size="xl" onClick={onClose} variant="ghost" />
          </HStack>
          {/* Toggle section */}
          {showToggle && (
            <HStack justifyContent="flex-end" mt={2}>
              <Tooltip content={toggleTooltipContent}>
                <HStack gap={2}>
                  <HStack gap={1} align="center">
                    <Text fontSize="xs" color="gray.500">
                      {toggleLabel}
                    </Text>
                    <HelpTooltip helpKey="allUsersToggle" />
                  </HStack>
                  <Switch.Root
                    key={`switch-${toggleValue}`}
                    size="sm"
                    colorPalette="blue"
                    checked={toggleValue}
                  >
                    <Switch.HiddenInput
                      checked={toggleValue}
                      onChange={onToggleChange}
                    />
                    <Switch.Control
                      data-state={toggleValue ? "checked" : "unchecked"}
                    >
                      <Switch.Thumb />
                    </Switch.Control>
                  </Switch.Root>
                </HStack>
              </Tooltip>
            </HStack>
          )}
        </Card.Header>
        <Card.Body>{children}</Card.Body>
        <Card.Footer justifyContent="flex-end">
          <ConfirmButton onClick={onClose} size="md">
            Done
          </ConfirmButton>
        </Card.Footer>
      </Card.Root>
    </div>
  )
}

export default SelectionModal
