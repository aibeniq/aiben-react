import {
  Box,
  Button,
  Container,
  HStack,
  Heading,
  Progress,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { useDropzone } from "react-dropzone"
import { useTranslation } from "react-i18next"
import {
  FiCheck,
  FiCopy,
  FiFile,
  FiFileText,
  FiTrash2,
  FiUpload,
} from "react-icons/fi"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { type TwinCheckTopicList, TwincheckService } from "@/client"
import SelectionCard from "@/components/Common/SelectionCard"
import SelectionModal from "@/components/Common/SelectionModal"
import TopicListTable from "@/components/Compare/TopicListTable"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import DownloadButton from "@/components/ui/download-button"
import useCustomToast from "@/hooks/useCustomToast"
import { useOperationCancellation } from "@/hooks/useOperationCancellation"
import { useTwincheckProgress } from "@/hooks/useTwincheckProgress"

import { useResults } from "@/contexts/ResultsContext"
import { copyToClipboard } from "@/utils/copyToClipboard"

const TwinCheck = () => {
  const { t, ready } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { registerOperation } = useOperationCancellation()
  const {
    compareResult,
    setCompareResult,
    compareInputs,
    setCompareInputs,
    clearCompareResult,
  } = useResults()

  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // Modal states
  const [showTopicListModal, setShowTopicListModal] = useState(false)

  // Initialize form state from persisted inputs or defaults
  const [document1, setDocument1] = useState<File | null>(
    compareInputs?.document1 || null,
  )
  const [document2, setDocument2] = useState<File | null>(
    compareInputs?.document2 || null,
  )

  // Topics state
  const [topics, setTopics] = useState(compareInputs?.topics || "")
  const [comparisons, setComparisons] = useState<TwinCheckTopicList[]>([])
  const [selectedComparison, setSelectedComparison] =
    useState<TwinCheckTopicList | null>(
      compareInputs?.selectedComparison || null,
    )

  // Loading state
  const [loading, setLoading] = useState(false)
  const [expandedTopic, setExpandedTopic] = useState<number | null>(null)

  // Progress tracking
  const [taskId, setTaskId] = useState<string | null>(null)
  // Use a TwinCheck-specific progress hook so progress maps to twincheck backend keys
  const progress = useTwincheckProgress(taskId)
  const hasHandledCompletionRef = useRef(false)

  // Handle feedback submission
  const handleFeedbackSubmitted = (type: string) => {
    console.log("Feedback submitted for compare result:", type)
    showSuccessToast(`Thank you for marking this response as ${type}!`)
  }

  // Handle progress completion
  useEffect(() => {
    if (
      taskId &&
      progress.completed &&
      !hasHandledCompletionRef.current &&
      progress.percentage >= 95
    ) {
      console.log("✅ Compare task completed, clearing taskId")
      hasHandledCompletionRef.current = true

      setTimeout(() => {
        setTaskId(null)
        hasHandledCompletionRef.current = false
        setLoading(false)
      }, 1500)
    }

    if (taskId && progress.error) {
      console.log("❌ Compare task failed:", progress.error)
      setTaskId(null)
      setLoading(false)
      hasHandledCompletionRef.current = false
      showErrorToast(progress.error)
    }
  }, [taskId, progress.completed, progress.error, progress.percentage])

  // Reset completion handler when taskId changes
  useEffect(() => {
    if (taskId) {
      console.log("🔄 New compare task started, resetting completion handler")
      hasHandledCompletionRef.current = false
    }
  }, [taskId])

  // Save input parameters to context whenever they change
  useEffect(() => {
    setCompareInputs({
      document1,
      document2,
      topics,
      selectedComparison,
    })
  }, [document1, document2, topics, selectedComparison, setCompareInputs])

  // Clear inputs and restore from context when clear button is clicked
  const handleClearResults = () => {
    clearCompareResult() // Clears both results and inputs
    // Reset local state to blank
    setDocument1(null)
    setDocument2(null)
    setTopics("")
    setSelectedComparison(null)
  }

  // Debug effect to log context state
  useEffect(() => {
    console.log("Compare tab - context state:", {
      hasResult: !!compareResult,
      summaryLength: compareResult?.summary?.length,
      topicResultsCount: compareResult?.topicResults?.length,
    })
  }, [compareResult])

  // Function to copy report to clipboard
  const handleCopyReport = async () => {
    try {
      // Prepare combined text with summary and all topic analyses
      let fullText = `# Summary\n\n${compareResult?.summary || ""}\n\n# Topic Analysis\n\n`

      // Add each topic and its analysis
      compareResult?.topicResults.forEach((topic: any) => {
        fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
      })

      await copyToClipboard(fullText)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Comparison results copied to clipboard")
    } catch (err) {
      console.error("Failed to copy report:", err)
      showErrorToast("Failed to copy report to clipboard")
    }
  }

  // Function to download report as DOCX
  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true)

      // Prepare combined text with summary and all topic analyses
      let fullText = `# Summary\n\n${compareResult?.summary || ""}\n\n# Topic Analysis\n\n`

      // Add each topic and its analysis
      compareResult?.topicResults.forEach((topic: any) => {
        fullText += `## Topic: ${topic.topic}\n\n${topic.analysis}\n\n`
      })

      const response = await TwincheckService.generateDocx({
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
        blob = new Blob([response as BlobPart], {
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
      a.href = url
      a.download = `comparison_${timestamp}.docx`

      console.log("DOCX download filename:", `comparison_${timestamp}.docx`)
      console.log("About to trigger DOCX download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("DOCX download triggered successfully")
      showSuccessToast("Comparison downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download report:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(
        `Failed to download report: ${err.message || "Unknown error"}`,
      )
    } finally {
      console.log("DOCX download process completed")
      setLoadingDownload(false)
    }
  }

  // Function to download comparison as CSV
  const handleDownloadCsv = async () => {
    try {
      setLoadingCsvDownload(true)

      // Prepare the data for CSV generation
      const csvData = {
        summary: compareResult?.summary || "",
        topic_results: compareResult?.topicResults || [],
        doc1_name: document1?.name || "Document 1",
        doc2_name: document2?.name || "Document 2",
      }

      const response = await TwincheckService.generateCsv({
        requestBody: { content: JSON.stringify(csvData) },
      })

      console.log("Received CSV response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)

      // Handle blob response
      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], { type: "text/csv" })
      } else {
        blob = new Blob([response as any], { type: "text/csv" })
      }

      console.log("Blob size:", blob.size)

      if (blob.size === 0) {
        throw new Error("Received empty CSV file")
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `TwinCheck_Comparison_${timestamp}.csv`

      console.log(
        "CSV download filename:",
        `TwinCheck_Comparison_${timestamp}.csv`,
      )
      console.log("About to trigger CSV download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("CSV download triggered successfully")
      showSuccessToast("CSV downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download CSV:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(
        `Failed to download CSV: ${err.message || "Unknown error"}`,
      )
    } finally {
      console.log("CSV download process completed")
      setLoadingCsvDownload(false)
    }
  }

  // Fetch saved comparison topic sets when component mounts
  const fetchComparisons = async () => {
    try {
      const data = await TwincheckService.getComparisons()
      setComparisons(data || [])
    } catch (error) {
      console.error("Error fetching comparisons:", error)
      showErrorToast("Failed to fetch topic lists")
    }
  }

  useEffect(() => {
    fetchComparisons()
  }, [])

  // Mutation for comparing documents
  const mutation = useMutation({
    mutationFn: async (data: {
      comparison_topics: string
      document1: File
      document2: File
    }) => {
      console.log("🎯 Creating compare task for progress tracking...")

      // First, create a task to get the task_id for progress tracking (TwinCheck-specific)
      // The SDK does not always include a generated Twincheck createOptimizeOutlineTask; use authenticated request helper
      const taskResponse = await (async () => {
        try {
          // Prefer generated SDK method if available
          // @ts-ignore
          if (
            typeof (TwincheckService as any).createOptimizeOutlineTask ===
            "function"
          ) {
            // @ts-ignore
            return await (TwincheckService as any).createOptimizeOutlineTask()
          }
        } catch (err) {
          // ignore and fallback to direct authenticated request
          console.warn(
            "TwincheckService.createOptimizeOutlineTask not available or failed:",
            err,
          )
        }

        // Fallback: call the backend using the generated request helper with auth
        const { request: __request } = await import("@/client/core/request")
        const { OpenAPI } = await import("@/client/core/OpenAPI")
        return await __request(OpenAPI, {
          method: "POST",
          url: "/api/v1/twincheck/optimize-outline/task",
        })
      })()

      const newTaskId =
        (taskResponse as any).task_id ||
        (taskResponse as any).taskId ||
        (taskResponse as any).id
      console.log("📋 Generated compare task_id:", newTaskId)
      setTaskId(newTaskId)

      // Simplified API call without knowledge base parameters
      const promise = TwincheckService.compareDocuments({
        comparisonTopics: data.comparison_topics,
        formData: {
          document1: data.document1,
          document2: data.document2,
          task_id: newTaskId, // Pass task_id for progress tracking
        } as any, // Type assertion - SDK will be regenerated later
      })

      // Register the operation for automatic cancellation on navigation
      return registerOperation(promise)
    },
    onSuccess: (data: any) => {
      console.log("Response data:", data)

      // Check if the request was cancelled
      if (data.results.status === "cancelled") {
        console.log("Compare operation was cancelled")
        showErrorToast("Request cancelled")
        return
      }

      const interactionId = data.results.interaction_id
      console.log("Compare interactionId for feedback:", interactionId)

      // Store result in global state
      setCompareResult({
        summary: data.results.summary || "",
        topicResults: data.results.topic_analysis || [],
        interactionId: interactionId,
      })

      showSuccessToast("Documents compared successfully!")
    },
    onError: (error: any) => {
      console.log("Comparison failed!")
      showErrorToast(`Comparison failed: ${error.message}`)
    },
    onSettled: () => {
      setLoading(false)
    },
  })

  const handleCompare = async () => {
    if (!document1) {
      showErrorToast(t("compare.selectFirstDocument"))
      return
    }

    if (!document2) {
      showErrorToast(t("compare.selectSecondDocument"))
      return
    }

    if (!topics.trim()) {
      showErrorToast("Please enter at least one comparison topic")
      return
    }

    // Simplified request data without knowledge base
    const requestData = {
      comparison_topics: topics,
      document1: document1,
      document2: document2,
    }

    setLoading(true)
    mutation.mutate(requestData)
  }

  // Custom components for markdown rendering
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
        {t("compare.subtitle")}
      </Text>

      {/* Progress bar overlay while comparing */}
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
              {progress.message || t("compare.loadingComparison")}
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
              {ready
                ? t("compare.pleaseWait")
                : "Please wait while we compare your documents"}
            </Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title={t("compare.topicList")}
              description={
                selectedComparison
                  ? selectedComparison.name
                  : t("compare.pleaseSelect")
              }
              icon={<FiFileText size={24} />}
              isSelected={!!selectedComparison}
              onClick={() => setShowTopicListModal(true)}
              helpKey="topicList"
            />

            <VStack gap={4} align="stretch">
              <HStack gap={6} align="stretch">
                <Box flex="1">
                  <FileUploader
                    label={t("compare.documentA")}
                    file={document1}
                    setFile={setDocument1}
                    accept={{
                      "application/pdf": [".pdf"],
                      "text/plain": [".txt"],
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        [".docx"],
                      "text/csv": [".csv"],
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        [".xlsx"],
                      "application/vnd.ms-excel": [".xls"],
                    }}
                  />
                </Box>

                <Box flex="1">
                  <FileUploader
                    label={t("compare.documentB")}
                    file={document2}
                    setFile={setDocument2}
                    accept={{
                      "application/pdf": [".pdf"],
                      "text/plain": [".txt"],
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        [".docx"],
                      "text/csv": [".csv"],
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        [".xlsx"],
                      "application/vnd.ms-excel": [".xls"],
                    }}
                  />
                </Box>
              </HStack>
            </VStack>
          </VStack>
        </HStack>

        <SelectionModal
          isOpen={showTopicListModal}
          onClose={() => setShowTopicListModal(false)}
          title={t("compare.selectTopicListTitle")}
        >
          <TopicListTable
            topicLists={comparisons}
            selectedTopicList={selectedComparison}
            onTopicListChange={setSelectedComparison}
            onTopicsChange={setTopics}
            onTopicListsUpdate={fetchComparisons}
            topics={topics}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedComparison && !compareResult ? 0.3 : 1}
          pointerEvents={
            !selectedComparison && !compareResult ? "none" : "auto"
          }
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={handleCompare}
              disabled={!document1 || !document2 || !topics.trim()}
              loading={loading}
              color="white"
              bg="rgba(0, 65, 72, 0.9)"
              width="20%"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              {t("compare.compareDocuments")}
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
                <Heading size="md">{t("compare.comparison")}</Heading>

                {compareResult && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyReport}
                      colorPalette={copySuccess ? "green" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? "Copied!" : "Copy Text"}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadReport}
                      loading={loadingDownload}
                    >
                      Download DOCX
                    </DownloadButton>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadCsv}
                      loading={loadingCsvDownload}
                    >
                      Download CSV
                    </DownloadButton>

                    <Button
                      size="sm"
                      variant="outline"
                      colorPalette="red"
                      onClick={() => {
                        handleClearResults()
                        showSuccessToast("Comparison results cleared")
                      }}
                    >
                      <FiTrash2 />
                      Clear Results
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
              >
                {compareResult ? (
                  <>
                    {/* Summary Section */}
                    <Heading as="h3" size="md" mb={2}>
                      Summary
                    </Heading>
                    <Box
                      p={3}
                      mb={4}
                      borderWidth="1px"
                      borderRadius="md"
                      bg="bg"
                    >
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={components}
                      >
                        {compareResult.summary}
                      </ReactMarkdown>
                    </Box>

                    {/* Topic Analysis Section */}
                    {compareResult.topicResults.length > 0 && (
                      <Box mt={8}>
                        <Heading as="h3" size="md" mb={4}>
                          Topic Analysis
                        </Heading>

                        {compareResult.topicResults.map(
                          (topicResult, index) => (
                            <Box
                              key={index}
                              mb={6}
                              p={5}
                              borderWidth="1px"
                              borderRadius="md"
                              bg={expandedTopic === index ? "surface" : "bg"}
                              _hover={{ bg: "surface" }}
                            >
                              <Heading
                                as="h4"
                                size="sm"
                                mb={3}
                                onClick={() =>
                                  setExpandedTopic(
                                    expandedTopic === index ? null : index,
                                  )
                                }
                                cursor="pointer"
                                display="flex"
                                alignItems="center"
                              >
                                <Box
                                  as="span"
                                  mr={2}
                                  transform={
                                    expandedTopic === index
                                      ? "rotate(90deg)"
                                      : "rotate(0deg)"
                                  }
                                  transition="transform 0.2s"
                                >
                                  ▶
                                </Box>
                                Topic: {topicResult.topic}
                              </Heading>

                              {expandedTopic === index && (
                                <Box
                                  mb={4}
                                  p={3}
                                  borderLeft="4px solid"
                                  borderColor="blue.200"
                                >
                                  <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={components}
                                  >
                                    {topicResult.analysis}
                                  </ReactMarkdown>
                                </Box>
                              )}
                            </Box>
                          ),
                        )}
                      </Box>
                    )}

                    {/* Add feedback buttons for the comparison result */}
                    {compareResult?.interactionId && (
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
                          interactionId={compareResult.interactionId}
                          onFeedbackSubmitted={handleFeedbackSubmitted}
                        />
                      </Box>
                    )}
                  </>
                ) : (
                  <Text color="gray.500">
                    {t("compare.selectTwoDocuments")}
                  </Text>
                )}
              </Box>
            </Box>
          </Box>
        </VStack>
      </VStack>
    </Container>
  )
}

