import {
  type KnowledgeBasePublic,
  type VeraDocChecklist,
  VeradocService,
} from "@/client"
import type { CancelablePromise } from "@/client/core/CancelablePromise"
import FileUpload, { type FileItem } from "@/components/Common/FileUpload"
import SearchModeToggle from "@/components/Common/SearchModeToggle"
import SourceLink from "@/components/Common/SourceLink"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import DownloadButton from "@/components/ui/download-button"
import HelpTooltip from "@/components/ui/help-tooltip"
import useCustomToast from "@/hooks/useCustomToast"
import { useKnowledgeBases } from "@/hooks/useKnowledgeBases"
import { useOperationCancellation } from "@/hooks/useOperationCancellation"
import { useVeradocProgress } from "@/hooks/useVeradocProgress"
import {
  Accordion,
  Box,
  Button,
  Container,
  HStack,
  Heading,
  Progress,
  Spinner,
  Tabs,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import {
  FiCheck,
  FiCopy,
  FiDatabase,
  FiFileText,
  FiTrash2,
} from "react-icons/fi"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import KnowledgeBaseSelectionModal from "../../components/Common/KnowledgeBaseSelectionModal"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import ChecklistTable from "../../components/Review/ChecklistTable"
import { useResults } from "../../contexts/ResultsContext"
import { copyToClipboard } from "../../utils/copyToClipboard"
import { getCleanFileName } from "../../utils/filename"
import { cleanRTFFormatting } from "../../utils/rtfCleaner"

interface QuestionData {
  id: string
  text: string
  consultDocuments: boolean
}

const VeraDoc = () => {
  const { t } = useTranslation()

  // Helper function to safely get translations with fallback
  const getTranslation = (key: string, fallback: string) => {
    try {
      const translated = t(key)
      // Check if translation is just the key (indicating missing translation)
      return translated === key ? fallback : translated
    } catch {
      return fallback
    }
  }
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    reviewResults: results,
    setReviewResults: setResults,
    reviewActiveTab: activeTab,
    setReviewActiveTab: setActiveTab,
    reviewInputs,
    setReviewInputs,
    clearReviewResults,
  } = useResults()

  // Initialize form state from persisted inputs or defaults
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] =
    useState<KnowledgeBasePublic | null>(
      reviewInputs?.selectedKnowledgeBase || null,
    )
  const { knowledgeBases, showAllUsers, toggleShowAllUsers } =
    useKnowledgeBases() // Respect All Users toggle state
  const { registerOperation } = useOperationCancellation()
  const abortControllerRef = useRef<AbortController | null>(null)
  const ongoingRequest = useRef<CancelablePromise<any> | null>(null)

  // Progress tracking
  const [taskId, setTaskId] = useState<string | null>(null)
  const progress = useVeradocProgress(taskId)
  const hasHandledCompletionRef = useRef(false)

  // Debug: Log progress changes
  useEffect(() => {
    console.log("📊 REVIEW PAGE: Progress object updated:", {
      message: progress.message,
      percentage: progress.percentage,
      isActive: progress.isActive,
      completed: progress.completed,
    })
  }, [progress])

  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showChecklistModal, setShowChecklistModal] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  const [questions, setQuestions] = useState(reviewInputs?.questions || "")
  const [structuredQuestions, setStructuredQuestions] = useState<
    QuestionData[]
  >([])
  const [customInstructions, setCustomInstructions] = useState(
    reviewInputs?.customInstructions || "",
  )

  const [fileItems, setFileItems] = useState<FileItem[]>(
    reviewInputs?.fileItems || [],
  )

  const [loading, setLoading] = useState<boolean>(false)

  const [checklists, setChecklists] = useState<VeraDocChecklist[]>([])
  const [selectedChecklist, setSelectedChecklist] =
    useState<VeraDocChecklist | null>(reviewInputs?.selectedChecklist || null)

  // Search mode state for main review functionality
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    reviewInputs?.searchMode || "vector",
  )

  // State to track which citations are expanded - using object instead of Set
  const [expandedCitations, setExpandedCitations] = useState<
    Record<string, boolean>
  >({})

  // Function to toggle citation expansion
  const toggleCitationExpansion = (
    resultIndex: number,
    pairIndex: number,
    citationIndex: number,
  ) => {
    const citationKey = `${resultIndex}-${pairIndex}-${citationIndex}`
    setExpandedCitations((prev) => ({
      ...prev,
      [citationKey]: !prev[citationKey],
    }))
  }

  // Function to check if a citation is expanded
  const isCitationExpanded = (
    resultIndex: number,
    pairIndex: number,
    citationIndex: number,
  ) => {
    const citationKey = `${resultIndex}-${pairIndex}-${citationIndex}`
    return expandedCitations[citationKey] || false
  }

  // Handle progress completion
  useEffect(() => {
    if (
      taskId &&
      progress.completed &&
      !hasHandledCompletionRef.current &&
      progress.results
    ) {
      console.log("✅ Review task completed with results, processing...")
      hasHandledCompletionRef.current = true

      // Process the results from progress
      const data = { results: progress.results }

      // Handle optimized multi-file results
      let reviewData = []

      if (data.results.multi_file_results) {
        // 🚀 New optimized multi-file format
        reviewData = data.results.multi_file_results.map((fileResult: any) => ({
          filename: fileResult.filename || "Unknown File",
          displayResults: fileResult.final_evaluation || "",
          qaPairs: fileResult.qa_pairs || [],
          interactionId: fileResult.interaction_id,
        }))

        console.log(
          `✅ Processed ${data.results.total_files_processed} files with optimized context sharing`,
        )
        console.log(
          `🚀 Context pre-fetch count: ${data.results.context_prefetch_count}`,
        )
        console.log(
          `🚀 Optimization applied: ${data.results.optimization_applied}`,
        )

        showSuccessToast(
          t("review.reviewSuccessMultiple", { count: reviewData.length }),
        )
      } else {
        // Fallback to single file format for backward compatibility
        const interactionId = data.results.interaction_id
        console.log("Review interactionId for feedback:", interactionId)

        reviewData = [
          {
            filename: data.results?.filename || "Review Result",
            displayResults: data.results?.final_evaluation || "",
            qaPairs: data.results?.qa_pairs || [],
            interactionId: interactionId,
          },
        ]

        const optimizationNote = data.results.optimization_applied
          ? " (Optimized)"
          : ""
        showSuccessToast(
          t("review.reviewSuccess") + optimizationNote,
        )
      }

      setResults(reviewData)

      // Clear taskId after a short delay to allow user to see 100% completion
      setTimeout(() => {
        setTaskId(null)
        hasHandledCompletionRef.current = false
        setLoading(false)
      }, 1500)
    }

    if (taskId && progress.error) {
      console.log("❌ Review task failed:", progress.error)
      setTaskId(null)
      setLoading(false)
      hasHandledCompletionRef.current = false
      showErrorToast(progress.error)
    }
  }, [taskId, progress.completed, progress.error, progress.results])

  // Reset completion handler when taskId changes
  useEffect(() => {
    if (taskId) {
      console.log("🔄 New review task started, resetting completion handler")
      hasHandledCompletionRef.current = false
    }
  }, [taskId])

  // Handle feedback submission
  const handleFeedbackSubmitted = (type: string) => {
    console.log("Feedback submitted for review result:", type)
    showSuccessToast(`Thank you for marking this response as ${type}!`)
  }

  // Save input parameters to context whenever they change
  useEffect(() => {
    setReviewInputs({
      selectedKnowledgeBase,
      selectedChecklist,
      questions,
      customInstructions,
      searchMode,
      fileItems,
    })
  }, [
    selectedKnowledgeBase,
    selectedChecklist,
    questions,
    customInstructions,
    searchMode,
    fileItems,
    setReviewInputs,
  ])

  // Clear inputs and restore from context when clear button is clicked
  const handleClearResults = () => {
    clearReviewResults() // Clears both results and inputs
    // Reset local state to blank
    setSelectedKnowledgeBase(null)
    setSelectedChecklist(null)
    setQuestions("")
    setCustomInstructions("")
    setSearchMode("vector")
    setFileItems([])
  }

  // Reset active tab when results change
  useEffect(() => {
    console.log("Review tab - results changed:", results.length, results)
    if (results.length > 0) {
      setActiveTab(0)
    }
  }, [results.length])

  // Debug effect to log context state
  useEffect(() => {
    console.log("Review tab - context state:", {
      resultsLength: results.length,
      activeTab,
      firstResult: results[0]?.filename,
    })
  }, [results, activeTab])

  const handleCopyReport = async () => {
    try {
      const activeTabIndex = activeTab
      const activeResult = results[activeTabIndex]

      if (!activeResult) {
        showErrorToast("No active result to copy")
        return
      }

      let fullText = "# Evaluation Summary\n\n"

      // Add the active result's display content and QA pairs
      fullText += `${activeResult.displayResults}\n\n`

      activeResult.qaPairs.forEach((pair, pairIndex) => {
        fullText += `## Question ${pairIndex + 1}: ${pair.question}\n\n`
        fullText += `### Answer\n${pair.answer}\n\n`
        fullText += `### Relevant Policy Context\n${pair.context}\n\n`
      })

      await copyToClipboard(fullText)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast(t("review.reportCopied"))
    } catch (err) {
      console.error("Failed to copy report:", err)
      showErrorToast("Failed to copy report to clipboard")
    }
  }

  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true)

      const activeTabIndex = activeTab
      const activeResult = results[activeTabIndex]

      if (!activeResult) {
        showErrorToast("No active result to download")
        return
      }

      let fullText = "# Evaluation Summary\n\n"
      fullText += `${activeResult.displayResults}\n\n`

      activeResult.qaPairs.forEach((pair, pairIndex) => {
        fullText += `## Question ${pairIndex + 1}: ${pair.question}\n\n`
        fullText += `### Answer\n${pair.answer}\n\n`
        fullText += `### Relevant Policy Context\n${pair.context}\n\n`
      })

      const response = await VeradocService.generateDocx({
        requestBody: { content: fullText },
      })

      console.log("Received DOCX response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)
      console.log(
        "Response instanceof ArrayBuffer:",
        response instanceof ArrayBuffer,
      )

      let blob
      if (response instanceof Blob) {
        console.log("Response is a Blob")
        blob = response
      } else if (response instanceof ArrayBuffer) {
        console.log("Response is an ArrayBuffer")
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        console.log("Response is a string or unexpected type")
        blob = new Blob([response as any], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      console.log("Final DOCX blob:", blob)
      console.log("Blob size:", blob.size)
      console.log("Blob type:", blob.type)

      const url = window.URL.createObjectURL(blob)
      console.log("Created DOCX object URL:", url)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      const filename = activeResult.filename.replace(/[^a-zA-Z0-9]/g, "_")
      a.href = url
      a.download = `Evaluation_${filename}_${timestamp}.docx`

      console.log(
        "DOCX download filename:",
        `Evaluation_${filename}_${timestamp}.docx`,
      )
      console.log("About to trigger DOCX download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("DOCX download triggered successfully")
      showSuccessToast("Evaluation downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download report:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(
        `Failed to download evaluation: ${err.message || "Unknown error"}`,
      )
    } finally {
      console.log("DOCX download process completed")
      setLoadingDownload(false)
    }
  }

  const handleDownloadCsv = async () => {
    try {
      setLoadingCsvDownload(true)

      const activeTabIndex = activeTab
      const activeResult = results[activeTabIndex]

      if (!activeResult) {
        showErrorToast("No active result to download")
        return
      }

      // Prepare the data for CSV generation
      const csvData = {
        qa_pairs: activeResult.qaPairs,
        final_evaluation: activeResult.displayResults,
      }

      const response = await VeradocService.generateCsv({
        requestBody: { content: JSON.stringify(csvData) },
      })

      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], {
          type: "text/csv",
        })
      } else {
        blob = new Blob([response as any], {
          type: "text/csv",
        })
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      const filename = activeResult.filename.replace(/[^a-zA-Z0-9]/g, "_")
      a.href = url
      a.download = `VeraDoc_Review_${filename}_${timestamp}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("CSV downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download CSV:", err)
      showErrorToast(
        `Failed to download CSV: ${err.message || "Unknown error"}`,
      )
    } finally {
      setLoadingCsvDownload(false)
    }
  }

  // Use shared filename utility
  const getDisplayFileName = getCleanFileName

  // Helper function to format source display with page number
  const formatSourceWithPage = (
    source: string,
    page?: number | string,
  ): string => {
    const fileName = getDisplayFileName(source)
    if (page && page !== "" && page !== 0) {
      return `${fileName} (Page ${page})`
    }
    return fileName
  }

  const fetchChecklists = async () => {
    try {
      const data = await VeradocService.getChecklists()
      setChecklists(data)
    } catch (error) {
      console.error("Error fetching checklists:", error)
    }
  }

  useEffect(() => {
    fetchChecklists()
  }, [])

  // Optimized single-request mutation for both single and multi-file processing
  const mutation = useMutation({
    mutationFn: async (data: {
      questions: string
      knowledgeBaseId: string
      files: File[]
      handwrittenFiles: File[]
      customInstructions?: string
      searchMode?: "vector" | "full_scan"
    }) => {
      // Clear previous results
      setResults([])
      setLoading(true)

      // STEP 1: Create a task to get the task_id for progress tracking (backend creates it in Redis immediately)
      console.log("🎯 Creating review task for progress tracking...")
      const taskResponse = await VeradocService.createReviewTask()

      const newTaskId = (taskResponse as any).task_id
      console.log("📋 Review task_id created by backend:", newTaskId)
      setTaskId(newTaskId)

      console.log(
        "🎯 Submitting review (synchronous with progress tracking)...",
      )
      console.log("Number of files:", data.files.length)
      console.log("Search mode being sent to backend:", data.searchMode)

      // STEP 2: Call the review endpoint with the task_id
      // Backend will use this task_id for progress tracking
      const promise = VeradocService.processRagChecklist({
        questions: data.questions,
        knowledgeBaseId: data.knowledgeBaseId,
        customInstructions: data.customInstructions,
        searchMode: data.searchMode,
        taskId: newTaskId, // Pass the task_id to the endpoint
        formData: {
          files: data.files,
        },
      })

      // Register the operation for automatic cancellation on navigation
      const cancellablePromise = registerOperation(promise)
      ongoingRequest.current = cancellablePromise

      // Wait for the full response (processes synchronously while updating progress)
      return cancellablePromise
    },
    onSuccess: (data: any) => {
      console.log("🚀 Review backend processing complete:", data)

      // Check if the request was cancelled
      if (data.results.status === "cancelled") {
        console.log("Review operation was cancelled")
        showErrorToast("Request cancelled")
        setTaskId(null)
        setLoading(false)
        return
      }

      // Don't process results here - let the progress hook handle it
      // The progress hook will fetch results via getVeradocResults and process them
      console.log(
        "✅ Review complete, waiting for progress hook to fetch and display results...",
      )
    },
    onError: (error: any) => {
      console.log("Review onError triggered:", error)

      // Check if it's a cancellation error from CancelablePromise
      if (error.name === "CancelError" || error.message === "Request aborted") {
        console.log("Review operation was cancelled (CancelError)")
        showErrorToast("Request cancelled")
        return
      }

      // Check if it's a cancellation error (HTTP 408)
      if (
        error.status === 408 ||
        error.message?.includes("Operation cancelled") ||
        error.detail?.includes("Operation cancelled")
      ) {
        console.log("Review operation was cancelled (HTTP 408)")
        showErrorToast("Request cancelled")
        return
      }

      console.log("RAG mutation unsuccessful!")
      // Convert error to array format
      const errorResult = {
        filename: "Error",
        displayResults: `Error: ${error.message}`,
        qaPairs: [],
      }
      setResults([errorResult])
    },
    onSettled: () => {
      ongoingRequest.current = null
      // Don't set loading to false here - let the progress hook handle it
      console.log("🏁 Mutation settled, progress hook will handle cleanup")
    },
  })

  const handleRun = async () => {
    if (fileItems.length < 1) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please upload at least one file.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!questions.trim()) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please enter at least one question.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!selectedKnowledgeBase) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please select a knowledge base for context.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    // Cancel any ongoing requests
    if (ongoingRequest.current) {
      ongoingRequest.current.cancel()
    }

    // Cancel any in-flight fetch requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Store current inputs in global state
    setReviewInputs({
      selectedKnowledgeBase,
      selectedChecklist,
      questions,
      customInstructions,
      searchMode,
      fileItems,
    })

    // 🚀 OPTIMIZATION: Send ALL files to backend for optimized processing
    console.log(`🚀 Starting optimized review for ${fileItems.length} files`)
    const requestData = {
      questions:
        structuredQuestions.length > 0
          ? JSON.stringify(structuredQuestions)
          : questions,
      knowledgeBaseId: selectedKnowledgeBase.id,
      files: fileItems.map((item) => item.file), // Send ALL files for optimized processing
      handwrittenFiles: [],
      customInstructions: customInstructions.trim() || undefined,
      searchMode: searchMode,
    }

    mutation.mutate(requestData)
  }

  // Create custom components for table rendering
  const components = {
    table: (props: any) => (
      <Box
        as="table"
        width="full"
        borderWidth="1px"
        borderRadius="md"
        overflow="hidden"
        {...props}
      />
    ),
    thead: (props: any) => <Box as="thead" bg="surface" {...props} />,
    tbody: (props: any) => <Box as="tbody" {...props} />,
    tr: (props: any) => <Box as="tr" {...props} />,
    th: (props: any) => (
      <Box
        as="th"
        p={4}
        textAlign="left"
        fontWeight="bold"
        borderBottomWidth="1px"
        {...props}
      />
    ),
    td: (props: any) => (
      <Box as="td" p={4} borderBottomWidth="1px" {...props} />
    ),
  }

  // Function to render results content
  const renderResultsContent = (
    result: { displayResults: string; qaPairs: any[]; interactionId?: string },
    resultIndex: number,
  ) => (
    <Box key={resultIndex}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {result.displayResults}
      </ReactMarkdown>

      {result.qaPairs.map((pair, pairIndex) => (
        <Box
          key={`${resultIndex}-${pairIndex}`}
          mt={4}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg="bg"
        >
          <Heading as="h3" size="md" mb={2}>
            Question {pairIndex + 1}: {pair.question}
          </Heading>

          <Box mb={3}>
            <Text fontWeight="bold">Answer:</Text>
            <Text>{pair.answer}</Text>
          </Box>

          <Box mb={3}>
            <Text fontWeight="bold">Relevant Policy Context:</Text>
            <Text>{pair.context}</Text>
          </Box>

          {pair.source_citations && pair.source_citations.length > 0 && (
            <Accordion.Root multiple>
              <Accordion.Item value={`citations-${resultIndex}-${pairIndex}`}>
                <h2>
                  <Accordion.ItemTrigger bg="surface" _hover={{ bg: "panel" }}>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      <HStack>
                        <FiFileText />
                        <Text>
                          View Source Citations ({pair.source_citations.length})
                        </Text>
                      </HStack>
                    </Box>
                  </Accordion.ItemTrigger>
                </h2>
                <Accordion.ItemContent pb={4} bg="surface">
                  {pair.source_citations.map(
                    (citation: any, cIndex: number) => {
                      const isExpanded = isCitationExpanded(
                        resultIndex,
                        pairIndex,
                        cIndex,
                      )
                      const citationText = cleanRTFFormatting(citation.content)
                      const shouldTruncate = citationText.length > 300
                      const displayText =
                        shouldTruncate && !isExpanded
                          ? `${citationText.substring(0, 300)}...`
                          : citationText

                      return (
                        <Box
                          key={`${resultIndex}-${pairIndex}-${cIndex}`}
                          p={3}
                          mb={2}
                          borderWidth="1px"
                          borderRadius="md"
                          bg="bg"
                        >
                          {citation.metadata.source_data_id ? (
                            <SourceLink
                              sourceId={citation.metadata.source_data_id}
                              fileName={formatSourceWithPage(
                                citation.metadata.source,
                                citation.metadata.page,
                              )}
                              ml={1}
                              fontWeight="normal"
                              color="blue.600"
                              useModal={true}
                              highlightSnippet={citationText}
                            />
                          ) : citation.metadata.source
                              ?.toLowerCase()
                              .endsWith(".docx") ? (
                            <SourceLink
                              sourceId="" // Empty sourceId, will be handled by filename fallback
                              fileName={formatSourceWithPage(
                                citation.metadata.source,
                                citation.metadata.page,
                              )}
                              ml={1}
                              fontWeight="normal"
                              color="blue.600"
                              useModal={true}
                              highlightSnippet={citationText}
                            />
                          ) : (
                            <Text
                              as="span"
                              ml={1}
                              fontWeight="normal"
                              color="blue.600"
                            >
                              {formatSourceWithPage(
                                citation.metadata.source,
                                citation.metadata.page,
                              )}
                            </Text>
                          )}
                          <Box
                            mt={2}
                            p={2}
                            bg="surface"
                            borderRadius="sm"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                          >
                            {displayText}
                          </Box>
                          {shouldTruncate && (
                            <Button
                              size="xs"
                              variant="ghost"
                              mt={1}
                              onClick={() =>
                                toggleCitationExpansion(
                                  resultIndex,
                                  pairIndex,
                                  cIndex,
                                )
                              }
                              colorPalette="blue"
                            >
                              {isExpanded ? "Show Less" : "Read More"}
                            </Button>
                          )}
                        </Box>
                      )
                    },
                  )}
                </Accordion.ItemContent>
              </Accordion.Item>
            </Accordion.Root>
          )}
        </Box>
      ))}
    </Box>
  )

  return (
    <Container maxW="container.xl" py={8}>
      {/* Tab description */}
      <Text
        fontSize="sm"
        color="gray.500"
        textAlign="center"
        mb={4}
        fontStyle="italic"
      >
        {t("review.pageDescription")}
      </Text>

      {/* Progress bar overlay while reviewing */}
      {(loading || progress.isActive || (taskId && !progress.completed)) && (
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="blackAlpha.800"
          zIndex="50"
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
          p={6}
        >
          <VStack gap={4} width="80%" maxWidth="400px">
            <Text
              color="white"
              fontSize="lg"
              fontWeight="medium"
              textAlign="center"
            >
              {progress.message ||
                (fileItems.length > 1
                  ? t("review.processingFiles")
                  : t("review.processingFile"))}
            </Text>
            <Box width="100%">
              <Progress.Root
                value={progress.percentage}
                size="lg"
                colorPalette="blue"
              >
                <Progress.Track>
                  <Progress.Range />
                </Progress.Track>
              </Progress.Root>
              <Text color="white" fontSize="sm" textAlign="center" mt={2}>
                {Math.round(progress.percentage)}%
              </Text>
            </Box>
            <Text color="gray.300" fontSize="sm" textAlign="center">
              {getTranslation(
                "review.pleaseWait",
                "Please wait while we review your documents",
              )}
            </Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title={t("review.knowledgeBaseTitle")}
              description={
                selectedKnowledgeBase
                  ? `${selectedKnowledgeBase.title}`
                  : t("review.knowledgeBaseDescription")
              }
              icon={<FiDatabase size={24} />}
              isSelected={!!selectedKnowledgeBase}
              onClick={() => setShowKnowledgeBaseModal(true)}
              helpKey="knowledgeBaseSelection"
            />

            <SelectionCard
              title={t("review.checklistTitle")}
              description={
                selectedChecklist
                  ? selectedChecklist.name
                  : t("review.checklistDescription")
              }
              icon={<FiFileText size={24} />}
              isSelected={!!selectedChecklist}
              onClick={() => setShowChecklistModal(true)}
              helpKey="checklistSelection"
            />

            {/* File Upload Component */}
            <FileUpload
              files={fileItems}
              onFilesChange={setFileItems}
              helpKey="fileUpload"
            />

            {/* Custom Instructions Text Box */}
            <Box width="100%" mt={4}>
              <HStack align="center" mb={2}>
                <Text fontSize="sm" fontWeight="medium" color="gray.700">
                  {t("review.customInstructionsTitle")}
                </Text>
                <HelpTooltip helpKey="customInstructions" />
              </HStack>
              <Textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder={t("review.customInstructionsPlaceholder")}
                rows={3}
                resize="vertical"
                bg="white"
                borderColor="gray.300"
                _hover={{ borderColor: "gray.400" }}
                _focus={{
                  borderColor: "blue.500",
                  boxShadow: "0 0 0 1px blue.500",
                }}
                fontSize="sm"
                maxLength={2000}
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                {t("review.characterCount", {
                  count: customInstructions.length,
                })}
              </Text>
            </Box>

            {/* Search Mode Toggle */}
            <Box width="100%" mt={4}>
              <SearchModeToggle
                searchMode={searchMode}
                onSearchModeChange={setSearchMode}
                helpKey="searchMode"
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                {t("review.searchModeHelp")}
              </Text>
            </Box>
          </VStack>
        </HStack>

        <KnowledgeBaseSelectionModal
          isOpen={showKnowledgeBaseModal}
          onClose={() => setShowKnowledgeBaseModal(false)}
          title={t("review.selectKnowledgeBaseTitle")}
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={selectedKnowledgeBase}
          onSelectionChange={setSelectedKnowledgeBase}
          showAllUsers={showAllUsers}
          toggleShowAllUsers={toggleShowAllUsers}
        />

        <SelectionModal
          isOpen={showChecklistModal}
          onClose={() => setShowChecklistModal(false)}
          title={t("review.selectChecklistTitle")}
        >
          <ChecklistTable
            checklists={checklists}
            selectedChecklist={selectedChecklist}
            onChecklistChange={setSelectedChecklist}
            onQuestionsChange={setQuestions}
            onStructuredQuestionsChange={setStructuredQuestions}
            onChecklistsUpdate={fetchChecklists}
            selectedKnowledgeBase={selectedKnowledgeBase}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={
            (!selectedKnowledgeBase || !selectedChecklist) && !results ? 0.3 : 1
          }
          pointerEvents={
            (!selectedKnowledgeBase || !selectedChecklist) && !results
              ? "none"
              : "auto"
          }
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={handleRun}
              disabled={
                fileItems.length < 1 ||
                !questions.trim() ||
                !fileItems.some((item) => item.file.size > 0)
              }
              loading={loading}
              color="white"
              bg="rgba(0, 65, 72, 0.9)"
              width="20%"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              {t("review.reviewButton")}
            </Button>
          </HStack>

          <Box
            border="1px solid"
            borderColor="gray.200"
            borderRadius="md"
            p={4}
            mt={4}
            display="flex"
            flexDirection={{ base: "column", md: "row" }}
            gap={4}
          >
            <Box
              flex="1"
              width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}
            >
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">{t("review.results")}</Heading>

                {results.length > 0 && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyReport}
                      colorPalette={
                        copySuccess ? "rgba(0, 65, 72, 0.9)" : "blue"
                      }
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess
                        ? t("review.reportCopied").replace("!", "")
                        : t("review.copyReport")}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadReport}
                      loading={loadingDownload}
                    >
                      {t("review.downloadReport")}
                    </DownloadButton>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadCsv}
                      loading={loadingCsvDownload}
                    >
                      {t("review.downloadCsv")}
                    </DownloadButton>

                    <Button
                      size="sm"
                      variant="outline"
                      colorPalette="red"
                      onClick={() => {
                        handleClearResults()
                        showSuccessToast(t("review.clearResults"))
                      }}
                    >
                      <FiTrash2 />
                      {t("review.clearResults")}
                    </Button>
                  </HStack>
                )}
              </HStack>

              <Box
                border="1px solid"
                borderColor="gray.200"
                borderRadius="md"
                p={4}
                bg="surface"
                minH="100px"
                maxH={{ base: "400px", md: "600px" }}
                overflowY="auto"
                position="relative"
                opacity={loading ? 0.5 : 1}
              >
                {loading && (
                  <Box
                    position="absolute"
                    top="50%"
                    left="50%"
                    transform="translate(-50%, -50%)"
                    zIndex="1"
                  >
                    <Spinner size="lg" color="blue.500" />
                  </Box>
                )}
                {results.length > 0 ? (
                  <>
                    <Tabs.Root
                      defaultValue="0"
                      value={activeTab.toString()}
                      onValueChange={(details) =>
                        setActiveTab(Number.parseInt(details.value))
                      }
                    >
                      <Tabs.List>
                        {results.map((result, index) => {
                          const fileName = result.filename

                          return (
                            <Tabs.Trigger key={index} value={index.toString()}>
                              {fileName.length > 30
                                ? `${fileName.slice(0, 30)}...`
                                : fileName}
                            </Tabs.Trigger>
                          )
                        })}
                      </Tabs.List>

                      {results.map((result, index) => (
                        <Tabs.Content key={index} value={index.toString()}>
                          {renderResultsContent(result, index)}
                        </Tabs.Content>
                      ))}
                    </Tabs.Root>

                    {/* Add feedback buttons for the active result */}
                    {results[activeTab]?.interactionId && (
                      <Box
                        position="sticky"
                        bottom={4}
                        right={4}
                        display="flex"
                        justifyContent="flex-end"
                        pointerEvents="auto"
                        zIndex={10}
                        mt={4}
                      >
                        <FeedbackButtons
                          interactionId={results[activeTab].interactionId}
                          onFeedbackSubmitted={handleFeedbackSubmitted}
                        />
                      </Box>
                    )}
                  </>
                ) : (
                  <Text color="gray.500">{t("review.noResults")}</Text>
                )}
              </Box>
            </Box>
          </Box>
        </VStack>
      </VStack>
    </Container>
  )
}

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/review")({
  component: VeraDoc,
})
