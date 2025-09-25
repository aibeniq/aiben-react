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
import type { KnowledgeBasePublic, ReportGenieOutline } from "../../client"
import { ReportgenieService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { useKnowledgeBases } from "../../hooks/useKnowledgeBases"
import { copyToClipboard } from "../../utils/copyToClipboard"
import { generateUUID } from "../../utils/uuid"
import FileUpload, { type FileItem } from "../Common/FileUpload"
import KnowledgeBaseSelectionModal from "../Common/KnowledgeBaseSelectionModal"
import SearchModeToggle from "../Common/SearchModeToggle"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { Field } from "../ui/field"
import HelpTooltip from "../ui/help-tooltip"
import OptimizeOutlineModal from "./OptimizeOutlineModal"
import SectionEditor from "./SectionEditor" // Import SectionEditor instead of InteractiveList

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
  console.log("🔍 OutlineModal: Received sections prop:", sections)
  console.log("🔍 OutlineModal: Type of sections prop:", typeof sections)
  console.log("🔍 OutlineModal: Editing outline:", editingOutline?.name)

  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { t } = useTranslation()
  const { knowledgeBases, showAllUsers, toggleShowAllUsers } = useKnowledgeBases()

  // Knowledge Base for optimization functionality
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)

  // Validation state
  const [validationErrors, setValidationErrors] = useState<{
    [key: string]: string
  }>({})

  // Validation function
  const validateForm = () => {
    const errors: { [key: string]: string } = {}

    if (!outlineName.trim()) {
      errors.name = "Outline name is required"
    } else if (outlineName.trim().length < 3) {
      errors.name = "Outline name must be at least 3 characters long"
    }

    // Description is optional - no validation required

    // Check if sections exist (either as JSON array or simple text)
    let hasSections = false
    if (sections.trim()) {
      try {
        const parsedSections = JSON.parse(sections)
        if (Array.isArray(parsedSections)) {
          hasSections = parsedSections.some((section) => section.text?.trim())
        }
      } catch {
        // If JSON parsing fails, treat as simple text
        hasSections = sections.split("\n").some((line) => line.trim())
      }
    }

    if (!hasSections) {
      errors.sections = "At least one section is required"
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
    setOutlineName(value)
    if (validationErrors.name) {
      setValidationErrors((prev) => ({ ...prev, name: "" }))
    }
  }

  const handleDescriptionChange = (value: string) => {
    setOutlineDescription(value)
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

  const [suggesting, setSuggesting] = useState(false)
  const [showOptimizeModal, setShowOptimizeModal] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")
  const [showReferenceKnowledgeBaseModal, setShowReferenceKnowledgeBaseModal] = useState(false)

  const handleSuggestOutline = async () => {
    if (!outlineDescription.trim()) {
      showErrorToast("Please enter an outline description first")
      return
    }

    // Validate minimum length requirement
    if (outlineDescription.trim().length < 10) {
      showErrorToast("Please enter a more detailed description (at least 10 characters)")
      return
    }

    // Validate reference requirements if any are selected
    if (referenceMode === "files" && exampleFiles.length === 0) {
      // Files mode but no files - this is okay, just use description
    } else if (referenceMode === "knowledge-base" && !referenceKnowledgeBase) {
      showErrorToast("Please select a Knowledge Base or switch to file upload mode")
      return
    }

    setSuggesting(true)

    try {
      let response

      if (referenceMode === "files" && exampleFiles.length > 0) {
        // Use the existing file upload endpoint
        const files = exampleFiles.map((item) => item.file)

        response = await ReportgenieService.generateOutline({
          formData: {
            description: outlineDescription.trim(),
            report_type: "general",
            files: files.length > 0 ? files : undefined,
          },
        })
      } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use the new JSON endpoint with knowledge base reference
        response = await ReportgenieService.generateOutlineJson({
          requestBody: {
            description: outlineDescription.trim(),
            report_type: "general",
            knowledge_base_id: referenceKnowledgeBase.id,
            search_mode: searchMode,
          },
        })
      } else {
        // Use the basic file upload endpoint without files
        response = await ReportgenieService.generateOutline({
          formData: {
            description: outlineDescription.trim(),
            report_type: "general",
          },
        })
      }

      // Replace current sections with suggested ones
      const suggestedSections = response.sections || []
      if (suggestedSections.length > 0) {
        // Create structured section data with all sections having consultDocuments: true by default
        const structuredSections = suggestedSections.map((section) => ({
          id: generateUUID(),
          text: section,
          consultDocuments: true,
        }))

        // Convert to JSON string format expected by the section editor
        const sectionsString = JSON.stringify(structuredSections)
        onSectionsChange(sectionsString)

        // Clear sections validation error if it exists
        if (validationErrors.sections) {
          setValidationErrors((prev) => ({ ...prev, sections: "" }))
        }

        let successMessage = `Suggested ${suggestedSections.length} sections from description`
        if (referenceMode === "files" && exampleFiles.length > 0) {
          successMessage += ` and ${exampleFiles.length} example file(s)`
        } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
          successMessage += ` using Knowledge Base "${referenceKnowledgeBase.title}"`
        }
        successMessage += ` (${searchMode === "vector" ? "vector search" : "full document scan"})`

        showSuccessToast(successMessage)
      } else {
        showErrorToast("No sections were suggested. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error generating outline:", error)

      // Handle specific error types
      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to suggest sections.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to suggest sections: ${error.message || "Unknown error"}`)
      }
    } finally {
      setSuggesting(false)
    }
  }

  // Handler for reference mode changes
  const handleReferenceModeChange = (mode: "files" | "knowledge-base") => {
    setReferenceMode(mode)
    // Clear the opposite mode's selection
    if (mode === "files") {
      setReferenceKnowledgeBase(null)
    } else {
      setExampleFiles([])
    }
  }

  const handleOptimizeClick = () => {
    if (!selectedKnowledgeBase) {
      showErrorToast("Please select a knowledge base first to optimize the outline.")
      return
    }

    if (!editingOutline?.id) {
      showErrorToast("Please save the outline first before optimizing.")
      return
    }

    if (!sections.trim()) {
      showErrorToast("Please add some sections to the outline before optimizing.")
      return
    }

    setShowOptimizeModal(true)
  }

  const handleClose = () => {
    setExampleFiles([])
    onClose()
  }

  const handleCopySections = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    try {
      // Parse sections from JSON format
      let sectionTexts: string[] = []

      if (sections.trim()) {
        try {
          const parsedSections = JSON.parse(sections)
          if (Array.isArray(parsedSections)) {
            sectionTexts = parsedSections
              .filter((section) => section.text && section.text.trim() !== "")
              .map((section) => section.text.trim())
          }
        } catch {
          // If JSON parsing fails, treat as simple text
          sectionTexts = sections
            .split("\n")
            .filter((line) => line.trim() !== "")
            .map((line) => line.trim())
        }
      }

      if (sectionTexts.length === 0) {
        showErrorToast("No sections to copy")
        return
      }

      await copyToClipboard(sectionTexts.join("\n"))
      showSuccessToast("Sections copied to clipboard!")
    } catch (error) {
      console.error("Error copying sections:", error)
      showErrorToast("Failed to copy sections to clipboard")
    }
  }

  const handleMainModalClose = (e: { open: boolean }) => {
    if (!e.open) {
      handleClose()
    }
  }

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={handleMainModalClose}>
        <Dialog.Backdrop />
        <Dialog.Positioner style={{ zIndex: 1500 }}>
          <Dialog.Content maxW="6xl" maxH="90vh">
            <Dialog.Header>
              <HStack align="center" gap={2}>
                <Dialog.Title>
                  {editingOutline ? t("editOutlineModal.title") : t("editOutlineModal.createTitle")}
                </Dialog.Title>
                <HelpTooltip helpKey="createOutline" />
              </HStack>
              <Dialog.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Dialog.CloseTrigger>
            </Dialog.Header>

            <Dialog.Body overflowY="auto">
              <VStack gap={4} align="stretch">
                {/* Two-column layout */}
                <HStack align="stretch" gap={4}>
                  {/* Left Column - Basic Fields and Settings */}
                  <VStack align="stretch" gap={4} flex="1">
                    <Field
                      label={t("editOutlineModal.outlineName")}
                      required
                      invalid={!!validationErrors.name}
                      errorText={validationErrors.name}
                    >
                      <Input
                        value={outlineName}
                        onChange={(e) => handleNameChange(e.target.value)}
                        placeholder={t("editOutlineModal.outlineNamePlaceholder")}
                      />
                    </Field>

                    <Field
                      label={
                        <HStack align="center" gap={2}>
                          <span>{t("editOutlineModal.description")}</span>
                          <HelpTooltip helpKey="minimumDescriptionLength" />
                        </HStack>
                      }
                      invalid={!!validationErrors.description}
                      errorText={validationErrors.description}
                    >
                      <Textarea
                        value={outlineDescription}
                        onChange={(e) => handleDescriptionChange(e.target.value)}
                        placeholder={t("editOutlineModal.descriptionPlaceholder")}
                        resize="vertical"
                        rows={3}
                      />
                    </Field>

                    <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                    <Field
                      label={
                        <HStack align="center" gap={2}>
                          <span>{t("editOutlineModal.referenceDocuments")}</span>
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
                            {t("editOutlineModal.uploadFiles")}
                          </Button>
                          <Button
                            size="sm"
                            variant={referenceMode === "knowledge-base" ? "solid" : "outline"}
                            onClick={() => handleReferenceModeChange("knowledge-base")}
                            disabled={!knowledgeBases || knowledgeBases.length === 0}
                          >
                            {t("editOutlineModal.knowledgeBase")}
                          </Button>
                        </HStack>

                        {/* Reference Mode Content */}
                        {referenceMode === "files" && (
                          <VStack align="stretch" gap={2}>
                            <FileUpload
                              files={exampleFiles}
                              onFilesChange={setExampleFiles}
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
                              {referenceKnowledgeBase?.title || t("dropdowns.selectKnowledgeBase")}
                            </Button>
                            {!knowledgeBases || knowledgeBases.length === 0 ? (
                              <Text fontSize="sm" color="orange.600">
                                No Knowledge Bases available. Create one first to use this feature.
                              </Text>
                            ) : null}
                          </Box>
                        )}
                      </VStack>
                    </Field>
                  </VStack>

                  {/* Right Column - Sections List */}
                  <VStack align="stretch" gap={4} flex="1">
                    {/* Knowledge Base Selection for Optimization */}
                    <Field label={t("editOutlineModal.knowledgeBase")}>
                      <Button
                        w="full"
                        variant={selectedKnowledgeBase ? "solid" : "outline"}
                        onClick={() => setShowKnowledgeBaseModal(true)}
                        justifyContent="flex-start"
                        textAlign="left"
                        color={selectedKnowledgeBase ? "white" : "gray.600"}
                      >
                        {selectedKnowledgeBase?.title || t("dropdowns.selectKnowledgeBase")}
                      </Button>
                    </Field>

                    <Field
                      label={
                        <HStack justify="space-between" w="full">
                          <span>{t("editOutlineModal.sections")} *</span>
                          <HStack gap={2}>
                            <Button
                              size="xs"
                              onClick={handleSuggestOutline}
                              disabled={
                                !outlineDescription.trim() ||
                                outlineDescription.trim().length < 10 ||
                                suggesting
                              }
                              loading={suggesting}
                              variant="outline"
                              colorPalette="green"
                              title={
                                outlineDescription.trim().length < 10
                                  ? "Description must be at least 10 characters to suggest sections"
                                  : "Suggest sections based on the description"
                              }
                            >
                              {suggesting ? "Suggesting..." : t("editOutlineModal.suggest")}
                            </Button>
                            <HelpTooltip helpKey="suggestOutlineSections" />

                            <Button
                              size="xs"
                              onClick={handleOptimizeClick}
                              disabled={
                                !selectedKnowledgeBase ||
                                !editingOutline?.id ||
                                !sections.trim() ||
                                suggesting
                              }
                              variant="outline"
                              colorPalette="blue"
                              title={
                                !selectedKnowledgeBase
                                  ? "Select a knowledge base first"
                                  : !editingOutline?.id
                                    ? "Save the outline first"
                                    : !sections.trim()
                                      ? "Add sections to optimize"
                                      : "Optimize sections using ground-truth document"
                              }
                            >
                              {t("editOutlineModal.optimize")}
                            </Button>
                            <HelpTooltip helpKey="optimizeOutlineSections" />

                            <IconButton
                              size="xs"
                              onClick={handleCopySections}
                              variant="ghost"
                              aria-label="Copy sections as text"
                              title="Copy all sections as text"
                              disabled={!sections.trim()}
                            >
                              <FiCopy size={12} />
                            </IconButton>
                          </HStack>
                        </HStack>
                      }
                      required
                      invalid={!!validationErrors.sections}
                      errorText={validationErrors.sections}
                    >
                      <Box
                        border="1px solid"
                        borderColor="gray.200"
                        borderRadius="md"
                        p={3}
                        width="full"
                      >
                        <SectionEditor
                          sections={sections}
                          placeholder={t("editOutlineModal.addSectionPlaceholder")}
                          onSectionsChange={(newSections) => {
                            onSectionsChange(newSections)
                            // Clear validation error when sections are modified
                            if (validationErrors.sections) {
                              setValidationErrors((prev) => ({
                                ...prev,
                                sections: "",
                              }))
                            }
                          }}
                        />
                      </Box>
                    </Field>
                  </VStack>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <HStack gap={3}>
                <CancelButton onClick={handleClose} size="md">
                  {t("editOutlineModal.cancel")}
                </CancelButton>
                <ConfirmButton onClick={handleSave} size="md">
                  {editingOutline
                    ? t("editOutlineModal.updateOutline")
                    : t("editOutlineModal.createOutline")}
                </ConfirmButton>
              </HStack>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>

      {/* Optimize Outline Modal */}
      {selectedKnowledgeBase && editingOutline?.id && (
        <OptimizeOutlineModal
          isOpen={showOptimizeModal}
          onClose={() => setShowOptimizeModal(false)}
          knowledgeBaseId={selectedKnowledgeBase.id}
          outlineId={editingOutline.id}
          currentSections={sections}
          onOptimizedSections={onSectionsChange}
        />
      )}

      <KnowledgeBaseSelectionModal
        isOpen={showKnowledgeBaseModal}
        onClose={() => setShowKnowledgeBaseModal(false)}
        title={t("editOutlineModal.knowledgeBase")}
        knowledgeBases={knowledgeBases}
        selectedKnowledgeBase={selectedKnowledgeBase}
        onSelectionChange={setSelectedKnowledgeBase}
        showAllUsers={showAllUsers}
        toggleShowAllUsers={toggleShowAllUsers}
      />

      <KnowledgeBaseSelectionModal
        isOpen={showReferenceKnowledgeBaseModal}
        onClose={() => setShowReferenceKnowledgeBaseModal(false)}
        title={t("dropdowns.selectKnowledgeBase")}
        knowledgeBases={knowledgeBases}
        selectedKnowledgeBase={referenceKnowledgeBase}
        onSelectionChange={setReferenceKnowledgeBase}
        showAllUsers={showAllUsers}
        toggleShowAllUsers={toggleShowAllUsers}
      />
    </Portal>
  )
}

export default OutlineModal
