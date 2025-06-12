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
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import SourceLink from "@/components/Common/SourceLink"
import DownloadButton from "@/components/ui/download-button"
import { useState, useEffect } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { useMutation } from "@tanstack/react-query"
import {
  ReportgenieService,
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
  const [generatedReport, setGeneratedReport] = useState("")
  const [sectionResults, setSectionResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedSection, setExpandedSection] = useState<number | null>(null)

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(generatedReport)
      setCopySuccess(true)

      // Reset the success icon after 2 seconds
      setTimeout(() => {
        setCopySuccess(false)
      }, 2000)

      showSuccessToast("Report copied to clipboard")
    } catch (err) {
      console.error("Failed to copy report:", err)
      showErrorToast("Failed to copy report to clipboard")
    }
  }

  const handleDownloadReport = async () => {
    try {
      setLoadingDownload(true)

      const response = await ReportgenieService.generateDocx({
        requestBody: { content: generatedReport },
      })

      let blob
      if (response instanceof Blob) {
        blob = response
      } else if (response instanceof ArrayBuffer) {
        blob = new Blob([response], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      } else {
        blob = new Blob([response as any], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
      a.href = url
      a.download = `report_${timestamp}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      showSuccessToast("Report downloaded successfully")
    } catch (err: any) {
      console.error("Failed to download report:", err)
      showErrorToast(`Failed to download report: ${err.message || "Unknown error"}`)
    } finally {
      setLoadingDownload(false)
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

  // Mutation hook for generating the report
  const mutation = useMutation({
    mutationFn: (data: { sections: string; knowledgeBaseId: string; outlineId?: string }) => {
      if (data.outlineId) {
        return ReportgenieService.generateReport({
          sections: data.sections,
          knowledgeBaseId: data.knowledgeBaseId,
          outlineId: data.outlineId,
        })
      } else {
        // For now, we'll pass an empty string as outlineId when not provided
        // This might need to be adjusted based on backend requirements
        return ReportgenieService.generateReport({
          sections: data.sections,
          knowledgeBaseId: data.knowledgeBaseId,
          outlineId: "",
        })
      }
    },
    onSuccess: (data: any) => {
      setGeneratedReport(data.results.full_report)
      setSectionResults(data.results.sections || [])
    },
    onError: (error: any) => {
      showErrorToast(`Failed to generate report: ${error.message}`)
    },
  })

  // Handle generating the report
  const handleGenerateReport = async () => {
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
      {/* Loading overlay while report generates */}
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
            <Text fontWeight="medium">Generating report...</Text>
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
              title="Report Outline"
              description={selectedOutline ? selectedOutline.name : "Click to select"}
              icon={<FiFileText size={24} />}
              isSelected={!!selectedOutline}
              onClick={() => setShowOutlineModal(true)}
            />
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
          title="Select Report Outline"
        >
          <OutlineTable
            outlines={outlines}
            selectedOutline={selectedOutline}
            onOutlineChange={setSelectedOutline}
            onSectionsChange={setSections}
            onOutlinesUpdate={fetchOutlines}
            sections={sections}
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
              onClick={handleGenerateReport}
              disabled={!sections.trim() || !selectedKnowledgeBase?.id}
              loading={loading}
              color="white"
              bg="rgba(0, 65, 72, 0.9)"
              width="20%"
              _hover={{
                bg: "rgba(0, 65, 72, 0.85)",
              }}
            >
              Generate Report
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

                {generatedReport && (
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
                {generatedReport || sectionResults.length > 0 ? (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
                      {generatedReport}
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
                            >
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
                              Section {index + 1}: {section.title}
                            </Heading>

                            {expandedSection === index && (
                              <>
                                <Box mb={4} p={3} borderLeft="4px solid" borderColor="blue.200">
                                  <Text whiteSpace="pre-wrap">{section.content}</Text>
                                </Box>

                                {section.source_citations &&
                                  section.source_citations.length > 0 && (
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
                                            (citation: any, cIndex: number) => (
                                              <Box
                                                key={cIndex}
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
                                                  {citation.content}
                                                </Box>
                                              </Box>
                                            ),
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
                  </>
                ) : (
                  <Text color="gray.500">Results will appear here after generating a report.</Text>
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
