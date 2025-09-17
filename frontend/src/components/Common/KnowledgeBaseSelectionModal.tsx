import { Card, CloseButton, HStack, Heading, Text, Switch } from "@chakra-ui/react"
import ConfirmButton from "../ui/confirm-button"
import { Tooltip } from "../ui/tooltip"
import HelpTooltip from "../ui/help-tooltip"
import { useTranslation } from "react-i18next"
import KnowledgeBaseTable from "./KnowledgeBaseTable"
import type { KnowledgeBasePublic } from "@/client"

interface KnowledgeBaseSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBase: KnowledgeBasePublic | null
  onSelectionChange: (kb: KnowledgeBasePublic | null) => void
  // Toggle props
  showAllUsers: boolean
  toggleShowAllUsers: () => void
}

/**
 * A consolidated Knowledge Base Selection Modal that includes the "All Users" toggle
 * and can be used across all features (Review, Generate, Compare, Match, Chatbot)
 */
const KnowledgeBaseSelectionModal = ({
  isOpen,
  onClose,
  title,
  knowledgeBases,
  selectedKnowledgeBase,
  onSelectionChange,
  showAllUsers,
  toggleShowAllUsers,
}: KnowledgeBaseSelectionModalProps) => {
  const { t } = useTranslation()

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
          {/* All Users Toggle */}
          <HStack justifyContent="flex-end" mt={2}>
            <Tooltip
              content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
            >
              <HStack gap={2}>
                <HStack gap={1} align="center">
                  <Text fontSize="xs" color="gray.500">
                    {t("archive.allUsers")}
                  </Text>
                  <HelpTooltip helpKey="allUsersToggle" />
                </HStack>
                <Switch.Root
                  key={`switch-${showAllUsers}`}
                  size="sm"
                  colorPalette="blue"
                  checked={showAllUsers}
                >
                  <Switch.HiddenInput
                    checked={showAllUsers}
                    onChange={toggleShowAllUsers}
                  />
                  <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                    <Switch.Thumb />
                  </Switch.Control>
                </Switch.Root>
              </HStack>
            </Tooltip>
          </HStack>
        </Card.Header>
        <Card.Body>
          <KnowledgeBaseTable
            knowledgeBases={knowledgeBases}
            selectedKnowledgeBase={selectedKnowledgeBase}
            onSelectionChange={onSelectionChange}
          />
        </Card.Body>
        <Card.Footer justifyContent="flex-end">
          <ConfirmButton onClick={onClose} size="md">
            Done
          </ConfirmButton>
        </Card.Footer>
      </Card.Root>
    </div>
  )
}

export default KnowledgeBaseSelectionModal
