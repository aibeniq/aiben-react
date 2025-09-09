import {
  type KnowledgeBasePublic,
  KnowledgeBasesService,
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
import {
  Accordion,
  Box,
  Button,
  Container,
  HStack,
  Heading,
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
import { FiCheck, FiCopy, FiDatabase, FiFileText, FiTrash2 } from "react-icons/fi"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import KnowledgeBaseTable from "../../components/Common/KnowledgeBaseTable"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import ChecklistTable from "../../components/Review/ChecklistTable"
import { useResults } from "../../contexts/ResultsContext"
import { copyToClipboard } from "../../utils/copyToClipboard"

interface QuestionData {
  id: string
  text: string
  consultDocuments: boolean
}

const VeraDoc = () => {
  const { t } = useTranslation()
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
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    reviewInputs?.selectedKnowledgeBase || null,
  )
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)
  const ongoingRequest = useRef<CancelablePromise<any> | null>(null)

  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showChecklistModal, setShowChecklistModal] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  const [questions, setQuestions] = useState(reviewInputs?.questions || "")
  const [structuredQuestions, setStructuredQuestions] = useState<QuestionData[]>([])
  const [customInstructions, setCustomInstructions] = useState(
    reviewInputs?.customInstructions || "",
  )

  const [fileItems, setFileItems] = useState<FileItem[]>(reviewInputs?.fileItems || [])

  const [loading, setLoading] = useState<boolean>(false)

  const [checklists, setChecklists] = useState<VeraDocChecklist[]>([])
  const [selectedChecklist, setSelectedChecklist] = useState<VeraDocChecklist | null>(
    reviewInputs?.selectedChecklist || null,
  )

  // Search mode state for main review functionality
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    reviewInputs?.searchMode || "vector",
  )

  // State to track which citations are expanded - using object instead of Set
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({})

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
  const isCitationExpanded = (resultIndex: number, pairIndex: number, citationIndex: number) => {
    const citationKey = `${resultIndex}-${pairIndex}-${citationIndex}`
    return expandedCitations[citationKey] || false
  }

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
      console.log("Response instanceof ArrayBuffer:", response instanceof ArrayBuffer)

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

      console.log("DOCX download filename:", `Evaluation_${filename}_${timestamp}.docx`)
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

      showErrorToast(`Failed to download evaluation: ${err.message || "Unknown error"}`)
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
      showErrorToast(`Failed to download CSV: ${err.message || "Unknown error"}`)
    } finally {
      setLoadingCsvDownload(false)
    }
  }

  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown"

    // Clean up temporary file paths
    if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
      // First get the filename without the path
      const filename = source.split("/").pop() || source.split("\\").pop() || ""

      // Then remove everything before and including the first underscore
      return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
    }

    return source
  }

  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        const response = await KnowledgeBasesService.readKnowledgeBases({
          skip: 0,
          limit: 100,
        })
        setKnowledgeBases(response.data || [])
      } catch (error) {
        console.error("Error fetching knowledge bases:", error)
      }
    }

    fetchKnowledgeBases()
  }, [])

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

  // Add this mutation hook inside your VeraDoc component, before your handleRun function
  const mutation = useMutation({
    mutationFn: (data: {
      questions: string
      knowledgeBaseId: string
      files: File[]
      handwrittenFiles: File[]
      customInstructions?: string
      searchMode?: "vector" | "full_scan"
    }) => {
      if (ongoingRequest.current) {
        ongoingRequest.current.cancel()
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      // Create a new controller and store directly in the ref
      const controller = new AbortController()
      abortControllerRef.current = controller

      console.log("Creating new request with fresh AbortController")
      console.log("Search mode being sent to backend:", data.searchMode)

      // Create the promise and store it
      const promise = VeradocService.processRagChecklist({
        questions: data.questions,
        knowledgeBaseId: data.knowledgeBaseId,
        customInstructions: data.customInstructions,
        searchMode: data.searchMode,
        formData: {
          files: data.files,
          handwritten_files: data.handwrittenFiles,
        },
      })

      ongoingRequest.current = promise
      return promise
    },
    onSuccess: (data: any) => {
      console.log("Response data:", data)

      const singleResult = {
        filename: data.results.filename,
        displayResults: data.results.final_evaluation || "",
        qaPairs: (data.results.qa_pairs as any[]) || [],
        interactionId: data.results.interaction_id as string | undefined,
      }

      setResults([singleResult])

      // Show success message with search mode information
      const searchMethod = searchMode === "vector" ? "vector search" : "full document scan"
      showSuccessToast(`Document review completed using ${searchMethod}`)
    },
    onError: (error) => {
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
      setLoading(false)
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

    // Filter out placeholder files and separate into regular vs handwritten
    const validItems = fileItems.filter((item) => item.file.size > 0)
    const regularFiles = validItems.filter((item) => !item.isHandwritten).map((item) => item.file)
    const handwrittenFiles = validItems
      .filter((item) => item.isHandwritten)
      .map((item) => item.file)

    if (validItems.length < 1) {
      const errorResult = {
        filename: "Error",
        displayResults: "Please upload at least one valid file.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    const requestData = {
      questions: structuredQuestions.length > 0 ? JSON.stringify(structuredQuestions) : questions,
      knowledgeBaseId: selectedKnowledgeBase.id,
      files: regularFiles,
      handwrittenFiles: handwrittenFiles,
      customInstructions: customInstructions.trim() || undefined,
      searchMode: searchMode,
    }

    console.log("Request Data:", requestData)

    setLoading(true) // Set loading to true
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false) // Set loading to false when the process finishes
      },
    })
  }

  const handleProcessBatch = async () => {
    if (fileItems.length === 0) {
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please upload at least one file for batch processing.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!questions.trim()) {
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please enter at least one question.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    if (!selectedKnowledgeBase) {
      const errorResult = {
        filename: "Error",
        displayResults: "Error: Please select a knowledge base for context.",
        qaPairs: [],
      }
      setResults([errorResult])
      return
    }

    // Clear previous results
    setResults([])
    setLoading(true)

    // Cancel any ongoing requests
    if (ongoingRequest.current) {
      ongoingRequest.current.cancel()
    }

    // Cancel any in-flight fetch requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create a new controller and store directly in the ref
    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      const batchResults: Array<{
        filename: string
        displayResults: string
        qaPairs: any[]
        interactionId?: string
      }> = []

      // Process each file individually
      for (let i = 0; i < fileItems.length; i++) {
        if (controller.signal.aborted) {
          console.log("Batch processing aborted")
          break
        }
        const fileItem = fileItems[i]

        // Separate files based on handwritten flag
        const regularFiles = fileItem.isHandwritten ? [] : [fileItem.file]
        const handwrittenFiles = fileItem.isHandwritten ? [fileItem.file] : []

        // Process this file
        const requestData = {
          questions:
            structuredQuestions.length > 0 ? JSON.stringify(structuredQuestions) : questions,
          knowledgeBaseId: selectedKnowledgeBase.id,
          files: regularFiles,
          handwrittenFiles: handwrittenFiles,
          customInstructions: customInstructions.trim() || undefined,
          searchMode: searchMode,
        }

        // Call the API using our mutation
        const response = await VeradocService.processRagChecklist({
          questions: requestData.questions,
          knowledgeBaseId: requestData.knowledgeBaseId,
          customInstructions: requestData.customInstructions,
          searchMode: requestData.searchMode,
          formData: {
            files: requestData.files,
            handwritten_files: requestData.handwrittenFiles,
          },
        })

        let displayResults = ""

        if (response.results.final_evaluation) {
          displayResults += "## FINAL EVALUATION\n\n"
          displayResults += `${response.results.final_evaluation}\n\n`
        }

        // Store the QA pairs in the results array
        batchResults.push({
          filename: fileItem.file.name,
          displayResults,
          qaPairs: (response.results.qa_pairs as any[]) || [],
          interactionId: response.results.interaction_id as string | undefined,
        })

        // Update your state for batch results
        setResults([...batchResults])
      }

      // Show success message for batch processing
      if (batchResults.length > 0) {
        const searchMethod = searchMode === "vector" ? "vector search" : "full document scan"
        showSuccessToast(
          `Batch processing completed for ${batchResults.length} files using ${searchMethod}`,
        )
      }
    } catch (error: any) {
      // Handle errors, checking if it's an abort
      if (error.name === "AbortError") {
        console.log("Batch processing was aborted")
      } else {
        console.error("Batch processing error:", error)
        const errorResult = {
          filename: "Error",
          displayResults: `Error processing batch: ${error.message}`,
          qaPairs: [],
        }
        setResults([errorResult])
      }
    } finally {
      setLoading(false)
    }
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
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props: any) => <Box as="td" p={4} borderBottomWidth="1px" {...props} />,
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
                        <Text>View Source Citations ({pair.source_citations.length})</Text>
                      </HStack>
                    </Box>
                  </Accordion.ItemTrigger>
                </h2>
                <Accordion.ItemContent pb={4} bg="surface">
                  {pair.source_citations.map((citation: any, cIndex: number) => {
                    const isExpanded = isCitationExpanded(resultIndex, pairIndex, cIndex)
                    const citationText = citation.content
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
                            fileName={getDisplayFileName(citation.metadata.source)}
                            ml={1}
                            fontWeight="normal"
                            color="blue.600"
                            useModal={true}
                          />
                        ) : citation.metadata.source?.toLowerCase().endsWith(".docx") ? (
                          <SourceLink
                            sourceId="" // Empty sourceId, will be handled by filename fallback
                            fileName={getDisplayFileName(citation.metadata.source)}
                            ml={1}
                            fontWeight="normal"
                            color="blue.600"
                            useModal={true}
                          />
                        ) : (
                          <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                            {getDisplayFileName(citation.metadata.source)}
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
                            onClick={() => toggleCitationExpansion(resultIndex, pairIndex, cIndex)}
                            colorPalette="blue"
                          >
                            {isExpanded ? "Show Less" : "Read More"}
                          </Button>
                        )}
                      </Box>
                    )
                  })}
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
      <Text fontSize="sm" color="gray.500" textAlign="center" mb={4} fontStyle="italic">
        {t("review.pageDescription")}
      </Text>

      {/* Add this overlay spinner that shows when loading is true */}
      {loading && (
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="rgba(255, 255, 255, 0.7)"
          zIndex="10"
          display="flex"
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
        >
          <VStack gap={4}>
            <Spinner size="xl" color="blue.500" />
            <Text fontWeight="medium">
              {fileItems.length > 1 ? t("review.processingFiles") : t("review.processingFile")}
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
                selectedChecklist ? selectedChecklist.name : t("review.checklistDescription")
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
              showHandwrittenToggle={true}
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
                {t("review.characterCount", { count: customInstructions.length })}
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

        <SelectionModal
          isOpen={showKnowledgeBaseModal}
          onClose={() => setShowKnowledgeBaseModal(false)}
          title="Select Knowledge Base"
        >
          <KnowledgeBaseTable
            knowledgeBases={knowledgeBases}
            selectedKnowledgeBase={selectedKnowledgeBase}
            onSelectionChange={setSelectedKnowledgeBase}
          />
        </SelectionModal>

        <SelectionModal
          isOpen={showChecklistModal}
          onClose={() => setShowChecklistModal(false)}
          title="Select Checklist"
        >
          <ChecklistTable
            checklists={checklists}
            selectedChecklist={selectedChecklist}
            onChecklistChange={setSelectedChecklist}
            onQuestionsChange={setQuestions}
            onStructuredQuestionsChange={setStructuredQuestions}
            onChecklistsUpdate={fetchChecklists}
            questions={questions}
            knowledgeBases={knowledgeBases}
            selectedKnowledgeBase={selectedKnowledgeBase}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={(!selectedKnowledgeBase || !selectedChecklist) && !results ? 0.3 : 1}
          pointerEvents={
            (!selectedKnowledgeBase || !selectedChecklist) && !results ? "none" : "auto"
          }
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={fileItems.length > 0 ? handleProcessBatch : handleRun}
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
            <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">{t("review.results")}</Heading>

                {results.length > 0 && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyReport}
                      colorPalette={copySuccess ? "rgba(0, 65, 72, 0.9)" : "blue"}
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
                      onValueChange={(details) => setActiveTab(Number.parseInt(details.value))}
                    >
                      <Tabs.List>
                        {results.map((result, index) => {
                          const fileName = result.filename

                          return (
                            <Tabs.Trigger key={index} value={index.toString()}>
                              {fileName.length > 30 ? `${fileName.slice(0, 30)}...` : fileName}
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
