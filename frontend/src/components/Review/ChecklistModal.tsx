import {
  Box,
  Button,
  CloseButton,
  Dialog,
  HStack,
  IconButton,
  Input,
  Portal,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { FiCopy } from "react-icons/fi"
import { type KnowledgeBasePublic, type VeraDocChecklist, VeradocService } from "../../client"
import useAuth from "../../hooks/useAuth"
import useCustomToast from "../../hooks/useCustomToast"
import { useKnowledgeBases } from "../../hooks/useKnowledgeBases"
import { copyToClipboard } from "../../utils/copyToClipboard"
import FileUpload from "../Common/FileUpload"
import KnowledgeBaseSelectionModal from "../Common/KnowledgeBaseSelectionModal"
import ProcessingSettingsPopup, { type ProcessingSettings } from "../Common/ProcessingSettingsPopup"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { Field } from "../ui/field"
import HelpTooltip from "../ui/help-tooltip"
import { Tooltip } from "../ui/tooltip"
import OptimizeChecklistModal from "./OptimizeChecklistModal"
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
  questionsData: QuestionData[]
  updateQuestion: (index: number, value: string) => void
  updateQuestionsList: (newQuestions: string[]) => void
  updateQuestionsData: (newData: QuestionData[]) => void
  handleQuestionBlur: (index: number, value: string) => void
  removeQuestion: (index: number) => void
  moveQuestionUp: (index: number) => void
  moveQuestionDown: (index: number) => void
  selectedKnowledgeBase: KnowledgeBasePublic | null // Parent's selected KB
}

interface QuestionData {
  id: string
  text: string
  consultDocuments: boolean
}

