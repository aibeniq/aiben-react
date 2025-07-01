import {
  HStack,
  VStack,
  Input,
  Textarea,
  Dialog,
  Portal,
  CloseButton,
  Button,
  Text,
  Box,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { ReportGenieOutline, KnowledgeBasePublic } from "../../client"
import SectionEditor from "./SectionEditor" // Import SectionEditor instead of InteractiveList
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import OptimizeOutlineModal from "./OptimizeOutlineModal"
import FileUpload, { FileItem } from "../Common/FileUpload"
import { useState } from "react"
import { ReportgenieService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

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
  selectedKnowledgeBase?: KnowledgeBasePublic | null
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
  selectedKnowledgeBase,
}: OutlineModalProps) => {
  console.log("Parent: sections prop value", sections)

  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [generating, setGenerating] = useState(false)
  const [showOptimizeModal, setShowOptimizeModal] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])

  const handleGenerateOutline = async () => {
    if (!outlineDescription.trim()) {
      showErrorToast("Please enter an outline description first")
      return
    }

    // Validate minimum length requirement
    if (outlineDescription.trim().length < 10) {
      showErrorToast("Please enter a more detailed description (at least 10 characters)")
      return
    }

    setGenerating(true)

    try {
      // Extract files from FileItem objects for the API call
      const files = exampleFiles.map((item) => item.file)

      const response = await ReportgenieService.generateOutline({
        formData: {
          description: outlineDescription.trim(),
          report_type: "general",
          files: files.length > 0 ? files : undefined,
        },
      })

      // Replace current sections with generated ones
      const generatedSections = response.sections || []
      if (generatedSections.length > 0) {
        // Create structured section data with all sections having consultDocuments: true by default
        const structuredSections = generatedSections.map((section) => ({
          id: crypto.randomUUID(),
          text: section,
          consultDocuments: true,
        }))

        // Convert to JSON string format expected by the section editor
        const sectionsString = JSON.stringify(structuredSections)
        onSectionsChange(sectionsString)

        showSuccessToast(`Generated ${generatedSections.length} sections from description`)
      } else {
        showErrorToast("No sections were generated. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error generating outline:", error)

      // Handle specific error types
      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to generate outline.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to generate outline: ${error.message || "Unknown error"}`)
      }
    } finally {
      setGenerating(false)
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

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && handleClose()}>
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
                    placeholder="Enter outline description to auto-generate sections (minimum 10 characters)..."
                    resize="vertical"
                    rows={3}
                  />
                  {outlineDescription.trim().length > 0 &&
                    outlineDescription.trim().length < 10 && (
                      <Text fontSize="xs" color="orange.600">
                        Description needs at least {10 - outlineDescription.trim().length} more
                        characters to generate sections
                      </Text>
                    )}
                </Field>

                <Field label="Example Document (Optional)">
                  <VStack align="stretch" gap={2}>
                    <Text fontSize="sm" color="gray.600">
                      Upload an example document to help the AI understand the desired structure and
                      style.
                    </Text>
                    <FileUpload
                      files={exampleFiles}
                      onFilesChange={setExampleFiles}
                      maxFiles={1}
                      showHandwrittenToggle={false}
                    />
                  </VStack>
                </Field>

                <Field
                  label={
                    <HStack justify="space-between" w="full">
                      <span>Sections</span>
                      <HStack gap={2}>
                        <Button
                          size="xs"
                          onClick={handleGenerateOutline}
                          disabled={
                            !outlineDescription.trim() ||
                            outlineDescription.trim().length < 10 ||
                            generating
                          }
                          loading={generating}
                          variant="outline"
                          colorPalette="green"
                          title={
                            outlineDescription.trim().length < 10
                              ? "Description must be at least 10 characters to generate sections"
                              : "Generate sections based on the description"
                          }
                        >
                          {generating ? "Generating..." : "Generate Outline"}
                        </Button>

                        <Button
                          size="xs"
                          onClick={handleOptimizeClick}
                          disabled={
                            !selectedKnowledgeBase ||
                            !editingOutline?.id ||
                            !sections.trim() ||
                            generating
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
                          Optimize
                        </Button>
                      </HStack>
                    </HStack>
                  }
                  required
                >
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
                <CancelButton onClick={handleClose} size="md">
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
    </Portal>
  )
}

export default OutlineModal
