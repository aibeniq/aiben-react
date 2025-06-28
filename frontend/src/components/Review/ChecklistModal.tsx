import { useState } from "react"
import {
  VStack,
  Input,
  Textarea,
  Dialog,
  Portal,
  CloseButton,
  HStack,
  IconButton,
  Button,
  Box,
  Text,
  Spinner,
  Card,
  Separator,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { FiCopy, FiCheck } from "react-icons/fi"
import { VeraDocChecklist, VeradocService } from "../../client"
import QuestionItem from "./QuestionItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload from "../Common/FileUpload"

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
  knowledgeBases?: any[]
  selectedKnowledgeBase?: any
}

interface ChecklistSuggestion {
  original_question: string
  suggested_question: string
  reason: string
  current_answer: string
  needs_revision: boolean
}

interface FileItem {
  file: File
  isHandwritten: boolean
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
  knowledgeBases,
  selectedKnowledgeBase,
}: ChecklistModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Optimization state
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [optimizing, setOptimizing] = useState(false)
  const [suggestions, setSuggestions] = useState<ChecklistSuggestion[]>([])
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
  const [showOptimizeSection, setShowOptimizeSection] = useState(false)

  const handleCopyQuestions = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Filter out empty questions and join with newlines
    const nonEmptyQuestions = questionsList.filter((q) => q.trim() !== "")

    if (nonEmptyQuestions.length === 0) {
      showErrorToast("No questions to copy")
      return
    }

    try {
      await navigator.clipboard.writeText(nonEmptyQuestions.join("\n"))
      showSuccessToast("Questions copied to clipboard!")
    } catch (error) {
      console.error("Error copying questions:", error)
      showErrorToast("Failed to copy questions to clipboard")
    }
  }

  const handleOptimize = async () => {
    if (questionsList.length === 0 || questionsList.every((q) => !q.trim())) {
      showErrorToast("No questions to optimize")
      return
    }

    if (!selectedKnowledgeBase) {
      showErrorToast("Please select a knowledge base")
      return
    }

    if (fileItems.length === 0) {
      showErrorToast("Please upload a test document")
      return
    }

    setOptimizing(true)
    setSuggestions([])

    try {
      const validItems = fileItems.filter((item) => item.file.size > 0)
      const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)

      // Join current questions
      const currentQuestions = questionsList.filter((q) => q.trim()).join("\n")

      const response = await VeradocService.optimizeChecklist({
        questions: currentQuestions,
        knowledgeBaseId: selectedKnowledgeBase.id,
        formData: {
          files: regularFiles,
        },
      })

      setSuggestions(response.suggestions || [])

      if (response.suggestions && response.suggestions.length > 0) {
        const optimizationCount = response.suggestions.filter((s) => s.needs_revision).length
        if (optimizationCount > 0) {
          showSuccessToast(`Found ${optimizationCount} questions that could be optimized`)
        } else {
          showSuccessToast("All questions are already well-optimized!")
        }
      }
    } catch (error: any) {
      console.error("Error optimizing checklist:", error)
      showErrorToast(`Failed to optimize checklist: ${error.message || "Unknown error"}`)
    } finally {
      setOptimizing(false)
    }
  }

  const toggleSuggestion = (index: number) => {
    const newAccepted = new Set(acceptedSuggestions)
    if (newAccepted.has(index)) {
      newAccepted.delete(index)
    } else {
      newAccepted.add(index)
    }
    setAcceptedSuggestions(newAccepted)
  }

  const handleApplySuggestions = () => {
    if (suggestions.length === 0) return

    // Update questions in real-time based on accepted suggestions
    suggestions.forEach((suggestion, index) => {
      if (acceptedSuggestions.has(index) && suggestion.needs_revision) {
        updateQuestion(index, suggestion.suggested_question)
      }
    })

    showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)

    // Clear optimization state
    setFileItems([])
    setSuggestions([])
    setAcceptedSuggestions(new Set())
    setShowOptimizeSection(false)
  }
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

                  <Field
                    label={
                      <HStack justify="space-between" w="full">
                        <span>Questions *</span>
                        <HStack gap={2}>
                          {/* Show optimization button if knowledge base is available */}
                          {knowledgeBases && selectedKnowledgeBase && (
                            <Button
                              size="xs"
                              onClick={() => setShowOptimizeSection(!showOptimizeSection)}
                              variant="outline"
                              colorPalette="blue"
                            >
                              {showOptimizeSection ? "Hide Optimize" : "Optimize"}
                            </Button>
                          )}
                          <IconButton
                            size="xs"
                            onClick={handleCopyQuestions}
                            variant="ghost"
                            aria-label="Copy questions as text"
                            title="Copy all questions as text"
                          >
                            <FiCopy size={12} />
                          </IconButton>
                        </HStack>
                      </HStack>
                    }
                    py={0}
                    flex="1"
                  >
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

                  {/* Optimization Section */}
                  {showOptimizeSection && (
                    <VStack align="stretch" gap={4} p={4} bg="gray.50" borderRadius="md">
                      <Text fontWeight="medium" fontSize="sm">
                        Optimize Questions
                      </Text>

                      <Box>
                        <Text mb={2} fontSize="sm">
                          Upload a document that SHOULD meet all checklist requirements:
                        </Text>
                        <FileUpload
                          files={fileItems}
                          onFilesChange={setFileItems}
                          showHandwrittenToggle={false}
                        />
                      </Box>

                      <HStack justify="space-between">
                        <Text fontSize="xs" color="gray.600">
                          Knowledge Base: {selectedKnowledgeBase?.title || "None selected"}
                        </Text>
                        <Button
                          size="sm"
                          onClick={handleOptimize}
                          disabled={fileItems.length === 0 || !selectedKnowledgeBase || optimizing}
                          loading={optimizing}
                          colorPalette="blue"
                        >
                          {optimizing ? "Analyzing..." : "Analyze & Suggest"}
                        </Button>
                      </HStack>

                      {optimizing && (
                        <Box textAlign="center" py={4}>
                          <Spinner size="md" mb={2} />
                          <Text fontSize="sm">Running optimization analysis...</Text>
                        </Box>
                      )}

                      {suggestions.length > 0 && !optimizing && (
                        <VStack gap={3} align="stretch">
                          <Separator />
                          <HStack justify="space-between">
                            <Text fontSize="sm" fontWeight="bold">
                              Optimization Suggestions
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {suggestions.filter((s) => s.needs_revision).length} questions need
                              optimization
                            </Text>
                          </HStack>

                          <Box maxH="300px" overflow="auto" pr={2}>
                            <VStack gap={3} align="stretch">
                              {suggestions.map((suggestion, index) => (
                                <Card.Root
                                  key={index}
                                  variant={suggestion.needs_revision ? "elevated" : "subtle"}
                                  size="sm"
                                >
                                  <Card.Body>
                                    <VStack gap={2} align="stretch">
                                      <HStack justify="space-between">
                                        <Text fontWeight="bold" fontSize="xs" color="gray.600">
                                          Question {index + 1}
                                        </Text>
                                        {suggestion.needs_revision && (
                                          <Button
                                            size="xs"
                                            variant={
                                              acceptedSuggestions.has(index) ? "solid" : "outline"
                                            }
                                            colorPalette={
                                              acceptedSuggestions.has(index) ? "green" : "blue"
                                            }
                                            onClick={() => toggleSuggestion(index)}
                                          >
                                            {acceptedSuggestions.has(index) ? (
                                              <>
                                                <FiCheck size={12} /> Accepted
                                              </>
                                            ) : (
                                              "Accept"
                                            )}
                                          </Button>
                                        )}
                                      </HStack>

                                      <Box>
                                        <Text fontSize="xs" fontWeight="medium" mb={1}>
                                          Original:
                                        </Text>
                                        <Text fontSize="xs" p={2} bg="gray.100" borderRadius="sm">
                                          {suggestion.original_question}
                                        </Text>
                                      </Box>

                                      {suggestion.needs_revision ? (
                                        <>
                                          <Box>
                                            <Text fontSize="xs" fontWeight="medium" mb={1}>
                                              Suggested:
                                            </Text>
                                            <Text
                                              fontSize="xs"
                                              p={2}
                                              bg="blue.50"
                                              borderRadius="sm"
                                              border="1px solid"
                                              borderColor="blue.200"
                                            >
                                              {suggestion.suggested_question}
                                            </Text>
                                          </Box>

                                          <Box>
                                            <Text fontSize="xs" fontWeight="medium" mb={1}>
                                              Reason:
                                            </Text>
                                            <Text fontSize="xs" color="gray.600">
                                              {suggestion.reason}
                                            </Text>
                                          </Box>
                                        </>
                                      ) : (
                                        <Text fontSize="xs" color="green.600" fontWeight="medium">
                                          ✓ Already well-optimized
                                        </Text>
                                      )}
                                    </VStack>
                                  </Card.Body>
                                </Card.Root>
                              ))}
                            </VStack>
                          </Box>

                          <Button
                            size="sm"
                            colorPalette="blue"
                            onClick={handleApplySuggestions}
                            disabled={acceptedSuggestions.size === 0}
                          >
                            Apply {acceptedSuggestions.size} Suggestion
                            {acceptedSuggestions.size !== 1 ? "s" : ""}
                          </Button>
                        </VStack>
                      )}
                    </VStack>
                  )}
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
