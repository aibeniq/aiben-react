import React from "react"
import { Box, Text, HStack, Accordion } from "@chakra-ui/react"
import { FiFileText } from "react-icons/fi"
import SourceLink from "../../Common/SourceLink"

interface SourceCitationAccordionProps {
  sourceCitations: any[]
  accordionValue: string
}

const SourceCitationAccordion: React.FC<SourceCitationAccordionProps> = ({
  sourceCitations,
  accordionValue,
}) => {
  const getDisplayFileName = (source: string): string => {
    if (!source) return "Unknown"
    if (source.includes("/tmp/") || source.includes("\\tmp\\")) {
      const filename = source.split("/").pop() || source.split("\\").pop() || ""
      return filename.includes("_") ? filename.substring(filename.indexOf("_") + 1) : filename
    }
    return source
  }

  return (
    <Accordion.Root collapsible mt={2}>
      <Accordion.Item value={accordionValue}>
        <h2>
          <Accordion.ItemTrigger bg="gray.100" _hover={{ bg: "gray.200" }}>
            <Box flex="1" textAlign="left" fontWeight="medium">
              <HStack>
                <FiFileText />
                <Text>View Source Citations ({sourceCitations.length})</Text>
              </HStack>
            </Box>
          </Accordion.ItemTrigger>
        </h2>
        <Accordion.ItemContent pb={4} bg="gray.50">
          {sourceCitations.map((citation: any, cIndex: number) => (
            <Box key={cIndex} p={3} mb={2} borderWidth="1px" borderRadius="md" bg="white">
              {citation.metadata.source_data_id ? (
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
                  {getDisplayFileName(citation.metadata.source)}
                </Text>
              )}
              <Box mt={2} p={2} bg="gray.50" borderRadius="sm" fontSize="sm" whiteSpace="pre-wrap">
                {citation.content}
              </Box>
            </Box>
          ))}
        </Accordion.ItemContent>
      </Accordion.Item>
    </Accordion.Root>
  )
}

export default SourceCitationAccordion
