import { useState } from "react"
import { Box, Button, VStack, HStack, Text, Spinner, Card, Separator } from "@chakra-ui/react"
import { DialogBody, DialogContent, DialogHeader, DialogRoot, DialogTitle } from "@chakra-ui/react"
import { FiCheck } from "react-icons/fi"
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

  const handleApplySuggestions = () => {
    if (suggestions.length === 0) return

    const optimizedQuestions = suggestions.map((suggestion, index) => {
      if (acceptedSuggestions.has(index) && suggestion.needs_revision) {
        return suggestion.suggested_question
      }
      return suggestion.original_question
    })

    onOptimized(optimizedQuestions)
    showSuccessToast(`Applied ${acceptedSuggestions.size} optimization suggestions`)
    handleClose()
  }

  const handleClose = () => {
    setFileItems([])
    setSuggestions([])
    setAcceptedSuggestions(new Set())
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
                  <Text fontSize="lg" fontWeight="bold">
                    Optimization Suggestions
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {suggestions.filter((s) => s.needs_revision).length} questions need optimization
                  </Text>
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
                                  <Text fontSize="sm" fontWeight="medium" mb={1}>
                                    Suggested Question:
                                  </Text>
                                  <Text
                                    fontSize="sm"
                                    p={2}
                                    bg="blue.50"
                                    borderRadius="md"
                                    border="1px solid"
                                    borderColor="blue.200"
                                  >
                                    {suggestion.suggested_question}
                                  </Text>
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
                                    Current Answer:
                                  </Text>
                                  <Text fontSize="sm" color="gray.600">
                                    {suggestion.current_answer.substring(0, 200)}
                                    {suggestion.current_answer.length > 200 ? "..." : ""}
                                  </Text>
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
