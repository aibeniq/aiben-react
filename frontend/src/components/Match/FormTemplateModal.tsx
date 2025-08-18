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
  IconButton,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { FormConnectForm, KnowledgeBasePublic } from "../../client"
import { InteractiveList } from "../ui/interactive-list"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import FileUpload, { FileItem } from "../Common/FileUpload"
import SearchModeToggle from "../Common/SearchModeToggle"
import useCustomToast from "../../hooks/useCustomToast"
import { FiCopy } from "react-icons/fi"
import { copyToClipboard } from "../../utils/copyToClipboard"

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
  searchMode?: "vector" | "full_scan"
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
  searchMode: passedSearchMode = "vector",
}: FormTemplateModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Validation state
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({})

  // Validation function
  const validateForm = () => {
    const errors: {[key: string]: string} = {}
    
    if (!formName.trim()) {
      errors.name = "Form template name is required"
    } else if (formName.trim().length < 3) {
      errors.name = "Form template name must be at least 3 characters long"
    }
    
    // Description is optional - no validation required
    
    // Check if fields exist (should be a newline-separated string)
    if (!fields.trim() || fields.split('\n').every(field => !field.trim())) {
      errors.fields = "At least one form field is required"
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
    setFormName(value)
    if (validationErrors.name) {
      setValidationErrors(prev => ({ ...prev, name: '' }))
    }
  }

  const handleDescriptionChange = (value: string) => {
    setFormDescription(value)
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

  const [suggesting, setSuggesting] = useState(false)
  const [exampleFiles, setExampleFiles] = useState<FileItem[]>([])
  const [referenceMode, setReferenceMode] = useState<"files" | "knowledge-base">("files")
  const [referenceKnowledgeBase, setReferenceKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    selectedKnowledgeBase || null,
  )
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(passedSearchMode)

  // Set reference mode based on preselected knowledge base
  useEffect(() => {
    if (selectedKnowledgeBase) {
      setReferenceMode("knowledge-base")
    }
  }, [selectedKnowledgeBase])

  const handleSuggestFields = async () => {
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

    setSuggesting(true)

    try {
      let response

      // Get auth token for API calls
      const token = localStorage.getItem("access_token")
      const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"

      if (referenceMode === "files" && exampleFiles.length > 0) {
        // Use the new file upload endpoint
        const apiUrl = `${baseUrl}/api/v1/formconnect/generate-fields-with-files`
        
        const formData = new FormData()
        formData.append("description", formDescription.trim())
        formData.append("num_fields", "15")
        formData.append("search_mode", searchMode)

        // Add files to formData
        exampleFiles.forEach((item) => {
          formData.append("files", item.file)
        })

        const headers: Record<string, string> = {}
        if (token) {
          headers["Authorization"] = `Bearer ${token}`
        }

        response = await fetch(apiUrl, {
          method: "POST",
          headers,
          body: formData,
        })
      } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
        // Use knowledge base reference
        const apiUrl = `${baseUrl}/api/v1/formconnect/generate-fields-json`
        
        const requestData = {
          description: formDescription.trim(),
          num_fields: 15, // Default number of fields
          knowledge_base_id: referenceKnowledgeBase.id,
          search_mode: searchMode,
        }

        const headers: Record<string, string> = {
          "Content-Type": "application/json",
        }
        if (token) {
          headers["Authorization"] = `Bearer ${token}`
        }

        response = await fetch(apiUrl, {
          method: "POST",
          headers,
          body: JSON.stringify(requestData),
        })
      } else {
        // Use description only (no files or knowledge base)
        const apiUrl = `${baseUrl}/api/v1/formconnect/generate-fields-json`
        
        const requestData = {
          description: formDescription.trim(),
          num_fields: 15, // Default number of fields
          search_mode: searchMode,
        }

        const headers: Record<string, string> = {
          "Content-Type": "application/json",
        }
        if (token) {
          headers["Authorization"] = `Bearer ${token}`
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

      // Convert suggested fields to the format expected by InteractiveList
      const suggestedFields = result.fields || []
      if (suggestedFields.length > 0) {
        const fieldsString = suggestedFields.join("\n")
        onFieldsChange(fieldsString)

        // Clear fields validation error if it exists
        if (validationErrors.fields) {
          setValidationErrors(prev => ({ ...prev, fields: '' }))
        }

        const searchMethodText = searchMode === "vector" ? "vector search" : "full document scan"
        let referenceText = ""
        
        if (referenceMode === "files" && exampleFiles.length > 0) {
          referenceText = ` using ${searchMethodText} on ${exampleFiles.length} uploaded file(s)`
        } else if (referenceMode === "knowledge-base" && referenceKnowledgeBase) {
          referenceText = ` using ${searchMethodText} on knowledge base`
        }

        showSuccessToast(
          `Suggested ${suggestedFields.length} form fields from description${referenceText}`,
        )
      } else {
        showErrorToast("No fields were suggested. Please try with a more detailed description.")
      }
    } catch (error: any) {
      console.error("Error suggesting fields:", error)

      if (error.status === 422) {
        showErrorToast(
          "Invalid request. Please check that your description meets the requirements.",
        )
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to suggest fields.")
      } else if (error.status === 404) {
        showErrorToast("Suggest fields feature is not available. Please contact support.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to suggest fields: ${error.message || "Unknown error"}`)
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

  const handleModalClose = () => {
    setExampleFiles([])
    onClose()
  }

  const handleCopyFields = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Parse fields from the string format used by InteractiveList
    const fieldLines = fields
      .split("\n")
      .filter((line) => line.trim() !== "")
      .map((line) => line.trim())

    if (fieldLines.length === 0) {
      showErrorToast("No fields to copy")
      return
    }

    try {
      await copyToClipboard(fieldLines.join("\n"))
      showSuccessToast("Fields copied to clipboard!")
    } catch (error) {
      console.error("Error copying fields:", error)
      showErrorToast("Failed to copy fields to clipboard")
    }
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
                    <Field label="Form Template Name" required invalid={!!validationErrors.name} errorText={validationErrors.name}>
                      <Input
                        value={formName}
                        onChange={(e) => handleNameChange(e.target.value)}
                        placeholder="Enter form template name"
                      />
                    </Field>

                    <Field label="Form Template Description" invalid={!!validationErrors.description} errorText={validationErrors.description}>
                      <Textarea
                        value={formDescription}
                        onChange={(e) => handleDescriptionChange(e.target.value)}
                        placeholder="Enter form template description to auto-suggest fields (minimum 10 characters)..."
                        resize="vertical"
                        rows={3}
                      />
                    </Field>

                    <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                    <Field label="Reference Documents (Optional)">
                      <VStack align="stretch" gap={3}>
                        <Text fontSize="sm" color="gray.600">
                          Upload reference documents or select a Knowledge Base to help the AI
                          suggest form fields.
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
                          >
                            Knowledge Base
                          </Button>
                        </HStack>

                        {referenceMode === "files" && (
                          <VStack align="stretch" gap={2}>
                            <Text fontSize="sm" color="gray.700" fontWeight="medium">
                              Upload reference documents to suggest form fields based on their content
                            </Text>
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
                            {exampleFiles.length > 0 && (
                              <Text fontSize="xs" color="green.600" fontWeight="medium">
                                ✅ {exampleFiles.length} file(s) will be analyzed to suggest relevant form fields
                              </Text>
                            )}
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

                        {formDescription.trim().length < 10 &&
                          formDescription.trim().length > 0 && (
                            <Text fontSize="sm" color="gray.500">
                              Description must be at least 10 characters to suggest fields
                            </Text>
                          )}
                      </VStack>
                    </Field>
                  </VStack>

                  <Field
                    label={
                      <HStack justify="space-between" w="full">
                        <span>Form Fields</span>
                        <HStack gap={2}>
                          <Button
                            size="xs"
                            onClick={handleSuggestFields}
                            disabled={
                              !formDescription.trim() ||
                              formDescription.trim().length < 10 ||
                              suggesting
                            }
                            loading={suggesting}
                            variant="outline"
                            colorPalette="green"
                            title={
                              formDescription.trim().length < 10
                                ? "Description must be at least 10 characters to suggest fields"
                                : referenceMode === "files" && exampleFiles.length > 0
                                ? `Suggest fields based on description and ${exampleFiles.length} uploaded file(s)`
                                : referenceMode === "knowledge-base" && referenceKnowledgeBase
                                ? "Suggest fields based on description and knowledge base"
                                : "Suggest fields based on the description"
                            }
                          >
                            {suggesting ? "Suggesting..." : "Suggest"}
                          </Button>

                          <IconButton
                            size="xs"
                            onClick={handleCopyFields}
                            variant="ghost"
                            aria-label="Copy fields as text"
                            title="Copy all fields as text"
                            disabled={
                              !fields.trim() ||
                              fields.split("\n").filter((line) => line.trim() !== "").length === 0
                            }
                          >
                            <FiCopy size={12} />
                          </IconButton>
                        </HStack>
                      </HStack>
                    }
                    required
                    invalid={!!validationErrors.fields}
                    errorText={validationErrors.fields}
                    py={0}
                    flex="1"
                  >
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
                        onChange={(newFields) => {
                          onFieldsChange(newFields)
                          // Clear validation error when fields are modified
                          if (validationErrors.fields) {
                            setValidationErrors(prev => ({ ...prev, fields: '' }))
                          }
                        }}
                        placeholder="Add a field name (e.g. First Name, Address, SSN) or suggest from description"
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
              <ConfirmButton onClick={handleSave} size="md">
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
