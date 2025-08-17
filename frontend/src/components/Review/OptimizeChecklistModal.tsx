import { useState, useRef } from "react"
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Spinner,
  Textarea,
  IconButton,
  Portal,
  Dialog,
} from "@chakra-ui/react"
import { Field } from "../ui/field"
import { FiCheck, FiEdit3, FiSave, FiX } from "react-icons/fi"
import {
  VeraDocChecklist,
  VeradocService,
  ChecklistSuggestion,
  CancelablePromise,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload, { FileItem } from "../Common/FileUpload"
import SearchModeToggle from "../Common/SearchModeToggle"

interface OptimizeChecklistModalProps {
  isOpen: boolean
  onClose: () => void
  checklist: VeraDocChecklist | null
  selectedKnowledgeBase: any
  onOptimized: (optimizedQuestions: string[]) => void
}

const OptimizeChecklistModal: React.FC<OptimizeChecklistModalProps> = ({
  isOpen,
  onClose,
  checklist,
  selectedKnowledgeBase,
  onOptimized,
}) => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [fileItems, setFileItems] = useState<FileItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<ChecklistSuggestion[]>([])
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
  const [isApplying, setIsApplying] = useState(false)
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector")
  const [customInstructions, setCustomInstructions] = useState("")
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)
  const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
  const [editingModes, setEditingModes] = useState<Set<number>>(new Set())
  const [hasOptimized, setHasOptimized] = useState(false)
  const [expandedAnswers, setExpandedAnswers] = useState<Set<number>>(new Set())

  // Add cancelable promise ref for request cancellation
  const ongoingRequestRef = useRef<CancelablePromise<any> | null>(null)

  const handleOptimize = async () => {
    if (!checklist) {
      showErrorToast("No checklist provided for optimization")
      return
    }

    if (!selectedKnowledgeBase) {
      showErrorToast("Please select a knowledge base first")
      return
    }

    if (!checklist.questions || checklist.questions.trim() === "") {
      showErrorToast("Please provide checklist questions to optimize")
      return
    }

    // Cancel any existing request
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

    setIsLoading(true)
    try {
      const validItems = fileItems.filter((item) => item.file.size > 0)
      const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)

      // Store the cancelable promise
      ongoingRequestRef.current = VeradocService.optimizeChecklist({
        knowledgeBaseId: selectedKnowledgeBase.id,
        questions: checklist.questions || "",
        customInstructions: customInstructions || undefined,
        searchMode: searchMode === "full_scan" ? "full_text" : searchMode,
        formData: {
          files: regularFiles,
        },
      })

      const response = await ongoingRequestRef.current

      // Clear the reference on successful completion
      ongoingRequestRef.current = null

      console.log("Optimization response:", response)

      if (response.suggestions && response.suggestions.length > 0) {
        const optimizationCount = response.suggestions.filter(
          (s: ChecklistSuggestion) => s.needs_revision,
        ).length
        setSuggestions(response.suggestions)
        setHasOptimized(true)
        showSuccessToast(
          `Analysis complete! Found ${optimizationCount} suggestions for improvement out of ${response.suggestions.length} questions.`,
        )
      } else {
        showSuccessToast("No optimization suggestions found - your checklist looks good!")
        setSuggestions([])
      }
    } catch (error: any) {
      // Don't show error if request was cancelled
      if (error.isCancelled || error.name === "CancelError") {
        console.log("Optimization request was cancelled")
        return
      }

      console.error("Optimization error:", error)
      showErrorToast("Failed to optimize checklist. Please try again.")
    } finally {
      setIsLoading(false)
      ongoingRequestRef.current = null
    }
  }

  const handleSuggestionToggle = (index: number) => {
    const newAccepted = new Set(acceptedSuggestions)
    if (newAccepted.has(index)) {
      newAccepted.delete(index)
    } else {
      newAccepted.add(index)
    }
    setAcceptedSuggestions(newAccepted)
  }

  const handleEditSuggestion = (index: number) => {
    const suggestion = suggestions[index]
    if (suggestion) {
      setEditingSuggestions(
        new Map(editingSuggestions.set(index, suggestion.suggested_question || "")),
      )
      setEditingModes(new Set(editingModes.add(index)))
    }
  }

  const handleSaveSuggestion = (index: number) => {
    const editedText = editingSuggestions.get(index)
    if (editedText !== undefined) {
      const updatedSuggestions = [...suggestions]
      updatedSuggestions[index] = {
        ...updatedSuggestions[index],
        suggested_question: editedText,
      }
      setSuggestions(updatedSuggestions)
      setEditingModes(new Set([...editingModes].filter((i) => i !== index)))
    }
  }

  const handleCancelEdit = (index: number) => {
    setEditingModes(new Set([...editingModes].filter((i) => i !== index)))
    setEditingSuggestions(new Map([...editingSuggestions].filter(([i]) => i !== index)))
  }

  const handleApplyOptimizations = () => {
    if (acceptedSuggestions.size === 0) {
      showErrorToast("Please select at least one suggestion to apply")
      return
    }

    setIsApplying(true)

    try {
      const optimizedQuestions: string[] = []

      suggestions.forEach((suggestion, index) => {
        if (acceptedSuggestions.has(index) && suggestion.suggested_question) {
          optimizedQuestions.push(suggestion.suggested_question)
        } else {
          optimizedQuestions.push(suggestion.original_question)
        }
      })

      onOptimized(optimizedQuestions)
      showSuccessToast(
        `Applied ${acceptedSuggestions.size} optimization${acceptedSuggestions.size > 1 ? "s" : ""} successfully!`,
      )
      handleClose()
    } catch (error) {
      console.error("Apply optimizations error:", error)
      showErrorToast("Failed to apply optimizations. Please try again.")
    } finally {
      setIsApplying(false)
    }
  }

  const handleDownloadCsv = async () => {
    if (!checklist || !hasOptimized) return

    setLoadingCsvDownload(true)
    try {
      const csvData = suggestions.map((suggestion, index) => ({
        "Question Number": index + 1,
        "Original Question": suggestion.original_question,
        "Needs Revision": suggestion.needs_revision ? "Yes" : "No",
        "Suggested Revision": suggestion.suggested_question || "N/A",
        Analysis: suggestion.reason,
        Status: acceptedSuggestions.has(index) ? "Accepted" : "Not Applied",
      }))

      const headers = Object.keys(csvData[0])
      const csvContent = [
        headers.join(","),
        ...csvData.map((row) =>
          headers
            .map((header) => `"${String(row[header as keyof typeof row]).replace(/"/g, '""')}"`)
            .join(","),
        ),
      ].join("\n")

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      link.setAttribute("href", url)
      link.setAttribute(
        "download",
        `checklist_optimization_${new Date().toISOString().split("T")[0]}.csv`,
      )
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      showSuccessToast("CSV file downloaded successfully!")
    } catch (error) {
      console.error("CSV download error:", error)
      showErrorToast("Failed to download CSV. Please try again.")
    } finally {
      setLoadingCsvDownload(false)
    }
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

  const handleClose = () => {
    // Cancel any ongoing request when closing
    if (ongoingRequestRef.current) {
      ongoingRequestRef.current.cancel()
      ongoingRequestRef.current = null
    }

    setFileItems([])
    setIsLoading(false)
    setSuggestions([])
    setAcceptedSuggestions(new Set())
    setIsApplying(false)
    setSearchMode("vector")
    setCustomInstructions("")
    setLoadingCsvDownload(false)
    setEditingSuggestions(new Map())
    setEditingModes(new Set())
    setHasOptimized(false)
    setExpandedAnswers(new Set())
    onClose()
  }

  if (!isOpen) return null

  return (
    <Portal>
      <Dialog.Root open={isOpen} onOpenChange={(e) => !e.open && handleClose()}>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxW="6xl" maxH="90vh" display="flex" flexDirection="column">
            <Dialog.Header flexShrink={0}>
              <Dialog.Title>Optimize Checklist</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body flex={1} overflow="hidden" display="flex" flexDirection="column">
              <VStack gap={6} align="stretch" height="100%" overflow="hidden">
                <Box>
                  <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />
                </Box>

                <Box>
                  <Text mb={2} fontWeight="medium">
                    Upload Supporting Documents (Optional)
                  </Text>
                  <FileUpload
                    files={fileItems}
                    onFilesChange={setFileItems}
                    showHandwrittenToggle={false}
                  />
                </Box>

                <Field
                  label="Custom Instructions (Optional)"
                  helperText="Enter any additional instructions that should be considered when answering the checklist questions"
                >
                  <Textarea
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    placeholder="e.g., Consider this is a pediatric study when evaluating age-related requirements, This protocol is for a low-risk intervention, etc."
                    rows={3}
                    maxLength={2000}
                  />
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    {customInstructions.length}/2000 characters
                  </Text>
                </Field>

                <HStack justifyContent="space-between">
                  <Button
                    onClick={handleOptimize}
                    loading={isLoading}
                    colorScheme="blue"
                    disabled={!checklist?.questions}
                  >
                    {isLoading ? "Analyzing..." : "Analyze Checklist"}
                  </Button>

                  {hasOptimized && suggestions.length > 0 && (
                    <Button
                      onClick={handleDownloadCsv}
                      loading={loadingCsvDownload}
                      variant="outline"
                    >
                      {loadingCsvDownload ? "Downloading..." : <>Download CSV</>}
                    </Button>
                  )}
                </HStack>

                {isLoading && (
                  <Box textAlign="center" py={8}>
                    <Spinner size="lg" />
                    <Text mt={4} color="gray.600">
                      Analyzing your checklist for optimization opportunities...
                    </Text>
                    <Button
                      mt={4}
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (ongoingRequestRef.current) {
                          ongoingRequestRef.current.cancel()
                          ongoingRequestRef.current = null
                        }
                        setIsLoading(false)
                        showSuccessToast("Optimization cancelled")
                      }}
                    >
                      Cancel Analysis
                    </Button>
                  </Box>
                )}

                {suggestions.length > 0 && (
                  <Box flex={1} overflow="hidden" display="flex" flexDirection="column">
                    <Text fontWeight="medium" mb={4}>
                      Optimization Suggestions ({suggestions.filter((s) => s.needs_revision).length}{" "}
                      improvements found)
                    </Text>

                    <Box flex={1} overflow="auto" pr={2}>
                      <VStack gap={4} align="stretch">
                        {suggestions.map((suggestion, index) => (
                          <Box
                            key={index}
                            p={4}
                            border="1px solid"
                            borderColor={suggestion.needs_revision ? "blue.200" : "gray.200"}
                            borderRadius="md"
                            bg={suggestion.needs_revision ? "blue.50" : "gray.50"}
                          >
                            <VStack align="stretch" gap={3}>
                              <HStack justifyContent="space-between" align="flex-start">
                                <Text fontWeight="medium" color="gray.700" flex={1}>
                                  Question {index + 1}
                                </Text>
                                {suggestion.needs_revision && (
                                  <HStack gap={2}>
                                    <IconButton
                                      aria-label="Edit suggestion"
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => handleEditSuggestion(index)}
                                      disabled={editingModes.has(index)}
                                    >
                                      <FiEdit3 />
                                    </IconButton>
                                    <Button
                                      size="sm"
                                      variant={acceptedSuggestions.has(index) ? "solid" : "outline"}
                                      colorScheme={
                                        acceptedSuggestions.has(index) ? "green" : "gray"
                                      }
                                      onClick={() => handleSuggestionToggle(index)}
                                    >
                                      {acceptedSuggestions.has(index) ? (
                                        <>
                                          <FiCheck /> Selected
                                        </>
                                      ) : (
                                        "Select"
                                      )}
                                    </Button>
                                  </HStack>
                                )}
                              </HStack>

                              <Box>
                                <Text fontSize="sm" fontWeight="medium" color="gray.600" mb={1}>
                                  Original:
                                </Text>
                                <Text fontSize="sm" bg="gray.50" p={2} borderRadius="md">
                                  {suggestion.original_question}
                                </Text>
                              </Box>

                              {suggestion.needs_revision && suggestion.suggested_question && (
                                <Box>
                                  <Text fontSize="sm" fontWeight="medium" color="blue.600" mb={1}>
                                    Suggested Improvement:
                                  </Text>
                                  {editingModes.has(index) ? (
                                    <VStack align="stretch" gap={2}>
                                      <Textarea
                                        value={editingSuggestions.get(index) || ""}
                                        onChange={(e) =>
                                          setEditingSuggestions(
                                            new Map(editingSuggestions.set(index, e.target.value)),
                                          )
                                        }
                                        size="sm"
                                        resize="vertical"
                                        minH="80px"
                                      />
                                      <HStack gap={2}>
                                        <Button
                                          size="sm"
                                          colorScheme="green"
                                          onClick={() => handleSaveSuggestion(index)}
                                        >
                                          <FiSave /> Save
                                        </Button>
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          onClick={() => handleCancelEdit(index)}
                                        >
                                          <FiX /> Cancel
                                        </Button>
                                      </HStack>
                                    </VStack>
                                  ) : (
                                    <Text
                                      fontSize="sm"
                                      bg="blue.50"
                                      p={2}
                                      borderRadius="md"
                                      color="blue.800"
                                    >
                                      {suggestion.suggested_question}
                                    </Text>
                                  )}
                                </Box>
                              )}

                              {!suggestion.needs_revision && (
                                <Box>
                                  <Text fontSize="sm" fontWeight="medium" color="green.600" mb={1}>
                                    Status:
                                  </Text>
                                  <Text
                                    fontSize="sm"
                                    color="green.700"
                                    bg="green.50"
                                    p={2}
                                    borderRadius="md"
                                  >
                                    ✓ This question looks good as is
                                  </Text>
                                </Box>
                              )}

                              <Box>
                                <HStack justifyContent="space-between" align="center">
                                  <Text fontSize="sm" fontWeight="medium" color="gray.600">
                                    Analysis:
                                  </Text>
                                  <Button
                                    size="xs"
                                    variant="ghost"
                                    onClick={() => toggleAnswerExpansion(index)}
                                  >
                                    {expandedAnswers.has(index) ? "Show Less" : "Show More"}
                                  </Button>
                                </HStack>
                                <Text
                                  fontSize="sm"
                                  color="gray.700"
                                  bg="gray.50"
                                  p={2}
                                  borderRadius="md"
                                  style={{
                                    overflow: expandedAnswers.has(index) ? "visible" : "hidden",
                                    display: expandedAnswers.has(index) ? "block" : "-webkit-box",
                                    WebkitLineClamp: expandedAnswers.has(index) ? "none" : 2,
                                    WebkitBoxOrient: "vertical" as const,
                                  }}
                                >
                                  {suggestion.reason}
                                </Text>
                              </Box>
                            </VStack>
                          </Box>
                        ))}
                      </VStack>
                    </Box>

                    {acceptedSuggestions.size > 0 && (
                      <Box mt={4} pt={4} borderTop="1px" borderColor="gray.200">
                        <HStack justifyContent="space-between">
                          <Text fontSize="sm" color="gray.600">
                            {acceptedSuggestions.size} optimization
                            {acceptedSuggestions.size > 1 ? "s" : ""} selected
                          </Text>
                          <Button
                            onClick={handleApplyOptimizations}
                            loading={isApplying}
                            colorScheme="green"
                          >
                            {isApplying ? "Applying..." : <>Apply Selected Optimizations</>}
                          </Button>
                        </HStack>
                      </Box>
                    )}
                  </Box>
                )}
              </VStack>
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </Portal>
  )
}

export default OptimizeChecklistModal
