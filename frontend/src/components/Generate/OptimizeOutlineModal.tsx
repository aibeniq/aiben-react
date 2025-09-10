import {
  Box,
  Button,
  Card,
  Dialog,
  HStack,
  IconButton,
  Portal,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { FiCheck, FiDownload, FiEdit3, FiSave, FiX } from "react-icons/fi"
import {
  type CancelablePromise,
  type OptimizedOutlineResponse,
  type OutlineSuggestion,
  ReportgenieService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import SearchModeToggle from "../Common/SearchModeToggle"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { Field } from "../ui/field"

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
  const { t } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [optimizing, setOptimizing] = useState(false)
  const [customInstructions, setCustomInstructions] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector") // Add search mode state
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

  // Add cancelable promise ref for request cancellation
  const ongoingRequestRef = useRef<CancelablePromise<any> | null>(null)

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

    // Cancel any existing request
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

    try {
      setOptimizing(true)

      // Store the cancelable promise
      ongoingRequestRef.current = ReportgenieService.optimizeOutline({
        formData: {
          knowledge_base_id: knowledgeBaseId,
          outline_id: outlineId,
          sections: currentSections,
          custom_instructions: customInstructions || undefined,
          search_mode: searchMode === "full_scan" ? "full_text" : searchMode, // Map full_scan to full_text for ReportGenie backend
          files: [selectedFile],
        },
      })

      const result = await ongoingRequestRef.current

      // Clear the reference on successful completion
      ongoingRequestRef.current = null

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
      // Don't show error if request was cancelled
      if (error.isCancelled || error.name === "CancelError") {
        console.log("Optimization request was cancelled")
        return
      }

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
      ongoingRequestRef.current = null
    }
  }

  const handleApplyOptimizations = () => {
    if (!optimizationResults) return

    try {
      // Parse the current sections to get the original structure
      const originalSections = JSON.parse(currentSections)
      console.log("OptimizeOutline: Original sections structure:", originalSections)
      console.log(
        "OptimizeOutline: Optimization suggestions count:",
        optimizationResults.suggestions.length,
      )

      // The backend only returns suggestions for sections with consultDocuments: true
      // We need to reconstruct the full sections array by:
      // 1. Keeping non-consulting sections unchanged from original
      // 2. Updating consulting sections from optimization results

      let suggestionIndex = 0
      const optimizedSections = originalSections.map(
        (originalSection: any, originalIndex: number) => {
          // If this section doesn't consult documents, keep it unchanged
          if (!originalSection.consultDocuments) {
            console.log(
              `OptimizeOutline: Keeping non-consulting section ${originalIndex} unchanged:`,
              originalSection.text?.substring(0, 50),
            )
            return originalSection
          }

          // This section consults documents, so it should have a corresponding suggestion
          if (suggestionIndex >= optimizationResults.suggestions.length) {
            console.warn(
              `OptimizeOutline: No suggestion found for consulting section at original index ${originalIndex}`,
            )
            return originalSection
          }

          const suggestion = optimizationResults.suggestions[suggestionIndex]
          console.log(
            `OptimizeOutline: Processing consulting section ${originalIndex} with suggestion ${suggestionIndex}`,
          )

          let updatedSection
          if (acceptedSuggestions.has(suggestionIndex) && suggestion.needs_revision) {
            // Use edited suggestion if available, otherwise use original suggestion
            updatedSection = {
              ...originalSection,
              text: getSuggestionText(suggestionIndex),
            }
            console.log(`OptimizeOutline: Applied optimization for section ${originalIndex}`)
          } else {
            // Keep the original section unchanged
            updatedSection = {
              ...originalSection,
              text: suggestion.original_section,
            }
            console.log(`OptimizeOutline: Kept original content for section ${originalIndex}`)
          }

          suggestionIndex++
          return updatedSection
        },
      )

      console.log("OptimizeOutline: Final optimized sections:", optimizedSections)
      onOptimizedSections(JSON.stringify(optimizedSections))
      showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)
      handleClose()
    } catch (error) {
      console.error("Error applying optimizations:", error)
      showErrorToast("Failed to apply optimizations. Please try again.")
    }
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
    // Cancel any ongoing request when closing
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

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
              <Dialog.Title>{t("optimizeOutlineModal.title")}</Dialog.Title>
            </Dialog.Header>

            <Dialog.Body overflowY="auto">
              {!showResults ? (
                <VStack gap={6} align="stretch">
                  <Box>
                    <Text fontSize="sm" mb={4} color="gray.600">
                      {t("optimizeOutlineModal.description")}
                    </Text>
                  </Box>

                  <Field label={t("optimizeOutlineModal.groundTruthDocument")} required>
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

                  <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

                  <Field
                    label={t("optimizeOutlineModal.customInstructionsLabel")}
                    helperText={t("optimizeOutlineModal.customInstructionsHelperText")}
                  >
                    <Textarea
                      value={customInstructions}
                      onChange={(e) => setCustomInstructions(e.target.value)}
                      placeholder={t("optimizeOutlineModal.customInstructionsPlaceholder")}
                      rows={3}
                      maxLength={2000}
                    />
                    <Text fontSize="xs" color="gray.500" mt={1}>
                      {customInstructions.length}/2000 {t("optimizeOutlineModal.characters")}
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
                        {t("optimizeOutlineModal.analyzingOutline")}
                      </Text>
                      <Box textAlign="center" mt={3}>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            if (ongoingRequestRef.current) {
                              ongoingRequestRef.current.cancel()
                              ongoingRequestRef.current = null
                            }
                            setOptimizing(false)
                            showSuccessToast("Optimization cancelled")
                          }}
                        >
                          {t("optimizeOutlineModal.cancelAnalysis")}
                        </Button>
                      </Box>
                    </Box>
                  )}
                </VStack>
              ) : (
                <VStack gap={6} align="stretch">
                  <HStack justify="space-between" align="center">
                    <VStack align="start" gap={1}>
                      <Text fontSize="lg" fontWeight="semibold">
                        {t("optimizeOutlineModal.optimizationResults")}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        {
                          optimizationResults?.suggestions.filter(
                            (s: OutlineSuggestion) => s.needs_revision,
                          ).length
                        }{" "}
                        {t("optimizeOutlineModal.sectionsNeedOptimization")}
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
                      {t("optimizeOutlineModal.downloadCsv")}
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
                                  {t("optimizeOutlineModal.section")} {index + 1}
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
                                        <FiCheck size={14} /> {t("optimizeOutlineModal.accepted")}
                                      </>
                                    ) : (
                                      t("optimizeOutlineModal.accept")
                                    )}
                                  </Button>
                                )}
                              </HStack>

                              <Box>
                                <Text fontSize="xs" fontWeight="medium" color="gray.600" mb={1}>
                                  {t("optimizeOutlineModal.originalSectionDescription")}:
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
                                        {t("optimizeOutlineModal.suggestedSectionDescription")}:
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
                  {showResults ? t("optimizeOutlineModal.close") : t("optimizeOutlineModal.cancel")}
                </CancelButton>

                {!showResults ? (
                  <ConfirmButton
                    onClick={handleOptimize}
                    size="md"
                    disabled={!selectedFile || optimizing}
                    loading={optimizing}
                  >
                    {optimizing
                      ? t("optimizeOutlineModal.optimizing")
                      : t("optimizeOutlineModal.optimizeOutline")}
                  </ConfirmButton>
                ) : (
                  <ConfirmButton
                    onClick={handleApplyOptimizations}
                    size="md"
                    disabled={acceptedSuggestions.size === 0}
                  >
                    {t("optimizeOutlineModal.applyOptimizations", {
                      count: acceptedSuggestions.size,
                    })}
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
