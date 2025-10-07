import { type KnowledgeBasePublic, type ReportGenieOutline, ReportgenieService } from "@/client"
import SearchModeToggle from "@/components/Common/SearchModeToggle"
import SourceLink from "@/components/Common/SourceLink"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import DownloadButton from "@/components/ui/download-button"
import HelpTooltip from "@/components/ui/help-tooltip"
import useCustomToast from "@/hooks/useCustomToast"
import { useKnowledgeBases } from "@/hooks/useKnowledgeBases"
import { useOperationCancellation } from "@/hooks/useOperationCancellation"
import { useReportGenieProgress } from "@/hooks/useReportGenieProgress"
import {
  Accordion,
  Box,
  Button,
  Container,
  HStack,
  Heading,
  Progress,
  Spinner,
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
import KnowledgeBaseSelectionModal from "../../components/Common/KnowledgeBaseSelectionModal"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import OutlineTable from "../../components/Generate/OutlineTable"
import { useResults } from "../../contexts/ResultsContext"
import { copyToClipboard } from "../../utils/copyToClipboard"
import { cleanRTFFormatting } from "../../utils/rtfCleaner"

const ReportGenie = () => {
  const { t } = useTranslation()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    generateResult,
    setGenerateResult,
    generateInputs,
    setGenerateInputs,
    clearGenerateResult,
  } = useResults()

  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // Modal states
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showOutlineModal, setShowOutlineModal] = useState(false)

  // Progress tracking
  const [taskId, setTaskId] = useState<string | null>(null)
  const progress = useReportGenieProgress(taskId)
  const hasHandledCompletionRef = useRef(false)

  // Initialize form state from persisted inputs or defaults
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    generateInputs?.selectedKnowledgeBase || null,
  )
  const { knowledgeBases, showAllUsers, toggleShowAllUsers } = useKnowledgeBases() // Respect All Users toggle state
  const { registerOperation } = useOperationCancellation()

  // Outline content state
  const [sections, setSections] = useState(generateInputs?.sections || "")
  const [outlines, setOutlines] = useState<ReportGenieOutline[]>([])
  const [selectedOutline, setSelectedOutline] = useState<ReportGenieOutline | null>(
    generateInputs?.selectedOutline || null,
  )

  // Loading state
  const [loading, setLoading] = useState(false)
  const [expandedSection, setExpandedSection] = useState<number | null>(null)

  // Search mode state
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
    generateInputs?.searchMode || "vector",
  )

  // Custom instructions state
  const [customInstructions, setCustomInstructions] = useState(
    generateInputs?.customInstructions || "",
  )

  // State to track which citations are expanded - using object instead of Set
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({})

  // Function to toggle citation expansion
  const toggleCitationExpansion = (sectionIndex: number, citationIndex: number) => {
    const citationKey = `${sectionIndex}-${citationIndex}`
    setExpandedCitations((prev) => ({
      ...prev,
      [citationKey]: !prev[citationKey],
    }))
  }

  // Function to check if a citation is expanded
  const isCitationExpanded = (sectionIndex: number, citationIndex: number) => {
    const citationKey = `${sectionIndex}-${citationIndex}`
    return expandedCitations[citationKey] || false
  }

  // Handle feedback submission
  const handleFeedbackSubmitted = (type: string) => {
    console.log("Feedback submitted for generate result:", type)
    showSuccessToast(`Thank you for marking this response as ${type}!`)
  }

  // Handle progress completion
  useEffect(() => {
    if (taskId && progress.completed && !hasHandledCompletionRef.current && progress.percentage >= 95) {
      console.log("✅ Generate task completed, clearing taskId")
      hasHandledCompletionRef.current = true
      
      setTimeout(() => {
        setTaskId(null)
        hasHandledCompletionRef.current = false
        setLoading(false)
      }, 1500)
    }

    if (taskId && progress.error) {
      console.log("❌ Generate task failed:", progress.error)
      setTaskId(null)
      setLoading(false)
      hasHandledCompletionRef.current = false
      showErrorToast(progress.error)
    }
  }, [taskId, progress.completed, progress.error, progress.percentage])

  // Reset completion handler when taskId changes
  useEffect(() => {
    if (taskId) {
      console.log("🔄 New generate task started, resetting completion handler")
      hasHandledCompletionRef.current = false
    }
  }, [taskId])

  // Save input parameters to context whenever they change
  useEffect(() => {
    setGenerateInputs({
      selectedKnowledgeBase,
      selectedOutline,
      sections,
      customInstructions,
      searchMode,
    })
  }, [
    selectedKnowledgeBase,
    selectedOutline,
    sections,
    customInstructions,
    searchMode,
    setGenerateInputs,
  ])

  // Clear inputs and restore from context when clear button is clicked
  const handleClearResults = () => {
    clearGenerateResult() // Clears both results and inputs
    // Reset local state to blank
    setSelectedKnowledgeBase(null)
    setSelectedOutline(null)
    setSections("")
    setCustomInstructions("")
    setSearchMode("vector")
  }

  // Debug effect to log context state
  useEffect(() => {
    console.log("Generate tab - context state:", {
      hasResult: !!generateResult,
      reportLength: generateResult?.full_report?.length,
      sectionsCount: generateResult?.sections?.length,
    })
  }, [generateResult])

  const handleCopyDocument = async () => {
    try {
      await copyToClipboard(generateResult?.full_report || "")
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast(t("generate.documentCopiedSuccess"))
    } catch (err) {
      console.error("Failed to copy document:", err)
      showErrorToast(t("generate.documentCopiedError"))
    }
  }

  const handleDownloadDocument = async () => {
    try {
      setLoadingDownload(true)

      const response = await ReportgenieService.generateDocx({
        requestBody: { content: generateResult?.full_report || "" },
      })

      console.log("Received DOCX response:", response)
      console.log("Response type:", typeof response)
      console.log("Response instanceof Blob:", response instanceof Blob)
      console.log("Response instanceof ArrayBuffer:", response instanceof ArrayBuffer)

      let blob
      if (response instanceof Blob) {
        console.log("Response is already a Blob")
        blob = response
      } else if (response instanceof ArrayBuffer) {
        console.log("Converting ArrayBuffer to Blob")
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        console.log("Converting unknown response type to Blob")
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
      a.href = url
      a.download = `document_${timestamp}.docx`

      console.log("DOCX download filename:", `document_${timestamp}.docx`)
      console.log("About to trigger DOCX download...")

      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log("DOCX download triggered successfully")
      showSuccessToast(t("generate.documentDownloadSuccess"))
    } catch (err: any) {
      console.error("Failed to download document:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(t("generate.documentDownloadError", { error: err.message || "Unknown error" }))
    } finally {
      console.log("DOCX download process completed")
      setLoadingDownload(false)
    }
  }

  const handleDownloadCsv = async () => {
    try {
      setLoadingCsvDownload(true)

      // Prepare the sections data for CSV generation
      const csvData = {
        sections: generateResult?.sections || [],
      }

      const response = await ReportgenieService.generateCsv({
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
      a.href = url
      a.download = `report_${timestamp}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast(t("generate.csvDownloadSuccess"))
    } catch (err: any) {
      console.error("Failed to download CSV:", err)
      showErrorToast(t("generate.csvDownloadError", { error: err.message || "Unknown error" }))
    } finally {
      setLoadingCsvDownload(false)
    }
  }

  const fetchOutlines = async () => {
    try {
      const data = await ReportgenieService.getOutlines()
      setOutlines(data || [])
    } catch (error) {
      console.error("Error fetching outlines:", error)
      showErrorToast("Failed to fetch outlines")
    }
  }

  // Function to clean up filenames in source paths
  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown"

    if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
      const filename = source.split("/").pop() || source.split("\\").pop() || ""
      return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
    }

    return source
  }

  // Helper function to format source display with page number
  const formatSourceWithPage = (source: string, page?: number | string): string => {
    const fileName = getDisplayFileName(source)
    if (page && page !== "" && page !== 0) {
      return `${fileName} (Page ${page})`
    }
    return fileName
  }

  // Fetch outlines on component mount
  useEffect(() => {
    fetchOutlines()
  }, [])

  // Mutation hook for generating the document
  const mutation = useMutation({
    mutationFn: async (data: {
      sections: string
      knowledgeBaseId: string
      outlineId?: string
      searchMode?: string
      customInstructions?: string
    }) => {
      // First, create a task to get the task_id for progress tracking
      console.log("🎯 Creating generate task for progress tracking...")
      const taskResponse = await ReportgenieService.createGenerateTask()

      const newTaskId = (taskResponse as any).task_id
      console.log("📋 Generated task_id:", newTaskId)
      setTaskId(newTaskId)

      // Now call the actual generation endpoint with the task_id
      const formData = {
        knowledge_base_id: data.knowledgeBaseId,
        sections: data.sections,
        outline_id: data.outlineId || "",
        search_mode: data.searchMode === "full_scan" ? "full_text" : data.searchMode || "vector",
        custom_instructions: data.customInstructions || undefined,
        task_id: newTaskId,
      }

      const promise = ReportgenieService.generateReport({
        formData: formData,
      })

      // Register the operation for automatic cancellation on navigation
      return registerOperation(promise)
    },
    onSuccess: (data: any) => {
      console.log("Generate Response data:", data)
      console.log("Generate interaction_id:", data.results.interaction_id)

      // Check if the request was cancelled
      if (data.results.status === "cancelled") {
        console.log("Generate operation was cancelled")
        showErrorToast("Request cancelled")
        return
      }

      const interactionId = data.results.interaction_id
      console.log("Generate interactionId for feedback:", interactionId)

      // Store result with interaction ID in global state
      setGenerateResult({
        full_report: data.results?.full_report || "",
        sections: data.results?.sections || [],
        interactionId: interactionId,
      })

      const searchMethod =
        searchMode === "vector" ? t("generate.vectorSearch") : t("generate.fullDocumentScan")
      showSuccessToast(t("generate.generateSuccess", { method: searchMethod }))
    },
    onError: (error: any) => {
      console.log("Generate onError triggered:", error)

      // Check if it's a cancellation error from CancelablePromise
      if (error.name === "CancelError" || error.message === "Request aborted") {
        console.log("Generate operation was cancelled (CancelError)")
        showErrorToast("Request cancelled")
        return
      }

      // Check if it's a cancellation error (HTTP 408)
      if (
        error.status === 408 ||
        error.message?.includes("Operation cancelled") ||
        error.detail?.includes("Operation cancelled")
      ) {
        console.log("Generate operation was cancelled (HTTP 408)")
        showErrorToast("Request cancelled")
        return
      }

      showErrorToast(t("generate.generateError", { error: error.message }))
    },
  })

  // Handle generating the document
  const handleGenerateDocument = async () => {
    if (!sections.trim()) {
      showErrorToast(t("generate.enterAtLeastOneSection"))
      return
    }

    if (!selectedKnowledgeBase?.id) {
      showErrorToast(t("generate.selectKnowledgeBase"))
      return
    }

    const requestData = {
      sections: sections,
      knowledgeBaseId: selectedKnowledgeBase.id,
      outlineId: selectedOutline?.id,
      searchMode: searchMode, // Pass the selected search mode to the backend
      customInstructions: customInstructions.trim() || undefined,
    }

    setLoading(true)
    mutation.mutate(requestData, {
      onSettled: () => {
        setLoading(false)
      },
    })
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
      <Box as="th" p={4} textAlign="left" fontWeight="bold" borderBottomWidth="1px" {...props} />
    ),
    td: (props: any) => <Box as="td" p={4} borderBottomWidth="1px" {...props} />,
  }

  return (
    <Container maxW="container.xl" py={8}>
      {/* Tab description */}
      <Text fontSize="sm" color="gray.500" textAlign="center" mb={4} fontStyle="italic">
        {t("generate.pageDescription")}
      </Text>

      {/* Progress bar overlay while document generates */}
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
            <Text color="white" fontSize="lg" fontWeight="medium" textAlign="center">
              {progress.message || t("generate.generatingDocument")}
            </Text>
            <Box width="100%">
              <Progress.Root value={progress.percentage} size="lg" colorPalette="blue">
                <Progress.Track>
                  <Progress.Range />
                </Progress.Track>
              </Progress.Root>
              <Text color="white" fontSize="sm" textAlign="center" mt={2}>
                {Math.round(progress.percentage)}%
              </Text>
            </Box>
            <Text color="gray.300" fontSize="sm" textAlign="center">
              {t("generate.pleaseWait")}
            </Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title={t("generate.knowledgeBaseTitle")}
              description={
                selectedKnowledgeBase
                  ? `${selectedKnowledgeBase.title}`
                  : t("generate.clickToSelect")
              }
              icon={<FiDatabase size={24} />}
              isSelected={!!selectedKnowledgeBase}
              onClick={() => setShowKnowledgeBaseModal(true)}
              helpKey="knowledgeBaseSelection"
            />

            <SelectionCard
              title={t("generate.documentOutlineTitle")}
              description={selectedOutline ? selectedOutline.name : t("generate.clickToSelect")}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedOutline}
              onClick={() => setShowOutlineModal(true)}
              helpKey="documentOutline"
            />

            <SearchModeToggle
              searchMode={searchMode}
              onSearchModeChange={setSearchMode}
              helpKey="searchMode"
            />

            {/* Custom Instructions Text Box */}
            <Box width="100%">
              <HStack align="center" mb={2}>
                <Text fontSize="sm" fontWeight="medium" color="gray.700">
                  {t("generate.customInstructionsTitle")}
                </Text>
                <HelpTooltip helpKey="customInstructions" />
              </HStack>
              <Textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder={t("generate.customInstructionsPlaceholder")}
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
                {t("generate.characterCount", { count: customInstructions.length })}
              </Text>
            </Box>
          </VStack>
        </HStack>

        <KnowledgeBaseSelectionModal
          isOpen={showKnowledgeBaseModal}
          onClose={() => setShowKnowledgeBaseModal(false)}
          title={t("generate.selectKnowledgeBaseTitle")}
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={selectedKnowledgeBase}
          onSelectionChange={setSelectedKnowledgeBase}
          showAllUsers={showAllUsers}
          toggleShowAllUsers={toggleShowAllUsers}
        />

        <SelectionModal
          isOpen={showOutlineModal}
          onClose={() => setShowOutlineModal(false)}
          title={t("generate.selectDocumentOutlineTitle")}
        >
          <OutlineTable
            outlines={outlines}
            selectedOutline={selectedOutline}
            onOutlineChange={setSelectedOutline}
            onSectionsChange={setSections}
            onOutlinesUpdate={fetchOutlines}
            sections={sections}
            selectedKnowledgeBase={selectedKnowledgeBase}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={(!selectedKnowledgeBase || !selectedOutline) && !generateResult ? 0.3 : 1}
          pointerEvents={
            (!selectedKnowledgeBase || !selectedOutline) && !generateResult ? "none" : "auto"
          }
        >
          <HStack gap={4} justify="center">
            <Button
              variant="solid"
              onClick={handleGenerateDocument}
              disabled={!sections.trim() || !selectedKnowledgeBase?.id}
              loading={loading}
              color="white"
              bg="rgba(0, 65, 72, 0.9)"
              width="20%"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              {t("generate.generateButton")}
            </Button>
          </HStack>

          <Box
            border="1px solid"
            borderColor="border"
            borderRadius="md"
            p={4}
            mt={4}
            display="flex"
            flexDirection={{ base: "column", md: "row" }}
            gap={4}
          >
            <Box flex="1" width={{ base: "100%", md: "calc(100% - 300px - 1rem)" }}>
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">{t("generate.results")}</Heading>

                {generateResult && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyDocument}
                      colorPalette={copySuccess ? "green" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? t("generate.copied") : t("generate.copyText")}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadDocument}
                      loading={loadingDownload}
                    >
                      {t("generate.downloadDocx")}
                    </DownloadButton>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadCsv}
                      loading={loadingCsvDownload}
                    >
                      {t("generate.downloadCsv")}
                    </DownloadButton>

                    <Button
                      size="sm"
                      variant="outline"
                      colorPalette="red"
                      onClick={() => {
                        handleClearResults()
                        showSuccessToast(t("generate.reportClearedSuccess"))
                      }}
                    >
                      <FiTrash2 />
                      {t("generate.clearReport")}
                    </Button>
                  </HStack>
                )}
              </HStack>

              <Box
                border="1px solid"
                borderColor="border"
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
                {generateResult ? (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {generateResult.full_report}
                    </ReactMarkdown>

                    {/* Detailed section results with sources */}
                    {generateResult.sections.length > 0 && (
                      <Box mt={8}>
                        <Heading as="h3" size="md" mb={4}>
                          Sections with Sources
                        </Heading>

                        {generateResult.sections.map((section, index) => (
                          <Box
                            key={index}
                            mb={6}
                            p={5}
                            borderWidth="1px"
                            borderRadius="md"
                            bg={expandedSection === index ? "surface" : "bg"}
                            _hover={{ bg: "surface" }}
                          >
                            <Heading
                              as="h4"
                              size="sm"
                              mb={3}
                              onClick={() =>
                                setExpandedSection(expandedSection === index ? null : index)
                              }
                              cursor="pointer"
                              display="flex"
                              alignItems="center"
                              justifyContent="space-between"
                            >
                              <HStack>
                                <Box
                                  as="span"
                                  mr={2}
                                  transform={
                                    expandedSection === index ? "rotate(90deg)" : "rotate(0deg)"
                                  }
                                  transition="transform 0.2s"
                                >
                                  ▶
                                </Box>
                                <Text>
                                  Section {index + 1}: {section.title}
                                </Text>
                              </HStack>
                              <HStack>
                                {section.consult_documents !== false ? (
                                  <Box
                                    as="span"
                                    fontSize="xs"
                                    color="green.600"
                                    bg="green.50"
                                    px={2}
                                    py={1}
                                    borderRadius="md"
                                    display="flex"
                                    alignItems="center"
                                    gap={1}
                                  >
                                    <FiDatabase size={12} />
                                    <Text>KB Generated</Text>
                                  </Box>
                                ) : (
                                  <Box
                                    as="span"
                                    fontSize="xs"
                                    color="gray.600"
                                    bg="gray.50"
                                    px={2}
                                    py={1}
                                    borderRadius="md"
                                    display="flex"
                                    alignItems="center"
                                    gap={1}
                                  >
                                    <FiFileText size={12} />
                                    <Text>Raw Text</Text>
                                  </Box>
                                )}
                              </HStack>
                            </Heading>

                            {expandedSection === index && (
                              <>
                                <Box mb={4} p={3} borderLeft="4px solid" borderColor="blue.200">
                                  <Text whiteSpace="pre-wrap">{section.content}</Text>
                                </Box>

                                {section.source_citations &&
                                  section.source_citations.length > 0 &&
                                  section.consult_documents !== false && (
                                    <Accordion.Root multiple>
                                      <Accordion.Item value={`citations-${index}`}>
                                        <h2>
                                          <Accordion.ItemTrigger
                                            bg="surface"
                                            _hover={{ bg: "panel" }}
                                          >
                                            <Box flex="1" textAlign="left" fontWeight="medium">
                                              <HStack>
                                                <FiFileText />
                                                <Text>
                                                  View Source Citations (
                                                  {section.source_citations.length})
                                                </Text>
                                              </HStack>
                                            </Box>
                                          </Accordion.ItemTrigger>
                                        </h2>
                                        <Accordion.ItemContent pb={4} bg="surface">
                                          {section.source_citations.map(
                                            (citation: any, cIndex: number) => {
                                              const isExpanded = isCitationExpanded(index, cIndex)
                                              const citationText = cleanRTFFormatting(
                                                citation.content,
                                              )
                                              const shouldTruncate = citationText.length > 300
                                              const displayText =
                                                shouldTruncate && !isExpanded
                                                  ? `${citationText.substring(0, 300)}...`
                                                  : citationText

                                              return (
                                                <Box
                                                  key={`${index}-${cIndex}`}
                                                  p={3}
                                                  mb={2}
                                                  borderWidth="1px"
                                                  borderRadius="md"
                                                  bg="bg"
                                                >
                                                  {citation.metadata?.source_data_id ? (
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
                                                  ) : citation.metadata?.source &&
                                                    (citation.metadata.source
                                                      .toLowerCase()
                                                      .endsWith(".docx") ||
                                                      citation.metadata.source
                                                        .toLowerCase()
                                                        .endsWith(".pdf")) ? (
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
                                                        citation.metadata?.source || "Unknown",
                                                        citation.metadata?.page,
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
                                                        toggleCitationExpansion(index, cIndex)
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
                              </>
                            )}
                          </Box>
                        ))}
                      </Box>
                    )}

                    {/* Add feedback buttons for the generated document */}
                    {generateResult?.interactionId && (
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
                          interactionId={generateResult.interactionId}
                          onFeedbackSubmitted={handleFeedbackSubmitted}
                        />
                      </Box>
                    )}
                  </>
                ) : (
                  <Text color="gray.500">{t("generate.resultsPlaceholder")}</Text>
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
export const Route = createFileRoute("/_layout/generate")({
  component: ReportGenie,
})
