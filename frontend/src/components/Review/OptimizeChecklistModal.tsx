import { useState } from "react"
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Spinner,
  Card,
  Separator,
  Textarea,
  IconButton,
} from "@chakra-ui/react"
import { DialogBody, DialogContent, DialogHeader, DialogRoot, DialogTitle } from "@chakra-ui/react"
import { FiCheck, FiEdit3, FiSave, FiX, FiDownload } from "react-icons/fi"
import { VeraDocChecklist, VeradocService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload from "../Common/FileUpload"

interface OptimizeChecklistModalProps {
  isOpen: boolean
  onClose: () => void
  checklist: VeraDocChecklist | null
  selectedKnowledgeBase: any
  onOptimized: (optimizedQuestions: string[]) => void
}

interface ChecklistSuggestion {
  original_question: string
  suggested_question: string
  reason: string
  current_answer: string
  needs_revision: boolean
}

interface FileItem {
  file: File
  isHandwritten: boolean
}

const OptimizeChecklistModal = ({
  isOpen,
  onClose,
  checklist,
  selectedKnowledgeBase,
  onOptimized,
}: OptimizeChecklistModalProps) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<ChecklistSuggestion[]>([])
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // State for editing suggestions
  const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
  const [editingModes, setEditingModes] = useState<Set<number>>(new Set())

  // State for expanding current answers
  const [expandedAnswers, setExpandedAnswers] = useState<Set<number>>(new Set())

  const handleOptimize = async () => {
    if (!checklist) {
      showErrorToast("No checklist selected")
      return
    }

    if (!selectedKnowledgeBase) {
      showErrorToast("Please select a knowledge base")
      return
    }

    if (fileItems.length === 0) {
      showErrorToast("Please upload a test document")
      return
    }

    setLoading(true)
    setSuggestions([])

    try {
      const validItems = fileItems.filter((item) => item.file.size > 0)
      const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)

      const response = await VeradocService.optimizeChecklist({
        questions: checklist.questions || "",
        knowledgeBaseId: selectedKnowledgeBase.id,
        formData: {
          files: regularFiles,
        },
      })

      setSuggestions(response.suggestions || [])

      if (response.suggestions && response.suggestions.length > 0) {
        const optimizationCount = response.suggestions.filter((s) => s.needs_revision).length
        if (optimizationCount > 0) {
          showSuccessToast(`Found ${optimizationCount} questions that could be optimized`)
        } else {
          showSuccessToast("All questions are already well-optimized!")
        }
      }
    } catch (error: any) {
      console.error("Error optimizing checklist:", error)
      showErrorToast(`Failed to optimize checklist: ${error.message || "Unknown error"}`)
    } finally {
      setLoading(false)
    }
  }

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

    // Initialize with the current suggested question if not already editing
    if (!editingSuggestions.has(index)) {
      const newEditingSuggestions = new Map(editingSuggestions)
      newEditingSuggestions.set(index, suggestions[index].suggested_question)
      setEditingSuggestions(newEditingSuggestions)
    }
  }

  const cancelEditingSuggestion = (index: number) => {
    const newEditingModes = new Set(editingModes)
    newEditingModes.delete(index)
    setEditingModes(newEditingModes)

    // Reset to original suggestion
    const newEditingSuggestions = new Map(editingSuggestions)
    newEditingSuggestions.set(index, suggestions[index].suggested_question)
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
    return editingSuggestions.get(index) || suggestions[index]?.suggested_question || ""
  }

  const toggleAnswerExpansion = (index: number) => {
    const newExpanded = new Set(expandedAnswers)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedAnswers(newExpanded)
  }

  const handleApplySuggestions = () => {
    if (suggestions.length === 0) return

    // Create a map of original questions to their suggestions for accepted items
    const suggestionMap = new Map<string, string>()

    suggestions.forEach((suggestion, index) => {
      if (acceptedSuggestions.has(index) && suggestion.needs_revision) {
        // Use edited suggestion if available, otherwise use original suggestion
        suggestionMap.set(suggestion.original_question, getSuggestionText(index))
      }
    })

    // Build the optimized questions array by replacing accepted suggestions
    const optimizedQuestions = suggestions.map((suggestion) => {
      const originalQuestion = suggestion.original_question
      if (suggestionMap.has(originalQuestion)) {
        return suggestionMap.get(originalQuestion) || originalQuestion
      }
      return originalQuestion
    })

    onOptimized(optimizedQuestions)
    showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)
    handleClose()
  }

  const handleDownloadCsv = async () => {
    if (suggestions.length === 0) {
      showErrorToast("No optimization results to download")
      return
    }

    setLoadingCsvDownload(true)

    try {
      // Create the data structure expected by the backend
      const csvData = {
        suggestions: suggestions,
        analysis_summary: "Checklist optimization results export", // You could store this from the optimization response
      }

      const response = await VeradocService.generateOptimizationCsv({
        requestBody: { content: JSON.stringify(csvData) },
      })

      // Handle the blob response
      const blob = new Blob([response as any], { type: "text/csv" })
      const url = window.URL.createObjectURL(blob)

      // Create download link
      const a = document.createElement("a")
      a.href = url
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-").split("T")[0]
      a.download = `checklist_optimization_${timestamp}.csv`
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
    setFileItems([])
    setSuggestions([])
    setAcceptedSuggestions(new Set())
    setEditingSuggestions(new Map())
    setEditingModes(new Set())
    setExpandedAnswers(new Set())
    setLoadingCsvDownload(false)
    onClose()
  }

  return (
    <DialogRoot open={isOpen} onOpenChange={({ open }) => !open && handleClose()}>
      <DialogContent maxW="6xl" maxH="90vh" display="flex" flexDirection="column">
        <DialogHeader flexShrink={0}>
          <DialogTitle>Optimize Checklist</DialogTitle>
        </DialogHeader>
        <DialogBody flex={1} overflow="hidden" display="flex" flexDirection="column">
          <VStack gap={6} align="stretch" height="100%" overflow="hidden">
            <Box>
              <Text mb={2} fontWeight="medium">
                Upload a document that SHOULD meet all checklist requirements:
              </Text>
              <FileUpload
                files={fileItems}
                onFilesChange={setFileItems}
                showHandwrittenToggle={false}
              />
            </Box>

            <HStack justify="space-between">
              <Text fontSize="sm" color="gray.600">
                Knowledge Base: {selectedKnowledgeBase?.title || "None selected"}
              </Text>
              <Button
                onClick={handleOptimize}
                disabled={fileItems.length === 0 || !selectedKnowledgeBase || loading}
                loading={loading}
                colorPalette="blue"
              >
                {loading ? "Analyzing..." : "Optimize Checklist"}
              </Button>
            </HStack>

            {loading && (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" mb={4} />
                <Text>Running optimization analysis...</Text>
              </Box>
            )}

            {suggestions.length > 0 && !loading && (
              <VStack gap={4} align="stretch" flex={1} overflow="hidden">
                <Separator />
                <HStack justify="space-between" flexShrink={0}>
                  <VStack align="start" gap={1}>
                    <Text fontSize="lg" fontWeight="bold">
                      Optimization Suggestions
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {suggestions.filter((s) => s.needs_revision).length} questions need
                      optimization
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
                </HStack>{" "}
                <Box flex={1} overflow="auto" pr={2}>
                  <VStack gap={4} align="stretch">
                    {suggestions.map((suggestion, index) => (
                      <Card.Root
                        key={index}
                        variant={suggestion.needs_revision ? "elevated" : "subtle"}
                      >
                        <Card.Body>
                          <VStack gap={3} align="stretch">
                            <HStack justify="space-between">
                              <Text fontWeight="bold" fontSize="sm" color="gray.600">
                                Question {index + 1}
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
                              <Text fontSize="sm" fontWeight="medium" mb={1}>
                                Original Question:
                              </Text>
                              <Text fontSize="sm" p={2} bg="gray.50" borderRadius="md">
                                {suggestion.original_question}
                              </Text>
                            </Box>

                            {suggestion.needs_revision ? (
                              <>
                                <Box>
                                  <HStack justify="space-between" mb={1}>
                                    <Text fontSize="sm" fontWeight="medium">
                                      Suggested Question:
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
                                  <Text fontSize="sm" fontWeight="medium" mb={1}>
                                    Reason for Change:
                                  </Text>
                                  <Text fontSize="sm" color="gray.600">
                                    {suggestion.reason}
                                  </Text>
                                </Box>

                                <Box>
                                  <Text fontSize="sm" fontWeight="medium" mb={1}>
                                    Current Answer (why this needs optimization):
                                  </Text>
                                  <Box
                                    p={2}
                                    bg="orange.50"
                                    borderRadius="md"
                                    border="1px solid"
                                    borderColor="orange.200"
                                  >
                                    <Text fontSize="sm" color="gray.600">
                                      {expandedAnswers.has(index)
                                        ? suggestion.current_answer
                                        : suggestion.current_answer.substring(0, 300)}
                                      {!expandedAnswers.has(index) &&
                                      suggestion.current_answer.length > 300
                                        ? "..."
                                        : ""}
                                    </Text>
                                    {suggestion.current_answer.length > 300 && (
                                      <Button
                                        size="xs"
                                        variant="ghost"
                                        mt={1}
                                        onClick={() => toggleAnswerExpansion(index)}
                                        colorPalette="orange"
                                      >
                                        {expandedAnswers.has(index) ? "Show Less" : "Show More"}
                                      </Button>
                                    )}
                                  </Box>
                                </Box>
                              </>
                            ) : (
                              <Box>
                                <Text fontSize="sm" color="green.600" fontWeight="medium">
                                  ✓ This question is already well-optimized
                                </Text>
                              </Box>
                            )}
                          </VStack>
                        </Card.Body>
                      </Card.Root>
                    ))}
                  </VStack>
                </Box>
                <HStack justify="space-between" pt={4} flexShrink={0}>
                  <Button variant="outline" onClick={handleClose}>
                    Cancel
                  </Button>
                  <Button
                    colorPalette="blue"
                    onClick={handleApplySuggestions}
                    disabled={acceptedSuggestions.size === 0}
                  >
                    Apply {acceptedSuggestions.size} Suggestion
                    {acceptedSuggestions.size !== 1 ? "s" : ""}
                  </Button>
                </HStack>
              </VStack>
            )}
          </VStack>
        </DialogBody>
      </DialogContent>
    </DialogRoot>
  )
}

export default OptimizeChecklistModal