// File uploader component
const FileUploader = ({
  label,
  file,
  setFile,
  accept,
}: {
  label: string
  file: File | null
  setFile: (file: File) => void
  accept?: Record<string, string[]>
}) => {
  const { t } = useTranslation()
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0])
      }
    },
    accept,
    multiple: false,
  })

  return (
    <Box>
      <Text fontWeight="medium" mb={2}>
        {label}
      </Text>
      <Box
        {...getRootProps()}
        border="2px dashed"
        borderColor="gray.300"
        borderRadius="md"
        p={4}
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: "blue.500" }}
        bg={file ? "accent.subtle" : "surface"}
        transition="all 0.2s"
      >
        <input {...getInputProps()} />
        <VStack gap={2}>
          {file ? (
            <>
              <Box as={FiFile} color="blue.500" fontSize="2xl" />
              <Text fontWeight="medium">{file.name}</Text>
              <Text fontSize="sm" color="gray.600">
                {(file.size / 1024).toFixed(1)} KB
              </Text>
            </>
          ) : (
            <>
              <Box as={FiUpload} color="gray.400" fontSize="2xl" />
              <Text>{t("compare.clickToBrowse")}</Text>
              <Text fontSize="xs" color="gray.500">
                {t("compare.supportedFormats")}
              </Text>
            </>
          )}
        </VStack>
      </Box>
    </Box>
  )
}

export const Route = createFileRoute("/_layout/compare")({
  component: TwinCheck,
})
