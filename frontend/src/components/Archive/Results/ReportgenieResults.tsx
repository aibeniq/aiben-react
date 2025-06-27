import React, { useState } from "react"
import { Box, Heading, Accordion, HStack, Text } from "@chakra-ui/react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FiFileText } from "react-icons/fi"
import SourceLink from "@/components/Common/SourceLink"

interface ReportgenieResultsProps {
  selectedReport: any
  components: any // Markdown components for table rendering
}

const ReportgenieResults: React.FC<ReportgenieResultsProps> = ({ selectedReport, components }) => {
  const results =
    selectedReport.results?.full_report ||
    selectedReport.full_report ||
    selectedReport.content ||
    ""
  const sections = selectedReport.results?.sections || []

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

  return (
    <>
      {results && (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {results}
        </ReactMarkdown>
      )}

      {/* Render sections with citations if present */}
      {sections.length > 0 && (
        <Box mt={8}>
          <Heading as="h3" size="md" mb={4}>
            Sections with Sources
          </Heading>
          {sections.map((section: any, index: number) => (
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
                onClick={() => setExpandedSection(expandedSection === index ? null : index)}
                cursor="pointer"
                display="flex"
                alignItems="center"
                justifyContent="space-between"
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
                      <Box as="span">🔍</Box>
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
                      <Box as="span">📝</Box>
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
                            <Accordion.ItemTrigger bg="surface" _hover={{ bg: "panel" }}>
                              <Box flex="1" textAlign="left" fontWeight="medium">
                                <HStack>
                                  <FiFileText />
                                  <Text>
                                    View Source Citations ({section.source_citations.length})
                                  </Text>
                                </HStack>
                              </Box>
                            </Accordion.ItemTrigger>
                          </h2>
                          <Accordion.ItemContent pb={4} bg="surface">
                            {section.source_citations.map((citation: any, cIndex: number) => (
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
                                    fileName={getDisplayFileName(citation.metadata.source)}
                                    ml={1}
                                    fontWeight="normal"
                                    color="blue.600"
                                    useModal={true}
                                  />
                                ) : (
                                  <Text as="span" ml={1} fontWeight="normal" color="blue.600">
                                    {getDisplayFileName(citation.metadata?.source || "Unknown")}
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
                            ))}
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
  )
}

export default ReportgenieResults
