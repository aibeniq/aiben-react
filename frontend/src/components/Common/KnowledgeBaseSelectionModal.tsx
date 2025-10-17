import type { KnowledgeBasePublic } from "@/client"
import { CloseButton, Dialog, HStack, Portal, Switch, Text } from "@chakra-ui/react"
import { useTranslation } from "react-i18next"
import ConfirmButton from "../ui/confirm-button"
import HelpTooltip from "../ui/help-tooltip"
import { Tooltip } from "../ui/tooltip"
import KnowledgeBaseTable from "./KnowledgeBaseTable"

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

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={({ open }) => !open && onClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner style={{ zIndex: 2000 }}>
          <Dialog.Content maxW="4xl" maxH="80vh">
            <Dialog.Header>
              <HStack justify="space-between" align="center" w="full">
                <Dialog.Title>{title}</Dialog.Title>
                <Dialog.CloseTrigger asChild>
                  <CloseButton size="sm" />
                </Dialog.CloseTrigger>
              </HStack>
              {/* All Users Toggle */}
              <HStack justifyContent="flex-end" mt={2}>
                <Tooltip
                  content={
                    showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")
                  }
                  contentProps={{ zIndex: 2100 }}
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
                      <Switch.HiddenInput checked={showAllUsers} onChange={toggleShowAllUsers} />
                      <Switch.Control data-state={showAllUsers ? "checked" : "unchecked"}>
                        <Switch.Thumb />
                      </Switch.Control>
                    </Switch.Root>
                  </HStack>
                </Tooltip>
              </HStack>
            </Dialog.Header>
            <Dialog.Body>
              <KnowledgeBaseTable
                knowledgeBases={knowledgeBases}
                selectedKnowledgeBase={selectedKnowledgeBase}
                onSelectionChange={onSelectionChange}
              />
            </Dialog.Body>
            <Dialog.Footer justifyContent="flex-end">
              <ConfirmButton onClick={onClose} size="md">
                {t("buttons.done")}
              </ConfirmButton>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default KnowledgeBaseSelectionModal
