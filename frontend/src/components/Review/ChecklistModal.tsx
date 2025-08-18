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
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { Tooltip } from "../ui/tooltip"
import { FiCopy } from "react-icons/fi"
import { VeraDocChecklist, VeradocService } from "../../client"
import QuestionItem from "./QuestionItem"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import useCustomToast from "../../hooks/useCustomToast"
import OptimizeChecklistModal from "./OptimizeChecklistModal"
import FileUpload from "../Common/FileUpload"
import SearchModeToggle from "../Common/SearchModeToggle"
import { copyToClipboard } from "../../utils/copyToClipboard"

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
  questionsData: QuestionData[]
  updateQuestion: (index: number, value: string) => void
  updateQuestionsList: (newQuestions: string[]) => void
  updateQuestionsData: (newData: QuestionData[]) => void
  handleQuestionBlur: (index: number, value: string) => void
  removeQuestion: (index: number) => void
  moveQuestionUp: (index: number) => void
  moveQuestionDown: (index: number) => void
  knowledgeBases?: any[]
  selectedKnowledgeBase?: any
}

interface QuestionData {
  id: string
  text: string
  consultDocuments: boolean
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
  questionsData,
  updateQuestion,
  updateQuestionsList,
  updateQuestionsData,
  handleQuestionBlur,
  removeQuestion,
  moveQuestionUp,
  moveQuestionDown,
  knowledgeBases,
  selectedKnowledgeBase,
}: ChecklistModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Validation state
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({})

  // Validation function
  const validateForm = () => {
    const errors: {[key: string]: string} = {}
    
    if (!checklistName.trim()) {
      errors.name = "Checklist name is required"
    } else if (checklistName.trim().length < 3) {
      errors.name = "Checklist name must be at least 3 characters long"
    }
    
    // Description is optional - no validation required
    
    if (questionsList.length === 0 || questionsList.every(q => !q.trim())) {
      errors.questions = "At least one question is required"
    }
    
    setValidationErrors(errors)
    
    // Show the first error as a toast
    const firstError = Object.values(errors)[0]
    if (firstError) {
      showErrorToast(firstError)
      return false
    }
    
    return true
  }

  // Clear validation errors when user starts typing
  const handleNameChange = (value: string) => {
    setChecklistName(value)
    if (validationErrors.name) {
      setValidationErrors(prev => ({ ...prev, name: '' }))
    }
  }

  const handleDescriptionChange = (value: string) => {
    setChecklistDescription(value)
    if (validationErrors.description) {
      setValidationErrors(prev => ({ ...prev, description: '' }))
    }
  }

  // Enhanced save handler with validation
  const handleSave = () => {
    if (!validateForm()) {
      return // Stop execution if validation fails
    }
    
    // Call the parent's onSave function if validation passes
    onSave()
  }

  // Handler for consult documents toggle
  const handleConsultDocumentsChange = (id: string, value: boolean) => {
    console.log("Toggle changed for question ID:", id, "new value:", value)
    const newData = questionsData.map((item) =>
      item.id === id ? { ...item, consultDocuments: value } : item,
    )
    console.log("Updated questionsData:", newData)
    updateQuestionsData(newData)
  }

  // Optimize modal state
  const [showOptimizeModal, setShowOptimizeModal] = useState(false)

  // Suggest questions state
  const [suggesting, setSuggesting] = useState(false)
  const [questionsKey, setQuestionsKey] = useState(0)
  const [referenceFiles, setReferenceFiles] = useState<FileItem[]>([])
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<any>(null)
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")

  const handleCopyQuestions = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Filter out empty questions and join with newlines
    const nonEmptyQuestions = questionsList.filter((q) => q.trim() !== "")
    const questionsText = nonEmptyQuestions.join("\n")

    if (nonEmptyQuestions.length === 0) {
      showErrorToast("No questions to copy")
      return
    }

    try {
      await copyToClipboard(questionsText)
      showSuccessToast("Questions copied to clipboard")
    } catch (error) {
      console.error("Error copying questions:", error)
      showErrorToast("Failed to copy questions to clipboard")
    }
  }

  const handleOptimizeClick = () => {
    if (!selectedKnowledgeBase) {
      showErrorToast("Please select a knowledge base first to optimize the checklist.")
      return
    }

    if (questionsList.length === 0 || questionsList.every((q) => !q.trim())) {
      showErrorToast("Please add some questions to the checklist before optimizing.")
      return
    }

    setShowOptimizeModal(true)
  }

  const handleOptimized = (optimizedQuestions: string[]) => {
    updateQuestionsList(optimizedQuestions)
    
    // Clear questions validation error if it exists
    if (validationErrors.questions) {
      setValidationErrors(prev => ({ ...prev, questions: '' }))
    }
    
    showSuccessToast(`Applied ${optimizedQuestions.length} optimized questions`)
  }

  const handleSuggestQuestions = async () => {
    if (!checklistDescription.trim()) {
      showErrorToast("Please enter a description")
      return
    }

    if (checklistDescription.trim().length < 10) {
      showErrorToast("Description must be at least 10 characters")
      return
    }

    setSuggesting(true)

    try {
      let response

      if (referenceMode === "files" && referenceFiles.length > 0) {
        // Use fetch directly for file uploads with multipart/form-data
        const formData = new FormData()
        formData.append("description", checklistDescription.trim())
        formData.append("checklist_type", "general")
        formData.append("search_mode", searchMode)

        // Add files to formData
        referenceFiles.forEach((item) => {
          formData.append("files", item.file)
        })

        // Use direct fetch for file upload
        const token = localStorage.getItem("access_token")
        const headers: any = {}

        if (token) {
          headers["Authorization"] = `Bearer ${token}`
        }

        const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const apiUrl = `${baseUrl}/api/v1/veradoc/generate-questions-with-files`

        console.log("Suggesting questions with files - API URL:", apiUrl)

        const apiResponse = await fetch(apiUrl, {
          method: "POST",
          headers,
          body: formData,
        })

        if (!apiResponse.ok) {
          throw new Error(`HTTP ${apiResponse.status}: ${apiResponse.statusText}`)
        }

        response = await apiResponse.json()
      } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use the SDK method with knowledge base reference
        response = await VeradocService.generateQuestions({
          requestBody: {
            description: checklistDescription.trim(),
            checklist_type: "general",
            knowledge_base_id: referenceKnowledgeBase.id,
            search_mode: searchMode,
          },
        })
      } else {
        // Use the basic SDK method without references
        response = await VeradocService.generateQuestions({
          requestBody: {
            description: checklistDescription.trim(),
            checklist_type: "general",
            search_mode: searchMode,
          },
        })
      }

      // Replace current questions with suggested ones
      const suggestedQuestions = response.questions || []
      if (suggestedQuestions.length > 0) {
        // Create new questions array with suggested questions plus one empty question at the end
        const newQuestions = [...suggestedQuestions, ""]

        // Replace the entire questions list
        updateQuestionsList(newQuestions)

        // Clear questions validation error if it exists
        if (validationErrors.questions) {
          setValidationErrors(prev => ({ ...prev, questions: '' }))
        }

        // Force re-render of question items
        setQuestionsKey((prev) => prev + 1)

        let successMessage = `Suggested ${suggestedQuestions.length} questions from description`
        if (referenceMode === "files" && referenceFiles.length > 0) {
          successMessage += ` and ${referenceFiles.length} reference file(s)`
        } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
          successMessage += ` using Knowledge Base: ${referenceKnowledgeBase.title}`
        }

        showSuccessToast(successMessage)
      } else {
        showErrorToast("No questions were suggested. Please try a different description.")
      }
    } catch (error: any) {
      console.error("Error suggesting questions:", error)
      showErrorToast(`Failed to suggest questions: ${error.message || "Unknown error"}`)
    } finally {
      setSuggesting(false)
    }
  }

  const handleClose = () => {
    // Reset modal state
    setShowOptimizeModal(false)
    onClose()
  }

  const handleReferenceModeChange = (mode: "files" | "knowledge-base") => {
    setReferenceMode(mode)
    // Clear the other mode's data when switching
    if (mode === "files") {
      setReferenceKnowledgeBase(null)
    } else {
      setReferenceFiles([])
    }
  }

  return (
    <>
      <Dialog.Root open={isOpen} onOpenChange={onClose}>
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content maxW="6xl" maxH="90vh">
              <Dialog.Header>
                <Dialog.Title>
                  {editingChecklist ? "Edit Checklist" : "Create New Checklist"}
                </Dialog.Title>
              </Dialog.Header>

              <Dialog.Body>
                <VStack align="stretch" gap={4}>
                  {/* Two-column layout */}
                  <HStack align="stretch" gap={4}>
                    {/* Left Column - Basic Fields and Settings */}
                    <VStack align="stretch" gap={4} flex={1}>
                      {/* Basic Info */}
                      <Field label="Checklist Name" required invalid={!!validationErrors.name} errorText={validationErrors.name}>
                        <Input
                          value={checklistName}
                          onChange={(e) => handleNameChange(e.target.value)}
                          placeholder="Enter checklist name..."
                        />
                      </Field>

                      <Field label="Description" invalid={!!validationErrors.description} errorText={validationErrors.description}>
                        <Textarea
                          value={checklistDescription}
                          onChange={(e) => handleDescriptionChange(e.target.value)}
                          placeholder="Enter checklist description to auto-suggest questions (minimum 10 characters)..."
                          rows={4}
                        />
                        {checklistDescription.trim().length > 0 &&
                          checklistDescription.trim().length < 10 && (
                            <Text fontSize="xs" color="orange.600">
                              Description needs at least {10 - checklistDescription.trim().length}{" "}
                              more characters to suggest questions
                            </Text>
                          )}
                      </Field>

                      <SearchModeToggle
                        searchMode={searchMode}
                        onSearchModeChange={setSearchMode}
                      />

                      <Field label="Reference Documents (Optional)">
                        <VStack align="stretch" gap={3}>
                          <Text fontSize="sm" color="gray.600">
                            Upload reference documents or select a Knowledge Base to help the AI
                            suggest checklist questions.
                          </Text>

                          {/* Reference Mode Toggle */}
                          <HStack gap={2}>
                            <Button
                              size="sm"
                              variant={referenceMode === "files" ? "solid" : "outline"}
                              onClick={() => handleReferenceModeChange("files")}
                            >
                              Upload Files
                            </Button>
                            <Button
                              size="sm"
                              variant={referenceMode === "knowledge-base" ? "solid" : "outline"}
                              onClick={() => handleReferenceModeChange("knowledge-base")}
                              disabled={!knowledgeBases || knowledgeBases.length === 0}
                            >
                              Knowledge Base
                            </Button>
                          </HStack>

                          {/* Reference Mode Content */}
                          {referenceMode === "files" && (
                            <VStack align="stretch" gap={2}>
                              <Text fontSize="sm" color="gray.700" fontWeight="medium">
                                Provide reference documents for suggesting a checklist
                              </Text>
                              <FileUpload
                                files={referenceFiles}
                                onFilesChange={setReferenceFiles}
                                acceptedFileTypes={{
                                  "application/pdf": [".pdf"],
                                  "application/msword": [".doc"],
                                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                    [".docx"],
                                  "text/plain": [".txt"],
                                  "text/csv": [".csv"],
                                  "application/json": [".json"],
                                }}
                                maxFiles={5}
                              />
                            </VStack>
                          )}

                          {referenceMode === "knowledge-base" && (
                            <Box>
                              <select
                                style={{
                                  width: "100%",
                                  padding: "8px",
                                  borderRadius: "6px",
                                  border: "1px solid #e2e8f0",
                                }}
                                value={referenceKnowledgeBase?.id || ""}
                                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                                  const kb = knowledgeBases?.find((kb) => kb.id === e.target.value)
                                  setReferenceKnowledgeBase(kb || null)
                                }}
                              >
                                <option value="">Select a Knowledge Base...</option>
                                {knowledgeBases?.map((kb) => (
                                  <option key={kb.id} value={kb.id}>
                                    {kb.title}
                                  </option>
                                ))}
                              </select>
                              {!knowledgeBases || knowledgeBases.length === 0 ? (
                                <Text fontSize="sm" color="orange.600">
                                  No Knowledge Bases available. Create one first to use this feature.
                                </Text>
                              ) : null}
                            </Box>
                          )}

                          {checklistDescription.trim().length < 10 &&
                            checklistDescription.trim().length > 0 && (
                              <Text fontSize="sm" color="gray.500">
                                Description must be at least 10 characters to suggest questions
                              </Text>
                            )}
                        </VStack>
                      </Field>
                    </VStack>

                    {/* Right Column - Questions List */}
                    <VStack align="stretch" gap={4} flex={1} height="100%">
                      {/* Suggest and Optimize buttons above questions */}
                      <HStack justify="space-between" align="center">
                        <Text fontSize="md" fontWeight="medium">
                          Questions
                        </Text>
                        <HStack gap={2}>
                          <Button
                            size="xs"
                            onClick={handleSuggestQuestions}
                            loading={suggesting}
                            disabled={!checklistDescription.trim() || suggesting}
                            variant="outline"
                            colorPalette="green"
                          >
                            {suggesting ? "Suggesting..." : "Suggest"}
                          </Button>
                          {/* Always show optimization button with tooltip when disabled */}
                          <Tooltip
                            content={
                              !knowledgeBases || !selectedKnowledgeBase
                                ? "Knowledge Base must be selected for Optimize function to be enabled"
                                : "Optimize questions based on the selected Knowledge Base"
                            }
                          >
                            <Button
                              size="xs"
                              onClick={handleOptimizeClick}
                              variant="outline"
                              colorPalette="blue"
                              disabled={!knowledgeBases || !selectedKnowledgeBase}
                            >
                              Optimize
                            </Button>
                          </Tooltip>
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

                      {/* Questions List */}
                      <Box flex={1} minH={0}>
                        {validationErrors.questions && (
                          <Text fontSize="sm" color="red.500" mb={2}>
                            {validationErrors.questions}
                          </Text>
                        )}
                        <VStack gap={3} align="stretch" maxH="400px" overflow="auto">
                          {questionsList.map((question, index) => (
                            <QuestionItem
                              key={`${questionsKey}-${index}`}
                              id={questionsData[index]?.id || `question-${index}`}
                              index={index}
                              question={question}
                              consultDocuments={questionsData[index]?.consultDocuments ?? true}
                              onUpdate={(idx, value) => updateQuestion(idx, value)}
                              onBlur={(idx, value) => handleQuestionBlur(idx, value)}
                              onRemove={(idx) => removeQuestion(idx)}
                              onMoveUp={(idx) => moveQuestionUp(idx)}
                              onMoveDown={(idx) => moveQuestionDown(idx)}
                              onConsultDocumentsChange={handleConsultDocumentsChange}
                              canRemove={questionsList.length > 1}
                              totalQuestions={questionsList.length}
                            />
                          ))}
                        </VStack>
                      </Box>
                    </VStack>
                  </HStack>
                </VStack>
              </Dialog.Body>

              <Dialog.Footer>
                <Dialog.ActionTrigger asChild>
                  <CancelButton onClick={handleClose} size="md">
                    Cancel
                  </CancelButton>
                </Dialog.ActionTrigger>
                <ConfirmButton onClick={handleSave} size="md">
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

      {/* Optimize Checklist Modal */}
      <OptimizeChecklistModal
        isOpen={showOptimizeModal}
        onClose={() => setShowOptimizeModal(false)}
        checklist={{
          id: editingChecklist?.id || "",
          name: checklistName,
          description: checklistDescription,
          questions: questionsList.filter((q) => q.trim()).join("\n"),
          owner_id: editingChecklist?.owner_id || "",
        }}
        selectedKnowledgeBase={selectedKnowledgeBase}
        onOptimized={handleOptimized}
      />
    </>
  )
}

export default ChecklistModal
