import React, { useState } from "react"
import { Box, Heading, HStack, Text } from "@chakra-ui/react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFileText } from "react-icons/fi"
import SourceLink from "@/components/Common/SourceLink"

interface ReportgenieResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const ReportgenieResults: React.FC<ReportgenieResultsProps> = ({ selectedReport, components }) => {
  console.log("🔍 REPORTGENIE UI DEBUG: Full selectedReport:", selectedReport)
  console.log("🔍 REPORTGENIE UI DEBUG: selectedReport.results:", selectedReport.results)
  console.log(
    "🔍 REPORTGENIE UI DEBUG: selectedReport.results?.sections:",
    selectedReport.results?.sections,
  )
  const results =
    selectedReport.results?.full_report ||
    selectedReport.full_report ||
    selectedReport.content ||
    ""
  const sections = selectedReport.results?.sections || []

  console.log("🔍 REPORTGENIE UI DEBUG: Processed sections:", sections)
  console.log("🔍 REPORTGENIE UI DEBUG: Sections length:", sections.length)

  // For expanding/collapsing sections
  const [expandedSection, setExpandedSection] = useState<number | null>(null)

  // Helper to get display file name
  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown"
    if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
      const filename = source.split("/").pop() || source.split("\\").pop() || ""
      return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
    }
    return source
  }

  // Get all sections (including those without citations for display)
  const allSections = sections || []

  // Filter for sections that have source citations to display them separately
  const sectionsWithSources = allSections.filter(
    (section: any) => section.consult_documents !== false && section.source_citations?.length > 0,
  )

  console.log("🔍 REPORTGENIE CITATIONS: Total sections:", allSections.length)
  console.log("🔍 REPORTGENIE CITATIONS: Sections with sources:", sectionsWithSources.length)
  console.log("🔍 REPORTGENIE CITATIONS: Sample section data:", allSections[0])

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      {/* Render all sections with better citation visibility */}
      {allSections.length > 0 && (
        <Box mt={8}>
          <Heading as="h3" size="md" mb={4}>
            Report Sections{" "}
            {sectionsWithSources.length > 0 && `(${sectionsWithSources.length} with citations)`}
          </Heading>
          {allSections.map((section: any, index: number) => {
            const hasCitations =
              section.consult_documents !== false && section.source_citations?.length > 0

            return (
              <Box
                key={index}
                mb={6}
                p={5}
                borderWidth="1px"
                borderRadius="md"
                bg={expandedSection === index ? "surface" : "bg"}
                _hover={{ bg: "surface" }}
                borderColor={hasCitations ? "blue.200" : "gray.200"}
                position="relative"
              >
                {/* Citation indicator badge */}
                {hasCitations && (
                  <Box
                    position="absolute"
                    top={2}
                    right={2}
                    bg="blue.100"
                    color="blue.800"
                    px={2}
                    py={1}
                    borderRadius="sm"
                    fontSize="xs"
                    fontWeight="medium"
                  >
                    {section.source_citations.length} sources
                  </Box>
                )}

                <Heading
                  as="h4"
                  size="sm"
                  mb={3}
                  onClick={() => setExpandedSection(expandedSection === index ? null : index)}
                  cursor="pointer"
                  display="flex"
                  alignItems="center"
                  justifyContent="space-between"
                  pr={hasCitations ? "80px" : "0"}
                >
                  <HStack>
                    <Box
                      as="span"
                      mr={2}
                      transform={expandedSection === index ? "rotate(90deg)" : "rotate(0deg)"}
                      transition="transform 0.2s"
                    >
                      ▶
                    </Box>
                    <Text>{section.title || `Section ${index + 1}`}</Text>
                    {hasCitations && <FiFileText color="blue" size="14px" />}
                  </HStack>
                </Heading>

                {expandedSection === index && (
                  <>
                    <Box
                      mb={4}
                      p={3}
                      borderLeft="4px solid"
                      borderColor={hasCitations ? "blue.200" : "gray.200"}
                    >
                      <Text whiteSpace="pre-wrap">{section.content}</Text>
                    </Box>

                    {hasCitations && (
                      <Box
                        mt={4}
                        p={4}
                        bg="blue.50"
                        borderRadius="md"
                        borderWidth="1px"
                        borderColor="blue.200"
                      >
                        <Heading as="h5" size="xs" mb={3} color="blue.700">
                          <HStack>
                            <FiFileText />
                            <Text>Source Citations ({section.source_citations.length})</Text>
                          </HStack>
                        </Heading>

                        <Box maxH="300px" overflowY="auto">
                          {section.source_citations.map((citation: any, cIndex: number) => (
                            <Box
                              key={cIndex}
                              p={3}
                              mb={3}
                              borderWidth="1px"
                              borderRadius="md"
                              bg="white"
                              borderColor="blue.100"
                              _last={{ mb: 0 }}
                            >
                              <HStack mb={2} justify="space-between" align="start">
                                {citation.metadata?.source_data_id ? (
                                  <SourceLink
                                    sourceId={citation.metadata.source_data_id}
                                    fileName={getDisplayFileName(citation.metadata.source)}
                                    fontWeight="medium"
                                    color="blue.600"
                                    useModal={true}
                                  />
                                ) : citation.metadata?.source &&
                                  (citation.metadata.source.toLowerCase().endsWith(".pdf") ||
                                    citation.metadata.source.toLowerCase().endsWith(".docx")) ? (
                                  <SourceLink
                                    sourceId={citation.metadata.source} // Use filename as fallback
                                    fileName={getDisplayFileName(citation.metadata.source)}
                                    fontWeight="medium"
                                    color="blue.600"
                                    useModal={true}
                                  />
                                ) : (
                                  <Text fontWeight="medium" color="blue.600">
                                    {getDisplayFileName(
                                      citation.metadata?.source || "Unknown Source",
                                    )}
                                  </Text>
                                )}
                                <Text fontSize="xs" color="gray.500">
                                  Citation {cIndex + 1}
                                </Text>
                              </HStack>

                              <Box
                                p={3}
                                bg="gray.50"
                                borderRadius="sm"
                                fontSize="sm"
                                whiteSpace="pre-wrap"
                                borderLeft="3px solid"
                                borderColor="blue.200"
                              >
                                {citation.content}
                              </Box>
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    )}

                    {!hasCitations && (
                      <Box mt={2} p={2} bg="gray.50" borderRadius="sm">
                        <Text fontSize="sm" color="gray.600" fontStyle="italic">
                          No source citations available for this section
                        </Text>
                      </Box>
                    )}
                  </>
                )}
              </Box>
            )
          })}
        </Box>
      )}

      {/* Show message if no sections found */}
      {allSections.length === 0 && (
        <Box mt={8} p={4} bg="gray.50" borderRadius="md" textAlign="center">
          <Text color="gray.600">No detailed sections available for this report</Text>
        </Box>
      )}
    </>
  )
}

export default ReportgenieResults
