import { Accordion, Box, Button, HStack, Text } from "@chakra-ui/react"
import type React from "react"
import { useState } from "react"
import { FiFileText } from "react-icons/fi"
import { getCleanFileName } from "../../../utils/filename"
import { cleanRTFFormatting } from "../../../utils/rtfCleaner"
import SourceLink from "../../Common/SourceLink"

interface SourceCitationAccordionProps {
  sourceCitations: any[]
  accordionValue: string
}

const SourceCitationAccordion: React.FC<SourceCitationAccordionProps> = ({
  sourceCitations,
  accordionValue,
}) => {
  // State to track which citations are expanded - using object instead of Set
  const [expandedCitations, setExpandedCitations] = useState<
    Record<number, boolean>
  >({})

  // Function to toggle citation expansion
  const toggleCitationExpansion = (citationIndex: number) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [citationIndex]: !prev[citationIndex],
    }))
  }

  // Function to check if a citation is expanded
  const isCitationExpanded = (citationIndex: number) => {
    return expandedCitations[citationIndex] || false
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

  return (
    <Accordion.Root collapsible mt={2}>
      <Accordion.Item value={accordionValue}>
        <h2>
          <Accordion.ItemTrigger bg="surface" _hover={{ bg: "panel" }}>
            <Box flex="1" textAlign="left" fontWeight="medium">
              <HStack>
                <FiFileText />
                <Text>View Source Citations ({sourceCitations.length})</Text>
              </HStack>
            </Box>
          </Accordion.ItemTrigger>
        </h2>
        <Accordion.ItemContent pb={4} bg="surface">
          {sourceCitations.map((citation: any, cIndex: number) => {
            const isExpanded = isCitationExpanded(cIndex)
            const citationText = cleanRTFFormatting(citation.content)
            const shouldTruncate = citationText.length > 300
            const displayText =
              shouldTruncate && !isExpanded
                ? `${citationText.substring(0, 300)}...`
                : citationText

            return (
              <Box
                key={cIndex}
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
                  <Text as="span" ml={1} fontWeight="normal" color="blue.600">
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
                    onClick={() => toggleCitationExpansion(cIndex)}
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
  )
}

export default SourceCitationAccordion
