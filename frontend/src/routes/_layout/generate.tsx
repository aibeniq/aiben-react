import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Spinner,
  Accordion,
  Textarea,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import SourceLink from "@/components/Common/SourceLink"
import DownloadButton from "@/components/ui/download-button"
import SearchModeToggle from "@/components/Common/SearchModeToggle"
import FeedbackButtons from "@/components/Feedback/FeedbackButtons"
import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import {
  ReportgenieService,
  TwincheckService,
  KnowledgeBasesService,
  KnowledgeBasePublic,
  ReportGenieOutline,
} from "@/client"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFileText, FiCopy, FiCheck, FiDatabase } from "react-icons/fi"
import SelectionCard from "../../components/Common/SelectionCard"
import SelectionModal from "../../components/Common/SelectionModal"
import KnowledgeBaseTable from "../../components/Common/KnowledgeBaseTable"
import OutlineTable from "../../components/Generate/OutlineTable"

const ReportGenie = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [copySuccess, setCopySuccess] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState(false)
  const [loadingCsvDownload, setLoadingCsvDownload] = useState(false)

  // Modal states
  const [showKnowledgeBaseModal, setShowKnowledgeBaseModal] = useState(false)
  const [showOutlineModal, setShowOutlineModal] = useState(false)

  // Knowledge base selection state
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<KnowledgeBasePublic | null>(
    null,
  )
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBasePublic[]>([])

  // Outline content state
  const [sections, setSections] = useState("")
  const [outlines, setOutlines] = useState<ReportGenieOutline[]>([])
  const [selectedOutline, setSelectedOutline] = useState<ReportGenieOutline | null>(null)

  // Results state
  const [generatedDocument, setGeneratedDocument] = useState("")
  const [sectionResults, setSectionResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedSection, setExpandedSection] = useState<number | null>(null)
  const [interactionId, setInteractionId] = useState<string | null>(null)

  // Search mode state
  const [searchMode, setSearchMode] = useState<"vector" | "full_scan">("vector") // Default to vector search

  // Custom instructions state
  const [customInstructions, setCustomInstructions] = useState("")

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

  const handleCopyDocument = async () => {
    try {
      await navigator.clipboard.writeText(generatedDocument)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Document copied to clipboard")
    } catch (err) {
      console.error("Failed to copy document:", err)
      showErrorToast("Failed to copy document to clipboard")
    }
  }

  const handleDownloadDocument = async () => {
    try {
      setLoadingDownload(true)

      const response = await TwincheckService.generateDocx({
        requestBody: { content: generatedDocument },
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
      showSuccessToast("Document downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download document:", err)
      console.error("Error details:", {
        message: err instanceof Error ? err.message : "Unknown error",
        stack: err instanceof Error ? err.stack : undefined,
        name: err instanceof Error ? err.name : undefined,
      })

      showErrorToast(`Failed to download document: ${err.message || "Unknown error"}`)
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
        sections: sectionResults,
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

      showSuccessToast("CSV downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download CSV:", err)
      showErrorToast(`Failed to download CSV: ${err.message || "Unknown error"}`)
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

  // Fetch knowledge bases on component mount
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
        showErrorToast("Failed to fetch knowledge bases")
      }
    }

    fetchKnowledgeBases()
    fetchOutlines()
  }, [])

  // Mutation hook for generating the document
  const mutation = useMutation({
    mutationFn: (data: {
      sections: string
      knowledgeBaseId: string
      outlineId?: string
      searchMode?: string
      customInstructions?: string
    }) => {
      const formData = {
        knowledge_base_id: data.knowledgeBaseId,
        sections: data.sections,
        outline_id: data.outlineId || "",
        search_mode: data.searchMode === "full_scan" ? "full_text" : data.searchMode || "vector", // Map full_scan to full_text for ReportGenie backend
        custom_instructions: data.customInstructions || undefined,
      }

      return ReportgenieService.generateReport({
        formData: formData,
      })
    },
    onSuccess: (data: any) => {
      console.log("Generate Response data:", data)
      console.log("Generate interaction_id:", data.results.interaction_id)
      setGeneratedDocument(data.results.full_report)
      setSectionResults(data.results.sections || [])
      setInteractionId(data.results.interaction_id as string | null)
    },
    onError: (error: any) => {
      showErrorToast(`Failed to generate document: ${error.message}`)
    },
  })

  // Handle generating the document
  const handleGenerateDocument = async () => {
    if (!sections.trim()) {
      showErrorToast("Please enter at least one section")
      return
    }

    if (!selectedKnowledgeBase?.id) {
      showErrorToast("Please select a knowledge base")
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
      {/* Loading overlay while document generates */}
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
            <Text fontWeight="medium">Generating document...</Text>
          </VStack>
        </Box>
      )}

      <VStack gap={6} align="stretch">
        <HStack width="100%" justify="space-between">
          <VStack gap={4} align="stretch" flex={1}>
            <SelectionCard
              title="Knowledge Base"
              description={
                selectedKnowledgeBase ? `${selectedKnowledgeBase.title}` : "Click to select"
              }
              icon={<FiDatabase size={24} />}
              isSelected={!!selectedKnowledgeBase}
              onClick={() => setShowKnowledgeBaseModal(true)}
            />

            <SelectionCard
              title="Document Outline"
              description={selectedOutline ? selectedOutline.name : "Click to select"}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedOutline}
              onClick={() => setShowOutlineModal(true)}
            />

            <SearchModeToggle searchMode={searchMode} onSearchModeChange={setSearchMode} />

            {/* Custom Instructions Text Box */}
            <Box width="100%">
              <Text fontSize="sm" fontWeight="medium" mb={2} color="gray.700">
                Custom Instructions (Optional)
              </Text>
              <Textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder="Enter any additional instructions that should be considered when generating each section of the report..."
                rows={3}
                resize="vertical"
                bg="white"
                borderColor="gray.300"
                _hover={{ borderColor: "gray.400" }}
                _focus={{ borderColor: "blue.500", boxShadow: "0 0 0 1px blue.500" }}
                fontSize="sm"
                maxLength={2000}
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                {customInstructions.length}/2000 characters. These instructions will be added to the
                prompt when generating each section.
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
          isOpen={showOutlineModal}
          onClose={() => setShowOutlineModal(false)}
          title="Select Document Outline"
        >
          <OutlineTable
            outlines={outlines}
            selectedOutline={selectedOutline}
            onOutlineChange={setSelectedOutline}
            onSectionsChange={setSections}
            onOutlinesUpdate={fetchOutlines}
            sections={sections}
            selectedKnowledgeBase={selectedKnowledgeBase}
            knowledgeBases={knowledgeBases}
          />
        </SelectionModal>

        <VStack
          align="stretch"
          mb={4}
          opacity={!selectedKnowledgeBase || !selectedOutline ? 0.3 : 1}
          pointerEvents={!selectedKnowledgeBase || !selectedOutline ? "none" : "auto"}
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
              Generate
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
                <Heading size="md">Results</Heading>

                {generatedDocument && (
                  <HStack gap={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCopyDocument}
                      colorPalette={copySuccess ? "green" : "blue"}
                    >
                      {copySuccess ? <FiCheck color="green" /> : <FiCopy />}
                      {copySuccess ? "Copied!" : "Copy Text"}
                    </Button>

                    <DownloadButton
                      size="sm"
                      onClick={handleDownloadDocument}
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
                {generatedDocument || sectionResults.length > 0 ? (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {generatedDocument}
                    </ReactMarkdown>

                    {/* Detailed section results with sources */}
                    {sectionResults.length > 0 && (
                      <Box mt={8}>
                        <Heading as="h3" size="md" mb={4}>
                          Sections with Sources
                        </Heading>

                        {sectionResults.map((section, index) => (
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
                                              const citationText = citation.content
                                              const shouldTruncate = citationText.length > 300
                                              const displayText =
                                                shouldTruncate && !isExpanded
                                                  ? citationText.substring(0, 300) + "..."
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
                                                      fileName={getDisplayFileName(
                                                        citation.metadata.source,
                                                      )}
                                                      ml={1}
                                                      fontWeight="normal"
                                                      color="blue.600"
                                                      useModal={true}
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
                                                      fileName={getDisplayFileName(
                                                        citation.metadata.source,
                                                      )}
                                                      ml={1}
                                                      fontWeight="normal"
                                                      color="blue.600"
                                                      useModal={true}
                                                    />
                                                  ) : (
                                                    <Text
                                                      as="span"
                                                      ml={1}
                                                      fontWeight="normal"
                                                      color="blue.600"
                                                    >
                                                      {getDisplayFileName(
                                                        citation.metadata?.source || "Unknown",
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
                    {interactionId ? (
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
                          interactionId={interactionId}
                          onFeedbackSubmitted={handleFeedbackSubmitted}
                        />
                      </Box>
                    ) : (
                      <Box
                        position="sticky"
                        bottom={4}
                        right={4}
                        display="flex"
                        justifyContent="flex-end"
                        pointerEvents="auto"
                        zIndex={10}
                        mt={4}
                        bg="yellow.100"
                        p={2}
                        borderRadius="md"
                      >
                        <Text fontSize="sm" color="red.600">
                          Debug: No interaction ID found
                        </Text>
                      </Box>
                    )}
                    {console.log("Generate interactionId for feedback:", interactionId)}
                  </>
                ) : (
                  <Text color="gray.500">
                    Results will appear here after generating a document.
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

// Export the Route for compatibility with the routing system
export const Route = createFileRoute("/_layout/generate")({
  component: ReportGenie,
})
