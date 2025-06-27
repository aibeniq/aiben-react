import { HStack, VStack, Input, Textarea, Dialog, Portal, CloseButton } from "@chakra-ui/react"
import { Field } from "../ui/field"
import { Box } from "@chakra-ui/react"
import { ReportGenieOutline } from "../../client"
import SectionEditor from "./SectionEditor" // Import SectionEditor instead of InteractiveList
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
  console.log("Parent: sections prop value", sections)

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && onClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="4xl" maxH="80vh">
            <Dialog.Header>
              <Dialog.Title>{editingOutline ? "Edit Outline" : "Create New Outline"}</Dialog.Title>
              <Dialog.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Dialog.CloseTrigger>
            </Dialog.Header>

            <Dialog.Body overflowY="auto">
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
                  <Box
                    border="1px solid"
                    borderColor="gray.200"
                    borderRadius="md"
                    p={3}
                    width="full"
                  >
                    <SectionEditor sections={sections} onSectionsChange={onSectionsChange} />
                  </Box>
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
