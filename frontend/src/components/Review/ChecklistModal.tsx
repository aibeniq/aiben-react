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
import { VeraDocChecklist } from "../../client"
import QuestionItem from "./QuestionItem"

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
                <HStack align="stretch" gap={4}>
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
                      maxH="300px"
                      overflowY="auto"
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
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <Dialog.ActionTrigger asChild>
                <Button
                  variant="outline"
                  onClick={onClose}
                  bg="transparent"
                  color="gray.500"
                  border="1px solid"
                  borderColor="gray.500"
                  _hover={{ bg: "gray.100" }}
                >
                  Cancel
                </Button>
              </Dialog.ActionTrigger>
              <Button
                onClick={onSave}
                bg="rgba(0, 65, 72, 0.9)"
                color="white"
                _hover={{ bg: "rgba(0, 65, 72, 0.8)" }}
              >
                {editingChecklist ? "Update Checklist" : "Create Checklist"}
              </Button>
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
