import React from "react"
import { Box, Text, Heading } from "@chakra-ui/react"
import SourceCitationAccordion from "./SourceCitationAccordion"

interface QAPairDisplayProps {
  pair: any
  index: number
}

const QAPairDisplay: React.FC<QAPairDisplayProps> = ({ pair, index }) => {
  return (
    <Box mb={4} p={4} borderWidth="1px" borderRadius="md" bg="white">
      <Heading as="h3" size="md" mb={2}>
        Question {index + 1}: {pair.question}
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
        <SourceCitationAccordion
          sourceCitations={pair.source_citations}
          accordionValue={`item-${index}`}
        />
      )}
    </Box>
  )
}

export default QAPairDisplay
