import {
  Button,
  HStack,
  VStack,
  Input,
  Textarea,
  Dialog,
  Portal,
  CloseButton,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { ReportGenieOutline } from "../../client"
import { InteractiveList } from "../ui/interactive-list"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"

interface OutlineModalProps {
  isOpen: boolean
  onClose: () => void
  editingOutline: ReportGenieOutline | null
  onSave: () => void
  outlineName: string
  setOutlineName: (name: string) => void
  outlineDescription: string
  setOutlineDescription: (description: string) => void
  sections: string
  onSectionsChange: (sections: string) => void
}

const OutlineModal = ({
  isOpen,
  onClose,
  editingOutline,
  onSave,
  outlineName,
  setOutlineName,
  outlineDescription,
  setOutlineDescription,
  sections,
  onSectionsChange,
}: OutlineModalProps) => {
  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="2xl" maxH="80vh">
            <Dialog.Header>
              <Dialog.Title>{editingOutline ? "Edit Outline" : "Create New Outline"}</Dialog.Title>
              <Dialog.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Dialog.CloseTrigger>
            </Dialog.Header>

            <Dialog.Body>
              <VStack gap={4} align="stretch">
                <Field label="Outline Name" required>
                  <Input
                    value={outlineName}
                    onChange={(e) => setOutlineName(e.target.value)}
                    placeholder="Enter outline name"
                  />
                </Field>

                <Field label="Description">
                  <Textarea
                    value={outlineDescription}
                    onChange={(e) => setOutlineDescription(e.target.value)}
                    placeholder="Enter outline description"
                    resize="vertical"
                  />
                </Field>

                <Field label="Sections" required>
                  <InteractiveList
                    value={sections}
                    onChange={onSectionsChange}
                    placeholder="Add a section (e.g. Introduction, Methods, Results)"
                  />
                </Field>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <HStack gap={3}>
                <CancelButton onClick={onClose} size="md">
                  Cancel
                </CancelButton>
                <ConfirmButton onClick={onSave} size="md">
                  {editingOutline ? "Update Outline" : "Create Outline"}
                </ConfirmButton>
              </HStack>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default OutlineModal
