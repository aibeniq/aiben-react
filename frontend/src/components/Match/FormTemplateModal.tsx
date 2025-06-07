import { HStack, VStack, Input, Textarea, Dialog, Portal, CloseButton } from "@chakra-ui/react"
import { Field } from "../ui/field"
import { FormConnectForm } from "../../client"
import { InteractiveList } from "../ui/interactive-list"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"

interface FormTemplateModalProps {
  isOpen: boolean
  onClose: () => void
  editingForm: FormConnectForm | null
  onSave: () => void
  formName: string
  setFormName: (name: string) => void
  formDescription: string
  setFormDescription: (description: string) => void
  fields: string
  onFieldsChange: (fields: string) => void
}

const FormTemplateModal = ({
  isOpen,
  onClose,
  editingForm,
  onSave,
  formName,
  setFormName,
  formDescription,
  setFormDescription,
  fields,
  onFieldsChange,
}: FormTemplateModalProps) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={(e) => (e.open ? null : onClose())}>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="4xl" maxH="90vh">
            <Dialog.Header>
              <Dialog.Title>
                {editingForm ? "Edit Form Template" : "Create New Form Template"}
              </Dialog.Title>
            </Dialog.Header>

            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                <HStack align="stretch" gap={4}>
                  <VStack align="stretch" gap={4} flex="1">
                    <Field label="Form Template Name" required>
                      <Input
                        value={formName}
                        onChange={(e) => setFormName(e.target.value)}
                        placeholder="Enter form template name"
                      />
                    </Field>

                    <Field label="Form Template Description">
                      <Textarea
                        value={formDescription}
                        onChange={(e) => setFormDescription(e.target.value)}
                        placeholder="Enter form template description"
                        resize="vertical"
                      />
                    </Field>
                  </VStack>

                  <Field label="Form Fields" required py={0} flex="1">
                    <VStack
                      align="stretch"
                      gap={2}
                      display="flex"
                      flexDirection="column"
                      width="100%"
                      maxH="300px"
                      overflowY="auto"
                    >
                      <InteractiveList
                        value={fields}
                        onChange={onFieldsChange}
                        placeholder="Add a field name (e.g. First Name, Address, SSN)"
                      />
                    </VStack>
                  </Field>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <CancelButton onClick={onClose} size="md">
                  Cancel
                </CancelButton>
              </Dialog.ActionTrigger>
              <ConfirmButton onClick={onSave} size="md">
                {editingForm ? "Update Form Template" : "Create Form Template"}
              </ConfirmButton>
            </Dialog.Footer>

            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  )
}

export default FormTemplateModal
