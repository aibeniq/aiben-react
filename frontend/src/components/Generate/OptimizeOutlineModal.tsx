import { VStack, HStack, Dialog, Portal, Text, Box, Textarea } from "@chakra-ui/react"
import { Field } from "../ui/field"
import CancelButton from "../ui/cancel-button"
import ConfirmButton from "../ui/confirm-button"
import { useState } from "react"
import { ReportgenieService, OptimizedOutlineResponse, OutlineSuggestion } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

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
  const [optimizationResults, setOptimizationResults] = useState<OptimizedOutlineResponse | null>(
    null,
  )
  const [showResults, setShowResults] = useState(false)

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
      setOptimizing(true) // Use SDK method following the optimize-checklist pattern
      const result = await ReportgenieService.optimizeOutline({
        knowledgeBaseId: knowledgeBaseId,
        outlineId: outlineId,
        sections: currentSections,
        customInstructions: customInstructions || undefined,
        formData: { files: [selectedFile] },
      })

      setOptimizationResults(result)
      setShowResults(true)
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
    if (optimizationResults) {
      onOptimizedSections(JSON.stringify(optimizationResults.optimized_sections))
      showSuccessToast("Optimized sections applied!")
      handleClose()
    }
  }

  const handleClose = () => {
    setSelectedFile(null)
    setCustomInstructions("")
    setOptimizationResults(null)
    setShowResults(false)
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
                  <Box>
                    <Text fontSize="lg" fontWeight="semibold" mb={2}>
                      Optimization Results
                    </Text>
                    <Text fontSize="sm" color="gray.600" mb={4}>
                      {optimizationResults?.analysis_summary}
                    </Text>
                  </Box>

                  <VStack gap={4} align="stretch">
                    {optimizationResults?.suggestions.map(
                      (suggestion: OutlineSuggestion, index: number) => (
                        <Box
                          key={index}
                          p={4}
                          border="1px solid"
                          borderColor={suggestion.needs_revision ? "orange.200" : "green.200"}
                          borderRadius="md"
                          bg={suggestion.needs_revision ? "orange.50" : "green.50"}
                        >
                          <HStack justify="space-between" mb={2}>
                            <Text fontWeight="semibold" fontSize="sm">
                              Section {index + 1}
                            </Text>
                            <Text
                              fontSize="xs"
                              px={2}
                              py={1}
                              borderRadius="md"
                              bg={suggestion.needs_revision ? "orange.100" : "green.100"}
                              color={suggestion.needs_revision ? "orange.700" : "green.700"}
                            >
                              {suggestion.needs_revision ? "Needs Revision" : "Good as is"}
                            </Text>
                          </HStack>

                          <VStack gap={3} align="stretch">
                            <Box>
                              <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                Original Section Description:
                              </Text>
                              <Text fontSize="sm">{suggestion.original_section}</Text>
                            </Box>

                            {suggestion.needs_revision && (
                              <Box>
                                <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                  Suggested Section Description:
                                </Text>
                                <Text fontSize="sm" fontWeight="medium" color="orange.700">
                                  {suggestion.suggested_section}
                                </Text>
                              </Box>
                            )}

                            <Box>
                              <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                Reason:
                              </Text>
                              <Text fontSize="sm">{suggestion.reason}</Text>
                            </Box>

                            <Box>
                              <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                Generated Content (with current description):
                              </Text>
                              <Box
                                fontSize="sm"
                                p={2}
                                bg="gray.50"
                                borderRadius="md"
                                maxH="150px"
                                overflowY="auto"
                                border="1px solid"
                                borderColor="gray.200"
                              >
                                <Text whiteSpace="pre-wrap">
                                  {suggestion.current_output || "No content generated"}
                                </Text>
                              </Box>
                            </Box>

                            <Box>
                              <Text fontSize="xs" fontWeight="medium" color="gray.600">
                                Ground-Truth Content (from uploaded document):
                              </Text>
                              <Box
                                fontSize="sm"
                                p={2}
                                bg="blue.50"
                                borderRadius="md"
                                maxH="150px"
                                overflowY="auto"
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
                        </Box>
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
                    disabled={!optimizationResults?.suggestions.some((s: any) => s.needs_revision)}
                  >
                    Apply Optimizations
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
