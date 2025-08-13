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

  // Generate questions state
  const [generating, setGenerating] = useState(false)
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

    try {
      await navigator.clipboard.writeText(questionsText)
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
    showSuccessToast(`Applied ${optimizedQuestions.length} optimized questions`)
  }

  const handleGenerateQuestions = async () => {
    if (!checklistDescription.trim()) {
      showErrorToast("Please enter a description")
      return
    }

    if (checklistDescription.trim().length < 10) {
      showErrorToast("Description must be at least 10 characters")
      return
    }

    setGenerating(true)

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

        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
        const apiUrl = `${baseUrl}/api/v1/veradoc/generate-questions-with-files`

        console.log("Generating questions with files - API URL:", apiUrl)

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

      // Replace current questions with generated ones
      const generatedQuestions = response.questions || []
      if (generatedQuestions.length > 0) {
        // Create new questions array with generated questions plus one empty question at the end
        const newQuestions = [...generatedQuestions, ""]

        // Replace the entire questions list
        updateQuestionsList(newQuestions)

        // Force re-render of question items
        setQuestionsKey((prev) => prev + 1)

        let successMessage = `Generated ${generatedQuestions.length} questions from description`
        if (referenceMode === "files" && referenceFiles.length > 0) {
          successMessage += ` and ${referenceFiles.length} reference file(s)`
        } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
          successMessage += ` using Knowledge Base: ${referenceKnowledgeBase.title}`
        }

        showSuccessToast(successMessage)
      } else {
        showErrorToast("No questions were generated. Please try a different description.")
      }
    } catch (error: any) {
      console.error("Error generating questions:", error)
      showErrorToast(`Failed to generate questions: ${error.message || "Unknown error"}`)
    } finally {
      setGenerating(false)
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
                      <Field label="Checklist Name" required>
                        <Input
                          value={checklistName}
                          onChange={(e) => setChecklistName(e.target.value)}
                          placeholder="Enter checklist name..."
                        />
                      </Field>

                      <Field label="Description" required>
                        <Textarea
                          value={checklistDescription}
                          onChange={(e) => setChecklistDescription(e.target.value)}
                          placeholder="Enter checklist description to auto-generate questions (minimum 10 characters)..."
                          rows={4}
                        />
                        {checklistDescription.trim().length > 0 &&
                          checklistDescription.trim().length < 10 && (
                            <Text fontSize="xs" color="orange.600">
                              Description needs at least {10 - checklistDescription.trim().length}{" "}
                              more characters to generate questions
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
                            understand the desired structure and requirements for the checklist
                            questions.
                          </Text>

                          {/* Toggle between files and knowledge base */}
                          <HStack gap={4}>
                            <Button
                              size="sm"
                              variant={referenceMode === "files" ? "solid" : "outline"}
                              colorPalette={referenceMode === "files" ? "blue" : "gray"}
                              onClick={() => handleReferenceModeChange("files")}
                            >
                              Upload Files
                            </Button>
                            <Button
                              size="sm"
                              variant={referenceMode === "knowledge-base" ? "solid" : "outline"}
                              colorPalette={referenceMode === "knowledge-base" ? "blue" : "gray"}
                              onClick={() => handleReferenceModeChange("knowledge-base")}
                              disabled={!knowledgeBases || knowledgeBases.length === 0}
                            >
                              Select Knowledge Base
                            </Button>
                          </HStack>

                          {referenceMode === "files" ? (
                            <FileUpload
                              files={referenceFiles}
                              onFilesChange={setReferenceFiles}
                              maxFiles={3}
                              showHandwrittenToggle={false}
                            />
                          ) : (
                            <VStack align="stretch" gap={2}>
                              {knowledgeBases && knowledgeBases.length > 0 ? (
                                <VStack align="stretch" gap={2}>
                                  <Text fontSize="xs" color="gray.600">
                                    Select a Knowledge Base to use as reference for generating
                                    checklist questions:
                                  </Text>
                                  <Box
                                    maxH="120px"
                                    overflowY="auto"
                                    border="1px solid"
                                    borderColor="gray.200"
                                    borderRadius="md"
                                  >
                                    {knowledgeBases.map((kb) => (
                                      <Box
                                        key={kb.id}
                                        p={2}
                                        cursor="pointer"
                                        _hover={{ bg: "gray.50" }}
                                        bg={
                                          referenceKnowledgeBase?.id === kb.id ? "blue.50" : "white"
                                        }
                                        borderBottom="1px solid"
                                        borderColor="gray.100"
                                        onClick={() => setReferenceKnowledgeBase(kb)}
                                      >
                                        <Text fontSize="sm" fontWeight="medium">
                                          {kb.title}
                                        </Text>
                                        {kb.description && (
                                          <Text fontSize="xs" color="gray.600" lineClamp={2}>
                                            {kb.description}
                                          </Text>
                                        )}
                                        <Text fontSize="xs" color="gray.500">
                                          {kb.number_of_sources || 0} sources
                                        </Text>
                                      </Box>
                                    ))}
                                  </Box>
                                  {referenceKnowledgeBase && (
                                    <Text fontSize="xs" color="green.600">
                                      Selected: {referenceKnowledgeBase.title}
                                    </Text>
                                  )}
                                </VStack>
                              ) : (
                                <Text fontSize="sm" color="gray.500">
                                  No Knowledge Bases available. Create one first or switch to file
                                  upload.
                                </Text>
                              )}
                            </VStack>
                          )}
                        </VStack>
                      </Field>
                    </VStack>

                    {/* Right Column - Questions List */}
                    <VStack align="stretch" gap={4} flex={1} height="100%">
                      {/* Generate and Optimize buttons above questions */}
                      <HStack justify="space-between" align="center">
                        <Text fontSize="md" fontWeight="medium">
                          Questions
                        </Text>
                        <HStack gap={2}>
                          <Button
                            size="sm"
                            onClick={handleGenerateQuestions}
                            loading={generating}
                            disabled={!checklistDescription.trim() || generating}
                            colorPalette="blue"
                          >
                            {generating ? "Generating..." : "Generate"}
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
                              size="sm"
                              onClick={handleOptimizeClick}
                              variant="outline"
                              colorPalette="blue"
                              disabled={!knowledgeBases || !selectedKnowledgeBase}
                            >
                              Optimize
                            </Button>
                          </Tooltip>
                          <IconButton
                            size="sm"
                            onClick={handleCopyQuestions}
                            variant="ghost"
                            aria-label="Copy questions as text"
                            title="Copy all questions as text"
                          >
                            <FiCopy size={14} />
                          </IconButton>
                        </HStack>
                      </HStack>

                      {/* Questions List */}
                      <Box flex={1} minH={0}>
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
