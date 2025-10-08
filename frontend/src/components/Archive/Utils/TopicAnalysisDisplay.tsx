import { Button } from "@/components/ui/button"
import { Badge, Box, HStack, Heading, Text, VStack } from "@chakra-ui/react"
import type React from "react"
import { useState } from "react"
import { FiChevronDown, FiChevronUp, FiExternalLink } from "react-icons/fi"
import { cleanRTFFormatting } from "../../../utils/rtfCleaner"

interface SourceCitation {
  content: string
  metadata: {
    source?: string
    page?: number
    chunk_index?: number
    [key: string]: any
  }
}

interface TopicAnalysis {
  topic: string
  analysis: string
  source_citations?: SourceCitation[]
  chunk_count?: number
  synthesis_error?: string
}

interface TopicAnalysisDisplayProps {
  topicAnalysis: TopicAnalysis[]
}

const TopicAnalysisDisplay: React.FC<TopicAnalysisDisplayProps> = ({
  topicAnalysis,
}) => {
  const [expandedCitations, setExpandedCitations] = useState<{
    [key: number]: boolean
  }>({})

  if (topicAnalysis.length === 0) return null

  const toggleCitations = (index: number) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [index]: !prev[index],
    }))
  }

  return (
    <Box mt={4}>
      {topicAnalysis.map((topic: TopicAnalysis, index: number) => (
        <Box
          key={index}
          mb={4}
          p={4}
          borderWidth="1px"
          borderRadius="md"
          bg="bg"
        >
          <Heading as="h3" size="md" mb={2}>
            Topic: {topic.topic}
          </Heading>
          <Text mb={3}>{topic.analysis}</Text>

          {/* Display source citations if available */}
          {topic.source_citations && topic.source_citations.length > 0 && (
            <VStack align="stretch" mt={4} gap={3}>
              <HStack justify="space-between" align="center">
                <Badge colorScheme="blue" variant="subtle">
                  {topic.source_citations.length} Knowledge Base Reference
                  {topic.source_citations.length !== 1 ? "s" : ""}
                </Badge>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => toggleCitations(index)}
                >
                  {expandedCitations[index] ? (
                    <FiChevronUp />
                  ) : (
                    <FiChevronDown />
                  )}
                  {expandedCitations[index] ? " Hide" : " Show"} References
                </Button>
              </HStack>

              {expandedCitations[index] && (
                <VStack align="stretch" gap={3} mt={2}>
                  {topic.source_citations.map(
                    (citation: SourceCitation, citationIndex: number) => (
                      <Box
                        key={citationIndex}
                        p={3}
                        bg="gray.50"
                        borderRadius="md"
                        borderLeft="4px solid"
                        borderLeftColor="blue.400"
                        _dark={{
                          bg: "gray.700",
                          borderLeftColor: "blue.300",
                        }}
                      >
                        <HStack
                          justify="space-between"
                          align="flex-start"
                          mb={2}
                        >
                          <Text
                            fontSize="sm"
                            fontWeight="semibold"
                            color="blue.600"
                            _dark={{ color: "blue.300" }}
                          >
                            <FiExternalLink
                              style={{ display: "inline", marginRight: "4px" }}
                            />
                            Reference {citationIndex + 1}
                            {citation.metadata.source &&
                              ` - ${citation.metadata.source}`}
                            {citation.metadata.page &&
                              ` (Page ${citation.metadata.page})`}
                          </Text>
                        </HStack>
                        <Text
                          fontSize="sm"
                          color="gray.700"
                          _dark={{ color: "gray.300" }}
                        >
                          {cleanRTFFormatting(citation.content)}
                        </Text>
                        {citation.metadata.chunk_index !== undefined && (
                          <Badge size="sm" variant="outline" mt={2}>
                            Chunk {citation.metadata.chunk_index}
                          </Badge>
                        )}
                      </Box>
                    ),
                  )}
                </VStack>
              )}
            </VStack>
          )}

          {/* Display additional metadata if available */}
          {topic.chunk_count && topic.chunk_count > 1 && (
            <Badge variant="outline" mt={2}>
              Processed in {topic.chunk_count} chunks
            </Badge>
          )}

          {topic.synthesis_error && (
            <Box
              mt={2}
              p={2}
              bg="red.50"
              borderRadius="md"
              borderLeft="4px solid red.400"
            >
              <Text fontSize="sm" color="red.600">
                Note: Synthesis error occurred - showing combined chunk results
              </Text>
            </Box>
          )}
        </Box>
      ))}
    </Box>
  )
}

export default TopicAnalysisDisplay
