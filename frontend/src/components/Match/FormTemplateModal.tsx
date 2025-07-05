import { useState, useEffect } from "react"
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
import { FormConnectForm, KnowledgeBasePublic } from "../../client"
import { InteractiveList } from "../ui/interactive-list"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import FileUpload, { FileItem } from "../Common/FileUpload"
import useCustomToast from "../../hooks/useCustomToast"

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
  selectedKnowledgeBase?: KnowledgeBasePublic | null
  knowledgeBases?: KnowledgeBasePublic[]
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
  selectedKnowledgeBase,
  knowledgeBases,
}: FormTemplateModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [generating, setGenerating] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    selectedKnowledgeBase || null,
  )

  // Set reference mode based on preselected knowledge base
  useEffect(() => {
    if (selectedKnowledgeBase) {
      setReferenceMode("knowledge-base")
    }
  }, [selectedKnowledgeBase])

  const handleGenerateFields = async () => {
    if (!formDescription.trim()) {
      showErrorToast("Please enter a form description first")
      return
    }

    // Validate minimum length requirement
    if (formDescription.trim().length < 10) {
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

    setGenerating(true)

    try {
      let response

      // For now, we'll call the JSON endpoint directly since the client might not be updated yet
      // TODO: Replace with generated client call once available
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const apiUrl = `${baseUrl}/api/v1/formconnect/generate-fields-json`

      // Get auth token for API calls
      const token = localStorage.getItem("access_token")
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      }
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }

      if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use knowledge base reference
        const requestData = {
          description: formDescription.trim(),
          num_fields: 15, // Default number of fields
          knowledge_base_id: referenceKnowledgeBase.id,
        }

        response = await fetch(apiUrl, {
          method: "POST",
          headers,
          body: JSON.stringify(requestData),
        })
      } else {
        // Use description only (files mode not implemented for form fields yet)
        const requestData = {
          description: formDescription.trim(),
          num_fields: 15, // Default number of fields
        }

        response = await fetch(apiUrl, {
          method: "POST",
          headers,
          body: JSON.stringify(requestData),
        })
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()

      // Convert generated fields to the format expected by InteractiveList
      const generatedFields = result.fields || []
      if (generatedFields.length > 0) {
        const fieldsString = generatedFields.join("\n")
        onFieldsChange(fieldsString)
        showSuccessToast(`Generated ${generatedFields.length} form fields from description`)
      } else {
        showErrorToast("No fields were generated. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error generating fields:", error)

      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to generate fields.")
      } else if (error.status === 404) {
        showErrorToast("Generate fields feature is not available. Please contact support.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to generate fields: ${error.message || "Unknown error"}`)
      }
    } finally {
      setGenerating(false)
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

  const handleModalClose = () => {
    setExampleFiles([])
    onClose()
  }
  return (
    <Dialog.Root open={isOpen} onOpenChange={(e) => (e.open ? null : handleModalClose())}>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="6xl" maxH="90vh">
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
                        placeholder="Enter form template description (e.g., 'Patient intake form for medical clinic', 'Employee onboarding documentation')"
                        resize="vertical"
                        rows={3}
                      />
                    </Field>

                    {/* Generate Fields Section */}
                    <Field label="Generate Fields from Reference">
                      <VStack align="stretch" gap={3}>
                        <HStack gap={2}>
                          <Button
                            size="sm"
                            variant={referenceMode === "files" ? "solid" : "ghost"}
                            onClick={() => handleReferenceModeChange("files")}
                          >
                            Upload Files
                          </Button>
                          <Button
                            size="sm"
                            variant={referenceMode === "knowledge-base" ? "solid" : "ghost"}
                            onClick={() => handleReferenceModeChange("knowledge-base")}
                          >
                            Knowledge Base
                          </Button>
                        </HStack>

                        {referenceMode === "files" && (
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
                              "application/json": [".json"],
                            }}
                            maxFiles={5}
                          />
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

                        <Button
                          onClick={handleGenerateFields}
                          loading={generating}
                          size="sm"
                          colorScheme="blue"
                          disabled={!formDescription.trim() || formDescription.trim().length < 10}
                        >
                          {generating ? "Generating Fields..." : "Generate Fields from Description"}
                        </Button>

                        {formDescription.trim().length < 10 &&
                          formDescription.trim().length > 0 && (
                            <Text fontSize="sm" color="gray.500">
                              Description must be at least 10 characters to generate fields
                            </Text>
                          )}
                      </VStack>
                    </Field>
                  </VStack>

                  <Field label="Form Fields" required py={0} flex="1">
                    <VStack
                      align="stretch"
                      gap={2}
                      display="flex"
                      flexDirection="column"
                      width="100%"
                      maxH="400px"
                      overflowY="auto"
                    >
                      <InteractiveList
                        value={fields}
                        onChange={onFieldsChange}
                        placeholder="Add a field name (e.g. First Name, Address, SSN) or generate from description"
                      />
                    </VStack>
                  </Field>
                </HStack>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer>
              <CancelButton onClick={handleModalClose} size="md">
                Cancel
              </CancelButton>
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