interface FileItem {
  file: File
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
  selectedKnowledgeBase, // Use parent's selected KB
}: ChecklistModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useTranslation()
  const { user } = useAuth()
  const { knowledgeBases, showAllUsers, toggleShowAllUsers } = useKnowledgeBases()

  // Note: selectedKnowledgeBase now comes from parent props
  // Internal KB selection not needed since we use parent's selection

  // Validation state
  const [validationErrors, setValidationErrors] = useState<{
    [key: string]: string
  }>({})

  // Validation function
  const validateForm = () => {
    const errors: { [key: string]: string } = {}

    if (!checklistName.trim()) {
      errors.name = "Checklist name is required"
    } else if (checklistName.trim().length < 3) {
      errors.name = "Checklist name must be at least 3 characters long"
    }

    // Description is optional - no validation required

    if (questionsList.length === 0 || questionsList.every((q) => !q.trim())) {
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
      setValidationErrors((prev) => ({ ...prev, name: "" }))
    }
  }

  const handleDescriptionChange = (value: string) => {
    setChecklistDescription(value)
    if (validationErrors.description) {
      setValidationErrors((prev) => ({ ...prev, description: "" }))
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
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")

  // Processing settings state - initialized from user defaults
  const [processingSettings, setProcessingSettings] = useState<ProcessingSettings>({
    searchMode: (user?.default_processing_mode as "vector" | "full_scan") || "vector",
    visionAnalysis: user?.vision_analysis_enabled || false,
    pdfParsing: (user?.pdf_parsing_preference as "enhanced" | "basic") || "basic",
  })

  const [showReferenceKnowledgeBaseModal, setShowReferenceKnowledgeBaseModal] = useState(false)

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
      setValidationErrors((prev) => ({ ...prev, questions: "" }))
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
        formData.append("search_mode", processingSettings.searchMode)
        formData.append("vision_analysis_override", processingSettings.visionAnalysis.toString())
        formData.append("pdf_parsing_override", processingSettings.pdfParsing)

        // Add files to formData
        referenceFiles.forEach((item) => {
          formData.append("files", item.file)
        })

        // Use direct fetch for file upload - now using HTTP-only cookies
        const headers: any = {}
        // No need for Authorization header - cookies are sent automatically

        const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
        const apiUrl = `${baseUrl}/api/v1/veradoc/generate-questions-with-files`

        console.log("Suggesting questions with files - API URL:", apiUrl)

        const apiResponse = await fetch(apiUrl, {
          method: "POST",
          headers,
          credentials: "include", // Include HTTP-only cookies
          body: formData,
        })

        if (!apiResponse.ok) {
          throw new Error(`HTTP ${apiResponse.status}: ${apiResponse.statusText}`)
        }

        response = await apiResponse.json()
      } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use the SDK method with knowledge base reference
        response = await VeradocService.generateQuestionsWithFiles({
          formData: {
            description: checklistDescription.trim(),
            checklist_type: "general",
            files: [],
            vision_analysis_override: processingSettings.visionAnalysis,
            pdf_parsing_override: processingSettings.pdfParsing,
          },
        })
      } else {
        // Use the basic SDK method without references
        response = await VeradocService.generateQuestionsWithFiles({
          formData: {
            description: checklistDescription.trim(),
            checklist_type: "general",
            vision_analysis_override: processingSettings.visionAnalysis,
            pdf_parsing_override: processingSettings.pdfParsing,
            files: [],
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
          setValidationErrors((prev) => ({ ...prev, questions: "" }))
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

  const handleMainModalClose = (details: { open: boolean }) => {
    if (!details.open) {
      onClose()
    }
  }

  return (
    <>
      <Portal>
        <Dialog.Root open={isOpen} onOpenChange={handleMainModalClose}>
          <Dialog.Backdrop />
          {/*
              Increase zIndex above SelectionModal (which uses 2000) so the
              Edit Checklist modal appears on top when opened from the
              Select Checklist dialog. Keep it below OptimizeChecklistModal (2500).
            */}
          <Dialog.Positioner style={{ zIndex: 2100 }}>
            <Dialog.Content maxW="6xl" maxH="90vh">
              <Dialog.Header>
                <HStack align="center" gap={2}>
                  <Dialog.Title>
                    {editingChecklist
                      ? t("editChecklistModal.title")
                      : t("editChecklistModal.createTitle")}
                  </Dialog.Title>
                  <HelpTooltip helpKey="createChecklist" />
                </HStack>
              </Dialog.Header>{" "}
              <Dialog.Body overflowY="auto">
                <VStack align="stretch" gap={4}>
                  {/* Two-column layout */}
                  <HStack align="stretch" gap={4}>
                    {/* Left Column - Basic Fields and Settings */}
                    <VStack align="stretch" gap={4} flex={1}>
                      {/* Basic Info */}
                      <Field
                        label={t("editChecklistModal.checklistName")}
                        required
                        invalid={!!validationErrors.name}
                        errorText={validationErrors.name}
                      >
                        <Input
                          value={checklistName}
                          onChange={(e) => handleNameChange(e.target.value)}
                          placeholder={t("editChecklistModal.checklistNamePlaceholder")}
                        />
                      </Field>

                      <Field
                        label={
                          <HStack align="center" gap={2}>
                            <span>{t("editChecklistModal.description")}</span>
                            <HelpTooltip helpKey="minimumDescriptionLength" />
                          </HStack>
                        }
                        invalid={!!validationErrors.description}
                        errorText={validationErrors.description}
                      >
                        <Textarea
                          value={checklistDescription}
                          onChange={(e) => handleDescriptionChange(e.target.value)}
                          placeholder={t("editChecklistModal.descriptionPlaceholder")}
                          rows={4}
                        />
                      </Field>

                      {/* Processing Settings */}
                      <Box width="100%">
                        <HStack align="center">
                          <Text fontSize="sm" fontWeight="medium">
                            {t("processingSettings.title")}
                          </Text>
                          <ProcessingSettingsPopup
                            settings={processingSettings}
                            onSettingsChange={setProcessingSettings}
                            disabled={suggesting}
                            contentZIndex={10050}
                            backdropZIndex={10040}
                          />
                          <HelpTooltip helpKey="searchMode" />
                        </HStack>
                      </Box>

                      <Field
                        label={
                          <HStack align="center" gap={2}>
                            <span>{t("editChecklistModal.referenceDocuments")}</span>
                            <HelpTooltip helpKey="referenceDocuments" />
                          </HStack>
                        }
                      >
                        <VStack align="stretch" gap={3}>
                          {/* Reference Mode Toggle */}
                          <HStack gap={2}>
                            <Button
                              size="sm"
                              variant={referenceMode === "files" ? "solid" : "outline"}
                              onClick={() => handleReferenceModeChange("files")}
                            >
                              {t("editChecklistModal.uploadFiles")}
                            </Button>
                            <Button
                              size="sm"
                              variant={referenceMode === "knowledge-base" ? "solid" : "outline"}
                              onClick={() => handleReferenceModeChange("knowledge-base")}
                              disabled={!knowledgeBases || knowledgeBases.length === 0}
                            >
                              {t("editChecklistModal.knowledgeBase")}
                            </Button>
                          </HStack>

                          {/* Reference Mode Content */}
                          {referenceMode === "files" && (
                            <VStack align="stretch" gap={2}>
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
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                    [".xlsx"],
                                  "application/vnd.ms-excel": [".xls"],
                                  "application/json": [".json"],
                                }}
                                maxFiles={5}
                              />
                            </VStack>
                          )}

                          {referenceMode === "knowledge-base" && (
                            <Box>
                              <Button
                                w="full"
                                variant={referenceKnowledgeBase ? "solid" : "outline"}
                                onClick={() => setShowReferenceKnowledgeBaseModal(true)}
                                justifyContent="flex-start"
                                textAlign="left"
                                color={referenceKnowledgeBase ? "white" : "gray.600"}
                              >
                                {referenceKnowledgeBase?.title ||
                                  t("dropdowns.selectKnowledgeBase")}
                              </Button>
                              {!knowledgeBases || knowledgeBases.length === 0 ? (
                                <Text fontSize="sm" color="orange.600">
                                  No Knowledge Bases available. Create one first to use this
                                  feature.
                                </Text>
                              ) : null}
                            </Box>
                          )}
                        </VStack>
                      </Field>
                    </VStack>

                    {/* Right Column - Questions List */}
                    <VStack align="stretch" gap={4} flex={1} height="100%">
                      {/* Suggest and Optimize buttons above questions */}
                      <HStack justify="space-between" align="center">
                        <Text fontSize="md" fontWeight="medium">
                          {t("editChecklistModal.questions", {
                            count: questionsList.filter((q) => q.trim()).length,
                          })}
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
                            {suggesting ? "Suggesting..." : t("editChecklistModal.suggest")}
                          </Button>
                          <HelpTooltip helpKey="suggestChecklistQuestions" />
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
                              {t("editChecklistModal.optimize")}
                            </Button>
                          </Tooltip>
                          <HelpTooltip helpKey="optimizeChecklistQuestions" />
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
                              placeholder={t("editChecklistModal.addQuestionPlaceholder")}
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
                <HStack gap={3}>
                  <CancelButton onClick={handleClose} size="md">
                    {t("editChecklistModal.cancel")}
                  </CancelButton>
                  <ConfirmButton onClick={handleSave} size="md">
                    {editingChecklist
                      ? t("editChecklistModal.updateChecklist")
                      : t("editChecklistModal.createChecklist")}
                  </ConfirmButton>
                </HStack>
              </Dialog.Footer>
              <Dialog.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Dialog.CloseTrigger>
            </Dialog.Content>
          </Dialog.Positioner>
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

        {/* KB Selection Modal removed - using parent's selectedKnowledgeBase */}

        <KnowledgeBaseSelectionModal
          isOpen={showReferenceKnowledgeBaseModal}
          onClose={() => {
            setShowReferenceKnowledgeBaseModal(false)
          }}
          title={t("dropdowns.selectKnowledgeBase")}
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={referenceKnowledgeBase}
          onSelectionChange={setReferenceKnowledgeBase}
          showAllUsers={showAllUsers}
          toggleShowAllUsers={toggleShowAllUsers}
        />
      </Portal>
    </>
  )
}

export default ChecklistModal
