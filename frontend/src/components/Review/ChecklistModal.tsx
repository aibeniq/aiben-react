import { HStack, VStack, Input, Textarea, Dialog, Portal, CloseButton } from "@chakra-ui/react"
import { Field } from "../ui/field"
import { VeraDocChecklist } from "../../client"
import QuestionItem from "./QuestionItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { css } from "@emotion/react"

interface ChecklistModalProps {
  isOpen: boolean
  onClose: () => void
  editingChecklist: VeraDocChecklist | null
  onSave: () => void
  checklistName: string
  setChecklistName: (name: string) => void
  checklistDescription: string
  setChecklistDescription: (description: string) => void
  questionsList: string[]
  updateQuestion: (index: number, value: string) => void
  handleQuestionBlur: (index: number, value: string) => void
  removeQuestion: (index: number) => void
  moveQuestionUp: (index: number) => void
  moveQuestionDown: (index: number) => void
}

const ChecklistModal = ({
  isOpen,
  onClose,
  editingChecklist,
  onSave,
  checklistName,
  setChecklistName,
  checklistDescription,
  setChecklistDescription,
  questionsList,
  updateQuestion,
  handleQuestionBlur,
  removeQuestion,
  moveQuestionUp,
  moveQuestionDown,
}: ChecklistModalProps) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={(e) => (e.open ? null : onClose())}>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="4xl" maxH="90vh">
            <Dialog.Header>
              <Dialog.Title>
                {editingChecklist ? "Edit Checklist" : "Create New Checklist"}
              </Dialog.Title>
            </Dialog.Header>

            <Dialog.Body>
              <VStack align="stretch" gap={4}>
                <VStack align="stretch" gap={4}>
                  <VStack align="stretch" gap={4} flex="1">
                    <Field label="Checklist Name" required>
                      <Input
                        value={checklistName}
                        onChange={(e) => setChecklistName(e.target.value)}
                        placeholder="Enter checklist name"
                      />
                    </Field>

                    <Field label="Checklist Description">
                      <Textarea
                        value={checklistDescription}
                        onChange={(e) => setChecklistDescription(e.target.value)}
                        placeholder="Enter checklist description"
                        resize="vertical"
                      />
                    </Field>
                  </VStack>

                  <Field label="Questions" required py={0} flex="1">
                    <VStack
                      align="stretch"
                      gap={0}
                      display="flex"
                      flexDirection="column"
                      width="100%"
                      maxH="260px"
                      overflowY="scroll"
                      css={{
                        "&:after": {
                          content: '""',
                          position: "absolute",
                          bottom: 0,
                          left: 0,
                          right: 0,
                          height: "25px",
                          background: "linear-gradient(to top, white, transparent)",
                          pointerEvents: "none",
                        },
                      }}
                    >
                      {questionsList.map((question, index) => (
                        <QuestionItem
                          key={index}
                          index={index}
                          question={question}
                          onUpdate={updateQuestion}
                          onBlur={handleQuestionBlur}
                          onRemove={removeQuestion}
                          onMoveUp={moveQuestionUp}
                          onMoveDown={moveQuestionDown}
                          canRemove={questionsList.length > 1 && question.trim() !== ""}
                          totalQuestions={questionsList.length}
                        />
                      ))}
                    </VStack>
                  </Field>
                </VStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <CancelButton onClick={onClose} size="md">
                  Cancel
                </CancelButton>
              </Dialog.ActionTrigger>
              <ConfirmButton onClick={onSave} size="md">
                {editingChecklist ? "Update Checklist" : "Create Checklist"}
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

export default ChecklistModal
