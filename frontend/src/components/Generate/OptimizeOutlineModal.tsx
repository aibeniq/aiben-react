import {
  VStack,
  HStack,
  Dialog,
  Portal,
  Text,
  Box,
  Textarea,
  IconButton,
  Button,
  Card,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { Radio, RadioGroup } from "../ui/radio"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { useState } from "react"
import { ReportgenieService, OptimizedOutlineResponse, OutlineSuggestion } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { FiCheck, FiEdit3, FiSave, FiX, FiDownload } from "react-icons/fi"

interface OptimizeOutlineModalProps {
  isOpen: boolean
  onClose: () => void
  knowledgeBaseId: string
  outlineId: string
  currentSections: string
  onOptimizedSections: (sections: string) => void
}

const OptimizeOutlineModal = ({
  isOpen,
  onClose,
  knowledgeBaseId,
  outlineId,
  currentSections,
  onOptimizedSections,
}: OptimizeOutlineModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [optimizing, setOptimizing] = useState(false)
  const [customInstructions, setCustomInstructions] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [searchMode, setSearchMode] = useState<string>("vector") // Add search mode state
  const [optimizationResults, setOptimizationResults] = useState<OptimizedOutlineResponse | null>(
    null,
  )
  const [showResults, setShowResults] = useState(false)

  // State for editing suggestions
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
  const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
  const [editingModes, setEditingModes] = useState<Set<number>>(new Set())
  const [expandedContent, setExpandedContent] = useState<Set<number>>(new Set())
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

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

    // Initialize with the current suggested section if not already editing
    if (!editingSuggestions.has(index)) {
      const newEditingSuggestions = new Map(editingSuggestions)
      const suggestion = optimizationResults?.suggestions[index]
      newEditingSuggestions.set(index, suggestion?.suggested_section || "")
      setEditingSuggestions(newEditingSuggestions)
    }
  }

  const cancelEditingSuggestion = (index: number) => {
    const newEditingModes = new Set(editingModes)
    newEditingModes.delete(index)
    setEditingModes(newEditingModes)

    // Reset to original suggestion
    const newEditingSuggestions = new Map(editingSuggestions)
    const suggestion = optimizationResults?.suggestions[index]
    newEditingSuggestions.set(index, suggestion?.suggested_section || "")
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
    const suggestion = optimizationResults?.suggestions[index]
    return editingSuggestions.get(index) || suggestion?.suggested_section || ""
  }

  const toggleContentExpansion = (index: number) => {
    const newExpanded = new Set(expandedContent)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedContent(newExpanded)
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
    }
  }

  const handleOptimize = async () => {
    if (!selectedFile) {
      showErrorToast("Please select a ground-truth document to upload.")
      return
    }

    try {
      setOptimizing(true)
      // Format the request to match the expected form data structure
      const result = await ReportgenieService.optimizeOutline({
        formData: {
          knowledge_base_id: knowledgeBaseId,
          outline_id: outlineId,
          sections: currentSections,
          custom_instructions: customInstructions || undefined,
          search_mode: searchMode,
          files: [selectedFile],
        },
      })

      setOptimizationResults(result)
      setShowResults(true)

      // Initialize all suggestions that need revision as accepted by default
      const needsRevisionIndices = new Set<number>()
      result.suggestions.forEach((suggestion: OutlineSuggestion, index: number) => {
        if (suggestion.needs_revision) {
          needsRevisionIndices.add(index)
        }
      })
      setAcceptedSuggestions(needsRevisionIndices)

      showSuccessToast(
        `Optimization complete! Found suggestions for ${result.suggestions.filter((s: OutlineSuggestion) => s.needs_revision).length} sections.`,
      )
    } catch (error: any) {
      console.error("Error optimizing outline:", error)

      if (error.status === 422) {
        showErrorToast("Invalid request. Please check your inputs and try again.")
      } else if (error.status === 401) {
        showErrorToast("You need to be logged in to optimize outlines.")
      } else if (error.status === 403) {
        showErrorToast("You don't have access to this knowledge base.")
      } else if (error.status === 404) {
        showErrorToast("Knowledge base or outline not found.")
      } else if (error.status === 500) {
        showErrorToast("Server error. Please try again later or contact support.")
      } else {
        showErrorToast(`Failed to optimize outline: ${error.message || "Unknown error"}`)
      }
    } finally {
      setOptimizing(false)
    }
  }

  const handleApplyOptimizations = () => {
    if (!optimizationResults) return

    // Create optimized sections using only accepted suggestions
    const optimizedSections = optimizationResults.suggestions.map(
      (suggestion: OutlineSuggestion, index: number) => {
        if (acceptedSuggestions.has(index) && suggestion.needs_revision) {
          // Use edited suggestion if available, otherwise use original suggestion
          return getSuggestionText(index)
        }
        return suggestion.original_section
      },
    )

    onOptimizedSections(JSON.stringify(optimizedSections))
    showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)
    handleClose()
  }

  const handleDownloadCsv = async () => {
    if (!optimizationResults || optimizationResults.suggestions.length === 0) {
      showErrorToast("No optimization results to download")
      return
    }

    setLoadingCsvDownload(true)

    try {
      // Create the data structure expected by the backend
      const csvData = {
        suggestions: optimizationResults.suggestions,
        analysis_summary:
          optimizationResults.analysis_summary || "Outline optimization results export",
      }

      const response = await ReportgenieService.generateOutlineOptimizationCsv({
        requestBody: { content: JSON.stringify(csvData) },
      })

      // Handle the blob response
      const blob = new Blob([response as any], { type: "text/csv" })
      const url = window.URL.createObjectURL(blob)

      // Create download link
      const a = document.createElement("a")
      a.href = url
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-").split("T")[0]
      a.download = `outline_optimization_${timestamp}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("CSV downloaded successfully")
    } catch (error: any) {
      console.error("Error downloading CSV:", error)
      showErrorToast(`Failed to download CSV: ${error.message || "Unknown error"}`)
    } finally {
      setLoadingCsvDownload(false)
    }
  }

  const handleClose = () => {
    setSelectedFile(null)
    setCustomInstructions("")
    setSearchMode("vector") // Reset search mode
    setOptimizationResults(null)
    setShowResults(false)
    setAcceptedSuggestions(new Set())
    setEditingSuggestions(new Map())
    setEditingModes(new Set())
    setExpandedContent(new Set())
    setLoadingCsvDownload(false)
    onClose()
  }

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && handleClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="6xl" maxH="90vh">
            <Dialog.Header>
              <Dialog.Title>Optimize Outline</Dialog.Title>
            </Dialog.Header>

            <Dialog.Body overflowY="auto">
              {!showResults ? (
                <VStack gap={6} align="stretch">
                  <Box>
                    <Text fontSize="sm" mb={4} color="gray.600">
                      Upload a ground-truth document that represents a high-quality example of the
                      type of report you want to generate. The system will generate a report using
                      your current outline and knowledge base, compare it to the ground-truth, and
                      suggest improvements to your outline sections.
                    </Text>
                  </Box>

                  <Field label="Ground-Truth Document" required>
                    <input
                      type="file"
                      accept=".pdf,.docx,.doc,.txt"
                      onChange={handleFileSelect}
                      style={{
                        width: "100%",
                        padding: "8px",
                        border: "1px solid #ccc",
                        borderRadius: "6px",
                      }}
                    />
                    {selectedFile && (
                      <Text fontSize="sm" color="green.600" mt={2}>
                        Selected: {selectedFile.name} (
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                      </Text>
                    )}
                  </Field>

                  <Field label="Search Mode" helperText="Choose how to analyze the knowledge base">
                    <RadioGroup
                      onValueChange={(details) => setSearchMode(details.value || "vector")}
                      value={searchMode}
                      defaultValue="vector"
                    >
                      <HStack gap={4}>
                        <Radio value="vector">Vector Search</Radio>
                        <Radio value="full_text">Full Document Scan</Radio>
                      </HStack>
                    </RadioGroup>
                  </Field>

                  <Field
                    label="Custom Instructions (Optional)"
                    helperText="Provide additional guidance for the optimization process"
                  >
                    <Textarea
                      value={customInstructions}
                      onChange={(e) => setCustomInstructions(e.target.value)}
                      placeholder="e.g., Focus on improving technical depth, ensure compliance with specific standards, etc."
                      rows={3}
                      maxLength={2000}
                    />
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      {customInstructions.length}/2000 characters
                    </Text>
                  </Field>

                  {optimizing && (
                    <Box>
                      <Box
                        width="100%"
                        height="4px"
                        bg="gray.200"
                        borderRadius="full"
                        overflow="hidden"
                      >
                        <Box
                          width="100%"
                          height="100%"
                          bg="blue.500"
                          animation="pulse 2s infinite"
                        />
                      </Box>
                      <Text fontSize="sm" mt={2} textAlign="center" color="gray.600">
                        Analyzing outline and generating optimizations...
                      </Text>
                    </Box>
                  )}
                </VStack>
              ) : (
                <VStack gap={6} align="stretch">
                  <HStack justify="space-between" align="center">
                    <VStack align="start" gap={1}>
                      <Text fontSize="lg" fontWeight="semibold">
                        Optimization Results
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        {
                          optimizationResults?.suggestions.filter(
                            (s: OutlineSuggestion) => s.needs_revision,
                          ).length
                        }{" "}
                        sections need optimization
                      </Text>
                    </VStack>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleDownloadCsv}
                      loading={loadingCsvDownload}
                      colorPalette="green"
                    >
                      <FiDownload />
                      Download CSV
                    </Button>
                  </HStack>

                  {optimizationResults?.analysis_summary && (
                    <Box>
                      <Text fontSize="sm" color="gray.600">
                        {optimizationResults.analysis_summary}
                      </Text>
                    </Box>
                  )}

                  <VStack gap={4} align="stretch">
                    {optimizationResults?.suggestions.map(
                      (suggestion: OutlineSuggestion, index: number) => (
                        <Card.Root
                          key={index}
                          variant={suggestion.needs_revision ? "elevated" : "subtle"}
                        >
                          <Card.Body>
                            <VStack gap={3} align="stretch">
                              <HStack justify="space-between">
                                <Text fontWeight="bold" fontSize="sm" color="gray.600">
                                  Section {index + 1}
                                </Text>
                                {suggestion.needs_revision && (
                                  <Button
                                    size="sm"
                                    variant={acceptedSuggestions.has(index) ? "solid" : "outline"}
                                    colorPalette={acceptedSuggestions.has(index) ? "green" : "blue"}
                                    onClick={() => toggleSuggestion(index)}
                                  >
                                    {acceptedSuggestions.has(index) ? (
                                      <>
                                        <FiCheck size={14} /> Accepted
                                      </>
                                    ) : (
                                      "Accept"
                                    )}
                                  </Button>
                                )}
                              </HStack>

                              <Box>
                                <Text fontSize="xs" fontWeight="medium" color="gray.600" mb={1}>
                                  Original Section Description:
                                </Text>
                                <Text fontSize="sm" p={2} bg="gray.50" borderRadius="md">
                                  {suggestion.original_section}
                                </Text>
                              </Box>

                              {suggestion.needs_revision ? (
                                <>
                                  <Box>
                                    <HStack justify="space-between" mb={1}>
                                      <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                        Suggested Section Description:
                                      </Text>
                                      {!editingModes.has(index) ? (
                                        <IconButton
                                          size="xs"
                                          variant="ghost"
                                          aria-label="Edit suggestion"
                                          onClick={() => startEditingSuggestion(index)}
                                        >
                                          <FiEdit3 size={12} />
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
                                            <FiSave size={12} />
                                          </IconButton>
                                          <IconButton
                                            size="xs"
                                            variant="ghost"
                                            colorPalette="red"
                                            aria-label="Cancel editing"
                                            onClick={() => cancelEditingSuggestion(index)}
                                          >
                                            <FiX size={12} />
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
                                        fontSize="sm"
                                        p={2}
                                        bg="blue.50"
                                        borderRadius="md"
                                        border="1px solid"
                                        borderColor="blue.200"
                                        resize="vertical"
                                        rows={3}
                                      />
                                    ) : (
                                      <Text
                                        fontSize="sm"
                                        p={2}
                                        bg="blue.50"
                                        borderRadius="md"
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
                                    <Text fontSize="xs" fontWeight="medium" color="gray.600" mb={1}>
                                      Reason for Change:
                                    </Text>
                                    <Text fontSize="sm" color="gray.600">
                                      {suggestion.reason}
                                    </Text>
                                  </Box>
                                </>
                              ) : (
                                <Box>
                                  <Text fontSize="sm" color="green.600" fontWeight="medium">
                                    ✓ This section is already well-optimized
                                  </Text>
                                </Box>
                              )}

                              <Box>
                                <Text fontSize="xs" fontWeight="medium" color="gray.600" mb={1}>
                                  Generated Content (with current description):
                                </Text>
                                <Box
                                  fontSize="sm"
                                  p={2}
                                  bg="gray.50"
                                  borderRadius="md"
                                  border="1px solid"
                                  borderColor="gray.200"
                                >
                                  <Text whiteSpace="pre-wrap">
                                    {expandedContent.has(index)
                                      ? suggestion.current_output || "No content generated"
                                      : (
                                          suggestion.current_output || "No content generated"
                                        ).substring(0, 300)}
                                    {!expandedContent.has(index) &&
                                    (suggestion.current_output || "").length > 300
                                      ? "..."
                                      : ""}
                                  </Text>
                                  {(suggestion.current_output || "").length > 300 && (
                                    <Button
                                      size="xs"
                                      variant="ghost"
                                      mt={1}
                                      onClick={() => toggleContentExpansion(index)}
                                      colorPalette="gray"
                                    >
                                      {expandedContent.has(index) ? "Show Less" : "Show More"}
                                    </Button>
                                  )}
                                </Box>
                              </Box>

                              <Box>
                                <Text fontSize="xs" fontWeight="medium" color="gray.600" mb={1}>
                                  Ground-Truth Content (from uploaded document):
                                </Text>
                                <Box
                                  fontSize="sm"
                                  p={2}
                                  bg="blue.50"
                                  borderRadius="md"
                                  border="1px solid"
                                  borderColor="blue.200"
                                >
                                  <Text whiteSpace="pre-wrap">
                                    {suggestion.ground_truth_content ||
                                      "No relevant ground-truth content found"}
                                  </Text>
                                </Box>
                              </Box>
                            </VStack>
                          </Card.Body>
                        </Card.Root>
                      ),
                    )}
                  </VStack>
                </VStack>
              )}
            </Dialog.Body>

            <Dialog.Footer>
              <HStack gap={3}>
                <CancelButton onClick={handleClose} size="md">
                  {showResults ? "Close" : "Cancel"}
                </CancelButton>

                {!showResults ? (
                  <ConfirmButton
                    onClick={handleOptimize}
                    size="md"
                    disabled={!selectedFile || optimizing}
                    loading={optimizing}
                  >
                    {optimizing ? "Optimizing..." : "Optimize Outline"}
                  </ConfirmButton>
                ) : (
                  <ConfirmButton
                    onClick={handleApplyOptimizations}
                    size="md"
                    disabled={acceptedSuggestions.size === 0}
                  >
                    Apply {acceptedSuggestions.size} Optimization
                    {acceptedSuggestions.size !== 1 ? "s" : ""}
                  </ConfirmButton>
                )}
              </HStack>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default OptimizeOutlineModal
