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
import { FiCopy, FiCheck, FiEdit3, FiSave, FiX } from "react-icons/fi"
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
  updateQuestionsList: (newQuestions: string[]) => void // Add this new prop
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
  updateQuestionsList, // Add this new prop
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

  // State for editing suggestions
  const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
  const [editingModes, setEditingModes] = useState<Set<number>>(new Set())

  // State for expanding current answers
  const [expandedAnswers, setExpandedAnswers] = useState<Set<number>>(new Set())

  // Generate questions state
  const [generating, setGenerating] = useState(false)
  const [questionsKey, setQuestionsKey] = useState(0)

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

  const startEditingSuggestion = (index: number) => {
    const newEditingModes = new Set(editingModes)
    newEditingModes.add(index)
    setEditingModes(newEditingModes)

    // Initialize with the current suggested question if not already editing
    if (!editingSuggestions.has(index)) {
      const newEditingSuggestions = new Map(editingSuggestions)
      newEditingSuggestions.set(index, suggestions[index].suggested_question)
      setEditingSuggestions(newEditingSuggestions)
    }
  }

  const cancelEditingSuggestion = (index: number) => {
    const newEditingModes = new Set(editingModes)
    newEditingModes.delete(index)
    setEditingModes(newEditingModes)

    // Reset to original suggestion
    const newEditingSuggestions = new Map(editingSuggestions)
    newEditingSuggestions.set(index, suggestions[index].suggested_question)
    setEditingSuggestions(newEditingSuggestions)
  }

  const saveEditedSuggestion = (index: number) => {
    const newEditingModes = new Set(editingModes)
    newEditingModes.delete(index)
    setEditingModes(newEditingModes)
    // The edited text is already saved in editingSuggestions map
  }

  const updateEditingSuggestion = (index: number, value: string) => {
    const newEditingSuggestions = new Map(editingSuggestions)
    newEditingSuggestions.set(index, value)
    setEditingSuggestions(newEditingSuggestions)
  }

  const getSuggestionText = (index: number) => {
    return editingSuggestions.get(index) || suggestions[index]?.suggested_question || ""
  }

  const toggleAnswerExpansion = (index: number) => {
    const newExpanded = new Set(expandedAnswers)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedAnswers(newExpanded)
  }

  const handleApplySuggestions = () => {
    if (suggestions.length === 0) return

    // Create a map of original questions to their suggestions
    const suggestionMap = new Map<string, string>()

    suggestions.forEach((suggestion, index) => {
      if (acceptedSuggestions.has(index) && suggestion.needs_revision) {
        // Use edited suggestion if available, otherwise use original suggestion
        suggestionMap.set(suggestion.original_question, getSuggestionText(index))
      }
    })

    // Update the questions list by finding and replacing the original questions
    const updatedQuestions = questionsList.map((question) => {
      const trimmedQuestion = question.trim()
      if (trimmedQuestion && suggestionMap.has(trimmedQuestion)) {
        return suggestionMap.get(trimmedQuestion) || question
      }
      return question
    })

    // Update the questions list with the optimized questions
    updateQuestionsList(updatedQuestions)

    showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)

    // Clear optimization state
    setFileItems([])
    setSuggestions([])
    setAcceptedSuggestions(new Set())
    setEditingSuggestions(new Map())
    setEditingModes(new Set())
    setExpandedAnswers(new Set())
    setShowOptimizeSection(false)
  }

  const handleGenerateQuestions = async () => {
    if (!checklistDescription.trim()) {
      showErrorToast("Please enter a checklist description first")
      return
    }

    // Validate minimum length requirement
    if (checklistDescription.trim().length < 10) {
      showErrorToast("Please enter a more detailed description (at least 10 characters)")
      return
    }

    setGenerating(true)

    try {
      const response = await VeradocService.generateQuestions({
        requestBody: {
          description: checklistDescription.trim(),
          checklist_type: "general",
          // Remove num_questions - let LLM decide based on description complexity
        },
      })

      // Replace current questions with generated ones
      const generatedQuestions = response.questions || []
      if (generatedQuestions.length > 0) {
        // Create new questions array with generated questions plus one empty question at the end
        const newQuestions = [...generatedQuestions, ""]

        // Replace the entire questions list
        updateQuestionsList(newQuestions)

        // Force re-render of question items
        setQuestionsKey((prev) => prev + 1)

        showSuccessToast(`Generated ${generatedQuestions.length} questions from description`)
      } else {
        showErrorToast("No questions were generated. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error generating questions:", error)

      // Handle specific error types
      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to generate questions.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to generate questions: ${error.message || "Unknown error"}`)
      }
    } finally {
      setGenerating(false)
    }
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

                    <Field
                      label={
                        <HStack justify="space-between" w="full">
                          <span>Checklist Description</span>
                          <Button
                            size="xs"
                            onClick={handleGenerateQuestions}
                            disabled={
                              !checklistDescription.trim() ||
                              checklistDescription.trim().length < 10 ||
                              generating
                            }
                            loading={generating}
                            variant="outline"
                            colorPalette="green"
                            title={
                              checklistDescription.trim().length < 10
                                ? "Description must be at least 10 characters to generate questions"
                                : "Generate questions based on the description"
                            }
                          >
                            {generating ? "Generating..." : "Generate Questions"}
                          </Button>
                        </HStack>
                      }
                    >
                      <Textarea
                        value={checklistDescription}
                        onChange={(e) => setChecklistDescription(e.target.value)}
                        placeholder="Enter checklist description to auto-generate questions (minimum 10 characters)..."
                        resize="vertical"
                        rows={3}
                      />
                      {checklistDescription.trim().length > 0 &&
                        checklistDescription.trim().length < 10 && (
                          <Text fontSize="xs" color="orange.600">
                            Description needs at least {10 - checklistDescription.trim().length}{" "}
                            more characters to generate questions
                          </Text>
                        )}
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
                          key={`${questionsKey}-${index}`}
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
                                            <HStack justify="space-between" mb={1}>
                                              <Text fontSize="xs" fontWeight="medium">
                                                Suggested:
                                              </Text>
                                              {!editingModes.has(index) ? (
                                                <IconButton
                                                  size="xs"
                                                  variant="ghost"
                                                  aria-label="Edit suggestion"
                                                  onClick={() => startEditingSuggestion(index)}
                                                >
                                                  <FiEdit3 size={10} />
                                                </IconButton>
                                              ) : (
                                                <HStack gap={1}>
                                                  <IconButton
                                                    size="xs"
                                                    variant="ghost"
                                                    colorPalette="green"
                                                    aria-label="Save changes"
                                                    onClick={() => saveEditedSuggestion(index)}
                                                  >
                                                    <FiSave size={10} />
                                                  </IconButton>
                                                  <IconButton
                                                    size="xs"
                                                    variant="ghost"
                                                    colorPalette="red"
                                                    aria-label="Cancel editing"
                                                    onClick={() => cancelEditingSuggestion(index)}
                                                  >
                                                    <FiX size={10} />
                                                  </IconButton>
                                                </HStack>
                                              )}
                                            </HStack>

                                            {editingModes.has(index) ? (
                                              <Textarea
                                                value={getSuggestionText(index)}
                                                onChange={(e) =>
                                                  updateEditingSuggestion(index, e.target.value)
                                                }
                                                fontSize="xs"
                                                p={2}
                                                bg="blue.50"
                                                borderRadius="sm"
                                                border="1px solid"
                                                borderColor="blue.200"
                                                resize="vertical"
                                                rows={2}
                                              />
                                            ) : (
                                              <Text
                                                fontSize="xs"
                                                p={2}
                                                bg="blue.50"
                                                borderRadius="sm"
                                                border="1px solid"
                                                borderColor="blue.200"
                                                cursor="pointer"
                                                onClick={() => startEditingSuggestion(index)}
                                                _hover={{ bg: "blue.100" }}
                                              >
                                                {getSuggestionText(index)}
                                              </Text>
                                            )}
                                          </Box>

                                          <Box>
                                            <Text fontSize="xs" fontWeight="medium" mb={1}>
                                              Reason:
                                            </Text>
                                            <Text fontSize="xs" color="gray.600">
                                              {suggestion.reason}
                                            </Text>
                                          </Box>

                                          <Box>
                                            <Text fontSize="xs" fontWeight="medium" mb={1}>
                                              Current Answer (why this needs optimization):
                                            </Text>
                                            <Box
                                              p={2}
                                              bg="orange.50"
                                              borderRadius="sm"
                                              border="1px solid"
                                              borderColor="orange.200"
                                            >
                                              <Text fontSize="xs" color="gray.600">
                                                {expandedAnswers.has(index)
                                                  ? suggestion.current_answer
                                                  : suggestion.current_answer.substring(0, 300)}
                                                {!expandedAnswers.has(index) &&
                                                suggestion.current_answer.length > 300
                                                  ? "..."
                                                  : ""}
                                              </Text>
                                              {suggestion.current_answer.length > 300 && (
                                                <Button
                                                  size="xs"
                                                  variant="ghost"
                                                  mt={1}
                                                  onClick={() => toggleAnswerExpansion(index)}
                                                  colorPalette="orange"
                                                >
                                                  {expandedAnswers.has(index)
                                                    ? "Show Less"
                                                    : "Show More"}
                                                </Button>
                                              )}
                                            </Box>
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
